# Drug/target extension: preliminary feasibility

The documentation-only assessment below is superseded for row coverage by the [captured-data assessment](EXTENSION_CAPTURE.md). The core graph remains unchanged.

Documentation checked on 2026-10-02. No extension records have been imported, and the frozen input manifest is unchanged. The three drug/target competency questions remain unsupported by the current graph.

## Candidate source

Open Targets documents target–disease associations and distinguishes direct associations from indirect associations that include ontology-descendant evidence. The extension must preserve that distinction and must not interpret an association score as proof of causation. [Association documentation](https://platform-docs.opentargets.org/associations).

The GraphQL disease interface exposes associated targets and known drugs; its drug interface includes indications and mechanisms. This provides a candidate retrieval route, not evidence that a complete T2DM extract has been obtained. [API documentation](https://platform-docs.opentargets.org/data-access/graphql-api).

Release archives provide partitioned Parquet datasets. A release-pinned extract is preferable for replay; a live API capture would require its schema, query, variables, pagination, retrieval time and response bytes to be preserved. [Download documentation](https://platform-docs.opentargets.org/data-access/datasets).

The Platform documents CC0 1.0 for its data and requests citation. Direct acquisition from upstream sources requires checking those sources' own terms rather than assuming the same licence. [Licence documentation](https://platform-docs.opentargets.org/licence).

## Required checks before implementation

1. Select and verify a release. The existing `26.06` designation is not authenticated by the local Parquet metadata; do not use it as proof of release compatibility.
2. Resolve the exact T2DM identifier against that release, retaining any mapping evidence.
3. Extract bounded target-association and drug-indication records with all pages/partitions accounted for. Record raw hashes and acquisition metadata separately from the frozen core.
4. Inspect identifiers, source evidence, direct/indirect status, clinical phase and indication-specific approval fields. Missing fields remain unknown; drug-level approval cannot establish approval for T2DM.
5. Reconcile mechanisms and catalog identifiers within the selected release. A drug–target mechanism plus a disease association does not by itself establish treatment efficacy or an approved indication.

The candidate is documentation-feasible. T2DM row coverage, release consistency, complete retrieval and query results are not yet verified. The next executable step is a small, separately stored source capture and schema audit, before extending OWL vocabulary or changing competency-query status.
