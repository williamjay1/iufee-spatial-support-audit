"""Record the completed map and manuscript visual review, without rerunning science."""
from pathlib import Path
import json, hashlib

R=Path(r'D:\MLWork\IUFEE_revision_20261005')
O=R/'results/revision_20261008'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

correction=json.loads((O/'KASHMIR_MAP_CORRECTION.json').read_text(encoding='utf-8'))
assert correction['all_passed']
assert correction['main_pdf_after_sha256']==sha(R/'manuscript/IUFEE_redeveloped.pdf')
assert correction['figure_pdf_sha256']==sha(R/'manuscript/figures/figure_1_frame.pdf')
citation=json.loads((O/'CITATION_CHECK_AFTER_MAP.json').read_text(encoding='utf-8'))
assert citation['all_passed'] and citation['main_pdf_sha256']==correction['main_pdf_after_sha256']
correction['visual_review']='PASS: root inspected the official Kashmir crop, current whole-figure preview and all five recompiled main pages. Delhi, Sultanpur and Kashmir region are in left white space; Guwahati and China are in right white space, with transparent labels and longer leaders. Every actual PDF word boundary clears the map frame by at least 2 pt. Regional dashes and original ceasefire cross symbols remain distinct; no text overlap, clipping or leader crossing through words observed.'
correction['figure_preview_sha256']=sha(R/'temp/figures_20261008/figure_1_frame_preview.png')
correction['main_page_render_sha256']={str(i):sha(R/f'temp/render_20261008/IUFEE_redeveloped_page{i}.png') for i in range(1,6)}
oldbuild=json.loads((R/'results/FINAL_BUILD_AND_READINESS.json').read_text(encoding='utf-8'))
unchanged=['IUFEE_supplement','Cover_letter_GRSL','Revision_memorandum','IUFEE_technical_record']
assert all(sha(R/f'manuscript/{stem}.pdf')==oldbuild['pdfs'][stem]['sha256'] for stem in unchanged)
correction['other_four_pdfs_unchanged']=True
(O/'KASHMIR_MAP_CORRECTION.json').write_text(json.dumps(correction,indent=2),encoding='utf-8')

qa=json.loads((O/'FIGURE_DESIGN_AND_QA.json').read_text(encoding='utf-8'))
qa['visual_inspection']['figure_1_frame'].update(
    actual_preview_opened=True,preview_sha256=correction['figure_preview_sha256'],
    status='PASS after external-label correction: root, figure agent and independent auditor inspected current figure; all five labels are in white space with transparent backgrounds and longer leaders',
    compiled_placement_owner='root; all five recompiled main pages inspected')
(O/'FIGURE_DESIGN_AND_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')

path=O/'FIGURE_DESIGN_AND_QA.md'
text=path.read_text(encoding='utf-8')
addition='''
<!-- KASHMIR_VISUAL_REVIEW_20261008 -->
## Kashmir correction: completed placement review

The root agent inspected the official cropped Kashmir source, the corrected Figure 1 preview, and all five recompiled main pages. The Kashmir region label and its leader are outside the dense city cluster. The regional dashed sample and ceasefire crossed sample match their respective official map symbols. No clipping, text overlap, or leader crossing through words was observed. The one caption addition identifies these restored source geometries; all other manuscript text is exactly unchanged. Main page count remains five, and the four other PDFs are byte-identical to the earlier completed delivery. The original three geographic layers passed a separate read-only audit. See KASHMIR_MAP_CORRECTION.json and CITATION_CHECK_AFTER_MAP.json for the current-file checks.
'''
if '<!-- KASHMIR_VISUAL_REVIEW_20261008 -->' not in text:
    path.write_text(text+addition,encoding='utf-8')

text=path.read_text(encoding='utf-8')
addition='''
<!-- MAP_LABEL_WHITE_SPACE_20261008 -->
## External labels and longer leaders

Delhi, Sultanpur and Kashmir region are placed in the left white margin; Guwahati and China are in the right white margin. Labels have transparent backgrounds and therefore do not mask geography. Every rendered text box is 2.5 pt outside the map frame, also verified against actual PDF word coordinates (all gaps at least 2 pt). Leader lengths are 24.04 to 51.87 pt and no leader intersects another text box. The source-period panel was repositioned to preserve white space, with its fields and data unchanged. All five recompiled main pages were visually inspected, and a separate read-only auditor checked the current main-page figure. Main TEX is byte-identical to the pre-label-adjustment backup; map geometry, 91 registered study points, scientific fields and other four figures are unchanged.
'''
if '<!-- MAP_LABEL_WHITE_SPACE_20261008 -->' not in text:
    path.write_text(text+addition,encoding='utf-8')

path=R/'PROJECT_STATE.md'
text=path.read_text(encoding='utf-8')
addition='The current Figure 1 restores the official Kashmir regional boundary and ceasefire symbols as separate layers and labels Kashmir region. All land fill is neutral; 91 study points and the original national/coast geometry are unchanged. Main caption and local package were updated; the only new manuscript prose is the cartographic clarification. See results/revision_20261008/KASHMIR_MAP_CORRECTION.json.'
marker='The current sources are canonical.'
if addition not in text:
    text=text.replace(marker,addition+'\n\n'+marker,1)
    path.write_text(text,encoding='utf-8')
path=R/'results/FINAL_SCIENTIFIC_AUDIT.md'
text=path.read_text(encoding='utf-8')
addition='2026-10-08 map correction: the omitted official Kashmir regional boundary and ceasefire symbols have been restored as independent layers; Kashmir region is labelled, land fill is neutral, and all 91 points remain unchanged. The original national, coastline and land path records are exactly unchanged. Only a figure-caption clarification was added; the scientific results and other four PDF documents are unchanged. Current figure, main PDF and package identities supersede the earlier rendering identities.'
marker='当前审计见 revision_20261008/DELIVERY_AUDIT.md 与 PRESENTATION_AUDIT.json。'
if addition not in text:
    text=text.replace(marker,addition+'\n\n'+marker,1)
    path.write_text(text,encoding='utf-8')
print('Map visual review and current rendering records completed.')
