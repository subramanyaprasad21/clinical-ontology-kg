# Competency queries

Run any `.rq` with `python scripts/query.py queries/competency/<file>.rq`. Queries use explicit source, provenance, inference or validation graph IRIs; the default graph is empty. The build executes all eleven and saves complete JSON result tables. Unsupported clinical joins have zero rows and explicit `unsupported` status; zero rows is not evidence of clinical absence.
