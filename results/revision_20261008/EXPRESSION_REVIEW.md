# 正文表达与 Letter 压缩审计：2026-10-08

审查与编辑范围：仅 `manuscript/IUFEE_redeveloped.tex`；本报告为审计记录。路线：SCIE 空间支持与来源表示测量审计，目标为最多 5 页且含参考文献的 Letter。未修改数据、实验、代码、数字来源或研究结论。原作者、单位与通讯信息保持原样。主稿 SHA256：`1a7af74ead7fb73cb2f5f46d9920b9dd81aa799227382a56820d4ec831eec7ae`。

## 当前稿状态

- 已将原完整文章压缩为 Introduction、Data and Methods、Results、Discussion、Conclusion 五个主节。
- 主稿约 2413 词，统计含图注、表内文字、数据可用性与致谢，不含参考文献；最终分页、图形大小和编译由主代理核验，本审计不将“写入源稿”等同于“五页编译已通过”。
- 摘要严格 5 句，采用正面表达：问题 → 受控 91 城比较与数据规模 → 4.00% 支持差、城市变化和 97.3% 抵消 → GLAD 组成/留存与六份记录 → 解释和可复用价值。没有“not / rather than / no claims”等否定式摘要。
- 正文共 3 图、2 表。图首次引用顺序为 `fig:frame`、`fig:representation`、`fig:glad`；表为 `tab:pooled`、`tab:cases`。所有保留图表都在正文中先后明示引用。
- 6 组主线公式保留正差值、J/F/A、有限概率深度汇总、W/N/E/C/D+、协方差与中心化效应、A 的兼容边界。对称 C/D+ 分解用文字说明，细节进入补充推导。

## Evidence / Novelty / Contribution / Scope

| 检查项 | 当前表达及证据 | 结果 |
|---|---|---|
| Evidence | 受控 J 对 F 的支持量减少 4.00%、中位/最大深度差、rho 与 rank changes 均保留；97.3% cancellation 与正负贡献明确置于主结果；等预算队列覆盖/重叠完整保留。 | 支撑清楚，没有用高相关掩盖局地差异。 |
| Novelty | 引言明确贡献是量化与定位 joint locations 降为 marginal fractions 后的实测后果，并留足字段复算；不把既有 covariance、Frechet 或 fractional programming 包装为首创。 | 自信程度与实证贡献匹配。 |
| Contribution | 引言最后一段、受控比较、结果首节、讨论首段、结论围绕相同主线；GLAD composition/retention 与城市组件帮助解释其意义。 | 一条可评估主线。 |
| Scope | 真实施工、thematic/hydraulic accuracy、统计独立性、推广性、review/intervention effectiveness 局限集中于 Discussion 的 Scope and limitations；方法保留共同测度、源类码、零分母等必要定义。 | 没有靠删除限制扩大科学主张。 |

读者五个核心问题都有直接答案：研究 maps linkage 的 spatial support choices；既有边际数据库丢失 joint locations；方法采用固定图源和网格的 J/F 对照及精确分解；结果指出 4.00% 支持差、高 rho 与 97.3% 抵消共存；意义是让稳定的汇总可解释并定位适合 targeted source review 的单元。

## 语言与形式扫描

- 全稿 Unicode em dash、TeX triple hyphen 和 double hyphen 均为 0；正文避免连词符拼接。
- 正文可见连词符仅正式产品/传感器 ID 的 4 处：GHS-FUA 1 处、GHS-BUILT-S 2 处、Sentinel-2 1 处。原作者元数据 e-mail 3 处未改。数学减号、负值和协方差差值是运算符，保留。
- 删除分散在引言、结果、图注、案例中的 accuracy disclaimer、not a new classifier、not a universal constant、neither ranking validated 等重复防御表述；对应必要限制集中写明。
- 不出现正文点名期刊，不出现文章结构导航段，不保留文献对比表；没有写作后台语言。
- 17 个原 citation key 全部保留，首次顺序保持：Rentschler2023、Tellman2021、Zhang2025、Koomen2026、TrentoOliveira2026、GHSFUA2019、GHSLBuiltS2023、GHSLDataPackage2023、MNRStandardAsia2023、WSFEvolution2021、WSF2019、Baugh2026、Potapov2022、GLADv2Download、Frechet1935、Dinkelbach1967、Olofsson2014。AI 软件仅在致谢如实披露，没有作为参考文献。

## 移出主稿的内容及不丢证据安排

移出主稿的原 `tab:sources`、`tab:sensitivity`、`fig:cases` 应按主代理的安排纳入补充或 extended technical record。原细节已在此前 20 页补充材料和已验证记录中：

- 源类码 native checks、历史零值替代、exponent/threshold 全矩阵、GHSL 阈值、RP 权重、QA 与非单调 RP 详情。
- archived ratio optimization 推导、条件共同测度与 synthetic vertex checks。
- 全 91 城组件、所有类分配与 retention、六个具体 cell dossiers、原 30 格队列与三城坐标。
- 三城 W/C/D+/E 12 个 city × scheme 行、Guwahati 的 t=0 但 f=.0767 单元、关键 GLAD 组成/留存和受控核心结果仍在主文。

主稿敏感性概述使用既有精确输出的四舍五入显示：最大兼容区间宽 1.9802 m、RP500 最大差 1.6225 m等均来自已核验结果；不是新实验或新增科学事实。完整数表保留在 extended record。

## 尚由主代理核验的环节

本代理未编译或重新绘图。主代理已回报首次编译成功，当前正文 5 页且含参考文献、投稿补充材料 3 页、cover letter 1 页；最终紧凑图件出来后仍须进行版面复核。17 条参考文献的输出编号、图件新尺寸与文字碰撞、最高分辨率/矢量输出、补充材料引用及复现包一致性由对应负责人闭合。若后续为五页再次改正文，需以最终快照更新本报告的词数和 SHA；本次表达审计针对上列快照。

术语扫描补充：已通知主代理在正文首次 GHS-BUILT-S 处恢复 Global Human Settlement Layer (GHSL) 的展开，并将首次 GloFAS 展开为 Global Flood Awareness System。本代理停止编辑正文，以免干扰主代理随后进行的表格排版。
