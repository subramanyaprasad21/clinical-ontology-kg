# Frozen competency questions and executable results

Every question has an executable `.rq` file in `queries/competency/`. The build writes complete results to `reports/tables/competency_results.json`; statuses and row counts also appear in the final report.

| # | Question | Scope/result |
|---|---|---|
| 01 | Where does T2DM sit in the disease hierarchy? | Named Mondo ancestors |
| 02 | Which phenotypes are associated with T2DM? | Positive aspect P only; original disease identifiers preserved |
| 03 | What evidence supports those associations? | File version, record locator, TAS code, OMIM reference and upstream HPO |
| 04 | Which targets are associated with T2DM? | Unsupported; missing association data |
| 05 | Which drugs are connected to T2DM? | Unsupported; missing structured indications |
| 06 | Is there a disease → target ← drug path? | Unsupported; missing clinical leg |
| 07 | What kinds of cross-resource mappings exist? | Explicit exact mappings plus unresolved NANDO xref |
| 08 | Which annotations occur across sources? | Five shared annotations; not independent evidence |
| 09 | Which facts are inferred? | Separate OWL RL graph; useful classification/inverse/hierarchy results |
| 10 | Can imported assertions be traced to source and version? | Full reified assertion/record/snapshot paths, including version basis |
| 11 | Which graph records violate constraints? | Canonical SHACL result graph; zero rows means no detected violations |

The sixth invalid-data demonstration and all other synthetic mutations are reported separately in `reports/tables/invalid_cases.json`, not mixed into canonical query results. `queries/analysis/missing_provenance.rq` provides an additional record-chain check. The Python dataset-aware check also detects source quads lacking any reified provenance assertion, which a query over only statement records would miss.

The [credibility audit](../reports/CREDIBILITY_AUDIT.md) qualifies the original machine statuses: four questions are answered within scope, four are partially answered and three remain unsupported. The saved query rows are unchanged; the distinction concerns what the results establish scientifically.
