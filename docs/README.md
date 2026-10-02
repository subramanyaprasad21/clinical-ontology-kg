# Documentation

The README gives the shortest view of the project. The files below contain the details behind it.

## Current notes

- [Clinical extension](CLINICAL_EXTENSION.md) describes the Open Targets 26.09 record model, join rule, report resolution and final counts.
- [Evaluation](EVALUATION.md) records the executed checks and the boundary of each result.
- [Validation](validation_results.md) summarizes core and extension validation.
- [Reproduction](REPRODUCING.md) lists the build and verification commands.
- [Ontology design](04_ontology_design_notes.md) explains the local annotation model and reasoning boundary.
- [Mapping policy](02_mapping_policy.md) records how external identifiers are handled.
- [Provenance model](provenance_model.md) describes statement, record and snapshot provenance.
- [Limitations](limitations.md) collects the remaining data, modelling and reproduction limits.
- [Protégé observations](PROTEGE_OBSERVATIONS.md) records the GUI checks already performed.

## Machine-readable results

Final extension counts are in [reports/final/extension_summary.json](../reports/final/extension_summary.json). Report resolution is in [reports/extension/clinical_report_audit.json](../reports/extension/clinical_report_audit.json). The independent extension comparison is in [reports/final/extension_verification.json](../reports/final/extension_verification.json), and the complete same-host verification is in [reports/final/project_verification.json](../reports/final/project_verification.json).

The core build report, metrics, OWL checks and audit outputs under `reports/` are generated evidence. Large RDF exports and raw source payloads are local build products and are not stored in Git.

## Historical records

Some files are retained exactly because later verification hashes them. They may describe an earlier stage of the project and should not be read as the current status.

This includes the design record, original extension capture, baseline credibility audit, export follow-up, reasoning projection review and earlier reproducibility outputs. The protected-file list is [reports/final/protected_files.json](../reports/final/protected_files.json).

The current README, evaluation, validation and reproduction notes take precedence when a historical document describes an earlier count or limitation.

## Source identity

The [core input manifest](../config/input_manifest.json) records the eleven frozen source-file hashes and version basis. Those hashes identify the local snapshots. They do not reconstruct missing historical download receipts or independently authenticate the declared Open Targets 26.06 release.
