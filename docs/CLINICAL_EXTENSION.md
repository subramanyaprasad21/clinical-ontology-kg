# Open Targets 26.09 clinical extension

The clinical extension is a separate dataset built beside the frozen core. It uses five Open Targets 26.09 tables: `disease`, `clinical_indication`, `clinical_target`, `drug_mechanism_of_action` and `clinical_report`.

The capture receipts record the archive URLs, retrieval times, file sizes and SHA-256 values. The historical core remains declared Open Targets 26.06 and is not rewritten by the extension.

## Join rule

A clinical path is created only when the same disease/drug/target context is supported by:

1. an exact T2DM indication for the drug;
2. a mechanism record containing that drug and target;
3. a clinical-target record containing the same drug, target and exact T2DM identifier.

Each path keeps links to the source records that support it. Missing support stops the build for that path. No general disease-target association predicate is introduced.

Stages remain on the records where Open Targets supplied them. A drug stage, report stage or multi-disease clinical-target stage is not promoted to a T2DM approval claim. Seventy indication records contain the source value `APPROVAL`; the project does not independently adjudicate those values.

## Records and provenance

The extension uses four named graphs for source records, reports, provenance and clinical context. Every imported record keeps its row locator, source snapshot hash, release, archive URL, provider and build activity. Full row payloads are retained as RDF JSON.

Report references resolve by exact report ID. Missing or ambiguous IDs remain unresolved. Resolution proves that the referenced source record was found; it does not prove clinical relevance or efficacy.

| Reference set | Resolved | Unresolved |
|---|---:|---:|
| T2DM indication records | 6,201 | 0 |
| Clinical-target records | 180,475 | 0 |
| Total references | 186,676 | 0 |
| Unique report IDs | 37,040 | 0 |

All 289,954 rows in the captured report table were scanned and report IDs were unique.

Of the 180,475 clinical-target references, 43,002 contain both the drug and T2DM identifiers. The other 137,473 contain the drug but not T2DM. Those references remain provenance for a multi-disease source record and are not counted as T2DM-specific report evidence.

QC flags occur on 847 indication references and 39,075 clinical-target references. Among the 37,040 imported reports, 8,353 have QC flags and 28,687 have a null QC field. `phaseFromSource` is missing on 6,797 reports. These states are preserved in the graph.

## Final counts

| Measure | Count |
|---|---:|
| T2DM indication records / unique indication drugs | 613 / 613 |
| Drug-target mechanism records | 434 |
| Clinical-target records / supported paths | 798 / 798 |
| Unique targets / drugs participating in paths | 333 / 372 |
| Disease records | 1 |
| Imported report records | 37,040 |
| All imported source records | 38,886 |
| Path-to-source support links | 2,401 |
| Record graph triples | 382,275 |
| Report graph triples | 494,349 |
| Provenance graph triples | 194,514 |
| Clinical-context graph triples | 6,391 |
| Unique triples / quads | 1,077,529 / 1,077,529 |
| Distinct subject resources | 39,696 |
| Distinct IRIs in triple positions | 40,697 |

Repeated references are not treated as independent studies.

## Queries and verification

The frozen competency queries 04, 05 and 06 still return zero rows against the extension because they use the core vocabulary. The record-aware extension queries return 333 targets, 613 indications and 798 supported paths.

Question 05 is answered within the source-indication scope. Questions 04 and 06 have a narrower clinical-context answer; the general disease-target association question remains unsupported.

The independent verifier checks all 38,886 imported payloads against raw rows, all report links, stages, QC fields, 798 joins and 2,401 support links. It also reparses the serialized dataset and checks the graph counts. The extension SHACL report conforms, but no extension OWL entailment result or clinical-validity claim is made.

The final same-host verification passes all 46 tests and reproduces the final extension graph, query results, SHACL report and summary byte-for-byte under hash seed `707`. See [REPRODUCING.md](REPRODUCING.md) for the commands.
