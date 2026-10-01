# Separate OWL reasoning projection — 2026-10-01

A new `data/processed/reasoning.ttl` export separates terminology reasoning from RDF provenance schema. This is a technical proposal pending author acceptance of the export boundary. The accepted annotation interpretation and evidence-conflict policy are unchanged.

The full `review.ttl`, canonical dataset and provenance output remain available. The new export preserves all 160 asserted source triples, anonymous restrictions, terminology declarations and disease hierarchy. It excludes exactly 13 schema triples defining provenance classes and their superclass declarations. Their complete RDF statements are listed in generated `reports/tables/reasoning_export.json`. Recombining those exclusions with the projection reconstructs the full review graph up to blank-node identity; a regression test enforces this boundary.

The builder fails if source assertions use excluded vocabulary or the projected graph retains references to it. This is an explicit, bounded projection, not a general OWL module extractor or a silent alteration of the full ontology.

## Verification

The installed OWL API 4.5.29 reports zero OWL 2 DL profile violations for this projection. HermiT 1.4.3.456 reports consistency and derives the selected Mondo concept classification and inverse relation. Removing all six positive phenotype assertions from an in-memory copy removes both selected entailments. The exported file is not changed by that negative control.

The full review still reports three provenance-related profile violations. A successful check of the projection does not certify the full RDF dataset, clinical truth, every possible entailment, or the original upstream ontologies. This test runs Protégé's installed libraries; no human GUI walkthrough is claimed.

Run the commands in [the earlier follow-up](EXPORT_VALIDATION_FOLLOWUP.md) to rebuild and check all three documents. The checker now fails for any DL profile violation in `reasoning.ttl` or failure of its selected entailments/negative control. See [machine results](owl_compatibility.json).

The 31 regression tests and all 35 independent audit checks pass. Two clean workspaces with different hash seeds reproduce 20 artifacts byte-for-byte, matching current outputs. This uses the same installed Python environment and frozen inputs, not a fresh dependency installation.

## Proposed author decision

Use `reasoning.ttl` for terminology OWL reasoning and the canonical dataset plus `provenance.ttl` for source evidence and auditing. Keep `review.ttl` as the combined inspection export with its documented limitations. This division retains evidence while keeping the formal reasoning input within the tested profile.

The trade-off is that reasoning and evidence inspection use different views. The exclusion manifest and preservation tests make their boundary explicit, but the projection does not carry the full statement-level provenance as OWL axioms. Accepting this design does not imply unaided authorship: AI assisted its implementation and proposed the separation. Author review is pending.
