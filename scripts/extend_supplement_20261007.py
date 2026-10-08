"""Add the frozen representation diagnostics and six computed cell dossiers."""
from pathlib import Path
import pandas as pd,re
R=Path(r'D:\MLWork\IUFEE_revision_20261005')
p=R/'manuscript/IUFEE_supplement.tex';s=p.read_text(encoding='utf-8')
s=s.replace('Source Evidence Bounds for Urban Change and Fluvial Exposure in 91 Indian Cities','Spatial Support Assumptions in Urban Change Exposure: An Audit of 91 Indian Cities')
note=r'''\noindent\textbf{Notation across representations.} Unadorned $s,p,u$ in Sections S1--S10 refer to the archived marginals $s^A,p^A,u^A$ in the main article. Their compatibility bounds condition on representing recorded values under a common normalized support measure; they do not establish an exact intersection under a shared native-area measure. Sections S11--S12 distinguish the explicit common-grid marginals $s^F,p^F$ and joint fraction $t^F$. The fine-grid measure is uniform over the 100 nested subcells. Archived compatibility intervals need not contain a result using different registration. Nearest registration does not increase the native spatial information of Evolution.

'''
if note not in s:s=s.replace(r'\section{Source states, target grid and four arithmetic weights}',note+r'\section{Source states, target grid and four arithmetic weights}')
section=r'''
% BEGIN DIAGNOSTICS 20261007
\clearpage
\section*{S12. Spatial representation diagnostics and executed cell dossiers}
\subsection*{S12.1 Exact identities and support interpretation}
All 91 cities and 1,259,886 positive-$g$ cells enter the diagnostic join. Cell keys are unique and identical between the joint-overlay and GLAD tables, as are $g$, integrated depth and centers. The largest paired GLAD class-partition residual is $4.47\times10^{-8}$; missing-pair count is zero. Let $f_i=s_i^F(1-p_i^F)$. From the retained joint fractions,
\[
t_i^F-f_i=-\operatorname{Cov}_{\mu_i^F}(S,P),\qquad
E_J-E_F=\sum_i\frac{g_i(t_i^F-f_i)(h_i-E_F)}{W_J}.
\]
The covariance reconstructed from $s,p,t$ is an algebraic explanation, not an independent rerun of the native-map intersection. The largest city centered-identity residual is $2.72\times10^{-16}$ m. The original native overlay verification is retained separately in S11.

For $W^+=\sum_i w_i\mathbf{1}(h_i>0)$, the diagnostic retains $C=W^+/W$ and $D^+=N/W^+$, so $E=CD^+$. Modelled nonzero-depth support is not actual flooded area. Six cities have no such support under J/F; their $D^+$ and symmetric decomposition are undefined. The largest symmetric-identity residual is $2.78\times10^{-16}$ m. All undefined fields remain explicit in the tables.

The pooled shift $-0.000591694$ m comprises positive centered contributions $0.010665820$ m and negative contributions $-0.011257513$ m. The absolute total is $0.021923333$ m and the cancellation fraction is $0.973011$. Pooled and city calculations use distinct centers and denominators. A pooled contribution is not a city's contribution to the unweighted average of city means.

\subsection*{S12.2 Queue definitions and concrete cells}
Original queues sort descending $g_i h_i$. Representation queues sort descending absolute centered contribution, using the appropriate city or pooled center. Top 1\% and 10\% budgets are rounded upward; ties use unit, row and column keys. Positive-$g$ cells with zero depth remain eligible. Coverage is calculated separately against the absolute representation effect and the unscreened depth numerator; different objectives can yield different cells. At the pooled 1\% budget (12,599 cells), the representation queue covers 56.2789\% of absolute effect and 20.9984\% of the standard depth numerator, whereas the standard queue covers 34.2558\% and 61.9118\%, respectively. Queue overlap is 28.2483\%. Exact values are retained in the machine-readable output.

The original three application cities were selected before the added joint and diagnostic analyses. The five-city mechanism comparison additionally selects Srinagar and Nashik post hoc to explain the largest depth and rank changes. Selection of the six dossiers below is explicit: Delhi and Sultanpur original orders 1--2, and the two QA-positive Guwahati cells, original orders 9--10. No independent image interpretation was performed for these dossiers.
\input{case_dossiers_table.tex}

At Guwahati order 10, the common-grid marginals $s^F=0.13$ and $p^F=0.41$ give $f^F=0.0767$ while the actual joint fraction is zero. The permanent-water QA value is one, and RP50--RP75 depths decrease from 9.552 to 9.424 m. The dossier therefore identifies both a representation effect and a hazard-profile issue for reference review. Delhi's first two cells have GLAD stable-built fraction one; this constrains a new-settlement interpretation while leaving infill and product-definition differences unresolved. Full CSV dossiers preserve all seven RP values, both QA fractions and separate archived/fine marginals.

\subsection*{S12.3 All-city depth decomposition}
Table S\ref{tab:diagnostics-all} reports J/F differences and the J factors. ``--'' means undefined because nonzero-depth support is empty. The effect-concentration column reports the share of $\sum|c_i|$ in the city's top 1\% of cells, rounded upward. It does not measure mapping accuracy or practical review efficiency.
\begingroup\small\setlength{\tabcolsep}{4pt}
\begin{longtable}{lrrrrrr}
\caption{All-city joint-support depth diagnostics.}\label{tab:diagnostics-all}\\
\toprule
FUA & $E_J$ & $E_F$ & $J-F$ & $C_J$ & $D_J^+$ & Top 1\%\\
 & (m)&(m)&(m)&(\%)&(m)& effect (\%)\\\midrule\endfirsthead
\multicolumn{7}{l}{\tablename\ \thetable\ (continued)}\\\toprule
FUA & $E_J$ & $E_F$ & $J-F$ & $C_J$ & $D_J^+$ & Top 1\%\\
 & (m)&(m)&(m)&(\%)&(m)& effect (\%)\\\midrule\endhead
\midrule\multicolumn{7}{r}{Continued on next page}\\\endfoot
\bottomrule\endlastfoot
'''
d=pd.read_csv(R/'results/revision_20261007/diagnostics_city_decomposition.csv')
e=pd.read_csv(R/'results/revision_20261007/diagnostics_exposure_components.csv');e=e[e.scheme=='J'].set_index('unit_key')
for _,row in d[d.unit_key!='ALL91_POOLED'].iterrows():
    ex=e.loc[row.unit_key]
    nm=row.eFUA_name.replace('&',r'\&').replace('_',r'\_')
    if (d.eFUA_name==row.eFUA_name).sum()>1: nm+=' ('+row.unit_key.split('_')[-1]+')'
    cv=lambda v:f'{v:.5f}' if pd.notna(v) else '--'
    vals=[cv(row.E_J_m),cv(row.E_F_m),cv(row.observed_EJ_minus_EF_m),f'{100*ex.model_nonzero_depth_support_share:.2f}',cv(ex.conditional_model_nonzero_mean_depth_m),f'{100*row.absolute_contribution_concentration_top1pct_cells:.2f}' if pd.notna(row.absolute_contribution_concentration_top1pct_cells) else '--']
    section+=nm+' & '+' & '.join(vals)+r' \\'+'\n'
