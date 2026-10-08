# Deterministic sensitivity analysis for the IUFEE revision

Executed 2026-10-05T00:41:44+08:00 in 3.412 s. Inputs were read only; output is on D:. No downloads or large-scale training were performed.

## Scope and reconstruction

Reconstructed 1,259,886 positive-change records in 91 FUAs, totaling 400.535818 km² of positive GHSL product difference. All seven return-period values were finite. Largest reconstructed versus published city depth difference: 3.84e-09 m; largest denominator difference: 0.00434 m² (float32 storage/arithmetic).
The four original scenario medians reproduce to six decimals: endpoint_supported: 0.115871 m; ghsl_only: 0.119330 m; joint_supported_screened: 0.117315 m; preexisting_detected_screened: 0.120465 m.

## Weighting conventions and binary endpoint decisions

Generalized weights are g·s^α·(1−p)^β for α,β∈{0,0.5,1,2}. Exponent zero means the corresponding evidence factor is omitted, including at a zero source fraction; (0,0), (1,0), (0,1), and (1,1) recover the four stated scenarios. Every denominator is reported as an arithmetic weight mass, not physically observed construction area. Binary alternatives are g·I(s≥τ)·(1−p), τ∈{0.25,0.50,0.75}; only endpoint support is thresholded.
Across the 15 nonbaseline exponent settings, Spearman correlations with joint weights range 0.986632–0.998980; median absolute city-depth changes range 0.001973–0.018919 m; top-ten overlaps range 8–9/10.

| setting | total_denominator_km2 | median_depth_m | spearman_vs_baseline | median_absolute_delta_m | max_absolute_delta_m | top10_overlap_count |
| --- | --- | --- | --- | --- | --- | --- |
| endpoint_threshold_0.25 | 147.354407 | 0.120904 | 0.991894 | 0.005806 | 0.226719 | 8 |
| endpoint_threshold_0.5 | 66.779354 | 0.071420 | 0.913297 | 0.015426 | 0.573101 | 8 |
| endpoint_threshold_0.75 | 17.342441 | 0.005872 | 0.794784 | 0.035029 | 1.124503 | 6 |

## Undocumented WSF2019 code

The positive-GHSL weighted undocumented fraction is 0.000331427555361, equivalent to 132748.606994 m² of arithmetic GHSL weight. The largest city fraction is 0.00343285148551 in Mangaluru.
Changing s to s+u is an extreme coding scenario in which all undocumented portions supply endpoint support. Treating those portions as nonsettlement or retaining them as unassigned supplies no positive support and gives the same s, without making the same semantic claim. Exact ratio bounds allow any additional cell support between 0 and u; these are conditional assignment bounds, not settlement accuracy bounds.
The maximum city joint-depth assignment width is 0.038271748843 m in Mangaluru; the maximum absolute all-supported versus unassigned change is 0.0286255580838 m.

## WSF Evolution zero semantics

Renaming the unresolved complement as nonsettlement while retaining the same numeric weights produces exactly zero numeric change; it would add an unsupported semantic assertion. Excluding unresolved source portions leaves only positive historic detections, which the preperiod screen then removes. That interpretation has zero retained weight and no defined screened depth in all 91 FUAs. Multiplying aggregated mutually exclusive fractions to manufacture retained overlap would be invalid.
For the meaningful no-screen versus screen calculation, the median signed change is 0.000612 m with GHSL weights and 0.000113 m with endpoint weights. The maximum absolute changes are 0.088241 and 0.207904 m, respectively. These compare arithmetic evidence choices; they do not establish the history of retained cells.

## Hazard summary choices

The published normalized trapezoid integrates over annual exceedance probability 0.002–0.1 and divides by that interval width. It omits the tail beyond RP500 and the range below RP10, and is not an annual expected depth. The uniform mean gives seven return-period layers equal weight, while RP100 and RP500 are single-layer stress cases; they answer different hazard-summary questions.

| hazard_metric | median_depth_m | spearman_vs_baseline | median_absolute_delta_m | max_absolute_delta_m | top10_overlap_count | max_delta_city |
| --- | --- | --- | --- | --- | --- | --- |
| RP100 | 0.165809 | 0.995747 | 0.040466 | 1.012067 | 9 | Guwahati |
| RP500 | 0.224551 | 0.988052 | 0.085783 | 1.622536 | 9 | Guwahati |
| normalized_exceedance_trapezoid | 0.117315 | 1.000000 | 0.000000 | 0.000000 | 10 | Srinagar |
| uniform_seven_RP_mean | 0.158271 | 0.996925 | 0.029255 | 0.643423 | 9 | Guwahati |

## Marginal support and Fréchet compatibility

The retained cell fractions s and p are marginal endpoint and historic support. Their product s(1−p) is a declared weighting convention. It does not identify the subcell intersection of endpoint support and absence of positive historic detection. Without a joint footprint, its feasible intersection fraction t lies in [max(0,s−p), min(s,1−p)]. The product lies inside this interval for every cell within 1e−7 storage tolerance.
Total arithmetic denominators under the lower endpoint, product, and upper endpoint weights are 79.852620, 90.243923, and 99.604911 km². The true fractional-ratio compatibility widths have median 0.048216 m, IQR 0.003466–0.118425 m, and maximum 1.980212 m in Srinagar. 0 cities admit a zero denominator; 0 cities admit no positive denominator. 0 cities have fully identified intersection weights from the stored marginals.
The gL and gU depth estimates are two endpoint scenarios. They are not generally the minimum and maximum weighted depths. Exact city-depth extrema were calculated separately by solving the box-constrained linear-fractional problem with Dinkelbach residual bisection. These are conditional compatibility bounds, not error-adjusted estimates or confidence intervals.

