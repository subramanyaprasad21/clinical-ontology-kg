"""Regression tests for semantic failure modes, not just graph size."""
import json
from pathlib import Path
import pytest
from rdflib import Dataset, Graph, RDF, RDFS, OWL, SKOS, URIRef, Literal
from rdflib.namespace import PROV
from owlrl import DeductiveClosure, OWLRL_Semantics
from clinical_kg.graph import Builder, KG, annotation_predicate
from clinical_kg.inputs import ANCHOR, OBO, digest, read_owl, verify, ancestors
from clinical_kg.mapping import mapping_uri
from clinical_kg.validation import provenance_coverage, run_shacl

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def artifacts():
    assert (ROOT / 'data/processed/knowledge_graph.nq').exists(), 'Run scripts/build.py before integration tests'
    ds = Dataset()
    ds.parse(ROOT / 'data/processed/knowledge_graph.nq', format='nquads')
    return ds


@pytest.mark.parametrize('aspect,negative,expected', [
    ('P', False, KG.hasPhenotype), ('I', False, KG.hasInheritanceAnnotation),
    ('C', False, KG.hasClinicalModifier), ('P', True, KG.hasExcludedPhenotype),
    ('I', True, None), ('unknown', False, None),
])
def test_annotation_aspects_and_negation(aspect, negative, expected):
    assert annotation_predicate(aspect, negative) == expected


def test_no_mapping_from_unrecognized_xref():
    assert mapping_uri('NANDO:2200461') is None
    assert mapping_uri('OMIM:125853') == 'https://omim.org/entry/125853'


def test_raw_corruption_is_detected(tmp_path):
    path = tmp_path / 'data/raw/hpo/hp.owl'
    path.parent.mkdir(parents=True)
    path.write_text('original')
    manifest = {'inputs': [{'path': 'data/raw/hpo/hp.owl', 'bytes': path.stat().st_size, 'sha256': digest(path)}]}
    verify(tmp_path, manifest)
    path.write_text('modified')  # Same length tests actual hash verification.
    with pytest.raises(ValueError, match='checksum'):
        verify(tmp_path, manifest)


def test_new_raw_input_is_detected(tmp_path):
    p = tmp_path / 'data/raw/hpo/hp.owl'
    p.parent.mkdir(parents=True)
    p.write_text('unexpected')
    with pytest.raises(ValueError, match='inventory'):
        verify(tmp_path, {'inputs': []})


def test_xml_nested_restriction_is_not_flattened(tmp_path):
    p = tmp_path / 'sample.owl'
    p.write_text('''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl="http://www.w3.org/2002/07/owl#">
      <owl:Class rdf:about="urn:A"><rdfs:label>A</rdfs:label><rdfs:subClassOf rdf:resource="urn:B"/>
      <rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="urn:p"/>
      <owl:someValuesFrom rdf:resource="urn:C"/></owl:Restriction></rdfs:subClassOf></owl:Class>
      </rdf:RDF>''')
    classes, _ = read_owl(p)
    assert classes['urn:A']['parents'] == ['urn:B']
    assert len(classes['urn:A']['restrictions_xml']) == 1
    with pytest.raises(ValueError, match='missing'):
        ancestors(classes, 'urn:A')


def test_no_inheritance_or_onset_as_positive_phenotype(artifacts):
    graph = artifacts.graph(KG['graph/source/ot-phenotypes'])
    anchor = URIRef(ANCHOR)
    assert (anchor, KG.hasInheritanceAnnotation, URIRef(OBO + 'HP_0000006')) in graph
    assert (anchor, KG.hasClinicalModifier, URIRef(OBO + 'HP_0003584')) in graph
    assert set(graph.objects(anchor, KG.hasPhenotype)) == {URIRef(OBO + x) for x in ('HP_0000855', 'HP_0005978', 'HP_0031819')}


def test_similar_disease_phenotype_labels_are_not_collapsed(artifacts):
    for gid in ('mondo', 'hpo-ontology', 'ot-phenotypes'):
        g = artifacts.graph(KG['graph/source/' + gid])
        assert not list(g.triples((URIRef(ANCHOR), SKOS.exactMatch, URIRef(OBO + 'HP_0005978'))))
        assert not list(g.triples((None, OWL.sameAs, None)))


def test_no_invented_drug_or_target_edges(artifacts):
    for g in artifacts.graphs():
        for prop in (KG.treats, KG.indicatedFor, KG.associatedTarget, KG.targets):
            assert not list(g.triples((None, prop, None)))


