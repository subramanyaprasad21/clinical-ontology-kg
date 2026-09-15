# Validation results and interpretation

The build validates the canonical source facts, schema and provenance **before** reasoning, with SHACL inference disabled. This prevents a reasoner's inferred types from masking missing imported endpoint types. The validation report is exported as Turtle/text and as a named graph queried by competency question 11.

The canonical graph conforms with no SHACL violations. The separate dataset-aware provenance check finds a complete record/file/version/activity chain for every source quad and rejects reified statements pointing at nonexistent graph facts. Six individually mutated graph copies fail as expected: missing label, missing identifier, missing assertion source, missing source version, literal phenotype target, and forbidden mapping predicate. The canonical dataset is never mutated by these cases.

`reports/validation.txt`, `reports/validation.ttl`, `reports/tables/invalid_cases.json` and `reports/metrics.json` contain the executed results. `reports/tests.txt` and `reports/tests.xml` record the final automated test run. `reports/reproducibility.json` records two complete, byte-identical local builds. A build also reparses all exported RDF and compares every triple/quad with the in-memory result; raw file hashes are checked again after completion.

SHACL checks the specified structural expectations. It is not an exhaustive clinical constraint system or proof of whole-ontology logical consistency. OWL RL runs over a documented local projection; source OWL restrictions and disjointness outside that projection are not validated. RDFLib emits upstream deprecation warnings from its N-Quads reader; these do not alter the parsed quads and are visible in test logs.

The subsequent [credibility audit](../reports/CREDIBILITY_AUDIT.md) independently checked raw-record fidelity and clean-output reproduction. It also found two SHACL coverage limits: generic HPO annotation endpoints and simultaneous positive/excluded annotations can escape the current shapes. Neither occurs in the canonical selection. The audit records those probes without changing the production ontology or shapes.