The depth interval collapses within 1e−10 m in 6 cities even though their intersection weights remain unidentified. It is at least 0.05 m wide in 44 cities. The lower and upper endpoint scenarios have rank correlations 0.994361 and 0.998455 with the product; those rank correlations do not contract the full compatibility interval.

## Alignment and fixed application examples

Published average versus nearest city-summary Spearman correlations range 0.997878–0.999327. Alternate weights cannot be recomputed with average alignment because the released cell tables contain nearest depths only.
Guwahati and Sultanpur were retained to interpret previously reported opposite extremes; the third example is Delhi [New Delhi], selected before depth computation as the largest-population roster unit. The application table reports all seven RP layers, the uniform mean, the normalized trapezoid, and all four scenarios for each city. The examples are not an external or representative validation sample.

## Positive-change cutoffs and GloFAS QA flags

Product-difference cutoffs retain only cells with g strictly greater than 0, 10, 50, 100, or 500 m². QA exclusions discard an entire 100 m cell when any registered source support is flagged as permanent water, spurious depth, or either; all QA fields are finite in the release. These conservative whole-cell exclusions are declared stress scenarios, not assertions that flagged fractions or excluded GHSL differences are erroneous.

| setting | retained_positive_GHSL_fraction | total_denominator_km2 | median_depth_m | spearman_vs_baseline | median_absolute_delta_m | max_absolute_delta_m | top10_overlap_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GHSL_g_gt_0_m2 | 1.000000 | 90.243923 | 0.117315 | 1.000000 | 0.000000 | 0.000000 | 10 |
| GHSL_g_gt_100_m2 | 0.959557 | 89.596252 | 0.117387 | 0.999841 | 0.000203 | 0.025796 | 9 |
| GHSL_g_gt_10_m2 | 0.995996 | 90.218259 | 0.117312 | 0.999968 | 0.000011 | 0.004722 | 10 |
| GHSL_g_gt_500_m2 | 0.781070 | 85.937236 | 0.104894 | 0.999347 | 0.001336 | 0.073378 | 9 |
| GHSL_g_gt_50_m2 | 0.979466 | 89.980127 | 0.117344 | 0.999968 | 0.000109 | 0.018355 | 10 |
| exclude_any_permanent_water_QA | 0.993736 | 90.048543 | 0.106672 | 0.993492 | 0.002152 | 0.306322 | 9 |
| exclude_any_spurious_depth_QA | 0.994028 | 89.796950 | 0.100675 | 0.988578 | 0.000000 | 0.401309 | 10 |
| exclude_either_QA | 0.987881 | 89.606284 | 0.098056 | 0.983767 | 0.002152 | 0.403928 | 9 |

## Return-period depth decreases and labelled monotonicization

There are 2,437 cells (0.193430%) with at least one adjacent return-period depth decrease exceeding 1e−6 m; their GHSL weight is 0.089864% of total positive change. Maximum adjacent depth decrease is 14.183000 m.

Among affected GHSL weights, 72.738436% intersect a positive permanent-water or spurious-depth QA flag. The largest drop occurs in Dhanbad from RP200 to RP500; its spurious-depth QA fraction is 1. The diagnostic record and all its supplied RP depths are retained in revision_monotonicity_summary.json.

| lower_RP | higher_RP | decreasing_record_count | decreasing_GHSL_change_m2 | max_drop_m | mean_drop_among_decreasing_records_m |
| --- | --- | --- | --- | --- | --- |
| 10 | 20 | 442 | 58077.000000 | 0.900000 | 0.586957 |
| 20 | 50 | 423 | 47116.000000 | 0.900000 | 0.570728 |
| 50 | 75 | 704 | 140006.000000 | 0.958000 | 0.526004 |
| 75 | 100 | 144 | 15957.000000 | 0.900000 | 0.701528 |
| 100 | 200 | 273 | 41653.000000 | 0.900000 | 0.596414 |
| 200 | 500 | 454 | 57146.000000 | 14.183000 | 2.072489 |

The supplied seven-layer representation is therefore not everywhere a monotone depth quantile sequence. The primary calculation preserves supplied values. A separately labelled upward cumulative maximum over return periods measures numeric sensitivity; it does not establish that this is a scientifically correct repair.
endpoint_supported: median shift 4.72392404e-09 m, maximum 0.00162551833 m (Tamluk); ghsl_only: median shift 2.48468009e-06 m, maximum 0.00152748224 m (Kolkata); joint_supported_screened: median shift 5.27357138e-09 m, maximum 0.00173534565 m (Srinagar); preexisting_detected_screened: median shift 2.78336564e-06 m, maximum 0.001712408 m (Kolkata).

## Algorithm verification with explicitly synthetic cases

The ratio-bound routine was compared against exhaustive enumeration of all positive-denominator box vertices in 96 synthetic cases (one to six cells; 2016 vertices; random seed 20261005). Maximum absolute difference in extrema is 1.78e-15. Three additional analytical corner cases passed. These synthetic values verify only the numerical optimizer and provide no empirical evidence about settlement or flood accuracy.

## Manuscript-ready evidence boundary

The added analyses assess how deterministic arithmetic weights, source-state coding choices, hazard-summary definitions, and marginal overlap assumptions affect linked city measures. They neither validate the settlement products independently nor estimate the accuracy of GloFAS depths. Numerical reproduction and stability under selected alternatives support auditability within the stated data representation. A valid spatial intersection requires a joint footprint; a physically verified change label and flood accuracy claim require independent references that are absent from this analysis.

See revision_run_log.json for the actual run and prespecified case-selection record; revision_validation.json for reconstruction checks; the revision_*.csv tables retain all city denominators, depth values, and ranking diagnostics.
