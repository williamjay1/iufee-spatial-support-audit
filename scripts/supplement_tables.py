"""Build a standalone supplement from the executed revision CSV/JSON files.

Owns only manuscript/IUFEE_supplement.tex. All empirical numbers are read from
the already completed deterministic analyses; running GLAD outputs are not read.
"""
from pathlib import Path
import json
import math
import re
import pandas as pd

ROOT = Path(r"D:\MLWork\IUFEE_revision_20261005")
RESULTS = ROOT / "results"
OUTPUT = ROOT / "manuscript" / "IUFEE_supplement.tex"
SOURCE = Path(r"D:\codex\sci\remote_sensing_sci_novelty_audit\guangzhou_india_flood_exposure_study\grsl_submission_2026\zenodo_release\IUFEE_v1_2\data\database_v1_2")

def read_csv(name):
    return pd.read_csv(RESULTS / name)

def read_json(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))

def escape(value):
    text = str(value)
    for old, new in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")):
        text = text.replace(old, new)
    return text

def f(value, digits=6):
    if pd.isna(value):
        return "---"
    return f"{float(value):.{digits}f}"

def sci(value, digits=3):
    if float(value) == 0:
        return "0"
    mantissa, exponent = f"{float(value):.{digits - 1}e}".split("e")
    return rf"${mantissa}\times10^{{{int(exponent)}}}$"

SCENARIO_NAMES = {
    "ghsl_only": "GHSL only",
    "endpoint_supported": "Endpoint support",
    "preexisting_detected_screened": "Preperiod screen",
    "joint_supported_screened": "Product",
}
SCENARIOS = list(SCENARIO_NAMES)
METRIC_NAMES = {"normalized_exceedance_trapezoid": "Finite probability-coordinate integral", "uniform_seven_RP_mean": "Uniform seven-RP mean"}
METRIC_ORDER = ["RP10", "RP20", "RP50", "RP75", "RP100", "RP200", "RP500", "uniform_seven_RP_mean", "normalized_exceedance_trapezoid"]

