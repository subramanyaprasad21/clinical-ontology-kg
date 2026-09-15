"""OWL review export; preserve anonymous class expressions for OWL parsers."""
from rdflib import Graph, RDF, RDFS, OWL, SKOS, URIRef
from rdflib.compare import to_canonical_graph
from .graph import KG


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
