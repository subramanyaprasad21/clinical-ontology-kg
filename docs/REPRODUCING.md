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

The first command runs the separate 35-check audit. The second constructs two temporary workspaces with empty derived-output directories, links the same read-only raw inputs, varies the Python hash seed, runs the original tests in each, and compares 17 artifacts byte-for-byte. It requires a filesystem that supports the hard links used by the script. Both share the installed environment; neither tests package installation or raw acquisition on another machine.

The earlier `scripts/check_reproducibility.py` checks two in-place builds instead. Its retained summary is valid evidence for that narrower procedure. No original result was overwritten to pretend it came from a clean workspace.

## Generated files

| Local path | Purpose |
|---|---|
| `data/processed/knowledge_graph.nq` | Source, schema, provenance, inference and validation named graphs |
| `data/processed/review.ttl` | Source union plus schema for review; graph separation is lost |
| `data/processed/asserted.ttl`, `inferred.ttl` | Separate source and reasoner views |
| `data/processed/provenance.ttl`, `mappings.ttl` | Record/statement lineage and mapping view |
| `reports/tables/` | Full query answers, schemas, reasoning examples, invalid-case summaries |
| `reports/credibility_audit/` | Separate audit summaries and detailed local comparisons |

Tracked [verification](../reports/credibility_audit/verification.json) and [clean-build](../reports/credibility_audit/clean_builds.json) summaries record the executed audit. Detailed evidence files are generated locally. The original generated report contains links to those local artifacts; their absence in a bare Git checkout is expected, not evidence that the computations ran there.
