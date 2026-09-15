# Verification

Run `scripts/build.py` first, then `python -m pytest -q`. Tests combine adversarial small fixtures with assertions against the real exported dataset. They check input integrity, nested OWL handling, HPO aspect/negation, mapping boundaries, inference dependence, provenance completeness, artifact round trips, and real competency results. Synthetic fixtures never enter the production graph.

`python scripts/check_reproducibility.py` runs two complete builds and compares scientific artifacts byte-for-byte. See `reports/reproducibility.json`. A final test run is captured in `reports/tests.txt` and `reports/tests.xml`.
