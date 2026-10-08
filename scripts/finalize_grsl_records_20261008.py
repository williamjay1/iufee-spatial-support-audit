"""Close the local delivery record after the completed final visual inspection."""
from pathlib import Path
import json, hashlib

R=Path(r'D:\MLWork\IUFEE_revision_20261005')
O=R/'results/revision_20261008'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

audit=json.loads((O/'PRESENTATION_AUDIT.json').read_text(encoding='utf-8'))
assert audit['all_passed']
assert list(audit['pdf_pages'].values())==[5,3,1,11,20]
assert all(v==0 for v in audit['pdf_em_dashes'].values())
map_fix=json.loads((O/'KASHMIR_MAP_CORRECTION.json').read_text(encoding='utf-8'))
assert map_fix['all_passed'] and 'Pending' not in map_fix['visual_review']
assert sha(R/'manuscript/IUFEE_redeveloped.pdf')==map_fix['main_pdf_after_sha256']
citation_check=json.loads((O/'CITATION_CHECK_AFTER_MAP.json').read_text(encoding='utf-8'))
assert citation_check['all_passed'] and citation_check['main_pdf_sha256']==map_fix['main_pdf_after_sha256']
assert citation_check['printed_first_citation_numbers']==list(range(1,18))
audit['visual_review']='Root inspected all five final main pages after the Kashmir map correction. The unchanged three supplement pages, one page cover letter, memorandum contacts and changed page 7, and technical-record contacts and nine-panel map page 13 retain the completed earlier review. No overlaps, clipped text or line/text collisions found. The corrected map and official Kashmir source symbols were also inspected.'
audit['printed_first_citation_numbers']=list(range(1,18))
audit['printed_citation_order_review']=citation_check['review']
audit['final_pdf_sha256']={p.stem:sha(p) for p in (R/'manuscript').glob('*.pdf') if p.stem in audit['pdf_pages']}
(O/'PRESENTATION_AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')

