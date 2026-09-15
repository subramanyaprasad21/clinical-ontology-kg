"""Build source-separated facts and statement/record/file provenance."""
import hashlib
import json
from urllib.parse import quote
from rdflib import Dataset, Graph, Literal, Namespace, RDF, RDFS, OWL, SKOS, URIRef
from rdflib.namespace import PROV
from .inputs import ANCHOR, OBO

KG = Namespace('https://example.org/clinical-kg/')


def stable_id(kind, value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return KG[kind + '/' + hashlib.sha256(raw.encode()).hexdigest()]


def annotation_predicate(aspect, negative=False):
    if negative:
        return KG.hasExcludedPhenotype if aspect == 'P' else None
    return {'P': KG.hasPhenotype, 'I': KG.hasInheritanceAnnotation, 'C': KG.hasClinicalModifier}.get(aspect)


def serialize_sorted(graph, path):
    """N-Triples are also valid Turtle; sorted bytes avoid serializer ordering drift."""
    path.write_text(''.join(sorted(graph.serialize(format='nt').splitlines(keepends=True))))


def serialize_dataset(dataset, path):
    path.write_text(''.join(sorted(dataset.serialize(format='nquads').splitlines(keepends=True))))


class Builder:
    def __init__(self, root, manifest, build_id):
        self.root, self.manifest = root, manifest
        self.ds = Dataset()
        self.prov = self.ds.graph(KG['graph/provenance'])
        self.schema = self.ds.graph(KG['graph/schema'])
        # Stable skolem IRIs replace ontology list/restriction blank nodes.
        from rdflib.compare import to_canonical_graph
        from rdflib import BNode
        source_schema = to_canonical_graph(Graph().parse(root / 'ontology/core/core.ttl'))
        for triple in source_schema:
            self.schema.add(tuple(KG['schema-node/' + str(t)] if isinstance(t, BNode) else t for t in triple))
        self.activity = KG['build/' + build_id]
        self.prov.add((self.activity, RDF.type, PROV.Activity))
        self.prov.add((self.activity, KG.buildFingerprint, Literal(build_id)))
        self.sources, self.source_graphs = {}, set()
        for item in manifest['inputs']:
            uri = KG['snapshot/' + item['sha256']]
            self.sources[item['path']] = uri
            self.prov.add((uri, RDF.type, KG.SourceSnapshot))
            for key in ('source', 'version', 'sha256', 'path'):
                self.prov.add((uri, KG[key], Literal(item[key])))
            self.prov.add((uri, KG.versionBasis, Literal(item['version_basis'])))
            self.prov.add((uri, KG.acquisitionStatus, Literal(item['acquisition_status'])))
            self.prov.add((self.activity, PROV.used, uri))

    def record(self, path, locator, identifier, payload):
        uri = stable_id('record', [self.sources[path].n3(), locator])
        self.prov.add((uri, RDF.type, KG.SourceRecord))
        self.prov.add((uri, PROV.wasDerivedFrom, self.sources[path]))
        self.prov.add((uri, KG.locator, Literal(locator)))
        self.prov.add((uri, KG.originalIdentifier, Literal(identifier)))
        self.prov.add((uri, KG.payload, Literal(json.dumps(payload, sort_keys=True, ensure_ascii=False), datatype=RDF.JSON)))
        return uri

    def add(self, source, triple, record, mapping=False):
        gid = KG['graph/source/' + source]
        self.source_graphs.add(gid)
        self.ds.graph(gid).add(triple)
        stmt = stable_id('assertion', [str(gid), *[t.n3() for t in triple], str(record)])
        for p, o in [(RDF.type, KG.ImportedAssertion), (RDF.type, RDF.Statement),
                     (RDF.subject, triple[0]), (RDF.predicate, triple[1]), (RDF.object, triple[2]),
                     (PROV.wasDerivedFrom, record), (PROV.wasGeneratedBy, self.activity), (KG.assertedIn, gid)]:
            self.prov.add((stmt, p, o))
        if mapping:
            self.prov.add((stmt, RDF.type, KG.MappingAssertion))
            self.prov.add((stmt, KG.mappingMethod, Literal('explicit source SKOS assertion; no label matching')))
        return stmt

    def entity(self, source, uri, identifier, label, typ, record):
        for p, o in [(RDF.type, typ), (KG.identifier, Literal(identifier)), (RDFS.label, Literal(label))]:
            self.add(source, (uri, p, o), record)

    def construct(self, audit):
        anchor = URIRef(ANCHOR)
        anchor_record = None
        for item in audit['hierarchy']:
            uri = URIRef(item['uri'])
            rec = self.record('data/raw/mondo/mondo.owl', 'owl:Class:' + item['uri'], item['uri'], item)
            if uri == anchor:
                anchor_record = rec
            self.entity('mondo', uri, item['uri'].rsplit('/', 1)[1].replace('_', ':'), item['labels'][0], KG.DiseaseConcept if '/MONDO_' in item['uri'] else KG.OntologyConcept, rec)
            self.add('mondo', (uri, RDF.type, OWL.Class), rec)
            for parent in item['parents']:
                self.add('mondo', (uri, RDFS.subClassOf, URIRef(parent)), rec)
            if uri == anchor:
                for syn in item['synonyms']:
                    self.add('mondo', (uri, SKOS.altLabel, Literal(syn)), rec)
                for xref in item['xrefs']:
                    self.add('mondo', (uri, KG.sourceXref, Literal(xref)), rec)
                for mapping in item['mappings']:
                    self.add('mondo', (uri, URIRef(mapping['predicate']), URIRef(mapping['object'])), rec, mapping=True)
        # Conservative candidate audit: an xref without a demonstrated SKOS target is unresolved.
        # URI conversion alone does not authorize a mapping.
        from .mapping import mapping_uri
        mapped = {m['object'] for m in audit['anchor']['mappings']}
        candidates = []
        for xref in audit['anchor']['xrefs']:
            if mapping_uri(xref) not in mapped:
                candidate = stable_id('candidate', [ANCHOR, xref])
                for p, o in [(RDF.type, KG.MappingCandidate), (KG.status, Literal('unresolved')),
                             (KG.candidateIdentifier, Literal(xref)), (PROV.wasDerivedFrom, anchor_record)]:
                    self.prov.add((candidate, p, o))
                candidates.append({'identifier': xref, 'status': 'unresolved', 'reason': 'xref has no verified corresponding explicit SKOS mapping'})
        for item in audit['hpo_terms']:
            uri = URIRef(item['uri'])
            rec = self.record('data/raw/hpo/hp.owl', 'owl:Class:' + item['uri'], item['uri'], item)
            self.entity('hpo-ontology', uri, item['uri'].rsplit('/', 1)[1].replace('_', ':'), item['labels'][0], KG.HPOTerm, rec)
        hpo_seen = set()
        for entry in audit['hpo_annotations']:
            row = entry['row']
            uri = URIRef('https://omim.org/entry/' + row['database_id'].split(':')[1])
            rec = self.record('data/raw/hpo/phenotype.hpoa', entry['locator'], row['database_id'], row)
            if uri not in hpo_seen:
                self.entity('hpo-annotations', uri, row['database_id'], row['disease_name'], KG.DiseaseConcept, rec)
                hpo_seen.add(uri)
            pred = annotation_predicate(row['aspect'], row['qualifier'] == 'NOT')
            if pred:
                self.add('hpo-annotations', (uri, pred, URIRef(OBO + row['hpo_id'].replace(':', '_'))), rec)
            self.evidence(rec, row['aspect'], row['evidence'], row['reference'].split(';'), 'HPO', row['qualifier'])
        entry = audit['ot_disease']
        row = entry['row']
        rec = self.record('data/raw/open_targets/disease.parquet', entry['locator'], row['id'], row)
        self.entity('ot-disease', anchor, row['id'], row['name'], KG.DiseaseConcept, rec)
        for parent in row['parents']:
            self.add('ot-disease', (anchor, RDFS.subClassOf, URIRef(OBO + parent)), rec)
        for xref in row['dbXRefs']:
            self.add('ot-disease', (anchor, KG.sourceXref, Literal(xref)), rec)
        for entry in audit['ot_phenotypes']:
            row = entry['row']
            for i, ev in enumerate(row['evidence']):
                # Keep duplicate physical evidence entries traceable, never count as independent studies.
                rec = self.record('data/raw/open_targets/disease_phenotype.parquet', entry['locator'] + f'/evidence:{i}', row['disease'], {'disease': row['disease'], 'phenotype': row['phenotype'], 'evidence': ev})
                pred = annotation_predicate(ev['aspect'], bool(ev['qualifierNot']) or ev['qualifier'] == 'NOT')
                if pred:
                    self.add('ot-phenotypes', (anchor, pred, URIRef(OBO + row['phenotype'])), rec)
                self.evidence(rec, ev['aspect'], ev['evidenceType'], ev['references'] or [], ev['resource'], 'NOT' if ev['qualifierNot'] else (ev['qualifier'] or ''))
        return candidates

    def evidence(self, rec, aspect, code, refs, resource, qualifier):
        for p, value in [(KG.aspect, aspect), (KG.evidenceCode, code), (KG.upstreamResource, resource), (KG.qualifier, qualifier)]:
            self.prov.add((rec, p, Literal(value or '')))
        for ref in refs:
            if ref:
                self.prov.add((rec, KG.reference, Literal(ref)))

    def asserted(self):
        graph = Graph()
        for gid in self.source_graphs:
            for triple in self.ds.graph(gid):
                graph.add(triple)
        return graph
