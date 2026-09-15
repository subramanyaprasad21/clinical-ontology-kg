"""SHACL checks plus dataset-aware statement provenance verification."""
from collections import Counter
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import PROV, SH
from pyshacl import validate
from .graph import KG


def union(dataset):
    g = Graph()
    for context in dataset.graphs():
        if context.identifier != KG['graph/inferred']:
            for triple in context:
                g.add(triple)
    return g


def run_shacl(graph, shapes):
    conforms, report, text = validate(graph, shacl_graph=shapes, inference='none', advanced=False)
    counts = Counter(str(v).rsplit('#', 1)[-1] for v in report.objects(None, SH.sourceConstraintComponent))
    return bool(conforms), report, text, dict(sorted(counts.items()))


def phenotype_conflicts(asserted, provenance):
    """Flag exact-IRI positive/excluded pairs without adjudicating evidence.

    Source disagreement is reviewable evidence, not an OWL contradiction or a
    reason to delete either assertion. Mappings do not propagate these flags.
    """
    pairs = set(asserted.subject_objects(KG.hasPhenotype)) & set(asserted.subject_objects(KG.hasExcludedPhenotype))
    results = []
    for subject, target in sorted(pairs, key=lambda pair: tuple(map(str, pair))):
        evidence = {}
        for predicate in (KG.hasPhenotype, KG.hasExcludedPhenotype):
            records = []
            for statement in provenance.subjects(RDF.subject, subject):
                if ((statement, RDF.predicate, predicate) in provenance
                        and (statement, RDF.object, target) in provenance):
                    records.append({'assertion': str(statement),
                                    'records': sorted(map(str, provenance.objects(statement, PROV.wasDerivedFrom))),
                                    'graphs': sorted(map(str, provenance.objects(statement, KG.assertedIn)))})
            evidence[str(predicate)] = sorted(records, key=lambda record: record['assertion'])
        results.append({'subject': str(subject), 'phenotype': str(target),
                        'status': 'human_review_required', 'evidence': evidence})
    return results


def provenance_coverage(builder):
    p = builder.prov
    covered, total = 0, 0
    malformed = []
    index = set()
    for stmt in p.subjects(RDF.type, KG.ImportedAssertion):
        s, pred, o, gid = (p.value(stmt, prop) for prop in (RDF.subject, RDF.predicate, RDF.object, KG.assertedIn))
        rec = p.value(stmt, PROV.wasDerivedFrom)
        snapshot = p.value(rec, PROV.wasDerivedFrom) if rec else None
        good = (rec and snapshot and p.value(stmt, PROV.wasGeneratedBy) == builder.activity
                and all(p.value(rec, prop) is not None for prop in (KG.locator, KG.originalIdentifier, KG.payload))
                and all(p.value(snapshot, prop) is not None for prop in (KG.source, KG.version, KG.sha256, KG.path)))
        if not good or gid not in builder.source_graphs or (s, pred, o) not in builder.ds.graph(gid):
            malformed.append(str(stmt))
        else:
            index.add((s, pred, o, gid))
    for gid in builder.source_graphs:
        for s, pred, o in builder.ds.graph(gid):
            total += 1
            covered += (s, pred, o, gid) in index
    return {'source_quads': total, 'covered_source_quads': covered,
            'coverage_percent': round(100 * covered / total, 3) if total else 0,
            'malformed_assertions': malformed}


def invalid_demonstrations(canonical, shapes):
    """Each mutation gets an isolated graph; canonical output is never mutated."""
    cases = {}
    entity = next(canonical.subjects(RDF.type, KG.DiseaseConcept))
    stmt = next(canonical.subjects(RDF.type, KG.ImportedAssertion))
    source = next(canonical.subjects(RDF.type, KG.SourceSnapshot))
    mapping = next(canonical.subjects(RDF.type, KG.MappingAssertion))
    mutations = {
        'missing_label': lambda g: g.remove((entity, RDFS.label, None)),
        'missing_identifier': lambda g: g.remove((entity, KG.identifier, None)),
        'missing_assertion_provenance': lambda g: g.remove((stmt, PROV.wasDerivedFrom, None)),
        'missing_source_version': lambda g: g.remove((source, KG.version, None)),
        'malformed_phenotype_target': lambda g: g.add((entity, KG.hasPhenotype, Literal('not an IRI'))),
        'illegal_mapping_predicate': lambda g: (g.remove((mapping, RDF.predicate, None)), g.add((mapping, RDF.predicate, OWL.sameAs))),
    }
    for name, mutate in mutations.items():
        graph = Graph()
        for t in canonical:
            graph.add(t)
        mutate(graph)
        conforms, _, _, counts = run_shacl(graph, shapes)
        if conforms:
            raise ValueError(f'SHACL failed to detect deliberately invalid case: {name}')
        cases[name] = {'conforms': conforms, 'constraint_counts': counts}
    return cases
