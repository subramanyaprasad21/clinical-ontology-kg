"""Synthetic tests for clinical-context boundaries; no source downloads needed."""
import copy
import pytest
from rdflib import RDF
from rdflib.namespace import PROV
from build import construct, selected, EX, ANCHOR


def fixture():
    def row(table, payload):
        return {'path': table, 'sha256': table, 'row': 0, 'payload': payload}
    rows = {'disease': [row('disease', {'name': 'T2DM'})],
        'indications': [row('indication', {'drugId': 'CHEMBL1', 'maxClinicalStage': 'PHASE_2', 'clinicalReportIds': ['report1']})],
        'mechanisms': [row('mechanism', {'chemblIds': ['CHEMBL1'], 'targets': ['ENSG1'], 'actionType': 'INHIBITOR'})],
        'clinical_targets': [row('target', {'drugId': 'CHEMBL1', 'targetId': 'ENSG1', 'maxClinicalStage': 'APPROVAL'})]}
    manifest = {'release': '26.09', 'files': [{'path': r['path'], 'sha256': r['sha256'], 'retrieved_at': 'test', 'url': 'https://example.org/source'} for records in rows.values() for r in records]}
    return rows, manifest


def test_stage_is_disease_specific_and_all_three_evidence_types_retained():
    rows,m = fixture(); ds=construct(rows,m)
    source=ds.graph(EX['graph/records']); joined=ds.graph(EX['graph/clinical-context'])
    link=next(joined.subjects(RDF.type,EX.ClinicalContextLink))
    supports=set(joined.objects(link,PROV.wasDerivedFrom))
    assert {source.value(r,RDF.type) for r in supports} == {EX.IndicationRecord,EX.MechanismRecord,EX.ClinicalTargetRecord}
    assert {str(v) for v in source.objects(None,EX.indicationStage)} == {'PHASE_2'}
    assert {str(v) for v in source.objects(None,EX.aggregateStage)} == {'APPROVAL'}
    assert not list(joined.objects(link,EX.indicationStage))
    provenance=ds.graph(EX['graph/provenance'])
    assert all(provenance.value(r,PROV.wasDerivedFrom) and provenance.value(r,EX.payload) for r in supports)


@pytest.mark.parametrize('missing', ['indications','mechanisms'])
def test_unsupported_join_is_rejected(missing):
    rows,m=fixture(); rows[missing]=[]
    with pytest.raises(ValueError,match='lacks indication or mechanism'): construct(rows,m)


def test_unknown_stage_is_not_replaced_by_aggregate_approval():
    rows,m=fixture();rows['indications'][0]['payload']['maxClinicalStage']=None
    ds=construct(rows,m)
    assert not list(ds.graph(EX['graph/records']).objects(None,EX.indicationStage))


def test_selection_excludes_other_disease_and_accepts_null_context_entries():
    row=lambda p: {'payload':p}
    tables={'disease':[row({'id':'MONDO_0005148'})],
      'clinical_indication':[row({'diseaseId':'MONDO_0005148','drugId':'CHEMBL1'}),row({'diseaseId':'OTHER','drugId':'CHEMBL2'})],
      'clinical_target':[row({'diseases':[None,{'diseaseId':'MONDO_0005148'}]}),row({'diseases':[{'diseaseId':'OTHER'}]})],
      'drug_mechanism_of_action':[row({'chemblIds':['CHEMBL1']}),row({'chemblIds':['CHEMBL2']})]}
    result=selected(tables)
    assert all(len(records)==1 for records in result.values())


def test_determinism_and_input_preservation():
    rows,m=fixture();before=copy.deepcopy(rows)
    first=construct(rows,m);second=construct(rows,m)
    assert set(first.quads())==set(second.quads())
    assert rows==before


def test_invalid_target_identifier_is_rejected():
    rows,m=fixture();rows['mechanisms'][0]['payload']['targets']=['not a target']
    with pytest.raises(ValueError,match='Invalid target'): construct(rows,m)
