# Project charter: frozen core V1

This phase asks whether the supplied Mondo, HPO and Open Targets snapshots can be integrated into a small T2DM knowledge graph with explicit mapping, provenance, validation and inference.

The scope is limited to the supplied files. DrugCentral, LOINC, Reactome and other additional datasets are excluded. No biomedical data was downloaded during the core implementation. Raw inputs are treated as immutable, and builds fail when the recorded inventory or checksum changes.

The graph is anchored at Mondo `MONDO:0005148`. It keeps the complete direct named-parent closure, including upper-ontology classes, links HPO annotations through source mappings, and includes Open Targets records that identify the same disease. This is a bounded projection rather than a replacement Mondo/HPO ontology, a comprehensive diabetes resource or a patient-record model.

The feasibility audit found that the supplied target and drug catalogs join to mechanism records, but no structured relation in the frozen source set connects those records to T2DM. The catalogs are therefore audited and fingerprinted without being added to the graph through labels or unsupported joins. Three frozen competency questions remain unsupported for that reason.

Core completion requires executable extraction, a frozen input manifest, documented mapping and semantic rules, source-separated RDF, statement provenance, OWL RL inference, SHACL checks with invalid controls, executable competency queries, repeatability checks, tests and documented limitations. Missing clinical relations remain negative findings; missing historical acquisition records are not reconstructed.
