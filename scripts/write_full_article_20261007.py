"""Assemble the full research article from the frozen, verified evidence."""
from pathlib import Path
ROOT=Path(r'D:\MLWork\IUFEE_revision_20261005')
author=r'''\author{Junjie Zhang, Yushi Tian, and Zhuo Zeng%
\thanks{J. Zhang is with the Shanghai Academy of Global Governance and Area Studies and the School of Economics and Finance, Shanghai International Studies University, Shanghai 201620, China (e-mail: junjiezhang2024@shisu.edu.cn).}%
\thanks{Y. Tian is with the School of Foreign Languages, Hanshan Normal University, Chaozhou, Guangdong 521041, China (e-mail: 20250075@hstc.edu.cn).}%
\thanks{Z. Zeng is with the School of History and Culture, Hanshan Normal University, Chaozhou, Guangdong 521041, China. Corresponding author: Z. Zeng (e-mail: zzhn1917@hstc.edu.cn).}}
'''
header=r'''\documentclass[journal]{IEEEtran}
\usepackage{cite,graphicx,amsmath,amssymb,booktabs,array,url}
\usepackage[hidelinks]{hyperref}
\graphicspath{{figures/}}
\input{revision_numbers.tex}
\raggedbottom
\title{Spatial Support Assumptions in Urban Change Exposure: An Audit of 91 Indian Cities}
'''+author
body=r'''
\begin{document}
\maketitle
\begin{abstract}
Urban change exposure estimates link products describing different objects, periods and spatial supports. We audit these choices in 91 Indian functional urban areas, where positive 2015--2020 Global Human Settlement Layer building surface differences total 400.536 km$^2$. A controlled experiment compares the joint intersection of World Settlement Footprint maps with the product of their marginal fractions on the same grid. Preserving joint locations reduces allocated support by 4.00\%. City mean-depth differences have median absolute value 0.0023 m and maximum 0.2132 m, despite rank correlation 0.9977. The pooled difference is only $-0.0006$ m because positive and negative spatial contributions cancel by 97.3\%. Separating nonzero model-depth support from conditional depth explains why reduced support can raise a city mean. A paired Global Land Analysis and Discovery (GLAD) 2015/2020 assessment places 19.16\% of jointly screened allocation in new-built classes and most of the remainder in stable-built classes. Screening retains only 27.43\% of original allocation associated with GLAD new-built classes. Compatibility bounds, coding tests and hazard alternatives expose further sensitivity. Three city examples produce traceable cell dossiers and task-specific review queues. The contribution is a controlled audit of spatial representation and a reproducible way to locate its consequences, with claims limited to declared source products rather than verified construction or local flood accuracy.
\end{abstract}
\begin{IEEEkeywords}
Urban change, spatial support, settlement mapping, fluvial exposure, source uncertainty.
\end{IEEEkeywords}

\section{Introduction}
Urban growth can place additional buildings and residents in flood-prone locations. Global studies have documented settlement growth in hazard zones \cite{Rentschler2023} and increases in the population exposed to observed floods \cite{Tellman2021}. Recent analyses compare exposure across the Global South and Global North \cite{Zhang2025} and model future urban area and population in relation to floods and landslides \cite{Koomen2026}. Such evidence makes the linkage between settlement and hazard data consequential: an apparent change in exposure may reflect development, a change in the mapped object, or the assumptions used to combine products.

Two distinctions are especially relevant. First, building surface, settlement footprint and a built-up land-cover class are different measurements. Additional building surface can occur inside a previously mapped settlement, while a land-cover transition can include roads and mixed pixels. Second, product epochs and spatial resolutions do not specify a common observation process. A temporally modelled 2020 building surface estimate, a 2019 settlement footprint and a history of detection through 2015 provide complementary evidence, but together they do not identify the date of construction. Community-based comparisons also show that the suitability of global urban data varies with the urban environments being represented \cite{TrentoOliveira2026}.

A further problem arises after data registration. Storing the fraction of a cell covered by each source is convenient, but separate fractions omit the locations where source classes coincide. Multiplying those fractions supplies an overlap convention. It need not recover the intersection available from a joint overlay of the maps. The resulting difference can propagate into a depth-weighted city summary through both its numerator and denominator. High correlation between city summaries provides little information about whether local positive and negative effects have offset one another.

The exposure studies above establish the importance of settlement growth and the changing distribution of exposed populations. They are not proposed as inaccurate because they use overlays. Our question is narrower: how much does reducing joint source locations to marginal fractions alter a declared urban-change exposure calculation, and where does that alteration occur? A controlled comparison must hold the building surface difference, hazard depths, target cells and source registration fixed. Comparing products with different preprocessing alone would not isolate this effect.

We address this question by redeveloping the India Urban Flood Exposure Evidence (IUFEE) linkage for 91 Indian functional urban areas. We reconstruct joint source support, compare it with same-grid marginal multiplication, and separate this contrast from differences involving archived fractions. Standard compatibility bounds characterize what the archived marginals permit; exact decompositions locate the effects on normalized depth. A complete paired GLAD comparison evaluates the source interpretation across another mapping pipeline. Finally, three city examples demonstrate concrete source-review outputs. The contribution is the measured consequence of a specific information reduction, together with retained joint-state data and a reproducible diagnostic workflow. The study does not introduce a classifier or claim a new mathematical bound.

\section{Data and Scope}
\subsection{Study frame and measured quantity}
The study frame comprises the 91 Indian functional urban areas (FUAs) in GHS-FUA R2019A whose 2015 populations are at least one million \cite{GHSFUA2019}. It is a frozen product-based frame, rather than a list of all current Indian cities. Figure~\ref{fig:frame} shows all 91 centroids and the three application cities. The unit boundaries determine the included cells throughout the comparisons.

The Global Human Settlement Layer (GHSL) GHS-BUILT-S R2023A supplies building surface in m$^2$ on a 100 m World Mollweide grid \cite{GHSLBuiltS2023,GHSLDataPackage2023}. For cell $i$, we define
\begin{equation}
g_i=\max(B_{i,2020}-B_{i,2015},0).
\label{eq:g}
\end{equation}
The five-year epochs use temporal modelling of Landsat and Sentinel-2 observations. Thus, $g_i$ is a positive within-product difference, not a difference between independently observed building inventories. The analysed support contains 1,259,886 cells with $g_i>0$. Their total of 400.536 km$^2$ is the quantity to be allocated under alternative source assumptions. It is not an unbiased estimate of confirmed construction during 2015--2020.

\begin{figure*}[!t]
\centering\includegraphics[width=\textwidth]{figure_1_frame.pdf}
\caption{Study frame and source periods. (a) All 91 FUA centroids; orange points identify Delhi, Guwahati and Sultanpur. The China--India boundary follows the Chinese official standard map GS(2023)2761 \cite{MNRStandardAsia2023}. National-boundary and coastline vectors are extracted from that source and rendered with the study points. (b) GHSL modelled epochs, WSF historic detection and 2019 endpoint, paired GLAD classes, and static GloFAS hazard. Evolution begins in 1985, outside the displayed axis. Connecting epochs identifies a comparison period, rather than a confirmed construction event.}
\label{fig:frame}
\end{figure*}

\begin{table*}[!t]
\caption{Input objects and their roles in the audit}
\label{tab:sources}\centering\small
\begin{tabular}{>{\raggedright\arraybackslash}p{.19\textwidth}>{\raggedright\arraybackslash}p{.20\textwidth}>{\raggedright\arraybackslash}p{.23\textwidth}>{\raggedright\arraybackslash}p{.28\textwidth}}
\toprule
Product & Recorded support & Role & Interpretation constraint\\
\midrule
GHS-BUILT-S R2023A & 100 m; modelled 2015 and 2020 epochs & Positive building surface difference $g$ & Modelled surface change is not verified dated construction.\\
WSF Evolution & 30 m; detection history through 2015 & Historic positive indicator $P$ & Complement of detection is unresolved history, not confirmed absence.\\
WSF 2019 & 10 m; 2019 endpoint footprint & Documented settlement indicator $S$ & A 2019 footprint does not confirm a change ending in 2020; code 1 is unassigned.\\
GloFAS Flood Hazard v2.1.2 & About 90 m output; seven static return periods & Modelled fluvial depth $h$ & Undefended global river hazard omits local processes and protection.\\
GLAD GLCLU v2 & Native 0.00025$^\circ$; paired 2015/2020 classes & Cross-product state comparison & Built-up class includes roads and mixed pixels; no independent construction truth.\\
\bottomrule
\end{tabular}
\end{table*}

\subsection{Settlement evidence and source integrity}
World Settlement Footprint (WSF) Evolution records 30 m settlement detections through 2015, while WSF 2019 supplies a separate 10 m endpoint footprint \cite{WSFEvolution2021,WSF2019}. Table~\ref{tab:sources} distinguishes their roles. The original archived representation average-registers native class indicators to GHSL cells and stores endpoint documented settlement support $s_i^A$, undocumented endpoint fraction $u_i^A$, and positive historic-detection fraction $p_i^A$. Endpoint support is documented coverage multiplied by settlement fraction within that coverage. Supplementary Section S1 describes the separate valid-coverage normalization and averaging of valid tile components. The superscript $A$ distinguishes these archived fractions from the common-grid experiment below.

Native WSF 2019 codes 0 and 255 have documented class meanings. Code 1 occurs in 52 of 56 source tiles, comprising 134,285 native pixels in the audited tiles; its semantic meaning remains unassigned. Base-raster reads, repeated native-block counts and valid-pixel masks show that the anomaly is not solely a consequence of reading an overview. Repeated blocks reproduce the earlier counts and file identities, but these checks cannot establish how the values were generated. We retain their fraction and vary its treatment explicitly. Likewise, zero in WSF Evolution is treated as the complement of positive historic detection, without assigning it a confirmed nonsettlement meaning.

The reconstructed overlay verifies all used source identities against the acquisition record. Full coverage and class-partition checks pass for all 91 FUAs. Supplementary Section S11 documents the input checks and official-source recovery where required. These checks establish the identity and computational integrity of the evaluated inputs; they do not establish thematic accuracy.

\subsection{Hazard and paired land-cover data}
The Global Flood Awareness System (GloFAS) Flood Hazard v2.1.2 supplies static, undefended fluvial depths for return periods (RPs) of 10, 20, 50, 75, 100, 200 and 500 years \cite{Baugh2026}. Its approximately 90 m (3 arcsec) hydraulic raster is distinct from the coarser hydrological forcing and covers rivers with upstream areas of at least 500 km$^2$. The 100 m analysis grid does not improve its effective hydraulic information. We use nearest registration for cell-level comparisons, retain valid dry zeros, and preserve missingness rather than recoding it as zero. All analysed positive-$g$ cells have finite values for the seven depths. Quality assurance (QA) flags for permanent water and spurious depth remain available for diagnostics.

The Global Land Analysis and Discovery (GLAD) GLCLU v2 land-cover maps provide 2015 and 2020 observations on a native 0.00025-degree grid \cite{Potapov2022,GLADv2Download}. Built-up code 250 includes roads and mixed land-cover pixels. We classify the two years jointly on the native grid as new built, stable built, absent in both, built loss, or missing pair, before averaging the five indicators onto GHSL cells. This order retains paired support and avoids multiplying separately averaged class fractions. The comparison uses another mapping pipeline, but shared Landsat inputs and incomplete public documentation of the v2 2015 training lineage preclude a claim of statistical independence.

\section{Methods}
\subsection{A controlled comparison of joint and marginal support}
Both WSF categorical maps are nearest-registered to a common 10 m World Mollweide grid nested within each 100 m GHSL cell. The resulting 100 subcells have uniform measure $1/100$. Nearest registration is a declared rasterization of the parent maps; it does not increase the native 30 m information in Evolution. Overlapping tiles use lexicographic first-valid merging. Missing-source sentinels remain separate from valid class zero, and coverage and overlapping binary-class conflicts are audited.

Let $S_{ij}$ indicate documented WSF 2019 settlement and $P_{ij}$ positive historic detection at fine subcell $j$. On this explicit common support,
\begin{align}
s_i^F&=\frac{1}{100}\sum_{j=1}^{100}S_{ij},\quad
p_i^F=\frac{1}{100}\sum_{j=1}^{100}P_{ij},\\
t_i^F&=\frac{1}{100}\sum_{j=1}^{100}S_{ij}(1-P_{ij}).
\label{eq:joint}
\end{align}
The evaluated weights are
\begin{equation}
w_i^J=g_it_i^F,\quad w_i^F=g_is_i^F(1-p_i^F),\quad
w_i^A=g_is_i^A(1-p_i^A).
\label{eq:weights}
\end{equation}
Here $J$ preserves joint map locations, $F$ multiplies marginals on exactly the same fine grid, and $A$ uses the archived marginals. The $J-F$ contrast isolates replacing a joint intersection by the product of its marginals under fixed maps and registration. The $F-A$ contrast also includes registration and merging differences and is interpreted separately. Unscreened $G$ denotes $w_i^G=g_i$.

Writing $f_i^F=s_i^F(1-p_i^F)$ gives the exact relation
\begin{equation}
t_i^F-f_i^F=-\operatorname{Cov}_{\mu_i^F}(S,P).
\label{eq:cov}
\end{equation}
Thus, positively associated endpoint settlement and historic detection reduce the joint complement relative to marginal multiplication. The sign describes map configuration, rather than classification error. These weights proportionally allocate the cell-level quantity $g_i$; even $J$ does not locate the added building surface within the 100 m cell. The reconstructed derivatives therefore retain $t^F$, both marginals, undocumented fraction and coverage, rather than only their final product.

\subsection{What the depth summary measures}
For $r_k\in\{10,20,50,75,100,200,500\}$ and $x_k=1/r_k$, the finite probability-coordinate depth summary is
\begin{equation}
h_i=\frac{\sum_{k=1}^{6}(d_{i,r_k}+d_{i,r_{k+1}})(x_k-x_{k+1})/2}{0.1-0.002}.
\label{eq:h}
\end{equation}
The trapezoid linearly interpolates in exceedance-probability coordinates. Equivalently, it is a weighted mean of the seven supplied depths with respective weights approximately 0.255102, 0.408163, 0.187075, 0.051020, 0.042517, 0.040816 and 0.015306. The nonnegative weights sum to one; they depend only on the fixed probability nodes. The statistic compares supplied model layers over probabilities 0.002--0.1. It excludes the remaining probability range and is not annual expected loss, total flood risk, or a calibrated random-depth expectation.

For any declared weights $w$ in city $c$, we retain
\begin{equation}
W_c=\sum_{i\in c}w_i,\quad N_c=\sum_{i\in c}w_ih_i,\quad
E_c=N_c/W_c.
\label{eq:components}
\end{equation}
$W$ is allocated weight mass in m$^2$, $N$ is its depth-weighted proxy in m$^3$, and $E$ is the mean modelled depth over that allocation. The units of $N$ do not make it floodwater volume. A positive $W$ is required; zero denominators yield undefined means.

To separate the prevalence of nonzero modelled depth from its magnitude, define $W_c^+=\sum_iw_i\mathbf{1}(h_i>0)$, $C_c=W_c^+/W_c$, and $D_c^+=N_c/W_c^+$. When $W_c^+>0$,
\begin{equation}
E_c=C_cD_c^+.
\label{eq:CD}
\end{equation}
$C$ is the fraction of declared allocation on modelled nonzero-depth support, and $D^+$ is its conditional modelled depth. Neither measures actual inundation frequency or observed flooded area. If $W^+=0$ with positive $W$, $E=0$ and $D^+$ remains undefined. For $J-F$ where both conditional means exist, the symmetric identity
\begin{align}
E_J-E_F={}&(C_J-C_F)(D_J^++D_F^+)/2\nonumber\\
&+(D_J^+-D_F^+)(C_J+C_F)/2
\label{eq:CDdiff}
\end{align}
attributes the difference to changes in support share and conditional depth without choosing either representation as the decomposition reference.

\subsection{Locating and bounding representation effects}
The exact city-level centered identity
\begin{equation}
E_J-E_F=\sum_{i\in c}\underbrace{\frac{g_i(t_i^F-f_i^F)(h_i-E_F)}{W_J}}_{c_i}
\label{eq:effect}
\end{equation}
links the difference to source covariance and the placement of modelled depth. Losing support above $E_F$ lowers the mean; losing it below $E_F$ raises the mean. We retain signed $c_i$, absolute contributions, and cancellation $1-|\sum c_i|/\sum|c_i|$ where the denominator is positive. City and pooled contributions use their respective normalizers. The pooled mean is a ratio of pooled sums, not the mean or median of the city means.

When only archived fractions remain, standard Fr\'echet bounds \cite{Frechet1935} yield
\begin{equation}
L_i^A=\max(0,s_i^A-p_i^A)\leq t_i^A\leq
U_i^A=\min(s_i^A,1-p_i^A).
\label{eq:bounds}
\end{equation}
For the archived representation, these bounds are conditional on treating recorded fractions as marginals under a common normalized support measure. Separate coverage normalization does not establish an exact native-area intersection. By contrast, the common-grid experiment specifies that measure explicitly in (\ref{eq:joint}). Archived compatibility intervals need not contain $J$, which uses a different registration.

We minimize and maximize $\sum_i g_it_i^Ah_i/\sum_i g_it_i^A$ over the compatible box with positive denominator. All-$L$ and all-$U$ allocations are generally not the ratio extrema. The solver uses the parameterized residual $\sum_i g_it_i^A(h_i-e)$ and bisection in $e$, following the standard fractional-programming equivalence \cite{Dinkelbach1967}; it is not a claim to a new optimization algorithm. Supplementary Section S2 provides endpoint choices, zero-denominator cases and synthetic vertex checks. These conditional intervals describe lost overlap information under recorded inputs. They do not incorporate thematic or hydraulic error distributions.

\subsection{Cross-product allocation and sensitivity design}
Let $z_{i\ell}$ be the jointly classified GLAD fraction of class $\ell$. For each of $G,J,F,A$, we compute $M_\ell(w)=\sum_iw_iz_{i\ell}$ and the composition $M_\ell(w)/W(w)$. We also report $M_\ell(w)/M_\ell(G)$ to show how much original allocation in each class survives screening. An increased class share can coincide with decreased absolute allocation, so both are required. Exact cell keys, $g$, $h$ and centers are checked before the J/GLAD join. Positive-$g$ and zero-change cells are compared using unweighted paired GLAD-new fractions within each city; this is a descriptive spatial comparison, not a randomized contrast.

The archived four-weight design $g$, $gs^A$, $g(1-p^A)$ and $gs^A(1-p^A)$ isolates the inclusion of endpoint and historic screens. It is a factorial diagnostic, not a calibrated probability model. We vary exponents in $g(s^A)^\alpha(1-p^A)^\beta$, with $\alpha,\beta\in\{0,0.5,1,2\}$, and endpoint thresholds in $g\mathbf{1}(s^A\geq\tau)(1-p^A)$, with $\tau=0.25,0.5,0.75$. Exponent zero omits the factor. Further tests vary minimum $g$, assignments of undocumented support, historic-zero treatment, individual RPs, uniform depth averaging, hazard registration and quality-flag exclusions. Results retain defined-city counts, absolute depth differences and ranks. These deterministic alternatives do not justify sampling confidence intervals.

The applications use two transparent audit priorities. The original queue ranks cells by $g_ih_i$ to inspect large unscreened depth-proxy contributions. A separate queue ranks $|c_i|$ to inspect large effects of the representation choice. We compare equal budgets of ten cells, the top 1\% and the top 10\%, rounding fractional cell counts upward and resolving ties by cell key. Queue coverage is computed against both $\sum|c_i|$ and $\sum g_ih_i$. Neither ranking has been validated as a superior hazard-monitoring or intervention rule.

\section{Results}
\subsection{Controlled joint-support comparison}
The frozen inputs reproduce the original GHSL total, and the maximum discrepancy in reconstructed original city depths is below $4\times10^{-9}$ m. All 91 reconstructed overlays have complete paired WSF coverage. The same 1,259,886 positive-$g$ cells align exactly with the GLAD comparison, with complete paired GLAD coverage. These results establish that subsequent contrasts do not arise from differing cell samples.

Table~\ref{tab:pooled} shows the effect on both scale and normalized depth. Joint support $J$ allocates 84.434 km$^2$, compared with 87.956 km$^2$ under same-grid marginal multiplication $F$, a reduction of 4.00\% relative to $F$. The $F-A$ support difference is $-2.54$\% relative to $A$; it includes changed registration and merging conventions. The $J-F$ controlled contrast is therefore essential to assigning a difference to joint-location loss.

\begin{table}[!t]
\caption{Pooled allocation and depth components across 91 cities}
\label{tab:pooled}\centering\small
\begin{tabular}{lrrrrr}
\toprule
Scheme & $W$ & $N$ & $C$ & $D^+$ & $E$\\
 & (km$^2$)&($10^6$ m$^3$)&(\%)&(m)&(m)\\
\midrule
$G$ &400.536&81.372&18.540&1.0958&0.2032\\
$J$ &84.434&16.591&18.331&1.0720&0.1965\\
$F$ &87.956&17.335&18.324&1.0755&0.1971\\
$A$ &90.244&17.797&18.390&1.0724&0.1972\\
\bottomrule
\end{tabular}
\parbox{\columnwidth}{\footnotesize $W$: allocated support; $N$: depth-weighted proxy; $C$: share on nonzero modelled-depth support; $D^+$: conditional depth; $E=N/W=CD^+$. All use pooled sums. These are arithmetic allocations, not measured construction or floodwater volumes.}
\end{table}

Across cities, $J-F$ has median absolute difference 0.0023 m and maximum absolute difference 0.2132 m in Srinagar. The Spearman correlation is 0.9977; 42 ranks change and nine of the ten highest cities are retained. Rank and depth changes answer different questions. Srinagar has the largest absolute depth difference but remains rank 7. Nashik moves from rank 63 under $F$ to rank 76 under $J$, although its depth falls by only 0.0069 m, from 0.0082 to 0.0013 m. A crowded part of the distribution can therefore generate a large rank change from a small depth change.

Figure~\ref{fig:representation}(a) displays every signed city difference. The pooled shift is only $-0.000592$ m, comprising positive centered contributions of 0.010666 m and negative contributions of $-0.011258$ m. Their absolute total is 0.021923 m, implying 97.3\% cancellation. This does not establish thematic error at those locations; it shows why the pooled normalized summary conceals stronger opposing effects of the representation choice. The 1\% of cells with largest absolute pooled contributions accounts for 56.28\% of their total absolute magnitude.

\begin{figure*}[!t]
\centering\includegraphics[width=.96\textwidth]{figure_4_representation.pdf}
\caption{Consequences of replacing joint support with same-grid marginal multiplication. (a) All 91 signed city-depth differences, ordered by value. (b) Symmetric decomposition into nonzero model-depth support share and conditional depth for five diagnostic cities. The original three application cities are retained; Srinagar and Nashik are added post hoc to illustrate the largest depth and rank changes. (c) Positive, negative and net centered contributions using pooled normalization. Cancellation is $1-|\sum c_i|/\sum|c_i|$. (d) Coverage of the absolute representation effect and unscreened depth numerator by two equal-budget pooled queues; top 1\% means 12,599 cells. The queues address different review tasks.}
\label{fig:representation}
\end{figure*}

The factor decomposition makes the direction interpretable. In Srinagar, $C$ falls from 46.32\% to 41.03\%, and $D^+$ from 1.9314 to 1.6609 m. The symmetric contributions are $-0.0951$ and $-0.1181$ m, respectively. In Guwahati, both components increase: $C$ rises from 73.47\% to 75.66\%, and $D^+$ from 1.5062 to 1.5312 m, contributing 0.0333 and 0.0186 m. Reduced allocated mass therefore need not lower the normalized depth. Six cities have zero nonzero-depth support under J/F; their means are zero and their conditional depths and symmetric decompositions remain undefined, rather than being imputed.

\subsection{What the additional product supports}
Under $G$, GLAD new-built, stable-built, absent-both and built-loss classes receive \GLADNewPct\%, \GLADStablePct\%, \GLADAbsentPct\% and \GLADLossPct\% of allocated GHSL differences. Under $J$, the new-built share is 19.16\%, compared with 18.65\% under $F$ and 18.76\% under $A$ (Fig.~\ref{fig:glad}). Most jointly screened allocation still lies within stable-built classes. Such coexistence is compatible with infill, densification, different mapped objects or source error; it does not by itself choose among them.

The change in composition must be read alongside the loss of allocated mass. Relative to $G$, $J$ retains 27.43\% of allocation associated with GLAD new-built classes, 23.56\% associated with stable-built classes and 10.09\% associated with absent-both classes. Although the new-built share is higher under $J$ than $F$, its absolute allocation is lower: 16.174 versus 16.401 km$^2$. Screening can concentrate a class while discarding much of its original allocation. These results undermine interpreting the screen as a validated rule for identifying construction, while making its arithmetic selectivity explicit.

The unweighted paired GLAD-new fraction is 9.97\% among positive-change cells and 3.28\% among zero-change cells, a pooled descriptive ratio of 3.04. Figure~\ref{fig:glad}(c) retains the city-level contrasts so that this pooled ratio is not mistaken for a universal local relation. The calculations show cross-product association on declared spatial support. They do not quantify the fraction of the 400.536 km$^2$ that is erroneous or independently verify its timing.

\begin{figure*}[!t]
\centering\includegraphics[width=\textwidth]{figure_5_glad.pdf}
\caption{Paired GLAD 2015/2020 evidence on the complete positive-change support. (a) Class composition of each allocated weight mass; $G$, $J$, $F$ and $A$ are defined in (\ref{eq:weights}). Built loss is below 0.01\% and is retained even though its segment is visually negligible; missing-pair allocation is zero. (b) Retained allocation within each GLAD class relative to $G$. A higher composition share does not imply more retained mass. (c) City-level GLAD-new fractions in positive-$g$ versus zero-change cells, using cell fractions without $g$ weighting; the dashed line is equality. These are product comparisons, not accuracy estimates.}
\label{fig:glad}
\end{figure*}

\subsection{Archived compatibility and source-code choices}
The archived lower, product and upper weight masses total 79.853, 90.244 and 99.605 km$^2$. All cities have positive lower mass, but the marginals do not completely identify intersection weights in any city. Six cities have degenerate depth intervals because the depth outcome can be invariant despite overlap ambiguity. Optimized interval width has median 0.0482 m, interquartile range 0.0035--0.1184 m, and exceeds or equals 0.05 m in 44 cities. The widest interval, Srinagar's 0.1791--2.1593 m, surrounds its archived product value of 0.8893 m. It is a conditional compatibility range under the archived common-measure assumption, not a confidence interval or validation target for the differently registered $J$.

Undocumented WSF endpoint support accounts for only 0.033143\% of pooled GHSL weight. Yet assigning all of it to settlement changes a product-weighted city depth by up to 0.0286 m. Allowing arbitrary assignments within its recorded fraction produces a maximum compatible width of 0.0383 m in Mangaluru. The combination of a small pooled fraction and a locally influential denominator explains why reporting the total anomaly alone is insufficient.

Renaming historic zeros as nonsettlement without changing their weights has no numerical effect. Excluding unresolved history and then removing all positive historic detections leaves no retained weight in any city. Omitting the historic screen instead changes endpoint-weighted city depth by up to 0.2079 m. These alternatives demonstrate what the zero-code interpretation does to the calculation. None establishes whether an unresolved cell was genuinely nonsettled in 2015, and a historic screen can remove legitimate later infill.

\subsection{Threshold and hazard sensitivity}
The 15 nonreference exponent choices yield rank correlations of 0.9866--0.9990 with $A$. Binary endpoint screens are less stable (Table~\ref{tab:sensitivity}). At a threshold of 0.75, one Kolkata FUA (10453) and Kolhapur have zero retained denominator; the 89 defined cities have rank correlation 0.7948, and only six of the original ten highest cities remain. Raising the GHSL difference threshold to 500 m$^2$ retains 78.11\% of positive GHSL weight and changes a product-weighted city depth by up to 0.0734 m. Correlation alone therefore does not summarize sensitivity to screening.

\begin{table}[!t]
\caption{Sensitivity relative to the archived product calculation}
\label{tab:sensitivity}\centering\footnotesize
\begin{tabular}{lrrrr}
\toprule
Alternative & $n$ & $\rho$ & Median $|\Delta|$ & Maximum $|\Delta|$\\
 & & & (m) & (m)\\
\midrule
Binary $s^A\geq0.25$ &91&0.992&0.006&0.227\\
Binary $s^A\geq0.50$ &91&0.913&0.015&0.573\\
Binary $s^A\geq0.75$ &89&0.795&0.035&1.125\\
Uniform RP mean &91&0.997&0.029&0.643\\
RP100 &91&0.996&0.040&1.012\\
RP500 &91&0.988&0.086&1.623\\
Exclude either QA flag &91&0.984&0.002&0.404\\
\bottomrule
\end{tabular}
\parbox{\columnwidth}{\footnotesize Reference: continuous $A$ weights and the finite probability-coordinate depth mean. $n$ counts defined paired cities; $\rho$ is Spearman correlation. QA excludes an entire target cell if either permanent-water or spurious-depth fraction is positive. Hazard alternatives change the summary definition, not its estimated accuracy.}
\end{table}

Nearest versus average hazard registration gives correlations of 0.9979--0.9993 across the original weights. This indicates stability to the evaluated alignment choice. It cannot test missing drainage, defences or small rivers. Replacing the finite probability-coordinate integral with the uniform RP mean or RP500 changes median $A$ depth from 0.1173 m to 0.1583 or 0.2246 m. These are different hazard summaries and should not be selected by which produces a preferred ranking.

Excluding any cell with either hazard quality flag changes a city estimate by up to 0.4039 m. We identify 2,437 cells with nonmonotonic supplied RP depths, accounting for 0.089864\% of GHSL weight. A cumulative-maximum stress calculation changes $A$ depth by at most 0.00174 m; the primary results retain the supplied depths. These tests quantify available model-layer and aggregation choices. They do not bound error from omitted hydraulic processes.

\section{Application Examples}
Delhi, Guwahati and Sultanpur were selected before the added joint-support and diagnostic analyses: Delhi is the largest population unit, while Guwahati and Sultanpur illustrate the opposing original differences between unscreened and screened means. They are worked examples, not a representative sample of Indian flood settings. Figure~\ref{fig:cases} places their means beside archived compatibility ranges and paired product classes. Table~\ref{tab:cases} separates allocation scale, nonzero-depth support and conditional depth so that the source of a mean difference can be inspected.

\begin{table*}[!t]
\caption{Executed city examples: allocation scale and depth components}
\label{tab:cases}\centering\small
\begin{tabular}{llrrrr|llrrrr}
\toprule
City & Scheme & $W$ & $C$ & $D^+$ & $E$ & City & Scheme & $W$ & $C$ & $D^+$ & $E$\\
 & & (km$^2$)&(\%)&(m)&(m)& & &(km$^2$)&(\%)&(m)&(m)\\
\midrule
Delhi &$G$&51.419&31.347&0.953&0.299&Sultanpur &$G$&1.833&20.336&2.863&0.582\\
 &$J$&11.646&34.015&0.901&0.306& &$J$&0.388&17.437&2.575&0.449\\
 &$F$&12.329&33.618&0.904&0.304& &$F$&0.406&17.053&2.582&0.440\\
 &$A$&12.655&33.719&0.906&0.305& &$A$&0.413&16.996&2.533&0.431\\
\midrule
Guwahati &$G$&0.789&56.328&1.551&0.873&\multicolumn{6}{l}{$W$: declared allocation mass.}\\
 &$J$&0.093&75.664&1.531&1.159&\multicolumn{6}{l}{$C$: fraction on modelled nonzero-depth support.}\\
 &$F$&0.101&73.471&1.506&1.107&\multicolumn{6}{l}{$D^+$: conditional modelled depth on that support.}\\
 &$A$&0.108&73.123&1.502&1.098&\multicolumn{6}{l}{$E=CD^+$; use unrounded values for the identity.}\\
\bottomrule
\end{tabular}
\end{table*}

\subsection{Delhi: separating dated-change claims from source support}
Delhi's unscreened allocation is 51.419 km$^2$, compared with 11.646 km$^2$ under $J$. Its mean depth changes much less, from 0.299 to 0.306 m, because the allocation shifts toward nonzero-depth support while conditional depth decreases. A near-stable normalized mean therefore conceals substantial changes in the amount and location of retained support.

The first two cells in the original $gh$ review queue lie at approximately (77.30714$^\circ$ E, 28.54311$^\circ$ N) and (77.04235$^\circ$ E, 28.56945$^\circ$ N). They have $g=3914$ and 5207 m$^2$ and integrated depths of 4.092 and 2.857 m. Both fall entirely in paired GLAD stable-built support. The executed review output therefore withholds a ``new-settlement'' interpretation for these contributions and retains infill, density change and product-definition differences as alternatives requiring dated reference evidence. The dossier records these source states and cell locators; it does not label either product wrong.

\subsection{Guwahati: explaining a higher screened mean}
Guwahati's $J$ allocation is only 0.093 km$^2$, compared with 0.789 km$^2$ under $G$, yet its mean rises from 0.873 to 1.159 m. The share on nonzero model-depth support rises from 56.33\% to 75.66\%, while conditional depth changes from 1.551 to 1.531 m. The higher normalized mean mainly reflects where the retained allocation lies, rather than deeper hazard throughout the city. Within the controlled $J-F$ contrast, both the support-share and conditional-depth terms contribute positively.

Two of the original ten highest-$gh$ cells carry permanent-water flags equal to one. At queue position 10 (91.68585$^\circ$ E, 26.17208$^\circ$ N), $g=850$ m$^2$ and $h=8.656$ m. Its fine marginals are $s^F=0.13$ and $p^F=0.41$, so the product fraction is 0.0767, while the actual joint fraction is zero. This cell concretely shows support introduced by marginal multiplication. Its supplied RP50 and RP75 depths are 9.552 and 9.424 m, a nonmonotonic decrease of 0.128 m. The dossier therefore identifies both an overlap issue and a flagged hazard profile for reference review. Neither the larger city mean nor the queue supplies a basis for ranking neighbourhood flood risk without local hydraulic and vulnerability information.

\subsection{Sultanpur: detecting a change in the retained population of cells}
Sultanpur shows the opposite direction. Mean depth falls from 0.582 m under $G$ to 0.449 m under $J$. The nonzero-depth support share falls from 20.34\% to 17.44\%, and conditional depth from 2.863 to 2.575 m. Both changes contribute to the difference. Its first queued cell (82.08905$^\circ$ E, 26.27070$^\circ$ N) has $g=3927$ m$^2$, $h=5.801$ m and $t^F=0.35$, but zero GLAD-new fraction. Across its ten queued cells, the median GLAD-new fraction is zero and one cell carries a positive hazard quality flag. The source-review output distinguishes a large depth-proxy contribution from evidence of new settlement, retaining the paired GLAD states and source fractions for each selected cell.

Supplementary Section S12 provides six concrete cell dossiers: the first two queue cells in Delhi and Sultanpur and the two flagged Guwahati cells. Selection uses existing queue rules and flags rather than a claim of independent visual validation. Section S9 maps the original 30 queued cells. The original ten-cell queues cover 0.87\%, 17.60\% and 15.84\% of the respective $gh$ numerators in Delhi, Guwahati and Sultanpur; a fixed cell budget has very different coverage across cities. The alternative representation-effect queue serves a different question. At the pooled 1\% budget, it covers 56.28\% of absolute $J-F$ effect and 21.00\% of the $gh$ numerator; the standard queue covers 34.26\% and 61.91\%, respectively. Only 28.25\% of selected cells overlap. These measured differences justify reporting the audit objective with a queue, rather than treating one score as a universal priority.

\begin{figure*}[!t]
\centering\includegraphics[width=\textwidth]{figure_2_cases.pdf}
\caption{Three original application cities. (a) Unscreened $G$, archived product $A$ and joint overlay $J$ depth summaries, with the conditional compatibility interval from archived marginals. The interval is neither a confidence interval nor a required bound on the differently registered $J$. (b) Paired GLAD 2015/2020 class composition under $G$ and $A$. New denotes non-built in 2015 and built in 2020 under the GLAD class definition; stable does not exclude building infill.}
\label{fig:cases}
\end{figure*}

\section{Discussion}
\subsection{What the controlled experiment adds}
The central finding is that a near-unchanged aggregate depth and a high city-rank correlation can coexist with substantial local representation effects. Equation~(\ref{eq:effect}) explains the mechanism: joint-support differences are weighted by depth relative to the reference mean, so both positive and negative contributions arise. The observed 97.3\% pooled cancellation is a property of this evaluated frame, not a universal constant. It shows why an audit should retain spatial contributions alongside pooled summaries.

The comparison also clarifies the role of simple overlays. A correctly constructed joint overlay already retains map-specific intersection information under its declared registration. The added value here is not replacing that operation with a more complex score. It is quantifying what is lost when a reusable database keeps only marginal fractions, distinguishing that loss from preprocessing differences, and supplying the joint fields and diagnostics needed to recover it. Known covariance and compatibility relations provide the explanation; the controlled full-frame evidence and traceable cell outputs provide the empirical contribution.

The signs and magnitudes are conditional on the evaluated rasterization. Nearest registration on a nested 10 m grid creates a reproducible comparison while retaining the 30 m information limit of Evolution. A finer common grid would not automatically be more accurate. Consequently, we claim an effect under a specified support measure, not stability across every possible resampling or geometry convention. The archived compatibility analysis is useful when parent-map joint states were not retained; its conditional common-measure assumption should accompany any reuse.

\subsection{Temporal interpretation and the role of cross-product evidence}
The GLAD comparison provides a substantive test of the proposed new-settlement interpretation: much of the positive GHSL difference and most screened allocation coincide with stable-built classes. Restoring joint WSF locations does not eliminate this pattern. The explanation cannot be reduced to a single error rate because the mapped objects differ, the inputs can be shared, and infill is possible within a stable footprint. Composition and class-specific retention make this distinction visible: screening raises the proportion associated with GLAD-new support while removing most of its original allocated mass.

Independent reference observations are needed to estimate verified construction area or thematic error. A defensible area-accuracy study would specify a probability sample, temporally suitable and more reliable reference classification, and estimation consistent with the sampling design \cite{Olofsson2014}. Independence of sensor names alone would not guarantee better reference evidence. The present cross-product assessment therefore fulfils a different role: it identifies where product semantics agree or remain ambiguous. Earlier AI-assisted labels were excluded because their generation does not supply the necessary independent reference standard.

\subsection{Using global hazard summaries responsibly}
Reporting $W$, $C$, $D^+$ and $E$ prevents a single normalized depth from carrying incompatible interpretations. Guwahati illustrates concentration of screened support in modelled nonzero-depth cells; Sultanpur illustrates reductions in both that share and conditional depth. Neither establishes a change in actual flood probability. The finite RP integration and the alternative-depth experiments make the summary reproducible, but the global model remains static and undefended, with limited small-river coverage and no local drainage calibration.

Quality flags, RP nonmonotonicity and nearest-versus-average comparisons identify influential choices within the supplied product. They cannot estimate errors from omitted defences, pluvial or coastal flooding, vulnerability, or exposure of particular buildings. Local planning would require suitable hazard validation and information on the assets and populations of interest. Within these limits, the city and cell outputs support source triage, sensitivity reporting and the design of targeted reference review.

\subsection{Reusable data requirements and remaining scope}
A reusable linkage should retain the source periods and classes, joint states or sufficient parent-map locators, a declared support measure, missing-coverage fields, numerator and denominator components, and the exact selection rule behind any review queue. This requirement is more informative than retaining a single evidence-weighted score. It lets another analyst change an interpretation without reconstructing every source decision from the manuscript.

The evaluated frame is limited to 91 product-defined Indian FUAs, one GHSL epoch pair and the stated global hazard release. Full-frame results avoid selecting only favourable cities within that frame, but do not establish transfer to other countries, periods or hazard models. The three original applications and two additional diagnostic cases are explanatory examples rather than independent workflow trials. Their dossiers demonstrate executed, reproducible source review; the benefits of human review efficiency and any improvement in local decisions remain to be evaluated.

\section{Conclusion}
Preserving joint source locations changes the allocated support and, in some cities, the normalized depth of an urban-change exposure linkage even when aggregate rank correlation is high. The 91-city comparison isolates this effect from registration differences, explains its spatial cancellation, and retains the fields needed to reproduce it. Decomposing depth into nonzero model support and conditional magnitude makes the city differences interpretable. Paired product classes and concrete review dossiers constrain dated-change claims and expose what screening retains or removes. These results support a spatial measurement audit of declared products; verified construction and local flood accuracy require additional reference evidence.

\section*{Data and Code Availability}
The original IUFEE v1.2 release is identified by Zenodo doi:10.5281/zenodo.21916290. Revision scripts, joint-support derivatives, cell dossiers, acquisition manifests and reproduction instructions accompany this manuscript. The new revision outputs have not yet been published as a versioned repository release. Parent products retain their provider licences.

\section*{Acknowledgment}
This work received no specific funding. OpenAI Codex assisted source retrieval, code development, deterministic analysis, figure production and manuscript redevelopment. AI-assisted reference labels were excluded from the validation evidence. The authors are responsible for source verification, interpretation and the final manuscript.
\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
'''
(ROOT/'manuscript/IUFEE_redeveloped.tex').write_text(header+body,encoding='utf-8')
print('Full article source written; numerical and layout audit required before delivery.')
