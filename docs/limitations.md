# Limitations

The frozen core and the Open Targets 26.09 extension answer different questions. The points below apply to the current repository state.

- The frozen core does not contain T2DM drug-target edges. The 26.09 extension contains 613 indications and 798 record-supported clinical paths across 333 targets, but it still does not provide a general disease-target association dataset. A supported path is a source-record join, not evidence of efficacy, causality or treatment suitability.

- Phenotype coverage is small: three positive phenotype terms, one inheritance annotation and one onset annotation are directly linked. This is enough for the bounded integration and reasoning checks, not for clinical coverage.

- Open Targets phenotype evidence shares HPO lineage with the HPO source material and contains duplicate evidence entries. Agreement across those files is therefore not independent corroboration.

- The historical core has incomplete acquisition history. Its raw hashes identify the supplied files, but the original download URLs and dates are unavailable. The Open Targets `26.06` label is a declared version rather than a release independently authenticated from preserved receipts. The 26.09 extension has separate receipts; those do not repair the earlier history.

- HPOA reports `2026-09-02` while the HPO ontology is `2026-09-01`. Both dates are kept as supplied.

- Reasoning uses a bounded projection. Direct named disease hierarchy axioms are imported; the project does not execute every upstream Mondo restriction, disjointness axiom or remote import. The reasoning projection passes the installed OWL 2 DL profile check and selected HermiT tests. The full review export still has three documented profile violations.

- Ten exact mappings are preserved from Mondo. They are source claims and have not been independently adjudicated against every external terminology. One NANDO xref remains unresolved.

- Reproduction has been shown on the same host. Two clean core builds reproduce 20 artifacts, and a fresh virtual environment reproduces those 20 core artifacts plus three final extension artifacts byte-for-byte. Cross-platform reproduction and raw-data reacquisition have not been demonstrated.

- Raw datasets, detailed payloads and large RDF outputs remain local. A Git clone is not sufficient to rebuild the project without the exact input files.

- The formal and GUI checks cover selected model behaviour. They do not establish correctness of every modelling choice or clinical truth.

- All 186,676 report references resolve, but 137,473 references from multi-disease clinical-target records do not contain T2DM. They remain attached as provenance and are not treated as T2DM-specific report evidence.

- QC and stage values remain source metadata. Among imported reports, 8,353 have QC flags, 28,687 have null QC fields and 6,797 are missing `phaseFromSource`. The graph retains these states rather than silently filtering them. Seventy indication records carry the source value `APPROVAL`; this is not an independently verified regulatory determination.
