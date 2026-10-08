# Representation diagnostics, 2026-10-07

All 91 cities and 1,259,886 positive GHSL-increment cells are included. All J/F/A and GLAD cell keys are unique and match exactly, as do g, integrated modelled depth h and cell centres. GLAD five-class partition maximum error is 4.47e-08; missing cells=0, minimum pair coverage=1.0. No new raw material was downloaded or read.

For the retained fine-grid map conventions, t=E[S(1-P)], so E[SP]=s-t and t-s(1-p)=-(E[SP]-sp)=-Cov(S,P). Covariance is reconstructed from stored t/s/p, so this identity check is algebraic rather than an independent native overlay validation. The independent native overlay audit remains the prior frozen input.

With f=s(1-p), A_J=sum(gt), E_J=sum(gth)/A_J and E_F=sum(gfh)/sum(gf), the exact centered decomposition is E_J-E_F=sum[g(t-f)(h-E_F)]/A_J. Each cell contributes c_i=g_i(t_i-f_i)(h_i-E_F)/A_J, in metres. City and pooled normalizers are kept separate. Maximum city identity residual=2.72e-16 m; pooled residual=4.37e-17 m.

The pooled J-F shift is -0.000591694 m, comprising positive contributions 0.010665820 m and negative contributions -0.011257513 m. Absolute-contribution mass is 0.021923333 m; cancellation fraction=0.973011. A small signed aggregate therefore need not mean small local representation differences.

Cell-budget queues use top 10 cells, top 1% cells (ceiling), and top 10% cells (ceiling), all drawn from g>0 cells including h=0. The representation queue sorts |c_i|; the standard queue sorts g_i*h_i. Ties are resolved by unit_key/grid_row/grid_column. Each queue reports the fraction of total |c| and total g*h it covers, plus queue overlap. These answer different deterministic auditing questions; the representation queue is not validated as a better hazard-monitoring queue. Pooled queues centre on pooled E_F; city queues centre on their city E_F.

Exposure is also decomposed into scale W=sum(w), model-nonzero-depth-supported allocation Wplus=sum(w*1[h>0]), depth numerator N=sum(wh), support share pplus=Wplus/W, conditional modelled depth muplus=N/Wplus, and E=N/W=pplus*muplus. Here w is g, gt, gf or g*a. h>0 denotes nonzero modelled integrated depth support, not actual inundation area or event risk. If Wplus=0, conditional depth is undefined; E is zero when W>0 and N=0. The symmetric J-F identity is deltaE=(pJ-pF)*(muJ+muF)/2+(muJ-muF)*(pJ+pF)/2, computed only where both conditional means exist. Undefined scopes=6; maximum identity residual=2.78e-16 m.

GLAD allocations multiply the same g/J/F/A weights by native-pair class fractions on precisely the same positive-cell support. They are product-consistency associations, not true-positive rates, roof-accuracy measures, construction-date validation or source independence. Both allocated-surface and depth-proxy class shares are reported; paired-coverage shares explicitly retain their denominator, and missing is shown as its own class.

Delhi, Guwahati and Sultanpur were selected before the preceding added analyses. The present five-city mechanism illustrations are diagnostic post hoc interpretations, with Srinagar and Nashik added because of observed differences. These are distinct selection timelines; the current diagnostic interpretation does not change the earlier selection record. Their full rows and all remaining cities are retained. Covariance/depth quadrant counts use covariance tolerance 1e-07; near-zero cases remain in exact contribution totals.

## Compact results

Across the pooled allocation, nonzero model-depth support shares are J=0.18330559, F=0.18324424, and conditional depths are J=1.07195892 m, F=1.07554678 m. The symmetric difference comprises a support-share term 0.000065872 m and a conditional-depth term -0.000657566 m. In the six cities without nonzero J/F model-depth support, both means E are zero and both conditional depths remain undefined; the symmetric conditional-mean decomposition is omitted.

The pooled top1% representation queue covers 56.2789% of absolute centered effects and 20.9984% of standard g*h mass. The same-budget standard queue covers 34.2558% of those effects and 61.9118% of g*h mass; queue overlap is 28.2483%. This follows from their different sorting objectives and is not evidence of a superior hazard queue.

Post hoc five-case centered differences and concentrations:

