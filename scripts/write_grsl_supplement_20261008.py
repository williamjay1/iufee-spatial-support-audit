"""Keep the extended technical record and prepare a three-page GRSL supplement."""
from pathlib import Path
import zipfile

R=Path(r'D:\MLWork\IUFEE_revision_20261005')
M=R/'manuscript'; T=R/'temp/baseline_20261007'; T.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(R/'IUFEE_revision_review_package.zip') as z:
    for name in ['IUFEE_redeveloped.tex','IUFEE_supplement.tex','Revision_memorandum.tex']:
        p=T/name
        if not p.exists():p.write_bytes(z.read('manuscript/'+name))
technical=M/'IUFEE_technical_record.tex'
if not technical.exists():
    s=(T/'IUFEE_supplement.tex').read_text(encoding='utf-8')
    s=s.replace('Supplementary Material\\\\[3pt]', 'Extended Technical Record\\\\[3pt]')
    s=s.replace('This supplement gives reproducible definitions, numerical checks and conditional sensitivity calculations accompanying the main article.', 'This technical record gives complete reproducible definitions, numerical checks, city diagnostics and conditional sensitivity calculations accompanying the released analysis.')
    technical.write_text(s,encoding='utf-8')

s=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=20mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,amssymb,booktabs,array,graphicx}
\usepackage[hidelinks]{hyperref}
\graphicspath{{figures/}}
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\theequation}{S\arabic{equation}}
\setlength{\parindent}{1em}
\setlength{\parskip}{3pt}
\setlength{\emergencystretch}{2em}
\title{Supplementary Material\\[2pt]\large Spatial Support Assumptions in Urban Change Exposure: An Audit of 91 Indian Cities}
\author{Junjie Zhang, Yushi Tian, and Zhuo Zeng}
\date{}
\begin{document}
\maketitle
\vspace{-3mm}
\section{Additional implementation and numerical checks}
\subsection{Archived registration and common support}
Archived endpoint support is $s_i^A=a_iq_i$, where $a_i$ is documented WSF 2019 coverage and $q_i$ its conditional settlement fraction. The undocumented fraction $u_i^A$ satisfies $a_i+u_i^A=1$ on valid registered coverage. Source indicators are registered by averaging; overlapping tiles contribute the mean of valid registered components. Historic detections and endpoint classes are normalized over their separate valid coverage. The compatibility calculation therefore conditions on treating the recorded marginals as sharing a common normalized measure.

The controlled $J/F$ experiment uses nearest registration to 100 nested 10 m subcells per GHSL cell, with lexicographic first valid merging. Outside coverage has a separate sentinel. The common measure is uniform over those subcells. Source identities, coverage, class partitions and overlapping binary states were checked for all 91 study units. The native 30 m historical map retains its original information content under the chosen registration.

For archived marginals define $L_i=\max(0,s_i^A-p_i^A)$ and $U_i=\min(s_i^A,1-p_i^A)$. Writing $\ell_i=g_iL_i$ and $v_i=g_iU_i$, the city ratio bounds are obtained from the zeros of
\begin{align}
F_-(x)&=\sum_i\ell_i(h_i-x)+\sum_i(v_i-\ell_i)\min(h_i-x,0),\\
F_+(x)&=\sum_i\ell_i(h_i-x)+\sum_i(v_i-\ell_i)\max(h_i-x,0).
\end{align}
Both residuals decrease strictly when $\sum\ell_i>0$, as holds for all 91 units. Bisection uses 65 iterations between eligible depth extrema. If lower mass is zero, the positive mass ratios attain the smallest and largest eligible depths; zero upper mass yields an undefined ratio. Assigning all lower or all upper weights produces endpoint scenarios, while optimizing the ratios permits different endpoint assignments across cells.

The solver agreed with exhaustive enumeration in 96 synthetic examples comprising 2,016 positive denominator vertices to $1.78\times10^{-15}$. The pooled lower, archived product and upper masses are 79.852620, 90.243923 and 99.604911 km$^2$. These calculations characterize representation compatibility conditional on recorded marginals.

