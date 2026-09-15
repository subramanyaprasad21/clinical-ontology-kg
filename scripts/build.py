#!/usr/bin/env python3
"""Build offline from the repository's frozen raw input files."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from clinical_kg.pipeline import build
if __name__ == '__main__':
    metrics = build(ROOT)
    print(f"Build complete: {metrics['asserted_unique_triples']} asserted triples; "
          f"{metrics['provenance']['coverage_percent']}% assertion provenance.")
