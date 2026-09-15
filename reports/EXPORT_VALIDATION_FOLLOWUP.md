# Export and validation follow-up

The review export now preserves the existential restriction when loaded by the installed Protégé libraries. Generic annotation endpoints have a SHACL shape. A separate report flags positive/excluded phenotype pairs for evidence review without deleting either assertion or declaring a clinical contradiction.

## OWL export finding and repair

The previous review file reused the dataset’s skolem IRIs for restriction/list nodes. OWL API parsed those as named classes: HermiT derived the inverse relation but did not classify the Mondo T2DM terminology individual as `PhenotypeAnnotatedConcept`. The source `core.ttl` itself contained the intended anonymous restriction.

`src/clinical_kg/review.py` now combines every asserted source triple with the original schema, preserves anonymous nodes, canonicalizes their labels for deterministic serialization, and adds explicit class, individual and property declarations. The source schema and canonical RDF dataset representation are unchanged. Identifier, xref and alternative-label predicates are declared as annotation properties; `skos:exactMatch` is an object property, not identity. RDF round trips compare graph isomorphism because parser-assigned blank-node labels can differ.

Using Protégé 5.6.9’s OWL API 4.5.29 and HermiT 1.4.3.456, the exported review ontology is consistent and entails both the Mondo annotation-class membership and the selected `HP_0000855 phenotypeOf MONDO_0005148` inverse. These checks invoke the actual installed libraries, not the GUI. They do not claim complete DL profile compliance or validate clinical truth.

Three OWL 2 DL profile violations remain: declaring the reserved `rdf:Statement` vocabulary as a class and the two provenance subclasses of it. No provenance axiom was removed to obtain a pass. A future decision about a separate clinical OWL module versus an RDF provenance model requires explicit design review. The machine report includes all profile violations and the library manifests/hashes: [owl_compatibility.json](owl_compatibility.json).

Reproduce offline, substituting the local installation paths:

```sh
.venv/bin/python scripts/build.py
.venv/bin/python -m pytest -q
.venv/bin/python audit/owl/check.py \
  --protege-contents '/path/to/Protege.app/Contents' \
  --java-home '/path/to/jdk/Contents/Home'
.venv/bin/python audit/verify.py
.venv/bin/python audit/clean_builds.py
```

The OWL check fails if consistency or either selected entailment fails. It reports profile violations without hiding them; it does not treat their presence as DL certification.

## Validation and evidence disagreements

The generic `hasHPOAnnotation` shape checks disease subject typing and an IRI target typed as `HPOTerm`, before inference. Regression cases exercise a literal, an untyped IRI and a valid typed IRI. The existing six invalid demonstrations remain intact.

`reports/tables/phenotype_conflicts.json` records exact-IRI pairs asserted both positively and as excluded, with assertion identifiers, source records and named graphs. Same-source and cross-source cases are tested. Evidence is preserved unchanged. The frozen data has no such pairs. Detection does not propagate across mappings, infer missing negative evidence, or adjudicate disagreements. This report is separate from hard SHACL conformity and competency query 11’s violation count.

## Verification and authorship boundary

All 29 regression tests pass. The source scope remains 160 unique asserted triples, 174 source quads and 179 imported assertion occurrences, with 100% source-quad provenance coverage. All 35 independent fidelity checks pass. Two clean workspaces with different hash seeds reproduce 18 artifacts byte-for-byte, matching the repository outputs. These runs share the installed Python environment and frozen inputs; they do not establish fresh-environment reproduction. The earlier audit is retained as historical evidence, not rewritten to imply these fixes existed then.

AI assisted this repair, validation code and documentation. Earlier assistance also included ontology drafting. Human review and acceptance of the modelling choices remain pending. No design ownership or human review is inferred from passing tests.