\subsection{Depth and diagnostic identities}
The normalized trapezoidal depth summary gives the RP10, 20, 50, 75, 100, 200 and 500 layers approximate weights 0.255102, 0.408163, 0.187075, 0.051020, 0.042517, 0.040816 and 0.015306. Their exact values sum to one. Valid dry zeros remain in the allocation denominator, while missing values remain distinct. Every positive GHSL record has finite values in all seven layers.

With $W^+=\sum_iw_i\mathbf{1}(h_i>0)$, define $C=W^+/W$ and $D^+=N/W^+$ whenever $W^+>0$. When $W>0$ and $W^+=0$, $E=0$ and $D^+$ is undefined. Six cities have this condition under $J/F$. The symmetric decomposition is
\[
E_J-E_F=\tfrac12(C_J-C_F)(D_J^++D_F^+)
+\tfrac12(D_J^+-D_F^+)(C_J+C_F).
\]
Its maximum numerical residual is $2.78\times10^{-16}$ m. Joint and GLAD tables share all 1,259,886 keys, GHSL differences, depths and cell centres. Paired GLAD coverage is complete; the maximum class partition residual is $4.47\times10^{-8}$.

\newpage
\section{Additional sensitivity and selected cells}
Table~\ref{tab:stress} collects alternatives to the archived allocation $A$ with nearest depth registration. Median and maximum changes are absolute paired city depth differences, in metres. Rank correlations use finite paired ratios; each alternative changes the declared representation or depth definition.

\begin{table}[htbp]\centering\small
\caption{Additional sensitivity summaries}\label{tab:stress}
\setlength{\tabcolsep}{6pt}
\begin{tabular}{@{}lrrrr@{}}\toprule
Alternative & Cities & $\rho$ & Median change & Maximum change\\\midrule
Binary threshold 0.25 & 91 & 0.991894 & 0.005806 & 0.226719\\
Binary threshold 0.50 & 91 & 0.913297 & 0.015426 & 0.573101\\
Binary threshold 0.75 & 89 & 0.794784 & 0.035029 & 1.124503\\
Uniform mean of RP depths & 91 & 0.996925 & 0.029255 & 0.643423\\
RP500 layer & 91 & 0.988052 & 0.085783 & 1.622536\\
Either QA flag excluded & 91 & 0.983767 & 0.002152 & 0.403928\\
\bottomrule\end{tabular}
\end{table}
Binary weights are $g_i\mathbf{1}(s_i^A\geq\tau)(1-p_i^A)$. A threshold of 0.75 leaves zero total mass in Kolkata (FUA 10453) and Kolhapur (FUA 07881). The exponent family uses $g_i(s_i^A)^\alpha(1-p_i^A)^\beta$ with $\alpha,\beta\in\{0,0.5,1,2\}$; zero exponents omit the corresponding factor. Its 15 alternatives to $\alpha=\beta=1$ give rank correlations 0.986632 to 0.998980. Retaining only $g_i>500$ m$^2$ retains 78.106963\% of original mass and changes $E_A$ by at most 0.073378 m. Across the four archived weighting schemes, nearest versus average depth registration gives correlations 0.997878 to 0.999327.

Native WSF 2019 code 1 occurs in 52 of 56 source tiles and 134,285 native pixels. Its registered support is 0.033143\% of the GHSL mass. Assigning every undocumented cell portion to settlement changes city depth by at most 0.028626 m; arbitrary endpoint treatment gives maximum conditional width 0.038272 m. Omitting the historic screen changes endpoint weighted city depth by at most 0.207904 m relative to $A$. There are 2,437 nonmonotone depth profiles, representing 0.089864\% of GHSL mass; cumulative maximum replacement changes $E_A$ by at most 0.001735 m.

Table~\ref{tab:dossiers} retains the six selected cells discussed in the Letter. Orders refer to each city's original descending $g_ih_i$ queue. Delhi and Sultanpur use orders 1 and 2; Guwahati uses the two QA positive cells, orders 9 and 10. Longitude and latitude are cell centres in degrees, $g$ is m$^2$, $h$ is metres, and $t$ is the common grid joint fraction. GLAD entries are paired class fractions. PW and SP denote permanent water and spurious depth source flags.

