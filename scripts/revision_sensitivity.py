"""Deterministic revision analyses of the released IUFEE v1.2 cell tables.

Read-only inputs; all outputs must be on D:. No source acquisition, model fit,
confidence intervals, settlement truth labels, or physical construction claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import itertools
import json
import platform
from pathlib import Path
import time

import numpy as np
import pandas as pd

DEFAULT_INPUT = Path(r"D:\codex\sci\remote_sensing_sci_novelty_audit\guangzhou_india_flood_exposure_study\grsl_submission_2026\zenodo_release\IUFEE_v1_2\data\database_v1_2")
DEFAULT_OUTPUT = Path(r"D:\MLWork\IUFEE_revision_20261005\results")
RPS = np.array([10, 20, 50, 75, 100, 200, 500], dtype=np.float64)
EXPONENTS = (0.0, 0.5, 1.0, 2.0)
THRESHOLDS = (0.25, 0.5, 0.75)
GHSL_THRESHOLDS_M2 = (0, 10, 50, 100, 500)
SCENARIOS = {
    "ghsl_only": (0.0, 0.0),
    "endpoint_supported": (1.0, 0.0),
    "preexisting_detected_screened": (0.0, 1.0),
    "joint_supported_screened": (1.0, 1.0),
}
JOINT = "joint_supported_screened"
LOCAL_TIME = timezone(timedelta(hours=8))


def stamp() -> str:
    return datetime.now(LOCAL_TIME).isoformat(timespec="seconds")


def record(weights: np.ndarray, depth: np.ndarray, total: float) -> dict:
    denominator = float(np.sum(weights, dtype=np.float64))
    return {
        "denominator_m2": denominator,
        "retained_added_surface_fraction": denominator / total,
        "depth_m": float(np.sum(weights * depth, dtype=np.float64) / denominator) if denominator > 0 else np.nan,
    }


def ratio_bounds(lower: np.ndarray, upper: np.ndarray, depth: np.ndarray) -> tuple[float, float]:
    """Exact box-constrained linear-fractional extrema, restricted to sum(w)>0.

    The minimizing Dinkelbach residual is sum(l*(h-z)) plus
    sum((u-l)*min(h-z, 0)); its unique zero gives the minimum when sum(l)>0.
    The analogous maximizing residual uses max. A zero lower denominator is
    explicitly permitted in the feasible set; extrema over its positive-weight
    portion are min/max eligible depths. All-zero upper weights are undefined.
    """
    active = upper > 0
    if not np.any(active):
        return np.nan, np.nan
    l, u, h = lower[active], upper[active], depth[active]
    if float(l.sum()) == 0:
        return float(h.min()), float(h.max())
    delta = u - l
    low_edge, high_edge = float(h.min()), float(h.max())
    solutions = []
    for maximize in (False, True):
        lo, hi = low_edge, high_edge
        for _ in range(65):
            mid = (lo + hi) / 2
            residual = h - mid
            variable = np.maximum(residual, 0) if maximize else np.minimum(residual, 0)
            value = float(np.sum(l * residual) + np.sum(delta * variable))
            if value > 0:
                lo = mid
            else:
                hi = mid
        solutions.append((lo + hi) / 2)
    return solutions[0], solutions[1]


def rank_statistics(candidate: pd.DataFrame, baseline: pd.DataFrame) -> dict:
    pair = candidate[["unit_key", "depth_m"]].merge(
        baseline[["unit_key", "depth_m"]], on="unit_key", suffixes=("", "_baseline"), validate="one_to_one"
    ).dropna()
    delta = pair.depth_m - pair.depth_m_baseline
    correlation = float(pair.depth_m.rank(method="average").corr(pair.depth_m_baseline.rank(method="average")))
    # Stable unit identifiers break any tie at the top-ten boundary.
    top = set(pair.sort_values(["depth_m", "unit_key"], ascending=[False, True]).head(10).unit_key)
    reference_top = set(pair.sort_values(["depth_m_baseline", "unit_key"], ascending=[False, True]).head(10).unit_key)
    return {
        "paired_city_count": len(pair),
        "spearman_vs_baseline": correlation,
        "median_absolute_delta_m": float(delta.abs().median()),
        "max_absolute_delta_m": float(delta.abs().max()),
        "median_signed_delta_m": float(delta.median()),
        "top10_overlap_count": len(top & reference_top),
        "top10_overlap_fraction": len(top & reference_top) / min(10, len(pair)),
    }


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format="%.12g")


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a small report table without an optional tabulate dependency."""
    columns = list(frame.columns)
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in frame.itertuples(index=False, name=None):
        cells = [f"{x:.6f}" if isinstance(x, (float, np.floating)) else str(x) for x in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def validate_ratio_optimizer() -> dict:
    """Synthetic examples verify the algorithm, never the empirical products."""
    rng = np.random.default_rng(20261005)
    errors = []
    vertices_examined = 0
    for n in range(1, 7):
        for trial in range(16):
            lower = rng.uniform(0, 2, n)
            if trial % 4 == 0:
                lower[:] = 0
            upper = lower + rng.uniform(0, 3, n)
            depth = rng.uniform(0, 10, n)
            vertex_ratios = []
            for choices in itertools.product((0, 1), repeat=n):
                weight = np.where(np.asarray(choices), upper, lower)
                denominator = weight.sum()
                if denominator > 0:
                    vertex_ratios.append(float(np.sum(weight * depth) / denominator))
                vertices_examined += 1
            found = ratio_bounds(lower, upper, depth)
            expected = (min(vertex_ratios), max(vertex_ratios))
            error = float(np.max(np.abs(np.asarray(found) - expected)))
            if error > 1e-11:
                raise AssertionError(f"Fractional-ratio optimizer failed synthetic case n={n}, trial={trial}, error={error}")
            errors.append(error)
    return {"synthetic_cases": len(errors), "box_vertices_examined": vertices_examined,
            "random_seed": 20261005, "max_abs_extreme_error": max(errors),
            "purpose": "Synthetic numerical algorithm verification only; not empirical settlement or flood validation."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    if output.drive.upper() != "D:":
        raise ValueError(f"Revision calculation outputs must be on D:, got {output}")
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    log = {
        "started_at_Asia_Shanghai": stamp(),
        "input_read_only": str(source),
        "output": str(output),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "operation": "deterministic analysis of released derived data; no downloads, fitting, or external accuracy validation",
        "per_city": [],
    }
    # Analytic corner checks are meaningful tests of the new optimization code.
    assert np.allclose(ratio_bounds(np.array([1., 0.]), np.array([1., 1.]), np.array([1., 3.])), (1., 2.))
    assert np.allclose(ratio_bounds(np.zeros(2), np.ones(2), np.array([1., 3.])), (1., 3.))
    assert all(np.isnan(v) for v in ratio_bounds(np.zeros(2), np.zeros(2), np.array([1., 3.])))
    log["ratio_vertex_enumeration_verification"] = validate_ratio_optimizer()

    evidence = pd.read_csv(source / "city_evidence_summary.csv")
    published = pd.read_csv(source / "city_exposure_scenarios.csv")
    identity = evidence.set_index("unit_key")
    # Selection is fixed before accessing any cell depths or newly computed result.
    largest_key = evidence.sort_values(["population_2015", "unit_key"], ascending=[False, True]).iloc[0].unit_key
    case_keys = [
        str(evidence.loc[evidence.eFUA_name.eq("Guwahati"), "unit_key"].iloc[0]),
        str(evidence.loc[evidence.eFUA_name.eq("Sultanpur"), "unit_key"].iloc[0]),
        str(largest_key),
    ]
    log["application_selection_before_depth_computation"] = {
        "Guwahati": "Previously reported largest positive joint-versus-GHSL difference; illustrates endpoint/history reweighting.",
        "Sultanpur": "Previously reported largest negative joint-versus-GHSL difference; illustrates the opposite direction.",
        str(identity.loc[largest_key, "eFUA_name"]): "Largest population in the frozen roster; an application example independent of new sensitivity results.",
        "purpose": "Interpretation examples, deliberately not an independent or representative validation sample.",
        "unit_keys": case_keys,
    }
    # Save the prespecified example choice before calculating results.
    (output / "revision_run_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")

    files = sorted((source / "expansion_cells_100m").glob("*.parquet"))
    if len(files) != 91:
        raise ValueError(f"Expected frozen 91-city census, got {len(files)} files")
    weight_rows, original_rows, coding_rows, history_rows, hazard_rows, frechet_rows = [], [], [], [], [], []
    qa_rows, monotonic_rows, monotonic_pair_rows = [], [], []
    total_g = total_u = 0.0
    affected_nonmonotonic_g = 0.0
    affected_nonmonotonic_flagged_g = 0.0
    worst_drop_reference = None
    total_cells = complete_hazard_cells = 0
    h_reconstruction_max_error = partition_max_error = 0.0
    product_bound_violations = monotonic_depth_violations = 0
    ap = 1 / RPS
    segment_width = ap[:-1] - ap[1:]
    for file in files:
        city_start = time.perf_counter()
        d = pd.read_parquet(file)
        key = str(d.unit_key.iloc[0])
        if d.unit_key.nunique() != 1 or key not in identity.index:
            raise ValueError(f"Unexpected city identity in {file}")
        name = str(identity.loc[key, "eFUA_name"])
        ident = {"unit_key": key, "eFUA_name": name}
        g = d.added_surface_m2.to_numpy(dtype=np.float64)
        s = d.endpoint_support_fraction.to_numpy(dtype=np.float64)
        p = d.preexisting_detected_fraction.to_numpy(dtype=np.float64)
        u = d.endpoint_undocumented_fraction.to_numpy(dtype=np.float64)
        unresolved = d.preexisting_unresolved_fraction.to_numpy(dtype=np.float64)
        retention = 1 - p
        rp_depth = d[[f"RP{int(r)}_depth_m" for r in RPS]].to_numpy(dtype=np.float64)
        if not (np.isfinite(g).all() and (g > 0).all() and np.isfinite(rp_depth).all()):
            raise ValueError(f"Invalid positive-change or hazard input for {key}")
        if not all(np.isfinite(x).all() and (x >= 0).all() and (x <= 1).all() for x in (s, p, u, unresolved)):
            raise ValueError(f"Invalid source fraction for {key}")
        h = np.sum(0.5 * (rp_depth[:, :-1] + rp_depth[:, 1:]) * segment_width, axis=1) / (ap[0] - ap[-1])
        h_reconstruction_max_error = max(h_reconstruction_max_error, float(np.max(np.abs(h - d.integrated_modelled_depth_m.to_numpy(dtype=float)))))
        partition_max_error = max(partition_max_error, float(np.max(np.abs(p + unresolved - 1))))
        adjacent_changes = np.diff(rp_depth, axis=1)
        nonmonotonic = np.any(adjacent_changes < -1e-6, axis=1)
        monotonic_depth_violations += int(nonmonotonic.sum())
        affected_nonmonotonic_g += float(np.sum(g[nonmonotonic]))
        total = float(g.sum())
        total_g += total
        total_u += float(np.sum(g * u))
        total_cells += len(d)
        complete_hazard_cells += int(np.sum(np.isfinite(rp_depth).all(axis=1)))
        original_weights = {scenario: g * np.power(s, a) * np.power(retention, b) for scenario, (a, b) in SCENARIOS.items()}
        for scenario, w in original_weights.items():
            original_rows.append({**ident, "scenario": scenario, **record(w, h, total)})
        # Positive product differences can be small; cutoffs are explicit numeric
        # sensitivity choices, not labels of valid versus invalid construction.
        qa_keep = {
            f"GHSL_g_gt_{threshold}_m2": g > threshold for threshold in GHSL_THRESHOLDS_M2
        }
        permanent = d.glofas_permanent_water_qa.to_numpy(dtype=np.float64)
        spurious = d.glofas_spurious_depth_qa.to_numpy(dtype=np.float64)
        if not (np.isfinite(permanent).all() and np.isfinite(spurious).all()):
            raise ValueError("QA exclusion comparison requires complete flag coverage")
        affected_nonmonotonic_flagged_g += float(np.sum(g[nonmonotonic & ((permanent > 0) | (spurious > 0))]))
        worst_position = np.unravel_index(np.argmin(adjacent_changes), adjacent_changes.shape)
        worst_drop = float(max(0.0, -adjacent_changes[worst_position]))
        if worst_drop_reference is None or worst_drop > worst_drop_reference["drop_m"]:
            cell, pair = worst_position
            worst_drop_reference = {
                **ident, "grid_row": int(d.grid_row.iloc[cell]), "grid_column": int(d.grid_column.iloc[cell]),
                "center_x_mollweide_m": float(d.center_x_mollweide_m.iloc[cell]),
                "center_y_mollweide_m": float(d.center_y_mollweide_m.iloc[cell]),
                "lower_RP": int(RPS[pair]), "higher_RP": int(RPS[pair + 1]), "drop_m": worst_drop,
                "added_surface_m2": float(g[cell]), "endpoint_support_fraction": float(s[cell]),
                "preexisting_detected_fraction": float(p[cell]), "permanent_water_QA_fraction": float(permanent[cell]),
                "spurious_depth_QA_fraction": float(spurious[cell]),
                "RP_depths_m": {f"RP{int(r)}": float(rp_depth[cell, j]) for j, r in enumerate(RPS)},
                "purpose": "Trace the largest supplied-layer decrease; one diagnostic record, not independent reference evidence.",
            }
        qa_keep.update({"exclude_any_permanent_water_QA": permanent <= 0,
                        "exclude_any_spurious_depth_QA": spurious <= 0,
                        "exclude_either_QA": (permanent <= 0) & (spurious <= 0)})
        for setting, keep in qa_keep.items():
            for scenario, w in original_weights.items():
                qa_rows.append({**ident, "scenario": scenario, "setting": setting,
                                "retained_record_count": int(keep.sum()),
                                "retained_positive_GHSL_change_m2": float(np.sum(g[keep])),
                                "retained_positive_GHSL_fraction": float(np.sum(g[keep]) / total),
                                **record(w * keep, h, total)})
        # No implicit correction of the parent layers. A cumulative maximum is
        # a separately labelled upward monotonicization stress calculation.
        rp_cummax = np.maximum.accumulate(rp_depth, axis=1)
        h_cummax = np.sum(0.5 * (rp_cummax[:, :-1] + rp_cummax[:, 1:]) * segment_width, axis=1) / (ap[0] - ap[-1])
        for j in range(len(RPS) - 1):
            affected = adjacent_changes[:, j] < -1e-6
            drops = -adjacent_changes[affected, j]
            monotonic_pair_rows.append({**ident, "lower_RP": int(RPS[j]), "higher_RP": int(RPS[j + 1]),
                                       "decreasing_record_count": int(affected.sum()),
                                       "decreasing_GHSL_change_m2": float(np.sum(g[affected])),
                                       "max_drop_m": float(drops.max()) if len(drops) else 0.0,
                                       "sum_drop_m": float(drops.sum()) if len(drops) else 0.0})
        for scenario, w in original_weights.items():
            base_depth = record(w, h, total)["depth_m"]
            altered_depth = record(w, h_cummax, total)["depth_m"]
            monotonic_rows.append({**ident, "scenario": scenario,
                                   "nonmonotonic_record_count": int(nonmonotonic.sum()),
                                   "nonmonotonic_GHSL_change_m2": float(np.sum(g[nonmonotonic])),
                                   "nonmonotonic_GHSL_weighted_fraction": float(np.sum(g[nonmonotonic]) / total),
                                   "nonmonotonic_scenario_weight_fraction": float(np.sum(w[nonmonotonic]) / w.sum()) if w.sum() else np.nan,
                                   "denominator_m2": float(w.sum()),
                                   "original_depth_m": base_depth,
                                   "cummax_sensitivity_depth_m": altered_depth,
                                   "cummax_minus_original_depth_m": altered_depth - base_depth,
                                   "max_adjacent_drop_m": float(max(0.0, -adjacent_changes.min()))})
        for a in EXPONENTS:
            for b in EXPONENTS:
                setting = f"alpha_{a:g}_beta_{b:g}"
                w = g * np.power(s, a) * np.power(retention, b)
                weight_rows.append({**ident, "family": "exponent", "setting": setting, "alpha": a, "beta": b, "threshold": np.nan, **record(w, h, total)})
        for threshold in THRESHOLDS:
            w = g * (s >= threshold) * retention
            weight_rows.append({**ident, "family": "binary_endpoint", "setting": f"endpoint_threshold_{threshold:g}", "alpha": np.nan, "beta": 1.0, "threshold": threshold, **record(w, h, total)})

        base_w, full_u_w = g * s * retention, g * np.minimum(s + u, 1) * retention
        endpoint_base_w, endpoint_full_w = g * s, g * np.minimum(s + u, 1)
        bound_min, bound_max = ratio_bounds(base_w, full_u_w, h)
        endpoint_min, endpoint_max = ratio_bounds(endpoint_base_w, endpoint_full_w, h)
        coding_rows.append({
            **ident, "positive_GHSL_change_m2": total,
            "undocumented_GHSL_weighted_m2": float(np.sum(g * u)),
            "undocumented_GHSL_weighted_fraction": float(np.sum(g * u) / total),
            "joint_u_denominator_increment_upper_m2": float(np.sum(full_u_w - base_w)),
            "joint_u_relative_increment_to_base_denominator": float(np.sum(full_u_w - base_w) / base_w.sum()) if base_w.sum() else np.nan,
            "joint_no_undocumented_support_depth_m": record(base_w, h, total)["depth_m"],
            "joint_all_undocumented_supported_depth_m": record(full_u_w, h, total)["depth_m"],
            "joint_possible_assignment_min_depth_m": bound_min,
            "joint_possible_assignment_max_depth_m": bound_max,
            "endpoint_possible_assignment_min_depth_m": endpoint_min,
            "endpoint_possible_assignment_max_depth_m": endpoint_max,
        })

        # Excluding unresolved source portions leaves only historic detections.
        # Applying a screen that removes those detections then leaves no weight.
        # No invalid product of mutually exclusive fractional partitions is used.
        history_rows.append({
            **ident, "unresolved_GHSL_weighted_fraction": float(np.sum(g * unresolved) / total),
            "fully_resolved_cell_count": int(np.sum(unresolved == 0)),
            "fully_resolved_GHSL_change_m2": float(np.sum(g[unresolved == 0])),
            "ghsl_no_screen_depth_m": record(g, h, total)["depth_m"],
            "ghsl_screen_depth_m": record(g * retention, h, total)["depth_m"],
            "ghsl_screen_retained_fraction": float(np.sum(g * retention) / total),
            "endpoint_no_screen_depth_m": record(g * s, h, total)["depth_m"],
            "endpoint_screen_depth_m": record(g * s * retention, h, total)["depth_m"],
            "endpoint_screen_retained_fraction": float(np.sum(g * s * retention) / total),
            "renaming_zero_without_changing_weights_depth_delta_m": 0.0,
            "exclude_unresolved_then_remove_detected_denominator_m2": 0.0,
            "exclude_unresolved_then_remove_detected_depth_m": np.nan,
        })

        hazards = {"normalized_exceedance_trapezoid": h, "uniform_seven_RP_mean": rp_depth.mean(axis=1)}
        hazards.update({f"RP{int(r)}": rp_depth[:, j] for j, r in enumerate(RPS)})
        for scenario, w in original_weights.items():
            for metric, depth in hazards.items():
                hazard_rows.append({**ident, "scenario": scenario, "hazard_metric": metric, **record(w, depth, total)})

        # Endpoint and historical fractions are marginals. Their product is a
        # specified arithmetic weight, not an identified subcell intersection.
        lower_fraction = np.maximum(0, s - p)
        upper_fraction = np.minimum(s, retention)
        product = s * retention
        violations = (product < lower_fraction - 1e-7) | (product > upper_fraction + 1e-7)
        product_bound_violations += int(violations.sum())
        lower_w, upper_w = g * lower_fraction, g * upper_fraction
        overlap_min, overlap_max = ratio_bounds(lower_w, upper_w, h)
        frechet_rows.append({
            **ident,
            "product_bound_violation_cells_tolerance_1e_7": int(violations.sum()),
            "positive_GHSL_change_m2": total,
            "product_denominator_m2": float(base_w.sum()),
            "lower_denominator_m2": float(lower_w.sum()),
            "upper_denominator_m2": float(upper_w.sum()),
            "lower_denominator_fraction": float(lower_w.sum() / total),
            "upper_denominator_fraction": float(upper_w.sum() / total),
            "product_depth_m": record(base_w, h, total)["depth_m"],
            "all_cell_lower_endpoint_scenario_depth_m": record(lower_w, h, total)["depth_m"],
            "all_cell_upper_endpoint_scenario_depth_m": record(upper_w, h, total)["depth_m"],
            "feasible_intersection_min_depth_m": overlap_min,
            "feasible_intersection_max_depth_m": overlap_max,
            "feasible_intersection_depth_width_m": overlap_max - overlap_min,
            "zero_denominator_feasible": bool(lower_w.sum() == 0),
            "no_positive_denominator_feasible": bool(upper_w.sum() == 0),
            "marginal_intersection_identified": bool(np.allclose(lower_fraction, upper_fraction, rtol=0, atol=1e-10)),
        })
        log["per_city"].append({"unit_key": key, "records": len(d), "seconds": time.perf_counter() - city_start})

    originals = pd.DataFrame(original_rows)
    weights = pd.DataFrame(weight_rows)
    coding = pd.DataFrame(coding_rows)
    history = pd.DataFrame(history_rows)
    hazard = pd.DataFrame(hazard_rows)
    frechet = pd.DataFrame(frechet_rows)
    qa = pd.DataFrame(qa_rows)
    monotonic = pd.DataFrame(monotonic_rows)
    monotonic_pairs = pd.DataFrame(monotonic_pair_rows)
    baseline = originals.loc[originals.scenario.eq(JOINT)]
    validation_pair = originals.merge(
        published.loc[published.glofas_resampling.eq("nearest")], on=["unit_key", "eFUA_name", "scenario"], validate="one_to_one"
    )
    validation = {
        "city_count": len(files), "positive_change_record_count": total_cells,
        "total_positive_GHSL_change_m2": total_g, "total_positive_GHSL_change_km2": total_g / 1e6,
        "complete_seven_RP_records": complete_hazard_cells,
        "max_cell_stored_vs_recomputed_integral_abs_error_m": h_reconstruction_max_error,
        "max_historic_detected_plus_unresolved_partition_error": partition_max_error,
        "max_city_original_four_scenario_depth_abs_error_m": float(np.max(np.abs(validation_pair.depth_m - validation_pair.integrated_modelled_depth_m))),
        "max_city_original_four_scenario_denominator_abs_error_m2": float(np.max(np.abs(validation_pair.denominator_m2 - validation_pair.scenario_weight_m2))),
        "cell_RP_monotonicity_violations_tolerance_1e_6_m": monotonic_depth_violations,
        "four_scenario_median_depth_m": originals.groupby("scenario").depth_m.median().to_dict(),
        "validation_interpretation": "Numerical reconstruction only. Reusing the same parent products is not independent settlement or flood accuracy validation.",
    }
    if validation["max_city_original_four_scenario_depth_abs_error_m"] > 1e-6:
        raise AssertionError("Reconstructed city depths differ beyond float32-storage tolerance")
    validation["reconstruction_passed"] = True
    weight_summary = []
    for setting, frame in weights.groupby("setting", sort=True):
        first = frame.iloc[0]
        weight_summary.append({"family": first.family, "setting": setting, "alpha": first.alpha, "beta": first.beta, "threshold": first.threshold,
                               "total_denominator_km2": float(frame.denominator_m2.sum() / 1e6),
                               "median_retained_fraction": float(frame.retained_added_surface_fraction.median()),
                               "median_depth_m": float(frame.depth_m.median()), **rank_statistics(frame, baseline)})
    weight_summary = pd.DataFrame(weight_summary)
    hazard_summary = []
    for (scenario, metric), frame in hazard.groupby(["scenario", "hazard_metric"], sort=True):
        metric_base = hazard.loc[hazard.scenario.eq(scenario) & hazard.hazard_metric.eq("normalized_exceedance_trapezoid")]
        stats = rank_statistics(frame, metric_base)
        merged = frame[["unit_key", "eFUA_name", "depth_m"]].merge(metric_base[["unit_key", "depth_m"]], on="unit_key", suffixes=("", "_base"))
        merged["absolute_delta_m"] = (merged.depth_m - merged.depth_m_base).abs()
        extreme = merged.sort_values(["absolute_delta_m", "unit_key"], ascending=[False, True]).iloc[0]
        hazard_summary.append({"scenario": scenario, "hazard_metric": metric, "median_depth_m": float(frame.depth_m.median()),
                               **stats, "max_delta_city": extreme.eFUA_name, "max_delta_unit_key": extreme.unit_key})
    hazard_summary = pd.DataFrame(hazard_summary)
    qa_summary = []
    for (scenario, setting), frame in qa.groupby(["scenario", "setting"], sort=True):
        scenario_baseline = originals.loc[originals.scenario.eq(scenario)]
        qa_summary.append({"scenario": scenario, "setting": setting,
                           "total_denominator_km2": float(frame.denominator_m2.sum() / 1e6),
                           "median_depth_m": float(frame.depth_m.median()),
                           "retained_positive_GHSL_km2": float(frame.retained_positive_GHSL_change_m2.sum() / 1e6),
                           "retained_positive_GHSL_fraction": float(frame.retained_positive_GHSL_change_m2.sum() / total_g),
                           **rank_statistics(frame, scenario_baseline)})
    qa_summary = pd.DataFrame(qa_summary)
    pair_summary = monotonic_pairs.groupby(["lower_RP", "higher_RP"], as_index=False).agg(
        decreasing_record_count=("decreasing_record_count", "sum"),
        decreasing_GHSL_change_m2=("decreasing_GHSL_change_m2", "sum"),
        max_drop_m=("max_drop_m", "max"), sum_drop_m=("sum_drop_m", "sum"))
    pair_summary["mean_drop_among_decreasing_records_m"] = np.where(pair_summary.decreasing_record_count > 0,
        pair_summary.sum_drop_m / pair_summary.decreasing_record_count, 0.0)
    monotonic_summary = {
        "decreasing_cell_count": monotonic_depth_violations,
        "decreasing_cell_fraction": monotonic_depth_violations / total_cells,
        "decreasing_GHSL_change_m2": affected_nonmonotonic_g,
        "decreasing_GHSL_weighted_fraction": affected_nonmonotonic_g / total_g,
        "decreasing_GHSL_fraction_with_either_QA_flag": affected_nonmonotonic_flagged_g / affected_nonmonotonic_g if affected_nonmonotonic_g else 0.0,
        "max_adjacent_drop_m": float(pair_summary.max_drop_m.max()),
        "largest_drop_diagnostic_record": worst_drop_reference,
        "adjacent_RP_pairs": pair_summary.to_dict(orient="records"),
        "cummax_city_shift_by_scenario": {
            scenario: {"median_shift_m": float(frame.cummax_minus_original_depth_m.median()),
                       "max_shift_m": float(frame.cummax_minus_original_depth_m.max()),
                       "max_shift_city": str(frame.loc[frame.cummax_minus_original_depth_m.idxmax(), "eFUA_name"])}
            for scenario, frame in monotonic.groupby("scenario")},
        "interpretation": "Parent-layer depth decreases are disclosed without silent modification. Cumulative maximum is a numeric sensitivity, not a validated correction or an annual depth quantile model.",
    }
    alignment_summary = []
    for scenario in SCENARIOS:
        near = published.loc[published.scenario.eq(scenario) & published.glofas_resampling.eq("nearest")].rename(columns={"integrated_modelled_depth_m": "depth_m"})
        average = published.loc[published.scenario.eq(scenario) & published.glofas_resampling.eq("average")].rename(columns={"integrated_modelled_depth_m": "depth_m"})
        alignment_summary.append({"scenario": scenario, **rank_statistics(average, near),
                                  "data_available": "published city-level average summary; cell-level alternate-average analyses cannot be reconstructed from nearest-only cell tables"})
    alignment_summary = pd.DataFrame(alignment_summary)
    cases = hazard.loc[hazard.unit_key.isin(case_keys)].copy()
    cases["selection_reason"] = cases.eFUA_name.map({k: v for k, v in log["application_selection_before_depth_computation"].items() if k not in ("purpose", "unit_keys")})
    frechet_summary = {
        "product_bound_violation_cells_tolerance_1e_7": product_bound_violations,
        "zero_denominator_feasible_city_count": int(frechet.zero_denominator_feasible.sum()),
        "no_positive_denominator_feasible_city_count": int(frechet.no_positive_denominator_feasible.sum()),
        "identified_intersection_city_count": int(frechet.marginal_intersection_identified.sum()),
        "collapsed_depth_compatibility_interval_city_count_tolerance_1e_10_m": int((frechet.feasible_intersection_depth_width_m.abs() < 1e-10).sum()),
        "depth_width_at_least_0_05_m_city_count": int((frechet.feasible_intersection_depth_width_m >= 0.05).sum()),
        "depth_width_median_m": float(frechet.feasible_intersection_depth_width_m.median()),
        "depth_width_q25_m": float(frechet.feasible_intersection_depth_width_m.quantile(.25)),
        "depth_width_q75_m": float(frechet.feasible_intersection_depth_width_m.quantile(.75)),
        "depth_width_max_m": float(frechet.feasible_intersection_depth_width_m.max()),
        "depth_width_max_city": str(frechet.loc[frechet.feasible_intersection_depth_width_m.idxmax(), "eFUA_name"]),
        "total_product_denominator_km2": float(frechet.product_denominator_m2.sum() / 1e6),
        "total_lower_denominator_km2": float(frechet.lower_denominator_m2.sum() / 1e6),
        "total_upper_denominator_km2": float(frechet.upper_denominator_m2.sum() / 1e6),
        "lower_endpoint_scenario_rank_diagnostics_vs_product": rank_statistics(frechet.rename(columns={"all_cell_lower_endpoint_scenario_depth_m": "depth_m"}), baseline),
        "upper_endpoint_scenario_rank_diagnostics_vs_product": rank_statistics(frechet.rename(columns={"all_cell_upper_endpoint_scenario_depth_m": "depth_m"}), baseline),
        "interpretation": "Marginal compatibility bounds, conditional on the retained source fractions; not confidence intervals, error models, or validation. gL and gU city depths are endpoint scenarios, not ratio extrema. The product is an arithmetic convention, not an identified spatial intersection.",
    }
    coding["joint_possible_assignment_width_m"] = coding.joint_possible_assignment_max_depth_m - coding.joint_possible_assignment_min_depth_m
    coding["joint_all_supported_delta_m"] = coding.joint_all_undocumented_supported_depth_m - coding.joint_no_undocumented_support_depth_m
    history["ghsl_screen_delta_m"] = history.ghsl_screen_depth_m - history.ghsl_no_screen_depth_m
    history["endpoint_screen_delta_m"] = history.endpoint_screen_depth_m - history.endpoint_no_screen_depth_m
    frames = {
        "revision_original_city.csv": originals,
        "revision_weight_city.csv": weights,
        "revision_weight_summary.csv": weight_summary,
        "revision_coding_bounds_city.csv": coding,
        "revision_history_city.csv": history,
        "revision_hazard_city.csv": hazard,
        "revision_hazard_summary.csv": hazard_summary,
        "revision_alignment_summary.csv": alignment_summary,
        "revision_application_cities.csv": cases,
        "revision_frechet_city.csv": frechet,
        "revision_qa_threshold_city.csv": qa,
        "revision_qa_threshold_summary.csv": qa_summary,
        "revision_monotonicity_city.csv": monotonic,
        "revision_monotonicity_pairs.csv": monotonic_pairs,
    }
    for filename, frame in frames.items():
        write_csv(frame, output / filename)
    (output / "revision_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (output / "revision_frechet_summary.json").write_text(json.dumps(frechet_summary, indent=2), encoding="utf-8")
    (output / "revision_monotonicity_summary.json").write_text(json.dumps(monotonic_summary, indent=2), encoding="utf-8")
    log.update({"finished_at_Asia_Shanghai": stamp(), "elapsed_seconds": time.perf_counter() - start,
                "input_parquet_bytes": sum(f.stat().st_size for f in files),
                "output_files": list(frames) + ["revision_validation.json", "revision_frechet_summary.json", "revision_monotonicity_summary.json", "revision_run_log.json", "SENSITIVITY_REPORT.md"],
                "all_outputs_created": False,
                "ratio_optimization_checks": "Three analytical cases passed, including all-zero denominator."})
    (output / "revision_run_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")

    exponent = weight_summary.loc[weight_summary.family.eq("exponent") & ~weight_summary.setting.eq("alpha_1_beta_1")]
    binary = weight_summary.loc[weight_summary.family.eq("binary_endpoint")]
    max_u = coding.loc[coding.undocumented_GHSL_weighted_fraction.idxmax()]
    max_u_depth = coding.loc[coding.joint_possible_assignment_width_m.idxmax()]
    report = [
        "# Deterministic sensitivity analysis for the IUFEE revision", "",
        f"Executed {log['finished_at_Asia_Shanghai']} in {log['elapsed_seconds']:.3f} s. Inputs were read only; output is on D:. No downloads or large-scale training were performed.", "",
        "## Scope and reconstruction", "",
        f"Reconstructed {total_cells:,} positive-change records in 91 FUAs, totaling {total_g / 1e6:.6f} km² of positive GHSL product difference. All seven return-period values were finite. Largest reconstructed versus published city depth difference: {validation['max_city_original_four_scenario_depth_abs_error_m']:.3g} m; largest denominator difference: {validation['max_city_original_four_scenario_denominator_abs_error_m2']:.3g} m² (float32 storage/arithmetic).",
        "The four original scenario medians reproduce to six decimals: " + "; ".join(f"{k}: {v:.6f} m" for k, v in validation["four_scenario_median_depth_m"].items()) + ".", "",
        "## Weighting conventions and binary endpoint decisions", "",
        "Generalized weights are g·s^α·(1−p)^β for α,β∈{0,0.5,1,2}. Exponent zero means the corresponding evidence factor is omitted, including at a zero source fraction; (0,0), (1,0), (0,1), and (1,1) recover the four stated scenarios. Every denominator is reported as an arithmetic weight mass, not physically observed construction area. Binary alternatives are g·I(s≥τ)·(1−p), τ∈{0.25,0.50,0.75}; only endpoint support is thresholded.",
        f"Across the 15 nonbaseline exponent settings, Spearman correlations with joint weights range {exponent.spearman_vs_baseline.min():.6f}–{exponent.spearman_vs_baseline.max():.6f}; median absolute city-depth changes range {exponent.median_absolute_delta_m.min():.6f}–{exponent.median_absolute_delta_m.max():.6f} m; top-ten overlaps range {int(exponent.top10_overlap_count.min())}–{int(exponent.top10_overlap_count.max())}/10.", "",
        markdown_table(binary[["setting", "total_denominator_km2", "median_depth_m", "spearman_vs_baseline", "median_absolute_delta_m", "max_absolute_delta_m", "top10_overlap_count"]]), "",
        "## Undocumented WSF2019 code", "",
        f"The positive-GHSL weighted undocumented fraction is {total_u / total_g:.12g}, equivalent to {total_u:.6f} m² of arithmetic GHSL weight. The largest city fraction is {max_u.undocumented_GHSL_weighted_fraction:.12g} in {max_u.eFUA_name}.",
        "Changing s to s+u is an extreme coding scenario in which all undocumented portions supply endpoint support. Treating those portions as nonsettlement or retaining them as unassigned supplies no positive support and gives the same s, without making the same semantic claim. Exact ratio bounds allow any additional cell support between 0 and u; these are conditional assignment bounds, not settlement accuracy bounds.",
        f"The maximum city joint-depth assignment width is {max_u_depth.joint_possible_assignment_width_m:.12g} m in {max_u_depth.eFUA_name}; the maximum absolute all-supported versus unassigned change is {coding.joint_all_supported_delta_m.abs().max():.12g} m.", "",
        "## WSF Evolution zero semantics", "",
        "Renaming the unresolved complement as nonsettlement while retaining the same numeric weights produces exactly zero numeric change; it would add an unsupported semantic assertion. Excluding unresolved source portions leaves only positive historic detections, which the preperiod screen then removes. That interpretation has zero retained weight and no defined screened depth in all 91 FUAs. Multiplying aggregated mutually exclusive fractions to manufacture retained overlap would be invalid.",
        f"For the meaningful no-screen versus screen calculation, the median signed change is {history.ghsl_screen_delta_m.median():.6f} m with GHSL weights and {history.endpoint_screen_delta_m.median():.6f} m with endpoint weights. The maximum absolute changes are {history.ghsl_screen_delta_m.abs().max():.6f} and {history.endpoint_screen_delta_m.abs().max():.6f} m, respectively. These compare arithmetic evidence choices; they do not establish the history of retained cells.", "",
        "## Hazard summary choices", "",
        "The published normalized trapezoid integrates over annual exceedance probability 0.002–0.1 and divides by that interval width. It omits the tail beyond RP500 and the range below RP10, and is not an annual expected depth. The uniform mean gives seven return-period layers equal weight, while RP100 and RP500 are single-layer stress cases; they answer different hazard-summary questions.", "",
        markdown_table(hazard_summary.loc[hazard_summary.scenario.eq(JOINT) & hazard_summary.hazard_metric.isin(["normalized_exceedance_trapezoid", "uniform_seven_RP_mean", "RP100", "RP500"]), ["hazard_metric", "median_depth_m", "spearman_vs_baseline", "median_absolute_delta_m", "max_absolute_delta_m", "top10_overlap_count", "max_delta_city"]]), "",
        "## Marginal support and Fréchet compatibility", "",
        "The retained cell fractions s and p are marginal endpoint and historic support. Their product s(1−p) is a declared weighting convention. It does not identify the subcell intersection of endpoint support and absence of positive historic detection. Without a joint footprint, its feasible intersection fraction t lies in [max(0,s−p), min(s,1−p)]. The product lies inside this interval for every cell within 1e−7 storage tolerance.",
        f"Total arithmetic denominators under the lower endpoint, product, and upper endpoint weights are {frechet_summary['total_lower_denominator_km2']:.6f}, {frechet_summary['total_product_denominator_km2']:.6f}, and {frechet_summary['total_upper_denominator_km2']:.6f} km². The true fractional-ratio compatibility widths have median {frechet_summary['depth_width_median_m']:.6f} m, IQR {frechet_summary['depth_width_q25_m']:.6f}–{frechet_summary['depth_width_q75_m']:.6f} m, and maximum {frechet_summary['depth_width_max_m']:.6f} m in {frechet_summary['depth_width_max_city']}. {frechet_summary['zero_denominator_feasible_city_count']} cities admit a zero denominator; {frechet_summary['no_positive_denominator_feasible_city_count']} cities admit no positive denominator. {frechet_summary['identified_intersection_city_count']} cities have fully identified intersection weights from the stored marginals.",
        "The gL and gU depth estimates are two endpoint scenarios. They are not generally the minimum and maximum weighted depths. Exact city-depth extrema were calculated separately by solving the box-constrained linear-fractional problem with Dinkelbach residual bisection. These are conditional compatibility bounds, not error-adjusted estimates or confidence intervals.", "",
        f"The depth interval collapses within 1e−10 m in {frechet_summary['collapsed_depth_compatibility_interval_city_count_tolerance_1e_10_m']} cities even though their intersection weights remain unidentified. It is at least 0.05 m wide in {frechet_summary['depth_width_at_least_0_05_m_city_count']} cities. The lower and upper endpoint scenarios have rank correlations {frechet_summary['lower_endpoint_scenario_rank_diagnostics_vs_product']['spearman_vs_baseline']:.6f} and {frechet_summary['upper_endpoint_scenario_rank_diagnostics_vs_product']['spearman_vs_baseline']:.6f} with the product; those rank correlations do not contract the full compatibility interval.", "",
        "## Alignment and fixed application examples", "",
        f"Published average versus nearest city-summary Spearman correlations range {alignment_summary.spearman_vs_baseline.min():.6f}–{alignment_summary.spearman_vs_baseline.max():.6f}. Alternate weights cannot be recomputed with average alignment because the released cell tables contain nearest depths only.",
        "Guwahati and Sultanpur were retained to interpret previously reported opposite extremes; the third example is Delhi [New Delhi], selected before depth computation as the largest-population roster unit. The application table reports all seven RP layers, the uniform mean, the normalized trapezoid, and all four scenarios for each city. The examples are not an external or representative validation sample.", "",
        "## Positive-change cutoffs and GloFAS QA flags", "",
        "Product-difference cutoffs retain only cells with g strictly greater than 0, 10, 50, 100, or 500 m². QA exclusions discard an entire 100 m cell when any registered source support is flagged as permanent water, spurious depth, or either; all QA fields are finite in the release. These conservative whole-cell exclusions are declared stress scenarios, not assertions that flagged fractions or excluded GHSL differences are erroneous.", "",
        markdown_table(qa_summary.loc[qa_summary.scenario.eq(JOINT), ["setting", "retained_positive_GHSL_fraction", "total_denominator_km2", "median_depth_m", "spearman_vs_baseline", "median_absolute_delta_m", "max_absolute_delta_m", "top10_overlap_count"]]), "",
        "## Return-period depth decreases and labelled monotonicization", "",
        f"There are {monotonic_depth_violations:,} cells ({100 * monotonic_depth_violations / total_cells:.6f}%) with at least one adjacent return-period depth decrease exceeding 1e−6 m; their GHSL weight is {100 * affected_nonmonotonic_g / total_g:.6f}% of total positive change. Maximum adjacent depth decrease is {monotonic_summary['max_adjacent_drop_m']:.6f} m.", "",
        f"Among affected GHSL weights, {100 * monotonic_summary['decreasing_GHSL_fraction_with_either_QA_flag']:.6f}% intersect a positive permanent-water or spurious-depth QA flag. The largest drop occurs in {worst_drop_reference['eFUA_name']} from RP{worst_drop_reference['lower_RP']} to RP{worst_drop_reference['higher_RP']}; its spurious-depth QA fraction is {worst_drop_reference['spurious_depth_QA_fraction']:g}. The diagnostic record and all its supplied RP depths are retained in revision_monotonicity_summary.json.", "",
        markdown_table(pair_summary[["lower_RP", "higher_RP", "decreasing_record_count", "decreasing_GHSL_change_m2", "max_drop_m", "mean_drop_among_decreasing_records_m"]]), "",
        "The supplied seven-layer representation is therefore not everywhere a monotone depth quantile sequence. The primary calculation preserves supplied values. A separately labelled upward cumulative maximum over return periods measures numeric sensitivity; it does not establish that this is a scientifically correct repair.",
        "; ".join(f"{scenario}: median shift {v['median_shift_m']:.9g} m, maximum {v['max_shift_m']:.9g} m ({v['max_shift_city']})" for scenario, v in monotonic_summary["cummax_city_shift_by_scenario"].items()) + ".", "",
        "## Algorithm verification with explicitly synthetic cases", "",
        f"The ratio-bound routine was compared against exhaustive enumeration of all positive-denominator box vertices in {log['ratio_vertex_enumeration_verification']['synthetic_cases']} synthetic cases (one to six cells; {log['ratio_vertex_enumeration_verification']['box_vertices_examined']} vertices; random seed 20261005). Maximum absolute difference in extrema is {log['ratio_vertex_enumeration_verification']['max_abs_extreme_error']:.3g}. Three additional analytical corner cases passed. These synthetic values verify only the numerical optimizer and provide no empirical evidence about settlement or flood accuracy.", "",
        "## Manuscript-ready evidence boundary", "",
        "The added analyses assess how deterministic arithmetic weights, source-state coding choices, hazard-summary definitions, and marginal overlap assumptions affect linked city measures. They neither validate the settlement products independently nor estimate the accuracy of GloFAS depths. Numerical reproduction and stability under selected alternatives support auditability within the stated data representation. A valid spatial intersection requires a joint footprint; a physically verified change label and flood accuracy claim require independent references that are absent from this analysis.", "",
        "See revision_run_log.json for the actual run and prespecified case-selection record; revision_validation.json for reconstruction checks; the revision_*.csv tables retain all city denominators, depth values, and ranking diagnostics.",
    ]
    (output / "SENSITIVITY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    log["all_outputs_created"] = all((output / filename).exists() for filename in log["output_files"])
    log["elapsed_seconds"] = time.perf_counter() - start
    log["finished_at_Asia_Shanghai"] = stamp()
    (output / "revision_run_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps({"completed": True, "runtime_s": log["elapsed_seconds"], "validation": validation,
                      "undocumented_fraction": total_u / total_g, "frechet": frechet_summary,
                      "monotonicity": monotonic_summary, "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
