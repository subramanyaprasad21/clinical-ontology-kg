# Documentation map

## Current summaries

- [Extension feasibility](EXTENSION_FEASIBILITY.md): candidate sources and unverified acquisition requirements.

- [Protégé observations](PROTEGE_OBSERVATIONS.md): recorded classification and inverse-relation views.

- [Evaluation and design assessment](EVALUATION.md): executed evidence, design rationale and remaining verification limits.

- [Repository overview](../README.md): implemented scope, measured results and limitations.
- [Semantic model](04_ontology_design_notes.md): annotation meaning, reasoning and export boundaries.
- [Validation results](validation_results.md): current checks and their limits.
- [Reproduction](REPRODUCING.md): inputs, environment and executable commands.
- [Mapping policy](02_mapping_policy.md), [provenance model](provenance_model.md), [competency questions](03_competency_questions.md), [limitations](limitations.md).
- [Protégé inspection guide](PROTEGE_REVIEW_GUIDE.md) and [technical questions](SUPERVISOR_DEFENCE_GUIDE.md).

## Technical implementation and results

[Build report](../reports/FINAL_REPORT.md), [metrics](../reports/metrics.json), [audit checks](../reports/credibility_audit/verification.json), [clean-build hashes](../reports/credibility_audit/clean_builds.json) and [OWL checks](../reports/owl_compatibility.json) are generated evidence. The build report describes its recorded run; current reproduction scope is summarized above. Generated source payloads and RDF exports require a local build.

## Historical records

These records retain their original bytes and may describe earlier counts, limitations or development review state. They are not current status summaries.

- [Design record](DESIGN_DECISIONS.md): recorded modelling rationale and review state through 2026-10-01.
- [Baseline credibility audit](../reports/CREDIBILITY_AUDIT.md): before the export and validation repairs.
- [Export repair record](../reports/EXPORT_VALIDATION_FOLLOWUP.md): 29-test repair stage.
- [Reasoning projection record](../reports/OWL_PROJECTION_REVIEW.md): 2026-10-01 export stage.
- [Initial scope](00_project_charter.md) and [source feasibility](01_data_feasibility_matrix.md): original bounded input study.
- [Earlier in-place repeatability](../reports/reproducibility.json) and `reports/credibility_audit/pre_export_fix/`: prior execution evidence.

## Frozen source identity

[Input manifest](../config/input_manifest.json) records the eleven raw file hashes and version basis. Raw files remain local and are checked before and after builds. Do not regenerate this manifest to accommodate replacement data. Source identity is distinct from publisher authenticity and clinical validity.

## Conventions

[Writing conventions](WRITING_CONVENTIONS.md) govern current documentation and preservation of historical material. [Attribution](../ATTRIBUTION.md) is maintained separately from technical results.
