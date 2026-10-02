"""Compare final RDF with raw Parquet independently of the graph constructor."""
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import pyarrow.parquet as pq
from rdflib import Dataset, Namespace, RDF, URIRef
from rdflib.namespace import PROV

ROOT = Path(__file__).resolve().parents[2]
EX = Namespace('https://example.org/clinical-kg/extension/')
ANCHOR = URIRef('http://purl.obolibrary.org/obo/MONDO_0005148')
OUT = ROOT / 'data/extensions/opentargets-26.09/final'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    files = {}
    for name in ('capture_manifest.json', 'clinical_report_manifest.json'):
        manifest = json.loads((ROOT/'reports/extension'/name).read_text())
        require(manifest['release'] == '26.09', 'Release mismatch')
        for entry in manifest['files']:
            path = ROOT/entry['path']
            require(path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], 'Capture mismatch')
            files[entry['path']] = entry
    summary = json.loads((ROOT/'reports/final/extension_summary.json').read_text())
    for name, expected in summary['artifacts'].items():
        require(sha(OUT/name) == expected, 'Output hash mismatch')
    ds = Dataset(); ds.parse(OUT/'extension.nq', format='nquads')
    g = ds.graph(EX['graph/records']); p = ds.graph(EX['graph/provenance'])
    reports = ds.graph(EX['graph/reports']); links = ds.graph(EX['graph/clinical-context'])
    records = set(g.subjects(RDF.type, None)); report_nodes = set(reports.subjects(RDF.type, EX.ClinicalReport))
    locators = {}; payloads = {}
    for node in records | report_nodes:
        snapshots = list(p.objects(node, PROV.wasDerivedFrom)); indices = list(p.objects(node, EX.rowIndex))
        values = list(p.objects(node, EX.payload)); activities = list(p.objects(node, PROV.wasGeneratedBy))
        require(len(snapshots) == len(indices) == len(values) == len(activities) == 1, 'Lineage cardinality')
        snap = snapshots[0]; path = str(p.value(snap, EX.path)); entry = files[path]
        require(str(p.value(snap, EX.sha256)) == entry['sha256'], 'Snapshot hash')
        require(str(p.value(snap, PROV.atLocation)) == entry['url'], 'Snapshot URL')
        require(str(p.value(snap, EX.release)) == '26.09', 'Snapshot release')
        require(str(p.value(snap, EX.sourceProvider)) == 'Open Targets Platform', 'Snapshot provider')
        require((activities[0], RDF.type, PROV.Activity) in p, 'Missing activity')
        key = (path, int(indices[0])); require(key not in locators, 'Duplicate row locator')
        locators[key] = node; payloads[node] = json.loads(str(values[0]))
    checked = set(); raw_tables = {}; raw_report_ids = Counter()
    for path, entry in files.items():
        if not path.endswith('.parquet'): continue
        table = Path(path).parent.name; rows = []; index = 0
        for batch in pq.ParquetFile(ROOT/path).iter_batches(batch_size=1024):
            for value in batch.to_pylist():
                if table == 'clinical-report-capture': raw_report_ids[value['id']] += 1
                else: rows.append(value)
                key = (path, index)
                if key in locators:
                    normalized = json.loads(json.dumps(value, default=lambda x: x.isoformat() if isinstance(x, date) else None))
                    require(payloads[locators[key]] == normalized, 'Raw payload mismatch')
                    checked.add(key)
                index += 1
        if table != 'clinical-report-capture': raw_tables[table] = rows
    require(checked == set(locators), 'Unverified row locator')
    indications = [v for v in raw_tables['clinical_indication'] if v['diseaseId'] == 'MONDO_0005148']
    drugs = {v['drugId'] for v in indications}
    targets = [v for v in raw_tables['clinical_target'] if any(d and d.get('diseaseId') == 'MONDO_0005148' for d in v.get('diseases') or [])]
    mechanisms = [v for v in raw_tables['drug_mechanism_of_action'] if drugs.intersection(v.get('chemblIds') or [])]
    for cls, expected in [(EX.IndicationRecord, indications), (EX.ClinicalTargetRecord, targets), (EX.MechanismRecord, mechanisms)]:
        actual = [payloads[n] for n in g.subjects(RDF.type, cls)]
        encode = lambda values: Counter(json.dumps(v, sort_keys=True) for v in values)
        require(encode(actual) == encode(expected), 'Record selection mismatch')
    by_id = {str(reports.value(n, EX.reportIdentifier)): n for n in report_nodes}
    require(len(by_id) == len(report_nodes), 'Duplicate report IDs')
    wanted = set(); resolved = Counter(); unresolved = Counter(); context = Counter(); evidence_flags = Counter()
    field_map = {'provider': EX.reportProvider, 'source': EX.reportSource, 'origin': EX.reportOrigin,
                 'type': EX.reportType, 'clinicalStage': EX.reportStage, 'phaseFromSource': EX.phaseFromSource, 'url': EX.reportURL}
    for rid, node in by_id.items():
        value = payloads[node]; require(value['id'] == rid and raw_report_ids[rid] == 1, 'Report identity')
        missing = set()
        for key, predicate in field_map.items():
            expected = value.get(key)
            if expected is None or expected == '':
                missing.add(key); require(not list(reports.objects(node, predicate)), 'Invented metadata')
            else: require([str(v) for v in reports.objects(node, predicate)] == [str(expected)], 'Report field mismatch')
        require({str(v) for v in reports.objects(node, EX.unresolvedField)} == missing, 'Missing metadata state')
        flags = value.get('qualityControls')
        state = 'absent' if 'qualityControls' not in value else 'null' if flags is None else 'empty' if not flags else 'present'
        require(str(reports.value(node, EX.qualityFieldState)) == state, 'QC state mismatch')
        require({str(v) for v in reports.objects(node, EX.qualityFlag)} == set(flags or []), 'QC flags mismatch')
    for node in records:
        value = payloads[node]; cls = g.value(node, RDF.type)
        refs = set(value.get('clinicalReportIds') or []); wanted.update(refs)
        require({str(v) for v in g.objects(node, EX.reportIdentifier)} == refs, 'Reference literals mismatch')
        expected = {by_id[rid] for rid in refs if rid in by_id}
        require(set(g.objects(node, EX.resolvedReport)) == expected, 'Resolution edge mismatch')
        missing = refs - by_id.keys()
        require({str(v) for v in g.objects(node, EX.unresolvedReportIdentifier)} == missing, 'Unresolved reference mismatch')
        resolved[str(cls).rsplit('/', 1)[-1]] += len(expected)
        unresolved[str(cls).rsplit('/', 1)[-1]] += len(missing)
        if cls in (EX.IndicationRecord, EX.ClinicalTargetRecord):
            predicate = EX.indicationStage if cls == EX.IndicationRecord else EX.aggregateStage
            stage = value.get('maxClinicalStage')
            require({str(v) for v in g.objects(node, predicate)} == ({stage} if stage else set()), 'Stage scope mismatch')
            for report in expected:
                rv = payloads[report]
                has_drug = value['drugId'] in {d.get('drugId') for d in rv.get('drugs') or [] if d}
                has_disease = 'MONDO_0005148' in {d.get('diseaseId') for d in rv.get('diseases') or [] if d}
                context[f'{str(cls).rsplit("/", 1)[-1]}:drug={has_drug},disease={has_disease}'] += 1
                if rv.get('qualityControls'): evidence_flags[str(cls).rsplit('/', 1)[-1]] += 1
    require(set(by_id) == wanted, 'Report selection coverage')
    expected_pairs = {(v['drugId'], v['targetId']) for v in targets}
    mechanism_pairs = {(drug, target) for v in mechanisms for drug in v.get('chemblIds') or [] for target in v.get('targets') or []}
    require(expected_pairs <= mechanism_pairs and all(d in drugs for d, _ in expected_pairs), 'Unsupported source join')
    actual_pairs = set(); evidence_links = 0
    for link in links.subjects(RDF.type, EX.ClinicalContextLink):
        drug = links.value(link, EX.drug); target = links.value(link, EX.target)
        require(links.value(link, EX.disease) == ANCHOR, 'Path disease mismatch')
        actual_pairs.add((str(drug).rsplit('/', 1)[-1], str(target).rsplit('/', 1)[-1]))
        evidence = set(links.objects(link, PROV.wasDerivedFrom)); evidence_links += len(evidence)
        expected_evidence = set()
        for record in records:
            cls = g.value(record, RDF.type)
            if (record, EX.drug, drug) not in g: continue
            if cls == EX.IndicationRecord and (record, EX.disease, ANCHOR) in g: expected_evidence.add(record)
            if cls in (EX.MechanismRecord, EX.ClinicalTargetRecord) and (record, EX.target, target) in g: expected_evidence.add(record)
        require(evidence == expected_evidence, 'Path evidence mismatch')
        require({g.value(n, RDF.type) for n in evidence} == {EX.IndicationRecord, EX.MechanismRecord, EX.ClinicalTargetRecord}, 'Missing support type')
    require(actual_pairs == expected_pairs, 'Path coverage mismatch')
    for predicate, allowed in [(EX.indicationStage, set(g.subjects(RDF.type, EX.IndicationRecord))),
                               (EX.aggregateStage, set(g.subjects(RDF.type, EX.ClinicalTargetRecord))),
                               (EX.reportStage, report_nodes)]:
        require({s for s, _, _, _ in ds.quads((None, predicate, None, None))} <= allowed, 'Stage leaked to other scope')
    results = json.loads((OUT/'query_results.json').read_text())
    actual_indications = {(r['drug'].rsplit('/', 1)[-1], r['stage']) for r in results['05_indications']}
    require(actual_indications == {(v['drugId'], v.get('maxClinicalStage')) for v in indications}, 'Indication query mismatch')
    require({(r['drug'].rsplit('/', 1)[-1], r['target'].rsplit('/', 1)[-1]) for r in results['06_supported_clinical_paths']} == expected_pairs, 'Path query mismatch')
    require({r['target'].rsplit('/', 1)[-1] for r in results['04_clinical_context_targets']} == {t for _, t in expected_pairs}, 'Target query mismatch')
    require({str(c.identifier): len(c) for c in ds.graphs() if len(c)} == summary['named_graph_counts'], 'Serialized graph counts')
    require(sum(len(c) for c in ds.graphs()) == summary['graph_counts']['quads'], 'Serialized quad count')
    for path, entry in files.items(): require(sha(ROOT/path) == entry['sha256'], 'Input changed during verification')
    result = {'all_checks_passed': True, 'verified_raw_payloads': len(checked), 'verified_report_records': len(report_nodes),
              'resolved_reference_edges': sum(resolved.values()), 'unresolved_reference_edges': sum(unresolved.values()),
              'resolved_by_record_type': dict(resolved), 'report_reference_context': dict(context),
              'references_with_qc_flags': dict(evidence_flags), 'clinical_paths': len(actual_pairs), 'path_evidence_links': evidence_links,
              'serialized_quads': sum(len(c) for c in ds.graphs()), 'verifier_sha256': sha(Path(__file__)),
              'scope': 'Independent raw-record comparison; shared RDFLib and PyArrow libraries. No clinical truth or regulatory verification.'}
    (ROOT/'reports/final/extension_verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__': main()
