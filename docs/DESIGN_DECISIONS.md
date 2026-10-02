# Ontology design decisions

This record summarizes the implemented ontology choices and their review state. The project brief fixed the research scope, source set, provenance requirements and prohibition on unsupported clinical claims. The specific OWL vocabulary and modelling choices below are implementation decisions. Development tooling is disclosed separately in [ATTRIBUTION.md](../ATTRIBUTION.md).

**Review status: annotation interpretation and evidence-conflict policy recorded; remaining semantic review pending.** Passing tests or publishing documentation does not by itself establish that every axiom has been reviewed. The rationale in this table describes the implemented design.

| Decision | Implemented choice and rationale | Alternative or limitation to consider |
|---|---|---|
| D1. Scope | T2DM and necessary named ancestors, five HPO terms and mapped disease identifiers. The brief required a bounded case study. | A larger diabetes graph changes the research question and data requirements. |
| D2. Identity | Keep Mondo and OMIM identifiers; use Mondo's explicit SKOS mapping to join annotations. | Merging identifiers would erase source distinctions. Source exactness is not external adjudication. |
| D3. Class/concept distinction | Native disease IRIs are OWL classes and also subjects of terminology-level metadata (`DiseaseConcept`). | Separate concept and disease-class IRIs would make the distinction clearer but require a documented linking model. Current RDF metamodeling is not certified OWL DL. |
| D4. HPO aspects | Map P to `hasPhenotype`, I to `hasInheritanceAnnotation`, C to `hasClinicalModifier`. | Treating all HPO terms as phenotypes would misrepresent onset and inheritance. These remain source annotations, not universal patient claims. |
| D5. Negative annotations | `hasExcludedPhenotype` records a negated P annotation without creating a positive edge. | It is not an OWL negative-property assertion. Exact-IRI positive/excluded pairs are flagged with both provenance chains for review, without rejecting or resolving disagreement. This evidence-preservation and review policy was recorded on 2026-09-16; neither source has automatic priority. No negative annotation is present in the canonical selection. |
| D6. OWL projection | Retain direct named subclass closure; keep nested source restrictions in audit records rather than flattening them into edges. | A proper OWL module extraction would preserve more semantics. The current graph cannot support full-source consistency claims. |
| D7. Reasoning definition | `PhenotypeAnnotatedConcept ≡ DiseaseConcept and (hasPhenotype some HPOTerm)`. | This is an elementary annotation classification. Domain/range makes much of the type condition redundant; it is not a clinical discovery. |
| D8. Inverse/property hierarchy | `hasPhenotype` is a subproperty of `hasHPOAnnotation` and inverse of `phenotypeOf`. | This improves navigation and demonstrates entailment, but adds no independent evidence. |
| D9. Cardinality | No OWL cardinality constraints. SHACL requires selected record fields and limits single-valued statement metadata. | Do not impose “one phenotype” or similar clinical cardinalities merely to demonstrate the syntax. |
| D10. Provenance | Named source graphs, reified statements, original record locators and hashed snapshots. | Direct and transformed assertions are not separately flagged in RDF; inference lineage is process-level rather than a minimal proof for every triple. |
| D11. Unresolved mappings | Retain NANDO as an unresolved xref; import only explicit source mapping predicates. | URI conversion and label similarity alone cannot decide equivalence. |
| D12. Unsupported joins | Audit drug/target catalogs but omit disconnected instances from the T2DM graph. | Adding structured association/indication data would be a separately justified extension. |
| D13. Deterministic export | Canonicalize ontology blank nodes and replace them with stable project IRIs; sort RDF output. | Keep this representation for the RDF dataset only. The review export preserves anonymous restrictions and adds explicit declarations. Installed OWL API/HermiT tests pass the selected entailments, with three provenance profile violations retained. |
| D14. Validation boundary | Validate the asserted projection before inference; test isolated invalid copies. | Generic endpoints now have a shape. A separate report flags exact-IRI positive/excluded pairs; it does not establish clinical contradiction or propagate conflicts through mappings. The conflict-review policy was recorded on 2026-09-16; the remaining validation boundary is still subject to review. |

The source evidence and exact classifications of direct, transformed, authored and inferred statements are in the [credibility audit](../reports/CREDIBILITY_AUDIT.md). The vocabulary is in [core.ttl](../ontology/core/core.ttl); conversion choices are in [graph.py](../src/clinical_kg/graph.py).

## Review method

For each decision, inspect the cited file and a real example. Then record: decision ID, **accept / revise / reject**, your rationale, the evidence inspected, and the actual review date. If you revise an axiom, explain the intended change in entailments and identify a positive and a negative test. Do not mark this review complete merely because the current tests pass.

### Annotation interpretation — 2026-09-16

The disease-level annotation interpretation was recorded on 2026-09-16 with the following wording:

> `hasPhenotype` represents a source-provided disease–phenotype annotation. It denotes that a phenotype has been associated with a disease concept in the source data; it does not imply universal manifestation in all individuals with that disease.

> `PhenotypeAnnotatedConcept` denotes a concept with at least one such phenotype annotation.

Here, “such” means a **positive** phenotype annotation. In the implemented definition, the concept is a `DiseaseConcept` and the annotation target is an `HPOTerm`.

**Rationale:** the supplied data describes disease-level annotations, not patient-level observations. This interpretation avoids a universal clinical claim and preserves the meaning of the source evidence. Classification identifies an annotated concept; it does not establish a clinical discovery or an independently corroborated association.

**Review scope:** this decision covers the conceptual distinction underlying D3, the positive-phenotype meaning in D4, and the intended interpretation of D7. It does not establish review of shared class/individual IRIs, all aspect mappings, every OWL axiom, or the complete design. No manual Protégé inspection or source-file review is implied by this record.

### Evidence-conflict policy — 2026-09-16

The evidence-conflict policy was recorded on 2026-09-16 with the following wording:

> Conflicting positive and excluded phenotype annotations are both retained with source provenance. Their coexistence is represented as a conflict condition for downstream review or analysis; neither assertion is discarded or automatically privileged.

**Rationale:** preserve the evidence first; resolve disagreement only when there is a defensible resolution rule. No source automatically dominates another. Introducing an evidence hierarchy later requires an explicit, separately reviewed policy.

**Implementation boundary:** the current detector flags positive/excluded assertions for the same disease IRI and phenotype IRI, including same-source and cross-source cases. It retains both provenance chains and reports the pair for human review. This is an evidence-conflict flag, not a claim that the OWL ontology is inconsistent or that the annotations have identical clinical context. The detector does not propagate conflicts through mappings or adjudicate source reliability. The frozen selection contains no such pair; regression cases exercise the policy.

**Review scope:** this covers the evidence-preservation and conflict-review policy in D5 and the corresponding reporting policy in D14. It does not certify every validation constraint or endorse a particular formal negation representation. No manual inspection of source files or Protégé is implied by this record.

D13's export choices and other unreviewed details remain pending. A separate OWL reasoning projection was implemented and tested on 2026-10-01; its [scope and proposed boundary](../reports/OWL_PROJECTION_REVIEW.md) remain documented separately. Development tooling is disclosed in [ATTRIBUTION.md](../ATTRIBUTION.md).
