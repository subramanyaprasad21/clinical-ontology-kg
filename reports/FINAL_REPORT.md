# T2DM knowledge graph — completed frozen-source core

The supplied snapshots support a small, reproducible disease/phenotype semantic graph. They do **not** support a structured T2DM drug/target graph. This report preserves that boundary instead of filling it with assumed clinical relations.

## Verified result

| Measure | Result |
|---|---:|
| Frozen raw files | 11 |
| Raw bytes | 487,211,049 |
| Named hierarchy classes, including anchor and upper ontology context | 17 |
| HPO terms | 5 |
| Positive phenotype terms | 3 |
| HPO annotation records | 5 |
| OT annotation rows | 5 |
| Duplicate nested OT evidence entries | 5 |
| Source-asserted exact mappings | 10 |
| Unresolved mappings | 1 |
| Source quads / unique source triples | 174 / 160 |
| Source assertion records | 179 |
| Complete recorded assertion provenance | 100.0% |
| Canonical SHACL conformity | True |
| Deliberately invalid cases detected | 6 / 6 |
| Exported OWL RL additions, including bookkeeping | 585 |
| Internal generalized RDF triples excluded from standard export | 84 |
| RDF dataset and Turtle round trips verified | True |
| T2DM-linked targets / drugs | 0 / 0 |

Triples are counted as representation size, not as proof of clinical quality. The complete statement-provenance percentage does not authenticate the declared Open Targets release or recover missing download history.

## What the graph says

Mondo `MONDO:0005148` has direct parent `MONDO:0005015` (diabetes mellitus). Its explicit Mondo exact mapping reaches `OMIM:125853`, the HPOA disease identifier. Open Targets preserves the same Mondo IRI.

| HP_0000006 | Autosomal dominant inheritance |
| HP_0000855 | Insulin resistance |
| HP_0003584 | Late onset |
| HP_0005978 | Type II diabetes mellitus |
| HP_0031819 | Increased waist to hip ratio |

Only insulin resistance, Type II diabetes mellitus, and increased waist-to-hip ratio are source-aspect P phenotype associations. Autosomal dominant inheritance and late onset remain separate source annotation types. The HPO term named Type II diabetes mellitus is not equated to the Mondo disease solely on naming.

Open Targets repeats HPO-derived evidence. Five annotations occur across two source deliveries, but there is one distinct upstream annotation resource (HPO); independent corroboration has not been established. One NANDO xref remains unresolved.

## Executable competency questions

| Query | Result status | Rows |
|---|---|---:|
| 01_hierarchy | answered | 16 |
| 02_phenotypes | answered | 6 |
| 03_phenotype_evidence | answered | 9 |
| 04_disease_targets | unsupported | 0 |
| 05_drugs | unsupported | 0 |
| 06_disease_target_drug_path | unsupported | 0 |
| 07_mappings | answered | 11 |
| 08_multi_source_annotations | answered | 5 |
| 09_inference | answered | 22 |
| 10_provenance | answered | 179 |
| 11_validation_violations | answered | 0 |

The phenotype query returns separate source disease identifiers, so six rows represent three terms across the Mondo and OMIM concepts. Evidence occurrences are not independent studies. Zero rows for the drug/target questions mean the supplied data cannot support the query; they do not assert absence of drugs or biological associations in the world. Zero SHACL result rows means no violations were detected in the canonical graph.

The mechanism audit checked 6,500 records: every one of 12,698 target references and 7,924 drug references resolves locally. The missing relation is the clinical link to T2DM, not a broken identifier join between these catalogs.

## Reasoning and validation

OWL RL derives `PhenotypeAnnotatedConcept` membership from the local equivalent-class definition and actual positive phenotype annotations. It also derives inverse phenotype relations and transitive named ancestors. These classifications are about terminology concepts, not patients or treatments. See [reasoning examples](tables/reasoning_examples.json).

SHACL checks required identifiers/labels, relationship endpoint types, statement provenance, source versions and hashes, record locators/payloads, and allowed mapping predicates. Six isolated mutations exercise missing label, missing identifier, missing statement provenance, missing source version, malformed phenotype target and illegal mapping predicate. See [invalid cases](tables/invalid_cases.json) and [canonical report](validation.txt). Fixtures never enter the canonical graph.

Additional tests cover negation, premise-dependent inference, raw changes, source evidence duplication, label-based mapping prevention, and serialization round trips. The final test execution is recorded in [tests.txt](tests.txt). Two complete builds are compared in [reproducibility.json](reproducibility.json); this is same-environment repeatability, not a cross-platform guarantee.

## Reproduction and review

Follow [the README](../README.md). The full named-graph artifact is [knowledge_graph.nq](../data/processed/knowledge_graph.nq). The Protégé-friendly asserted union plus local ontology is [review.ttl](../data/processed/review.ttl). Machine-readable [metrics](metrics.json), [query answers](tables/competency_results.json), [schemas](tables/input_schemas.json), [mapping candidates](tables/mapping_candidates.json) and [artifact hashes](artifact_checksums.json) support review.

## Material limitations

Mondo and HPO OWL versions are `2026-09-01`; the actual HPOA header is `2026-09-02`. OT `26.06` is user-declared and not independently confirmed by Parquet metadata. Original download URLs/dates remain unknown in the manifest. The OWL projection excludes execution of nested source restrictions and is not a full ontology consistency proof. Source mapping judgments are preserved, not externally re-adjudicated. No biomedical sources were downloaded, no raw input was modified, and no public distribution was performed.

Read the [feasibility audit](../docs/01_data_feasibility_matrix.md), [mapping policy](../docs/02_mapping_policy.md), [ontology design](../docs/04_ontology_design_notes.md), [provenance model](../docs/provenance_model.md), and [limitations](../docs/limitations.md) for the precise scope.

Build fingerprint: `2b35d6f2b11d9713646c7fc402ad05651f48e42b49896ec5d87875d24e36d140`.
