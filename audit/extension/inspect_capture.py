"""Verify capture identity and inspect exact-anchor clinical joins, offline."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'data/extensions/opentargets-26.09'
ANCHOR = 'MONDO_0005148'


def main():
    manifest = json.loads((BASE / 'capture_manifest.json').read_text())
    tables, schemas = {}, {}
    for record in manifest['files']:
        path = ROOT / record['path']
        if path.stat().st_size != record['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f'Capture identity mismatch: {path.name}')
    for name in manifest['scope']:
        expected = set(re.findall(r'href="([^"/?]+\.parquet)"', (BASE / (name + '-index.html')).read_text()))
        paths = sorted((BASE / name).glob('*.parquet'))
        if {p.name for p in paths} != expected:
            raise ValueError(f'Partition coverage mismatch: {name}')
        rows = []
        for path in paths:
            table = pq.read_table(path)
            schemas[name] = str(table.schema)
            rows.extend({'file': str(path.relative_to(ROOT)), 'row_index_zero_based': index, 'payload': row}
                        for index, row in enumerate(table.to_pylist()))
        tables[name] = rows
    diseases = [r for r in tables['disease'] if r['payload']['id'] == ANCHOR]
    if len(diseases) != 1:
        raise ValueError('Anchor must resolve to exactly one source disease record')
    indications = [r for r in tables['clinical_indication'] if r['payload']['diseaseId'] == ANCHOR]
    targets = [r for r in tables['clinical_target'] if any(d and d.get('diseaseId') == ANCHOR for d in r['payload']['diseases'] or [])]
    drugs = {r['payload']['drugId'] for r in indications}
    mechanisms = [r for r in tables['drug_mechanism_of_action'] if drugs.intersection(r['payload']['chemblIds'] or [])]
    pairs = {(d,t) for r in mechanisms for d in r['payload']['chemblIds'] or [] for t in r['payload']['targets'] or [] if d in drugs}
    target_pairs = {(r['payload']['drugId'],r['payload']['targetId']) for r in targets}
    output = ROOT / 'reports/extension'
    output.mkdir(parents=True, exist_ok=True)
    summary = {'release': manifest['release'], 'anchor': ANCHOR, 'anchor_name': diseases[0]['payload']['name'],
        'capture_manifest_sha256': hashlib.sha256((BASE / 'capture_manifest.json').read_bytes()).hexdigest(),
        'source_rows': {name: len(rows) for name, rows in tables.items()},
        'indication_rows': len(indications), 'indication_drugs': len(drugs),
        'indication_stages': dict(sorted(Counter(r['payload']['maxClinicalStage'] for r in indications).items())),
        'clinical_target_rows': len(targets), 'clinical_target_unique_pairs': len(target_pairs),
        'clinical_target_drugs': len({d for d,t in target_pairs}), 'clinical_targets': len({t for d,t in target_pairs}),
        'clinical_target_pairs_with_exact_indication': sum(d in drugs for d,t in target_pairs),
        'mechanism_rows_for_indication_drugs': len(mechanisms),
        'clinical_target_pairs_matching_indication_and_mechanism': len(target_pairs & pairs),
        'clinical_target_pairs_without_matching_indication_and_mechanism': len(target_pairs - pairs),
        'all_captured_hashes_verified': True, 'all_listed_partitions_present': True,
        'limitations': ['No general target association tables captured', 'Clinical report IDs retained but their report bodies not captured',
                       'Clinical-target maxClinicalStage is aggregate over its disease context; not treated as T2DM-specific approval',
                       'No drug or target catalog labels joined from another release', 'No RDF extension integrated']}
    (output / 'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (BASE / 'selected_records.json').write_text(json.dumps({'disease': diseases, 'indications': indications, 'clinical_targets': targets, 'mechanisms': mechanisms},indent=2)+'\n')
    (BASE / 'schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
