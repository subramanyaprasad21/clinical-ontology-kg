# Validation

Validation is split between the frozen core and the 26.09 clinical extension.

## Frozen core

SHACL runs before reasoning with inference disabled. This keeps inferred types from hiding missing imported endpoint types.

The canonical graph conforms. Six isolated mutations fail in the expected way: missing label, missing identifier, missing assertion source, missing source version, literal phenotype target and forbidden mapping predicate. These tests operate on copies and do not change the canonical dataset.

The core regression suite has 31 passing tests and the separate fidelity audit has 35 passing checks. Two clean workspaces reproduce 20 artifacts byte-for-byte with different Python hash seeds. A later fresh virtual environment installs the pinned dependencies, passes the same tests and audit checks, and reproduces all 20 artifacts on the same host.

Every exported RDF view is reparsed. Blank-node views are compared by graph isomorphism; dataset quads are compared exactly. Raw input hashes are checked again after the build.

The OWL reasoning projection has zero OWL 2 DL profile violations under the installed OWL API. HermiT checks consistency, selected classification and inverse entailments, and their loss after premise removal. The full review export retains three provenance-related profile violations.

## Clinical extension

The 26.09 extension uses separate SHACL shapes and 15 tests for join failures, identifier boundaries, report context, missing metadata, stage isolation and invalid report structures.

Together with the core suite, 46/46 tests pass. The independent verifier matches all 38,886 imported payloads and all 186,676 resolved report references against captured source rows. It also checks 798 supported paths and 2,401 path-to-record links.

The serialized extension has 1,077,529 quads across four named graphs. Zero report references are unresolved.

The final same-host verification runs the core build, extension build, all tests, the 35-check core audit, clean core builds, OWL checks and the independent extension verifier in an isolated workspace. Twenty core artifacts and three final extension artifacts match the recorded outputs byte-for-byte under a different hash seed.

## Boundary

These checks establish repeatable software behaviour for the captured inputs. They do not establish clinical truth, independent source corroboration, cross-platform behaviour or correctness of every modelling choice.

Null QC fields remain null, flags remain present, and missing report-stage metadata remains missing. SHACL conformity is not a clinical-quality judgement.