def test_real_inference_is_not_asserted(artifacts):
    triple = (URIRef(ANCHOR), RDF.type, KG.PhenotypeAnnotatedConcept)
    assert triple in artifacts.graph(KG['graph/inferred'])
    for g in artifacts.graphs():
        if str(g.identifier).startswith(str(KG['graph/source/'])):
            assert triple not in g


def test_negative_annotation_cannot_trigger_positive_classification():
    g = Graph().parse(ROOT / 'ontology/core/core.ttl')
    disease, phenotype = URIRef('urn:synthetic:disease'), URIRef('urn:synthetic:phenotype')
    g.add((disease, RDF.type, KG.DiseaseConcept))
    g.add((phenotype, RDF.type, KG.HPOTerm))
    g.add((disease, KG.hasExcludedPhenotype, phenotype))
    DeductiveClosure(OWLRL_Semantics).expand(g)
    assert (disease, RDF.type, KG.PhenotypeAnnotatedConcept) not in g
    assert (phenotype, KG.phenotypeOf, disease) not in g


def test_reasoning_depends_on_positive_premise():
    schema = Graph().parse(ROOT / 'ontology/core/core.ttl')
    disease, phenotype = URIRef('urn:synthetic:disease'), URIRef('urn:synthetic:phenotype')
    schema.add((disease, RDF.type, KG.DiseaseConcept))
    schema.add((phenotype, RDF.type, KG.HPOTerm))
    without = Graph() + schema
    with_positive = Graph() + schema
    with_positive.add((disease, KG.hasPhenotype, phenotype))
    DeductiveClosure(OWLRL_Semantics).expand(without)
    DeductiveClosure(OWLRL_Semantics).expand(with_positive)
    assert (disease, RDF.type, KG.PhenotypeAnnotatedConcept) not in without
    assert (disease, RDF.type, KG.PhenotypeAnnotatedConcept) in with_positive


def test_missing_statement_provenance_is_detected():
    manifest = json.loads((ROOT / 'config/input_manifest.json').read_text())
    b = Builder(ROOT, manifest, 'test-only')
    gid = KG['graph/source/test']
    b.source_graphs.add(gid)
    b.ds.graph(gid).add((URIRef('urn:s'), RDFS.label, Literal('untracked')))
    coverage = provenance_coverage(b)
    assert coverage['coverage_percent'] == 0


def test_all_raw_files_still_match_freeze():
    verify(ROOT, json.loads((ROOT / 'config/input_manifest.json').read_text()))


def test_canonical_validation_and_isolated_failures():
    metrics = json.loads((ROOT / 'reports/metrics.json').read_text())
    assert metrics['shacl_conforms'] is True
    assert metrics['provenance']['coverage_percent'] == 100
    cases = json.loads((ROOT / 'reports/tables/invalid_cases.json').read_text())
    assert len(cases) == 6
    assert all(not x['conforms'] and x['constraint_counts'] for x in cases.values())


def test_shared_evidence_is_not_independent(artifacts):
    p = artifacts.graph(KG['graph/provenance'])
    assert set(p.objects(None, KG.upstreamResource)) == {Literal('HPO')}
    metrics = json.loads((ROOT / 'reports/metrics.json').read_text())
    assert metrics['ot_duplicate_evidence_entries'] == 5
    assert metrics['independent_corroboration_established'] is False


def test_bfo_ancestors_are_not_disease_concepts(artifacts):
    graph = artifacts.graph(KG['graph/source/mondo'])
    bfo = URIRef(OBO + 'BFO_0000001')
    assert (bfo, RDF.type, KG.OntologyConcept) in graph
    assert (bfo, RDF.type, KG.DiseaseConcept) not in graph


def test_frozen_queries_have_expected_supported_and_negative_results():
    q = json.loads((ROOT / 'reports/tables/competency_results.json').read_text())
    assert len(q) == 11
    assert q['01_hierarchy']['row_count'] == 16
    assert q['08_multi_source_annotations']['row_count'] == 5
    for name in ('04_disease_targets', '05_drugs', '06_disease_target_drug_path'):
        assert q[name]['status'] == 'unsupported' and q[name]['row_count'] == 0
    assert q['11_validation_violations']['row_count'] == 0


def test_artifact_checksums():
    hashes = json.loads((ROOT / 'reports/artifact_checksums.json').read_text())
    assert all(digest(ROOT / path) == expected for path, expected in hashes.items())
