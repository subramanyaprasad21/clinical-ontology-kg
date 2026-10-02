"""Report-context and stage-boundary checks using synthetic data."""
from pathlib import Path
import pytest
from rdflib import Dataset, Graph, Literal, RDF
from rdflib.namespace import PROV
from pyshacl import validate
from build import EX
from inspect_reports import classify
from final_build import attach_report


@pytest.mark.parametrize('drugs,diseases,expected',[
    ([{'drugId':'CHEMBL1'}],[{'diseaseId':'MONDO_0005148'}],'exact_drug_and_disease_present'),
    ([None,{'drugId':'CHEMBL1'}],[{'diseaseId':'OTHER'}],'disease_not_present'),
    ([{'drugId':'OTHER'}],[{'diseaseId':'MONDO_0005148'}],'drug_not_present'),
    (None,None,'neither_identifier_present')])
def test_report_context_is_not_implied_by_its_reference(drugs,diseases,expected):
    assert classify({'drugs':drugs,'diseases':diseases},'CHEMBL1')==expected


def test_missing_metadata_and_qc_are_explicit_and_stage_stays_on_report():
    ds=Dataset();row={'sha256':'a','row':1,'payload':{'id':'report1','clinicalStage':'APPROVAL','qualityControls':['UNVALIDATED_INDICATION']}}
    report=attach_report(ds,row,EX.snapshot,EX.activity)
    graph=ds.graph(EX['graph/reports'])
    assert str(graph.value(report,EX.reportStage))=='APPROVAL'
    assert not list(graph.objects(None,EX.indicationStage))
    assert (report,EX.unresolvedField,Literal('provider')) in graph
    assert (report,EX.qualityFlag,Literal('UNVALIDATED_INDICATION')) in graph
    assert (report,EX.qualityFieldState,Literal('present')) in graph


@pytest.mark.parametrize('mutation',['missing_report_id','stage_leak','dangling_report'])
def test_shacl_rejects_report_failures(mutation):
    graph=Graph();report=EX.report1
    graph.add((report,RDF.type,EX.ClinicalReport))
    graph.add((report,EX.reportIdentifier,Literal('R1')))
    graph.add((report,EX.qualityFieldState,Literal('null')))
    shapes=Graph().parse(Path(__file__).with_name('final_shapes.ttl'))
    assert validate(graph,shacl_graph=shapes,inference='none')[0]
    if mutation=='missing_report_id':graph.remove((report,EX.reportIdentifier,None))
    elif mutation=='stage_leak':graph.add((report,EX.indicationStage,Literal('APPROVAL')))
    else:graph.add((EX.record1,EX.resolvedReport,EX.missing))
    assert not validate(graph,shacl_graph=shapes,inference='none')[0]
