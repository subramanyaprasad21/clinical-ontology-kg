"""Check the review export with locally installed Protégé libraries, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--protege-contents', type=Path, required=True)
parser.add_argument('--java-home', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('reports/owl_compatibility.json'))
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
base = args.protege_contents.resolve()
hermit = list((base / 'plugins').glob('org.semanticweb.hermit-*.jar'))
if len(hermit) != 1:
    raise SystemExit('Expected exactly one HermiT plugin')
owlapi = base / 'bundles/owlapi-osgidistribution.jar'
with tempfile.TemporaryDirectory(prefix='kg-owl-') as tmp:
    folder = Path(tmp)
    jars = sorted((base / 'bundles').glob('*.jar')) + hermit
    libraries = {}
    for index, jar in enumerate((owlapi, hermit[0])):
        with zipfile.ZipFile(jar) as archive:
            libraries[jar.name] = {
                'sha256': hashlib.sha256(jar.read_bytes()).hexdigest(),
                'manifest': archive.read('META-INF/MANIFEST.MF').decode(),
            }
            for number, name in enumerate(archive.namelist()):
                if name.endswith('.jar'):
                    destination = folder / f'{index}-{number}.jar'
                    destination.write_bytes(archive.read(name))
                    jars.append(destination)
    cp = ':'.join(map(str, jars + [folder]))
    subprocess.run([str(args.java_home / 'bin/javac'), '-cp', cp, '-d', tmp,
                    str(root / 'audit/owl/CheckOntology.java')], check=True)
    results = {}
    for relative in ('ontology/core/core.ttl', 'data/processed/review.ttl'):
        run = subprocess.run([str(args.java_home / 'bin/java'), '-cp', cp,
                              'CheckOntology', str(root / relative)], capture_output=True, text=True, check=True)
        rows = [line.removeprefix('RESULT_JSON=') for line in run.stdout.splitlines() if line.startswith('RESULT_JSON=')]
        if len(rows) != 1:
            raise RuntimeError(run.stdout + run.stderr)
        results[relative] = json.loads(rows[0])
        results[relative]['sha256'] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'libraries': libraries, 'results': results}, indent=2) + '\n')
    review = results['data/processed/review.ttl']
    for check in ('consistent', 't2dm_annotation_class_entailed', 'inverse_entailed'):
        if review.get(check) is not True:
            raise SystemExit(f'FAILED: {check}; inspect {args.output}')
    print(f'PASS: consistency, existential classification, inverse; {len(review["dl_profile_violations"])} DL profile violations retained.')