| eFUA_name | observed_EJ_minus_EF_m | positive_contributions_sum_m | negative_contributions_sum_m | absolute_contribution_concentration_top1pct_cells |
| --- | --- | --- | --- | --- |
| Srinagar | -0.213177 | 0.442294 | -0.655471 | 0.486712 |
| Delhi [New Delhi] | 0.00247855 | 0.0201238 | -0.0176452 | 0.336409 |
| Nashik | -0.00691074 | 0.00051537 | -0.00742611 | 0.950691 |
| Sultanpur | 0.00857873 | 0.0214754 | -0.0128967 | 0.384975 |
| Guwahati | 0.0519266 | 0.0956453 | -0.0437187 | 0.572248 |

Original three-case scale, support and depth components (Cplus is the model-nonzero support share; Dplus is the conditional modelled depth):

| eFUA_name | scheme | W_m2 | Wplus_m2 | Cplus | Dplus_m | E_m |
| --- | --- | --- | --- | --- | --- | --- |
| Delhi [New Delhi] | G | 5.14185e+07 | 1.6118e+07 | 0.313467 | 0.952666 | 0.29863 |
| Delhi [New Delhi] | J | 1.16464e+07 | 3.96155e+06 | 0.340151 | 0.900788 | 0.306404 |
| Delhi [New Delhi] | F | 1.23288e+07 | 4.14466e+06 | 0.336178 | 0.904062 | 0.303926 |
| Delhi [New Delhi] | A | 1.26547e+07 | 4.26708e+06 | 0.337192 | 0.905952 | 0.30548 |
| Guwahati | G | 788595 | 444198 | 0.563278 | 1.55062 | 0.873432 |
| Guwahati | J | 92813.9 | 70227 | 0.756643 | 1.53118 | 1.15856 |
| Guwahati | F | 101227 | 74372.9 | 0.734711 | 1.50621 | 1.10663 |
| Guwahati | A | 108364 | 79238.8 | 0.73123 | 1.50209 | 1.09837 |
| Sultanpur | G | 1.83258e+06 | 372673 | 0.20336 | 2.86255 | 0.582127 |
| Sultanpur | J | 387777 | 67615.2 | 0.174366 | 2.57478 | 0.448954 |
| Sultanpur | F | 406092 | 69250.9 | 0.17053 | 2.58239 | 0.440375 |
| Sultanpur | A | 413211 | 70228 | 0.169957 | 2.53314 | 0.430524 |

GLAD class absolute mass retained by J/F/A relative to the unscreened g-weighted mass in that same class:

| scheme | glad_pair_class | G_glad_class_mass_m2 | allocated_surface_times_glad_class_fraction_m2 | absolute_G_class_mass_retention_fraction |
| --- | --- | --- | --- | --- |
| J | new_built | 5.89593e+07 | 1.61743e+07 | 0.274329 |
| J | stable_built | 2.50781e+08 | 5.90941e+07 | 0.23564 |
| J | absent_both | 9.0788e+07 | 9.16433e+06 | 0.100942 |
| F | new_built | 5.89593e+07 | 1.64009e+07 | 0.278174 |
| F | stable_built | 2.50781e+08 | 6.20027e+07 | 0.247238 |
| F | absent_both | 9.0788e+07 | 9.55015e+06 | 0.105192 |
| A | new_built | 5.89593e+07 | 1.693e+07 | 0.287147 |
| A | stable_built | 2.50781e+08 | 6.38403e+07 | 0.254566 |
| A | absent_both | 9.0788e+07 | 9.47172e+06 | 0.104328 |

A larger GLAD-new composition share does not imply larger retained absolute class mass, and neither measure is mapping accuracy. Denominators and absolute masses are therefore reported together.

Outputs: diagnostics_city_decomposition.csv; diagnostics_queue_coverage.csv; diagnostics_top_effect_cells.csv; diagnostics_covariance_depth_quadrants.csv; diagnostics_exposure_components.csv; diagnostics_exposure_JF_symmetric_decomposition.csv; diagnostics_glad_class_allocation.csv; diagnostics_posthoc_five_cases.csv; diagnostics_cell_contributions.parquet; diagnostics_cell_alignment_checks.csv; diagnostics_summary.json; diagnostics_manifest.json.

Reproduce: `python -u "D:\MLWork\IUFEE_revision_20261005\scripts\representation_diagnostics_20261007.py"`. All computations and outputs are on D:. Source input SHA256 values are retained in the manifest.
