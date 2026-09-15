# Provenance-aware Type 2 diabetes knowledge graph

A completed, source-bounded semantic integration project using the supplied Mondo, HPO and Open Targets snapshots. It demonstrates OWL/HPOA/Parquet ingestion, verified identifier joins, SKOS mappings, record and statement provenance, OWL RL reasoning, SHACL validation, executable SPARQL questions and deterministic local builds.

**Start with [the final report](reports/FINAL_REPORT.md).** It explains the actual result and its limitations.

The graph contains 17 named hierarchy classes, five HPO terms (three positive phenotype annotations, one inheritance annotation and one onset annotation), ten source-asserted exact mappings, and one unresolved mapping. Every imported source quad has a recorded provenance chain. Canonical SHACL validation passes; six isolated invalid cases are detected.

**The supplied data does not contain structured T2DM–target associations or drug indications.** The mechanism-to-target and mechanism-to-drug catalog joins are verified, but three clinical competency questions remain unsupported. No unsupported drug/target edges were fabricated and no additional biomedical datasets were downloaded. Open Targets' release is user-declared; original download URLs/dates remain unknown. These limitations are part of the result.

## Reproduce

Use Python **3.12** with the supplied `data/raw/` tree and frozen manifest in `config/input_manifest.json`. The local environment is already installed in `.venv/`.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_reproducibility.py
```

On Windows, use `.venv\Scripts\python.exe` for the virtual-environment interpreter. Dependency installation requires package access; the audit and all builds use only local files. No OWL imports or biomedical endpoints are downloaded. `requirements.txt` pins the tested dependency versions; `reports/environment.json` records the executed environment.

The build verifies all 11 raw files before and after execution, runs the audit, constructs the graph, validates it, demonstrates invalid cases, executes OWL RL, evaluates all questions, reopens all RDF exports to check round-trip equality, and writes reports. A checksum/inventory mismatch is an error, never a silent refreeze. `scripts/freeze_inputs.py` created the supplied manifest and refuses to overwrite it; it is not part of routine reproduction.

To run the standalone audit or a saved question:

```bash
.venv/bin/python scripts/audit.py
.venv/bin/python scripts/query.py queries/competency/03_phenotype_evidence.rq
```

## Review the artifacts

| Artifact | Purpose |
|---|---|
| [Final report](reports/FINAL_REPORT.md) | Findings, coverage, negative results and evaluation |
| [Full dataset](data/processed/knowledge_graph.nq) | Authoritative N-Quads with source, schema, provenance, inference and validation graphs |
| [Protégé review file](data/processed/review.ttl) | Source fact union plus local ontology |
| [Asserted facts](data/processed/asserted.ttl) / [inferred facts](data/processed/inferred.ttl) | Separate materialized views; inference includes RDF/OWL bookkeeping |
| [Provenance](data/processed/provenance.ttl) | Statement → record → frozen source; build/reasoning activities |
| [Frozen input manifest](config/input_manifest.json) | Actual sizes, SHA-256, observed versions and explicit acquisition gaps |
| [Metrics](reports/metrics.json) / [query answers](reports/tables/competency_results.json) | Machine-readable evaluation |
| [Validation](reports/validation.txt) / [invalid cases](reports/tables/invalid_cases.json) | Passing canonical graph and six detected failure cases |
| [Tests](reports/tests.txt) / [repeatability](reports/reproducibility.json) | Executed verification evidence |

The `.ttl` views use sorted, fully expanded N-Triples-compatible Turtle for stable bytes. Source graph context lives in the N-Quads dataset; flattening into Turtle loses that separation. See [Protégé review instructions](docs/protege_review.md).

## Implementation and design

`src/clinical_kg/` contains the implemented pipeline: `inputs.py`, `audit.py`, `mapping.py`, `graph.py`, `reasoning.py`, `validation.py`, `pipeline.py`, and `reporting.py`. Entry points are in `scripts/`, ontology and SHACL files in `ontology/`, and executable queries in `queries/`. The earlier empty scaffold directories are not separate implementations.

Read the [charter](docs/00_project_charter.md), [verified join matrix](docs/01_data_feasibility_matrix.md), [mapping policy](docs/02_mapping_policy.md), [ontology design](docs/04_ontology_design_notes.md), [provenance model](docs/provenance_model.md), and [limitations](docs/limitations.md).

This is a local semantic engineering artifact, with a deliberately small T2DM graph. It does not claim clinical completeness, novel biomedical discoveries, full Mondo OWL consistency, independently corroborated phenotype evidence, or verified acquisition history. Raw data is excluded by `.gitignore`; local completion does not authorize public redistribution under unreviewed source terms.
