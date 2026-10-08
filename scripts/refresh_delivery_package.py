"""Refresh current build metadata and package without appending duplicate records."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,zipfile
import fitz

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
assert shutil.disk_usage('D:\\').free>1000000000
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

build_path=ROOT/'results/FINAL_BUILD_AND_READINESS.json'
build=json.loads(build_path.read_text(encoding='utf-8'))
build['completed_utc']=datetime.now(timezone.utc).isoformat()
for stem in ['IUFEE_redeveloped','IUFEE_supplement','Cover_letter_GRSL','Revision_memorandum','IUFEE_technical_record']:
    path=ROOT/'manuscript'/f'{stem}.pdf'
    log=(path.with_suffix('.log')).read_text(encoding='utf-8',errors='replace')
    critical=[line for line in log.splitlines() if line.startswith('!') or 'Overfull' in line or 'undefined' in line.lower()]
    assert not critical,critical
    with fitz.open(path) as doc:
        clipped=[]
        for i,page in enumerate(doc):
            for b in page.get_text('blocks'):
                if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
                    clipped.append([i+1,list(b[:4])])
        assert not clipped,clipped
        build['pdfs'][stem]=dict(pages=len(doc),bytes=path.stat().st_size,sha256=sha(path),
             critical_latex_diagnostics=critical,off_page_text_blocks=clipped)
assert build['pdfs']['IUFEE_redeveloped']['pages']==5
assert 2<=build['pdfs']['IUFEE_supplement']['pages']<=3
assert build['pdfs']['Cover_letter_GRSL']['pages']==1
diagnostics=json.loads((ROOT/'results/revision_20261007/diagnostics_summary.json').read_text(encoding='utf-8'))
assert diagnostics['verification']['all_passed'] and diagnostics['verification']['cells']==1259886
assert diagnostics['verification']['cities']==91
build['diagnostics_20261007']=diagnostics['verification']
build['article_format']='GRSL Letter: five pages including references; three page noncore supplement'
build['target_journal']='IEEE Geoscience and Remote Sensing Letters (user selected 2026-10-08)'
build['editorial_eligibility']='Previous Reject supplies no resubmission invitation; unsent cover letter requests an editorial eligibility judgment.'
presentation=json.loads((ROOT/'results/revision_20261008/PRESENTATION_AUDIT.json').read_text(encoding='utf-8'))
assert presentation['all_passed']
build['presentation_20261008']=presentation
assert 'Pending' not in presentation['visual_review']
build['readiness']={
    'local_revision':'GO: verified, bounded measurement-audit GRSL Letter and local submission materials completed',
    'new_submission':'CONDITIONAL: target and presentation rules checked; editorial eligibility after prior Reject and author review remain required; nothing sent or uploaded',
    'original_construction_and_city_accuracy_claims':'Unsupported with current evidence; not claimed in the revised article'
}
map_audit=json.loads((ROOT/'results/OFFICIAL_MAP_FIGURE_AUDIT.json').read_text(encoding='utf-8'))
assert map_audit['displayed_study_points']==91 and map_audit['all_points_in_crop']
assert map_audit['figure_pdf_sha256']==sha(ROOT/'manuscript/figures/figure_1_frame.pdf')
with fitz.open(ROOT/'manuscript/figures/figure_1_frame.pdf') as doc:
    assert len(doc[0].get_images())==0
build['official_map']=map_audit
build['visual_review']='All five Letter pages, three supplement pages and one cover letter page inspected at final layout. Memorandum contact sheets and changed extended technical record figures reviewed. Nature style figures passed font, vector and text collision checks with 1000 dpi PNG exports; exact Chinese official boundary vertices and all 91 points remain verified.'
build_path.write_text(json.dumps(build,indent=2),encoding='utf-8')

files=[]
allowed_man={'.tex','.bib','.cls','.bst','.pdf','.png','.svg','.bbl'}
for folder in ['manuscript','scripts','results','datasets','submission']:
    for path in sorted((ROOT/folder).rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts: continue
        if folder=='manuscript' and path.suffix not in allowed_man: continue
        if folder=='scripts' and path.suffix!='.py': continue
        files.append(path)
files += [ROOT/name for name in ['README_REPRODUCE.txt','PROJECT_STATE.md','ARTICLE_BUILD_SPEC.md','审稿意见落实与投稿边界.txt']]
manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),kind='Current local review package; not submitted or publicly published',
    parent_raw_inputs='Preserved on E/F; paths and hashes recorded, raw files not bundled',
    files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
mp=ROOT/'DELIVERY_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
package=ROOT/'IUFEE_revision_review_package.zip'
temporary=ROOT/'temp/IUFEE_package_refresh.zip'
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in files+[mp]: z.write(path,path.relative_to(ROOT))
with zipfile.ZipFile(temporary) as z: assert z.testzip() is None
temporary.replace(package)
print(json.dumps(dict(main_pages=build['pdfs']['IUFEE_redeveloped']['pages'],
    supplement_pages=build['pdfs']['IUFEE_supplement']['pages'],package_files=len(files)+1,
    package_bytes=package.stat().st_size,package_sha256=sha(package)),indent=2))
