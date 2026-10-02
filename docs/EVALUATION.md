# Evaluation and design assessment

This evaluation distinguishes the frozen core (declared Open Targets 26.06) from the separate Open Targets 26.09 clinical extension. Historical audit records and all other core competency results remain unchanged.

## Executed evidence

| Check | Observation | Boundary |
|---|---|---|
| Source fidelity | 35/35 separate audit checks pass; 38 records and 179 assertion occurrences checked | Same RDF libraries; not external clinical adjudication |
| Regression suite | 46/46 tests pass: 31 core and 15 extension | Selected semantic and implementation failure cases |
| Clean-output reproduction | Two workspaces reproduce 20 artifacts byte-for-byte | Shared installed environment, different hash seeds |
| Fresh installation | Install, dependency check, core/extension builds, 46 tests and 35 core audit checks pass; 20 core and three extension artifacts match byte-for-byte | Same host/base Python; hashed raw files reused |
| Extension source comparison | 38,886 payloads, 186,676 report links, 798 paths and 2,401 support links verified | Raw-row comparison; not clinical adjudication |
| Extension SHACL | Conforms; three synthetic report failures rejected | Structural record/provenance constraints; no extension OWL reasoning |
| OWL projection | Zero DL profile violations; selected HermiT entailments and premise-removal control pass | `reasoning.ttl` only; full review retains three violations |
| GUI inspection | Two inferred concept instances, Mondo classification and two insulin-resistance inverse links observed | Selected views in `reasoning.ttl`; see [observations](PROTEGE_OBSERVATIONS.md) |

The fresh-environment procedure creates a virtual environment without system packages, installs the pinned requirements with pip's cache disabled, runs `pip check`, builds in a workspace without derived outputs, runs the regression suite and separate audit, and compares all selected artifacts against the recorded outputs. Its result records package versions, exit codes, requirements hash and artifact hashes. This extends the earlier clean-output check; it does not test another operating system, independently install Python, or reacquire raw files.

## Technical design assessment

| Decision | Assessment and retained limitation |
|---|---|
| D1 scope | Retain the bounded T2DM case; extending coverage requires additional source relations and a revised evaluation. |
| D2 identity | Preserve native Mondo/OMIM identifiers and explicit SKOS claims. Mapping fidelity does not independently establish equivalence. |
| D3 class/concept roles | Retain disease-class hierarchy and terminology-individual annotations. The tested DL projection accepts this use; patient-level semantics are outside scope. |
| D4 annotation aspects | Preserve P/I/C distinctions. Positive annotation means a source association, not universal patient manifestation. |
| D5 exclusion | Preserve excluded annotations separately. Exact-IRI conflicts retain both provenance chains with no source priority. |
| D6 source projection | Named hierarchy extraction is sufficient for the selected queries. It does not preserve or reason over every upstream axiom. |
| D7 definition | Retain the existential definition as an annotation classification. Premise-removal checks demonstrate dependence on positive source annotations. |
| D8 inverse and hierarchy | Retain navigation entailments. They do not create independent evidence. |
| D9 cardinality | Keep structural counts in SHACL. No source evidence justifies clinical OWL cardinality restrictions. |
| D10 provenance | Retain named graphs and assertion/record/snapshot chains. Per-inferred-triple minimal proofs are not implemented. |
| D11 unresolved mappings | Preserve unresolved NANDO metadata without inventing an equivalence. |
| D12 clinical joins | Frozen core remains unsupported. The separate extension supports 613 indications and 798 clinical-context paths using exact indication/mechanism/clinical-target joins. General disease–target association remains unsupported. |
| D13 exports | Use the explicitly scoped reasoning projection for DL checks and the dataset for provenance. The 13 exclusions are auditable; this does not repair or certify the full review ontology. |
| D14 validation | Keep pre-inference shapes and separate conflict reporting. Neither establishes clinical truth or complete constraint coverage. |

These conclusions assess the implemented model against its source scope and tests. They do not establish that every design choice is uniquely correct, that the ontology was independently authored or that every axiom has been inspected. Attribution is recorded separately in [ATTRIBUTION.md](../ATTRIBUTION.md).

## Remaining verification boundary

The selected GUI classification and inverse checks are now observed. The broader inspection guide is not an exhaustive completed axiom review. The library-level checks already exercise the installed OWL API and HermiT versions. Missing historical acquisition details and absent general disease–target association data remain source limitations. The extension supplies structured clinical context but does not establish efficacy or independently verify approval.

## Completed clinical extension

The [final summary](../reports/final/extension_summary.json), [source comparison](../reports/final/extension_verification.json) and [full-project verification](../reports/final/project_verification.json) contain the measured results. The separate graph has 1,077,529 unique triples/quads in four named graphs and 39,696 subject resources: 613 indication records, 434 mechanism records, 798 clinical-target records, one disease record, 37,040 reports, derived paths and provenance resources. There are 613 indication drugs, 372 path drugs and 333 targets.

All 37,040 report IDs resolve, covering 6,201 indication references and 180,475 clinical-target references; unresolved references: zero. Report resolution is distinct from context: 137,473 clinical-target references lack T2DM. QC flags remain on 8,353 reports; 28,687 have null QC fields. Missing `phaseFromSource` values on 6,797 reports remain explicit. No report-level stage is copied to an indication or path.

| Question | Unchanged query on extension | Record-aware executed result | Current interpretation |
|---|---:|---:|---|
| 04: disease-associated targets | 0 rows | 333 clinical-context targets | Partial clinical-context answer; general association evidence absent |
| 05: drugs connected to T2DM | 0 rows | 613 source indications | Answered within indication scope; not all approved therapies |
| 06: disease–target–drug path | 0 rows | 798 supported clinical paths | Partial clinical-context answer; no general association leg asserted |

The zero results use the original core vocabulary. The separate queries use record semantics and preserve the narrower meaning of the clinical extension. Core query files and historical results are unchanged; questions 01–03 and 07–11 retain their previous assessment. Query counts are neither a drug recommendation nor a measure of independent clinical evidence.
