# Verified data feasibility

The evidence is generated directly from local files by `scripts/audit.py` and recorded in `data/interim/audit.json` and `reports/tables/input_schemas.json`. No identifiers below were accepted solely because labels match.

| Join / relationship | Verified local evidence | Decision |
|---|---|---|
| Mondo T2DM | Unique active class `MONDO_0005148`, label “type 2 diabetes mellitus” | Anchor |
| Disease hierarchy | Named direct parent `MONDO_0005015` (“diabetes mellitus”); 17 classes in inclusive named-parent closure | Include named subclass axioms |
| Mondo → HPO disease | Mondo explicitly asserts `skos:exactMatch https://omim.org/entry/125853`; HPOA has `database_id=OMIM:125853` | Exact source mapping; preserve both concept IRIs |
| Mondo → OT disease | OT `id=MONDO_0005148`, `code=http://purl.obolibrary.org/obo/MONDO_0005148`; unique matching row | Same identifier reused, not a new equivalence assertion |
| HPOA → HPO ontology | Each of five `HP:...` IDs resolves after colon/underscore syntax conversion | Five HPO terms included |
| OT disease → OT phenotype | Five rows have `disease=MONDO_0005148` | Include evidence-aware annotations |
| HPO → OT evidence | OT evidence explicitly carries `diseaseFromSourceId=OMIM:125853`, `resource=HPO`, matching terms/aspects | Shared upstream evidence, not independent corroboration |
| OT mechanism → target | All 12,698 target references in 6,500 mechanisms resolve against target `id` | Catalog join verified; no T2DM selection key |
| OT mechanism → drug | All 7,924 `chemblIds` references resolve against molecule `id` | Catalog join verified; no T2DM selection key |
| T2DM → target | No association/evidence dataset; target catalog has no structured T2DM association field | Unsupported |
| Drug → T2DM indication | Molecule schema has no structured disease/indication field; mechanism has no disease field | Unsupported; no clinical relation mined from free text |
| Disease → target ← drug | Missing disease-target leg | Unsupported |
| NANDO mapping | Anchor has xref `NANDO:2200461` without corresponding explicit SKOS mapping | Retain unresolved candidate |

## Annotation audit

| HPO ID | Source label | Aspect | Graph predicate |
|---|---|---|---|
| HP:0000855 | Insulin resistance | P | `kg:hasPhenotype` |
| HP:0005978 | Type II diabetes mellitus | P | `kg:hasPhenotype` |
| HP:0031819 | Increased waist to hip ratio | P | `kg:hasPhenotype` |
| HP:0000006 | Autosomal dominant inheritance | I | `kg:hasInheritanceAnnotation` |
| HP:0003584 | Late onset | C | `kg:hasClinicalModifier` |

The “Type II diabetes mellitus” HPO term remains a phenotype concept. Similar naming does not establish identity with Mondo. Inheritance and onset are source annotations, not blanket clinical claims about every person with T2DM.

Five HPOA rows correspond to five OT disease/phenotype rows, each containing two identical evidence entries. Physical entries remain traceable; five redundant entries are reported. They do not increase the number of phenotype associations or independent observations. These records cite `OMIM:125853` with evidence code `TAS`.

## Versions and acquisition evidence

- Mondo ontology: embedded version IRI identifies `2026-09-01`.
- HPO ontology: embedded version IRI identifies `2026-09-01`.
- HPO annotations: embedded `#version: 2026-09-02`; the header points to HPO ontology `2026-09-01`.
- Open Targets: `26.06` is user-declared. Parquet schemas and Spark metadata do not independently prove that release. The disease files preserve the audited Mondo anchor, but that is not release authentication.
- Original download URLs and dates were not supplied. Manifest fields remain null. The manifest records a separate freeze-observation timestamp, byte sizes and SHA-256 hashes. File modification times are not substituted for download dates.

The go/no-go decision is **go for the bounded semantic core**, with explicit negative results for drug/target clinical joins and incomplete acquisition history.
