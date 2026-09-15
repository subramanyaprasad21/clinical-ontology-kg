#!/usr/bin/env python3
"""Run two complete offline builds and compare stable scientific artifacts."""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from clinical_kg.inputs import digest, dump


def snapshot():
    paths = sorted((ROOT / 'data/processed').glob('*')) + [ROOT / 'data/interim/audit.json', ROOT / 'reports/metrics.json', ROOT / 'reports/FINAL_REPORT.md',
        ROOT / 'reports/validation.ttl', ROOT / 'reports/validation.txt', ROOT / 'reports/artifact_checksums.json']
    paths += sorted((ROOT / 'reports/tables').glob('*.json'))
    return {str(p.relative_to(ROOT)): digest(p) for p in paths if p.is_file() and not p.name.startswith('.')}


if __name__ == '__main__':
    subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], check=True, cwd=ROOT)
    first = snapshot()
    subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], check=True, cwd=ROOT)
    second = snapshot()
    changed = sorted(k for k in first.keys() | second.keys() if first.get(k) != second.get(k))
    dump(ROOT / 'reports/reproducibility.json', {'identical': not changed, 'compared_artifacts': len(first),
         'changed': changed, 'sha256': second, 'scope': 'two builds, same frozen inputs and pinned local environment'})
    if changed:
        raise SystemExit('Nondeterministic artifacts: ' + ', '.join(changed))
    print(f'Reproducibility passed: {len(first)} artifacts byte-identical across two complete builds.')
