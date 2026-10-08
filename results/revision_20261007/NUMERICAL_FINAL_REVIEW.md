# 本轮主文终稿数值、公式与解释核对

审查对象：`D:\MLWork\IUFEE_revision_20261005\manuscript\IUFEE_redeveloped.tex`。

审查时间：2026-10-07 23:16–23:20（Asia/Shanghai）。核对时主文 SHA256：`54BE0B11A49EF030979231562A1C63177E109C8ACF92F289F4B677E240C47E82`。

结论：**PASS；当前快照没有未解决的 P0 或 P1 数值、公式或解释范围问题。** 审查中发现的“六城零非零深度支持”范围问题已由主代理将正文限定为 J/F；最新稿第 191 行已核验。该结论只针对本轮指定数值和数学解释，不代替文献、图形、版式或投稿适配审查。

路线：SCIE 描述性空间测量与表征审计。适用标准是源定义、共同测度、计算复现和主张边界；本任务采用 `paper-verification` 的数值与公式对照模块。没有追加因果识别、外部精度验证或新实验。

## 1. 数据与计算范围

本轮只读核对正文、已冻结的 J/F/A 全 91 城结果、GLAD 全样本结果、本代理已运行并核验的本轮诊断输出，以及原敏感性输出；只新增本报告，不改正文、数据或既有结果。以下“通过”表示正文与这些可追踪输出及数学关系一致，并不表示这些源产品已经获得独立真值验证。

主要结果目录是 `D:\MLWork\IUFEE_revision_20261005\results`；本轮诊断子目录是 `revision_20261007`。`diagnostics_summary.json` 的 `all_passed=true`，91 城、1,259,886 个正 g 单元完全按键对齐，g、h 和中心坐标一致，J/F/A 聚合量与冻结结果一致。GLAD 无 missing cell，最小 paired coverage 为 1，类份额分区最大误差为 4.47035e-8。

## 2. 核心数值审计

