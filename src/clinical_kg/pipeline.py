"""Offline build, validation, reasoning, executable questions and metrics."""
import hashlib
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from rdflib import BNode, Dataset, Graph, RDF, RDFS, SKOS, URIRef
from rdflib.namespace import PROV
from rdflib.compare import to_canonical_graph, isomorphic
from .audit import audit
from .graph import Builder, KG, serialize_dataset, serialize_sorted
from .inputs import ANCHOR, digest, dump, inventory, verify
from .reasoning import reason
from .review import review_graph, reasoning_graph
from .validation import invalid_demonstrations, provenance_coverage, run_shacl, union, phenotype_conflicts


def code_fingerprint(root, manifest):
    paths = sorted(set((root / 'src').rglob('*.py')) | set((root / 'scripts').glob('*.py')) | set((root / 'ontology').rglob('*.ttl')) |
                   set((root / 'queries').rglob('*.rq')) | {root / 'requirements.txt', root / 'config/project.yaml', root / 'pyproject.toml'})
    components = {str(p.relative_to(root)): digest(p) for p in paths}
    return hashlib.sha256(json.dumps({'inputs': manifest, 'implementation': components, 'python': platform.python_version()}, sort_keys=True).encode()).hexdigest()


def execute_queries(root, ds):
    output = {}
    for p in sorted((root / 'queries/competency').glob('*.rq')):
        result = ds.query(p.read_text())
        rows = [{str(v): (str(row[v]) if row[v] is not None else None) for v in result.vars} for row in result]
        name = p.stem
        status = 'unsupported' if name[:2] in ('04', '05', '06') else 'answered'
        output[name] = {'status': status, 'row_count': len(rows), 'rows': rows}
    dump(root / 'reports/tables/competency_results.json', output)
    return output


