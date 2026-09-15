"""Execute OWL RL closure over the bounded ontology and facts, not provenance."""
from rdflib import Graph, RDF, RDFS, URIRef, Literal, BNode
from rdflib.namespace import PROV
from owlrl import DeductiveClosure, OWLRL_Semantics
from .graph import KG, stable_id
from .inputs import ANCHOR


def reason(builder):
    premises = builder.asserted() + builder.schema
    closure = Graph()
    for triple in premises:
        closure.add(triple)
    DeductiveClosure(OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(closure)
    inferred = builder.ds.graph(KG['graph/inferred'])
    event = URIRef(str(builder.activity) + '/owlrl')
    builder.prov.add((event, RDF.type, PROV.Activity))
    builder.prov.add((event, KG.reasoningProfile, Literal('OWL 2 RL, owlrl; bounded projection, no remote imports')))
    builder.prov.add((event, PROV.wasInformedBy, builder.activity))
    for gid in sorted(builder.source_graphs | {builder.schema.identifier}, key=str):
        builder.prov.add((event, PROV.used, gid))
    excluded_generalized = 0
    for triple in closure:
        if not isinstance(triple[0], (URIRef, BNode)) or not isinstance(triple[1], URIRef):
            excluded_generalized += 1
            continue
        if triple not in premises:
            inferred.add(triple)
            stmt = stable_id('inference', [str(event), *[t.n3() for t in triple]])
            for p, o in [(RDF.type, KG.InferredAssertion), (RDF.subject, triple[0]),
                         (RDF.predicate, triple[1]), (RDF.object, triple[2]),
                         (PROV.wasGeneratedBy, event), (KG.assertedIn, inferred.identifier)]:
                builder.prov.add((stmt, p, o))
    examples = []
    anchor = URIRef(ANCHOR)
    classification = (anchor, RDF.type, KG.PhenotypeAnnotatedConcept)
    if classification not in inferred:
        raise ValueError('Expected phenotype annotation classification was not inferred')
    examples.append({'triple': [str(x) for x in classification], 'rule': 'owl:intersectionOf + owl:someValuesFrom + owl:equivalentClass',
                     'explanation': 'The disease concept has a positive phenotype annotation to an HPOTerm. This is a terminology classification, not a patient diagnosis.'})
    for phenotype in sorted(premises.objects(anchor, KG.hasPhenotype), key=str):
        triple = (phenotype, KG.phenotypeOf, anchor)
        if triple not in inferred:
            raise ValueError('OWL inverse property inference missing')
        examples.append({'triple': [str(x) for x in triple], 'rule': 'owl:inverseOf',
                         'premises': [[str(anchor), str(KG.hasPhenotype), str(phenotype)],
                                      [str(KG.hasPhenotype), 'http://www.w3.org/2002/07/owl#inverseOf', str(KG.phenotypeOf)]]})
    ancestors = sorted({o for s, p, o in inferred.triples((anchor, RDFS.subClassOf, None))
                        if o != anchor and str(o).startswith('http://purl.obolibrary.org/obo/')}, key=str)
    examples.append({'rule': 'rdfs:subClassOf transitivity', 'subject': ANCHOR,
                     'new_ancestors': [str(o) for o in ancestors]})
    return inferred, examples, {'generalized_non_rdf_triples_excluded': excluded_generalized}
