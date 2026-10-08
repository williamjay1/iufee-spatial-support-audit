"""Verify original public DOI; preserve the fetched metadata under a new raw name."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,stat
import requests
ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
RAW=Path(r'F:\AcademicData\IUFEE_revision_20261005\raw\release_metadata_20261005')
RAW.mkdir(exist_ok=True)
doi='https://doi.org/10.5281/zenodo.21916290'
r=requests.get(doi,timeout=30);r.raise_for_status()
api=requests.get('https://zenodo.org/api/records/21916290',timeout=30);api.raise_for_status()
record=api.json()
assert record['metadata']['title']=='India Urban Flood Exposure Evidence (IUFEE) v1.2'
name='Zenodo_21916290_api_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
path=RAW/name
path.write_bytes(api.content);path.chmod(stat.S_IREAD)
out={'checked_utc':datetime.now(timezone.utc).isoformat(),'doi_requested':doi,
     'doi_http_status':r.status_code,'resolved_url':r.url,'api_http_status':api.status_code,
     'title':record['metadata']['title'],'public_doi_verified':True,
     'raw_metadata_path':str(path),'raw_metadata_sha256':hashlib.sha256(api.content).hexdigest(),
     'revision_outputs_published':False}
(ROOT/'results'/'public_release_verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('Original v1.2 public DOI and title verified; revision outputs remain unpublished.')
