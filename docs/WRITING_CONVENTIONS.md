Apply the following writing and documentation rules throughout this repository from the beginning. Treat them as permanent project conventions.

## 1. Overall writing style

Write like a careful engineer/researcher documenting work for another technical person.

Use:
- concrete technical nouns;
- short factual statements;
- specific observations, commands, files, counts, versions and results;
- restrained interpretation;
- explicit limitations;
- clear separation between observation, interpretation and conclusion.

Prefer wording such as:

- "The loader returned successfully, but all target tables were empty."
- "This isolates the failure to the schema-qualified insertion path."
- "The result does not establish that the transformation logic is incorrect."
- "The verifier retained all submitted assertions; no incremental precision effect was observed."
- "The artifact is preserved for replay."

Do not use promotional or vague wording such as:

- "powerful"
- "cutting-edge"
- "highly advanced"
- "robust" unless demonstrated by a defined test
- "successful" without saying what passed
- "intelligent"
- "comprehensive" unless scope actually supports it
- "novel" unless novelty has been established against prior work

## 2. Do not write the development conversation into the repository

Repository documentation must describe the project, not the interaction used to build it.

Do not write phrases such as:

- "the user requested"
- "the owner approved"
- "owner decision"
- "human approved"
- "assistant"
- "agent was instructed"
- "during this turn"
- "in this chat"
- "next prompt"
- "waiting for approval"
- "do not push yet"
- "ready for the next task"
- "Task 001 / Task 002" unless task numbering is a real project convention
- "checkpoint approved"
- "pending user confirmation"

Do not mention Codex, ChatGPT, AI assistance, prompts, token usage, conversation state, or tool usage in normal project documentation.

If a real system control requires terms such as `authorization`, `approved`, `human review`, or `owner`, retain them only when they are part of the actual technical interface, protocol, artifact name, security control or experimental design.

## 3. Separate engineering state from research claims

For every important finding, distinguish:

**Observation**
What directly happened.

**Evidence**
What file, output, count, test, query or artifact supports it.

**Interpretation**
What the evidence reasonably means.

**Non-claim / limitation**
What the result does not establish.

Use this structure naturally where useful. Do not force headings everywhere.

Never convert:
- a software failure into a scientific finding;
- a passing test into proof of real-world correctness;
- a citation into proof that a claim is true;
- a graph connection into biological or causal evidence;
- absence of data into evidence of absence;
- identifier agreement into semantic equivalence without justification;
- model output into a verified fact.

## 4. Keep current documentation current

The top-level `README.md` is a **living document**.

It must always reflect:
- what currently exists;
- the current architecture;
- current datasets/sources;
- current evaluation status;
- current reproducibility instructions;
- current limitations.

Never leave the README saying "M1 has not begun" after later stages exist.

If the project evolves, update the README instead of preserving obsolete status language there.

Current research summaries should also remain living documents, for example:
- `docs/research_questions.md`
- `docs/evaluation_protocol.md`
- `docs/reproducibility.md`
- `docs/portfolio_summary.md`

## 5. Historical records are historical records

Milestone/design records may preserve what was known at that point.

When writing one, make its historical status obvious through its filename, heading, date, milestone or opening note.

Example:

"Recorded state at M2 closure. Later project status is described in the repository README."

Do not silently rewrite historical records later to make history look cleaner.

If historical bytes become part of a frozen manifest or SHA-256 authority:
- never edit them in place;
- never update the recorded hash merely to accommodate a wording change;
- preserve the exact historical bytes;
- create or update a separate living document instead.

Keep immutable historical evidence separate from editable current summaries whenever possible, e.g.:

`archive/frozen/...`

## 6. Do not over-document project management

Document engineering decisions, not routine workflow.

Worth recording:
- why a modelling choice was made;
- alternatives considered;
- a compatibility failure;
- a changed data interpretation;
- a source limitation;
- a reproducibility boundary;
- why a test exists;
- why an artifact is frozen;
- a failed experiment that changes subsequent design.

Usually not worth recording:
- that a file was staged;
- that a commit is waiting;
- that something will be pushed later;
- that a person approved continuing;
- that no push occurred;
- conversational task sequencing;
- generic "next steps" that simply repeat the plan.

Git already records file history. Do not duplicate Git mechanics in research prose.

## 7. Keep terminology stable

Choose one term for each concept and use it consistently across:
- README;
- source code;
- ontology/schema;
- tests;
- manifests;
- research documents;
- evaluation artifacts.

