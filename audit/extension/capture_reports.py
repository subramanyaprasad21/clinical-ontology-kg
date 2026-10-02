"""Capture clinical-report bodies separately from the existing input receipt."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/clinical_report/'
OUT = ROOT / 'data/extensions/opentargets-26.09/clinical-report-capture'
LIMIT = 150_000_000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = OUT / 'capture_manifest.json'
    if receipt.exists():
        raise SystemExit('Capture already complete; do not overwrite its receipt')
    files = []
    total = 0
    def capture(name):
        nonlocal total
        destination = OUT / name
        temporary = destination.with_suffix(destination.suffix + '.partial')
        url = BASE + ('' if name == 'index.html' else name)
        count = 0; digest = hashlib.sha256()
        with urlopen(url, timeout=120) as response, temporary.open('wb') as output:
            headers = {k: response.headers.get(k) for k in ('ETag','Last-Modified','Content-Length')}
            if headers['Content-Length'] and total + int(headers['Content-Length']) > LIMIT:
                raise ValueError('Capture size budget exceeded')
            while chunk := response.read(1024 * 1024):
                count += len(chunk); total += len(chunk)
                if total > LIMIT: raise ValueError('Capture size budget exceeded')
                digest.update(chunk); output.write(chunk)
        if headers['Content-Length'] and count != int(headers['Content-Length']):
            raise ValueError('Incomplete HTTP response')
        temporary.replace(destination)
        files.append({'url': url, 'path': str(destination.relative_to(ROOT)), 'bytes': count,
                      'sha256': digest.hexdigest(), 'headers': headers,
                      'retrieved_at': datetime.now(timezone.utc).isoformat()})
    capture('index.html')
    names = sorted(set(re.findall(r'href="([\w.-]+\.parquet)"', (OUT/'index.html').read_text())))
    if not names: raise ValueError('No listed Parquet partitions')
    for name in names:
        capture(name); print(f'Captured {name}',flush=True)
    receipt.write_text(json.dumps({'release':'26.09','table':'clinical_report','files':files,
                                  'release_basis':'official release archive URL'},indent=2)+'\n')


if __name__ == '__main__': main()
