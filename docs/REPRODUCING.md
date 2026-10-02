# Reproduce the local results

The tested environment is Python 3.12.7 with the exact package versions in [requirements.txt](../requirements.txt). The implementation accepts Python 3.12 and checks installed package versions before building. The repository contains code, ontology, input hashes and selected aggregate evidence. Raw data, detailed source payloads, environments and execution logs remain local.

## Inputs and environment

You need the eleven files named in [input_manifest.json](../config/input_manifest.json), in their original `data/raw/` paths. The manifest records file size and SHA-256, observed ontology/HPOA versions, and the declared OT version. It does not contain a verified download recipe. Do not substitute a current release or regenerate the manifest to bypass a mismatch.

From the repository root on macOS/Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m pytest -q
```

On Windows use `.venv\Scripts\python.exe` after creating the virtual environment. Windows execution has not been tested. Package installation needs network access; the build reads the local frozen files and does not resolve remote ontology imports.

The build verifies hashes, runs the source audit, constructs the projected graph, validates source facts and provenance, exercises isolated invalid cases, executes OWL RL, runs all queries and compares exported RDF with its in-memory form. It checks raw hashes again before reporting success. `freeze_inputs.py` created the existing manifest and refuses to overwrite it; routine reproduction does not use it.

## Additional checks

```sh
.venv/bin/python audit/verify.py
.venv/bin/python audit/clean_builds.py
.venv/bin/python scripts/query.py queries/competency/03_phenotype_evidence.rq
```

The first command runs the separate 35-check audit. The second constructs two temporary workspaces with empty derived-output directories, links the same read-only raw inputs, varies the Python hash seed, runs 31 tests in each, and compares 20 artifacts byte-for-byte. It requires a filesystem that supports the hard links used by the script. Both share the installed environment; neither tests package installation or raw acquisition on another machine.

The earlier `scripts/check_reproducibility.py` checks two in-place builds instead. Its retained summary is valid evidence for that narrower procedure. No original result was overwritten to pretend it came from a clean workspace.

## Generated files

| Local path | Purpose |
|---|---|
| `data/processed/knowledge_graph.nq` | Source, schema, provenance, inference and validation named graphs |
| `data/processed/reasoning.ttl` | OWL reasoning projection; exclusions listed in `reports/tables/reasoning_export.json` |
| `data/processed/review.ttl` | Source union plus schema for review; graph separation is lost |
| `data/processed/asserted.ttl`, `inferred.ttl` | Separate source and reasoner views |
| `data/processed/provenance.ttl`, `mappings.ttl` | Record/statement lineage and mapping view |
| `reports/tables/` | Full query answers, schemas, reasoning examples, invalid-case summaries |
| `reports/credibility_audit/` | Separate audit summaries and detailed local comparisons |

Tracked [verification](../reports/credibility_audit/verification.json) and [clean-build](../reports/credibility_audit/clean_builds.json) summaries record the executed audit. Detailed evidence files are generated locally. The original generated report contains links to those local artifacts; their absence in a bare Git checkout is expected, not evidence that the computations ran there.

## OWL profile and entailment checks

The tested libraries are OWL API 4.5.29 and HermiT 1.4.3.456 from Protégé 5.6.9, with JDK 17. The check compiles its Java probe locally and requires no download. Set these variables to the installed application contents and JDK directories:

```sh
export KG_PROTEGE_CONTENTS='/path/to/Protege.app/Contents'
export KG_JAVA_HOME='/path/to/jdk/Contents/Home'
.venv/bin/python audit/owl/check.py \
  --protege-contents "$KG_PROTEGE_CONTENTS" \
  --java-home "$KG_JAVA_HOME"
```

The check requires zero profile violations for `reasoning.ttl`, consistency, the selected classification and inverse, and loss of those entailments after removing six positive annotation assertions from an in-memory copy. The full `review.ttl` retains three reported profile violations. This is a library-level check, not a GUI inspection or a full-source consistency result.

## Fresh dependency installation

```sh
.venv/bin/python audit/fresh_environment.py
```

This creates a new virtual environment, installs pinned packages with the pip cache disabled, runs `pip check`, builds in a separate empty workspace, runs tests and the separate audit, and compares 20 artifacts with recorded outputs. Package installation requires network access. The same host, base Python and hard-linked frozen raw inputs are reused. Results are saved in `reports/fresh_environment/result.json`; temporary paths in execution logs remain local.

## Final separate clinical extension

The final builder requires the four context-table captures in [capture_manifest.json](../reports/extension/capture_manifest.json) and the report capture in [clinical_report_manifest.json](../reports/extension/clinical_report_manifest.json), including their saved directory listings. Place the exact bytes at the receipt paths under `data/extensions/opentargets-26.09/`. The receipts include archive URLs, sizes and hashes. Hash mismatch fails replay; do not regenerate receipts to accept replacement bytes. The earlier `derived/` graph is retained as historical evidence; completed outputs are written to `final/`.

```sh
.venv/bin/python audit/extension/final_build.py
.venv/bin/python audit/extension/verify_final.py
.venv/bin/python -m pytest -q tests audit/extension/test_build.py audit/extension/test_reports.py
```

The builder rereads captured Parquet, resolves report IDs, builds four named graphs, validates structural shapes and executes original competency queries 04–06 plus three record-aware variants. Outputs are `data/extensions/opentargets-26.09/final/extension.nq`, `query_results.json` and `validation.txt`. Local report inspection files separate selected report records from per-reference context checks. The final summary records resolved counts and an explicit unresolved-reference list. The independent verifier compares imported payloads, report fields, QC state, stages, resolutions and paths with raw rows.

## Complete verification without replacing historical reports

With the installed Protégé and JDK directories configured as above:

```sh
.venv/bin/python audit/extension/verify_project.py \
  --protege-contents "$KG_PROTEGE_CONTENTS" \
  --java-home "$KG_JAVA_HOME"
```

This command creates a temporary workspace and fresh virtual environment, installs pinned requirements without the pip cache, runs dependency checks, the core build, all 46 tests, the 35-check core audit, two clean core builds, two in-place core builds, OWL/HermiT checks, the final extension build and its independent audit. It compares 20 core and three extension artifacts with existing local outputs and verifies the [protected-file baseline](../reports/final/protected_files.json). Baseline core and final extension outputs must exist before the comparison. Network access is needed only for package installation; input files are hard-linked into the temporary workspace and read without modification.

All steps passed in the [recorded final run](../reports/final/project_verification.json). All compared artifacts and extension summaries were byte-identical under hash seed `707`. Reports are written under `reports/final/`; detailed execution logs stay local. Historical reports remain unchanged. This is same-host reproduction, not a test of another OS, Python installation or new raw acquisition.
