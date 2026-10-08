"""Freeze verified revision numbers and only the references cited by the main text."""
from pathlib import Path
import json, re

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
MAN=ROOT/'manuscript'
old=Path(r'D:\codex\sci\remote_sensing_sci_novelty_audit\guangzhou_india_flood_exposure_study\grsl_submission_2026\latex\references.bib')
def entries(path):
    txt=path.read_text(encoding='utf-8')
    starts=list(re.finditer(r'@\w+\s*\{\s*([^,]+),',txt))
    out={}
    for i,m in enumerate(starts):
        segment=txt[m.start():starts[i+1].start() if i+1<len(starts) else len(txt)]
        level=0; end=None
        for j,c in enumerate(segment[segment.index('{'):],segment.index('{')):
            if c=='{': level+=1
            if c=='}':
                level-=1
                if level==0:
                    end=j+1;break
        if end is None: raise ValueError(f'Unbalanced bibliography {m.group(1)}')
        out[m.group(1).strip()]=segment[:end]
    return out
bib=entries(old)
for path in [ROOT/'results'/'LITERATURE_ADDITIONS.bib',ROOT/'results'/'LITERATURE_REPLACEMENTS.bib',ROOT/'results/revision_20261007/ADDITIONS_20261007.bib']:
    bib.update(entries(path))
bib['Zhang2025']=bib['Zhang2025'].replace('  doi     =', '  pages   = {594},\n  doi     =')
bib['GLADv2Download']=r'''@misc{GLADv2Download,
  author = {{Global Land Analysis and Discovery, University of Maryland}},
  title = {{GLCLU 2000--2020}, version 2: land-cover and land-use download},
  howpublished = {Dataset documentation},
  url = {https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/download.html},
  note = {2015 and 2020 layers; accessed 2026-10-05}
}'''
bib['MNRStandardAsia2023']=r'''@misc{MNRStandardAsia2023,
  author = {{Ministry of Natural Resources of China}},
  title = {Asia standard map: {GS(2023)2761}},
  year = {2023},
  howpublished = {Standard Map Service; 1:25 million, four-format white base},
  url = {https://bzdt.ch.mnr.gov.cn/browse.html?picId=\%224o28b0625501ad13015501ad2bfc2193\%22},
  note = {Official vector parent map; accessed 2026-10-05}
}'''
text=(MAN/'IUFEE_redeveloped.tex').read_text(encoding='utf-8')
keys=[]
for group in re.findall(r'\\cite\{([^}]+)\}',text):
    for key in group.split(','):
        if key not in keys: keys.append(key)
assert set(keys)<=set(bib),set(keys)-set(bib)
(MAN/'references.bib').write_text('\n\n'.join(bib[k] for k in keys)+'\n',encoding='utf-8')
a=json.loads((ROOT/'results'/'glad_aggregate_summary.json').read_text())
v=json.loads((ROOT/'results'/'glad_verification.json').read_text())
assert a['completed_cities']==a['expected_cities']==91
assert a['formula_version']=='GLADpair_v2_joint_s_endpoint_support'
assert a['positive_cells']==1259886
assert abs(a['ghsl_added_surface_m2']-400535818)<.01
assert abs(a['joint_screened_surface_m2']-90243923.12804441)<.01
assert v['all_passed'] is True
mapping={'GLADNewPct':100*a['g_covered_new_built_fraction'],
         'GLADStablePct':100*a['g_covered_stable_built_fraction'],
         'GLADAbsentPct':100*a['g_covered_absent_both_fraction'],
         'GLADLossPct':100*a['g_covered_built_loss_fraction'],
         'GLADJointNewPct':100*a['joint_covered_new_built_fraction'],
         'GLADCoveragePct':100*a['pair_coverage_g_weighted']}
lines=['% Generated from verified complete 91-city comparison; do not hand-edit.']
for key,value in mapping.items():
    digits=4 if key=='GLADLossPct' else 2
    lines.append('\\newcommand{\\'+key+'}{'+f'{value:.{digits}f}'+'}')
lines.append(r'\newcommand{\ComparisonCities}{91}')
(MAN/'revision_numbers.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Generated {len(keys)} verified bibliography entries and final 91-city macros.')
