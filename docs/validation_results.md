# Validation results and interpretation

The build validates the canonical source facts, schema and provenance **before** reasoning, with SHACL inference disabled. This prevents a reasoner's inferred types from masking missing imported endpoint types. The validation report is exported as Turtle/text and as a named graph queried by competency question 11.

The canonical graph conforms with no SHACL violations. The separate dataset-aware provenance check finds a complete record/file/version/activity chain for every source quad and rejects reified statements pointing at nonexistent graph facts. Six individually mutated graph copies fail as expected: missing label, missing identifier, missing assertion source, missing source version, literal phenotype target, and forbidden mapping predicate. The canonical dataset is never mutated by these cases.

The recorded results are in `reports/validation.txt`, `reports/validation.ttl`, `reports/tables/invalid_cases.json` and `reports/metrics.json`. The current regression suite has 31 passing tests; the separate fidelity audit has 35 passing checks. Two clean-output workspaces reproduce 20 artifacts byte-for-byte with different Python hash seeds. They share installed dependencies and frozen raw inputs, so this does not establish fresh-environment reproduction.

Generic `hasHPOAnnotation` endpoints must be IRIs typed as `HPOTerm`, with a disease-concept subject. Positive/excluded pairs are reported separately in `reports/tables/phenotype_conflicts.json`; they do not create SHACL violations or discard evidence. Tests cover same-source and cross-source pairs. The canonical selection contains no such pair.

Every exported RDF view is reparsed. Graph isomorphism handles anonymous OWL nodes; dataset quads are compared exactly. Raw file hashes are checked again after the build. RDFLib emits three N-Quads deprecation warnings in the current test run.

The installed OWL API reports zero DL profile violations in `reasoning.ttl`; the full `review.ttl` retains three. HermiT checks consistency and two selected entailments, plus their loss after premise removal. These are bounded formal checks, not clinical validation or full-source ontology consistency.

The [baseline audit](../reports/CREDIBILITY_AUDIT.md) preserves the earlier validation gaps. Current results supersede those gaps without rewriting that historical record.
