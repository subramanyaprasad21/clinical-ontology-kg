# Ontology design decisions

This record makes the implemented choices available for author review. It is not a certificate of unaided authorship. The supplied project brief fixed the research scope, source set, provenance requirements and prohibition on unsupported clinical claims. AI assistance translated that brief into code and also proposed the specific OWL vocabulary and modelling choices below.

**Review status: author semantic sign-off pending.** A request to finish or publish documentation does not establish that each axiom has been reviewed. The rationale in this table describes the implemented design; it is not presented as a verbatim record of the author's reasoning.

| Decision | Implemented choice and rationale | Alternative or limitation to consider |
|---|---|---|
| D1. Scope | T2DM and necessary named ancestors, five HPO terms and mapped disease identifiers. The brief required a bounded case study. | A larger diabetes graph changes the research question and data requirements. |
| D2. Identity | Keep Mondo and OMIM identifiers; use Mondo's explicit SKOS mapping to join annotations. | Merging identifiers would erase source distinctions. Source exactness is not external adjudication. |
| D3. Class/concept distinction | Native disease IRIs are OWL classes and also subjects of terminology-level metadata (`DiseaseConcept`). | Separate concept and disease-class IRIs would make the distinction clearer but require a documented linking model. Current RDF metamodeling is not certified OWL DL. |
| D4. HPO aspects | Map P to `hasPhenotype`, I to `hasInheritanceAnnotation`, C to `hasClinicalModifier`. | Treating all HPO terms as phenotypes would misrepresent onset and inheritance. These remain source annotations, not universal patient claims. |
| D5. Negative annotations | `hasExcludedPhenotype` records a negated P annotation without creating a positive edge. | It is not an OWL negative-property assertion. Exact-IRI positive/excluded pairs are flagged with both provenance chains for review, without rejecting or resolving disagreement. Human acceptance of this review policy is pending. No negative annotation is present in the canonical selection. |
| D6. OWL projection | Retain direct named subclass closure; keep nested source restrictions in audit records rather than flattening them into edges. | A proper OWL module extraction would preserve more semantics. The current graph cannot support full-source consistency claims. |
| D7. Reasoning definition | `PhenotypeAnnotatedConcept ≡ DiseaseConcept and (hasPhenotype some HPOTerm)`. | This is an elementary annotation classification. Domain/range makes much of the type condition redundant; it is not a clinical discovery. |
| D8. Inverse/property hierarchy | `hasPhenotype` is a subproperty of `hasHPOAnnotation` and inverse of `phenotypeOf`. | This improves navigation and demonstrates entailment, but adds no independent evidence. |
| D9. Cardinality | No OWL cardinality constraints. SHACL requires selected record fields and limits single-valued statement metadata. | Do not impose “one phenotype” or similar clinical cardinalities merely to demonstrate the syntax. |
| D10. Provenance | Named source graphs, reified statements, original record locators and hashed snapshots. | Direct and transformed assertions are not separately flagged in RDF; inference lineage is process-level rather than a minimal proof for every triple. |
| D11. Unresolved mappings | Retain NANDO as an unresolved xref; import only explicit source mapping predicates. | URI conversion and label similarity alone cannot decide equivalence. |
| D12. Unsupported joins | Audit drug/target catalogs but omit disconnected instances from the T2DM graph. | Adding structured association/indication data would be a separately justified extension. |
| D13. Deterministic export | Canonicalize ontology blank nodes and replace them with stable project IRIs; sort RDF output. | Keep this representation for the RDF dataset only. The review export preserves anonymous restrictions and adds explicit declarations. Installed OWL API/HermiT tests pass the selected entailments, with three provenance profile violations retained. |
| D14. Validation boundary | Validate the asserted projection before inference; test isolated invalid copies. | Generic endpoints now have a shape. A separate report flags exact-IRI positive/excluded pairs; it does not establish clinical contradiction or propagate conflicts through mappings. Human policy review is pending. |

The source evidence and exact classifications of direct, transformed, authored and inferred statements are in the [credibility audit](../reports/CREDIBILITY_AUDIT.md). The vocabulary is in [core.ttl](../ontology/core/core.ttl); conversion choices are in [graph.py](../src/clinical_kg/graph.py).

## Recording your review

For each decision, inspect the cited file and a real example. Then record: decision ID, **accept / revise / reject**, your rationale, the evidence inspected, and the actual review date. If you revise an axiom, explain the intended change in entailments and identify a positive and a negative test. Do not mark this review complete merely because the current tests pass.

No decisions have been marked reviewed here. The first useful author-led review is D3, D5, D7 and D13: they contain the largest modelling trade-offs. This gives you a concrete way to demonstrate design judgment while retaining an accurate account of how the implementation was produced.
