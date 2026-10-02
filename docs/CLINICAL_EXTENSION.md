# Clinical indication and mechanism extension

The Open Targets 26.09 capture now has a separate RDF export and three executable queries. The original frozen core and its eleven competency-query results are unchanged. General target-association evidence remains outside this extension.

## Representation

The namespace is `https://example.org/clinical-kg/extension/`. Its classes describe source records and derived joins, not patients or clinical guarantees.

| Resource | Meaning |
|---|---|
| `DiseaseRecord` | Exact disease record for `MONDO_0005148` |
| `IndicationRecord` | Source drug–disease record; `indicationStage` preserves its `maxClinicalStage` value |
| `ClinicalTargetRecord` | Source drug–target record whose disease contexts include T2DM; `aggregateStage` remains scoped to this multi-disease record |
| `MechanismRecord` | Mechanism description, action type, drug identifiers and target identifiers |
| `ClinicalContextLink` | A T2DM/drug/target tuple supported by an exact indication, a clinical-target record and a matching mechanism |

Three named graphs separate records, provenance and derived clinical context. Every selected record has a snapshot hash, zero-based file row, original JSON payload and build activity. Every derived path links to all supporting indication, mechanism and clinical-target records. Report identifiers are preserved as source references; their bodies have not been retrieved. References on a multi-disease record are not independently attributed to T2DM.

Missing indication stages stay absent. Aggregate clinical-target approval cannot substitute for an indication-specific stage. The builder rejects a clinical-target path lacking either an exact-T2DM indication or a matching mechanism. It does not copy labels from another release or assert treatment efficacy, regulatory endorsement, causality, or general disease–target association.

## Results

| Measure | Result |
|---|---:|
| Selected source records | 1,846 |
| Indication query rows | 613 |
| Clinical-path query rows | 798 |
| Path-to-source-record query rows | 2,401 |
| Source-record graph triples | 195,599 |
| Provenance graph triples | 9,288 |
| Clinical-context graph triples | 6,391 |

Source-record triple count includes report identifier references; it is not a count of independent studies. The indication table includes investigational and unknown stages. Seventy source indication rows carry `APPROVAL`; this is preserved source metadata, not an independent regulatory assessment.

The [separate verifier](../audit/extension/verify_graph.py) rereads captured Parquet and checks every selected payload, all indication/stage results, path pairs, supporting record types and provenance-query coverage. It shares RDFLib and PyArrow with the builder. The [verification report](../reports/extension/graph_verification.json) records the executed counts. The RDF dataset round trip preserves all quads. Two in-place builds, with the second using `PYTHONHASHSEED=404`, produce identical graph/query bytes and summaries; see [repeatability evidence](../reports/extension/repeatability.json). This does not establish fresh-environment reproduction of the extension.

The combined test run passes 38 tests: 31 core tests and seven extension tests. Extension cases cover missing support, exact disease filtering, null disease contexts, stage isolation, identifier rejection, deterministic identifiers and input preservation. These are software checks, not clinical validation. No extension OWL reasoning or SHACL conformity result is claimed.

## Offline replay

With the captured files available:

```sh
.venv/bin/python audit/extension/build.py
.venv/bin/python audit/extension/verify_graph.py
.venv/bin/python -m pytest -q tests audit/extension/test_build.py
```

The committed capture manifest is the file-identity authority. The builder checks all capture hashes and partition listings before and after processing; it does not trust the previously selected-record JSON. Generated outputs are `data/extensions/opentargets-26.09/derived/clinical_context.nq` and `query_results.json`. [Graph summary](../reports/extension/graph_summary.json) records their hashes and the implementation fingerprint. Raw files and large generated outputs remain local.

Queries are in [audit/extension/queries](../audit/extension/queries/): indications, clinical paths and path evidence. They answer clinical-context questions in the extension; they do not silently change the meaning or status of the original core queries.

## Remaining scope

Clinical report bodies, complete general target-association evidence and same-release drug/target catalog enrichment are not captured. The existing clinical paths require no invented labels or inferred approval. Extending beyond them requires an additional source capture and evidence-specific interpretation.
