"""Verify identifiers and available joins before choosing graph content."""
import json
from collections import Counter
import pyarrow.parquet as pq
from .inputs import ANCHOR, OBO, SKOS, ancestors, dump, hpo_rows, parquet_rows, read_owl


def audit(root):
    raw = root / 'data/raw'
    mondo, mondo_meta = read_owl(raw / 'mondo/mondo.owl')
    matches = [r for r in mondo.values() if 'type 2 diabetes mellitus' in r['labels'] and not r['deprecated']]
    if len(matches) != 1 or matches[0]['uri'] != ANCHOR:
        raise ValueError('T2DM anchor is missing, ambiguous, or changed')
    anchor = matches[0]
    hierarchy = ancestors(mondo, ANCHOR)
    # Only explicit Mondo SKOS exact matches authorize HPO disease linkage.
    omim_ids = sorted('OMIM:' + m['object'].rsplit('/', 1)[1] for m in anchor['mappings']
                      if m['predicate'] == SKOS + 'exactMatch' and m['object'].startswith('https://omim.org/entry/'))
    hpo = [dict(row=r, locator=f'line:{i}') for i, r in hpo_rows(raw / 'hpo/phenotype.hpoa')
           if r['database_id'] in omim_ids]
    disease_rows = [dict(row=r, locator=f'row:{i}') for i, r in parquet_rows(raw / 'open_targets/disease.parquet')
                    if r['id'] == ANCHOR.rsplit('/', 1)[1]]
    if len(disease_rows) != 1 or disease_rows[0]['row']['code'] != ANCHOR:
        raise ValueError('Open Targets does not uniquely preserve the Mondo anchor IRI')
    ot_pheno = [dict(row=r, locator=f'row:{i}') for i, r in parquet_rows(raw / 'open_targets/disease_phenotype.parquet')
                if r['disease'] == disease_rows[0]['row']['id']]
    hp, hp_meta = read_owl(raw / 'hpo/hp.owl')
    wanted = {OBO + r['row']['hpo_id'].replace(':', '_') for r in hpo}
    wanted |= {OBO + r['row']['phenotype'] for r in ot_pheno}
    missing_hp = sorted(wanted - hp.keys())
    hpo_terms = [hp[u] for u in sorted(wanted) if u in hp]
    schemas = {}
    for path in sorted((raw / 'open_targets').rglob('*.parquet')):
        f = pq.ParquetFile(path)
        schemas[str(path.relative_to(root))] = {'rows': f.metadata.num_rows,
                                              'fields': f.schema_arrow.names, 'schema': str(f.schema_arrow)}
    target_ids, drug_ids = set(), set()
    for path in sorted((raw / 'open_targets/target').glob('*.parquet')):
        target_ids.update(r['id'] for _, r in parquet_rows(path, ['id']))
    for path in sorted((raw / 'open_targets/drug_molecule').glob('*.parquet')):
        drug_ids.update(r['id'] for _, r in parquet_rows(path, ['id']))
    mechanism_counts = Counter()
    missing_targets, missing_drugs = set(), set()
    for path in sorted((raw / 'open_targets/drug_mechanism_of_action').glob('*.parquet')):
        for _, row in parquet_rows(path):
            mechanism_counts['records'] += 1
            mechanism_counts['target_references'] += len(row['targets'])
            mechanism_counts['drug_references'] += len(row['chemblIds'] or [])
            missing_targets.update(set(row['targets']) - target_ids)
            missing_drugs.update(set(row['chemblIds'] or []) - drug_ids)
    dup = sum(len(x['row']['evidence']) - len({json.dumps(e, sort_keys=True) for e in x['row']['evidence']}) for x in ot_pheno)
    out = dict(anchor=anchor, mondo_metadata=mondo_meta, hpo_metadata=hp_meta,
               hierarchy=hierarchy, hpo_disease_ids=omim_ids, hpo_annotations=hpo,
               ot_disease=disease_rows[0], ot_phenotypes=ot_pheno, hpo_terms=hpo_terms,
               unresolved_hpo_ids=missing_hp, schemas=schemas,
               duplicate_ot_evidence=dup, mechanism_audit=dict(mechanism_counts),
               missing_mechanism_targets=sorted(missing_targets), missing_mechanism_drugs=sorted(missing_drugs),
               target_catalog_size=len(target_ids), drug_catalog_size=len(drug_ids),
               disease_target_join='unsupported: no disease association/evidence table supplied',
               drug_indication_join='unsupported: no structured indication table or disease identifier in molecule/mechanism schemas')
    dump(root / 'data/interim/audit.json', out)
    dump(root / 'reports/tables/input_schemas.json', schemas)
    return out
