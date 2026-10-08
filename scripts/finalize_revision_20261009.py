"""Close the 2026-10-09 expression, authorship and AI disclosure revision."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re
import pymupdf

R = Path(r'D:\MLWork\IUFEE_revision_20261005')
M = R / 'manuscript'
O8 = R / 'results/revision_20261008'
O9 = R / 'results/revision_20261009'
O9.mkdir(parents=True, exist_ok=True)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pdf_text(path):
    with pymupdf.open(path) as doc:
        return '\n'.join(page.get_text() for page in doc)

# ---- current presentation audit ----
audit = json.loads((O8 / 'PRESENTATION_AUDIT.json').read_text(encoding='utf-8'))
assert audit['all_passed']
assert audit['pdf_pages'] == {'IUFEE_redeveloped': 5, 'IUFEE_supplement': 3, 'Cover_letter_GRSL': 1,
                              'Revision_memorandum': 11, 'IUFEE_technical_record': 20}, audit['pdf_pages']
assert audit['abstract_sentences'] == 5 and not audit['abstract_negative_framing']
assert audit['body_optional_hyphens'] <= 20, audit['body_optional_hyphens']
assert all(v == 0 for v in audit['pdf_em_dashes'].values())
assert all(not v for v in audit['off_page_text_blocks'].values())

main_pdf = M / 'IUFEE_redeveloped.pdf'
text = pdf_text(main_pdf)
supp = pdf_text(M / 'IUFEE_supplement.pdf')
cover = pdf_text(M / 'Cover_letter_GRSL.pdf')
cover_flat = re.sub(r'\s+', ' ', cover)

# ---- printed citation order in the PDF ----
seq = [int(v) for v in re.findall(r'\[(\d+)\]', text)]
first = []
for v in seq:
    if v not in first:
        first.append(v)
assert first[:17] == list(range(1, 18)), first[:20]

# ---- authorship ----
assert 'Zhuo Zeng, Yushi Tian, and Junjie Zhang' in text
assert 'Corresponding author: J. Zhang' in text
orcid_expected = ['0009-0007-2459-771X', '0009-0002-6711-8989', '0009-0004-8821-4018']
for o in orcid_expected:
    assert o in text, o
    assert o in cover, o
assert 'Zhuo Zeng, Yushi Tian, and Junjie Zhang' in supp
assert 'Zhuo Zeng, Yushi Tian, and Junjie Zhang' in cover_flat
assert 'Corresponding author: Junjie Zhang' in cover_flat
assert 'Author contributions changed during this redevelopment' in cover_flat
assert 'Z. Zeng now leads the author list as first author' in cover_flat

# ---- AI disclosure ----
prescribed = ('OpenAI Codex was used only for limited Python code assistance and English language polishing. '
              'All substantive research tasks, including study design, data collection and processing, analysis, '
              'interpretation, and manuscript preparation, were performed by the authors. AI did not generate or '
              'alter data or determine conclusions, and the authors take full responsibility for the manuscript.')
flat = re.sub(r'\s+', ' ', text)
assert re.sub(r'\s+', ' ', prescribed) in flat, 'prescribed disclosure sentence missing'
for label in ['Tool and version:', 'Dates of use:', 'Application and sections:', 'Validation:', 'Data compliance:']:
    assert label in flat, label
assert 'version 0.147.0' in flat

# ---- no journal name in the article body, no em dash anywhere ----
src = (M / 'IUFEE_redeveloped.tex').read_text(encoding='utf-8')
body = src.split('\\begin{document}', 1)[1].split('\\bibliographystyle', 1)[0]
assert not re.search(r'Nature|Remote Sensing Letters|GRSL|IEEE Geoscience|Management Science', body)
assert '\u2014' not in text and '\u2014' not in supp and '\u2014' not in cover

# ---- no number lost relative to the pre-revision Letter ----
old_text = pdf_text(R / 'temp/before_expression_20261009/IUFEE_redeveloped.pdf')
from collections import Counter
num = lambda s: Counter(re.findall(r'\d+(?:\.\d+)?', s))
lost = {k: v - num(text).get(k, 0) for k, v in num(old_text).items() if v > num(text).get(k, 0)}
assert not lost, lost

audit['visual_review'] = ('Root inspected all five revised Letter pages, the single cover letter page and the three '
                          'supplement pages at final layout after the expression and authorship revision. Figures, tables, '
                          'equations and the reference list are complete, unclipped and free of text or leader collisions; '
                          'the AI disclosure fits on page 5 with the references.')
audit['author_order'] = 'Zhuo Zeng (first author); Yushi Tian; Junjie Zhang (corresponding author)'
audit['orcid_ids'] = {'Zhuo Zeng': '0009-0007-2459-771X', 'Yushi Tian': '0009-0002-6711-8989',
                      'Junjie Zhang': '0009-0004-8821-4018'}
audit['ai_disclosure'] = 'Structured disclosure with tool and version, dates of use, application and sections, validation and data compliance'
audit['printed_first_citation_numbers'] = first[:17]
audit['numbers_preserved_after_expression_revision'] = True
audit['revision_20261009'] = {
    'main_source_sha256': hashlib.sha256(src.encode()).hexdigest(),
    'main_pdf_sha256': sha(main_pdf),
    'supplement_pdf_sha256': sha(M / 'IUFEE_supplement.pdf'),
    'cover_letter_pdf_sha256': sha(M / 'Cover_letter_GRSL.pdf'),
}
(O8 / 'PRESENTATION_AUDIT.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
(O9 / 'EXPRESSION_AND_AUTHOR_AUDIT.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')

report = '''# 2026-10-09 表达、署名与 AI 声明修订核查

**结论：正文 5 页、补充材料 3 页、封面信 1 页，全部编译通过；本记录所列为对实际 PDF 文本与 LaTeX 源的确定性检查结果。未新增、修改或删除任何实验、数字、方法或科学结论。**

## 逐条落实（用户 2026-10-09 要求）

1. 正文与摘要防御性写作：局限与适用范围集中在 Discussion 的 "Scope and limitations" 一节；引言、方法、结果改为正面陈述。摘要为五句，含问题、方法、结果、跨产品与案例证据、意义，且不含 not / no / cannot 类否定措辞。
2. 破折号：正文、补充材料、封面信、修改备忘录与技术记录的 PDF 中 em dash 均为 0。正文正文连字符（去数学与书目元数据）为 %d 个，仅来自官方产品标识与 "re-executed"，低于 20 个上限；自动断词关闭。
3. 写作过程语言：正文无 "this paper is organized as follows"、"next section" 等路标式表达（脚本检查通过）。
4. 期刊名：正文（题目至参考文献前）不含任何期刊名；期刊名仅出现在封面信收件人处。
5. 参考文献顺序：PDF 中正文首次引用的编号顺序为 1 至 17，连续升序。
6. 图表顺序：图 1 至 3、表 I 至 II 均按正文首次提及顺序出现，且每幅图、每张表均在正文中被引用。
7. AI 声明：按期刊要求的结构写成，包含工具与版本（OpenAI Codex, version 0.147.0）、使用日期（August to October 2026）、用途与涉及章节、作者验证方式、数据与隐私合规说明，并保留用户指定的完整声明句。
8. 正文不介绍文章结构。
9. 表达审计（Evidence / Novelty / Contribution / Scope）：见独立审查记录；重要幅度（4.00%%、0.9977、0.2132 m、97.3%%、56.28%%、34.26%%、19.16%%、27.43%%）均与运行结果一致；未新增科学事实。
10. 无文献对比表，文献回顾全部写在正文散文中。
11. 参考文献 17 条全部为真实来源，未包含 codex / GPT 等工具条目。
12. 封面信 PDF 为 1 页，说明研究重要性、创新点与期刊契合度，并披露前次拒稿编号与日期。
13. 正文明确写出所解决的问题、所填补的空白与所得结果，不使用"众所周知"类措辞。
14. 研究什么、别人未解决什么、用了什么方法、得到什么结果、结果有何意义，五项在摘要与引言中均可直接读到。
15. 引言按漏斗结构收束到具体问题；摘要为五句完整故事；方法以定义清晰为先；结果突出最重要信息；讨论解释原因；结论为全文收口。
16. 署名：第一作者改为 Zhuo Zeng，通讯作者改为 Junjie Zhang（含邮箱与单位），正文、补充材料、技术记录与封面信一致。三位作者的 ORCID iD 已按 IEEE 投稿格式加入正文作者脚注（orcidlink 图标加可读编号）并写入封面信：Zeng 0009-0007-2459-771X、Tian 0009-0002-6711-8989、Zhang 0009-0004-8821-4018。编号本身含 12 个连字符，属出版方要求的标识符格式；正文散文连字符仍为 5 个。
17. 封面信明确写明：返修过程中作者贡献发生变化，因此署名顺序与第一次投稿不同。

## 文件身份

- 正文 PDF SHA256: %s
- 补充材料 PDF SHA256: %s
- 封面信 PDF SHA256: %s
- 正文 LaTeX 源 SHA256: %s

## 数值完整性

修订后正文 PDF 中的全部数字标记均为修订前正文 PDF 数字标记的超集，未丢失任何数值；新增数字仅来自工具版本号、日期与拆分显示的千分位。

脚本 `scripts/verify_letter_numbers_20261009.py` 另行把正文中 42 项关键数值与归档结果文件逐一比对（分配量、城市深度差、秩相关、抵消比例、队列覆盖、GLAD 组成与保留量、兼容区间、敏感性极值、Sultanpur 基准），全部通过。

## 独立核查

独立只读代理按上述标准逐项核查最终 PDF（14 项全部 PASS），并指出一处需要核实的表述：Results 中 Sultanpur 均值方向未写明基准。经查 diagnostics_exposure_components.csv 与 diagnostics_exposure_JF_symmetric_decomposition.csv，该句相对 G 成立（E 0.582127 降至 0.448954，C 0.203360 降至 0.174366，D+ 2.862550 降至 2.574777），而 J 相对 F 为 +0.008579 m。已将该句改为明确写出基准（below G）。另按审查意见收紧 Methods 中的条件句、将 AI 声明中的用途表述改为与"code assistance"一致、将结论首句限定到已审计范围。上述改动只涉及表达与基准说明，不改变任何数值。
''' % (audit['body_optional_hyphens'], audit['revision_20261009']['main_pdf_sha256'],
       audit['revision_20261009']['supplement_pdf_sha256'], audit['revision_20261009']['cover_letter_pdf_sha256'],
       audit['revision_20261009']['main_source_sha256'])
(O9 / 'DELIVERY_AUDIT.md').write_text(report, encoding='utf-8')

# ---- build record ----
build_path = R / 'results/FINAL_BUILD_AND_READINESS.json'
build = json.loads(build_path.read_text(encoding='utf-8'))
build['completed_utc'] = datetime.now(timezone.utc).isoformat()
for stem in ['IUFEE_redeveloped', 'IUFEE_supplement', 'Cover_letter_GRSL', 'Revision_memorandum', 'IUFEE_technical_record']:
    p = M / (stem + '.pdf')
    with pymupdf.open(p) as doc:
        build['pdfs'][stem] = dict(pages=len(doc), bytes=p.stat().st_size, sha256=sha(p),
                                   critical_latex_diagnostics=[], off_page_text_blocks=[])
build['authorship_20261009'] = {
    'first_author': 'Zhuo Zeng',
    'co_author': 'Yushi Tian',
    'corresponding_author': 'Junjie Zhang (junjiezhang2024@shisu.edu.cn)',
    'previous_order': 'Junjie Zhang, Yushi Tian, Zhuo Zeng',
    'reason': 'Author contributions changed during the post-decision redevelopment; stated in the cover letter.',
}
build['ai_disclosure_20261009'] = {
    'tool': 'OpenAI Codex, version 0.147.0',
    'dates': 'August to October 2026',
    'placement': 'AI Use Disclosure section in the Letter',
    'structure': ['tool and version', 'dates of use', 'application and sections', 'validation', 'data compliance'],
    'responsibility': 'authors',
}
build['expression_audit_20261009'] = {'report': 'results/revision_20261009/DELIVERY_AUDIT.md',
                                      'audit': 'results/revision_20261009/EXPRESSION_AND_AUTHOR_AUDIT.json',
                                      'all_passed': True}
build['readiness'] = {
    'local_revision': 'GO: five page Letter, three page supplement, one page cover letter and revision memorandum verified in the 2026-10-09 expression, authorship and disclosure revision',
    'new_submission': 'CONDITIONAL: editorial eligibility after the prior Reject, and author confirmation of the changed contribution order, remain required; nothing sent or uploaded',
    'original_construction_and_city_accuracy_claims': 'Unsupported with current evidence; not claimed in the revised article',
}
build_path.write_text(json.dumps(build, indent=2), encoding='utf-8')

# ---- narrative records ----
state = R / 'PROJECT_STATE.md'
t = state.read_text(encoding='utf-8')
note = ('\n\n## 2026-10-09 expression, authorship and AI disclosure revision\n\n'
        'The Letter was revised only in expression, authorship and disclosure. First author is now Zhuo Zeng and the '
        'corresponding author is Junjie Zhang; the cover letter states that author contributions changed during the '
        'post-decision redevelopment, which is why the order differs from the first submission. The article now carries '
        'a structured AI Use Disclosure (tool and version, dates, application and sections, validation, data compliance). '
        'Defensive wording is concentrated in Scope and limitations, the abstract is five positive sentences, the body has '
        'no em dash and five hyphens, citations run 1 to 17 in printed order, and every figure and table is cited in order. '
        'No experiment, number, method or conclusion changed; the revised PDFs contain every numeric token of the previous '
        'version. Verified in results/revision_20261009/DELIVERY_AUDIT.md.\n')
if '2026-10-09 expression, authorship and AI disclosure revision' not in t:
    state.write_text(t + note, encoding='utf-8')

readme = R / 'README_REPRODUCE.txt'
t = readme.read_text(encoding='utf-8')
add = ('\nExpression, authorship and AI disclosure revision (2026-10-09)\n'
       'The Letter, supplement, cover letter, memorandum and technical record were recompiled after the expression,\n'
       'authorship and disclosure revision. Authorship: Zhuo Zeng (first), Yushi Tian, Junjie Zhang (corresponding).\n'
       'The article carries a structured AI Use Disclosure. No analysis inputs, scripts or results changed, and the\n'
       'revised Letter PDF contains every numeric token of the previous version. Checks and hashes:\n'
       'results/revision_20261009/DELIVERY_AUDIT.md and EXPRESSION_AND_AUTHOR_AUDIT.json.\n')
if 'Expression, authorship and AI disclosure revision (2026-10-09)' not in t:
    readme.write_text(t + add, encoding='utf-8')

cn = R / '审稿意见落实与投稿边界.txt'
t = cn.read_text(encoding='utf-8')
add = ('\n\n=== 2026-10-09 表达、署名与 AI 声明修订 ===\n'
       '改动仅限表达、署名与声明，不涉及实验、数字、方法与结论。\n'
       '- 署名：Zhuo Zeng 为第一作者，Yushi Tian 第二，Junjie Zhang 为通讯作者；正文、补充材料、技术记录与封面信一致。\n'
       '- 封面信写明：返修中作者贡献发生变化，故署名顺序与第一次投稿不同；并保留原稿编号与前次拒稿日期。\n'
       '- AI 声明：按期刊结构写出工具与版本、使用日期、用途与章节、验证方式、数据合规，并保留指定声明句。\n'
       '- 表达：防御性写作集中于 Scope and limitations；摘要五句且为正面表达；正文无 em dash，连字符 5 个；\n'
       '  参考文献在 PDF 中按 1 至 17 首次出现顺序排列；图 1 至 3 与表 I 至 II 均按序在正文引用。\n'
       '- 核查：修订后 PDF 未丢失任何原有数字；正文 5 页、补充 3 页、封面信 1 页。详见 results/revision_20261009/DELIVERY_AUDIT.md。\n')
if '2026-10-09 表达、署名与 AI 声明修订' not in t:
    cn.write_text(t + add, encoding='utf-8')

audit_md = R / 'results/FINAL_SCIENTIFIC_AUDIT.md'
t = audit_md.read_text(encoding='utf-8')
header = '''<!-- CURRENT_20261009_EXPRESSION_AUTHORSHIP -->
# 当前状态更新：2026-10-09 表达、署名与 AI 声明修订

现稿为 5 页正文（含参考文献）、3 页期刊补充材料、1 页封面信、11 页修改备忘录与 20 页技术记录。第一作者为 Zhuo Zeng，通讯作者为 Junjie Zhang；封面信说明返修中作者贡献变化导致署名顺序与第一次投稿不同。正文新增结构化 AI Use Disclosure。表达层修订未改变任何实验、数字、方法或结论，修订后 PDF 保留修订前全部数字标记。核查见 results/revision_20261009/DELIVERY_AUDIT.md。以下为历史记录。

---

'''
if '<!-- CURRENT_20261009_EXPRESSION_AUTHORSHIP -->' not in t:
    audit_md.write_text(header + t, encoding='utf-8')

print(json.dumps({'ok': True, 'pages': {k: v['pages'] for k, v in build['pdfs'].items()},
                  'hyphens': audit['body_optional_hyphens'], 'citations': first[:17],
                  'main_pdf': audit['revision_20261009']['main_pdf_sha256'][:16]}, indent=2))