| 正文位置及主张 | 原始输出值或核验依据 | 判定 |
|---|---|---|
| 第 16、160 行：91 城，1,259,886 个正 g 单元，GHSL 总量 400.536 km² | `revision_validation.json`：400,535,818 m²；91；1,259,886；七 RP 完整记录数相同 | 通过 |
| 第 69 行：WSF2019 code1 在 56 张中的 52 张出现，共 134,285 个 native pixels | 直接汇总旧 `wsf_source_semantic_audit.csv` 的 WSF_2019 56 行，52 行 count>0，sum=134,285；两张 native 法证输出与旧计数及身份一致 | 通过；仍未给 code1 指派真实类别 |
| 第 160 行：原城市均值重构最大差异小于 4e-9 m | `revision_validation.json`：3.836230000331398e-9 m | 通过 |
| 第 162 行及 pooled 表：J/F/A 的 W 为 84.434/87.956/90.244 km² | 实际 W=84.4343917421/87.9556437231/90.2439231280 km² | 通过 |
| 第 162 行：J 相对 F 质量减少 4.00%；F 相对 A 减少 2.54% | `joint_overlay_aggregate_summary.json`：−4.003440634% 与 −2.535660381% | 通过；两个比较的分母和处理含义不同，正文已区分 |
| pooled 表：G 的 W/N/C/D+/E | 400.535818 km²；81.3719028716 百万 m³；18.5397471744%；1.09579497766 m；0.203157618407 m | 表内四舍五入一致 |
| pooled 表：J 的 W/N/C/D+/E | 84.4343917421；16.5910251730；18.3305586859%；1.07195891731；0.196496058427 | 一致 |
| pooled 表：F 的 W/N/C/D+/E | 87.9556437231；17.3349800928；18.3244239002%；1.07554678403；0.197087751951 | 一致 |
| pooled 表：A 的 W/N/C/D+/E | 90.2439231280；17.7967473884；18.3897769202%；1.07237383267；0.197207155580 | 一致 |
| 第 181 行：J−F 城市绝对差 median 0.0023、max 0.2132 m，ρ=0.9977，42 城 rank 改变，top10 保留 9 | `joint_overlay_aggregate_summary.json`：0.002265150665、0.213176595120、0.997721932375、42、9 | 通过 |
| 第 181 行：Srinagar 最大差异但仍 rank 7；Nashik F63→J76，0.0082→0.0013 m | `joint_overlay_city_summary.csv` 与本轮分解：Srinagar −0.213176595120 m；Nashik −0.006910738900 m | 通过；rank 变化与绝对深度差未混同 |
| 第 183 行：pooled 差 −0.000592、正贡献 +0.010666、负贡献 −0.011258、绝对量 0.021923 m、cancel 97.3% | `diagnostics_summary.json`：−0.000591693523895、+0.010665819799223、−0.011257513323117、0.021923333122340；0.973010786243 | 通过；没有把 pooled 量当城市均值平均 |
| 第 191 行：Srinagar 支持份额 46.32→41.03%，条件深度 1.9314→1.6609，分解 −0.0951/−0.1181 m | `diagnostics_exposure_components.csv`、`diagnostics_exposure_JF_symmetric_decomposition.csv`：−0.095055766073126 与 −0.118120829046568 | 通过 |
| 第 191 行：Guwahati 73.47→75.66%，1.5062→1.5312，分解 +0.0333/+0.0186 m | 同上：+0.033307415082980 与 +0.018619223398605 | 通过 |
| 第 194–196 行：GLAD new 组成 G/J/F/A 为 14.72/19.16/18.65/18.76%；J 留存 new/stable/absent 为 27.43/23.56/10.09% | `diagnostics_glad_class_allocation.csv`：J new 19.15603596%；质量留存 27.4329404/23.5640052/10.0942089% | 通过；组成份额与相对 G 的绝对质量留存分母已明确区分 |
| 第 196 行：J/F 的 GLAD-new 绝对质量 16.174/16.401 km² | 16.174282295/16.400944719 km² | 通过；J 比 F 组成更高同时绝对量更低 |
| 第 198 行：正 g/零变化单元无权重 GLAD-new 9.97/3.28%，pooled ratio 3.04 | 原全 GLAD 输出：0.09970124023/0.03275380770，ratio 3.04395877 | 通过；明确是描述性跨产品对照 |
| 第 202 行：GLAD loss 低于 0.01%，missing 分配为零 | G loss 0.001815188%；本轮 G/J/F/A 均低于 0.01%，共同支持 missing=0 | 通过 |
| 第 207 行：L/A/U 质量 79.853/90.244/99.605 km²；interval median/IQR 0.0482/[0.0035,0.1184]；≥0.05 有 44 城；6 个退化深度区间 | `revision_frechet_summary.json`：79.852619583488/90.243923128044/99.604910831111；0.0482162282255/[0.0034661470631,0.1184246358838]；44；6 | 通过 |
| 第 207 行：Srinagar 区间 0.1791–2.1593 m；A=0.8893 m | `revision_frechet_city.csv` 及 summary 最大宽度 1.980212032113 m | 通过；未宣称该 A 条件区间必须包含不同注册的 J |
| 第 209 行：未记载类 g 质量 0.033143%；全置 settlement 最大均值变化 0.0286 m；任意兼容赋值 max width 0.0383 m，Mangaluru | 本次直接汇总 `revision_coding_bounds_city.csv`：0.0331427555361%；0.0286255580838；0.038271748843，Mangaluru | 通过 |
| 第 211 行：只改 historic-zero 名称无数值变化；严格剔除 unresolved 并剔除 positive history 后所有分母为零；omit history max 0.2079 m | `revision_history_city.csv`：rename max=0；strict denominator sum=0；omit max abs=0.207903889089 | 通过 |
| 第 214 行：15 个非参照 exponent ρ=0.9866–0.9990；τ=.75 仅 89 定义城，ρ=.7948，top10=6；Kolkata/Kolhapur 分母零 | `revision_weight_summary.csv` 与逐城 CSV：ρ min=.986631627851、max=.998980445259；89；.794784067943；6；两个零分母城市逐行复核 | 通过 |
| 第 214 行：g>500 留存 78.11% 的正 GHSL 质量，A 城市均值 max shift .0734 m | `revision_qa_threshold_summary.csv`：.781069629583；.0733775050306 | 通过 |
| sensitivity 表的三 binary、uniform、RP100、RP500、QA 行 | 原 weight/hazard/QA summary：ρ、n、median absolute、max absolute 均按展示精度匹配；RP500 max=1.62253559261 m、QA max=.403928478252 m | 通过 |
| 第 236 行：nearest/average ρ=.9979–.9993；A 的 median 从 .1173 到 uniform .1583/RP500 .2246 | alignment：.997877524816–.999327093324；hazard summary：.117314662487、.158271295299、.224551153137 | 通过；这些数值为城市 median，而非 pooled E |
| 第 238 行：2,437 非单调 RP 单元，0.089864% GHSL 质量；cummax A 最大变化约 .00174 m | `revision_monotonicity_summary.json`：2,437；.00089864372629 的质量 fraction；.001735345650779 m | 通过 |

