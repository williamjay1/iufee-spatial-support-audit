"""Acquire the official MNR standard Asia map verified from its detail-page DOM."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,shutil,stat
import requests

raw=Path(r'F:\AcademicData\IUFEE_revision_20261005\raw\MNR_standard_map_20261005')
spaces={d:shutil.disk_usage(d).free for d in ['F:\\','E:\\']}
assert spaces['F:\\']>50000000
raw.mkdir(exist_ok=True)
url='https://bzdt-sbsm.obs.cn-north-4.myhuaweicloud.com/prototype/4/4o28b0625501ad13015501ad2bfc2193.jpg'
path=raw/'MNR_Asia_GS2023_2761_20261005.jpg'
if not path.exists():
    with requests.get(url,stream=True,timeout=60) as r:
        r.raise_for_status()
        headers={k:r.headers.get(k) for k in ['Content-Type','Content-Length','ETag','Last-Modified']}
        with path.open('xb') as stream:
            for chunk in r.iter_content(1<<20): stream.write(chunk)
    os.chmod(path,stat.S_IREAD)
else:
    raise RuntimeError('Raw path already exists; preserve and use a new version.')
assert path.stat().st_size==14177765
record=dict(source_url=url,official_detail_url='https://bzdt.ch.mnr.gov.cn/browse.html?picId=%224o28b0625501ad13015501ad2bfc2193%22',
            source_authority='Ministry of Natural Resources, China; Standard Map Service',
            approval_number='GS(2023)2761',title='Asia, white base, 1:25 million, 4-format',
            downloaded_utc=datetime.now(timezone.utc).isoformat(),raw_path=str(path),bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),http_headers=headers,space_check_free_bytes=spaces,
            boundary_instruction='Use Chinese official standard-map depiction for the China-India boundary; do not redraw an approximate boundary.',
            approval_scope='Existing approval identifies the parent standard map; derivative research overlays are not claimed independently approved.')
out=Path(r'D:\MLWork\IUFEE_revision_20261005\results\OFFICIAL_MAP_SOURCE.json')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
