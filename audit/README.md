# Audit checks

These checks evaluate the existing graph without changing the production ontology, raw files or canonical outputs. Run them from the repository root using the pinned environment and the local frozen inputs:

```sh
.venv/bin/python audit/verify.py
.venv/bin/python audit/clean_builds.py
```

`verify.py` compares raw OWL/HPOA/Parquet records with graph facts, checks provenance chains, recomputes the OWL RL closure, removes positive premises to test their effect, runs SHACL mutations, and reruns all competency queries. It does not import the production extraction or build helpers. It uses the same RDF/OWL libraries, so this is a separate verification implementation, not an independent reasoner or external review.

`clean_builds.py` runs the production pipeline and its 31 tests in two temporary workspaces with no derived outputs. Raw files are hard-linked to avoid duplicate storage, opened read-only by the pipeline, and hash-checked. Different Python hash seeds test iteration-order dependence. The same installed interpreter and dependencies are used for both runs.

The tracked summaries are `reports/credibility_audit/verification.json` and `clean_builds.json`. Full record comparisons, query results, inference chains, SHACL focus nodes and logs are generated locally in that directory and excluded from Git. Coverage probes are reported separately from the 35 passing integrity checks: the generic endpoint now has a shape; positive/excluded pairs are handled by a separate provenance-preserving report rather than a hard SHACL violation.

The production repeatability script still performs two in-place builds. This separate audit establishes clean-output repeatability without rewriting the original verification record. Neither workflow reacquires raw files or proves cross-platform reproduction.

The OWL library check and configurable installation paths are documented in [reproduction instructions](../docs/REPRODUCING.md).

`fresh_environment.py` additionally installs pinned dependencies in a new virtual environment with pip's cache disabled, checks dependency consistency, and runs a clean build, tests and the separate audit. All 20 artifact hashes match the recorded outputs on the same host. See `reports/fresh_environment/result.json`.
