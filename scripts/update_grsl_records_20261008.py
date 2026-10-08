"""Align review records with the GRSL Letter and keep dated technical evidence."""
from pathlib import Path
import re,json
R=Path(r'D:\MLWork\IUFEE_revision_20261005'); M=R/'manuscript'
baseline=R/'temp/baseline_20261007'
s=(baseline/'Revision_memorandum.tex').read_text(encoding='utf-8')
s=s.replace('7 October 2026','8 October 2026')
s=s.replace('uses a full Article format','uses a five page Letter format')
s=s.replace('uses a full Article structure','uses a focused Letter structure')
s=s.replace('the full Article organization','the focused Letter organization')
s=s.replace('full Article','Letter').replace('main Article','main Letter').replace('Article placement','Letter placement').replace('Article location','Letter location')
old='The main-text structure is I~Introduction; II~Data and Scope; III~Methods; IV~Results; V~Application Examples; VI~Discussion; and VII~Conclusion. The section references below identify these actual sections; final pagination is checked separately. Supplementary Sections S1--S10 retain the archived definitions, sensitivity results and verification details, S11 records the completed joint overlay, and S12 reports the spatial diagnostics and six executed cell dossiers. The main text now carries the definitions and evidence needed to evaluate the central contribution.'
new='The Letter contains Introduction, Data and Methods, Results, Discussion, and Conclusion. The main text retains the controlled experiment, quantitative evidence, source definitions, depth components and concrete city interpretation. The journal supplement contains three pages of additional checks, sensitivity settings, selected cells and city summaries. In this memorandum, references to the earlier S1 through S12 denote the Extended Technical Record, supplied in the reproducibility package; they do not denote an additional twenty page journal supplement. The five page Letter and three page supplement follow the current GRSL page limits.'
assert old in s;s=s.replace(old,new)
mapping={'VII':'V','VI':'IV','V':'III','IV':'III','III':'II','II':'II','I':'I'}
s=re.sub(r'(?<![A-Za-z])(?:VII|VI|IV|III|II|V|I)(?![A-Za-z])',lambda x:mapping[x.group()],s)
s=s.replace('II; II;','II;').replace('II and II','II').replace('III; III;','III;').replace('III--III','III')
s=s.replace('full Article','Letter').replace('reconstructed Article','reconstructed Letter')
s=s.replace('Table~\\ref{tab:pooled} records pooled components.','Table~\\ref{tab:pooled} records pooled components.')
extra='''
\\paragraph{Same journal eligibility.} The GRSL public submission guidance distinguishes Reject from Reject and Resubmit. The original decision supplies no invitation to resubmit. The accompanying cover letter transparently states the earlier manuscript ID and asks the editor whether the substantially reconstructed study may be considered as a new submission. This local content and presentation work does not establish editorial permission; the letter has not been sent and no new manuscript has been uploaded.
'''
s=s.replace('\\end{document}',extra+'\n\\end{document}')
(M/'Revision_memorandum.tex').write_text(s,encoding='utf-8')

p=R/'PROJECT_STATE.md'; text=p.read_text(encoding='utf-8')
marker='<!-- CURRENT_GRSL_20261008 -->'
if marker not in text:
    text=marker+'''\n# Current GRSL Letter delivery: 2026-10-08

The user explicitly selected IEEE Geoscience and Remote Sensing Letters. The canonical article is now a five page Letter with three figures, two tables, a five sentence positive abstract, and 17 verified references. Necessary definitions remain in the methods; scientific scope and limitations are concentrated in Discussion. The journal supplement is three pages. The former complete supplement is preserved as IUFEE_technical_record.tex/pdf for reproducibility, rather than represented as a journal supplement.

All scientific experiments and source data remain the verified October 7 results. Figures are being finalized using the Nature style in GitHub SciencePlots, with exact Chinese official boundary paths, editable PDF/SVG and direct 1000 dpi PNG exports. Cover_letter_GRSL.tex/pdf states importance, empirical contribution and journal fit; it discloses the previous Reject decision and requests an eligibility judgment. No editor message or submission has occurred. The official Reject guidance means content readiness does not imply resubmission permission.

The current sources are canonical. Do not run write_full_article_20261007.py, extend_supplement_20261007.py or update_records_20261007.py over this version. They are historical assembly scripts. Current presentation and content checks are under results/revision_20261008.

The following dated record describes the October 7 complete article and its unchanged scientific evidence. Its format statements are superseded by this header.

---

'''+text
    p.write_text(text,encoding='utf-8')
