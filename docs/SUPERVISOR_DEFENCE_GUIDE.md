# Questions for a supervisor discussion

These questions explain the current implementation and its evidence boundaries. Refer to the [semantic model](04_ontology_design_notes.md) and the source artifacts for the implemented choices.

1. **What is the research question?** Can the supplied Mondo, HPO and Open Targets records be integrated around T2DM while retaining identity, evidence, provenance and explicit limits? The result is an engineering case study, not a new clinical ontology. See the [charter](00_project_charter.md).

2. **Why T2DM?** The supplied brief selected it as a bounded disease case with hierarchy, phenotype and potential drug/target questions. The implementation did not perform a comparative disease-selection study or establish that T2DM is the best benchmark.

3. **Why RDF rather than a property graph?** The task requires source IRIs, OWL axioms, SKOS mappings, PROV-O and SHACL in one representation. RDF supports that combination directly. This project does not benchmark RDF against Neo4j or establish a performance advantage.

4. **What does RDFS contribute?** Native `rdfs:subClassOf` edges preserve the named disease hierarchy. Local subclass, subproperty and domain/range axioms organize terminology types and annotations. Question 01 traverses the asserted hierarchy; that traversal itself is not OWL reasoning.

5. **What does OWL add beyond those RDFS relations?** The local equivalent-class restriction classifies concepts with positive phenotype annotations, and `owl:inverseOf` derives the reverse relation. The audit independently recomputes the closure from exported premises. See [reasoning.py](../src/clinical_kg/reasoning.py).

6. **What is an axiom here?** A formal statement such as `hasPhenotype owl:inverseOf phenotypeOf`, or the definition of `PhenotypeAnnotatedConcept`. Some axioms come directly from Mondo; the local vocabulary is an implementation design. Their origins should not be conflated.

7. **Does a disease identifier denote a class or an individual?** The native Mondo IRI participates as an OWL class in its hierarchy and as a terminology concept in metadata relations. The latter does not denote a patient. This class/concept dual use needs careful explanation and has not been certified for every OWL DL tool.

8. **What does the existential restriction mean?** A `DiseaseConcept` related by `hasPhenotype` to at least one `HPOTerm` satisfies the local definition. It classifies the annotation-bearing concept, not a person. It does not assert that all people with T2DM exhibit that term.

9. **Are there cardinality axioms?** No OWL cardinality axioms are implemented. SHACL has min/max counts for record fields and statement components. Requiring exactly one provenance record on an assertion is a data-shape choice, not a clinical cardinality.

10. **Why is domain/range not validation?** Those axioms can infer the types of relation endpoints; they do not reject a row because a type was omitted. The build therefore runs SHACL before reasoning. Its shapes test selected graph expectations independently of inferred typing.

11. **Why SKOS instead of `owl:sameAs`?** The mappings align terminology concepts without treating them as universally substitutable individuals. The ten exact-match triples are explicit Mondo claims, not label-based identity guesses. No source `owl:sameAs` is generated. See the [mapping policy](02_mapping_policy.md).

12. **What exactly does “exact mapping” establish?** It establishes that this Mondo snapshot explicitly claims the corresponding SKOS relation. This audit verifies preservation of that claim, not the complete clinical semantics of every external target vocabulary. Broader/narrower/related categories are permitted but unpopulated.

13. **How was the Mondo–HPO join verified?** Mondo explicitly maps T2DM to `https://omim.org/entry/125853`. HPOA has five rows under `OMIM:125853`. The identifier conversion is syntactic and the mapping provides its semantic justification. The [join matrix](../reports/CREDIBILITY_AUDIT.md) records the evidence.

14. **What came from each source?** Mondo supplies the anchor, named hierarchy, synonyms, xrefs and mapping claims. HPO supplies terms and OMIM-indexed annotations. OT preserves the Mondo disease identifier and HPO-derived phenotype evidence; its drug/target catalogs were audited but not added as unrelated graph instances.

15. **Why are there five HPO terms but only three phenotypes?** Three rows have aspect P. Autosomal dominant inheritance has aspect I, and late onset has C. The pipeline gives them separate predicates. Calling all five clinical phenotypes would distort the source format.

16. **Why is “Type II diabetes mellitus” itself an HPO term here?** The selected HPOA record uses that term with aspect P. It is retained with its source identity and provenance, without equating it to the Mondo class based on the similar label. This should be explained as a source annotation, not a new diagnostic conclusion.

17. **Do two sources corroborate the phenotype findings?** Not independently. OT's nested evidence names HPO and agrees with the HPOA signatures. Each OT row also repeats its evidence twice. Separate deliveries and duplicate entries are not separate studies.

18. **Why are the drug/target questions unsupported?** The supplied target, molecule and mechanism tables contain catalog identifiers and drug–target relations, but no structured relation from T2DM to a target or indication. All mechanism catalog references resolve; the missing part is the clinical leg of the path.

19. **Why not download another dataset?** The frozen brief requires testing the available source set first and preserving negative results. A larger source set would answer a different feasibility question. A later extension needs a specific clinical relation, version and provenance plan.

20. **What is an asserted versus inferred triple?** A source fact is added by the documented extraction/projection and retained in a source graph. An inferred triple is new relative to those facts and the schema, produced by the reasoner and stored separately. Local schema axioms are authored premises, not imported clinical evidence.

21. **Is the reasoning substantive?** It is genuine but elementary: two annotation-concept classifications, six inverse edges and fifteen additional named ancestors are demonstrated. The 585 closure additions include bookkeeping. Removing positive phenotype premises removes the classifications and inverse edges, but this is not diagnostic or treatment reasoning.

22. **How is provenance represented?** Reified assertion → source record → snapshot, with original ID, physical locator, payload, version and file hash; each assertion also names its build activity and graph. All 179 assertion occurrences cover 174 source quads. This audit checked 38 selected record payloads against raw files. See the [provenance model](provenance_model.md).

23. **Why named graphs, and is RDF-star used?** Named graphs distinguish source deliveries, schema, inference, validation and provenance even where the fact triples coincide. Flattened Turtle loses that context. RDF-star is not used; provenance relies on RDF statement reification and PROV-O.

24. **What does SHACL establish, and what escaped it?** Nine shapes check selected entity, relation, mapping, record and snapshot requirements. Six isolated mutations produce their expected violations. Malformed generic endpoints are rejected. Positive/excluded pairs are flagged by a separate evidence report. Conformity therefore is not a general semantic-quality certificate.

25. **How are conflicts and negation treated?** A negated P record uses `hasExcludedPhenotype`, not a positive relation. The predicate is an exclusion marker, not a formal OWL negative assertion. There is no canonical negative record here. The conflict report preserves both source records and gives neither automatic priority; it does not resolve clinical disagreement.

26. **What does deterministic reproduction mean?** Two workspaces starting without derived outputs, using different Python hash seeds, reproduce all 20 selected files byte-for-byte and pass the 31 tests. They share the same installed Python/dependencies and exact local raw inputs. A clone alone cannot reacquire the files from the incomplete acquisition manifest.

27. **Why is this semantic integration rather than file conversion?** It verifies cross-source identity claims, distinguishes annotation meanings, retains unresolved mappings, formalizes local entailments and keeps evidence lineage. The mapping/projection choices are the semantic work. Correct RDF serialization alone would not establish them.

28. **What remains outside scope?** Verified acquisition history, cross-platform reproduction and full-source ontology reasoning are not demonstrated. A freshly installed virtual environment reproduces the 20 artifacts on the same host. Patient-level work would additionally require individual/observation modelling, time, uncertainty and access controls. None is implemented here.