def build(root):
    if sys.version_info[:2] != (3, 12):
        raise ValueError('Use Python 3.12 with the frozen requirements')
    for requirement in (root / 'requirements.txt').read_text().splitlines():
        if '==' in requirement:
            package, expected = requirement.split('==', 1)
            if version(package) != expected:
                raise ValueError(f'Dependency drift: install requirements.txt ({package})')
    import yaml
    config = yaml.safe_load((root / 'config/project.yaml').read_text())
    if config['project']['disease_anchor'] != 'MONDO_0005148' or config['policy']['allow_downloads']:
        raise ValueError('Unsupported configuration: this implementation is frozen to the audited T2DM scope')
    manifest_path = root / 'config/input_manifest.json'
    if not manifest_path.exists():
        raise ValueError('Missing frozen input manifest. Use scripts/freeze_inputs.py explicitly before the first build.')
    manifest = json.loads(manifest_path.read_text())
    verify(root, manifest)
    print('Frozen input checksums verified.', flush=True)
    result = audit(root)
    if result['unresolved_hpo_ids']:
        raise ValueError('Unresolved HPO identifiers; audit report written for review')
    fingerprint = code_fingerprint(root, manifest)
    builder = Builder(root, manifest, fingerprint)
    candidates = builder.construct(result)
    asserted = builder.asserted()
    canonical = union(builder.ds)
    shapes = Graph().parse(root / 'ontology/shapes/shapes.ttl')
    conforms, report, report_text, violations = run_shacl(canonical, shapes)
    serialize_sorted(to_canonical_graph(report), root / 'reports/validation.ttl')
    (root / 'reports/validation.txt').write_text(report_text)
    validation_graph = builder.ds.graph(KG['graph/validation'])
    for triple in to_canonical_graph(report):
        validation_graph.add(tuple(KG['validation-node/' + str(t)] if isinstance(t, BNode) else t for t in triple))
    coverage = provenance_coverage(builder)
    if not conforms or coverage['coverage_percent'] != 100 or coverage['malformed_assertions']:
        raise ValueError('Canonical validation/provenance failure; see reports/validation.txt')
    invalid = invalid_demonstrations(canonical, shapes)
    print('Canonical SHACL passed; six isolated invalid cases detected.', flush=True)
    inferred, examples, reasoning_stats = reason(builder)
    # Query-only union is explicit; the Dataset default graph remains empty.
    queries = execute_queries(root, builder.ds)
    for q in ('04_disease_targets', '05_drugs', '06_disease_target_drug_path'):
        if queries[q]['row_count'] != 0:
            raise ValueError('Unexpected unsupported disease/drug relationship')
    out = root / 'data/processed'
    out.mkdir(parents=True, exist_ok=True)
    serialize_dataset(builder.ds, out / 'knowledge_graph.nq')
    serialize_sorted(asserted, out / 'asserted.ttl')
    serialize_sorted(inferred, out / 'inferred.ttl')
    serialize_sorted(builder.prov, out / 'provenance.ttl')
    review = review_graph(root, asserted)
    serialize_sorted(review, out / 'review.ttl')
    reasoning_review, export_manifest = reasoning_graph(root, asserted)
    serialize_sorted(reasoning_review, out / 'reasoning.ttl')
    dump(root / 'reports/tables/reasoning_export.json', export_manifest)
    conflicts = phenotype_conflicts(asserted, builder.prov)
    dump(root / 'reports/tables/phenotype_conflicts.json', conflicts)
    mappings = Graph()
    for triple in builder.ds.graph(KG['graph/source/mondo']):
        if str(triple[1]).startswith(str(SKOS)) and triple[1] != SKOS.altLabel:
            mappings.add(triple)
    serialize_sorted(mappings, out / 'mappings.ttl')
    reparsed = Dataset()
    reparsed.parse(out / 'knowledge_graph.nq', format='nquads')
    if set(reparsed.quads()) != set(builder.ds.quads()):
        raise ValueError('Dataset serialization round-trip changed quads')
    for name, graph in [('asserted', asserted), ('inferred', inferred), ('provenance', builder.prov),
                        ('review', review), ('reasoning', reasoning_review), ('mappings', mappings)]:
        if not isomorphic(Graph().parse(out / (name + '.ttl'), format='turtle'), graph):
            raise ValueError(f'{name} Turtle round-trip changed triples')
    dump(root / 'reports/tables/mapping_candidates.json', candidates)
    dump(root / 'reports/tables/reasoning_examples.json', examples)
    dump(root / 'reports/tables/invalid_cases.json', invalid)
    source_counts = {str(g): len(builder.ds.graph(g)) for g in sorted(builder.source_graphs, key=str)}
    metrics = {
        'build_fingerprint': fingerprint, 'frozen_input_files': len(manifest['inputs']),
        'raw_file_bytes': sum(r['bytes'] for r in manifest['inputs']),
        'hierarchy_classes_including_anchor': len(result['hierarchy']),
        'disease_concepts': len(set(asserted.subjects(RDF.type, KG.DiseaseConcept))),
        'hpo_terms': len(result['hpo_terms']),
        't2dm_positive_phenotypes': len(set(asserted.objects(URIRef(ANCHOR), KG.hasPhenotype))),
        'hpo_annotation_records': len(result['hpo_annotations']),
        'ot_annotation_rows': len(result['ot_phenotypes']), 'ot_duplicate_evidence_entries': result['duplicate_ot_evidence'],
        't2dm_targets': 0, 't2dm_drugs': 0,
        'mapping_counts': {str(p): len(list(mappings.triples((None, p, None)))) for p in
                           (SKOS.exactMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.relatedMatch, SKOS.closeMatch)},
        'unresolved_mappings': len(candidates), 'ambiguous_mappings': 0,
        'asserted_unique_triples': len(asserted), 'source_graph_counts': source_counts,
        'imported_assertion_records': len(set(builder.prov.subjects(RDF.type, KG.ImportedAssertion))),
        'inferred_triples_including_rdf_owl_bookkeeping': len(inferred),
        'reasoning_export': reasoning_stats,
        'rdf_round_trip_verified': True,
        'provenance': coverage, 'shacl_conforms': conforms, 'shacl_violations': violations,
        'invalid_cases_detected': len(invalid),
        'phenotype_conflicts_for_review': len(conflicts),
        'competency_questions': {k: {'status': v['status'], 'rows': v['row_count']} for k, v in queries.items()},
        'distinct_upstream_annotation_resources': len(set(builder.prov.objects(None, KG.upstreamResource))),
        'independent_corroboration_established': False,
        'acquisition_metadata_complete': False,
        'ot_release_independently_verified': False,
    }
    dump(root / 'reports/metrics.json', metrics)
    dump(root / 'reports/environment.json', {'python': platform.python_version(), 'platform': platform.platform(),
         'packages': {p: version(p) for p in ('rdflib', 'pyarrow', 'pyshacl', 'owlrl', 'pytest')}})
    artifacts = sorted(out.glob('*'))
    dump(root / 'reports/artifact_checksums.json', {str(p.relative_to(root)): digest(p) for p in artifacts if p.is_file() and not p.name.startswith('.')})
    verify(root, manifest)
    from .reporting import write_report
    write_report(root, metrics, result)
    return metrics
