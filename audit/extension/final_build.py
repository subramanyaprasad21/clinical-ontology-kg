"""Final separate extension: existing clinical joins plus captured report provenance."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from rdflib import Dataset, Graph, Literal, RDF, URIRef
from rdflib.namespace import PROV, SH, XSD
from pyshacl import validate
from build import ROOT, EX, construct, load, selected, ident, canonical, digest
import inspect_reports

OUT = ROOT / 'data/extensions/opentargets-26.09/final'
REPORT = ROOT / 'reports/final'


def attach_report(ds, row, snapshot, activity):
    """Keep report scope and absence states on the report itself."""
    g=ds.graph(EX['graph/reports']); p=ds.graph(EX['graph/provenance'])
    value=row['payload']; resource=ident('report', [row['sha256'],row['row']])
    g.add((resource,RDF.type,EX.ClinicalReport))
    g.add((resource,EX.reportIdentifier,Literal(value['id'])))
    fields={'provider':EX.reportProvider,'source':EX.reportSource,'origin':EX.reportOrigin,
            'type':EX.reportType,'clinicalStage':EX.reportStage,'phaseFromSource':EX.phaseFromSource,'url':EX.reportURL}
    for key,predicate in fields.items():
        if value.get(key) is None or value.get(key)=='':
            g.add((resource,EX.unresolvedField,Literal(key)))
        else: g.add((resource,predicate,Literal(value[key])))
    flags=value.get('qualityControls')
    state='absent' if 'qualityControls' not in value else 'null' if flags is None else 'empty' if not flags else 'present'
    g.add((resource,EX.qualityFieldState,Literal(state)))
    for flag in flags or []: g.add((resource,EX.qualityFlag,Literal(flag)))
    for key,field,predicate in [('drugs','drugId',EX.reportDrugIdentifier),('diseases','diseaseId',EX.reportDiseaseIdentifier)]:
        for item in value.get(key) or []:
            if item and item.get(field): g.add((resource,predicate,Literal(item[field])))
    p.add((resource,RDF.type,PROV.Entity));p.add((resource,PROV.wasDerivedFrom,snapshot))
    p.add((resource,PROV.wasGeneratedBy,activity));p.add((resource,EX.rowIndex,Literal(row['row'],datatype=XSD.integer)))
    p.add((resource,EX.payload,Literal(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,default=inspect_reports.json_value),datatype=RDF.JSON)))
    return resource


def execute(ds, path):
    result=ds.query(path.read_text())
    return [{str(v):str(row[v]) if row[v] is not None else None for v in result.vars} for row in result]


def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(exist_ok=True)
    tables, manifest=load(ROOT); rows=selected(tables)
    inputs=[Path(__file__),Path(__file__).with_name('build.py'),Path(__file__).with_name('inspect_reports.py'),
            Path(__file__).with_name('final_shapes.ttl'),*sorted(Path(__file__).with_name('final_queries').glob('*.rq'))]
    implementation=hashlib.sha256(canonical({str(p.relative_to(ROOT)):digest(p) for p in inputs}).encode()).hexdigest()
    ds=construct(rows,manifest,implementation);del tables
    report_manifest=inspect_reports.verify_receipt('clinical_report_manifest.json')
    # Regenerate the report selection from hashed Parquet rather than trust cached JSON.
    inspect_reports.main()
    report_rows=json.loads((inspect_reports.BASE/'clinical-report-capture/inspection/referenced_reports.json').read_text())
    p=ds.graph(EX['graph/provenance']);g=ds.graph(EX['graph/records']); rgraph=ds.graph(EX['graph/reports'])
    activity=ident('report-build',[report_manifest,implementation]);p.add((activity,RDF.type,PROV.Activity))
    p.add((activity,EX.implementationHash,Literal(implementation)))
    snapshots={}
    for entry in report_manifest['files']:
        snap=ident('snapshot',entry['sha256']);snapshots[entry['path']]=snap
        p.add((snap,RDF.type,PROV.Entity));p.add((snap,PROV.atLocation,URIRef(entry['url'])))
        for pred,val in [(EX.sha256,entry['sha256']),(EX.path,entry['path']),(EX.release,'26.09'),(EX.retrievedAt,entry['retrieved_at'])]:
            p.add((snap,pred,Literal(val)))
        p.add((activity,PROV.used,snap))
    for snap in list(p.subjects(EX.release,None)): p.add((snap,EX.sourceProvider,Literal('Open Targets Platform')))
    report_ids={}
    for rid,matches in sorted(report_rows.items()):
        if len(matches)==1: report_ids[rid]=attach_report(ds,matches[0],snapshots[matches[0]['path']],activity)
    del report_rows
    ref_counts=Counter();missing=[]
    for subject,literal in list(g.subject_objects(EX.reportIdentifier)):
        cls=g.value(subject,RDF.type);name=str(cls).rsplit('/',1)[-1]
        if str(literal) in report_ids:
            g.add((subject,EX.resolvedReport,report_ids[str(literal)]));ref_counts[name+'.resolved']+=1
        else:
            g.add((subject,EX.unresolvedReportIdentifier,literal));ref_counts[name+'.unresolved']+=1
            missing.append({'record':str(subject),'report_id':str(literal)})
    # Validate only structural requirements; QC values do not become truth filters.
    union=Graph()
    for context in ds.graphs():
        for triple in context: union.add(triple)
    print('Final graph assembled; validating SHACL.',flush=True)
    shapes=Graph().parse(Path(__file__).with_name('final_shapes.ttl'))
    conforms,report,text=validate(union,shacl_graph=shapes,inference='none',advanced=False)
    (OUT/'validation.txt').write_text(text)
    if not conforms: raise ValueError('Final extension SHACL failure')
    del union
    results={}
    for path in sorted(Path(__file__).with_name('final_queries').glob('*.rq')): results[path.stem]=execute(ds,path)
    for code in ('04','05','06'):
        path=next((ROOT/'queries/competency').glob(code+'*.rq'))
        results['original_'+path.stem]=execute(ds,path)
    (OUT/'query_results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    target=OUT/'extension.nq'
    target.write_text(''.join(sorted(ds.serialize(format='nquads').splitlines(keepends=True))))
    triples=set();subjects=set();iris=set();quads=0
    for s,pred,o,ctx in ds.quads():
        triples.add((s,pred,o));subjects.add(s);quads+=1
        iris.update(x for x in (s,pred,o) if isinstance(x,URIRef))
    counts={'quads':quads,'unique_triples':len(triples),'subject_resources':len(subjects),'distinct_iris_in_triples':len(iris)}
    del triples,subjects,iris
    summary={'release':'26.09','selected_records':{k:len(v) for k,v in rows.items()},
             'unique_indication_drugs':len({r['payload']['drugId'] for r in rows['indications']}),
             'unique_clinical_path_drugs':len({r['payload']['drugId'] for r in rows['clinical_targets']}),
             'unique_clinical_path_targets':len({r['payload']['targetId'] for r in rows['clinical_targets']}),
             'imported_reports':len(report_ids),'reference_counts':dict(sorted(ref_counts.items())),
             'unresolved_references':missing,'graph_counts':counts,
             'named_graph_counts':{str(c.identifier):len(c) for c in ds.graphs() if len(c)},
             'query_rows':{k:len(v) for k,v in results.items()},'shacl_conforms':bool(conforms),
             'missing_report_metadata':dict(sorted(Counter(str(v) for v in rgraph.objects(None,EX.unresolvedField)).items())),
             'report_quality_field_states':dict(sorted(Counter(str(v) for v in rgraph.objects(None,EX.qualityFieldState)).items())),
             'implementation_sha256':implementation,'artifacts':{f.name:digest(f) for f in sorted(OUT.glob('*')) if f.is_file()}}
    (REPORT/'extension_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__': main()