readme=R/'README_REPRODUCE.txt'; text=readme.read_text(encoding='utf-8')
if marker not in text:
    text=marker+'''\nCURRENT DELIVERY, 2026-10-08
Target: IEEE Geoscience and Remote Sensing Letters, selected by the user.
Canonical editable sources: manuscript/IUFEE_redeveloped.tex (five page Letter),
IUFEE_supplement.tex (three page journal supplement), Cover_letter_GRSL.tex,
Revision_memorandum.tex, and IUFEE_technical_record.tex (extended analysis record).
The October 7 data and experiments are unchanged. Current presentation scripts:
scripts/write_grsl_supplement_20261008.py and the Nature figure script for this date.
Compile the saved sources directly with compile_revision_20261007.py plus all five
stems as command arguments. Figure production uses the dedicated scifig runtime.
Vector PDF/SVG and directly rendered 1000 dpi PNG outputs accompany the package.

Historical assembly commands below can regenerate older versions only. In
particular, do not run write_full_article_20261007.py, extend_supplement_20261007.py,
update_records_20261007.py, or finalize_audit_record_20261007.py over this version.
Raw E/F inputs are unchanged. All working data and outputs remain on D.
The prior Reject decision did not invite resubmission. The unsent cover letter
asks for an editorial eligibility judgment; no new submission has occurred.

--- OCTOBER 7 REPRODUCTION PROVENANCE FOLLOWS ---

'''+text
    readme.write_text(text,encoding='utf-8')
(R/'ARTICLE_BUILD_SPEC.md').write_text('''# GRSL Letter build specification, 2026-10-08

User selected GRSL. Five pages inclusive of references; three page optional supplement only contains additional noncore content. Scientific evidence is unchanged from the verified October 7 full-frame analyses.

Main sequence: five sentence abstract; Introduction; Data and Methods; Results; Discussion with one Scope and limitations subsection; Conclusion; availability; disclosure; 17 references in first citation order. No article roadmap paragraph or literature comparison table. No journal names in running scientific prose. Avoidable compound hyphens and em dashes are removed; product identifiers, mathematical subtraction and bibliography metadata are necessary exceptions. Automatic body hyphenation is disabled.

Main displays: Fig1 official study map and source periods, Fig2 four panel representation diagnostics, Fig3 three panel GLAD evidence; TableI pooled G/J/F/A allocation components; TableII three city grouped components. Every display is introduced and numbered in sequence. Nature figure aesthetics use SciencePlots with readable sans serif labels, colourblind safe colours, restrained line art and panel labels. Preserve all official boundary vertices and 91 locations. Export true PDF/SVG vectors and direct 1000 dpi PNGs; inspect the final page renders for collisions.

Supplement: S1 additional computational checks, S2 additional sensitivity and six selected cells, S3 extra city summary and queue coverage. Tables S1 sensitivity, S2 selected cells, S3 queue coverage; Figure S1 additional city summaries. The Extended Technical Record is supplied separately in the reproducibility package and is not part of the journal supplement.

Cover letter: one page explaining importance, contribution, results and GRSL fit; disclose previous Reject and ID, request editorial eligibility judgment, no fabricated author or simultaneous submission declarations. No sending or uploading authorized by this production request.

Compile all five saved sources, verify mathematical claims against unchanged outputs, check page counts/citation order/hyphens/display sequence/reference provenance, render and inspect all journal pages and cover letter. Update delivery manifest only after independent scientific content review and final layout checks.
''',encoding='utf-8')
(R/'审稿意见落实与投稿边界.txt').write_text('''当前交付：2026年10月8日，按用户明确选择的IEEE Geoscience and Remote Sensing Letters制作。
正文5页（含参考文献）、投稿补充3页、封面信1页；22组可见审稿意见的实质落实说明另附。完整技术记录属于复现包，不作为超长投稿补充。
科学计算仍为已核验的91城结果，无新增或修改实验、方法和结论。当前主线是空间支持和来源表示的测量审计。正文呈现受控比较、关键量、来源定义、深度组成和案例解释。实际施工精度、局地洪水准确性和code 1生成含义仍未被现有材料证明。
图件使用Nature风格，保留中国官方国界矢量路径；PDF/SVG加1000dpiPNG。
原决定是Reject，官方指南没有赋予重投邀请。封面信透明注明旧编号和实质重构，请编辑判断能否按新提交受理。文件均未发送，也未上传投稿系统。
本轮表达及图表检查见results/revision_20261008，较早报告保留为历史追踪。
''',encoding='utf-8')
print('GRSL records aligned; technical evidence unchanged.')
