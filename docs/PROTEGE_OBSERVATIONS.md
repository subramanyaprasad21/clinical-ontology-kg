# Protégé GUI observations — 2026-10-02

The selected classification and inverse-relation checks were observed in `data/processed/reasoning.ttl`. The window metadata identified HermiT 1.4.3.456 as active and synchronized, with Show Inferences enabled.

| View | Observation |
|---|---|
| PhenotypeAnnotatedConcept, asserted individuals | Empty direct-instance list |
| PhenotypeAnnotatedConcept, inferred individuals | Two instances labelled “Diabetes mellitus, noninsulin-dependent” and “type 2 diabetes mellitus” |
| Mondo T2DM individual | Header identifies `MONDO:0005148`; `DiseaseConcept` is displayed as asserted and `PhenotypeAnnotatedConcept` as inferred |
| Mondo T2DM properties | Three `hasPhenotype` links; inheritance and onset use separate predicates |
| Insulin resistance individual | Identifier `HP:0000855`; two highlighted inferred `phenotypeOf` links to the displayed disease concepts |

Evidence was inspected in supplied application screenshots. Capture timestamps include `2026-10-01T19-19-50.078Z` (inferred instances), `2026-10-01T19-20-30.513Z` (Mondo individual) and `2026-10-01T19-24-47.116Z` (inverse relations). These correspond to 2026-10-02 in Asia/Kolkata. Image files are not archived in this repository; this is a transcription of the observed views, not a hash-bound screenshot archive.

The observations agree with the separately recorded OWL library checks. They verify the selected GUI entailments, not every axiom, clinical correctness, full-source consistency or independent ontology authorship. The equivalent-class editor and every item in the broader inspection guide were not separately documented. No ontology changes are required by these observations.