def table(caption, headers, rows, spec=None, label=None, size="small", note=None):
    spec = spec or ("l" + "r" * (len(headers) - 1))
    output = [r"\begin{table}[htbp]", r"\centering", rf"\caption{{{caption}}}"]
    if label:
        output.append(rf"\label{{{label}}}")
    output += [rf"\{size}", r"\setlength{\tabcolsep}{4pt}", rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    output += [" & ".join(str(x) for x in row) + r" \\" for row in rows]
    output += [r"\bottomrule", r"\end{tabular}"]
    if note:
        output.append(r"\par\smallskip\begin{minipage}{0.97\linewidth}\footnotesize " + note + r"\end{minipage}")
    output += [r"\end{table}", ""]
    return "\n".join(output)

def longtable(caption, headers, rows, spec, label):
    head = " & ".join(headers) + r" \\"
    return "\n".join([
        r"\begingroup\small\setlength{\tabcolsep}{4pt}",
        rf"\begin{{longtable}}{{{spec}}}", rf"\caption{{{caption}}}\label{{{label}}}\\",
        r"\toprule", head, r"\midrule\endfirsthead", r"\multicolumn{" + str(len(headers)) + r"}{l}{\tablename\ \thetable\ (continued)}\\",
        r"\toprule", head, r"\midrule\endhead", r"\midrule\multicolumn{" + str(len(headers)) + r"}{r}{Continued on next page}\\\endfoot",
        r"\bottomrule\endlastfoot", *[" & ".join(str(x) for x in row) + r" \\" for row in rows], r"\end{longtable}\endgroup", ""
    ])

def preserve_external_sections():
    """Retain root-owned S11+ material if the generated source is rebuilt."""
    if not OUTPUT.exists():
        return ""
    existing = OUTPUT.read_text(encoding="utf-8")
    start_marker = "% BEGIN ROOT-OWNED SUPPLEMENT SECTIONS"
    end_marker = "% END ROOT-OWNED SUPPLEMENT SECTIONS"
    if start_marker in existing and end_marker in existing:
        saved = existing.split(start_marker, 1)[1].split(end_marker, 1)[0].strip()
        if saved:
            return saved
    sections = list(re.finditer(r"(?m)^\\section\{", existing))
    if len(sections) > 10:
        return existing[sections[10].start():].split(r"\end{document}", 1)[0].strip()
    return ""


def main():
    v = read_json("revision_validation.json")
    fr = read_json("revision_frechet_summary.json")
    mono = read_json("revision_monotonicity_summary.json")
    run = read_json("revision_run_log.json")
    weights = read_csv("revision_weight_summary.csv")
    weight_city = read_csv("revision_weight_city.csv")
    original = read_csv("revision_original_city.csv")
    frechet = read_csv("revision_frechet_city.csv")
    coding = read_csv("revision_coding_bounds_city.csv")
    history = read_csv("revision_history_city.csv")
    hazard = read_csv("revision_hazard_summary.csv")
    alignment = read_csv("revision_alignment_summary.csv")
    qa = read_csv("revision_qa_threshold_summary.csv")
    cases = read_csv("revision_application_cities.csv")
    roster = pd.read_csv(SOURCE / "city_evidence_summary.csv")
    queue = read_csv("revision_case_review_queue.csv")
    if len(queue) != 30 or set(queue.city) != {"Delhi", "Guwahati", "Sultanpur"}:
        raise ValueError("Expected the completed 30-cell, three-city review queue")
    queue["any_positive_QA"] = (queue.glofas_permanent_water_qa > 0) | (queue.glofas_spurious_depth_qa > 0)
    for city, frame in queue.groupby("city"):
        ordered = frame.sort_values("review_order")
        if list(ordered.review_order) != list(range(1, 11)) or not ordered.review_score_m3.is_monotonic_decreasing:
            raise ValueError(f"Review queue ordering does not match the declared selection for {city}")
    queue_summary = queue.groupby("city").agg(
        selected_cells=("review_order", "count"), median_GLAD_new_fraction=("glad_new_built_fraction", "median"),
        any_QA_count=("any_positive_QA", "sum"), min_score_m3=("review_score_m3", "min"), max_score_m3=("review_score_m3", "max"))
    external_sections = preserve_external_sections()
    assert run["all_outputs_created"] and v["reconstruction_passed"]
    assert len(frechet) == 91 and len(original) == 364 and len(cases) == 108
    assert set(cases.unit_key) == set(run["application_selection_before_depth_computation"]["unit_keys"])
    assert int(weights.loc[weights.setting.eq("endpoint_threshold_0.75"), "paired_city_count"].iloc[0]) == 89
    undocumented_total = coding.undocumented_GHSL_weighted_m2.sum()
    undocumented_fraction = undocumented_total / v["total_positive_GHSL_change_m2"]
    max_coding = coding.loc[coding.joint_possible_assignment_width_m.idxmax()]
    max_u = coding.loc[coding.undocumented_GHSL_weighted_fraction.idxmax()]
    vertex = run["ratio_vertex_enumeration_verification"]

    text = [r"""\documentclass[10pt,a4paper]{article}
\usepackage[margin=20mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,amssymb,booktabs,longtable,array,graphicx,placeins}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\theequation}{S\arabic{equation}}
\setlength{\parindent}{1em}
\setlength{\parskip}{3pt}
\setlength{\emergencystretch}{2em}
\graphicspath{{figures/}}
\title{Supplementary Material\\[3pt]\large Source Evidence Bounds for Urban Change and Fluvial Exposure in 91 Indian Cities}
\author{Junjie Zhang, Yushi Tian, and Zhuo Zeng}
\date{}
\begin{document}
\maketitle
\noindent This supplement gives reproducible definitions, numerical checks and conditional sensitivity calculations accompanying the main article. The main article retains the research question, core evidence bounds, cross-product findings and interpretation. Here, decimal precision facilitates reconstruction; it does not describe measurement accuracy. The analysis uses a frozen census of 91 functional urban areas (FUAs), so no population confidence interval is attached to deterministic scenario differences. The source products do not supply a joint error model.

\section{Source states, target grid and four arithmetic weights}
\label{sec:source}
\subsection{Frame and processing sequence}
The roster is the fixed set of GHS-FUA R2019A units with \path{Cntry_name=India} and 2015 population at least one million. The calculation is anchored to the exact 100 m GHSL study grid in World Mollweide (ESRI:54009), including its affine transform, cell indices and FUA mask. The FUA selection refers to this product release, not every present-day Indian urban area. The two GHSL epochs are building-surface estimates; their labels do not make them independent, contemporaneous image observations of construction.

The construction sequence is as follows. (1) Register the 2015 and 2020 GHSL building-surface arrays to the frozen grid and apply the study-unit mask. For finite valid epochs, retain positive differences $g_i=\max(B_{i,2020}-B_{i,2015},0)$. The extracted GHSL no-data sentinel is 65535 and is not differenced as a real surface value. (2) Enumerate every intersecting WSF asset. Convert the native source states to separate indicator components before average registration. Native source no-data is converted to nonfinite values; it is never treated as a settlement class. (3) Average-register each WSF component to the exact target grid. Where source tiles overlap, the implementation averages the valid tile-level registered components and records contributing-tile counts. Finite coverage and fraction partitions are checked; absent registered source coverage causes a failure. This finite-value coverage check does not quantify source-product accuracy. (4) Register each of the seven GloFAS layers separately, retaining valid dry zeros and treating source no-data as missing. The primary registration is nearest neighbour; average registration is a separate sensitivity. Overlapping hydraulic source domains are mosaicked by the maximum registered finite value. (5) Build one sparse table per FUA, containing only cells with $g_i>0$, and calculate the named weights and city depth summaries.

In WSF 2019, code 255 contributes documented settlement support and code 0 contributes documented nonsettlement support. Native code 1 is finite but undocumented and remains a separate quality-review state. In WSF Evolution, years 1985--2015 contribute positive historical settlement detection, while zero contributes its unresolved complement. Unsupported finite source codes fail the semantic checks. Continuous component registration preserves partial source support; it does not recover a finer-grid joint endpoint/history footprint.

\subsection{Variables and semantic boundaries}
Let $a_i$ be documented WSF 2019 support, $q_i$ the settlement fraction conditional on that documented portion, $u_i$ the undocumented code-1 fraction, and $p_i$ the WSF Evolution positive-detection fraction. Endpoint support is $s_i=a_iq_i$, not $q_i$ alone. Within finite registered coverage, $a_i+u_i=1$ and $p_i+z_i=1$, where $z_i$ is the unresolved history fraction, up to floating-point storage. Zero history response does not establish nonsettlement, recent settlement, or a construction date.
"""]
    semantics = [
        (r"\path{unit_key}, \path{eFUA_ID}", "Stable FUA identifiers. Names can repeat; identifiers distinguish the two Kolkata roster units."),
        (r"\path{grid_row}, \path{grid_column}", "Integer positions on the frozen 100 m target grid."),
        (r"\path{center_x_mollweide_m}, \path{center_y_mollweide_m}", "Cell-centre coordinates in metres in World Mollweide."),
        (r"\path{added_surface_m2} ($g_i$)", "Positive GHSL 2015--2020 building-surface product difference in square metres. It is neither a verified construction label nor necessarily the area of new settlement footprint."),
        (r"\path{endpoint_documented_fraction} ($a_i$)", "Fraction of finite registered WSF 2019 support assigned documented class semantics."),
        (r"\path{endpoint_settlement_fraction} ($q_i$)", "Settlement fraction conditional on the documented WSF 2019 portion; not a target-cell marginal without multiplication by documented support."),
        (r"\path{endpoint_undocumented_fraction} ($u_i$)", "Registered fraction with native code 1. No settlement or nonsettlement class is imputed."),
        (r"\path{endpoint_support_fraction} ($s_i$)", "Documented marginal endpoint support $a_iq_i$. This supplies a declared weight, not temporal truth for a GHSL change ending in 2020."),
        (r"\path{preexisting_detected_fraction} ($p_i$)", "Positive WSF Evolution detections through 2015, registered as a target-cell fraction."),
        (r"\path{preexisting_unresolved_fraction} ($z_i$)", "Complement of historical detection. It is unresolved and is never a negative settlement label."),
        (r"\path{glofas_permanent_water_qa}", "Registered permanent-water quality flag fraction. It is not vulnerability, flood duration, or a building label."),
        (r"\path{glofas_spurious_depth_qa}", "Registered spurious-depth quality flag fraction. Its exclusion is assessed as a declared sensitivity."),
        (r"\path{RP10_depth_m} through \path{RP500_depth_m}", "Seven static modelled fluvial depth layers at RP 10, 20, 50, 75, 100, 200 and 500 years, in metres. Sparse cell tables store nearest registration only."),
        (r"\path{integrated_modelled_depth_m} ($h_i$)", "Normalized finite-interval summary of the seven depth layers on annual-exceedance-probability coordinates; defined in Section S5."),
    ]
    text.append(longtable("Cell variables and their interpretation.", ["Stored field or symbol", "Meaning"], semantics, r"p{0.39\linewidth}p{0.55\linewidth}", "tab:variables"))
    text.append(r"""For a city $c$ and nonnegative declared weights $w_i$, the measure is
\begin{equation}
E_c(w;h)=\frac{\sum_{i\in c}w_i h_i}{\sum_{i\in c}w_i},\qquad \sum_{i\in c}w_i>0.
\label{eq:city}
\end{equation}
It is undefined if the denominator is zero. All retained primary records have all seven depth values, so the valid-depth and total-weight denominators coincide. The four original conventions are given in Table~\ref{tab:four}. The denominator has units inherited from $g_i$, but a weighted denominator is an arithmetic mass, not an independently observed construction area. Likewise, multiplying the endpoint and historical marginal fractions does not identify their spatial intersection. We call the arithmetic convention $w_i^{\mathrm{prod}}=g_i s_i(1-p_i)$ the product weight. Its stored machine identifier \path{joint_supported_screened} is retained for reproducibility; it does not denote the map-specific joint intersection obtained by intersecting the native parent maps before aggregation.
""")
    rows = []
    formulas = [r"$g_i$", r"$g_i s_i$", r"$g_i(1-p_i)$", r"$g_i s_i(1-p_i)$"]
    for scenario, formula in zip(SCENARIOS, formulas):
        subset = original[original.scenario.eq(scenario)]
        rows.append([SCENARIO_NAMES[scenario], formula, f(subset.denominator_m2.sum() / 1e6), f(subset.depth_m.median())])
    text.append(table("Four conventions and reconstructed totals.", ["Convention", "Weight", r"Total mass (km$^2$)", "Median depth (m)"], rows, "llrr", "tab:four"))
    text.append(rf"""The reconstruction uses {v['positive_change_record_count']:,} records and reproduces a total positive GHSL difference of {f(v['total_positive_GHSL_change_km2'])} km$^2$. The largest difference between reconstructed and published nearest city depths is {sci(v['max_city_original_four_scenario_depth_abs_error_m'])} m; the largest denominator difference is {f(v['max_city_original_four_scenario_denominator_abs_error_m2'], 9)} m$^2$. These small differences reflect stored single-precision fractions and arithmetic, rather than a new reference comparison. All seven RP values are finite for every released positive-change record.

\section{{Compatibility of marginal spatial support}}
\label{{sec:frechet}}
\subsection{{What the marginals identify}}
""")
    text.append(r"""Consider endpoint support $S$ and the complement $H^c$ of positive historical detection within a common target-cell support measure. Their marginals are $s_i$ and $1-p_i$. If $t_i$ is their joint intersection fraction, the probability/area identities for two events give
\begin{equation}
L_i=\max(0,s_i-p_i)\le t_i\le U_i=\min(s_i,1-p_i).
\label{eq:frechet}
\end{equation}
The upper bound follows because an intersection cannot exceed either marginal. The lower bound follows from $\Pr(S\cup H^c)\le1$. These bounds describe compatibility with the stored marginal representation, conditional on treating the registered fractions as marginals over common target-cell support. They do not account for geolocation error, classification error, temporal truth or uncertain source footprints.

The interval is an information-loss consequence of the stored marginal representation, not irreducible uncertainty about the physical settlement. If both native classification maps are retained, their positive endpoint indicator and complement of positive historical detection can be registered to a common finer grid under a declared categorical-registration rule. Computing their conjunction before aggregation identifies a map-specific joint fraction $t_i$. That operation restores joint information discarded by separate marginal aggregation; it does not establish that either map is correct. Even an identified mapped $t_i$ leaves a further allocation assumption: $g_i t_i$ distributes the total GHSL change in a 100 m cell in proportion to mapped joint area. It neither identifies the locations of changed building surfaces within the cell nor proves physical construction. The present bounds therefore concern ambiguity in the retained representation and must not be read as an irreducible land-surface uncertainty interval.

The product convention is feasible: $s_i(1-p_i)\le s_i$ and $s_i(1-p_i)\le1-p_i$, while
$s_i(1-p_i)-(s_i-p_i)=p_i(1-s_i)\ge0$.
Thus it lies in $[L_i,U_i]$. This inclusion is not evidence for independence or an observed joint footprint. The numerical check found no product-bound violation at tolerance $10^{-7}$ across all positive-change records.

\subsection{City ratio bounds and an optimization proof}
Define $\ell_i=g_iL_i$, $v_i=g_iU_i$. The desired city bounds are
\begin{equation}
E_c^- =\min_{\ell_i\le w_i\le v_i,\,\sum_iw_i>0}E_c(w;h),\qquad
E_c^+ =\max_{\ell_i\le w_i\le v_i,\,\sum_iw_i>0}E_c(w;h).
\label{eq:ratio-bounds}
\end{equation}
Assigning every cell its lower or upper endpoint gives two constructed city scenarios. Because both numerator and denominator change, those scenarios are not generally the ratio extrema.

For a trial depth $x$, minimizing the residual $\sum_iw_i(h_i-x)$ over a box can be done independently in each cell. Select the upper endpoint if $h_i<x$ and the lower endpoint if $h_i>x$. The resulting residual is
\begin{equation}
F_-(x)=\sum_i\ell_i(h_i-x)+\sum_i(v_i-\ell_i)\min(h_i-x,0).
\end{equation}
For maximization, select the upper endpoint where $h_i>x$, giving
\begin{equation}
F_+(x)=\sum_i\ell_i(h_i-x)+\sum_i(v_i-\ell_i)\max(h_i-x,0).
\end{equation}
If $\sum_i\ell_i>0$, both residuals are continuous and strictly decreasing. A feasible ratio below $x$ exists exactly when $F_-(x)<0$; a feasible ratio above $x$ exists exactly when $F_+(x)>0$. Their unique zeros therefore give $E_c^-$ and $E_c^+$. Bisection on the smallest and largest eligible cell depths, for 65 iterations, solves the two scalar problems. Cells with $v_i=0$ are omitted. If $\sum_i\ell_i=0$ but some $v_i>0$, zero total mass is feasible; over the positive-mass portion, the extrema are the smallest and largest eligible depths. If every $v_i=0$, the ratio is undefined. The implementation records these denominator cases rather than substituting zero depth.
""")
    text.append(rf"""All 91 cities have strictly positive lower masses. No city therefore admits a zero denominator under these conditional bounds. None has completely identified intersection weights, although the depth interval collapses within $10^{{-10}}$ m in {fr['collapsed_depth_compatibility_interval_city_count_tolerance_1e_10_m']} cities. Total lower, product and upper masses are {f(fr['total_lower_denominator_km2'])}, {f(fr['total_product_denominator_km2'])} and {f(fr['total_upper_denominator_km2'])} km$^2$. Interval width has median {f(fr['depth_width_median_m'])} m, interquartile range {f(fr['depth_width_q25_m'])}--{f(fr['depth_width_q75_m'])} m, and maximum {f(fr['depth_width_max_m'])} m in {escape(fr['depth_width_max_city'])}; {fr['depth_width_at_least_0_05_m_city_count']} cities have widths of at least 0.05 m.

The lower and upper endpoint scenarios have rank correlations {f(fr['lower_endpoint_scenario_rank_diagnostics_vs_product']['spearman_vs_baseline'])} and {f(fr['upper_endpoint_scenario_rank_diagnostics_vs_product']['spearman_vs_baseline'])} with the product convention. Those high correlations do not replace or contract the full ratio compatibility intervals in Table~\ref{{tab:all-bounds}}.

\subsection{{Explicitly synthetic algorithm checks}}
The optimizer was compared with exhaustive enumeration of positive-denominator box vertices in {vertex['synthetic_cases']} synthetic examples with one to six cells, using seed {vertex['random_seed']}. The {vertex['box_vertices_examined']:,} enumerated vertices agree with the optimized extrema within {sci(vertex['max_abs_extreme_error'])}. Three additional analytical corner cases include a positive fixed mass, a zero lower mass, and an all-zero upper mass. Synthetic values in these checks verify only the algorithm; they are neither human observations nor empirical settlement or flood validation.
""")
    bound_rows = []
    for row in frechet.sort_values("unit_key").itertuples():
        bound_rows.append([str(int(row.unit_key.rsplit("_", 1)[-1])), escape(row.eFUA_name), f(row.product_denominator_m2 / 1e6), f(row.product_depth_m), f(row.feasible_intersection_min_depth_m), f(row.feasible_intersection_max_depth_m), f(row.feasible_intersection_depth_width_m)])
    text.append(longtable("City product masses and exact conditional ratio bounds. Depths and widths are in metres; product mass is in km$^2$. FUA IDs distinguish repeated names.", ["FUA ID", "Name", "Mass", r"$E_{\rm prod}$", r"$E^-$", r"$E^+$", "Width"], bound_rows, "rlrrrrr", "tab:all-bounds"))
    text.append(r"""\section{Continuous exponents and binary endpoint choices}
\label{sec:weights}
The sensitivity family is $w_i(\alpha,\beta)=g_i s_i^\alpha(1-p_i)^\beta$, with each exponent in $\{0,0.5,1,2\}$. An exponent of zero means that evidence factor is omitted, including when its fraction is zero. The four corners $(0,0)$, $(1,0)$, $(0,1)$ and $(1,1)$ therefore recover the original conventions. Fractional powers and squared fractions test different emphasis on partial support; they are not estimated reliability parameters.

Ranking uses Spearman correlation of average city ranks on paired finite estimates. Absolute changes are calculated city by city before taking their median. A median paired difference is not the difference of two scenario medians. Top-ten overlap uses descending city depth and ascending stable FUA identifier to break a boundary tie. Table~\ref{tab:exponents} compares every setting with the product convention $(1,1)$.
""")
    rows = []
    for row in weights[weights.family.eq("exponent")].sort_values(["alpha", "beta"]).itertuples():
        rows.append([f(row.alpha, 1), f(row.beta, 1), f(row.total_denominator_km2), f(row.median_depth_m), f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count))])
    text.append(table("All exponent settings versus the product weight. All settings have 91 finite city pairs.", [r"$\alpha$", r"$\beta$", "Mass", "Median", r"$\rho$", "Median abs.", "Max. abs.", "Top 10"], rows, "rrrrrrrr", "tab:exponents", "footnotesize", "Mass is the total arithmetic denominator in km$^2$; median and absolute differences are in metres; Top 10 is overlap count out of ten."))
    text.append(r"""The binary alternative is $w_i(\tau)=g_i\mathbf{1}(s_i\ge\tau)(1-p_i)$, for $\tau\in\{0.25,0.50,0.75\}$. Only endpoint support is thresholded; the historic factor remains continuous. Thresholding replaces the endpoint fraction with unit support above a cutoff, so it can increase or decrease the denominator relative to a continuous fraction. It is a declared overlay convention, not a verified class decision.
""")
    rows = []
    for row in weights[weights.family.eq("binary_endpoint")].sort_values("threshold").itertuples():
        rows.append([f(row.threshold, 2), str(int(row.paired_city_count)), f(row.total_denominator_km2), f(row.median_depth_m), f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count))])
    text.append(table("Binary endpoint alternatives versus continuous product weights.", [r"$\tau$", "$n$", "Mass", "Median", r"$\rho$", "Median abs.", "Max. abs.", "Top 10"], rows, "rrrrrrrr", "tab:binary", "footnotesize", "At 0.75, Kolhapur (FUA 07881) and Kolkata (FUA 10453) have zero retained mass. Their depths are undefined and are excluded from paired ranking and depth medians; they are never entered as zero. The overlap comparison is calculated within the paired finite cities."))
    text.append(r"""\section{Undocumented endpoint support and unresolved history}
\label{sec:semantics}
\subsection{WSF 2019 native code 1}
The original base-raster audit found the undocumented native value in 52 of 56 WSF 2019 tiles. Its base-block reads do not request an output shape that would select overviews, so an overview-only explanation has been excluded by that implementation check. The product documentation has not established a semantic interpretation of code 1; this observation does not identify the origin or correctness of the code.

For coding sensitivity, endpoint support ranges from $s_i$ to $s_i+u_i$. The lower endpoint either leaves code 1 unassigned or supplies no positive settlement support under a nonsettlement assignment; those choices share a number while making different semantic assertions. The upper endpoint supplies support to every undocumented portion. Under product weights, the additional eligible mass is $g_i u_i(1-p_i)$. Its allocation can vary by cell. The box $g_is_i(1-p_i)\le w_i\le g_i(s_i+u_i)(1-p_i)$ is therefore analyzed with the same ratio optimizer as Section S2. Assigning all undocumented portions as settlement is one endpoint scenario and need not maximize or minimize depth.
""")
    text.append(rf"""Across all positive GHSL differences, the weighted undocumented fraction $\sum_i g_i u_i/\sum_i g_i$ is {f(100 * undocumented_fraction, 6)}\%, equivalent to {f(undocumented_total, 6)} m$^2$ of arithmetic mass. The largest city fraction is {f(100 * max_u.undocumented_GHSL_weighted_fraction, 6)}\% in {escape(max_u.eFUA_name)}. The maximum absolute all-supported versus unassigned product-depth difference is {f(coding.joint_all_supported_delta_m.abs().max())} m; the largest arbitrary-assignment interval width is {f(max_coding.joint_possible_assignment_width_m)} m, also in {escape(max_coding.eFUA_name)}. These are conditional coding bounds, not settlement-accuracy bounds.
""")
    rows = []
    for row in coding.sort_values(["undocumented_GHSL_weighted_fraction", "unit_key"], ascending=[False, True]).head(10).itertuples():
        rows.append([escape(row.eFUA_name), f(100 * row.undocumented_GHSL_weighted_fraction), f(row.joint_u_relative_increment_to_base_denominator * 100), f(row.joint_no_undocumented_support_depth_m), f(row.joint_all_undocumented_supported_depth_m), f(row.joint_possible_assignment_min_depth_m), f(row.joint_possible_assignment_max_depth_m)])
    text.append(table("Ten largest city undocumented GHSL-weighted fractions, ordered by that diagnostic.", ["City", r"$u$ mass (\%)", r"Product mass + (\%)", "Unassigned", "All supported", "Ratio min.", "Ratio max."], rows, "lrrrrrr", "tab:code1", "footnotesize", "The two mass percentages use different denominators: all positive GHSL difference and baseline product mass, respectively. Depths are in metres."))
    text.append(r"""\subsection{What alternative WSF Evolution zero semantics change}
Relabelling the unresolved historical complement as nonsettlement while leaving the same numeric $1-p_i$ weights produces exactly zero numeric change. It would nevertheless add an unsupported negative class claim. The published approach instead preserves the unresolved state.

Excluding unresolved source portions first leaves only portions with positive historic detection. A screen that then removes all positive historic detection leaves zero weight. Thus this combined interpretation has no defined screened city depth in all 91 FUAs. Multiplying the two mutually exclusive aggregated partitions to manufacture a retained fraction would not correspond to that operation. A meaningful numeric comparison retains all GHSL evidence or endpoint-supported evidence and then compares the presence and absence of the positive-detection screen.
""")
    rows = []
    for label, column in [("GHSL: screen minus no screen", "ghsl_screen_delta_m"), ("Endpoint: screen minus no screen", "endpoint_screen_delta_m")]:
        values = history[column]
        rows.append([label, f(values.median()), f(values.abs().median()), f(values.abs().max())])
    text.append(table("No-history-screen comparisons.", ["Comparison", "Median signed (m)", "Median absolute (m)", "Maximum absolute (m)"], rows, "lrrr", "tab:history", "footnotesize"))
    text.append(r"""\section{Hazard-summary choices and grid registration}
\label{sec:hazard}
For seven return periods $r_k\in\{10,20,50,75,100,200,500\}$ years, define $a_k=1/r_k$. The primary finite-interval summary is
\begin{equation}
h_i=\frac{\sum_{k=1}^{6}\frac{d_{i,r_k}+d_{i,r_{k+1}}}{2}(a_k-a_{k+1})}{0.1-0.002}.
\label{eq:hazard}
\end{equation}
It linearly interpolates supplied depths on the probability coordinate over $[0.002,0.1]$ and divides by this interval width. It excludes more frequent events beyond RP10 and the tail beyond RP500. It is not annual expected depth, event inundation, loss, vulnerability or flood risk. Section S8 also documents that the supplied RP sequence is not everywhere monotone, so it is not treated as a universally coherent annual depth quantile function.

The uniform seven-RP mean, $\bar d_i=\frac{1}{7}\sum_k d_{i,r_k}$, gives each supplied layer equal weight. A single RP summary uses $d_{i,r}$ directly. These choices change the hazard estimand. Ranking stability therefore does not make their depth magnitudes interchangeable. The next four tables compare each alternative with the finite integral within the same weight convention.
""")
    for scenario in SCENARIOS:
        rows = []
        frame = hazard[hazard.scenario.eq(scenario)].set_index("hazard_metric")
        for metric in METRIC_ORDER:
            row = frame.loc[metric]
            label = {"uniform_seven_RP_mean": "Uniform RP mean", "normalized_exceedance_trapezoid": "Finite integral"}.get(metric, metric)
            rows.append([label, f(row.median_depth_m), f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count)), "---" if metric == "normalized_exceedance_trapezoid" else escape(row.max_delta_city)])
        text.append(table(f"Hazard definitions under {SCENARIO_NAMES[scenario].lower()} weights; 91 city pairs.", ["Metric", "Median", r"$\rho$", "Median abs.", "Max. abs.", "Top 10", "Max.-change city"], rows, "lrrrrrl", size="footnotesize", note="Depths and changes are in metres. A dash in the reference row avoids labelling an arbitrary city as an extreme when every difference is zero."))
    rows = []
    for scenario in SCENARIOS:
        row = alignment[alignment.scenario.eq(scenario)].iloc[0]
        rows.append([SCENARIO_NAMES[scenario], f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count))])
    text.append(table("Published average versus nearest city summaries.", ["Weight convention", r"$\rho$", "Median abs. (m)", "Max. abs. (m)", "Top 10"], rows, "lrrrr", "tab:alignment", "footnotesize"))
    text.append(r"""The average-registration calculation is available only in the original city tables. The released sparse cell tables contain nearest depths, so new exponent, threshold and support-bound calculations are not recomputed under average registration. This limits the registration check to the original four conventions. It assesses registration sensitivity within the same hazard product and supplies no external flood-accuracy evidence.

\section{Small positive GHSL differences}
\label{sec:ghsl}
The primary inclusion condition is $g_i>0$. To assess sensitivity to small within-product changes, alternatives retain only cells with $g_i>\gamma$, for $\gamma\in\{0,10,50,100,500\}$ m$^2$. The strict inequality matters: a cell at the cutoff is excluded. The retained fraction is calculated with all positive GHSL differences in the denominator. These cutoffs neither identify measurement error nor distinguish construction from infill or temporal-model differences.
""")
    qa_order = [f"GHSL_g_gt_{k}_m2" for k in (0, 10, 50, 100, 500)]
    for scenario in SCENARIOS:
        frame = qa[qa.scenario.eq(scenario)].set_index("setting")
        rows = []
        for setting in qa_order:
            row = frame.loc[setting]
            gamma = setting.split("_")[3]
            rows.append([gamma, f(row.retained_positive_GHSL_fraction * 100, 3), f(row.total_denominator_km2), f(row.median_depth_m), f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count))])
        text.append(table(f"Positive-difference cutoffs under {SCENARIO_NAMES[scenario].lower()} weights; 91 city pairs.", [r"$\gamma$", r"GHSL retained (\%)", "Mass", "Median", r"$\rho$", "Median abs.", "Max. abs.", "Top 10"], rows, "rrrrrrrr", size="footnotesize", note="Mass is in km$^2$; depth and changes are in metres. Correlations and changes use the same convention at $g>0$ as reference."))
    text.append(r"""\section{GloFAS quality-flag exclusions}
\label{sec:qa}
The released registered permanent-water and spurious-depth fractions are finite in every positive-change cell. Three conservative exclusions discard a whole 100 m cell if any registered source support has a positive permanent-water flag, a positive spurious-depth flag, or either. They therefore remove more than just the flagged subcell fraction when support is partial. The primary representation preserves supplied hazard and QA information; exclusions are separate stress calculations. Flags do not validate a construction label, and discarding flagged support is not asserted to recover true flood depth.
""")
    qa_settings = {"exclude_any_permanent_water_QA": "Permanent water", "exclude_any_spurious_depth_QA": "Spurious depth", "exclude_either_QA": "Either flag"}
    for scenario in SCENARIOS:
        rows = []
        frame = qa[qa.scenario.eq(scenario)].set_index("setting")
        for setting, label in qa_settings.items():
            row = frame.loc[setting]
            rows.append([label, f(row.retained_positive_GHSL_fraction * 100, 3), f(row.total_denominator_km2), f(row.median_depth_m), f(row.spearman_vs_baseline), f(row.median_absolute_delta_m), f(row.max_absolute_delta_m), str(int(row.top10_overlap_count))])
        text.append(table(f"QA exclusions under {SCENARIO_NAMES[scenario].lower()} weights; 91 city pairs.", ["Excluded support", r"GHSL retained (\%)", "Mass", "Median", r"$\rho$", "Median abs.", "Max. abs.", "Top 10"], rows, "lrrrrrrr", size="footnotesize", note="Mass is in km$^2$; depth and changes are in metres. Reference is the unexcluded calculation under the same convention."))
    qa_city = read_csv("revision_qa_threshold_city.csv").merge(original, on=["unit_key", "eFUA_name", "scenario"], suffixes=("", "_base"))
    qa_city["absolute_delta"] = (qa_city.depth_m - qa_city.depth_m_base).abs()
    qa_extreme = qa_city[qa_city.scenario.eq("joint_supported_screened") & qa_city.setting.eq("exclude_either_QA")].sort_values(["absolute_delta", "unit_key"], ascending=[False, True]).iloc[0]
    text.append(rf"""Under product weights, excluding either flag changes the largest city measure by {f(qa_extreme.absolute_delta)} m in {escape(qa_extreme.eFUA_name)}, from {f(qa_extreme.depth_m_base)} to {f(qa_extreme.depth_m)} m. This local change should be considered alongside the city-rank correlation rather than hidden by it.

\section{{Nonmonotone supplied return-period depths}}
\label{{sec:nonmonotone}}
A decrease is registered when $d_{{i,r_{{k+1}}}}-d_{{i,r_k}}<-10^{{-6}}$ m. There are {mono['decreasing_cell_count']:,} affected cells, representing {f(100 * mono['decreasing_cell_fraction'])}\% of positive-change records and {f(100 * mono['decreasing_GHSL_weighted_fraction'])}\% of positive GHSL arithmetic mass. Counts by adjacent pair can overlap when one cell decreases at more than one pair. Of affected GHSL mass, {f(100 * mono['decreasing_GHSL_fraction_with_either_QA_flag'])}\% intersects a positive permanent-water or spurious-depth QA flag.
""")
    rows = []
    for pair in mono["adjacent_RP_pairs"]:
        rows.append([str(pair["lower_RP"]), str(pair["higher_RP"]), str(pair["decreasing_record_count"]), f(pair["decreasing_GHSL_change_m2"], 0), f(pair["max_drop_m"]), f(pair["mean_drop_among_decreasing_records_m"])])
    text.append(table("Adjacent-pair decreases in supplied layers.", ["Lower RP", "Higher RP", "Records", "GHSL mass (m$^2$)", "Max. drop (m)", "Mean drop (m)"], rows, "rrrrrr", "tab:decreases", "footnotesize"))
    worst = mono["largest_drop_diagnostic_record"]
    text.append(rf"""The largest drop, {f(worst['drop_m'])} m, is in {escape(worst['eFUA_name'])} (FUA {int(worst['unit_key'].rsplit('_', 1)[-1])}), from RP{worst['lower_RP']} to RP{worst['higher_RP']}. The supplied depth sequence is {', '.join(f(x, 3) for x in worst['RP_depths_m'].values())} m. This diagnostic cell has $g_i={f(worst['added_surface_m2'], 0)}$ m$^2$, $s_i={f(worst['endpoint_support_fraction'], 0)}$, $p_i={f(worst['preexisting_detected_fraction'], 0)}$, and spurious-depth fraction {f(worst['spurious_depth_QA_fraction'], 0)}. Its product weight is therefore zero. The record is retained for tracing the supplied-layer anomaly, not as independent evidence of its cause.

For numeric sensitivity only, define $\widetilde d_{{i,r_k}}=\max_{{j\le k}}d_{{i,r_j}}$, recompute the finite integral and retain the original four weight arrays. This cumulative-maximum transformation raises depths to enforce monotonicity. It is a labelled stress calculation, not a validated correction, and it does not overwrite parent layers or replace the primary estimates.
""")
    rows = []
    for scenario in SCENARIOS:
        item = mono["cummax_city_shift_by_scenario"][scenario]
        rows.append([SCENARIO_NAMES[scenario], sci(item["median_shift_m"]), f(item["max_shift_m"], 9), escape(item["max_shift_city"])])
    text.append(table("Cumulative-maximum depth sensitivity with fixed original weights.", ["Convention", "Median shift (m)", "Maximum shift (m)", "Maximum-shift city"], rows, "lrrl", "tab:cummax", "footnotesize"))
    text.append(r"""\section{Fixed application examples}
\label{sec:cases}
Guwahati and Sultanpur illustrate the previously reported opposite extremes of product-versus-GHSL depth changes. The third example, Delhi [New Delhi], was selected before the new sensitivity results were calculated because it is the largest-population FUA in the frozen roster. The selection record precedes cell-depth computation in the run log. These three examples are neither a representative city sample nor independent validation sites.

The tables report all seven return periods and both aggregate hazard summaries under all four conventions. The common positive-cell domain and the changing arithmetic denominators are shown explicitly. The additional paired-year GLAD comparison is described in the main article; its aggregate results are not inferred from these three examples. The maps in Figure~\ref{fig:case-maps} locate evidence for reference review and are not ground-truth settlement or event-inundation maps.
""")
    text.append(r"""\subsection{A concrete 30-cell queue for dated reference review}
The accompanying \path{revision_case_review_queue.csv} contains 30 actual positive-GHSL cells: the ten largest recorded $g_i h_i$ values within each of the three examples, in descending order. This score is used solely as an illustrative review-priority score with units inherited as m$^3$. It is not a calibrated risk, expected loss, construction accuracy or ground-truth score. The CSV retains longitude and latitude, target-grid row and column, all source fractions, all seven RP depths and both GloFAS QA fractions. The unweighted medians and flagged-cell counts for these deliberately selected cells are reported below; they do not summarize an unbiased city sample.

The queue supports a subsequent review with references whose acquisition dates, spatial resolution and visibility are recorded for the 2015--2020 interval. Producing this queue does not perform that review or create a verified label. The executed joint-preserving overlay in Section S11 refines map-state selection while retaining the within-cell proportional allocation limitation described in Section S2.
""")
    queue_rows = []
    for city in ("Delhi", "Guwahati", "Sultanpur"):
        item = queue_summary.loc[city]
        queue_rows.append([city, str(int(item.selected_cells)), f(item.median_GLAD_new_fraction, 9), str(int(item.any_QA_count)), f(item.min_score_m3, 3), f(item.max_score_m3, 3)])
    text.append(table("Diagnostics for the concrete cell-review queue.", ["City", "$n$", "Median GLAD new fraction", "Any-QA cells", "Min. score", "Max. score"], queue_rows, "lrrrrr", "tab:review-queue", "footnotesize", "Median GLAD new fraction is unweighted across the selected ten cells. A cell counts as Any-QA when either registered QA fraction is positive. Score is the recorded $g_i h_i$ priority value in m$^3$, not a risk estimate."))
    for city in ("Guwahati", "Sultanpur", "Delhi"):
        queue_rows = []
        for row in queue[queue.city.eq(city)].sort_values("review_order").itertuples():
            qa_label = "P" if row.glofas_permanent_water_qa > 0 else ""
            qa_label += "S" if row.glofas_spurious_depth_qa > 0 else ""
            qa_label = qa_label or "---"
            queue_rows.append([str(int(row.review_order)), f(row.center_longitude, 5), f(row.center_latitude, 5), f(row.added_surface_m2, 0), f(row.integrated_modelled_depth_m, 6), f(row.endpoint_support_fraction, 4), f(row.preexisting_detected_fraction, 4), f(row.endpoint_undocumented_fraction, 4), f(row.glad_new_built_fraction, 6), qa_label])
        text.append(table(f"{city}: the ten queued cells and their recorded source states.", ["Order", "Longitude", "Latitude", "$g$", "$h$", "$s$", "$p$", "$u$", "GLAD new", "QA"], queue_rows, "rrrrrrrrrl", size="footnotesize", note="$g$ is in m$^2$ and $h$ in metres; source quantities and GLAD new are fractions. P and S indicate positive permanent-water and spurious-depth QA, respectively. Coordinates locate cell centres; rounding here serves compact display, while the CSV retains the recorded coordinates and all fields."))
    case_order = ["Guwahati", "Sultanpur", "Delhi [New Delhi]"]
    for city in case_order:
        frame = cases[cases.eFUA_name.eq(city)]
        pivot = frame.pivot(index="hazard_metric", columns="scenario", values="depth_m")
        denom = frame.groupby("scenario").denominator_m2.first()
        rows = []
        for metric in METRIC_ORDER:
            label = {"uniform_seven_RP_mean": "Uniform RP mean", "normalized_exceedance_trapezoid": "Finite integral"}.get(metric, metric)
            rows.append([label, *[f(pivot.loc[metric, scenario]) for scenario in SCENARIOS]])
        note = "Arithmetic masses (km$^2$), in column order: " + ", ".join(f(denom[scenario] / 1e6) for scenario in SCENARIOS) + ". All depth entries are in metres."
        text.append(table(f"{escape(city)}: complete hazard-summary application.", ["Metric", "GHSL only", "Endpoint", "Preperiod", "Product"], rows, "lrrrr", label="tab:case-" + city.split()[0].lower(), size="small", note=note))
    text.append(r"""\IfFileExists{figures/figure_3_case_maps.pdf}{%
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figure_3_case_maps.pdf}
\caption{Spatial diagnostics for the three fixed examples. Panels locate positive GHSL product differences, paired-year GLAD class fractions and GloFAS quality flags on the registered study grid. Teal circles mark the ten queued cells per city selected by descending $g_i h_i$ for dated reference review. White background denotes cells outside displayed positive-GHSL support; it does not indicate absence of hazard. The panels provide review locations, not verified construction, calibrated risk or flood-event labels. The main article defines the paired-product comparison and its boundaries.}
\label{fig:case-maps}
\end{figure}
}{%
\begin{figure}[htbp]
\centering
\fbox{\parbox{0.92\linewidth}{Case-map figure is generated separately from the complete paired-product analysis. This compilation retains the application tables; it does not insert partial cross-product results.}}
\caption{Spatial case diagnostics; see the completed case-map artifact accompanying the main article.}
\label{fig:case-maps}
\end{figure}
}
\FloatBarrier

\section{Numerical verification, excluded legacy labels and reproducibility}
\label{sec:verification}
\subsection{Software checks and their limits}
The original release reported 12 targeted tests, grouped in Table~\ref{tab:tests}. This description records the conditions checked by that release; it is not a field-reference assessment. The separate verifier reconstructs primary metrics from sparse tables without calling the construction function. Independence of software paths can catch implementation disagreement, but does not make the source evidence independent or establish accuracy.
""")
    rows = [
        ["WSF semantic handling", "4", "Conservation of fractions; unresolved zero; unsupported-code failure; separate code-1 preservation."],
        ["Database construction", "5", "Declared weights; retained unresolved states; rejected invalid partitions; nonfinite-data handling; no code-1 endpoint support."],
        ["Separate numerical verifier", "2", "Rebuilt weights and city summaries; rejection of a deliberately mismatched cell depth."],
        ["Census summary", "1", "Exact distributional and paired-city summaries for the frozen 91-city frame."],
    ]
    text.append(table("Original software-test families, totalling 12.", ["Family", "$n$", "Tested condition"], rows, r"p{0.27\linewidth}rp{0.61\linewidth}", "tab:tests", "small"))
    text.append(rf"""The revision calculation reconstructs all four city measures, checks seven-layer finiteness, discloses nonmonotone depths, checks fraction partitions, and verifies the conditional ratio optimizer with synthetic vertex enumeration. The executed deterministic analysis completed in {f(run['elapsed_seconds'], 3)} s on the local workstation. This timing covers the released sparse-table calculations only, not downloads, source preparation, cross-product acquisition or author interpretation. The largest cell stored-versus-recomputed finite-integral difference is {sci(v['max_cell_stored_vs_recomputed_integral_abs_error_m'])} m; the largest detected-plus-unresolved partition error is {sci(v['max_historic_detected_plus_unresolved_partition_error'])}.

\subsection{{Exclusion of legacy AI-derived labels}}
An audit of legacy development materials found 1,200 label records: 300 marked \path{{codex_assisted_visual_interpretation}} and 900 marked \path{{landsat_model_transfer_v1}}. Their metadata set \path{{independent_second_human=false}} and \path{{human_ground_truth_claim_allowed=false}}. Those records and repeatability statistics derived from them are excluded from the current independent-accuracy evidence. AI-assisted interpretation is not a human reference panel; model-transferred labels are not independently observed construction. Neither their counts, internal repeatability nor their model agreement is used to assert settlement or flood accuracy. This exclusion is separate from the main article's disclosure of the actual assistance used in the present revision.

\subsection{{Reproduction records}}
The executed calculation is implemented by \path{{revision_sensitivity.py}}. The supplementary tables are generated from its CSV and JSON outputs by \path{{supplement_tables.py}}. The generator also reads the completed 30-cell review queue; it does not read running or partial GLAD aggregate results. The accompanying \path{{revision_run_log.json}} records software versions, actual elapsed time, the synthetic-verification seed and application selection before computation. The released IUFEE v1.2 table schema remains the input specification. The revision's numerical tables retain stable FUA identifiers, including repeated city names, and undefined depths retain missing values rather than zeros.
""")
    rows = [
        [r"\path{revision_original_city.csv}", "All four reconstructed city masses and finite-integral depths."],
        [r"\path{revision_weight_city.csv}, \path{revision_weight_summary.csv}", "Every exponent and binary-threshold result, paired-city counts and ranking diagnostics."],
        [r"\path{revision_frechet_city.csv}, \path{revision_frechet_summary.json}", "Cell-marginal compatibility-derived city masses, endpoint scenarios, exact ratio bounds and zero-denominator diagnostics."],
        [r"\path{revision_coding_bounds_city.csv}, \path{revision_history_city.csv}", "Undocumented-code assignments and no-history-screen comparisons."],
        [r"\path{revision_hazard_city.csv}, \path{revision_hazard_summary.csv}, \path{revision_alignment_summary.csv}", "All seven RP city measures, both aggregate summaries, and original registration comparison."],
        [r"\path{revision_qa_threshold_city.csv}, \path{revision_qa_threshold_summary.csv}", "All GHSL-difference cutoffs and whole-cell QA exclusions, with retained masses."],
        [r"\path{revision_monotonicity_city.csv}, \path{revision_monotonicity_pairs.csv}, \path{revision_monotonicity_summary.json}", "Nonmonotone-depth counts, severities, diagnostic record and labelled cumulative-maximum sensitivity."],
        [r"\path{revision_application_cities.csv}", "Every RP and aggregate hazard measure for the three fixed examples under four conventions."],
        [r"\path{revision_case_review_queue.csv}", "Actual 30-cell illustrative review queue with coordinates, source fractions, QA flags and recorded priority score."],
        [r"\path{revision_validation.json}, \path{revision_run_log.json}", "Reconstruction tolerance checks and actual execution record."],
    ]
    text.append(longtable("Machine-readable evidence corresponding to this supplement.", ["File", "Contents"], rows, r"p{0.50\linewidth}p{0.44\linewidth}", "tab:files"))
    text.append(r"""\noindent The interpretation remains conditional: arithmetic reproduction, deterministic sensitivity and compatible marginal-support bounds establish what can be reconstructed from stated product choices. They do not establish physically verified construction area, a calibrated joint error model, or independently validated flood depths.
\end{document}
""")
    appendix = "% BEGIN ROOT-OWNED SUPPLEMENT SECTIONS\n" + external_sections + "\n% END ROOT-OWNED SUPPLEMENT SECTIONS\n"
    generated = "\n".join(text).replace(r"\end{document}", appendix + r"\end{document}")
    OUTPUT.write_text(generated, encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "characters": OUTPUT.stat().st_size,
                      "read_complete_run_only": True, "city_bound_rows": len(frechet),
                      "application_rows": len(cases), "binary_high_threshold_pairs": 89,
                      "case_map_present": (OUTPUT.parent / "figures" / "figure_3_case_maps.pdf").exists(),
                      "review_queue_cells": len(queue), "review_queue_summary": queue_summary.to_dict(orient="index"),
                      "preserved_root_owned_sections": bool(external_sections)}, indent=2))

if __name__ == "__main__":
    main()
