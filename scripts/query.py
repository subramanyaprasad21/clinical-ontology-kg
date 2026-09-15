#!/usr/bin/env python3
"""Run a local read-only SPARQL query against the exported named-graph dataset."""
import argparse
import json
from pathlib import Path
from rdflib import Dataset
ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', type=Path, help='Path to a local .rq competency query')
    args = parser.parse_args()
    ds = Dataset()
    ds.parse(ROOT / 'data/processed/knowledge_graph.nq', format='nquads')
    query = args.query.read_text()
    # The bundled queries are offline SELECT queries. Do not offer a remote SERVICE runner.
    import re
    if re.search(r'\b(SERVICE|LOAD|FROM)\b', query, re.IGNORECASE):
        raise SystemExit('Remote query operations are outside this offline runner.')
    result = ds.query(query)
    if result.type != 'SELECT':
        raise SystemExit('This runner accepts SELECT result tables only.')
    print(json.dumps([{str(v): str(row[v]) if row[v] is not None else None for v in result.vars}
                      for row in result], indent=2))
