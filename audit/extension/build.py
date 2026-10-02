"""Offline record-centric clinical extension; never writes core artifacts."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import pyarrow.parquet as pq
from rdflib import Dataset, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import PROV, XSD

ROOT = Path(__file__).resolve().parents[2]
EX = Namespace('https://example.org/clinical-kg/extension/')
ANCHOR = URIRef('http://purl.obolibrary.org/obo/MONDO_0005148')
TABLES = {'disease', 'clinical_indication', 'clinical_target', 'drug_mechanism_of_action'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def ident(kind, value):
    return EX[kind + '/' + hashlib.sha256(canonical(value).encode()).hexdigest()]


def load(root):
    # The committed receipt is the identity authority, not mutable derived JSON.
    receipt = root / 'reports/extension/capture_manifest.json'
    manifest = json.loads(receipt.read_text())
    if manifest['release'] != '26.09' or set(manifest['scope']) != TABLES:
        raise ValueError('Unsupported extension receipt')
    tables = defaultdict(list)
    registered = set()
    for item in manifest['files']:
        path = root / item['path']
        if not path.resolve().is_relative_to((root / 'data/extensions/opentargets-26.09').resolve()):
            raise ValueError('Capture path outside extension directory')
        if path in registered or path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Capture identity mismatch')
        registered.add(path)
        if path.suffix == '.parquet':
            table = path.parent.name
            if table not in TABLES:
                raise ValueError('Unexpected table')
            for index, row in enumerate(pq.read_table(path).to_pylist()):
                tables[table].append({'path': item['path'], 'sha256': item['sha256'], 'row': index, 'payload': row})
    for table in TABLES:
        directory = root / 'data/extensions/opentargets-26.09' / table
        listing = directory.parent / (table + '-index.html')
        if listing not in registered:
            raise ValueError('Unregistered partition listing')
        listed = {directory / n for n in re.findall(r'href="([^"/?]+\.parquet)"', listing.read_text())}
        if not listed or set(directory.glob('*.parquet')) != listed or not listed <= registered:
            raise ValueError('Incomplete partition coverage')
    return tables, manifest


def selected(tables):
    anchor = str(ANCHOR).rsplit('/', 1)[1]
    diseases = [r for r in tables['disease'] if r['payload']['id'] == anchor]
    if len(diseases) != 1:
        raise ValueError('Expected one exact disease anchor')
    indications = [r for r in tables['clinical_indication'] if r['payload']['diseaseId'] == anchor]
    drugs = {r['payload']['drugId'] for r in indications}
    targets = [r for r in tables['clinical_target'] if any(d and d.get('diseaseId') == anchor for d in r['payload'].get('diseases') or [])]
    mechanisms = [r for r in tables['drug_mechanism_of_action'] if drugs.intersection(r['payload'].get('chemblIds') or [])]
    return {'disease': diseases, 'indications': indications, 'clinical_targets': targets, 'mechanisms': mechanisms}


def entity(kind, value):
    pattern = r'CHEMBL\d+' if kind == 'drug' else r'ENSG\d+'
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError(f'Invalid {kind} identifier')
    return URIRef(('https://www.ebi.ac.uk/chembl/compound_report_card/' if kind == 'drug' else 'http://identifiers.org/ensembl/') + value)


def construct(rows, manifest, implementation='test'):
    ds = Dataset()
    source = ds.graph(EX['graph/records'])
    joined = ds.graph(EX['graph/clinical-context'])
    provenance = ds.graph(EX['graph/provenance'])
    snapshots = {}
    activity = ident('build', [manifest, implementation])
    provenance.add((activity, RDF.type, PROV.Activity))
    provenance.add((activity, EX.implementationHash, Literal(implementation)))
    for item in manifest['files']:
        snapshot = ident('snapshot', item['sha256'])
        snapshots[item['path']] = snapshot
        for prop, val in [(EX.sha256, item['sha256']), (EX.path, item['path']),
                          (EX.release, manifest['release']), (EX.retrievedAt, item['retrieved_at'])]:
            provenance.add((snapshot, prop, Literal(val)))
        provenance.add((snapshot, PROV.atLocation, URIRef(item['url'])))
        provenance.add((snapshot, RDF.type, PROV.Entity))
        provenance.add((activity, PROV.used, snapshot))
    record_ids = {}
    def record(row, cls):
        rid = ident('record', [row['sha256'], row['row']])
        if rid in record_ids:
            raise ValueError('Duplicate physical source row')
        record_ids[rid] = row
        source.add((rid, RDF.type, cls))
        provenance.add((rid, RDF.type, PROV.Entity))
        provenance.add((rid, PROV.wasDerivedFrom, snapshots[row['path']]))
        provenance.add((rid, PROV.wasGeneratedBy, activity))
        provenance.add((rid, EX.rowIndex, Literal(row['row'], datatype=XSD.integer)))
        provenance.add((rid, EX.payload, Literal(canonical(row['payload']), datatype=RDF.JSON)))
        return rid
    for row in rows['disease']:
        rid = record(row, EX.DiseaseRecord)
        source.add((rid, EX.disease, ANCHOR))
        source.add((rid, RDFS.label, Literal(row['payload']['name'])))
    indications = defaultdict(list)
    for row in rows['indications']:
        p = row['payload']; rid = record(row, EX.IndicationRecord)
        source.add((rid, EX.disease, ANCHOR))
        source.add((rid, EX.drug, entity('drug', p['drugId'])))
        if p.get('maxClinicalStage') is not None:
            source.add((rid, EX.indicationStage, Literal(p['maxClinicalStage'])))
        for report in set(p.get('clinicalReportIds') or []):
            source.add((rid, EX.reportIdentifier, Literal(report)))
        indications[p['drugId']].append(rid)
    mechanisms = defaultdict(list)
    for row in rows['mechanisms']:
        p = row['payload']; rid = record(row, EX.MechanismRecord)
        for prop, name in [(EX.actionType, 'actionType'), (EX.mechanismDescription, 'mechanismOfAction')]:
            if p.get(name) is not None:
                source.add((rid, prop, Literal(p[name])))
        for drug in set(p.get('chemblIds') or []):
            if drug not in indications:
                continue
            source.add((rid, EX.drug, entity('drug', drug)))
            for target in set(p.get('targets') or []):
                source.add((rid, EX.target, entity('target', target)))
                mechanisms[drug, target].append(rid)
    for row in rows['clinical_targets']:
        p = row['payload']; rid = record(row, EX.ClinicalTargetRecord)
        pair = p['drugId'], p['targetId']
        source.add((rid, EX.drug, entity('drug', pair[0])))
        source.add((rid, EX.target, entity('target', pair[1])))
        source.add((rid, EX.includesDiseaseContext, ANCHOR))
        # Aggregate stage belongs to the original multi-disease row only.
        if p.get('maxClinicalStage') is not None:
            source.add((rid, EX.aggregateStage, Literal(p['maxClinicalStage'])))
        for report in set(p.get('clinicalReportIds') or []):
            source.add((rid, EX.reportIdentifier, Literal(report)))
        if not indications[pair[0]] or not mechanisms[pair]:
            raise ValueError('Clinical context lacks indication or mechanism support')
        link = ident('clinical-context', [str(ANCHOR), *pair])
        joined.add((link, RDF.type, EX.ClinicalContextLink))
        for prop, value in [(EX.disease, ANCHOR), (EX.drug, entity('drug', pair[0])), (EX.target, entity('target', pair[1]))]:
            joined.add((link, prop, value))
        for evidence in [rid, *indications[pair[0]], *mechanisms[pair]]:
            joined.add((link, PROV.wasDerivedFrom, evidence))
        joined.add((link, PROV.wasGeneratedBy, activity))
    return ds


def main():
    tables, manifest = load(ROOT)
    rows = selected(tables)
    files = [Path(__file__), *sorted((Path(__file__).parent / 'queries').glob('*.rq'))]
    implementation = hashlib.sha256(canonical({p.name: digest(p) for p in files}).encode()).hexdigest()
    ds = construct(rows, manifest, implementation)
    out = ROOT / 'data/extensions/opentargets-26.09/derived'
    out.mkdir(exist_ok=True)
    target = out / 'clinical_context.nq'
    target.write_text(''.join(sorted(ds.serialize(format='nquads').splitlines(keepends=True))))
    restored = Dataset(); restored.parse(target, format='nquads')
    if set(restored.quads()) != set(ds.quads()):
        raise ValueError('Extension round trip changed quads')
    results = {}
    for path in sorted((Path(__file__).parent / 'queries').glob('*.rq')):
        result = ds.query(path.read_text())
        data = [{str(v): str(r[v]) if r[v] is not None else None for v in result.vars} for r in result]
        results[path.stem] = data
    (out / 'query_results.json').write_text(json.dumps(results, indent=2, sort_keys=True)+'\n')
    load(ROOT)  # Check captured bytes again after processing.
    summary = {'release': manifest['release'], 'selected_records': {k: len(v) for k,v in rows.items()},
               'named_graph_counts': {str(g.identifier): len(g) for g in ds.graphs() if len(g)},
               'query_rows': {k: len(v) for k,v in results.items()}, 'implementation_sha256': implementation,
               'artifacts': {p.name: digest(p) for p in sorted(out.glob('*')) if p.is_file()},
               'rdf_round_trip_verified': True, 'core_modified': False,
               'semantics': 'Clinical indication/mechanism context only; no general disease-target association or efficacy claim.'}
    (ROOT / 'reports/extension/graph_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
