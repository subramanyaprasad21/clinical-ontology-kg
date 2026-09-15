# Mapping policy

1. Identify the active Mondo anchor using its exact label and confirm the unique resulting IRI. Labels identify the requested starting class; they never authorize cross-resource equivalence.
2. Import the anchor's explicit SKOS mappings with their original predicates. In this snapshot there are ten `skos:exactMatch` assertions and no broad/narrow/related/close mappings. These are source assertions, not independently validated clinical equivalences.
3. Preserve Mondo and OMIM IRIs. HPOA `OMIM:125853` is converted to the OMIM IRI using a documented identifier rule only after the Mondo exact mapping is verified.
4. An OT record whose `code` equals the Mondo IRI shares that identifier. Named graphs distinguish assertions made in different snapshots. No redundant `owl:sameAs` is introduced.
5. Normalize HPO CURIE punctuation (`HP:0000855` → `HP_0000855`) without changing concept identity. Resolve the result against the actual local HPO ontology.
6. An ordinary xref does not imply exact equivalence. URI syntax rules in `mapping.py` are used to compare xrefs with explicit source mappings. `NANDO:2200461` has no verified matching SKOS assertion and remains a `MappingCandidate` with `status="unresolved"`.
7. Broad, narrow, related and close mapping types are permitted by SHACL. They are not generated just to populate categories. No mapping confidence score is invented. Method and evidence are recorded instead.
8. An ambiguous or missing required anchor fails the audit. Missing HPO terms are written to the audit and fail the build. Unresolved optional mapping candidates remain visible in the graph and reports.

A source mapping assertion is reified as both `rdf:Statement` and `kg:MappingAssertion`. It links to a record, source snapshot and build activity, and records `kg:mappingMethod`. The full source class projection preserves xrefs, exact synonyms and mappings for inspection.

SKOS exact matching is used for cross-source query alignment; it does not authorize copying every phenotype or clinical relation across concepts. The multi-source query compares annotations along a verified exact mapping without inserting extra biomedical facts. No source-derived `owl:sameAs` facts are produced. OWL RL may emit reflexive identity bookkeeping in its separate inference graph; that is not a mapping policy.
