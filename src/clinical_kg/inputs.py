"""Read frozen inputs without rewriting them or resolving remote OWL imports."""
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pyarrow.parquet as pq

RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
OWL = 'http://www.w3.org/2002/07/owl#'
OBO = 'http://purl.obolibrary.org/obo/'
OIO = 'http://www.geneontology.org/formats/oboInOwl#'
SKOS = 'http://www.w3.org/2004/02/skos/core#'
ANCHOR = OBO + 'MONDO_0005148'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def raw_files(root):
    return sorted(p for p in (root / 'data/raw').rglob('*')
                  if p.suffix in {'.owl', '.hpoa', '.parquet'})


def inventory(root):
    result = []
    for path in raw_files(root):
        source = path.relative_to(root / 'data/raw').parts[0]
        version, basis = '26.06', 'user-declared; not independently encoded in Parquet metadata'
        if path.suffix == '.owl':
            _, metadata = read_owl(path, metadata_only=True)
            version, basis = metadata['versionIRI'], 'embedded owl:versionIRI'
        elif path.suffix == '.hpoa':
            with path.open() as f:
                headers = [next(f).strip() for _ in range(4)]
            version = next(x.split(': ', 1)[1] for x in headers if x.startswith('#version:'))
            basis = 'embedded HPOA #version header'
        result.append(dict(path=str(path.relative_to(root)), source=source,
                           version=version, version_basis=basis,
                           bytes=path.stat().st_size, sha256=digest(path),
                           download_url=None, download_date=None,
                           acquisition_status='not recorded in supplied folder'))
    return result


def verify(root, manifest):
    expected = {r['path']: r for r in manifest['inputs']}
    actual = {str(p.relative_to(root)): p for p in raw_files(root)}
    if expected.keys() != actual.keys():
        raise ValueError('Raw input inventory changed; review the manifest, do not silently refreeze.')
    for name, path in actual.items():
        if path.stat().st_size != expected[name]['bytes'] or digest(path) != expected[name]['sha256']:
            raise ValueError(f'Frozen input checksum mismatch: {name}')


def read_owl(path, metadata_only=False):
    """Extract named class annotations and direct named parents; retain restrictions as XML.

    This is a deliberately bounded projection, not a lossless OWL converter. Nested
    class expressions are never flattened into clinical relations or named parents.
    """
    classes, metadata, depth = {}, {}, 0
    for event, el in ET.iterparse(path, events=('start', 'end')):
        if event == 'start':
            depth += 1
            continue
        if depth == 2:
            if el.tag == '{' + OWL + '}Ontology':
                for name in ('versionIRI', 'versionInfo'):
                    child = el.find('{' + OWL + '}' + name)
                    if child is not None:
                        metadata[name] = child.get('{' + RDF + '}resource') or child.text
                if metadata_only:
                    return {}, metadata
            elif el.tag == '{' + OWL + '}Class':
                uri = el.get('{' + RDF + '}about')
                if uri:
                    item = {'uri': uri, 'labels': [], 'parents': [], 'xrefs': [],
                            'synonyms': [], 'mappings': [], 'restrictions_xml': [], 'deprecated': False}
                    for child in el:
                        tag = child.tag.replace('{', '').replace('}', '')
                        value = child.get('{' + RDF + '}resource')
                        if tag == RDFS + 'label' and child.text:
                            item['labels'].append(child.text)
                        elif tag == RDFS + 'subClassOf':
                            if value:
                                item['parents'].append(value)
                            else:
                                item['restrictions_xml'].append(ET.tostring(child, encoding='unicode'))
                        elif tag == OIO + 'hasDbXref' and child.text:
                            item['xrefs'].append(child.text)
                        elif tag == OIO + 'hasExactSynonym' and child.text:
                            item['synonyms'].append(child.text)
                        elif tag.startswith(SKOS) and value:
                            item['mappings'].append({'predicate': tag, 'object': value})
                        elif tag == OWL + 'deprecated':
                            item['deprecated'] = child.text in ('true', '1')
                    classes[uri] = item
            el.clear()
        depth -= 1
    return classes, metadata


def ancestors(classes, anchor):
    seen, pending = set(), [anchor]
    while pending:
        uri = pending.pop()
        if uri in seen:
            continue
        if uri not in classes:
            raise ValueError(f'Named parent missing from OWL input: {uri}')
        seen.add(uri)
        pending.extend(classes[uri]['parents'])
    return [classes[u] for u in sorted(seen)]


def parquet_rows(path, columns=None):
    """Bound memory and retain stable zero-based physical row locators."""
    offset = 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=4096, columns=columns):
        for i, row in enumerate(batch.to_pylist()):
            yield offset + i, row
        offset += batch.num_rows


def hpo_rows(path):
    with path.open() as f:
        lines = ((i, line) for i, line in enumerate(f, 1) if not line.startswith('#'))
        _, header = next(lines)
        fields = header.rstrip('\n').split('\t')
        for line_no, line in lines:
            values = next(csv.reader([line], delimiter='\t'))
            if len(values) != len(fields):
                raise ValueError(f'Malformed HPOA line {line_no}')
            yield line_no, dict(zip(fields, values))
