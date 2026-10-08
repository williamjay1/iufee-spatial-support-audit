# IUFEE：数学与遥感测量的聚焦文献核验

核验日期：2026-10-07。责任范围：新增数学及测量论证来源，未修改主正文或主参考文献。已读 manuscript/references.bib 与 results/LITERATURE_EVIDENCE.md；下列三个 BibTeX 键及 DOI 均不在这两份既有材料中。

## 范围与方法

Route：SCI，主线为遥感测量／数据产品诊断；关注共同空间支撑、条件兼容集合、比值计算与参考证据设计。没有因果识别或预测训练要求。本次使用 paper-venue-router 的类型判断、literature-review 的来源／实际支持范围核验，以及 agent-reach 的 Exa 搜索、Jina 网页阅读。是三篇经典来源的聚焦核验，不是系统综述。仅依赖出版记录、Crossref 注册元数据和作者机构存档正文片段；其他搜索结果只用于找到原始出处。

检索词包括完整论文题名及 DOI，并进一步检索 Olofsson 作者稿的 sampling design 与 Sources of Reference Data。三个 DOI 均从 Crossref API 实际读取并与官方或作者机构记录交叉核验。全文取得程度逐篇说明；没有将摘要或索引片段写成全文阅读。未下载或保存新的原始文件；只有本说明及配套新增 BibTeX 写入 D 盘。

## 1. Fréchet：兼容界的经典来源

**书目**：Fréchet, Maurice. 1935. “Généralisation du théorème des probabilités totales.” *Fundamenta Mathematicae* 25: 379–387. DOI **10.4064/fm-25-1-379-387**。官方出版记录和 Crossref 均为单数 Généralisation；不从第三方拼成 Généralisations。

**实际核验及支持范围**：确认该原始论文存在、作者、年份、题名、卷页和 DOI。它可作为 Fréchet 兼容界的经典出处；本次未读取其受限原文，不能给出原论文公式号或声称逐页核验了本文的二维特例。IUFEE 的实际数学支持仍来自补充 S2 自足的集合恒等式推导：同一概率／归一化面积测度下，令 Pr(S)=s、Pr(P)=p、t=Pr(S∩P^c)，则 t≤s、t≤1−p，且 Pr(S∪P^c)=s+1−p−t≤1，从而 max(0,s−p)≤t≤min(s,1−p)。这段是当前稿件的直接推导，不能包装成此次从1935原文读取的段落。

**应用边界**：该引用不能证明分别重投影的两份 archived fractions 事实上共享同一个 native-area measure，也不建立分类误差、地理配准误差或建筑变化真实性。保留 S2 的共同支撑条件；对 S11 显式写出 uniform 100-subcell measure 即可清楚界定 fine-grid geometric intersection。兼容界是经典结果，新增贡献应落在可复核的表示损失及应用诊断。

**全文状态**：官方出版页经 Jina 成功读取，并找到 CC-BY 下载链接；官方 PDF 下载和旧 ICM 扫描均遇到403/反机器人页面。未获取原文，不编造精确原文页内定位。

