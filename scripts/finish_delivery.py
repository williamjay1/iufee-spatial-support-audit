"""Finalize local revision records only after full source and calculation checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
import fitz

ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
def read(name): return json.loads((ROOT/'results'/name).read_text(encoding='utf-8'))
checks={name:read(name) for name in ['glad_verification.json','joint_overlay_verification.json']}
assert all(v['all_passed'] is True for v in checks.values())
assert checks['joint_overlay_verification.json']['completed_cities']==91
assert 'v3_fresh_identity' in checks['joint_overlay_verification.json']['version']
sources=checks['joint_overlay_verification.json']['source_identity_stability_checks']
assert len(sources)==112
recoveries=read('joint_overlay_source_overrides.json')
assert len(recoveries)==9
assert all(v['recovered_sha256_matches_old_audit'] and v['original_preserved'] and v['recovered_file_readonly'] for v in recoveries.values())
stats=read('joint_overlay_aggregate_summary.json')
assert stats['completed_cities']==91 and stats['positive_cells']==1259886
map_source=read('OFFICIAL_MAP_SOURCE.json')
map_audit=read('OFFICIAL_MAP_FIGURE_AUDIT.json')
assert map_source['approval_number']=='GS(2023)2761'
assert map_audit['displayed_study_points']==91 and map_audit['all_points_in_crop'] is True
assert map_audit['registration_holdout_max_error_pt']<.02
assert map_source['eps']['readonly'] and map_source['eps_zip']['readonly']
assert map_audit['official_pdf_sha256']==map_source['vector_conversion']['output_sha256']
assert map_audit['figure_pdf_sha256']==hashlib.sha256((ROOT/'manuscript/figures/figure_1_frame.pdf').read_bytes()).hexdigest()

readme=ROOT/'README_REPRODUCE.txt'
t=readme.read_text(encoding='utf-8')
t=t.replace('matplotlib, shapely, pyproj and requests.', 'matplotlib, shapely, pyproj, requests and PyMuPDF.')
t=t.replace('python scripts/joint_overlay_baseline.py --help', 'python scripts/joint_overlay_baseline.py --scope all --recover-sources --force')
t=t.replace('The joint-overlay command and actual scope\nare recorded in its own run log/report. The --help command above only inspects its\navailable arguments; it does not imply a new analysis was executed by that line.',
'''The joint-overlay command above was actually executed for all 91 cities with forced
recomputation. It automatically reads results/joint_overlay_source_overrides.json:
nine official WSF replacement files on F were used, all byte-identical to the old
source audit. Existing E originals were never overwritten. Observed hash/read
failures were not consistently reproducible; no persistent damage cause or timing
is inferred. The final run checks initial/final file statistics and fresh hashes.
It fails rather than silently using a changed or missing source. The recovery flag
reuses matching existing read-only replacements and does not overwrite raw files.''')
t=t.replace('python scripts/build_manuscript_inputs.py\npython scripts/supplement_tables.py',
            'python scripts/build_manuscript_inputs.py\npython scripts/supplement_tables.py\npython scripts/finalize_revision.py')
t=t.replace('python scripts/plot_revision.py',
            'python scripts/prepare_official_map.py\npython scripts/fit_official_map_registration.py\npython scripts/plot_revision.py')
t+='''
Official boundary convention and map reproduction
Figure 1 uses extracted vector boundary layers from the Asia standard map from China's Ministry of Natural
Resources, GS(2023)2761. The China-India boundary uses the official Chinese
depiction. The EPS ZIP and extracted EPS are preserved read-only on F; their
official URL, hashes and conversion command are in OFFICIAL_MAP_SOURCE.json.
prepare_official_map.py checks these raw identities and regenerates a vector PDF
on D using the existing Ghostscript. Point registration is fitted to 16 official
graticule intersections, with held-out/leave-one-out checks. It is an inferred
display transformation, not a declared official CRS or geographic accuracy test.
official_boundary_layers.py extracts the original national-boundary and coastline
line/Bezier paths. plot_revision.py renders them as a clean publication map,
without printed labels, rivers, graticule or source city symbols. Boundary control
vertices are unchanged; no tracing, smoothing or basemap reprojection is used.
Reusable SVG/PDF layers and datasets/official_boundary_paths.json are supplied. The analytical FUA frame is unchanged.
The GS number identifies the parent map. The study-point overlay has not been
separately reviewed; before external publication apply the official requirements
for edited maps and the chosen venue's requirements.

Frozen interpretation of weight names
The four legacy factor choices use Product for g*s*(1-p). Old machine field names
such as joint_supported_screened and GLADJointNewPct remain for compatibility;
they denote the archived product, not the newly retained native map intersection.
The joint baseline separates J (g*t), F (same-grid marginal product) and A (archived
product). The GLAD comparison uses g and A, not J. Archived-marginal bounds must
not be assumed to bound J under a different registration convention.

Package contents
IUFEE_revision_review_package.zip contains one current manuscript PDF/source,
one supplement PDF/source, figures, scripts, derived datasets, result tables,
source/run audits, this README and the Chinese closure record. Raw parent files
remain at the stated F/E locations; local absolute paths in records support exact
reproduction and do not appear in the manuscript body. Historical failed audits
are retained explicitly as history, alongside the final passed v3 audit.
The package and manifest are created on D; no automatic long-term F/E archive or
external repository publication is performed.
'''
readme.write_text(t,encoding='utf-8')

state=ROOT/'PROJECT_STATE.md'
s=state.read_text(encoding='utf-8').replace('## Work in progress','## Completed local redevelopment')
s+='''

## Frozen delivery state

All 91 cities completed GLAD paired comparison and the forced v3 joint-preserving
overlay. Both calculation audits passed. The final overlay uses 112 source files
whose fresh initial/final identities and file statistics are stable and match the
historical audit. Nine replacement raw files were acquired on F under new names,
made read-only and verified byte-identical; E originals were not written. Earlier
identity/decode failures and successful repeat probes remain documented, without
inferring a cause or persistent physical corruption.

New J/F/A comparison: 84.434392/87.955644/90.243923 km2 allocated weight mass.
J versus F isolates joint-position loss: -4.003441% mass; city-depth Spearman
0.997722, median absolute difference 0.002265 m, maximum 0.213177 m, 42 changed
ranks, maximum shift 13, top-ten overlap 9. F versus A contains registration effects.
The revised data derivatives retain t as well as the marginal fields.

Revision delivery: GO for the explicitly limited source-representation audit.
New-submission readiness: CONDITIONAL on venue/type fit, author review and a
versioned public revision release, plus applicable edited-map review. Figure 1
now uses China's official Asia vector map, GS(2023)2761, for the China-India
boundary. All 91 study centroids are registered to the unchanged parent geometry.
The source approval belongs to the parent map, not a new derivative approval.
Independent construction dates, actual GHSL
error decomposition, WSF code-1 semantics and local hydraulic accuracy remain
unestablished. Restoring the original stronger construction/accuracy claims is
NO-GO with current evidence. No new journal is invented and no submission occurs.
'''
state.write_text(s,encoding='utf-8')

closure=ROOT/'审稿意见落实与投稿边界.txt'
c=closure.read_text(encoding='utf-8')
c=c.replace('联合筛选权重','乘积筛选权重').replace('原联合结果','原乘积结果')
c=c.replace('原联合\n指标','原乘积\n指标').replace('联合深度','乘积加权深度')
c=c.replace('GHSL0.873432m、联合1.098374m','GHSL0.873432m、乘积1.098374m')
c=c.replace('GHSL0.582127m、联合0.430524m','GHSL0.582127m、乘积0.430524m')
old='该基线的实际范围、结果、重叠处理和计算检查见JOINT_OVERLAY_REPORT。'
new='''全91城强制重算及最终来源核验已完成：地图联合J的权重质量为84.434392km2，
同细网格边际乘积F为87.955644km2，原存档乘积A为90.243923km2。J相对F
少4.003441%，说明丢弃共同位置确实改变支持配置；F相对A另少2.535660%，
该差异含注册/合并约定，不能全部归因于联合位置。J/F城市深度rho=0.997722，
绝对差中位数0.002265m、最大0.213177m（Srinagar），42城名次变动、最大
13名，最高10城重叠9城。新派生库保存t、s、p、u及coverage。
全部FUA来源覆盖完整，源类划分和兼容界最大数值误差5.96e-8。
该基线的重叠处理、完整城市结果和计算检查见JOINT_OVERLAY_REPORT及S11。'''
assert old in c
c=c.replace(old,new)
c=c.replace('先完成最终联合overlay结果和全文一致性核验，再核实拟投期刊是否接受此\n类测量/数据审计贡献、实际AI披露与数据代码要求，发布修订版复现资料。',
'''最终联合overlay、全文数值/图表一致性与来源核验已完成；接下来须按实际拟投
期刊核实其是否接受这类测量/数据审计贡献、AI披露与数据代码要求，并公开
发布修订版复现资料。当前没有选择新期刊，也没有把原Reject当成受邀重投。''')
c+='''

10. 中印边界与印度总览底图——已按中国官方底图修正
正文图1已替换为自然资源部标准地图服务的亚洲矢量底图，原图审图号
GS(2023)2761。中印边界严格采用该官方图上的边界线。原EPS转换为PDF后
提取国界与海岸线，按论文风格绘图；保留原直线/Bezier控制点及未定国界
虚线，去掉原地名、河流、经纬网和城市符号；旧geoBoundaries文件
保留但不再用于当前总览图。91个研究点通过官方经纬网配准叠加，16点拟合
最大残差0.003743pt，留出验证最大0.005133pt；这是显示配准检查，不是地理
精度证据。原始JPG、EPS压缩包和EPS全部只读，来源、SHA与转换记录齐备。
冻结的GHS-FUA研究范围和分析结果未因展示底图变化而重定义。正文图注与
参考文献已注明自然资源部来源；GS号属于原图，叠加研究点后的图件未另外
送审。外部公开发表前按标准地图服务的编辑地图规定及期刊要求办理。

11. 来源完整性事故与恢复——本轮使用源已冻结核验
处理中曾观测9个E盘WSF源的身份检查不一致，其中78_28还报LZW解码失败。
前6个原件后来复读SHA又与历史audit相同；78_28全部1,936原生block复扫
成功，类计数和扫描前后SHA均与旧记录一致。因此不能断言持续物理损坏、
损坏时间或有人修复；实际原因未知。原件从未被本任务写入、覆盖或迁移。
按旧audit从官方来源新取9份文件至F盘，只读，共62,305,843byte，每份SHA
均精确匹配旧记录。最终v3使用这些恢复文件，强制重算全部91城，逐个对112
个实际使用源进行新鲜SHA和前后stat检查；全部通过。失败历史及复读记录
保留在审计文件中。文件身份恢复不等于code1语义解释或真实地物精度验证。

交付阶段决策
限定来源表示审计的本地改稿交付：GO。已经有新实验、新结果和可复核派生
数据，而非只换措辞。重新投稿阶段：CONDITIONAL。文章不再承担真实施工
误差比例或独立城市洪水准确率主张；若作者要求恢复这些主张，当前NO-GO。
Reviewer3未提供的独立附件仍无法逐项处理，不能据此声称所有未见意见已落实。
'''
closure.write_text(c,encoding='utf-8')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

pdfs={}
for name in ['IUFEE_redeveloped','IUFEE_supplement']:
    path=ROOT/'manuscript'/f'{name}.pdf'
    doc=fitz.open(path)
    log=(ROOT/'manuscript'/f'{name}.log').read_text(encoding='utf-8',errors='replace')
    critical=[line for line in log.splitlines() if line.startswith('!') or 'Overfull' in line or 'undefined' in line.lower()]
    assert not critical,critical
    clipped=[]
    for i,page in enumerate(doc):
        for b in page.get_text('blocks'):
            if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
                clipped.append([i+1,list(b[:4])])
    assert not clipped,clipped
    pdfs[name]=dict(pages=len(doc),bytes=path.stat().st_size,sha256=sha(path),
                    critical_latex_diagnostics=critical,off_page_text_blocks=clipped)
    doc.close()
assert pdfs['IUFEE_redeveloped']['pages']==5
build=dict(completed_utc=datetime.now(timezone.utc).isoformat(),pdfs=pdfs,
    visual_review='All main pages, all supplement pages via page renders/contact sheets, and three figure layouts inspected at final size; official vector map inspected after replacement.',
           numerical_verification='GLAD full91 and fresh-identity joint v3 full91 all_passed; published original reconstruction and deterministic sensitivity recorded separately.',
           official_map=map_audit,
           readiness=dict(local_revision='GO, limited source-representation audit',new_submission='CONDITIONAL: venue fit, author review, versioned public release and applicable edited-map review',
                          original_construction_and_city_accuracy_claims='NO-GO with current evidence'))
(ROOT/'results/FINAL_BUILD_AND_READINESS.json').write_text(json.dumps(build,indent=2),encoding='utf-8')

files=[]
allowed_man={'.tex','.bib','.cls','.bst','.pdf','.png','.svg','.bbl'}
for folder in ['manuscript','scripts','results','datasets']:
    for path in sorted((ROOT/folder).rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts: continue
        if folder=='manuscript' and path.suffix not in allowed_man: continue
        if folder=='scripts' and path.suffix!='.py': continue
        files.append(path)
files += [ROOT/name for name in ['README_REPRODUCE.txt','PROJECT_STATE.md','ARTICLE_BUILD_SPEC.md','审稿意见落实与投稿边界.txt']]
manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),kind='Local review package; not submitted or publicly published',
              parent_raw_inputs='Preserved on E/F; paths and hashes recorded in source manifests, raw files not bundled',
              files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
mp=ROOT/'DELIVERY_MANIFEST.json'
mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
package=ROOT/'IUFEE_revision_review_package.zip'
with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in files+[mp]: z.write(path,path.relative_to(ROOT))
with zipfile.ZipFile(package) as z: assert z.testzip() is None
print(json.dumps(dict(main_pages=pdfs['IUFEE_redeveloped']['pages'],supplement_pages=pdfs['IUFEE_supplement']['pages'],
                      package_files=len(files)+1,package_bytes=package.stat().st_size,package_sha256=sha(package)),indent=2))