## 3. 三城 W/C/D+/E 表与具体单元

正文三城表共 12 个 city×scheme 行，逐项对照 `diagnostics_original_three_case_exposure_components.csv`。W 的 km² 换算、C 的百分数换算、D+/E 的 m 单位及三位小数四舍五入均一致。表下正文的 G→J 解释与因子方向也一致：Delhi 的 C 上升、D+ 下降；Guwahati 的 C 大幅上升、D+ 略下降；Sultanpur 两项下降。没有用 J−F 分解数字冒充 G−J 分解。

第 191 行的六个 J/F 零支持城市是 Saharanpur、Dehradun、Aurangabad、Gwalior、Hardoi、Salem。它们在 J/F/A 下 W>0、W+=0、E=0，D+ 未定义，J−F 对称分解未定义。G 下只有其中四城 W+=0；Gwalior 和 Salem 的 G 仍分别有 C=.000134420890588 和 .000220337934616。这是初版表述范围需要限定的原因，最新稿已经使用“under J/F”，故该 P1 已关闭。

第 267、272、275 行与 `case_dossiers_cells.csv` 对照通过：

- Delhi 两格的坐标、g=3914/5207 m²、h=4.092/2.857 m、GLAD-stable=1 均一致；不存在影像人工判读或真值认证的冒称。
- Guwahati queue order 10：中心 (91.6858463002 E, 26.172076736 N)，g=850，h=8.6555919647，PW QA=1，sF=.1299999952、pF=.4099999964、fF=.0766999977、tF=0；RP50=9.5520000458、RP75=9.4239997864，下降 .1280002594 m。正文四舍五入正确。top10 两格 PW=1 也与旧队列一致。
- Sultanpur queue order 1：中心 (82.0890546311 E, 26.2707029303 N)，g=3927，h=5.8005576134，tF=.3499999940，GLAD-new=0。旧 top10 的 GLAD-new median=0，恰有一格正 QA，正文一致。

第 277 行三城原 top10 对本城 Σgh 的覆盖分别为 .008701396540375、.176033811119906、.158421533215461，展示 0.87/17.60/15.84% 正确。

## 4. 公式、共同支持与队列预算

| 数学或解释条件 | 核对结果 |
|---|---|
| `eq:joint`：100 个等测度子格，t=mean[S(1−P)]，s=mean[S]，p=mean[P] | 与 native joint 脚本的同一嵌套 10 m 网格及明确 class/missing 规则一致。共同 grid 不是提高 Evolution 原生信息精度。 |
| `eq:cov`：t−s(1−p)=−Cov(S,P) | 正确，因为 E(SP)=s−t。诊断中 covariance 按已存 t/s/p 重构，恒等残差为 0；这不是另一次独立 native overlay 精度验证。正文没有越过这一边界。 |
| `eq:effect`：EJ−EF=Σg(t−f)(h−EF)/WJ | 正确。最大城市残差 2.71701e-16 m，pooled 残差 4.36933e-17 m；city 和 pooled 各用自身 EF/WJ。失去低于参考均值的支持可提高归一化均值，正文方向正确。 |
| `eq:components`、`eq:CD` 与 `eq:CDdiff` | 单位、分母条件正确。E=CD+ 最大残差 2.22045e-16 m；对称分解最大残差 2.77556e-16 m。W=0 与 W+ =0 已分别处理。C 被限定为模型非零深度支持份额，N 被限定为分配深度 proxy，未伪称真实淹没面积或洪水体积。 |
| `eq:h` RP 梯形加权 | 七 RP 节点及 .098 概率跨度正确。精确权重为 .2551020408163、.4081632653061、.1870748299320、.0510204081633、.0425170068027、.0408163265306、.0153061224490，总和 1。正文六位近似正确；其近似项合计 .999999 是显示精度，不是计算权重错误。 |
| A/F 共同测度及 bounds | F 有明确共同 μF；A 的共同支持作为条件假设书写，另行覆盖归一化不保证 native-area intersection。A bounds 没有被包装为 J 的外部验证；ratio extrema 没有误写成 all-L/all-U 两个端点。 |
| 等预算队列 | 共同 eligible set 是全部 1,259,886 个正 g 单元；ceil(1%)=12,599，两种队列同预算、按键处理并列。不是各自使用不同非零 score 单元作百分比分母。 |
| pooled top1% 结果 | effect queue 绝对效应覆盖 .562789018995、Σgh 覆盖 .209984155276；standard queue 为 .342557768779/.619118482142；overlap=3559/12599=.282482736725。56.28/21.00/34.26/61.91/28.25% 均正确。 |
| GLAD retention 与 composition | `M_l(w)/W(w)` 和 `M_l(w)/M_l(G)` 已分开；五类先在 native paired grid 形成再平均，J/GLAD 同 cell 支持且无 missing；跨产品一致性没有被转述为 accuracy。 |
| 案例选取时间 | 原三城先于本轮追加 joint/diagnostic；Srinagar/Nashik 为事后诊断案例。正文第 187、241、306 行说明一致，没有冒称预注册或独立验证。 |

