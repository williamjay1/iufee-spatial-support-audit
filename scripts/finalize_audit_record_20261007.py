"""Record the final review state without altering historical audit evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import fitz

root = Path(r'D:\MLWork\IUFEE_revision_20261005')
out = root / 'results/revision_20261007'
records = {}
for stem, expected in [('IUFEE_redeveloped', 10), ('IUFEE_supplement', 20), ('Revision_memorandum', 11)]:
    pdf = root / 'manuscript' / (stem + '.pdf')
    with fitz.open(pdf) as doc:
        assert len(doc) == expected
        records[stem] = {'pages': len(doc), 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest()}
    log = pdf.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
    critical = [x for x in log.splitlines() if x.startswith('!') or 'Overfull' in x or 'undefined' in x.lower()]
    assert not critical, critical

audit = '''# 2026-10-07 最终交付核验

阶段：本轮实质修订交付与新投稿准备。结论：**内容层面 GO；当前声明范围内无未解决 P0/P1。** 该结论针对来源表示与空间支持的测量审计，不代表某一期刊的正式提交检查或录用判断。

交付版本为 10 页完整正文、20 页补充材料、11 页修改备忘录。正文含 4 幅图、4 张表与 17 条相关文献；修改备忘录处理 22 组可见审稿意见。Reviewer 3 提及但未提供的附件不计入已处理内容。

## 核验依据

- `FINAL_READINESS_REVIEW.md`：独立科学内容审查通过，五项核心行动均已闭合。
- `NUMERICAL_FINAL_REVIEW.md`：主文公式、数值及备忘录额外数字独立核对通过；未将数值复现当作实地精度验证。
- 全框架诊断覆盖 91 城、1,259,886 条正差记录，验证标记全部通过。跨产品对照覆盖 91 城；新增六份案例 dossier 来自实际计算记录。
- 最后提出的措辞微修已落实：六城零支持限定为 J/F；首次展开 GLAD 和 QA；补充表对重名 Kolkata 使用 FUA 标识。
- 三份最终 PDF 均成功编译，无 LaTeX 严重错误、未定义引用或 overfull 警告；全部正文页、修改备忘录联系表及补充材料改动页面完成视觉核对。既有补充页沿用此前视觉审查结果。
- 两幅新增科学图通过尺寸、字体及矢量输出审计，同时提供 900 dpi 位图。官方国界层保持已核验版本，来自中国自然资源部标准地图 GS(2023)2761 的矢量路径；研究地图含 91 点且 PDF 内无栅格底图。来源审图号不表示叠加后的研究图另获审批。
- 本轮未提交期刊、未发送外部消息、未公开发布新版代码数据；原始材料保持原位。最终打包器另核验文件清单、散列与 ZIP 完整性。

## 剩余科学边界与投稿步骤

独立施工真值、局地水动力精度与 WSF 原生 code 1 生成含义仍未被现有材料证实。正文已限制相关主张，没有将 GLAD 比较或计算 dossier 写成独立真值或人工判读。它们不阻止当前测量审计贡献的内容交付；扩大为真实施工面积或更准确洪水风险的主张时，需要相应外部证据。

目标期刊尚未重新确定。正式投稿前应按所选期刊核对完整 Article 类型、篇幅、格式与数据代码发布要求；当前 10 页稿不是对原拒稿信的受邀返修稿。

本文件与当前 `PROJECT_STATE.md`、`FINAL_BUILD_AND_READINESS.json` 一起定义本轮交付状态。较早审计中“五页稿”“13 条文献”“等待受控联合对照”的判断是历史快照，已由本轮完整正文及实做分析取代。
'''
(out / 'DELIVERY_AUDIT.md').write_text(audit, encoding='utf-8')
(out / 'FINAL_PDF_SNAPSHOT.json').write_text(json.dumps({'recorded_utc':datetime.now(timezone.utc).isoformat(), 'pdfs':records}, indent=2), encoding='utf-8')
history = root / 'results/FINAL_SCIENTIFIC_AUDIT.md'
old = history.read_text(encoding='utf-8')
start, end = '<!-- CURRENT_20261007_START -->', '<!-- CURRENT_20261007_END -->'
if start in old:
    old = old.split(end, 1)[1].lstrip()
cover = '''<!-- CURRENT_20261007_START -->
# 当前最终状态：2026-10-07 完整文章交付

**本轮内容层面 GO。** 当前最终稿为正文 10 页、补充 20 页、修改备忘录 11 页；两项独立审查通过，关键措辞修正已闭合，无未解决 P0/P1。具体依据见 `revision_20261007/DELIVERY_AUDIT.md`、`FINAL_READINESS_REVIEW.md` 和 `NUMERICAL_FINAL_REVIEW.md`，文件页数及散列见 `FINAL_BUILD_AND_READINESS.json`。

以下全部为历次带时间的审计记录，保留供追踪。它们不覆盖上述当前状态；其中较早关于五页稿、受控联合支持比较尚缺以及核心整合待办的判断已被本轮实做分析和完整正文取代。内容 GO 仅针对有边界的测量审计贡献；独立真值与局地洪水准确性未被宣称完成，具体期刊的正式投稿检查仍须按最终选刊执行。
<!-- CURRENT_20261007_END -->

---

'''
history.write_text(cover + old, encoding='utf-8')
print(json.dumps(records, indent=2))
