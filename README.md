# T2DM knowledge graph with provenance

A bounded RDF/OWL integration of Mondo, the Human Phenotype Ontology (HPO) and Open Targets around type 2 diabetes mellitus (T2DM).

The repository has two parts. The frozen core keeps the original hierarchy, phenotype annotations, mappings, provenance, SHACL checks, OWL reasoning and competency queries. A separate Open Targets 26.09 extension adds indication, drug-target mechanism, clinical-target and report records without rewriting the core.

## Scope

The graph records disease-level source annotations. It does not treat an HPO annotation as something every patient with T2DM must have. Positive and excluded annotations keep separate evidence. SKOS mappings preserve source mapping claims and are not identity assertions.

The core uses eleven frozen files: Mondo/HPO `2026-09-01`, HPOA `2026-09-02`, and declared Open Targets `26.06`. The historical acquisition URLs and dates for the core are unavailable. The 26.09 extension has separate capture receipts with archive URLs, retrieval times, sizes and hashes.

## Results

| Measure | Frozen core | Open Targets 26.09 extension |
|---|---|---|
| Source content | 38 records; 160 unique asserted triples; 174 source quads | 613 indications, 434 mechanisms, 798 clinical-target records, 1 disease record, 37,040 reports |
| Clinical joins | Drug/target questions 04-06 unsupported in the frozen core | 798 supported paths; 372 participating drugs; 333 targets; 613 indication drugs |
| Report resolution | Original provenance retained | 186,676 references resolved; 0 unresolved |
| Graph size | Original outputs unchanged | 1,077,529 triples/quads; 39,696 subject resources |
| Validation | 35 separate audit checks; SHACL conforms | All 38,886 imported payloads checked against raw rows; SHACL conforms |

The regression suite has 46 passing tests: 31 core tests and 15 extension tests. Two clean core builds reproduce 20 artifacts byte-for-byte. The final verification also reproduces those 20 core artifacts and the three final extension artifacts in a fresh virtual environment on the same host.

The OWL reasoning projection has zero OWL 2 DL profile violations under OWL API 4.5.29. HermiT 1.4.3.456 verifies selected classification and inverse entailments, including premise-removal controls. The full review export retains three documented provenance-related profile violations.

## Clinical extension

A supported clinical path needs all three source records for the same disease/drug/target context:

1. an exact T2DM indication for the drug;
2. a drug-target mechanism containing that drug and target;
3. a clinical-target record containing the same drug, target and T2DM identifier.

This rule produces 798 paths. It does not create a general disease-target association and does not establish efficacy or regulatory approval.

Of the 186,676 resolved report references, 137,473 references from multi-disease clinical-target records do not contain T2DM. They stay attached as provenance for the source record rather than being treated as T2DM-specific evidence. QC flags and missing stage fields are preserved rather than filtered away.

See [the extension notes](docs/CLINICAL_EXTENSION.md) and [evaluation](docs/EVALUATION.md) for the full scope.

## Reproduce

Python 3.12 and the pinned [requirements](requirements.txt) are used. The raw datasets are not stored in Git, so a clone also needs the exact files listed in the [core manifest](config/input_manifest.json) and the extension capture receipts.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python audit/extension/final_build.py
.venv/bin/python audit/extension/verify_final.py
.venv/bin/python -m pytest -q tests audit/extension/test_build.py audit/extension/test_reports.py
```

The full same-host verification procedure is in [docs/REPRODUCING.md](docs/REPRODUCING.md).

## Repository layout

- `src/clinical_kg/`: core build, validation, reasoning and reporting code
- `ontology/`: local OWL vocabulary and SHACL shapes
- `queries/competency/`: frozen competency queries
- `audit/extension/`: 26.09 extension build and verification code
- `reports/final/`: final verification summaries and protected-file baseline
- `docs/`: model, provenance, evaluation, limitations and reproduction notes

The [documentation map](docs/README.md) separates current documentation from hash-bound historical records. Machine-readable evidence that is directly viewable in Git is concentrated under [`reports/final/`](reports/final/). Some historical core reports link to `data/processed/` and `reports/tables/`; those are reproducible build outputs intentionally excluded from Git rather than missing committed evidence.