来源：[官方出版记录](https://www.impan.pl/pl/wydawnictwa/czasopisma-i-serie-wydawnicze/fundamenta-mathematicae/all/25/0/93246/generalisation-du-theoreme-des-probabilites-totales)、[Crossref 注册记录](https://api.crossref.org/works/10.4064/fm-25-1-379-387)、[官方全文入口，当前访问失败](https://www.impan.pl/shop/publication/transaction/download/product/93246)。建议键：Frechet1935。

## 2. Dinkelbach：分式问题与参数残差的经典关系，勿错称算法

**书目**：Dinkelbach, Werner. 1967. “On Nonlinear Fractional Programming.” *Management Science* 13(7): 492–498. DOI **10.1287/mnsc.13.7.492**。出版页首发日期为1967-03-01。

**实际支持论点**：出版摘要明确说明该论文研究非线性／线性分子分母的分式规划，并依据 Jagannathan（1966）的分式规划与参数规划关系，重新陈述和证明相关定理。故可引用它说明本文 ratio-residual transformation 属于经典 fractional programming，不能把这个变换写为本文新提出。此关系对本文在严格正的 lower mass 情形中的残差求根具有适切性；本文 separable box residual、二分求根和零质量特例仍需依靠 S2 的具体证明与独立数值检查。

**归属与实现区别**：当前 IUFEE 执行的是对标量残差 F−(x)、F+(x) 做二分求根。标准 Dinkelbach iteration 会解参数化子问题，再以所得可行解的分子／分母比值更新参数；本文65次 bisection 不应称作运行 Dinkelbach 算法。出版摘要本身还注明 Jagannathan（1966）的在先关系；若需要历史首创归属，应进一步核验并引用该在先论文，当前不凭二手摘要新增一个未经书目核验的条目。

**可用英文措辞**：The ratio bounds use the classical relationship between fractional and parametric optimization (Dinkelbach, 1967). For the separable cellwise box constraints, we solve the resulting scalar residual equations by bisection.

**全文状态与精确定位**：出版方摘要完整读取；View PDF 链接返回摘要／访问入口，未取得正文。所确认归属来自官方 Abstract，不能附伪造 theorem number、原文页内定位或声称已经核对原文全部假设。

来源：[INFORMS 出版摘要](https://pubsonline.informs.org/doi/10.1287/mnsc.13.7.492)、[Crossref 注册记录](https://api.crossref.org/works/10.1287/mnsc.13.7.492)。建议键：Dinkelbach1967。

## 3. Olofsson：accuracy / area estimation 所需的参考设计

**书目**：Olofsson, Pontus; Foody, Giles M.; Herold, Martin; Stehman, Stephen V.; Woodcock, Curtis E.; Wulder, Michael A. 2014. “Good practices for estimating area and assessing accuracy of land change.” *Remote Sensing of Environment* 148: 42–57. DOI **10.1016/j.rse.2014.02.015**。

**实际支持论点**：作者稿的 Abstract、§2 Sampling Design、§3.2 Sources of Reference Data 和 response-design 定义已通过 Exa 的作者机构 PDF 索引片段定向读取。文中将 sampling、response 与 analysis 作为配套设计；概率抽样须有已知且非零的 inclusion probabilities，参考分类应满足变化期与空间单元要求，并比待评地图分类更可靠。故另一全球产品之间的类别一致性以及按贡献刻意挑选的 top cells，均不能直接替代其定义的总体 accuracy / area estimation。

**容易误写的边界**：§3.2 允许沿用与地图相同的影像来源，只要参考判读过程更准确；不应把本论文写成要求完全不同传感器或零共享来源。IUFEE 当前没有这种有凭据的高质量参考分类，因此可准确写成 cross-product agreement 与 review queue。按 g·h 或表示误差贡献挑选的队列适合诊断／后续审查，其选择并非概率抽样，不能外推总体准确率或面积误差。将其用作有信息的例证不自动要求当前测量诊断稿新增 accuracy experiment。

**定位与全文状态**：机构作者稿索引 Abstract 行7–22、§2 行181–195、§3.2 行467–480提供上述直接文本依据。作者稿保留部分编辑痕迹，所引定位是作者稿行号，不冒充最终出版页内位置。已找到官方出版摘要和作者存档；直接机构 PDF 下载403，仅获得定向原文片段，未读取完整PDF。

来源：[ScienceDirect 出版页](https://www.sciencedirect.com/science/article/pii/S0034425714000704)、[Nottingham 作者机构记录](https://nottingham-repository.worktribe.com/output/728216/good-practices-for-estimating-area-and-assessing-accuracy-of-land-change)、[该机构作者稿](https://nottingham-repository.worktribe.com/preview/728232/Olofsson_good%20practices.pdf)、[Crossref 注册记录](https://api.crossref.org/works/10.1016/j.rse.2014.02.015)。建议键：Olofsson2014。

## 整合建议与核验边界

- 数学界公式附近可引 Frechet1935，同时保留自足证明及共同测度条件；当前只确认原始出处，原文公式定位未读到。
- 比值优化节可引 Dinkelbach1967，写 classical fractional–parametric relationship + bisection。当前 box 特例、极值及零分母处理由自己的证明和检查支撑，不能只靠外引。
- 讨论参考证据及队列外推边界处引 Olofsson2014，精确区分 agreement、diagnostic selection、accuracy / area estimation。无需增加与主张不相称的无条件实验门槛。

配套 ADDITIONS_20261007.bib 仅含以上三条。主正文和 references.bib 未修改。三个 DOI 的存在及元数据均已核验；1935与1967全文尚未取得，2014只获得作者稿的定向片段。引用不能替代IUFEE共同支撑的声明或实际结果核验。