## 5. 问题关闭与剩余边界

唯一在本审查中提出的 P1 是六城零支持的 scheme 范围，现已关闭。当前快照无其余 P0/P1。没有提出扩大分析范围的请求。

仍应按正文现有边界理解结果：同产品重构、恒等式核验、cross-product 一致性和计算 dossier 不是建设真值、人工影像审核或本地水动力精度验证；本次 PASS 也不改变这些边界。

## 6. Revision memorandum 附加数字核对

2026-10-07 23:24（Asia/Shanghai），补核 `manuscript\Revision_memorandum.tex` 中主文以外的附加数字，未重复主文审查。备忘录 SHA256：`F6166323288224E9C900CCDB4C2E58BF79E03EEE5C6C6B203A5C275D07DEFBB7`。**PASS；没有发现新的 P0/P1。**

| 备忘录位置及附加数字 | 来源的精确值 | 判定 |
|---|---|---|
| 第 239 行 Delhi cancel 93.44% | `diagnostics_city_decomposition.csv`：.9343761648731036 | 通过 |
| 第 239 行 Delhi top10 effect/gh 队列分别覆盖 1.46/0.16% 的绝对表征效应，overlap 1 格 | `diagnostics_queue_coverage.csv`：.014645157663373062/.0015525366083380982；overlap=1 | 通过；两个队列均选 10 格 |
| 第 241 行 Guwahati top10 覆盖 24.77/15.35%，overlap 5 格，gh 队列 Σgh 覆盖 17.60% | 同上：.24773890040930036/.15349576562719794；5；.1760338111199057 | 通过 |
| 第 243 行 Sultanpur top10 effect/gh 队列覆盖 17.50/0%，overlap 0 格，gh 队列 Σgh 覆盖 15.84% | 同上：.17500407683233707/0.0；0；.15842153321546049 | 通过；“none”确为精确零，不是仅因展示精度归零 |
| 第 239 行 Delhi G/J GLAD-new 组成 18.31/26.96% | `diagnostics_glad_class_allocation.csv`，键 `IND_FUA_07466`（表中名称 `Delhi [New Delhi]`）：.1830818232349786/.2696154065509838 | 通过 |
| 第 243 行 Sultanpur G/J GLAD-new 组成 8.78/9.77% | 同上：.08777805200978976/.09770939560041761 | 通过 |
| 第 198 行 pooled GLAD-new 质量 G/J/F/A：58.959/16.174/16.401/16.930 km² | `diagnostics_glad_pooled_class_mass_retention.csv`：58.959346110179596/16.174282295155816/16.400944719246717/16.92998643819729 | 通过；这些是类分配质量，不是城市 GLAD-new 百分数 |
| 第 217 行 pooled 对称项 +.0000659/−.0006576 m | `diagnostics_summary.json`：+.00006587243676277836/−.0006575659606576174 | 通过 |
| 第 69 行最大 rank change=13 | 冻结 `joint_overlay_aggregate_summary.json` 的 J/F 比较 | 通过 |
| 第 232–234 行三城 E 的六位小数、C 的两位百分数，以及第 241/243 行 D+ 的六位小数 | 对照三城 G/J/F/A exposure components | 四舍五入一致 |

上述队列数字全部使用本城 Σ|c_i| 和 Σgh 作为各自覆盖分母，与 pooled 队列的 pooled normalizer 分开；没有将绝对效应覆盖误写为有符号均值变化覆盖。备忘录的 GLAD-new 城市百分数采用 allocation composition，而 pooled 四个质量采用 class-allocated surface；两种定义没有混用。