section+=r'''\end{longtable}\endgroup
\subsection*{S12.4 Class composition and retention}
Paired GLAD fractions share exactly the same cells as J/F/A. Screening changes both total allocation and class composition. Pooled J retains 27.4329\% of G allocation associated with GLAD new-built class, 23.5640\% of stable-built and 10.0942\% of absent-both. Corresponding F values are 27.8174\%, 24.7238\% and 10.5192\%; A values are 28.7147\%, 25.4566\% and 10.4328\%. New-class composition is higher for J than F, but its absolute allocation is lower (16.1743 versus 16.4009 km$^2$). These quantities describe source allocation, not true-positive rates.

The diagnostic outputs retain cell contributions, all-city signed/absolute totals, support/depth factors, symmetric terms, queue coverage and overlap, five GLAD class allocations, selected-cell dossiers and join checks. The run manifest records input identities and the execution version. The analysis adds no new raw imagery and does not relabel any existing source product.
% END DIAGNOSTICS 20261007
'''
start='% BEGIN DIAGNOSTICS 20261007';end='% END DIAGNOSTICS 20261007'
if start in s:s=s[:s.index(start)]+s[s.index(end)+len(end):]
s=s.replace(r'\end{document}',section+'\n'+r'\end{document}')
s=s.replace(r'Table S\ref{tab:diagnostics-all}',r'Table~\ref{tab:diagnostics-all}')
p.write_text(s,encoding='utf-8')
print('Supplement S12 and A/F notation updated.')
