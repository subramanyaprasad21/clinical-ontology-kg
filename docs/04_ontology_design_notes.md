# Semantic model and export boundaries

The ontology is `ontology/core/core.ttl`; this document supersedes the initial provisional class list.

| Technology | Implemented purpose |
|---|---|
| RDF | Source facts, evidence records, snapshots and statement reification |
| RDFS | Native named disease subclass hierarchy; terminology class and property hierarchy |
| OWL | Source class declarations, inverse phenotype relation, existential/intersection definition, executed OWL 2 RL closure |
| SKOS | Source exact mappings and concept-level typing; synonyms preserved as alternative labels |
| PROV-O | Assertion → source record → source snapshot; build and reasoning activities |
| SHACL | Entity, relationship, statement, mapping, record and snapshot checks |
| SPARQL | Eleven executable competency queries over explicitly selected named graphs |

## Concepts, not patient instances

Native Mondo IRIs remain `owl:Class` subjects in the disease hierarchy. The same identifiers carry terminology metadata using `kg:DiseaseConcept` (OWL 2 punning / RDF metamodeling). An instance of `kg:DiseaseConcept` describes a terminology concept; it is not a patient diagnosed with that disease. BFO ancestors are `kg:OntologyConcept`, never disease concepts. HPO terms are `kg:HPOTerm`; the HPO subclass hierarchy is not imported in this bounded projection.

HPO associations use three distinct predicates for source aspects P, I and C. A negated P annotation uses `kg:hasExcludedPhenotype` and alone does not produce a positive classification. Unknown/non-P negative aspects are not converted to positive relations. All source evidence is retained in record payloads; the currently selected records contain no such excluded aspects.

`kg:PhenotypeAnnotatedConcept` is equivalent to the intersection of `kg:DiseaseConcept` and a restriction `kg:hasPhenotype some kg:HPOTerm`. A real OWL RL execution classifies the T2DM and mapped OMIM concepts from their positive annotations. `owl:inverseOf` yields phenotype-to-disease-concept links. Named superclass chains yield additional ancestors. These demonstrate semantic inference without inventing drugs, indications, or patient diagnoses.

## Projection boundary

The OWL reader streams XML and extracts named classes, direct named parents, labels, xrefs, exact synonyms, explicit SKOS mappings and a record of nested restrictions. Only the anchor's synonyms/xrefs/mappings are added to the fact graph. Complete named-parent closure adds necessary context, including BFO ancestors. Nested restrictions are retained as XML in the audit/source record projection but **not** translated into simple clinical edges. Other OWL constructs, axiom annotations, disjointness and remote imports are not part of the graph projection. Raw input remains the authoritative full source.

This is not a logically complete OWL module extraction or whole-Mondo consistency check. The classification demonstration is restricted to the local ontology and projected source facts. SHACL conformity does not establish medical truth or full OWL consistency.

Ontology blank nodes are canonicalized and assigned deterministic project IRIs before graph construction. The local `https://example.org/clinical-kg/` namespace is intentionally a project placeholder and makes no claim to be a resolvable public ontology.

No drug, target, pathway or measurement instances are introduced because the audit provides no bounded, structured connection from those records to T2DM. The corresponding competency queries remain explicit negative queries.

## Annotation and conflict semantics

`hasPhenotype` represents a source-provided disease–phenotype annotation. It denotes that a phenotype has been associated with a disease concept in the source data; it does not imply universal manifestation in all individuals with that disease. `PhenotypeAnnotatedConcept` denotes a `DiseaseConcept` with at least one positive annotation to an `HPOTerm`.

Conflicting positive and excluded phenotype annotations are both retained with source provenance. Their coexistence is flagged for downstream evidence review; neither assertion is discarded or automatically privileged. The detector compares exact disease/phenotype IRI pairs, preserves both record chains, and does not propagate conflicts through mappings. Such a pair need not establish an OWL inconsistency or identical clinical context. No such pair occurs in the frozen selection; tests cover same-source and cross-source fixtures.

## Export views

| File | Content and reasoning boundary |
|---|---|
| `knowledge_graph.nq` | Named source graphs, provenance, schema, inference and validation; schema nodes use stable project IRIs for RDF processing |
| `review.ttl` | Asserted facts plus full local schema, with anonymous OWL restrictions restored; three provenance-related DL profile violations remain |
| `reasoning.ttl` | All 160 asserted source triples and terminology axioms; 13 provenance-schema triples excluded explicitly |
| `provenance.ttl` | Assertion, record, snapshot and activity metadata for evidence inspection |

`reports/tables/reasoning_export.json` lists every excluded triple. Recombining exclusions with the reasoning projection reconstructs the full review graph up to blank-node identity. The builder rejects source use of excluded vocabulary and dangling references to it in the projection. This boundary is an implemented export choice, not a general module-extraction algorithm.

OWL API 4.5.29 detects zero DL profile violations in the reasoning projection. HermiT 1.4.3.456 derives the tested concept classification and inverse; removing the six positive assertions removes both selected entailments. These observations support this bounded export, not the full upstream ontologies or clinical validity.

## Terminology

A **source record** is an extracted row or XML record with a locator and payload. An **assertion occurrence** connects a represented statement to a record and named graph. A **triple** is a unique subject–predicate–object statement; a **quad** additionally includes its graph. **Provenance** records origin and transformation history; repeated provenance does not necessarily provide independent **evidence**. **Validation** checks selected graph constraints; **verification** compares implementation results with source records or specified expectations.
