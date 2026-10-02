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
- [Protégé observations](PROTEGE_OBSERVATIONS.md) records the selected GUI checks already performed; the broader [review guide](PROTEGE_REVIEW_GUIDE.md) contains additional inspection steps that were not all executed.

## Machine-readable results

Final extension counts are in [reports/final/extension_summary.json](../reports/final/extension_summary.json). Report resolution is in [reports/extension/clinical_report_audit.json](../reports/extension/clinical_report_audit.json). The independent extension comparison is in [reports/final/extension_verification.json](../reports/final/extension_verification.json), and the complete same-host verification is in [reports/final/project_verification.json](../reports/final/project_verification.json).

The committed final verification evidence is concentrated under [`reports/final/`](../reports/final/). Large RDF exports, raw source payloads and generated `reports/tables/` files are local build products and are intentionally not stored in Git. Historical reports may link to those generated paths because they document the build outputs available at that stage.

## Historical records

Some files are retained because later verification hashes them. They may describe an earlier stage of the project and should not be read as the current status.

The following are historical or stage-specific records:

- [Extension feasibility](EXTENSION_FEASIBILITY.md): documentation-only planning before the 26.09 capture and graph build.
- [Extension capture](EXTENSION_CAPTURE.md): source-capture state before the RDF extension was completed.
- [Scientific and semantic audit](../reports/CREDIBILITY_AUDIT.md): baseline audit before the later export/validation fixes and clinical extension.
- [Export and validation follow-up](../reports/EXPORT_VALIDATION_FOLLOWUP.md): repair-stage record superseded in part by the later reasoning projection and final verification.
- [OWL projection review](../reports/OWL_PROJECTION_REVIEW.md): reasoning-projection checkpoint before the completed extension verification.
- [Design decisions](DESIGN_DECISIONS.md): retained design record whose own review-status wording reflects the stage at which it was written.

The protected-file list is [reports/final/protected_files.json](../reports/final/protected_files.json). The current README, evaluation, validation, reproduction notes and committed `reports/final/` results take precedence when a historical document describes an earlier count, limitation or pending action.

## Source identity

The [core input manifest](../config/input_manifest.json) records the eleven frozen source-file hashes and version basis. Those hashes identify the local snapshots. They do not reconstruct missing historical download receipts or independently authenticate the declared Open Targets 26.06 release.