\begin{table}[htbp]\centering\footnotesize
\caption{Selected source review cells}\label{tab:dossiers}
\setlength{\tabcolsep}{3.4pt}
\begin{tabular}{@{}lcrrrrrrrc@{}}\toprule
City & Order & Longitude & Latitude & $g$ & $h$ & $t$ & New (\%) & Stable (\%) & PW/SP\\\midrule
Delhi & 1 & 77.30714 & 28.54311 & 3914 & 4.092 & .700 & 0.0 & 100.0 & 0/0\\
Delhi & 2 & 77.04235 & 28.56945 & 5207 & 2.857 & .850 & 0.0 & 100.0 & 0/0\\
Guwahati & 9 & 91.67903 & 26.17123 & 950 & 8.511 & .000 & 0.0 & 81.6 & 1/0\\
Guwahati & 10 & 91.68585 & 26.17208 & 850 & 8.656 & .000 & 0.0 & 70.6 & 1/0\\
Sultanpur & 1 & 82.08905 & 26.27070 & 3927 & 5.801 & .350 & 0.0 & 37.5 & 0/0\\
Sultanpur & 2 & 82.08380 & 26.27576 & 2687 & 7.301 & .260 & 4.1 & 93.9 & 0/0\\
\bottomrule\end{tabular}
\end{table}
For Guwahati order 10, $s^F=.13$ and $p^F=.41$ give marginal product .0767 with joint fraction zero. RP50 and RP75 depths are 9.552 and 9.424 m. Delhi's two cells have stable built fraction one. The dossiers retain archived and common grid fractions separately and identify concrete source states for further reference review.

\newpage
\section{Additional city summaries and review queues}
Figure~\ref{fig:case-summary} shows the original three city depth summaries under the archived weight alternatives. This additional display accompanies the controlled $J/F$ comparison in the Letter. An allocated mean changes through the composition of retained cells as well as the magnitude of their depths.
\begin{figure}[htbp]\centering
\includegraphics[width=\linewidth]{figure_2_cases.pdf}
\caption{Additional allocation summaries in three cities. Panel a compares GHSL, joint and archived depth summaries with archived compatibility intervals. Panel b gives paired GLAD class composition under GHSL and archived weights. Weights and depths follow the definitions in the Letter.}\label{fig:case-summary}
\end{figure}

The standard queue ranks descending $g_ih_i$; the representation queue ranks descending absolute centred $J/F$ contribution using the corresponding city mean. Ties use stable unit, row and column keys. Table~\ref{tab:queues} compares equal ten cell budgets. Effect coverage uses each city's $\sum_i|c_i|$; standard depth coverage uses its $\sum_ig_ih_i$. Coverage therefore measures the objective for which a queue was constructed.
\begin{table}[htbp]\centering\small
\caption{Equal budget review queue coverage}\label{tab:queues}
\setlength{\tabcolsep}{6pt}
\begin{tabular}{@{}lrrrr@{}}\toprule
City & Representation effect & Standard effect & Standard depth & Shared cells\\
 & coverage (\%) & coverage (\%) & coverage (\%) & of ten\\\midrule
Delhi & 1.46 & 0.16 & 0.870 & 1\\
Guwahati & 24.77 & 15.35 & 17.603 & 5\\
Sultanpur & 17.50 & 0.00 & 15.842 & 0\\
\bottomrule\end{tabular}
\end{table}
At the pooled top 1\% budget, both queues contain 12,599 cells. The representation queue covers 56.2789\% of absolute effect and 20.9984\% of the standard numerator; the standard queue covers 34.2558\% and 61.9118\%, respectively. Their overlap is 28.2483\%. These distinct selections support source review for distinct objectives.

Paired GLAD new class allocation masses are 58.959346, 16.174282, 16.400945 and 16.929986 km$^2$ under $G/J/F/A$. The corresponding new class composition under $J$ is 19.1560\%, while its new class retention relative to $G$ is 27.4329\%. Stable built and absent in both retention under $J$ are 23.5640\% and 10.0942\%. The separate reporting of composition and retained mass explains how screening can increase a class share while reducing its absolute allocation.
\end{document}
'''
(M/'IUFEE_supplement.tex').write_text(s,encoding='utf-8')
print('Three-page supplement source and preserved technical record written.')
