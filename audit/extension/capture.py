"""Capture bounded clinical tables from the official Open Targets archive."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/'
TABLES = ('disease', 'clinical_indication', 'clinical_target', 'drug_mechanism_of_action')
OUT = ROOT / 'data/extensions/opentargets-26.09'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / 'capture_manifest.json'
    if manifest.exists():
        raise SystemExit('Capture exists; preserve it rather than overwrite it')
    records = []
    def capture(url, destination):
        with urlopen(url, timeout=90) as response:
            data = response.read(50_000_001)
            if len(data) > 50_000_000:
                raise ValueError('Per-file capture limit exceeded')
            headers = {key: response.headers.get(key) for key in ('ETag', 'Last-Modified', 'Content-Length')}
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        records.append({'url': url, 'path': str(destination.relative_to(ROOT)),
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'headers': headers})
        return data
    for table in TABLES:
        listing = capture(BASE + table + '/', OUT / (table + '-index.html')).decode()
        links = sorted(set(re.findall(r'href="([^"/?]+\.parquet)"', listing)))
        if not links or any(not re.fullmatch(r'[\w.-]+\.parquet', name) for name in links):
            raise ValueError('Unexpected partition listing')
        for name in links:
            capture(BASE + table + '/' + name, OUT / table / name)
        print(f'{table}: captured {len(links)} partitions', flush=True)
    manifest.write_text(json.dumps({'release': '26.09', 'release_basis': 'official release archive URL',
        'scope': list(TABLES), 'files': records,
        'excludes': ['association_overall_direct', 'association_overall_indirect', 'clinical_report']}, indent=2) + '\n')


if __name__ == '__main__':
    main()
