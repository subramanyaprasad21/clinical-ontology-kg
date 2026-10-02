"""Run final project checks in an isolated workspace with fresh pinned packages."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'audit'))
from clean_builds import artifact_hashes


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protege-contents', type=Path, required=True)
    parser.add_argument('--java-home', type=Path, required=True)
    args = parser.parse_args()
    out = ROOT/'reports/final'; out.mkdir(exist_ok=True)
    logs = out/'logs'; logs.mkdir(exist_ok=True)
    result = {'python': platform.python_version(), 'platform': platform.platform(), 'steps': {},
              'scope': 'Fresh pinned packages and empty derived outputs on the same host/base Python; captured inputs hard-linked read-only by convention.',
              'harness_sha256': sha(Path(__file__)), 'requirements_sha256': sha(ROOT/'requirements.txt')}
    def save(): (out/'project_verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    with tempfile.TemporaryDirectory(prefix='clinical-kg-final-') as temporary:
        base = Path(temporary); workspace = base/'workspace'; workspace.mkdir()
        for name in ('src', 'scripts', 'ontology', 'queries', 'config', 'tests', 'audit'):
            shutil.copytree(ROOT/name, workspace/name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('requirements.txt', 'pyproject.toml'): shutil.copy2(ROOT/name, workspace/name)
        shutil.copytree(ROOT/'data/raw', workspace/'data/raw', copy_function=os.link)
        (workspace/'reports/extension').mkdir(parents=True)
        for name in ('capture_manifest.json', 'clinical_report_manifest.json'):
            receipt = ROOT/'reports/extension'/name
            shutil.copy2(receipt, workspace/'reports/extension'/name)
            for entry in json.loads(receipt.read_text())['files']:
                destination = workspace/entry['path']; destination.parent.mkdir(parents=True, exist_ok=True)
                os.link(ROOT/entry['path'], destination)
        envdir = base/'venv'
        subprocess.run([sys.executable, '-m', 'venv', str(envdir)], check=True)
        python = envdir/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        commands = [
            ('install', ['-m', 'pip', 'install', '--no-cache-dir', '-r', 'requirements.txt']),
            ('dependency_check', ['-m', 'pip', 'check']),
            ('core_build', ['scripts/build.py']),
            ('all_tests', ['-m', 'pytest', '-q', 'tests', 'audit/extension/test_build.py', 'audit/extension/test_reports.py']),
            ('core_audit', ['audit/verify.py']),
            ('core_clean_builds', ['audit/clean_builds.py']),
            ('core_repeatability', ['scripts/check_reproducibility.py']),
            ('owl', ['audit/owl/check.py', '--protege-contents', str(args.protege_contents.resolve()),
                     '--java-home', str(args.java_home.resolve()), '--output', 'reports/final/owl_checks.json']),
            ('extension_build', ['audit/extension/final_build.py']),
            ('extension_audit', ['audit/extension/verify_final.py']),
        ]
        for name, command in commands:
            print(f'{name}: started', flush=True)
            with (logs/f'{name}.log').open('w') as log:
                completed = subprocess.run([str(python), *command], cwd=workspace,
                                           env=dict(os.environ, PYTHONHASHSEED='707'), stdout=log, stderr=subprocess.STDOUT)
            result['steps'][name] = completed.returncode; save()
            print(f'{name}: exit {completed.returncode}', flush=True)
            if completed.returncode: raise SystemExit(f'{name} failed; inspect reports/final/logs/{name}.log')
        result['packages'] = json.loads(subprocess.check_output([str(python), '-m', 'pip', 'list', '--format=json'], text=True))
        expected = artifact_hashes(ROOT); actual = artifact_hashes(workspace)
        result['core_artifacts_compared'] = len(expected)
        result['core_artifact_differences'] = sorted(k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k))
        final = Path('data/extensions/opentargets-26.09/final')
        names = ('extension.nq', 'query_results.json', 'validation.txt')
        result['extension_artifact_sha256'] = {name: sha(workspace/final/name) for name in names}
        result['extension_artifact_differences'] = [name for name in names if sha(ROOT/final/name) != sha(workspace/final/name)]
        # These summaries exclude execution time and temporary absolute paths.
        result['extension_summary_identical'] = (ROOT/'reports/final/extension_summary.json').read_bytes() == (workspace/'reports/final/extension_summary.json').read_bytes()
        for source, destination in [
            ('reports/credibility_audit/verification.json', 'core_audit.json'),
            ('reports/credibility_audit/clean_builds.json', 'core_clean_builds.json'),
            ('reports/reproducibility.json', 'core_repeatability.json'),
            ('reports/final/owl_checks.json', 'owl_checks.json'),
        ]: shutil.copy2(workspace/source, out/destination)
        result['protected_files_checked'] = 0; changed = []
        for path, expected_hash in json.loads((out/'protected_files.json').read_text()).items():
            result['protected_files_checked'] += 1
            if not (ROOT/path).is_file() or sha(ROOT/path) != expected_hash: changed.append(path)
        result['protected_files_changed'] = changed
        result['all_checks_passed'] = not (result['core_artifact_differences'] or result['extension_artifact_differences'] or changed) and result['extension_summary_identical']
        save()
        if not result['all_checks_passed']: raise SystemExit('Final comparison failed')
    print('Final project verification passed.', flush=True)


if __name__ == '__main__': main()
