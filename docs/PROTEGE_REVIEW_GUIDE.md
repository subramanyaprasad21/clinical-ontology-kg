# Review the model in Protégé

This is a manual understanding exercise. The author has accepted the disease-level annotation interpretation and evidence-conflict policy in conversation; the remaining design review and a manual Protégé walkthrough are pending. The automated audit does not establish human sign-off. Use copies for experiments and record observations in [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md); do not edit generated artifacts as the way to change the reproducible model.

## Files and views

Start with `ontology/core/core.ttl` to inspect the local definition in isolation. Then open the generated `data/processed/review.ttl` in a separate window for the source facts plus schema. Build it first with `.venv/bin/python scripts/build.py` if it is absent. The raw 242 MB Mondo ontology is not needed for this initial walkthrough.

Protégé's [view reference](https://protegeproject.github.io/protege/views/) describes the class hierarchy, class description, object property description, annotations and individual views. If a view is missing, add it through **Window → Views**. Exact tab arrangements can differ by installation. Use the search/find facility with the identifier suffixes below rather than relying on label rendering.

## Walkthrough

| Inspect | Entity or view | What to establish |
|---|---|---|
| Local definition | `PhenotypeAnnotatedConcept`, Class Description | Equivalent intersection of `DiseaseConcept` and `hasPhenotype some HPOTerm`; not equivalent to the Mondo disease class |
| Property hierarchy | `hasPhenotype`, Object Property Description | Subproperty of `hasHPOAnnotation`; inverse `phenotypeOf` |
| Other annotations | `hasInheritanceAnnotation`, `hasClinicalModifier`, `hasExcludedPhenotype` | Separate meanings; exclusion is not an OWL negative-property assertion |
| Domain/range | `hasHPOAnnotation` and `phenotypeOf` | Terminology concepts and HPO terms; inferential typing, not input rejection |
| Disease hierarchy | `MONDO_0005148`, Class Hierarchy and Description in `review.ttl` | Direct named superclass `MONDO_0005015`; further ancestors include upper ontology context |
| Positive annotations | Mondo terminology individual with IRI ending `MONDO_0005148` | Objects `HP_0000855`, `HP_0005978`, `HP_0031819` via `hasPhenotype` |
| Non-phenotype aspects | Same individual | `HP_0000006` via inheritance; `HP_0003584` via clinical modifier |
| Mapping | Search `125853` and `MONDO_0005148`; inspect Usage/Annotations where rendered | Explicit `skos:exactMatch` to the OMIM IRI; no manually added identity link |
| Labels and xrefs | Entity Annotations/Usage | `rdfs:label`, `skos:altLabel`, `kg:sourceXref`; source labels do not prove equivalence |

The terminology individual and the disease class can share an IRI. Inspect both roles: a concept's phenotype relation is an individual-level assertion in this model, not an OWL restriction on every patient instance of the disease class. The HPO term named Type II diabetes mellitus remains separate from Mondo.

`review.ttl` explicitly declares identifiers, source xrefs and alternative labels as annotation properties; exact matching remains an object property. It declares terminology individuals and referenced classes. These export declarations make the intended roles explicit and do not equate mapped concepts. The underlying `core.ttl` remains unchanged.

## Reasoner check

Inspect the asserted model before starting a reasoner. Record the installed reasoner and version. If the ontology is accepted, run it and enable the relevant displayed inferences in Reasoner Preferences. Protégé's [Individual Description](https://protegeproject.github.io/protege/views/individual-description/) shows individual types, and [Reasoner Preferences](https://protegeproject.github.io/protege/preferences/reasoner/) controls which computed results are displayed.

The verified Python OWL RL workflow derives these results:

- Mondo T2DM and OMIM:125853 terminology individuals have type `PhenotypeAnnotatedConcept`.
- Each of their three phenotype terms has the inverse `phenotypeOf` relation.
- Fifteen additional named ancestors of T2DM follow transitively from its direct hierarchy.

The first result is **individual classification**, not a new disease superclass. Look in individual types/instances rather than expecting T2DM to move underneath the local annotation class in the disease hierarchy. The [Class Description](https://protegeproject.github.io/protege/views/class-description/) distinguishes equivalent classes, superclasses and instances.

The installed Protégé 5.6.9 OWL API 4.5.29 and HermiT 1.4.3.456 libraries now verify consistency, the Mondo individual classification and one inverse relation in the repaired export. This is an automated library check, not a completed human GUI walkthrough. `review.ttl` preserves anonymous restriction/list nodes; the canonical RDF dataset still uses stable IRIs. Three OWL DL profile violations involving `rdf:Statement` in the provenance schema remain and are not suppressed. See [the follow-up report](../reports/EXPORT_VALIDATION_FOLLOWUP.md) for exact scope and reproduction.

`data/processed/inferred.ttl` is the materialized result of the Python run. If you load those triples manually, Protégé treats the loaded statements as assertions in that document; their presence is not proof that the Protégé reasoner derived them. Use the separate source and inference files plus competency query 09 for that distinction.

## Provenance and useful observations

`data/processed/provenance.ttl` contains statement, record and snapshot resources. It is RDF provenance, not a conventional clinical OWL ontology, so Protégé may be less useful than the query runner for this part. Run:

```sh
.venv/bin/python scripts/query.py queries/competency/03_phenotype_evidence.rq
.venv/bin/python scripts/query.py queries/competency/10_provenance.rq
```

Choose a phenotype assertion and follow its record locator to the source file, original identifier, version basis and build activity. Named graph context is preserved in `knowledge_graph.nq`; Protégé's flattened review ontology does not display that dataset separation.

Useful views to save for your own review are: the T2DM direct hierarchy, the local equivalent-class definition, the property inverse/subproperty description, an individual's positive versus inheritance/onset relations, and a successful inferred-type view **or the actual reasoner warning**. Label each image with the file and whether it shows asserted, loaded materialized, or newly reasoned content. Screenshots support your understanding; they are not substitutes for the executed checks.

Finish by recording what you accepted, what you would change, and what your installed tools could not verify. Human review remains pending until those observations actually exist.
