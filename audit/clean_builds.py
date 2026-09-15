"""Run the existing pipeline in two empty derived-output workspaces.

Raw files are hard-linked solely to avoid duplicate storage; the audited pipeline
opens them read-only and verifies their hashes before/after each build. This is
same-interpreter reproduction, not a fresh dependency installation.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/credibility_audit'


def hashfile(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def artifact_hashes(root):
    files = sorted((root / 'data/processed').glob('*'))
    files += [root / 'data/interim/audit.json', root / 'reports/metrics.json', root / 'reports/FINAL_REPORT.md',
              root / 'reports/validation.ttl', root / 'reports/validation.txt', root / 'reports/artifact_checksums.json']
    files += sorted((root / 'reports/tables').glob('*.json'))
    return {str(p.relative_to(root)): hashfile(p) for p in files if p.is_file() and not p.name.startswith('.')}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    runs = []
    for n in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f'clinical-kg-audit-{n}-') as directory:
            checkout = Path(directory)
            for name in ('src', 'scripts', 'ontology', 'queries', 'config', 'tests'):
                shutil.copytree(ROOT / name, checkout / name, ignore=shutil.ignore_patterns('__pycache__'))
            for name in ('requirements.txt', 'pyproject.toml'):
                shutil.copy2(ROOT / name, checkout / name)
            shutil.copytree(ROOT / 'data/raw', checkout / 'data/raw', copy_function=os.link)
            assert not (checkout / 'data/interim').exists() and not (checkout / 'data/processed').exists()
            # Different hash seeds also challenge accidental set iteration order dependencies.
            environment = dict(os.environ, PYTHONHASHSEED=str(101 * n))
            result = subprocess.run([sys.executable, 'scripts/build.py'], cwd=checkout, env=environment,
                                    capture_output=True, text=True)
            (OUT / f'clean_build_{n}.log').write_text(result.stdout + result.stderr)
            if result.returncode:
                raise RuntimeError(f'Clean build {n} failed; see saved log')
            tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--tb=short'], cwd=checkout,
                                   env=environment, capture_output=True, text=True)
            (OUT / f'clean_tests_{n}.log').write_text(tests.stdout + tests.stderr)
            runs.append({'run': n, 'clean_derived_outputs': True, 'hash_seed': environment['PYTHONHASHSEED'],
                         'build_exit_code': result.returncode, 'tests_exit_code': tests.returncode,
                         'sha256': artifact_hashes(checkout)})
            print(f'Clean build {n}: success; tests exit {tests.returncode}', flush=True)
    changed = [name for name in runs[0]['sha256'].keys() | runs[1]['sha256'].keys()
               if runs[0]['sha256'].get(name) != runs[1]['sha256'].get(name)]
    current = artifact_hashes(ROOT)
    baseline_differences = sorted(k for k, v in runs[0]['sha256'].items() if current.get(k) != v)
    evidence = {'runs': runs, 'byte_identical': not changed, 'changed_between_clean_builds': sorted(changed),
                'compared_artifacts': len(runs[0]['sha256']), 'differences_from_repository_artifacts': baseline_differences,
                'scope': 'Separate empty derived-output directories; same installed interpreter/packages, linked frozen raw inputs; different Python hash seeds.',
                'audit_script_sha256': hashfile(Path(__file__))}
    (OUT / 'clean_builds.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    if changed or any(r['tests_exit_code'] for r in runs):
        raise SystemExit('Clean build comparison or tests failed; evidence retained')
    print(f"Verified {len(current)} artifacts; repository differences: {len(baseline_differences)}", flush=True)


if __name__ == '__main__':
    main()
