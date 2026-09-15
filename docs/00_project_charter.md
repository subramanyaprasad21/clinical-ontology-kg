# Project charter — frozen core V1

**Provenance-Aware Semantic Integration of Type 2 Diabetes Knowledge Across Heterogeneous Biomedical Sources**

The engineering question is whether the supplied Mondo, HPO and Open Targets snapshots can support a small, defensible, reproducible T2DM knowledge graph with explicit mapping, provenance, validation and inference.

The implementation follows the supplied ChatGPT scope, which supersedes the initial scaffold. DrugCentral, LOINC, Reactome and other additional datasets are excluded. No biomedical data was downloaded during implementation. Raw files are immutable. All builds operate offline and fail on a changed raw input inventory or checksum.

The graph starts at Mondo `MONDO:0005148`, retains its complete **direct named-parent closure** (including upper ontology classes), links HPO annotations through source-asserted mappings, and includes Open Targets records that identify this same disease. This is a bounded semantic projection, not a replacement Mondo/HPO ontology, a comprehensive diabetes resource, or a patient record model.

The feasibility audit found that target and drug catalogs join to mechanism records, but no supplied structured relation connects them to T2DM. Those catalogs are audited and fingerprinted but are not imported into an unrelated or label-selected graph component. Three frozen questions therefore have unsupported results. No additional download is necessary to report that negative finding honestly.

Completion means executable extraction, a frozen manifest, a documented mapping policy and semantic model, source-separated RDF, statement provenance, real OWL RL inference, canonical and deliberately invalid SHACL cases, executable competency questions, repeated-build verification, tests, and documented limitations. It does not mean every clinical question has a positive answer or that missing acquisition history has been reconstructed.
