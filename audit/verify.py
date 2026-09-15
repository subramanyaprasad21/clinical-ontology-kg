"""Independent checks of source facts, provenance, inference and validation.

Does not import production extraction/build helpers. Writes audit evidence only;
never modifies source inputs, ontology, canonical RDF, or production tests.
"""
import csv
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
import xml.etree.ElementTree as ET

import pyarrow.parquet as pq
from rdflib import BNode, Dataset, Graph, Literal, Namespace, RDF, RDFS, OWL, SKOS, URIRef
from rdflib.namespace import PROV, SH
from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/credibility_audit'
KG = Namespace('https://example.org/clinical-kg/')
OBO = Namespace('http://purl.obolibrary.org/obo/')
OIO = Namespace('http://www.geneontology.org/formats/oboInOwl#')
ANCHOR = OBO.MONDO_0005148
OMIM = URIRef('https://omim.org/entry/125853')
checks = []


def check(name, passed, detail=None):
    checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    if not passed:
        print('DISCREPANCY:', name, detail, flush=True)


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def hashfile(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def scan_classes(path, wanted):
    """Build parent index from raw XML; parse selected complete class fragments as RDF."""
    parents, selected, versions, labels = {}, {}, [], {}
    depth = 0
    for event, el in ET.iterparse(path, events=('start', 'end')):
        depth += 1 if event == 'start' else 0
        if event == 'end':
            if depth == 2:
                if el.tag == '{' + str(OWL) + '}Ontology':
                    versions = [x.get('{' + str(RDF) + '}resource') for x in el.findall('{' + str(OWL) + '}versionIRI')]
                elif el.tag == '{' + str(OWL) + '}Class':
                    u = el.get('{' + str(RDF) + '}about')
                    if u:
                        parents[u] = [x.get('{' + str(RDF) + '}resource') for x in el.findall('{' + str(RDFS) + '}subClassOf')
                                      if x.get('{' + str(RDF) + '}resource')]
                        labels[u] = [x.text for x in el.findall('{' + str(RDFS) + '}label')]
                        if u in wanted:
                            fragment = '<rdf:RDF xmlns:rdf="' + str(RDF) + '">' + ET.tostring(el, encoding='unicode') + '</rdf:RDF>'
                            selected[u] = Graph().parse(data=fragment, format='xml')
                el.clear()
            depth -= 1
    return parents, selected, versions, labels


def closure(graph):
    result = Graph() + graph
    DeductiveClosure(OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(result)
    return result


def validation(graph, shapes):
    conforms, report, _ = validate(graph, shacl_graph=shapes, inference='none', advanced=False)
    counts = Counter(str(v).rsplit('#', 1)[-1] for v in report.objects(None, SH.sourceConstraintComponent))
    rows = []
    for node in report.subjects(RDF.type, SH.ValidationResult):
        rows.append({key: str(report.value(node, prop)) for key, prop in
                     [('focus', SH.focusNode), ('path', SH.resultPath), ('component', SH.sourceConstraintComponent), ('message', SH.resultMessage)]})
    return {'conforms': bool(conforms), 'constraint_counts': dict(counts), 'violations': sorted(rows, key=lambda x: json.dumps(x, sort_keys=True))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'config/input_manifest.json').read_text())
    files = {str(p.relative_to(ROOT)): p for p in (ROOT / 'data/raw').rglob('*') if p.suffix in ('.owl', '.parquet', '.hpoa')}
    check('Exactly 11 raw biomedical input files', len(files) == 11)
    check('Manifest paths unique and match raw inventory', len(manifest['inputs']) == len(files) and {r['path'] for r in manifest['inputs']} == set(files))
    check('All frozen SHA-256 and sizes match', all(hashfile(files[r['path']]) == r['sha256'] and files[r['path']].stat().st_size == r['bytes'] for r in manifest['inputs']))
    ds = Dataset().parse(ROOT / 'data/processed/knowledge_graph.nq', format='nquads')
    source_graphs = {str(g.identifier).split('/source/')[1]: g for g in ds.graphs() if '/graph/source/' in str(g.identifier)}
    source = Graph()
    for g in source_graphs.values():
        source += g
    schema, inferred, provenance = [ds.graph(KG['graph/' + x]) for x in ('schema', 'inferred', 'provenance')]
    source_quads = {(s, p, o, g.identifier) for g in source_graphs.values() for s, p, o in g}
    wanted = {str(u) for u in source.subjects(RDF.type, OWL.Class)}
    parent_index, raw_mondo, mondo_version, labels = scan_classes(ROOT / 'data/raw/mondo/mondo.owl', wanted)
    seen, queue = set(), deque([str(ANCHOR)])
    while queue:
        node = queue.popleft()
        if node not in seen:
            seen.add(node)
            queue.extend(parent_index[node])
    check('Full named-parent closure matches exported classes', seen == wanted, {'count': len(seen)})
    raw_edges = {(URIRef(u), RDFS.subClassOf, URIRef(v)) for u in seen for v in parent_index[u]}
    check('Every named Mondo subclass edge matches raw XML', set(source_graphs['mondo'].triples((None, RDFS.subClassOf, None))) == raw_edges,
          {'edges': len(raw_edges), 'anchor_parents': parent_index[str(ANCHOR)]})
    check('Unique T2DM label identifies expected class', [u for u, v in labels.items() if 'type 2 diabetes mellitus' in v] == [str(ANCHOR)])
    anchor_raw = raw_mondo[str(ANCHOR)]
    check('All ten exact mappings equal raw Mondo assertions', set(source.triples((ANCHOR, SKOS.exactMatch, None))) == set(anchor_raw.triples((ANCHOR, SKOS.exactMatch, None))))
    check('Anchor xrefs preserved', set(source.objects(ANCHOR, KG.sourceXref)) == set(anchor_raw.objects(ANCHOR, OIO.hasDbXref)))
    check('Exact synonyms transformed to altLabel without additions', set(source.objects(ANCHOR, SKOS.altLabel)) == set(anchor_raw.objects(ANCHOR, OIO.hasExactSynonym)))
    check('OMIM join is explicitly source mapped', (ANCHOR, SKOS.exactMatch, OMIM) in anchor_raw)
    lines = (ROOT / 'data/raw/hpo/phenotype.hpoa').read_text().splitlines()
    header_i = next(i for i, x in enumerate(lines) if not x.startswith('#'))
    fields = lines[header_i].split('\t')
    raw_hpo = {f'line:{i + 1}': dict(zip(fields, next(csv.reader([line], delimiter='\t')))) for i, line in enumerate(lines)
               if i > header_i and line.startswith('OMIM:125853\t')}
    check('Five HPO rows with P/P/P/I/C aspects', len(raw_hpo) == 5 and Counter(r['aspect'] for r in raw_hpo.values()) == {'P': 3, 'I': 1, 'C': 1})
    predicates = {'P': KG.hasPhenotype, 'I': KG.hasInheritanceAnnotation, 'C': KG.hasClinicalModifier}
    expected_hpo = {(OMIM, predicates[r['aspect']], OBO[r['hpo_id'].replace(':', '_')]) for r in raw_hpo.values()}
    actual_hpo = {t for t in source_graphs['hpo-annotations'] if t[1] in predicates.values()}
    check('HPO source annotation edges match raw aspects and identifiers', expected_hpo == actual_hpo)
    hp_wanted = {str(u) for u in source.subjects(RDF.type, KG.HPOTerm)}
    _, raw_hp, hp_version, _ = scan_classes(ROOT / 'data/raw/hpo/hp.owl', hp_wanted)
    check('Every HPO label resolves exactly to the raw ontology', all(set(source.objects(URIRef(u), RDFS.label)) == set(g.objects(URIRef(u), RDFS.label)) for u, g in raw_hp.items()) and len(raw_hp) == 5)
    # Independent Parquet reader scans row groups; verify stored physical row locators.
    raw_ot, schemas = {}, {}
    for p in sorted((ROOT / 'data/raw/open_targets').rglob('*.parquet')):
        f = pq.ParquetFile(p)
        schemas[str(p.relative_to(ROOT))] = {'rows': f.metadata.num_rows, 'schema': str(f.schema_arrow), 'columns': f.schema_arrow.names}
        if p.name in ('disease.parquet', 'disease_phenotype.parquet'):
            offset = 0
            for rg in range(f.num_row_groups):
                rows = f.read_row_group(rg).to_pylist()
                for i, row in enumerate(rows):
                    if row.get('id', row.get('disease')) == 'MONDO_0005148':
                        raw_ot[(str(p.relative_to(ROOT)), f'row:{offset + i}')] = row
                offset += len(rows)
    disease = [r for (p, _), r in raw_ot.items() if p.endswith('/disease.parquet')]
    check('OT uniquely preserves anchor code and parent', len(disease) == 1 and disease[0]['code'] == str(ANCHOR) and disease[0]['parents'] == ['MONDO_0005015'])
    ot_pheno = [r for (p, _), r in raw_ot.items() if p.endswith('/disease_phenotype.parquet')]
    check('OT has five phenotype rows, ten evidence occurrences', len(ot_pheno) == 5 and sum(len(r['evidence']) for r in ot_pheno) == 10)
    hpo_signatures = {(r['hpo_id'].replace(':', '_'), r['aspect'], r['evidence'], r['reference'], r['database_id'], r['biocuration']) for r in raw_hpo.values()}
    ot_signatures = {(r['phenotype'], e['aspect'], e['evidenceType'], ';'.join(e['references']), e['diseaseFromSourceId'], e['bioCuration']) for r in ot_pheno for e in r['evidence']}
    check('OT and HPO evidence signatures agree; all OT resource=HPO', hpo_signatures == ot_signatures and all(e['resource'] == 'HPO' for r in ot_pheno for e in r['evidence']))
    expected_ot = {(ANCHOR, predicates[e['aspect']], OBO[r['phenotype']]) for r in ot_pheno for e in r['evidence']}
    check('OT annotation edges match raw rows', expected_ot == set(source_graphs['ot-phenotypes']))
    target_ids, drug_ids = set(), set()
    for subdir, ids in [('target', target_ids), ('drug_molecule', drug_ids)]:
        for path in (ROOT / 'data/raw/open_targets' / subdir).glob('*.parquet'):
            ids.update(pq.read_table(path, columns=['id'])['id'].to_pylist())
    mechanisms = [r for p in sorted((ROOT / 'data/raw/open_targets/drug_mechanism_of_action').glob('*.parquet')) for r in pq.read_table(p).to_pylist()]
    targets = [t for r in mechanisms for t in r['targets']]
    drugs = [d for r in mechanisms for d in r['chemblIds']]
    check('Every mechanism catalog identifier resolves', set(targets) <= target_ids and set(drugs) <= drug_ids,
          {'records': len(mechanisms), 'target_references': len(targets), 'drug_references': len(drugs), 'target_catalog': len(target_ids), 'drug_catalog': len(drug_ids)})
    check('No structured disease/indication columns in target/drug/mechanism schemas', all(not any(t in s['columns'] for t in ('diseaseId', 'disease', 'indications', 'indication', 'diseases')) for p, s in schemas.items() if '/target/' in p or '/drug_' in p))
    dump('raw_schemas.json', schemas)
    # Verify every source record's selected fields against original data, not the cached audit.
    record_results = []
    for rec in sorted(provenance.subjects(RDF.type, KG.SourceRecord), key=str):
        snapshot = provenance.value(rec, PROV.wasDerivedFrom)
        path = str(provenance.value(snapshot, KG.path))
        loc = str(provenance.value(rec, KG.locator))
        payload = json.loads(str(provenance.value(rec, KG.payload)))
        original = str(provenance.value(rec, KG.originalIdentifier))
        if path.endswith('.hpoa'):
            ok = payload == raw_hpo.get(loc) and original == payload['database_id']
        elif path.endswith('.parquet'):
            rowloc, _, suffix = loc.partition('/evidence:')
            row = raw_ot.get((path, rowloc))
            expected = {'disease': row['disease'], 'phenotype': row['phenotype'], 'evidence': row['evidence'][int(suffix)]} if suffix else row
            ok = payload == expected and original == payload.get('id', payload.get('disease'))
        else:
            u = original
            raw = (raw_mondo if '/mondo/' in path else raw_hp)[u]
            uri = URIRef(u)
            ok = (loc == 'owl:Class:' + u and payload['uri'] == u
                  and sorted(payload['labels']) == sorted(str(x) for x in raw.objects(uri, RDFS.label))
                  and sorted(payload['parents']) == sorted(str(x) for x in raw.objects(uri, RDFS.subClassOf) if isinstance(x, URIRef))
                  and sorted(payload['synonyms']) == sorted(str(x) for x in raw.objects(uri, OIO.hasExactSynonym))
                  and sorted(payload['xrefs']) == sorted(str(x) for x in raw.objects(uri, OIO.hasDbXref))
                  and {(m['predicate'], m['object']) for m in payload['mappings']} == {(str(p), str(o)) for _, p, o in raw.triples((uri, None, None)) if str(p).startswith(str(SKOS))}
                  and len(payload['restrictions_xml']) == sum(isinstance(x, BNode) for x in raw.objects(uri, RDFS.subClassOf)))
        record_results.append({'record': str(rec), 'path': path, 'locator': loc, 'matches_raw_selected_fields': ok})
    check('All selected-field source record payloads and original IDs match raw records', all(r['matches_raw_selected_fields'] for r in record_results), {'records': len(record_results)})
    covered, classifications = set(), Counter()
    provenance_errors = []
    manifest_by_path = {r['path']: r for r in manifest['inputs']}
    for stmt in provenance.subjects(RDF.type, KG.ImportedAssertion):
        values = {p: list(provenance.objects(stmt, p)) for p in (RDF.subject, RDF.predicate, RDF.object, PROV.wasDerivedFrom, PROV.wasGeneratedBy, KG.assertedIn)}
        if any(len(v) != 1 for v in values.values()):
            provenance_errors.append(str(stmt)); continue
        s, p, o, rec, event, gid = [values[k][0] for k in values]
        snapshot = provenance.value(rec, PROV.wasDerivedFrom)
        path = str(provenance.value(snapshot, KG.path))
        if (s, p, o, gid) not in source_quads or path not in manifest_by_path or (event, RDF.type, PROV.Activity) not in provenance:
            provenance_errors.append(str(stmt)); continue
        item = manifest_by_path[path]
        if any(str(provenance.value(snapshot, KG[k])) != item[k] for k in ('source', 'version', 'sha256')):
            provenance_errors.append(str(stmt)); continue
        if (stmt, RDF.type, KG.MappingAssertion) in provenance:
            if p not in (SKOS.exactMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.relatedMatch, SKOS.closeMatch) or not provenance.value(stmt, KG.mappingMethod):
                provenance_errors.append(str(stmt)); continue
        covered.add((s, p, o, gid))
        # Direct source RDF vs project projection (not a per-statement flag in current graph).
        direct = path.endswith('mondo.owl') and (s, p, o) in raw_mondo.get(str(s), Graph())
        direct |= path.endswith('hp.owl') and (s, p, o) in raw_hp.get(str(s), Graph())
        classifications['direct_source_RDF' if direct else 'mapped_or_normalized_source_information'] += 1
    check('179 assertion chains complete and reconstructable to snapshots', not provenance_errors and sum(classifications.values()) == 179)
    check('Every one of 174 source quads has verified assertion provenance', covered == source_quads, {'covered': len(covered), 'total': len(source_quads)})
    dump('provenance_checks.json', {'records': record_results, 'assertion_errors': provenance_errors, 'assertion_categories': dict(classifications),
                                 'coverage_percent': 100 * len(covered) / len(source_quads)})
    check('No source owl:sameAs mappings', not list(source.triples((None, OWL.sameAs, None))))
    check('No nonreflexive inferred owl:sameAs identity merges', not any(s != o for s, _, o in inferred.triples((None, OWL.sameAs, None))))
    check('No synthetic URNs or malformed fixture literals in canonical dataset', not any('urn:synthetic:' in str(t) or str(t) == 'not an IRI' for quad in ds.quads() for t in quad))
    check('No invented clinical drug-target predicates', not any(list(source.triples((None, p, None))) for p in (KG.treats, KG.targets, KG.indicatedFor, KG.associatedTarget)))
    # Recompute closure from exported premises independently of the production reason() helper.
    premises = source + schema
    result = closure(premises)
    expected = {t for t in result if t not in premises and isinstance(t[0], (BNode, URIRef)) and isinstance(t[1], URIRef)}
    check('Exported inference exactly equals independent OWL RL closure delta', expected == set(inferred), {'exported': len(inferred), 'overlap_with_asserted': len(set(inferred) & set(source))})
    check('No inferred fact is explicitly present among premises', not (set(inferred) & set(premises)))
    meaningful = []
    for entity in (ANCHOR, OMIM):
        fact = (entity, RDF.type, KG.PhenotypeAnnotatedConcept)
        positives = list(source.triples((entity, KG.hasPhenotype, None)))
        meaningful.append({'kind': 'defined class membership', 'asserted': [[str(x) for x in t] for t in positives] + [[str(entity), str(RDF.type), str(KG.DiseaseConcept)]],
                           'axiom': 'DiseaseConcept intersection (hasPhenotype some HPOTerm) equivalentClass PhenotypeAnnotatedConcept',
                           'inferred': [str(x) for x in fact], 'new': fact in inferred and fact not in premises})
    for s, p, o in source.triples((None, KG.hasPhenotype, None)):
        meaningful.append({'kind': 'inverse property', 'asserted': [[str(s), str(p), str(o)]],
                          'axiom': 'hasPhenotype owl:inverseOf phenotypeOf', 'inferred': [str(o), str(KG.phenotypeOf), str(s)],
                          'new': (o, KG.phenotypeOf, s) in inferred and (o, KG.phenotypeOf, s) not in premises})
    for target in sorted(inferred.objects(ANCHOR, RDFS.subClassOf), key=str):
        if target == ANCHOR or not str(target).startswith(str(OBO)):
            continue
        queue = deque([(str(ANCHOR), [])]); path = []
        while queue:
            node, steps = queue.popleft()
            if node == str(target):
                path = steps; break
            queue.extend((v, steps + [[node, str(RDFS.subClassOf), v]]) for v in parent_index[node] if v not in {a[0] for a in steps})
        meaningful.append({'kind': 'named subclass transitivity', 'asserted': path, 'axiom': 'rdfs:subClassOf transitivity (OWL RL rule)',
                          'inferred': [str(ANCHOR), str(RDFS.subClassOf), str(target)], 'new': bool(path) and len(path) > 1})
    check('Every meaningful inference has a source-premise path and is new', all(e['new'] for e in meaningful), {'examples': len(meaningful)})
    # A real-data ablation: remove positive facts, leaving other annotations intact.
    ablated = Graph() + premises
    ablated.remove((None, KG.hasPhenotype, None))
    ablated_result = closure(ablated)
    check('Positive-annotation ablation removes both class memberships and inverse facts', not any(ablated_result.triples((None, RDF.type, KG.PhenotypeAnnotatedConcept))) and not any(ablated_result.triples((None, KG.phenotypeOf, None))))
    dump('inference_chains.json', meaningful)
    canonical = source + schema + provenance
    shapes = Graph().parse(ROOT / 'ontology/shapes/shapes.ttl')
    canonical_before = set(canonical)
    canonical_validation = validation(canonical, shapes)
    check('Independent canonical SHACL run conforms', canonical_validation['conforms'])
    stmt = sorted(provenance.subjects(RDF.type, KG.ImportedAssertion), key=str)[0]
    snapshot = sorted(provenance.subjects(RDF.type, KG.SourceSnapshot), key=str)[0]
    mapping = sorted(provenance.subjects(RDF.type, KG.MappingAssertion), key=str)[0]
    mutations = {
      'missing_label': (lambda g: g.remove((ANCHOR, RDFS.label, None)), {'MinCountConstraintComponent'}),
      'missing_identifier': (lambda g: g.remove((ANCHOR, KG.identifier, None)), {'MinCountConstraintComponent'}),
      'missing_assertion_provenance': (lambda g: g.remove((stmt, PROV.wasDerivedFrom, None)), {'MinCountConstraintComponent'}),
      'missing_source_version': (lambda g: g.remove((snapshot, KG.version, None)), {'MinCountConstraintComponent'}),
      'malformed_phenotype_target': (lambda g: g.add((ANCHOR, KG.hasPhenotype, Literal('not an IRI'))), {'ClassConstraintComponent', 'NodeKindConstraintComponent'}),
      'illegal_mapping_predicate': (lambda g: (g.remove((mapping, RDF.predicate, None)), g.add((mapping, RDF.predicate, OWL.sameAs))), {'InConstraintComponent'}),
    }
    cases = {}
    for name, (mutate, expected_components) in mutations.items():
        altered = Graph() + canonical
        mutate(altered)
        observed = validation(altered, shapes)
        observed['expected_components'] = sorted(expected_components)
        observed['expected_detected'] = expected_components == set(observed['constraint_counts']) and not observed['conforms']
        cases[name] = observed
    check('All six isolated mutations detect expected violation components', all(x['expected_detected'] for x in cases.values()))
    check('Invalid-case audit leaves canonical graph unchanged', canonical_before == set(canonical))
    # Deliberate coverage probes reveal limits; they are not expected to conform semantically.
    probes = {}
    altered = Graph() + canonical
    altered.add((ANCHOR, KG.hasHPOAnnotation, Literal('audit-only bad generic endpoint')))
    probes['unshaped_generic_annotation_endpoint'] = validation(altered, shapes)
    altered = Graph() + canonical
    altered.add((ANCHOR, KG.hasExcludedPhenotype, OBO.HP_0000855))
    probes['simultaneous_positive_and_excluded_annotation'] = validation(altered, shapes)
    dump('shacl_checks.json', {'canonical': canonical_validation, 'invalid_cases': cases, 'uncovered_semantic_probes': probes,
                              'canonical_unchanged': canonical_before == set(canonical)})
    stored = json.loads((ROOT / 'reports/tables/competency_results.json').read_text())
    query_results = {}
    for p in sorted((ROOT / 'queries/competency').glob('*.rq')):
        response = ds.query(p.read_text())
        rows = [{str(v): str(row[v]) if row[v] is not None else None for v in response.vars} for row in response]
        query_results[p.stem] = {'rows': rows, 'row_count': len(rows), 'matches_saved_results': rows == stored[p.stem]['rows']}
    check('All 11 queries execute and reproduce stored result rows', len(query_results) == 11 and all(r['matches_saved_results'] for r in query_results.values()))
    dump('query_checks.json', query_results)
    dump('source_trace.json', {'anchor': str(ANCHOR), 'parent_edges': [[str(x) for x in t] for t in sorted(raw_edges, key=str)],
                              'mondo_version': mondo_version, 'hpo_version': hp_version,
                              'hpoa_header': lines[:header_i], 'hpo_rows': raw_hpo,
                              'ot_disease': disease, 'ot_phenotypes': ot_pheno,
                              'anchor_mappings': sorted([[str(p), str(o)] for _, p, o in anchor_raw.triples((ANCHOR, None, None)) if str(p).startswith(str(SKOS))]),
                              'anchor_synonyms': sorted(str(x) for x in anchor_raw.objects(ANCHOR, OIO.hasExactSynonym)),
                              'anchor_xrefs': sorted(str(x) for x in anchor_raw.objects(ANCHOR, OIO.hasDbXref))})
    check('Raw files still match frozen hashes after audit', all(hashfile(files[r['path']]) == r['sha256'] for r in manifest['inputs']))
    dump('verification.json', {'checks': checks, 'passed': sum(c['passed'] for c in checks), 'total': len(checks),
                              'audit_script_sha256': hashfile(Path(__file__))})
    print(f"Independent audit: {sum(c['passed'] for c in checks)}/{len(checks)} checks pass. See coverage probes separately.")
    if not all(c['passed'] for c in checks):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
