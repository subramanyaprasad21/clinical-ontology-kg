# Integrating Type 2 diabetes knowledge with provenance

Biomedical resources can use different identifiers for related concepts and repeat the same underlying evidence. Combining their records without checking those distinctions can produce a graph that looks connected but makes stronger claims than its sources support.

This project tests a bounded integration around Type 2 diabetes mellitus (T2DM), the disease case selected in the research brief. It connects the supplied Mondo, Human Phenotype Ontology (HPO) and Open Targets snapshots, preserving source identities, mapping decisions and annotation evidence. It is a semantic engineering case study, not a comprehensive diabetes knowledge base.

## Findings

- **The disease–phenotype integration works.** Mondo `MONDO:0005148` maps explicitly to HPOA's `OMIM:125853`; Open Targets preserves the same Mondo IRI. The graph contains 17 named hierarchy classes, five HPO terms and ten source-asserted exact mappings. Three terms are phenotype annotations; inheritance and onset are represented separately. One NANDO xref remains unresolved.
- **Cross-source agreement is not independent corroboration.** The Open Targets annotations reproduce HPO-derived evidence and contain duplicate evidence entries. These are retained for traceability, not counted as additional studies.
- **The supplied files cannot answer the clinical drug/target questions.** Every mechanism-to-catalog identifier resolves, but the data lacks structured T2DM–target associations and drug indications. Those three competency questions remain unsupported.

Mondo and HPO ontology headers identify 2026-09-01; HPOA identifies 2026-09-02. Open Targets 26.06 is user-declared, not independently authenticated by the Parquet metadata. Original download URLs and dates are unavailable.

## What the model demonstrates

RDF stores facts in named source graphs. RDFS retains the named disease hierarchy. SKOS expresses the source mapping claims; similar labels do not create identity links. Reified statements and PROV-O connect each imported assertion to its source record, frozen file and build activity.

The local OWL definition classifies terminology concepts that have positive phenotype annotations. The reasoner also derives inverse phenotype relations and transitive ancestors. These are real but elementary inferences, not diagnostic or treatment discoveries. SHACL checks selected entity, relationship, mapping and provenance requirements; six deliberately invalid copies fail as expected. Generic annotation endpoints are now checked, and a separate evidence report flags exact-IRI positive/excluded pairs for human review.

The eleven SPARQL questions execute. The credibility audit interprets four as answered within scope, four as partially answered and three as unsupported. It explains the difference from the original pipeline's simpler status labels.

## Verification and reproduction

The 31 tests pass. A separate audit checks 38 source records and all 179 assertion occurrences, covering every one of the 174 source quads. Two workspaces starting without derived outputs reproduce 20 artifacts byte-for-byte. They use the same pinned Python environment and local frozen inputs; a Git clone alone cannot reacquire those files.

See [reproduction instructions](docs/REPRODUCING.md). With the required environment and raw files in place:

```sh
.venv/bin/python scripts/build.py
.venv/bin/python -m pytest -q
.venv/bin/python audit/verify.py
.venv/bin/python audit/clean_builds.py
```

## Review the work

Start with the [credibility audit](reports/CREDIBILITY_AUDIT.md) for methods, join keys, results and qualifications. The [generated build report](reports/FINAL_REPORT.md) retains the original results; its local artifact links require a build. Inspect the [ontology](ontology/core/core.ttl), [shapes](ontology/shapes/shapes.ttl), [implementation](src/clinical_kg/) and [queries](queries/competency/) for technical detail.

The [design decisions](docs/DESIGN_DECISIONS.md), [supervisor questions](docs/SUPERVISOR_DEFENCE_GUIDE.md) and [Protégé guide](docs/PROTEGE_REVIEW_GUIDE.md) support an author-led review. The installed Protégé OWL API/HermiT libraries verify the repaired review export’s consistency, existential classification and inverse relation. The separate `reasoning.ttl` projection has zero profile violations in the installed checker; the full review retains three provenance-related violations. See the [projection review](reports/OWL_PROJECTION_REVIEW.md) for its explicit boundary and pending design decision. Full OWL DL compatibility, clinical completeness and independent environment reproduction are not established.

## Development

This is researcher-directed, AI-assisted work. The researcher supplied the scope, source choices and validation requirements. AI assistance supported coding, debugging and documentation, including drafting the implemented OWL vocabulary. Specific modelling choices are recorded for author review; that semantic sign-off is still pending.
