"""OWL review export; preserve anonymous class expressions for OWL parsers."""
from rdflib import Graph, RDF, RDFS, OWL, SKOS, URIRef
from rdflib.compare import to_canonical_graph
from .graph import KG

# Explicit export boundary, not a repair of the full provenance ontology.
PROVENANCE_CLASSES = frozenset((KG.SourceRecord, KG.SourceSnapshot,
    KG.ImportedAssertion, KG.MappingAssertion, KG.MappingCandidate, KG.InferredAssertion))


def reasoning_graph(root, asserted):
    """Produce a separately scoped review projection and its exact exclusions."""
    from rdflib.namespace import PROV
    full = review_graph(root, asserted)
    excluded_subjects = PROVENANCE_CLASSES | {RDF.Statement, PROV.Entity}
    excluded = {triple for triple in full if triple[0] in excluded_subjects}
    # Fail closed if future source data uses the omitted vocabulary.
    if any(term in excluded_subjects for triple in asserted for term in triple):
        raise ValueError('Source assertions reference excluded provenance vocabulary')
    graph = Graph()
    for triple in full:
        if triple not in excluded:
            graph.add(triple)
    if any(term in excluded_subjects for triple in graph for term in triple):
        raise ValueError('Reasoning projection retains references to excluded vocabulary')
    manifest = {
        'status': 'technical_projection_pending_author_design_review',
        'source': 'review.ttl', 'output': 'reasoning.ttl',
        'asserted_triples_preserved': len(asserted),
        'excluded_triple_count': len(excluded),
        'excluded_triples': sorted(' '.join(term.n3() for term in triple) + ' .' for triple in excluded),
        'reason': 'RDF provenance schema remains in the full review and canonical dataset; this projection is for terminology OWL reasoning only.',
    }
    return to_canonical_graph(graph), manifest


def review_graph(root, asserted):
    # The dataset's skolem IRIs suit RDF processing, but OWL parsers read them
    # as named classes rather than anonymous existential restrictions.
    graph = asserted + Graph().parse(root / 'ontology/core/core.ttl')
    for cls in list(graph.objects(None, RDFS.subClassOf)):
        if isinstance(cls, URIRef):
            graph.add((cls, RDF.type, OWL.Class))
    for prop in (KG.identifier, KG.sourceXref, SKOS.altLabel):
        graph.add((prop, RDF.type, OWL.AnnotationProperty))
    graph.add((SKOS.exactMatch, RDF.type, OWL.ObjectProperty))
    for subject, cls in asserted.subject_objects(RDF.type):
        if cls != OWL.Class:
            graph.add((subject, RDF.type, OWL.NamedIndividual))
    for target in asserted.objects(None, SKOS.exactMatch):
        graph.add((target, RDF.type, OWL.NamedIndividual))
    return to_canonical_graph(graph)
