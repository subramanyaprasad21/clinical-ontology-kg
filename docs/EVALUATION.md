# Evaluation and design assessment

This is the current evaluation of the bounded T2DM integration. Historical audit records remain unchanged. The implemented source scope and clinical limitations are retained.

## Executed evidence

| Check | Observation | Boundary |
|---|---|---|
| Source fidelity | 35/35 separate audit checks pass; 38 records and 179 assertion occurrences checked | Same RDF libraries; not external clinical adjudication |
| Regression suite | 31/31 tests pass | Selected semantic and implementation failure cases |
| Clean-output reproduction | Two workspaces reproduce 20 artifacts byte-for-byte | Shared installed environment, different hash seeds |
| Fresh installation | Install, dependency check, build, 31 tests and 35 audit checks pass; 20 artifacts match byte-for-byte | New virtual environment on the same host and base Python; raw files reused |
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
| D12 unsupported joins | Keep the three clinical drug/target queries unsupported. Catalog connectivity cannot supply the missing T2DM relation. |
| D13 exports | Use the explicitly scoped reasoning projection for DL checks and the dataset for provenance. The 13 exclusions are auditable; this does not repair or certify the full review ontology. |
| D14 validation | Keep pre-inference shapes and separate conflict reporting. Neither establishes clinical truth or complete constraint coverage. |

These conclusions assess the implemented model against its source scope and tests. They do not establish that every design choice is uniquely correct, that the ontology was independently authored or that every axiom has been inspected. Attribution is recorded separately in [ATTRIBUTION.md](../ATTRIBUTION.md).

## Remaining verification boundary

The selected GUI classification and inverse checks are now observed. The broader inspection guide is not an exhaustive completed axiom review. The library-level checks already exercise the installed OWL API and HermiT versions. Missing acquisition history and the absence of structured T2DM drug/target data remain source limitations, not implementation defects.
