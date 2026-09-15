"""Regression checks for OWL export and evidence review coverage."""
from pathlib import Path
import pytest
from rdflib import Graph, RDF, OWL, Literal, BNode
from rdflib.namespace import PROV
from rdflib.compare import isomorphic
from clinical_kg.graph import KG, serialize_sorted
from clinical_kg.review import review_graph
from clinical_kg.validation import run_shacl, phenotype_conflicts

ROOT = Path(__file__).resolve().parents[1]


def test_review_preserves_restrictions_and_all_source_facts(tmp_path):
    asserted = Graph().parse(ROOT / 'data/processed/asserted.ttl')
    review = review_graph(ROOT, asserted)
    assert set(asserted) <= set(review)
    restrictions = list(review.subjects(RDF.type, OWL.Restriction))
    assert restrictions and all(isinstance(node, BNode) for node in restrictions)
    assert any((node, OWL.someValuesFrom, KG.HPOTerm) in review for node in restrictions)
    a, b = tmp_path / 'a.ttl', tmp_path / 'b.ttl'
    serialize_sorted(review, a)
    serialize_sorted(review_graph(ROOT, asserted), b)
    assert a.read_bytes() == b.read_bytes()
    assert isomorphic(review, Graph().parse(a))


@pytest.mark.parametrize('target,typed,expected', [
    (Literal('invalid'), False, False), (KG.testTerm, False, False),
    (KG.testTerm, True, True),
])
def test_generic_annotation_target(target, typed, expected):
    graph = Graph()
    graph.add((KG.testDisease, RDF.type, KG.DiseaseConcept))
    graph.add((KG.testDisease, KG.hasHPOAnnotation, target))
    if typed:
        graph.add((target, RDF.type, KG.HPOTerm))
    # Isolate the endpoint shape from unrelated label/identifier requirements.
    shapes = Graph().parse(ROOT / 'ontology/shapes/shapes.ttl')
    from rdflib.namespace import SH
    shapes.remove((KG.EntityShape, SH.targetClass, None))
    assert run_shacl(graph, shapes)[0] == expected


@pytest.mark.parametrize('same_source', [True, False])
def test_conflict_review_preserves_both_records_and_graphs(same_source):
    graph, provenance = Graph(), Graph()
    for index, predicate in enumerate((KG.hasPhenotype, KG.hasExcludedPhenotype)):
        graph.add((KG.disease, predicate, KG['term']))
        statement = KG[f'statement/{index}']
        for prop, value in [(RDF.subject, KG.disease), (RDF.predicate, predicate),
                            (RDF.object, KG['term']), (PROV.wasDerivedFrom, KG[f'record/{index}']),
                            (KG.assertedIn, KG[f'graph/{0 if same_source else index}'])]:
            provenance.add((statement, prop, value))
    before = set(graph), set(provenance)
    result = phenotype_conflicts(graph, provenance)
    assert len(result) == 1
    evidence = result[0]['evidence']
    assert evidence[str(KG.hasPhenotype)][0]['records'] == [str(KG['record/0'])]
    assert evidence[str(KG.hasExcludedPhenotype)][0]['graphs'] == [str(KG[f'graph/{0 if same_source else 1}'])]
    assert before == (set(graph), set(provenance))
    graph.remove((KG.disease, KG.hasExcludedPhenotype, KG['term']))
    graph.add((KG.disease, KG.hasExcludedPhenotype, KG.otherTerm))
    assert phenotype_conflicts(graph, provenance) == []
