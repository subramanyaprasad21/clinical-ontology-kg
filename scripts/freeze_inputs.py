#!/usr/bin/env python3
"""Create an input manifest once; never overwrite an existing freeze."""
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from clinical_kg.inputs import inventory, dump
if __name__ == '__main__':
    path = ROOT / 'config/input_manifest.json'
    if path.exists():
        raise SystemExit('Manifest already exists. Explicitly review any proposed new freeze; overwrite refused.')
    dump(path, {'schema_version': 1, 'freeze_observed_at': datetime.now(timezone.utc).isoformat(),
                'inputs': inventory(ROOT),
                'note': 'Freeze observation time is not a download/access date. Unknown acquisition fields remain null.'})
    print(path)
