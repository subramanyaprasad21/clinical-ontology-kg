# T2DM knowledge integration with provenance

This repository implements a bounded transformation of Mondo, Human Phenotype Ontology (HPO) and Open Targets snapshots into a source-separated RDF knowledge graph. It preserves disease identifiers, source annotations, mapping claims and statement provenance. The data supports disease–phenotype integration; it does not support the three T2DM drug/target queries.

## Implementation and workflow

Frozen files → source audit → named source graphs and provenance → SHACL validation → OWL RL inference → SPARQL results and deterministic exports.

The ontology distinguishes phenotype, inheritance, onset and excluded-phenotype annotations. Positive/excluded pairs retain both provenance chains and are flagged for evidence review. Disease-level annotations do not imply universal manifestation in patients. SKOS mappings align source identifiers without asserting identity.

`knowledge_graph.nq` retains graph context. `review.ttl` combines source facts and schema. `reasoning.ttl` preserves every asserted source triple while excluding 13 provenance-schema triples listed in an export manifest. Separate files contain asserted facts, inferred statements and provenance.

## Data scope

Eleven frozen files yield 17 named hierarchy classes, five HPO terms, three positive phenotype terms and ten explicit exact mappings. One NANDO xref remains unresolved. Mondo and HPO identify `2026-09-01`; HPOA identifies `2026-09-02`. Open Targets `26.06` is declared metadata, not independently authenticated. Original acquisition URLs and dates are unavailable.

## Results

- 160 unique asserted triples; 174 source quads; 179 assertion occurrences from 38 records.
- 31/31 tests and 35/35 separate audit checks pass.
- Two clean-output builds reproduce 20 artifacts byte-for-byte. A new virtual environment with freshly installed pinned packages also reproduces all 20 artifacts and passes the tests and separate audit on the same host.
- Eleven competency queries execute; the evidence assessment identifies four answered within scope, four partially answered and three unsupported.
- The installed OWL API 4.5.29 detects zero OWL 2 DL profile violations in `reasoning.ttl`. HermiT 1.4.3.456 derives the selected classification and inverse; removing positive premises removes those entailments.

## Limitations

The full review export retains three provenance-related OWL profile violations. The reasoning projection does not validate the complete upstream ontologies. Source agreement is not independent corroboration: Open Targets repeats HPO-derived evidence. Neither SHACL conformity nor an inferred graph connection establishes clinical truth. Raw acquisition and cross-platform reproduction have not been demonstrated. Selected [Protégé GUI checks](docs/PROTEGE_OBSERVATIONS.md) confirm the classification and inverse relations; they do not constitute an exhaustive axiom review.

## Reproduction

Use Python 3.12 and the pinned [requirements](requirements.txt), with the exact local files listed in [the input manifest](config/input_manifest.json). A clone alone does not supply those files.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m pytest -q
.venv/bin/python audit/verify.py
.venv/bin/python audit/clean_builds.py
```

See [reproduction instructions](docs/REPRODUCING.md) for the offline OWL library check and platform limits.

## Repository map

[Evaluation](docs/EVALUATION.md), [current model](docs/04_ontology_design_notes.md), [validation results](docs/validation_results.md), [documentation map](docs/README.md), [source code](src/clinical_kg/), [ontology](ontology/core/core.ttl), [SHACL shapes](ontology/shapes/shapes.ttl), [queries](queries/competency/) and [attribution](ATTRIBUTION.md).