report='''# 当前交付审计：2026-10-08，GRSL Letter

**内容与本地制作 GO；同刊新投稿资格 CONDITIONAL。** 目标期刊由用户明确指定为 IEEE Geoscience and Remote Sensing Letters。正文 5 页含参考文献，期刊补充材料 3 页，封面信 1 页，修改备忘录 11 页。20 页 Extended Technical Record 供复现核查，未作为期刊补充材料计算。没有发送编辑消息或上传稿件。

## 内容与表达

- 保留已执行的 91 城、1,259,886 格受控 J/F 比较、F/A 区别、深度分解、GLAD 配对、等预算队列和六格记录。未新增实验、数字、方法或科学结论。
- 五句摘要按问题、方法、主要结果、跨产品与案例、意义组织，均为正面表达。引言收束到 joint location loss，讨论解释局部抵消及筛选效应，适用范围集中在 Scope and limitations。
- 重要幅度明确保留：4.00% allocated mass difference、最大 0.2132 m 城市深度差、97.3% 相反贡献抵消、19.16% class composition 与 27.43% class retention。无未经证实的 construction/accuracy/hydraulics/review-efficiency 主张。
- 正文无结构路标段、文献对比表、期刊点名或后台操作痕迹。全文 PDF 实际 em dash 均为 0。主文去除数学和书目元数据后仅 4 个必要连字符，全部来自官方产品标识；作者 e-mail 元数据另外 3 个。主文、补充和封面信关闭自动单词断行。
- 17 条真实文献按实际 PDF 首次引用顺序 1 至 17 编排。图 1 至 3、表 I 至 II 按正文首次提及顺序对应。Codex 等工具只在实际使用披露中出现，未作为参考文献。
- 9.97% 与 3.28% 明确为 pooled cell area fractions；0.207904 m 明确为去除历史筛选相对 A 的最大绝对城市变化。所选 Srinagar/Nashik 明确为后续诊断案例。

## 图件与版式

- 5 幅图均采用 GitHub SciencePlots 的 Nature style 制作，提供真正矢量 PDF/SVG 和直接绘制 1000 dpi PNG。所有 PDF 的嵌入栅格图像对象为 0；九面板图采用原生单元多边形。
- 最小图字号 7 pt，在正文 IEEE 宽度约为 6.65 pt。字体嵌入、文字框碰撞和画布外文字检查通过；主代理实际查看最终页面，未发现文字遮挡、裁切或标注与线条交叉。图1的 Delhi、Sultanpur、Kashmir region 位于左侧白色留白，Guwahati、China 位于右侧白色留白；使用透明标注框，各文字框离地图框 2.5 pt，引线延长且不穿其他文字，并以实际 PDF 文字坐标复核。
- 主图国界和海岸线来自中国自然资源部标准地图 GS(2023)2761 的精确矢量路径，逐个顶点与 code 检查一致，全部 91 城定位保持不变。已补回克什米尔地区界虚线与原图停火线军事分界符号，外置标注 Kashmir region；这两类线独立于国界，陆地统一中性填色。原 106 条陆地、35 条国界和 12 条海岸路径记录与修正前完全一致。图中叠加研究点，父图审图号说明来源，不宣称该研究叠加图取得新的审图批准。
- 全部五个 PDF 编译完成，无 undefined references、Overfull 或致命 LaTeX 诊断，文字块均在页面边界内。期刊补充材料表 S3 已避免插入句子中间；技术记录图注与实际三列内容一致。

## 审稿意见和投稿边界

独立 Evidence / Novelty / Contribution / Scope 审查 PASS，无未关闭 P0/P1。可见编辑与审稿意见的 22 个归组事项在备忘录逐项对应。Reviewer 3 所称另一个附件未提供，不能宣称审查了不可见意见。

GRSL 的官方指南区分 Reject 与 Reject and Resubmit。原决定不构成重投邀请。封面信说明研究重要性、技术与实证增量、遥感读者契合，披露原稿编号与拒稿日期，并请求编辑判断这次实质重构能否作为新投稿受理。内容制作完成不能替代该资格判断。

官方制作和投稿依据：
- https://www.grss-ieee.org/publications/checklist-for-authors/
- https://www.grss-ieee.org/publications/author-resources/scope-of-grsl/
- https://www.grss-ieee.org/publications/grsl-submission-hints/
- https://www.nature.com/nature/for-authors/final-submission
- https://github.com/garrettj403/SciencePlots

详细证据：INDEPENDENT_CONTENT_REVIEW.md、FIGURE_DESIGN_AND_QA.md/json、PRESENTATION_AUDIT.json、KASHMIR_MAP_CORRECTION.json、CITATION_CHECK_AFTER_MAP.json；数据与数值审计沿用已验证的 revision_20261007 结果。当前页数和文件身份以 FINAL_BUILD_AND_READINESS.json 与 DELIVERY_MANIFEST.json 为准。
'''
(O/'DELIVERY_AUDIT.md').write_text(report,encoding='utf-8')

path=R/'PROJECT_STATE.md'
text=path.read_text(encoding='utf-8').replace('Figures are being finalized using the Nature style in GitHub SciencePlots, with exact Chinese official boundary paths, editable PDF/SVG and direct 1000 dpi PNG exports.','All five figures are finalized using the Nature style in GitHub SciencePlots, with exact Chinese official boundary paths, editable PDF/SVG and direct 1000 dpi PNG exports. Final page rendering, printed citation sequence and independent content checks pass; see results/revision_20261008/DELIVERY_AUDIT.md.')
path.write_text(text,encoding='utf-8')
path=R/'results/FINAL_SCIENTIFIC_AUDIT.md'
text=path.read_text(encoding='utf-8')
header='''<!-- CURRENT_GRSL_20261008 -->
# 当前最终状态：2026-10-08 GRSL Letter 交付

**内容与本地制作 GO；同刊投稿资格 CONDITIONAL。** 目标期刊已由用户指定为 IEEE Geoscience and Remote Sensing Letters。现稿为正文 5 页、期刊补充 3 页、封面信 1 页和修改备忘录 11 页；完整技术记录 20 页供复现核查。October 7 的全部已验证科学结果保留。独立内容审查、实际 PDF 引文顺序、Nature 风格矢量图与 1000 dpi 输出、官方地图精确路径和逐页版式检查通过。原 Reject 未邀请重投，未进行任何对外发送或投稿。

当前审计见 revision_20261008/DELIVERY_AUDIT.md 与 PRESENTATION_AUDIT.json。以下均为历史记录，其版式和选刊状态由本段覆盖，其科学审计证据保留。

---

'''
if '<!-- CURRENT_GRSL_20261008 -->' not in text:
    path.write_text(header+text,encoding='utf-8')
print('Final presentation and current delivery records closed; ready to refresh local package.')
