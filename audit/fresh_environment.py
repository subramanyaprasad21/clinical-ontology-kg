"""Reinstall pinned dependencies and reproduce artifacts in an empty workspace."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from clean_builds import artifact_hashes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/fresh_environment'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {'python': platform.python_version(), 'platform': platform.platform(),
               'requirements_sha256': hashlib.sha256((ROOT / 'requirements.txt').read_bytes()).hexdigest(),
               'scope': 'New virtual environment and empty output workspace; same host, base Python and hard-linked frozen raw files.',
               'steps': {}}
    with tempfile.TemporaryDirectory(prefix='clinical-kg-fresh-') as temporary:
        base = Path(temporary)
        envdir, workspace = base / 'venv', base / 'workspace'
        subprocess.run([sys.executable, '-m', 'venv', str(envdir)], check=True)
        python = envdir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        workspace.mkdir()
        for name in ('src', 'scripts', 'ontology', 'queries', 'config', 'tests', 'audit'):
            shutil.copytree(ROOT / name, workspace / name, ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('requirements.txt', 'pyproject.toml'):
            shutil.copy2(ROOT / name, workspace / name)
        shutil.copytree(ROOT / 'data/raw', workspace / 'data/raw', copy_function=os.link)
        commands = {
            'install': [str(python), '-m', 'pip', 'install', '--no-cache-dir', '-r', 'requirements.txt'],
            'dependency_check': [str(python), '-m', 'pip', 'check'],
            'build': [str(python), 'scripts/build.py'],
            'tests': [str(python), '-m', 'pytest', '-q'],
            'audit': [str(python), 'audit/verify.py'],
        }
        for name, command in commands.items():
            result = subprocess.run(command, cwd=workspace, env=dict(os.environ, PYTHONHASHSEED='303'), capture_output=True, text=True)
            (OUT / f'{name}.log').write_text(result.stdout + result.stderr)
            results['steps'][name] = result.returncode
            print(f'{name}: exit {result.returncode}', flush=True)
            if result.returncode:
                (OUT / 'result.json').write_text(json.dumps(results, indent=2) + '\n')
                raise SystemExit(result.returncode)
        results['packages'] = json.loads(subprocess.check_output([str(python), '-m', 'pip', 'list', '--format=json'], text=True))
        produced, baseline = artifact_hashes(workspace), artifact_hashes(ROOT)
        results['artifact_sha256'] = produced
        results['compared_artifacts'] = len(produced)
        results['differences'] = sorted(name for name in produced.keys() | baseline.keys() if produced.get(name) != baseline.get(name))
        results['byte_identical'] = not results['differences']
        (OUT / 'result.json').write_text(json.dumps(results, indent=2) + '\n')
        if results['differences']:
            raise SystemExit('Fresh build differs from recorded artifacts')
        print(f'Verified {len(produced)} identical artifacts in a fresh environment.', flush=True)


if __name__ == '__main__':
    main()