Do not casually alternate between terms such as:
- record / entity / resource / node;
- evidence / citation / provenance;
- verification / validation;
- dataset / corpus / benchmark;
unless they genuinely mean different things.

When they mean different things, define the distinction once.

## 8. Preserve technical identifiers exactly

Never casually rewrite:
- hashes;
- release IDs;
- manifest IDs;
- ontology IRIs;
- RDF predicates;
- source versions;
- dataset versions;
- commit SHAs;
- question IDs;
- fixture IDs;
- artifact filenames;
- command-line flags;
- JSON keys;
- evaluation condition names;
- recorded counts.

When editing prose around them, preserve these values byte-for-byte unless the underlying technical artifact actually changes.

## 9. Results language

Report numbers before adjectives.

Prefer:

"23/23 tests passed."

Not:

"The system performed extremely well."

Prefer:

"55 submitted assertions passed the local verifier."

Not:

"The verifier successfully guaranteed factuality."

Prefer:

"Required-fact completion was 68.1%."

Not:

"The model showed strong evidence understanding."

If there is no measured improvement, say so directly.

Negative and neutral results are valid results.

## 10. Research language

Do not force every engineering project into a grand research question.

When the main value is engineering, write it as engineering.

Good:
- "This project implements a provenance-preserving transformation pipeline and tests its failure boundaries."
- "The repository demonstrates end-to-end KG construction, retrieval and replay."

Avoid manufacturing novelty:
- "This groundbreaking framework revolutionises..."
- "This research proves..."
- "The proposed architecture solves..."

Research questions should exist only where there is an actual question being evaluated.

## 11. README structure

Prefer a compact README structure:

1. Project name and one-paragraph description
2. What is implemented
3. Architecture/workflow
4. Data or system scope
5. Main results
6. Limitations
7. Reproduction instructions
8. Repository structure / documentation links

A reviewer should understand the project within roughly one minute.

Do not turn the README into a chronological diary.

## 12. Documentation map

If the repository accumulates many milestone documents, maintain:

`docs/README.md`

It should distinguish:
- current summaries;
- technical implementation/results;
- historical development records;
- frozen provenance records.

This prevents an old milestone document from being mistaken for current project status.

## 13. Reproducibility

From the start, keep:
- dependency specification;
- Python/runtime version;
- portable paths;
- environment-variable configuration where needed;
- reproducible commands;
- deterministic seeds where relevant;
- source/release versions;
- hashes where useful;
- tests.

Avoid hard-coded personal paths such as:

`/Users/name/...`
`/private/tmp/...`

Runtime defaults should be repository-relative, home-relative, configurable, or environment-based.

Historical captured commands may preserve an old path if it is genuinely part of the historical record.

## 14. Source and provenance discipline

Keep separate:
- source capture;
- normalized representation;
- derived representation;
- inferred statements;
- generated outputs;
- reviewed outputs.

Never silently replace one with another.

Record enough identity/provenance information to determine:
- where a record came from;
- which source version produced it;
- what transformations occurred;
- which statements are asserted versus derived.

## 15. Editing rule

Before modifying an existing file, determine whether it is:

A. living/current documentation;
B. executable code;
C. generated artifact;
D. historical record;
E. hash-bound/frozen authority.

Living documentation may be updated.

Historical or hash-bound material must not be rewritten merely for style.

If uncertain whether a file is frozen, inspect manifests/tests/references before changing it.

## 16. Consistency check before every substantial commit

Before committing documentation changes, check:

- Does the README still describe the actual current state?
- Do research questions and evaluation protocol agree with the README?
- Are any historical statements accidentally presented as current?
- Did any numeric result change unintentionally?
- Did any hash, ID, source version or artifact name change?
- Did wording become stronger than the evidence?
- Did conversational/process language enter the repository?
- Did a local absolute path enter executable code?
- Did any frozen artifact change?
- Do local Markdown links still resolve?

Fix inconsistencies before committing.

## 17. Tone reference

The desired style is:

**factual, restrained, technical, auditable, and specific.**

The writing should resemble an engineer/researcher maintaining a real system and research record, not:
- an AI-generated project report;
- a tutorial;
- a project-management transcript;
- marketing copy;
- a thesis written before results exist.

Do not make prose more elaborate than necessary.

When uncertain, prefer the smallest defensible claim supported by the evidence.