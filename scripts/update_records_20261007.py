"""Synchronize the current delivery records; historical run audits stay intact."""
from pathlib import Path
import json
R=Path(r'D:\MLWork\IUFEE_revision_20261005')
(R/'PROJECT_STATE.md').write_text('''# IUFEE substantive redevelopment — current state

Updated 2026-10-07 (Asia/Shanghai). Original decision: Reject, GRSL-02356-2026, dated 2026-10-04. The user requested substantive redevelopment to the best attainable standard for a new submission. No invitation to revise the existing submission is presumed; no external submission, publication, email or message to reviewers has occurred.

## Current article and contribution

Title: Spatial Support Assumptions in Urban Change Exposure: An Audit of 91 Indian Cities.

Type: complete research article; remote sensing measurement and source-representation audit. The earlier five-page Letter constraint is superseded. The main article now carries definitions, controlled J/F/A comparison, covariance and centered-contribution explanation, nonzero-support/conditional-depth decomposition, full-frame GLAD evidence, sensitivities and three executed applications. Causal identification and prediction benchmarks are inapplicable to this claim.

Contribution: a controlled experiment quantifies and locates the effect of replacing joint map support with marginal fractions, distinguishes that effect from registration, and retains joint derivatives and cell dossiers for reproducible source review.

## Verified evidence

- All 91 FUAs, 1,259,886 positive GHSL cells and 400.535818 km2 within-product surface difference are retained.
- Final native overlay v3 passed all-city geometry, class, coverage and source-identity checks. All 112 used sources match the historical identities; nine separately recovered official inputs on F remain read-only. Historical transient identity/decode failures remain documented without attributing their cause.
- J/F/A pooled allocation: 84.434392 / 87.955644 / 90.243923 km2. Controlled J-F support difference: -4.003441%; median absolute city-depth difference 0.002265 m; maximum 0.213177 m; rho 0.997722.
- New full-frame diagnostics align every J/GLAD cell key, g, h and center exactly. No missing GLAD pairs. Maximum symmetric identity residual 2.78e-16 m.
- Pooled J-F depth change -0.000591694 m conceals +0.010665820 and -0.011257513 m centered contributions: 97.3011% cancellation.
- At equal top-1% cell budget, representation-effect and standard gh queues cover different targets and overlap by 28.2483%. No review-efficiency or accuracy gain is inferred.
- J allocates 19.1560% of its mass to GLAD-new class, while retaining only 27.4329% of G allocation in that class. Composition and absolute retention are distinguished.
- W, nonzero-model-support share C, conditional depth D+ and E=C D+ are retained for G/J/F/A. Six J/F conditional means remain undefined because W+=0; G has four such cities.
- Three original cities remain Delhi, Guwahati and Sultanpur. Six actual cell dossiers are exported with coordinates, source states, seven RP depths and QA flags. Srinagar/Nashik are explicitly additional post hoc mechanism examples.

## Map requirement completed

The user requires China's official national-boundary geometry in a clean programmable research map. Figure 1 uses exact national/coastal line and Bezier paths from the Ministry of Natural Resources Asia standard map GS(2023)2761. It does not embed the printed basemap. All 91 points are placed by the verified display transformation. Reusable SVG/PDF and PDF-plane path JSON are supplied. Parent geometry is unchanged; no inferred official GIS CRS or new derivative approval is claimed.

## Boundaries and readiness

Content redevelopment: GO for the explicitly bounded measurement-audit article after independent conceptual and numerical checks. The original stronger claims of verified construction, an error-corrected 400.536 km2, known WSF code-1 meaning or validated local hydraulics remain unsupported. Cross-product comparison is complete; independent accuracy validation is not.

New-submission preparation still requires an actual target journal, its article and data/code requirements, and author review. Revised outputs are locally supplied but not yet released publicly under a new version. The parent map approval is not a separate approval of this derivative. No acceptance guarantee is made.

The supplied PDF has no annotations; Reviewer 3's separate attachment was not provided. Visible comments are all mapped in Revision_memorandum.tex/pdf (22 grouped items), but unseen attachment comments cannot be claimed addressed.

## Storage and canonical files

Original manuscript remains unchanged under D:/codex/sci/remote_sensing_sci_novelty_audit/guangzhou_india_flood_exposure_study/grsl_submission_2026/latex. Existing raw data on E are read-only inputs. New raw sources reside under F:/AcademicData/IUFEE_revision_20261005/raw. All scripts, derivatives, calculations and current manuscript outputs are under D:/MLWork/IUFEE_revision_20261005. No original material was overwritten, migrated or cleaned. Long-term archival remains the user's task.

Current deliverables: manuscript/IUFEE_redeveloped.pdf and .tex; IUFEE_supplement.pdf and .tex; Revision_memorandum.pdf and .tex; one refreshed IUFEE_revision_review_package.zip. Old main draft snapshots remain only in excluded temp/. Use README_REPRODUCE.txt for the updated execution order. Current audit conclusions are in results/revision_20261007; older reports record their historical stages.
''',encoding='utf-8')
(R/'README_REPRODUCE.txt').write_text('''IUFEE complete-article redevelopment — current reproduction record
Updated 2026-10-07. Original GRSL-02356-2026 decision was Reject.

CURRENT ARTIFACTS
manuscript/IUFEE_redeveloped.tex/pdf: complete research article.
manuscript/IUFEE_supplement.tex/pdf: S1–S12, complete methods and result tables.
manuscript/Revision_memorandum.tex/pdf: 22 grouped visible editorial/reviewer points.
The current main article supersedes the former five-page Letter. The new title is
Spatial Support Assumptions in Urban Change Exposure: An Audit of 91 Indian Cities.
The package is local and reviewable; no new submission or public release occurred.

PURPOSE AND SCOPE
Quantify the effect of replacing joint WSF support with marginal fractions while
holding maps, grid, merge convention, g and h fixed. Separate J-F from F-A;
report numerator, denominator, nonzero-model-support share and conditional depth.
GHSL positive differences are not confirmed construction. GLAD agreement is not
independent accuracy. The old AI-assisted labels are excluded as reference truth.

INPUTS PRESERVED
1. Original IUFEE v1.2, DOI 10.5281/zenodo.21916290, supplies the 91 cell tables.
2. Existing GHSL/WSF/GloFAS: E:/science/India_Flood_Remote_Sensing_IEEE/data.
3. New GLAD native windows and nine recovered WSF sources:
   F:/AcademicData/IUFEE_revision_20261005/raw, immutable new filenames.
4. MNR Asia map GS(2023)2761 official EPS/JPG/ZIP are immutable in the same F raw
   tree. Official URLs, hashes, conversion and exact-layer extraction are recorded.
5. Original manuscript remains under D:/codex/sci/remote_sensing_sci_novelty_audit/
   guangzhou_india_flood_exposure_study/grsl_submission_2026/latex.
All working outputs stay under D:/MLWork/IUFEE_revision_20261005. Do not migrate,
overwrite or delete E/F originals. This package excludes raw source rasters and temp.

RUNTIMES
Analysis Python:
C:/Users/Administrator/AppData/Local/Programs/Python/Python312/python.exe
Packages: numpy, pandas, pyarrow, rasterio, scipy, matplotlib, shapely, pyproj,
requests, PyMuPDF, Pillow. Exact used versions are retained in execution records.
New diagnostic figures use the existing dedicated runtime:
C:/Users/Administrator/.dsh/venvs/scifig/Scripts/python.exe
and figstyle.py from C:/Users/Administrator/.agents/skills/sci-figures.
The fallback is to install the declared scientific dependencies on a separate
reproduction machine and adapt the path constants explicitly; never silently move
this machine's computation to C, E or F.

ANALYSIS REPRODUCTION ORDER
From the project directory, with the analysis Python unless otherwise indicated:
  scripts/revision_sensitivity.py
  scripts/glad_cross_product.py --scope all --workers 2
  scripts/wsf_code1_forensics.py
  scripts/joint_overlay_baseline.py --scope all --recover-sources --force
  scripts/representation_diagnostics_20261007.py
  scripts/case_dossiers_20261007.py
The final native overlay was actually forced for all 91 cities. Source overrides
point to nine verified read-only official replacements; no E original is changed.
The program checks initial/final source identities and fails on changed input.
No new raw inputs were needed for the October 7 diagnostics.

MAP AND FIGURE REPRODUCTION
  scripts/prepare_official_map.py
  scripts/fit_official_map_registration.py
  scripts/plot_revision.py
  scripts/plot_diagnostics_20261007.py  [dedicated scifig Python]
Figure 1 extracts official boundary/coastal line and Bezier paths, preserving all
control vertices. Source labels/rivers/graticule/city glyphs are excluded. The
graticule fit is an inferred display transformation, not an official GIS CRS or
independent geographic-accuracy claim. Exact vectors are supplied as PDF/SVG/JSON.
New scientific plots are PDF and editable SVG with 900 dpi PNG backups.

CURRENT MANUSCRIPT BUILD
The saved .tex files are the canonical editable sources; compile them directly.
The original article source remains openable in the Codex panel. The built-in
compiler could not locate its standard directories on this platform, so existing
local MiKTeX compiled all three documents successfully. No TeX installation added.
  scripts/compile_revision_20261007.py
  scripts/render_final_pdfs.py

For exact regeneration of the current assembled article and S12 (not needed when
merely compiling the saved sources), run:
  scripts/write_full_article_20261007.py
  scripts/build_manuscript_inputs.py
  scripts/extend_supplement_20261007.py
  scripts/compile_revision_20261007.py
The article writer preserves the original author header in its source; the saved
delivered .tex can also be compiled directly without running any assembly script.
The current bibliography generator includes ADDITIONS_20261007.bib. Core data
macros require complete GLAD verification and reject incomplete runs.
Legacy supplement_tables.py/finalize_revision.py/finish_delivery.py describe the
earlier redevelopment assembly; do not run them over the current finished sources.
They are retained for provenance, not as the current manuscript build entrypoint.

VALIDATION AND DELIVERY
Current numerical and conceptual audits are in results/revision_20261007.
Synthetic optimizer checks verify computation only. Joined cell identities and
math identities do not establish source accuracy. Six J/F cities have W+=0;
their conditional means are missing, while E is zero with positive W.
Archived s,p bounds condition on a common normalized measure. Fine-grid J/F
defines that measure explicitly. Archived bounds need not cover a differently
registered J. Legacy field names containing joint_screened refer to A, not J.

After source changes, compile, inspect rendered pages, then run
scripts/refresh_delivery_package.py. It checks LaTeX diagnostics, page text bounds,
official figure identity, current diagnostics and creates DELIVERY_MANIFEST.json
and one verified ZIP. It does not submit, publish or archive to E/F.
Original raw source licenses apply. Before an actual new submission, confirm the
chosen venue's article, data/code and map requirements. Reviewer 3's separately
mentioned attachment was unavailable; only visible comments were addressed.
''',encoding='utf-8')
(R/'审稿意见落实与投稿边界.txt').write_text('''IUFEE 拒稿后实质重构——2026-10-07 当前交付说明

本轮按“解决实质问题、达到当前资料下最佳可实现水平”的要求，已经从五页
短文重构成完整研究论文。新标题为 Spatial Support Assumptions in Urban
Change Exposure: An Audit of 91 Indian Cities。文章主线是遥感来源与空间
表示审计。当前正文能够独立呈现核心方法、受控比较和应用证据。

一、真正新增的分析
1. 在全部91城、1,259,886个正差格网上，将联合叠加J、同细网格边际乘积F、
   原存档乘积A及GLAD逐键对齐，g、h、中心坐标全部一致，无GLAD缺失配对。
2. 用t−s(1−p)=−Cov(S,P)及精确的城市中心化分解解释J−F。全国平均差只有
   −0.000592m，但正贡献0.010666m和负贡献−0.011258m抵消了97.3%。正文现在
   显示全部91城差异，而不是用高相关掩盖局部差异。
3. 把城市指标拆为W、N、非零模型深度支持比例C、条件深度D+和E=C×D+。
   六城在J/F下没有非零深度支持，D+保持未定义，不伪造为零；G下为四城。
4. GLAD新增J/F/A配对结果，并同时报告类别组成和绝对保留率：J的new类别
   组成19.16%，但只保留G中对应new类别分配量的27.43%。不能把组成份额
   上升写成精度提高。J的new绝对分配16.1743km²，低于F的16.4009km²。
5. 原三案例扩展为实际执行的来源审查。六格档案包括经纬度、g/h、archive
   与fine边际、真正joint、GLAD配对、全部RP与QA。Guwahati一格sF=.13、
   pF=.41，边际乘积=.0767而joint=0，同时永久水体QA=1，RP50到RP75下降
   .128m。这是可复查的具体来源诊断，不是虚构人工判读。
6. 等量top1%队列对照：表示效应队列覆盖56.28%绝对效应、21.00%原gh分子；
   原gh队列覆盖34.26%效应、61.91%gh分子，重叠28.25%。明确两者任务不同，
   不声称已有实证证明工作效率提升。

二、审稿核心意见如何落实
贡献薄弱/普通叠加：补齐受控J−F基线、区别F−A的注册效应、空间机制和
真实cell输出；承认Fréchet界和分式优化是经典工具，不包装公式首创。
时间错位与400.536km²：主张改为GHSL模型化时期差分；补全GLAD跨产品
比较，仍不将其当实际施工或误差校正量。
权重任意：四权重明确为因素诊断，保留16指数、3阈值、兼容区间与零分母。
code1与Evolution零：保留原生读取/重复核验/赋值界，零值不解释成确认无
聚落；未知编码真实含义尚未得到数据提供方解释。
GloFAS尺度/指标：区分水力输出和水文强迫，展开梯形节点权重、W/N/C/D+
含义，保留7RP、注册、QA和非单调敏感性；不夸大为局地水力验证。
独立或跨产品评估：全91城GLAD已执行，满足审稿信列明的cross-product
assessment路径。独立施工参考真值尚无，旧AI/模型转移标签完全排除。
应用与地图：三个原案例保留，新增具体cell档案和队列覆盖。地图国界沿用
中国自然资源部官方GS(2023)2761原始矢量路径，干净重绘，而非贴整张底图。
文献与格式：17条直接相关已核验引用，含2026近邻文献与经典方法归属；
完整方法/结果/讨论，四图四表，图注解释单位、基线与条件。

三、交付与判定
内容层面：GO，可用于新投稿准备的完整测量审计稿。独立数字与内容审查
通过后刷新最终包。主文、补充S1–S12、英文逐点修订备忘及代码/结果统一。
英文Revision memorandum覆盖22组可见AE/R1/R2/R3意见。R3另附文件没有
提供，不能声称逐条处理了看不到的附件。
真正投稿前仍需落实目标期刊、其文章/数据代码要求、作者审阅与适用地图
要求；新修订输出尚未发布到公开版本库。本次没有外部投稿或自动归档。
现有证据不支持恢复“已验证施工量、精确本地洪水风险、已知code1语义”
等强主张。剩余限制在正文中明确，不以无限增加无关实验拖延本路线交付。

当前文件位于D:/MLWork/IUFEE_revision_20261005/manuscript。
完整复现包为根目录IUFEE_revision_review_package.zip，旧原稿和E/F原材料
均保留原样。所有本轮计算与工作输出写D盘，长期归档由用户手动处理。
''',encoding='utf-8')
buildp=R/'results/FINAL_BUILD_AND_READINESS.json';b=json.loads(buildp.read_text())
b['numerical_verification']='Full91 GLAD and native v3 passed; Oct7 exact aligned 1,259,886-cell diagnostics and six dossiers passed; actual numbers/formulas independently reviewed.'
b['readiness']={'local_revision':'GO, complete article with bounded source-representation claims','new_submission':'Target journal, applicable article/data-code/map requirements and author review remain to be finalized; no submission or new public release performed','original_construction_and_city_accuracy_claims':'Unsupported with current evidence'}
buildp.write_text(json.dumps(b,indent=2),encoding='utf-8')
print('Current state, reproduction guide and Chinese closure record synchronized.')
