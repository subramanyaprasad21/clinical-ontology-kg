# Open Targets 26.09 clinical capture

This records the source-capture stage. The [clinical extension](CLINICAL_EXTENSION.md) describes the subsequent RDF export; counts and source limitations below are retained.

Four complete table listings were captured from the official release archive: disease, clinical indication, clinical target and drug mechanism of action. Each listing contained one Parquet partition. All eight captured files (four listings and four partitions) match their recorded sizes and SHA-256 hashes. URLs, response headers and retrieval timestamps are in [the capture manifest](../reports/extension/capture_manifest.json).

## Observations

| Selection or check | Result |
|---|---:|
| Exact disease identifier `MONDO_0005148` | One record, type 2 diabetes mellitus |
| Exact-T2DM indication records / distinct drugs | 613 / 613 |
| Indications with source stage `APPROVAL` | 70 |
| Clinical-target records containing exact T2DM identifier | 798 |
| Distinct drug–target pairs | 798 |
| Drugs / targets in those pairs | 372 / 333 |
| Pairs matched to both T2DM indication and mechanism | 798 |
| Pairs lacking either match | 0 |

The selected records retain source payloads, filenames and zero-based row positions in the local capture directory. The [summary](../reports/extension/summary.json) includes the full indication-stage distribution. Stages include investigational and unknown values; the 613 drugs are not described as approved T2DM treatments.

The `clinical_target` rows contain multiple disease contexts. Their aggregate `maxClinicalStage` is not assigned to T2DM. Disease-specific stage is taken only from the exact-T2DM indication row. `clinicalReportIds` remain references: the report bodies have not been captured, so publication-level or jurisdiction-specific approval verification is not claimed.

The recorded joins support a bounded drug-indication/mechanism extension. They do not establish general genetic target associations, causal relevance, treatment efficacy or independent corroboration. Clinical-target tables and mechanisms may share upstream evidence.

## Comparison with the dementia capture

The dementia project's `ot2606-context-001.capture.json` records edition `26.06`. None of the four new Parquet hashes appears among its complete-file hashes. [Comparison evidence](../reports/extension/reuse_comparison.json) records the manifest hash. This is a manifest comparison; external raw files were not independently rehashed. The snapshots are not treated as interchangeable and no cross-release label enrichment was performed.

## Replay and boundaries

```sh
.venv/bin/python audit/extension/inspect_capture.py
```

This verifies capture hashes and partition coverage before inspecting the exact-anchor rows and joins. The original acquisition command is `.venv/bin/python audit/extension/capture.py`; it requires network access and refuses to overwrite a completed capture. Existing captured bytes, not a later download from the same URL, define this observation.

Raw Parquet files and selected payloads remain outside Git under `data/extensions/opentargets-26.09/`. The original eleven-file manifest, core ontology, core query results and generated RDF are unchanged. The three core drug/target questions remain unsupported in the core dataset. No extension RDF has been integrated.

The next implementation boundary is a separate clinical-record graph: retain indication stage and record provenance, join mechanisms explicitly, and distinguish clinical-context target links from general disease–target association evidence. Clinical report bodies and same-release catalogs remain additional data requirements if detailed evidence or labels are needed.
