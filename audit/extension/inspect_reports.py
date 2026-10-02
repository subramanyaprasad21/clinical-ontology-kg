"""Resolve captured clinical-report references without asserting efficacy."""
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'data/extensions/opentargets-26.09'
ANCHOR = 'MONDO_0005148'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_value(value):
    if isinstance(value, date): return value.isoformat()
    raise TypeError(f'Unsupported source value: {type(value)}')


def classify(report, drug):
    """Co-present IDs are a source-context check, not pairwise efficacy evidence."""
    drugs = {d.get('drugId') for d in report.get('drugs') or [] if d}
    diseases = {d.get('diseaseId') for d in report.get('diseases') or [] if d}
    if drug in drugs and ANCHOR in diseases: return 'exact_drug_and_disease_present'
    if drug not in drugs and ANCHOR not in diseases: return 'neither_identifier_present'
    return 'disease_not_present' if ANCHOR not in diseases else 'drug_not_present'


def verify_receipt(name):
    receipt = ROOT / 'reports/extension' / name
    manifest = json.loads(receipt.read_text())
    if manifest['release'] != '26.09': raise ValueError('Wrong release')
    for record in manifest['files']:
        path = ROOT / record['path']
        if not path.resolve().is_relative_to(BASE.resolve()): raise ValueError('Capture path outside extension')
        if path.stat().st_size != record['bytes'] or sha(path) != record['sha256']: raise ValueError('Capture identity mismatch')
    return manifest


def main():
    original = verify_receipt('capture_manifest.json')
    receipt = verify_receipt('clinical_report_manifest.json')
    source_files = {Path(r['path']).parent.name: ROOT/r['path'] for r in original['files'] if r['path'].endswith('.parquet')}
    # The current receipt contains one partition for each clinical context table.
    if len(source_files) != sum(r['path'].endswith('.parquet') for r in original['files']):
        raise ValueError('Update reference loader for multiple context partitions')
    references = []
    for table in ('clinical_indication','clinical_target'):
        for index,r in enumerate(pq.read_table(source_files[table]).to_pylist()):
            include = r['diseaseId']==ANCHOR if table=='clinical_indication' else any(d and d.get('diseaseId')==ANCHOR for d in r.get('diseases') or [])
            if include:
                for report_id in sorted(set(r.get('clinicalReportIds') or [])):
                    references.append({'table':table,'row':index,'source_id':r['id'],'drug':r['drugId'],'report_id':report_id})
    wanted={r['report_id'] for r in references}
    resolved=defaultdict(list); all_ids=Counter(); total=0; schemas={}
    directory=BASE/'clinical-report-capture'
    listed=set(re.findall(r'href="([\w.-]+\.parquet)"',(directory/'index.html').read_text()))
    registered={Path(r['path']).name for r in receipt['files'] if r['path'].endswith('.parquet')}
    if not listed or listed!=registered or listed!={p.name for p in directory.glob('*.parquet')}:
        raise ValueError('Clinical report partition coverage mismatch')
    for entry in receipt['files']:
        if not entry['path'].endswith('.parquet'): continue
        path=ROOT/entry['path']; parquet=pq.ParquetFile(path); schemas[path.name]=str(parquet.schema_arrow); index=0
        for batch in parquet.iter_batches(batch_size=1024):
            for report in batch.to_pylist():
                all_ids[report['id']]+=1
                if report['id'] in wanted:
                    resolved[report['id']].append({'path':entry['path'],'sha256':entry['sha256'],'row':index,'payload':report})
                index+=1; total+=1
    counts=defaultdict(Counter); flags=defaultdict(Counter); missing=set(); ambiguous=set()
    indication_ids=set(); flag_refs=Counter(); non_indication_types=defaultdict(Counter)
    for reference in references:
        matches=resolved.get(reference['report_id'],[])
        if not matches:
            status='unresolved';missing.add(reference['report_id'])
        elif len(matches)!=1:
            status='ambiguous_report_id';ambiguous.add(reference['report_id'])
        else:
            report=matches[0]['payload'];status=classify(report,reference['drug'])
            quality=report.get('qualityControls') or []
            if quality: flag_refs[reference['table']]+=1
            flags[reference['table']].update(quality)
            if report.get('type')!='INDICATION': non_indication_types[reference['table']][str(report.get('type'))]+=1
            if reference['table']=='clinical_indication': indication_ids.add(reference['report_id'])
        reference['context_check']=status
        counts[reference['table']][status]+=1
    indication_reports=[resolved[i][0]['payload'] for i in sorted(indication_ids)]
    summary={'release':'26.09','source_report_rows':total,'unique_source_ids':len(all_ids),
        'duplicate_source_ids':sum(n>1 for n in all_ids.values()),'referenced_unique_ids':len(wanted),
        'resolved_unique_ids':len(resolved),'unresolved_ids':sorted(missing),'ambiguous_ids':sorted(ambiguous),
        'reference_context_counts':{t:dict(sorted(c.items())) for t,c in counts.items()},
        'references_with_quality_flags':dict(flag_refs),
        'quality_flags_per_reference':{t:dict(c) for t,c in flags.items()},
        'non_indication_type_reference_counts':{t:dict(c) for t,c in non_indication_types.items()},
        'unique_indication_reports':len(indication_reports),
        'indication_report_providers':dict(sorted(Counter(str(r.get('provider')) for r in indication_reports).items())),
        'indication_report_sources':dict(sorted(Counter(str(r.get('source')) for r in indication_reports).items())),
        'indication_report_stages':dict(sorted(Counter(str(r.get('clinicalStage')) for r in indication_reports).items())),
        'indication_reports_missing_url':sum(not r.get('url') for r in indication_reports),
        'report_manifest_sha256':sha(ROOT/'reports/extension/clinical_report_manifest.json'),
        'audit_sha256':sha(Path(__file__)),
        'interpretation':'Identifier co-presence within a report is not an independently verified pairwise indication, clinical efficacy or regulatory determination.'}
    output=directory/'inspection';output.mkdir(exist_ok=True)
    for name,value in [('referenced_reports.json',dict(sorted(resolved.items()))),('reference_checks.json',references),('schemas.json',schemas)]:
        (output/name).write_text(json.dumps(value,indent=2,sort_keys=True,default=json_value)+'\n')
    summary['artifacts']={p.name:sha(p) for p in sorted(output.glob('*.json'))}
    verify_receipt('capture_manifest.json');verify_receipt('clinical_report_manifest.json')
    (ROOT/'reports/extension/clinical_report_audit.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=='__main__': main()
