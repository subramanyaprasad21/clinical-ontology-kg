"""Compare extension RDF and query outputs with captured Parquet rows."""
import hashlib
import json
from pathlib import Path
import pyarrow.parquet as pq
from rdflib import Dataset, Namespace, RDF, URIRef
from rdflib.namespace import PROV

ROOT = Path(__file__).resolve().parents[2]
EX = Namespace('https://example.org/clinical-kg/extension/')
BASE = ROOT / 'data/extensions/opentargets-26.09'


def main():
    manifest = json.loads((ROOT / 'reports/extension/capture_manifest.json').read_text())
    files = {r['path']: r for r in manifest['files']}
    for name,r in files.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('Raw capture hash mismatch')
    raw = {name: pq.read_table(ROOT/name).to_pylist() for name in files if name.endswith('.parquet')}
    ds = Dataset(); ds.parse(BASE/'derived/clinical_context.nq',format='nquads')
    g=ds.graph(EX['graph/records']); p=ds.graph(EX['graph/provenance']); links=ds.graph(EX['graph/clinical-context'])
    records=set(g.subjects(RDF.type,None)); checked=0
    for record in records:
        snapshots=list(p.objects(record,PROV.wasDerivedFrom)); indices=list(p.objects(record,EX.rowIndex)); payloads=list(p.objects(record,EX.payload))
        if len(snapshots)!=1 or len(indices)!=1 or len(payloads)!=1: raise ValueError('Record lineage cardinality')
        path=str(p.value(snapshots[0],EX.path)); index=int(indices[0])
        if str(p.value(snapshots[0],EX.sha256)) != files[path]['sha256']: raise ValueError('Snapshot hash mismatch')
        if index < 0 or json.loads(str(payloads[0])) != raw[path][index]: raise ValueError('Source payload mismatch')
        checked+=1
    def rows(table):
        return [r for name,values in raw.items() if Path(name).parent.name==table for r in values]
    indications=[r for r in rows('clinical_indication') if r['diseaseId']=='MONDO_0005148']
    expected_drugs={r['drugId']:r['maxClinicalStage'] for r in indications}
    expected_pairs={(r['drugId'],r['targetId']) for r in rows('clinical_target') if any(d and d.get('diseaseId')=='MONDO_0005148' for d in r.get('diseases') or [])}
    mechanism_pairs={(drug,target) for r in rows('drug_mechanism_of_action') for drug in r.get('chemblIds') or [] for target in r.get('targets') or []}
    queries=json.loads((BASE/'derived/query_results.json').read_text())
    actual_drugs={r['drug'].rsplit('/',1)[1]:r['stage'] for r in queries['01_indications']}
    actual_pairs={(r['drug'].rsplit('/',1)[1],r['target'].rsplit('/',1)[1]) for r in queries['02_clinical_paths']}
    if actual_drugs!=expected_drugs or len(queries['01_indications'])!=len(indications): raise ValueError('Indication query differs from source')
    if actual_pairs!=expected_pairs or not actual_pairs<=mechanism_pairs: raise ValueError('Clinical query differs from source join')
    paths=list(links.subjects(RDF.type,EX.ClinicalContextLink))
    if len(paths)!=len(expected_pairs): raise ValueError('Clinical link count')
    for link in paths:
        evidence=list(links.objects(link,PROV.wasDerivedFrom))
        if not set(evidence)<=records: raise ValueError('Dangling evidence')
        types={g.value(r,RDF.type) for r in evidence}
        if types!={EX.IndicationRecord,EX.ClinicalTargetRecord,EX.MechanismRecord}: raise ValueError('Missing evidence type')
        drug=links.value(link,EX.drug); target=links.value(link,EX.target)
        for r in evidence:
            if (r,EX.drug,drug) not in g: raise ValueError('Evidence drug mismatch')
            if g.value(r,RDF.type)!=EX.IndicationRecord and (r,EX.target,target) not in g: raise ValueError('Evidence target mismatch')
        if list(links.objects(link,EX.indicationStage)) or list(links.objects(link,EX.aggregateStage)): raise ValueError('Stage leaked onto path')
    expected_evidence={(str(link),str(record)) for link,record in links.subject_objects(PROV.wasDerivedFrom)}
    actual_evidence={(r['link'],r['record']) for r in queries['03_path_evidence']}
    if expected_evidence!=actual_evidence: raise ValueError('Provenance query coverage')
    result={'source_payloads_verified':checked,'indication_rows_verified':len(indications),
            'clinical_paths_verified':len(paths),'path_evidence_links_verified':len(expected_evidence),
            'all_checks_passed':True,'scope':'Separate comparison implementation; shared RDFLib and PyArrow libraries.',
            'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'reports/extension/graph_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
