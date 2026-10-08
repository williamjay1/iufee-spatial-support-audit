"""Integrate the executed full-city joint baseline without inventing validation."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(r'D:\MLWork\IUFEE_revision_20261005')
MAN = ROOT / 'manuscript'
aggregate = json.loads((ROOT/'results/joint_overlay_aggregate_summary.json').read_text())
assert aggregate['completed_cities'] == aggregate['expected_cities'] == 91
assert aggregate['positive_cells'] == 1259886
verification = json.loads((ROOT/'results/joint_overlay_verification.json').read_text())
assert verification['all_passed'] is True and verification['completed_cities'] == 91
assert 'v3_fresh_identity' in verification['version']
assert len(verification['source_identity_stability_checks']) == 112
city = pd.read_csv(ROOT/'results/joint_overlay_city_summary.csv')
assert len(city) == 91
path = MAN/'IUFEE_redeveloped.tex'
text = path.read_text(encoding='utf-8')
# These names denote the archived factor product, not the new map-specific joint.
for old, new in [
    ('joint weights', 'product weights'),
    ('joint calculation', 'product calculation'),
    ('joint depth', 'product-weighted depth'),
    ('joint city depths', 'product-weighted city depths'),
    ('joint city depth', 'product-weighted city depth'),
    ('joint-depth interval', 'product-support depth interval'),
    ('joint-weighted', 'product-weighted'),
    ('joint-weight', 'product-weight'),
    ('continuous joint', 'continuous product'),
    ('joint weight', 'product weight'),
]:
    text = text.replace(old,new)
text = text.replace("median depth is", "median depth is")
text = text.replace("Guwahati's joint depth", "Guwahati's product-weighted depth")
text = text.replace('marginal-compatible product-support depth interval', 'marginal-compatible depth interval')
text = text.replace('We compare these fractions under GHSL and product weights', 'We compare these fractions under GHSL and archived product weights')
text = text.replace('All cities have positive lower mass, but none has fully identified intersection weights.', 'From the archived marginals, all cities have positive lower mass, but none has fully identified intersection weights.')
text = text.replace('Under product weights the new-built fraction', 'Under archived product weights the new-built fraction')
text = text.replace('GHSL and continuous product-weighted depth summaries, with the marginal-compatible depth interval.', 'GHSL, archived product and joint-preserving overlay depth summaries, with the marginal-compatible interval derived from archived fractions.')
text = text.replace('Intervals condition on the stored source fractions and static GloFAS depths;', 'Intervals condition on the archived source fractions and static GloFAS depths;')
text = text.replace('and by the continuous product weight.', 'and by the archived product weight.')
old = 'The compatible depth interval has median width 0.048 m and maximum width 1.980 m.'
new = old + ' A joint-preserving overlay allocates 4.00\\% less support than the same-grid marginal product, with a maximum city-depth difference of 0.213 m.'
if new not in text:
    assert old in text
    text = text.replace(old,new)
old = 'A zero WSF Evolution response is the complement of positive detection, not proof of nonsettlement.'
new = 'Two repeat native-block checks reproduced the old counts and file identities, including valid masks at code-1 pixels; their generation mechanism remains unknown. '+old
if new not in text:
    assert old in text
    text = text.replace(old,new)
anchor = '\\subsection{Hazard summary and experiment design}'
joint_method = r'''To test a correctly implemented overlay, we nearest-register both categorical parent maps to a common 10 m Mollweide grid nested within the GHSL cells. We form $S(1-P)$ before averaging its 100 subcells to $t_i$, then compare $gt$ with $gs(1-p)$ using marginals from that same fine grid. A separate comparison with the archived product diagnoses registration differences. Tiles use lexicographic first-valid merging; coverage and binary-class overlap conflicts are audited. Revised derivatives retain $t$, $s$, $p$, undocumented fraction and coverage. Supplementary Section S11 supplies the full-city baseline and source-identity checks.

'''
if joint_method not in text:
    assert anchor in text
    text = text.replace(anchor,joint_method+anchor)
anchor = '\\subsection{Alternative overlays and hazard choices}'
joint_result = r'''The joint-preserving overlay allocates 84.434 km$^2$, versus 87.956 km$^2$ for the same-grid marginal product: a 4.00\% decrease. Their city-depth correlation is 0.997722, but the median absolute difference is 0.002265 m and the maximum is 0.213177 m in Srinagar. Forty-two city ranks change, by up to 13 positions, with nine of the ten highest cities retained. The same-grid product versus the archived product changes pooled support by 2.54\%; this second contrast includes registration differences and cannot be attributed solely to joint-location loss. All 91 FUAs have complete source coverage. These results quantify a representation effect, not an accuracy gain.

'''
if joint_result not in text:
    assert anchor in text
    text = text.replace(anchor,joint_result+anchor)
text = text.replace('The revised schema should retain joint support when parent maps are available.',
                    'The executed joint-preserving baseline restores map-specific support and the revised derivatives retain it.')
path.write_text(text,encoding='utf-8')

plot = ROOT/'scripts/plot_revision.py'
p = plot.read_text(encoding='utf-8').replace("label='Joint product weight'", "label='Product weight'")
p = p.replace("['GHSL','joint']", "['GHSL','product']")
plot.write_text(p,encoding='utf-8')

def fmt(x,n=6): return f'{float(x):.{n}f}'
rows=[]
for key in ['IND_FUA_07466','IND_FUA_10496','IND_FUA_09258','IND_FUA_02091']:
    r=city.set_index('unit_key').loc[key]
    rows.append(f"{r.eFUA_name} & {fmt(r.joint_overlay_normalized_city_depth_m)} & {fmt(r.fine_product_normalized_city_depth_m)} & {fmt(r.archived_product_normalized_city_depth_m)} \\\\")
section = r'''
\section*{S11. Executed joint-preserving overlay and source recovery}
\subsection*{S11.1 Common-grid comparison}
This experiment completed all 91 FUAs and all 1,259,886 positive GHSL records. It is distinct from the archived four-weight design: its map-specific intersection is $t=\operatorname{mean}_{100}(S(1-P))$ after nearest registration to a 10 m World Mollweide grid exactly nested inside each 100 m GHSL cell. $S$ denotes documented WSF2019 settlement (255); $P$ denotes a positive WSF Evolution detection (1985--2015). WSF2019 value 1 remains undocumented. Source-outside coverage uses a distinct sentinel and is never merged with valid zero. Tiles are ordered lexicographically and the first valid value is retained. Processing uses blocks of 32 GHSL rows, avoiding a persistent whole-city 10 m raster.

Three representations retain the same $g$ and nearest-registered $h$: (J) $g t$, the joint-preserving overlay; (F) $g s(1-p)$, using marginals from that same fine grid and merge convention; (A) the archived product using the original average-registered marginals. Their weight masses are $W=\sum w$ and unnormalised depth numerators are $N=\sum wh$; city mean depth is $N/W$. J versus F isolates joint-location loss under the declared common grid. F versus A additionally contains registration and merge-convention effects. All are proportional allocations of a cell's modelled GHSL surface difference, without identification of its subcell roof geometry or construction date.

\begin{center}\begin{tabular}{lrrr}\toprule
Representation & Mass (km$^2$) & $N$ (m$^3$ proxy) & Pooled $N/W$ (m)\\\midrule
Joint-preserving J & 84.434392 & 16,591,025.173 & 0.196496\\
Fine marginal product F & 87.955644 & 17,334,980.093 & 0.197088\\
Archived product A & 90.243923 & 17,796,747.388 & 0.197207\\\bottomrule
\end{tabular}\end{center}

The J--F signed mass difference is $-3.521252$ km$^2$ ($-4.003441\%$ of F), whereas the sum of cellwise absolute mass differences is 5.274053 km$^2$; aggregation therefore contains cancellation. Their signed depth-numerator difference is $-743,954.920$ m$^3$ proxy ($-4.291640\%$). The F--A mass difference is $-2.288279$ km$^2$ ($-2.535660\%$), with 12.973530 km$^2$ cellwise absolute difference. These masses and numerators are not confirmed construction area or physical flood volume.

For city means, J--F Spearman correlation is 0.997722, median absolute difference 0.002265 m, and maximum absolute difference 0.213177 m (Srinagar). Forty-two ranks differ, with maximum change 13 positions (Nashik), and top-ten overlap is nine. J--A correlation is 0.997961, median absolute difference 0.002481 m, maximum difference 0.207928 m (Srinagar), 41 changed ranks, maximum change 12, and top-ten overlap nine. Pooled means above are ratios of pooled masses and numerators, not medians of the 91 city means.

\begin{center}\begin{tabular}{lrrr}\toprule
City & J mean (m) & F mean (m) & A mean (m)\\\midrule
''' + '\n'.join(rows) + r'''
\bottomrule\end{tabular}\end{center}

\subsection*{S11.2 Geometry, class and source identity checks}
All 91 FUA masks have complete paired source coverage; the missing-source cell count is zero. Output geometry matches each GHSL raster. The maximum numerical violation of the fine-marginal compatibility bounds and the independently computed class-partition error are both $5.96\times10^{-8}$. All positive-cell $g$ values match their GHSL parent bands. Direct recomputation from the retained cell tables checks masses, numerators and normalised means. These are geometry, arithmetic and file-identity checks, not independent map accuracy.

WSF2019 tile overlaps contain no value or class conflicts. Evolution overlaps contain 2,916 FUA fine-pixel year-value conflicts, but no positive-detection binary-class conflicts; these year differences do not alter the $P$ classification used here. This finding is specific to the present binary diagnostic and does not justify ignoring year conflicts in a construction-dating analysis.

The source-integrity checks encountered nine existing local files whose identities differed from the historical source audit, including a WSF2019 file with a short LZW decode error. Repeat reads of the first six original files later matched the historical hashes, and a repeated read of the previously failing block decoded successfully. The observed failures are therefore not evidence of persistent physical damage, its cause or timing. Original files were preserved without writes. Nine official replacements were downloaded under new raw filenames and made read-only. Every recovered file exactly matches its historical SHA256, and all 112 source files actually used in the final forced recomputation match that audit. Initial and final file statistics and hashes agree in the frozen run. Recovered WSF2019 identifiers are 76\_10, 78\_28, 84\_26, 78\_22 and 80\_24; recovered Evolution identifiers are 74\_30, 84\_22, 74\_26 and 82\_24. The recovery record preserves observed original identity, replacement identity, provenance and overrides. Recovery secures source identity for this run; it does not resolve undocumented code 1 or provide accuracy validation.

\subsection*{S11.3 Reproducible outputs}
\path{joint_overlay_city_summary.csv} contains all 91 city masses, numerators, means and ranks; \path{joint_overlay_aggregate_summary.json} contains pooled and paired comparisons. \path{joint_overlay_verification.json} records every city and used-source check. \path{joint_overlay_source_recovery_audit.json} and \path{joint_overlay_source_overrides.json} document the nine replacements. Per-city retained fraction rasters contain $t,s,p,u,$ and coverage, and positive-cell tables retain the baseline and original fractions. The script and run log state the executed scope and merge rule. Internal checks and recovered bitwise identities must not be reported as independently verified construction or hydraulic accuracy.
'''
supp=MAN/'IUFEE_supplement.tex'
s=supp.read_text(encoding='utf-8')
begin='% BEGIN ROOT-OWNED SUPPLEMENT SECTIONS'
end='% END ROOT-OWNED SUPPLEMENT SECTIONS'
assert s.count(begin)==s.count(end)==1
s=s.split(begin)[0]+begin+'\n'+section+'\n'+end+s.split(end)[1]
supp.write_text(s,encoding='utf-8')
print('Integrated complete 91-city joint experiment and protected S11.')
