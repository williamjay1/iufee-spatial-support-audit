"""Map-specific joint-location overlay and matched marginal-product baseline.

Both WSF sources are registered by nearest neighbour to 10 m Mollweide pixels
strictly nested in the GHSL 100 m grid. No real-construction truth is inferred.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import stat
import shutil
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import requests
from affine import Affine
from rasterio.enums import Resampling
from rasterio.transform import array_bounds
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, from_bounds

WORK = Path(r"D:\MLWork\IUFEE_revision_20261005")
RAW = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\raw\wsf_evidence")
GHSL = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\ghsl_built_s_100m\study_units")
ROSTER = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\roster\study_unit_roster.csv")
AUDIT = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\iufee_v1\source_plan\wsf_source_semantic_audit.csv")
CELLS = Path(r"D:\codex\sci\remote_sensing_sci_novelty_audit\guangzhou_india_flood_exposure_study\grsl_submission_2026\zenodo_release\IUFEE_v1_2\data\database_v1_2\expansion_cells_100m")
MISSING = -9999
VERSION = "joint_overlay_10m_nearest_lexicographic_first_valid_v3_fresh_identity"
ROW_BLOCK = 32
HASH_CACHE = {}
STAT_CACHE = {}


def source_stat(path):
    info = Path(path).stat()
    return dict(bytes=info.st_size, mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as src:
        for data in iter(lambda: src.read(1048576), b""):
            h.update(data)
    return h.hexdigest().upper()


def catalog_sources():
    audit = pd.read_csv(AUDIT).set_index("item_id")
    override_file = WORK / "results" / "joint_overlay_source_overrides.json"
    overrides = json.loads(override_file.read_text(encoding="utf-8")) if override_file.exists() else {}
    result = {}
    for collection in ["WSF_2019", "WSF_Evolution"]:
        rows = []
        for path in sorted((RAW / collection).glob("*.tif")):
            original = path
            recovery = overrides.get(path.stem)
            if recovery:
                path = Path(recovery["recovered_path"])
            with rasterio.open(path) as src:
                rows.append(dict(path=str(path), original_source_path=str(original), recovery_record=recovery,
                                 item_id=original.stem, bounds=list(src.bounds),
                                 crs=str(src.crs), shape=list(src.shape), nodata=src.nodata,
                                 dtype=src.dtypes[0], transform=list(src.transform),
                                 prior_source_sha256=audit.loc[original.stem, "source_sha256"]))
        result[collection] = rows
    return result


def recover_sources():
    """Recover byte-identical audited sources to new immutable F: filenames."""
    failures_path = WORK / "results" / "joint_overlay_failures_pre_source_recovery_20261005.json"
    failures = json.loads(failures_path.read_text(encoding="utf-8"))
    source_paths = {x["error"].split("Source identity differs from prior audit: ",1)[1] for x in failures if x["error"].startswith("Source identity differs from prior audit: ")}
    final_identity_failure = WORK / "results" / "joint_overlay_verification_failed_identity_pre_additional_recovery_20261005.json"
    if final_identity_failure.exists():
        failed_audit = json.loads(final_identity_failure.read_text(encoding="utf-8"))
        source_paths.update(x["path"] for x in failed_audit["source_identity_stability_checks"] if not x["sha256_matches_recorded_and_old_audit"])
    source_paths = sorted(source_paths)
    assets = pd.read_csv(AUDIT.parent / "wsf_asset_plan.csv").set_index("item_id")
    audit = pd.read_csv(AUDIT).set_index("item_id")
    recovery_dir = Path(r"F:\AcademicData\IUFEE_revision_20261005\raw\WSF_source_recovery_20261005")
    recovery_dir.mkdir(parents=True,exist_ok=True)
    override_file = WORK / "results" / "joint_overlay_source_overrides.json"
    overrides = json.loads(override_file.read_text(encoding="utf-8")) if override_file.exists() else {}
    recovery_audit = list(overrides.values())
    estimated_bytes = sum(Path(p).stat().st_size for p in source_paths)
    spaces = {drive: shutil.disk_usage(drive).free for drive in ["F:\\","E:\\"]}
    if spaces["F:\\"] < estimated_bytes*2:
        raise RuntimeError("F: lacks space for immutable WSF source recovery")
    print(f"SOURCE_RECOVERY estimated_bytes={estimated_bytes} free_F={spaces['F:'+chr(92)]} path={recovery_dir}",flush=True)
    for original_path in source_paths:
        original = Path(original_path)
        item = original.stem
        expected = audit.loc[item,"source_sha256"].upper()
        if item in overrides and sha256(overrides[item]["recovered_path"]) == expected:
            continue
        url = assets.loc[item,"remote_href"]
        path = recovery_dir / f"{item}_refetch_20261005_{time.time_ns()}.tif"
        print(f"SOURCE_FETCH {item} {url}",flush=True)
        with requests.get(url,stream=True,timeout=90) as response:
            response.raise_for_status()
            headers = {k:response.headers.get(k) for k in ["etag","last-modified","content-length","content-type"]}
            with open(path,"xb") as stream:
                for data in response.iter_content(1048576):
                    stream.write(data)
        os.chmod(path,stat.S_IREAD)
        actual = sha256(path)
        record = dict(item_id=item, original_source_path=str(original), original_current_sha256=sha256(original),
                      old_audit_sha256=expected, recovered_path=str(path), recovered_sha256=actual,
                      recovered_sha256_matches_old_audit=actual == expected, recovered_bytes=path.stat().st_size,
                      source_url=url, http_headers=headers, retrieved_utc=datetime.now(timezone.utc).isoformat(),
                      collection_license=assets.loc[item,"collection_license"], original_preserved=True,
                      recovered_file_readonly=True)
        recovery_audit.append(record)
        audit_output = dict(space_check_free_bytes=spaces,estimated_download_bytes=estimated_bytes,records=recovery_audit)
        (WORK / "results" / "joint_overlay_source_recovery_audit.json").write_text(json.dumps(audit_output,indent=2),encoding="utf-8")
        if actual != expected:
            raise RuntimeError(f"Recovered source differs from old audit; retained but not used: {item}")
        overrides[item] = record
        override_file.write_text(json.dumps(overrides,indent=2),encoding="utf-8")
        print(f"SOURCE_RECOVERED {item} checksum_match=True bytes={path.stat().st_size}",flush=True)


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def source_identity(record):
    path = record["path"]
    if path not in HASH_CACHE:
        before = source_stat(path)
        actual = sha256(path)
        after = source_stat(path)
        if before != after:
            raise RuntimeError(f"Source stat changed while hashing: {path}")
        if actual != record["prior_source_sha256"].upper():
            raise RuntimeError(f"Source identity differs from prior audit: {path}")
        HASH_CACHE[path] = actual
        STAT_CACHE[path] = after
    return {**record, "source_sha256": HASH_CACHE[path], "sha256_matches_prior_audit": True,
            "source_stat_at_initial_hash": STAT_CACHE[path]}


def fine_mosaic(source_records, shape, dst_transform, dst_crs, fine_fua_mask, collection):
    """Nearest-register raw categorical pixels; first valid filename wins overlap."""
    dst = np.full(shape, MISSING, dtype="int32")
    dst_bounds = array_bounds(shape[0], shape[1], dst_transform)
    geographic = transform_bounds(dst_crs, "EPSG:4326", *dst_bounds, densify_pts=21)
    overlaps = conflicts = fua_overlaps = fua_conflicts = binary_fua_conflicts = 0
    for record in source_records:
        if not intersects(record["bounds"], geographic):
            continue
        with rasterio.open(record["path"], "r") as src:
            # Native windows only; the two-pixel halo covers transform rounding.
            win0 = from_bounds(*geographic, transform=src.transform)
            c0 = max(0, math.floor(win0.col_off)-2)
            r0 = max(0, math.floor(win0.row_off)-2)
            c1 = min(src.width, math.ceil(win0.col_off+win0.width)+2)
            r1 = min(src.height, math.ceil(win0.row_off+win0.height)+2)
            if c1 <= c0 or r1 <= r0:
                continue
            window = Window(c0, r0, c1-c0, r1-r0)
            native = src.read(1, window=window).astype("int32", copy=False)
            # Zero is explicitly retained even if a reader would infer a mask.
            # In these source files nodata is None; sentinel is outside known codes.
            if collection == "WSF_2019":
                unexpected = ~np.isin(native, [0, 1, 255])
            else:
                unexpected = (native != 0) & ~((native >= 1985) & (native <= 2015))
            if unexpected.any():
                raise RuntimeError(f"Unexpected native codes in {record['item_id']}: {np.unique(native[unexpected]).tolist()}")
            tmp = np.full(shape, MISSING, dtype="int32")
            reproject(native, tmp, src_transform=src.window_transform(window), src_crs=src.crs,
                      src_nodata=MISSING, dst_transform=dst_transform, dst_crs=dst_crs,
                      dst_nodata=MISSING, resampling=Resampling.nearest, num_threads=2,
                      init_dest_nodata=True)
        valid = tmp != MISSING
        overlap = (dst != MISSING) & valid
        conflict = overlap & (dst != tmp)
        overlaps += int(overlap.sum())
        conflicts += int(conflict.sum())
        fua_overlaps += int((overlap & fine_fua_mask).sum())
        fua_conflicts += int((conflict & fine_fua_mask).sum())
        if collection == "WSF_2019":
            binary_conflict = overlap & ((dst == 255) != (tmp == 255))
        else:
            binary_conflict = overlap & (((dst >= 1985) & (dst <= 2015)) != ((tmp >= 1985) & (tmp <= 2015)))
        binary_fua_conflicts += int((binary_conflict & fine_fua_mask).sum())
        accept = (dst == MISSING) & valid
        dst[accept] = tmp[accept]
    return dst, dict(overlap_fine_pixel_events=overlaps, value_conflict_fine_pixel_events=conflicts,
                     fua_overlap_fine_pixel_events=fua_overlaps, fua_value_conflict_fine_pixel_events=fua_conflicts,
                     fua_binary_class_conflict_fine_pixel_events=binary_fua_conflicts)


def aggregate_100m(binary, coarse_rows, coarse_cols):
    return binary.reshape(coarse_rows, 10, coarse_cols, 10).mean(axis=(1,3), dtype="float64").astype("float32")


def process_city(row, catalog, force=False):
    unit = row.unit_key
    output_json = WORK / "results" / f"joint_overlay_{unit}.json"
    if output_json.exists() and not force:
        cached = json.loads(output_json.read_text(encoding="utf-8"))
        if cached.get("version") == VERSION:
            return cached
    begin = time.perf_counter()
    print(f"OVERLAY_START {unit} {row.eFUA_name}", flush=True)
    with rasterio.open(GHSL / f"{unit}.tif") as target:
        i15 = next(i+1 for i,d in enumerate(target.descriptions) if d and "E2015" in d)
        i20 = next(i+1 for i,d in enumerate(target.descriptions) if d and "E2020" in d)
        old, new = target.read(i15).astype("int32"), target.read(i20).astype("int32")
        valid = (old != target.nodata) & (new != target.nodata)
        g_grid = np.maximum(new-old, 0)
        g_grid[~valid] = 0
        geographic = transform_bounds(target.crs, "EPSG:4326", *target.bounds, densify_pts=41)
        selected = {collection: [source_identity(r) for r in records if intersects(r["bounds"], geographic)] for collection,records in catalog.items()}
        if any(not x for x in selected.values()):
            raise RuntimeError(f"No raw source coverage: {unit}")
        # [t, s, p, u, paired source coverage] on the 100 m GHSL grid.
        coarse = np.empty((5, target.height, target.width), dtype="float32")
        partition_error_2019 = partition_error_evolution = 0.
        stats = {collection: dict(overlap_fine_pixel_events=0, value_conflict_fine_pixel_events=0,
                                  fua_overlap_fine_pixel_events=0, fua_value_conflict_fine_pixel_events=0,
                                  fua_binary_class_conflict_fine_pixel_events=0) for collection in selected}
        for r0 in range(0, target.height, ROW_BLOCK):
            nrows = min(ROW_BLOCK, target.height-r0)
            shape = (nrows*10, target.width*10)
            fine_transform = target.transform * Affine.translation(0,r0) * Affine.scale(.1,.1)
            fine_valid = np.repeat(np.repeat(valid[r0:r0+nrows],10,axis=0),10,axis=1)
            wsf, stat19 = fine_mosaic(selected["WSF_2019"],shape,fine_transform,target.crs,fine_valid,"WSF_2019")
            evo, stat15 = fine_mosaic(selected["WSF_Evolution"],shape,fine_transform,target.crs,fine_valid,"WSF_Evolution")
            pair_coverage = (wsf != MISSING) & (evo != MISSING)
            settlement, historic, undocumented = wsf == 255, (evo >= 1985) & (evo <= 2015), wsf == 1
            joint = settlement & ~historic & pair_coverage
            arrays = [joint, settlement & pair_coverage, historic & pair_coverage,
                      undocumented & pair_coverage, pair_coverage]
            for idx, array in enumerate(arrays):
                coarse[idx,r0:r0+nrows] = aggregate_100m(array,nrows,target.width)
            nonsettlement = aggregate_100m((wsf == 0) & pair_coverage,nrows,target.width)
            not_historic_positive = aggregate_100m((evo == 0) & pair_coverage,nrows,target.width)
            chunk = coarse[:,r0:r0+nrows]
            partition_error_2019 = max(partition_error_2019,float(np.max(np.abs(chunk[1]+chunk[3]+nonsettlement-chunk[4]))))
            partition_error_evolution = max(partition_error_evolution,float(np.max(np.abs(chunk[2]+not_historic_positive-chunk[4]))))
            for collection, new_stats in [("WSF_2019",stat19),("WSF_Evolution",stat15)]:
                for key,value in new_stats.items():
                    stats[collection][key] += value
            if r0 == 0 or r0+nrows == target.height:
                print(f"OVERLAY_ROWS {unit} {r0+nrows}/{target.height}",flush=True)
        coverage = coarse[4]
        incomplete = valid & (coverage != 1)
        if incomplete.any():
            failure = dict(unit_key=unit, incomplete_fua_cells=int(incomplete.sum()),
                           incomplete_positive_cells=int((incomplete & (g_grid > 0)).sum()),
                           ghsl_g_on_incomplete_cells_m2=float(g_grid[incomplete].sum()),
                           minimum_coverage=float(coverage[valid].min()), source_records=selected)
            (WORK / "results" / f"joint_overlay_coverage_failure_{unit}.json").write_text(json.dumps(failure,indent=2),encoding="utf-8")
            raise RuntimeError(f"Incomplete paired source coverage in GHSL-valid FUA cells: {unit}; {failure['incomplete_fua_cells']} cells")
        # Values outside the covered city domain remain missing, never inferred zero.
        coarse[:,~valid] = np.nan
        t,s,p,u = coarse[:4]
        lower, upper = np.maximum(0,s-p), np.minimum(s,1-p)
        bound_violation = max(float(np.max(lower[valid]-t[valid])),float(np.max(t[valid]-upper[valid])),0.)
        if bound_violation > 1e-6:
            raise RuntimeError(f"Joint indicator outside same-grid Frechet bounds: {unit}")
        partition_error = max(partition_error_2019,partition_error_evolution)
        if partition_error > 1e-6:
            raise RuntimeError(f"Independent source class partition fails: {unit}")
        data = pd.read_parquet(CELLS / f"{unit}.parquet")
        rr,cc = data.grid_row.to_numpy(),data.grid_column.to_numpy()
        g = data.added_surface_m2.to_numpy(dtype="float64")
        if not np.array_equal(g_grid[rr,cc],g) or len(data) != np.count_nonzero(g_grid):
            raise RuntimeError(f"Released positive-cell support differs from GHSL epochs: {unit}")
        depth = data.integrated_modelled_depth_m.to_numpy(dtype="float64")
        tf,sf,pf,uf = [x[rr,cc].astype("float64") for x in [t,s,p,u]]
        archived_s = data.endpoint_support_fraction.to_numpy(dtype="float64")
        archived_p = data.preexisting_detected_fraction.to_numpy(dtype="float64")
        archived_u = data.endpoint_undocumented_fraction.to_numpy(dtype="float64")
        fine_product = sf*(1-pf)
        archived_product = archived_s*(1-archived_p)
        summary = dict(unit_key=unit,eFUA_name=row.eFUA_name,version=VERSION,
                       positive_cells=len(data),ghsl_added_surface_m2=float(g.sum()),
                       target_bbox_100m_cells=target.width*target.height, fine_grid_pixels=target.width*target.height*100,
                       ghsl_valid_100m_cells=int(valid.sum()),ghsl_valid_fine_grid_pixels=int(valid.sum())*100,
                       paired_coverage_minimum_fua=float(coverage[valid].min()),
                       missing_source_fua_cells=int(incomplete.sum()),bound_max_violation=bound_violation,
                       class_partition_max_error=partition_error,
                       independent_2019_class_partition_max_error=partition_error_2019,
                       independent_evolution_class_partition_max_error=partition_error_evolution,
                       source_overlap_statistics=stats, source_records=selected)
        for name,fraction in [("joint_overlay",tf),("fine_product",fine_product),("archived_product",archived_product)]:
            summary[f"{name}_allocated_surface_m2"] = float(np.dot(g,fraction))
            summary[f"{name}_depth_weighted_proxy_m3"] = float(np.dot(g*depth,fraction))
            data[f"{name}_fraction"] = fraction.astype("float32")
        for name,first,second in [("joint_vs_fine_product",tf,fine_product),("fine_vs_archived_product",fine_product,archived_product)]:
            delta = first-second
            summary[f"{name}_signed_surface_difference_m2"] = float(np.dot(g,delta))
            summary[f"{name}_absolute_cell_surface_difference_m2"] = float(np.dot(g,np.abs(delta)))
            summary[f"{name}_signed_depth_proxy_difference_m3"] = float(np.dot(g*depth,delta))
            summary[f"{name}_absolute_cell_depth_proxy_difference_m3"] = float(np.dot(g*depth,np.abs(delta)))
            summary[f"{name}_max_cell_fraction_difference"] = float(np.max(np.abs(delta)))
        for name,fine,archived in [("s",sf,archived_s),("p",pf,archived_p),("u",uf,archived_u)]:
            summary[f"fine_minus_archived_{name}_g_weighted_mean"] = float(np.dot(g,fine-archived)/g.sum())
            summary[f"fine_vs_archived_{name}_g_weighted_mae"] = float(np.dot(g,np.abs(fine-archived))/g.sum())
            summary[f"fine_vs_archived_{name}_cell_max_absolute_difference"] = float(np.max(np.abs(fine-archived)))
            data[f"fine_{name}_fraction"] = fine.astype("float32")
        lower_pos,upper_pos = lower[rr,cc].astype("float64"),upper[rr,cc].astype("float64")
        summary["fine_lower_allocated_surface_m2"] = float(np.dot(g,lower_pos))
        summary["fine_upper_allocated_surface_m2"] = float(np.dot(g,upper_pos))
        summary["fine_lower_depth_weighted_proxy_m3"] = float(np.dot(g*depth,lower_pos))
        summary["fine_upper_depth_weighted_proxy_m3"] = float(np.dot(g*depth,upper_pos))
        data["fine_lower_fraction"] = lower_pos.astype("float32")
        data["fine_upper_fraction"] = upper_pos.astype("float32")
        raster_path = WORK / "datasets" / "joint_overlay" / f"{unit}_t_s_p_u_coverage_100m.tif"
        profile = target.profile.copy()
        profile.update(dtype="float32",count=5,nodata=np.nan)
        with rasterio.open(raster_path,"w",**profile) as dst:
            dst.write(coarse)
            for idx,name in enumerate(["joint_t","settlement_s","historic_positive_p","undocumented_u","pair_coverage"],1):
                dst.set_band_description(idx,name)
            dst.update_tags(fine_grid="nested 10m Mollweide, 10x10 subcells per GHSL100mcell", registration="nearest",merge_rule="lexicographic filename first valid",interpretation="map-specific joint-class proportion, not construction truth")
        data.to_parquet(WORK / "datasets" / "joint_overlay" / f"{unit}_positive_cells.parquet",index=False,compression="zstd")
    summary.update(completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.perf_counter()-begin,3),raster_path=str(raster_path))
    output_json.write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(f"OVERLAY_DONE {unit} joint={summary['joint_overlay_allocated_surface_m2']:.3f} fineproduct={summary['fine_product_allocated_surface_m2']:.3f} archived={summary['archived_product_allocated_surface_m2']:.3f} seconds={summary['elapsed_seconds']}",flush=True)
    return summary


def write_report(records,expected):
    for record in records:
        for name in ["joint_overlay","fine_product","archived_product"]:
            area = record[f"{name}_allocated_surface_m2"]
            record[f"{name}_normalized_city_depth_m"] = record[f"{name}_depth_weighted_proxy_m3"]/area if area else None
    frame = pd.DataFrame([{k:v for k,v in r.items() if k not in ["source_records","source_overlap_statistics"]} for r in records]).sort_values("unit_key")
    for name in ["joint_overlay","fine_product","archived_product"]:
        frame[f"{name}_city_depth_rank"] = frame[f"{name}_normalized_city_depth_m"].rank(ascending=False,method="min").astype("Int64")
    frame["rank_delta_joint_minus_fine_product"] = frame.joint_overlay_city_depth_rank-frame.fine_product_city_depth_rank
    frame["rank_delta_joint_minus_archived_product"] = frame.joint_overlay_city_depth_rank-frame.archived_product_city_depth_rank
    for name in ["fine_product","archived_product"]:
        frame[f"city_depth_signed_difference_joint_minus_{name}_m"] = frame.joint_overlay_normalized_city_depth_m-frame[f"{name}_normalized_city_depth_m"]
        frame[f"city_depth_absolute_difference_joint_vs_{name}_m"] = frame[f"city_depth_signed_difference_joint_minus_{name}_m"].abs()
    frame.to_csv(WORK / "results" / "joint_overlay_city_summary.csv",index=False)
    aggregate = dict(version=VERSION, completed_cities=len(frame),expected_cities=expected,
                     positive_cells=int(frame.positive_cells.sum()), ghsl_added_surface_m2=float(frame.ghsl_added_surface_m2.sum()),
                     total_processing_seconds=float(frame.elapsed_seconds.sum()), max_bound_violation=float(frame.bound_max_violation.max()),
                     max_class_partition_error=float(frame.class_partition_max_error.max()),
                     missing_source_fua_cells=int(frame.missing_source_fua_cells.sum()))
    sums = [c for c in frame if c.endswith("_m2") or c.endswith("_m3")]
    for col in sums:
        if col != "ghsl_added_surface_m2":
            aggregate[col] = float(frame[col].sum())
    for prefix in ["joint_vs_fine_product","fine_vs_archived_product"]:
        denom = "fine_product" if prefix.startswith("joint") else "archived_product"
        aggregate[prefix+"_relative_surface_difference"] = aggregate[prefix+"_signed_surface_difference_m2"]/aggregate[denom+"_allocated_surface_m2"]
        aggregate[prefix+"_relative_depth_proxy_difference"] = aggregate[prefix+"_signed_depth_proxy_difference_m3"]/aggregate[denom+"_depth_weighted_proxy_m3"]
    for name in ["joint_overlay","fine_product","archived_product"]:
        aggregate[f"{name}_normalized_pooled_depth_m"] = aggregate[f"{name}_depth_weighted_proxy_m3"]/aggregate[f"{name}_allocated_surface_m2"]
    for name in ["fine_product","archived_product"]:
        first = frame.joint_overlay_normalized_city_depth_m.rank(method="average")
        second = frame[f"{name}_normalized_city_depth_m"].rank(method="average")
        aggregate[f"spearman_joint_vs_{name}_city_depth"] = float(first.corr(second)) if len(frame) > 1 else None
        aggregate[f"max_absolute_rank_shift_joint_vs_{name}"] = int(np.max(np.abs(frame.joint_overlay_city_depth_rank-frame[f"{name}_city_depth_rank"])))
        aggregate[f"cities_rank_changed_joint_vs_{name}"] = int((frame.joint_overlay_city_depth_rank != frame[f"{name}_city_depth_rank"]).sum())
        difference = frame[f"city_depth_absolute_difference_joint_vs_{name}_m"]
        max_row = frame.loc[difference.idxmax()]
        aggregate[f"median_absolute_city_depth_difference_joint_vs_{name}_m"] = float(difference.median())
        aggregate[f"max_absolute_city_depth_difference_joint_vs_{name}_m"] = float(difference.max())
        aggregate[f"city_at_max_absolute_depth_difference_joint_vs_{name}"] = dict(
            unit_key=max_row.unit_key,eFUA_name=max_row.eFUA_name,
            joint_depth_m=float(max_row.joint_overlay_normalized_city_depth_m),
            comparison_depth_m=float(max_row[f"{name}_normalized_city_depth_m"]),
            signed_joint_minus_comparison_m=float(max_row[f"city_depth_signed_difference_joint_minus_{name}_m"]))
        k = min(10,len(frame))
        joint_top = frame.sort_values(["joint_overlay_normalized_city_depth_m","unit_key"],ascending=[False,True]).head(k)
        comparison_top = frame.sort_values([f"{name}_normalized_city_depth_m","unit_key"],ascending=[False,True]).head(k)
        common = sorted(set(joint_top.unit_key)&set(comparison_top.unit_key))
        aggregate[f"top10_overlap_joint_vs_{name}"] = dict(k=k,overlap_cities=len(common),
            common_unit_keys=common,joint_top10_unit_keys=joint_top.unit_key.tolist(),
            comparison_top10_unit_keys=comparison_top.unit_key.tolist(),
            tie_break="normalized depth descending, then unit_key ascending")
    pilot_rows = frame[frame.unit_key.isin(["IND_FUA_09258","IND_FUA_10496","IND_FUA_07466"])]
    case_columns = ["unit_key","eFUA_name"] + [f"{name}_normalized_city_depth_m" for name in ["joint_overlay","fine_product","archived_product"]] + [f"{name}_city_depth_rank" for name in ["joint_overlay","fine_product","archived_product"]] + [f"city_depth_absolute_difference_joint_vs_{name}_m" for name in ["fine_product","archived_product"]]
    aggregate["three_pilot_case_depths_and_ranks"] = json.loads(pilot_rows[case_columns].to_json(orient="records"))
    for fraction in ["s","p","u"]:
        for metric in ["g_weighted_mean","g_weighted_mae"]:
            key = f"fine_minus_archived_{fraction}_{metric}" if metric == "g_weighted_mean" else f"fine_vs_archived_{fraction}_{metric}"
            aggregate[key] = float(np.dot(frame.ghsl_added_surface_m2,frame[key])/frame.ghsl_added_surface_m2.sum())
    aggregate["cities_joint_surface_greater_than_fine_product"] = int((frame.joint_overlay_allocated_surface_m2 > frame.fine_product_allocated_surface_m2).sum())
    aggregate["cities_joint_depth_proxy_greater_than_fine_product"] = int((frame.joint_overlay_depth_weighted_proxy_m3 > frame.fine_product_depth_weighted_proxy_m3).sum())
    sources = {x["path"]:x for r in records for values in r["source_records"].values() for x in values}
    aggregate["source_files_used"] = len(sources)
    aggregate["source_sha256_all_match_prior_audit"] = all(x["sha256_matches_prior_audit"] for x in sources.values())
    overlap = {collection:{key:sum(r["source_overlap_statistics"][collection][key] for r in records) for key in records[0]["source_overlap_statistics"][collection]} for collection in ["WSF_2019","WSF_Evolution"]}
    aggregate["source_overlap_statistics"] = overlap
    override_file = WORK / "results" / "joint_overlay_source_overrides.json"
    overrides = json.loads(override_file.read_text(encoding="utf-8")) if override_file.exists() else {}
    aggregate["source_recovery_files_available"] = len(overrides)
    aggregate["source_recovery_files_used"] = sum(bool(x.get("recovery_record")) for x in sources.values())
    aggregate["reproduce_command"] = f'python -u "{Path(__file__)}" --scope all --recover-sources --force'
    (WORK / "results" / "joint_overlay_aggregate_summary.json").write_text(json.dumps(aggregate,indent=2),encoding="utf-8")
    (WORK / "results" / "joint_overlay_source_manifest.json").write_text(json.dumps(list(sources.values()),indent=2),encoding="utf-8")
    table = frame[["unit_key","eFUA_name","joint_overlay_allocated_surface_m2","fine_product_allocated_surface_m2","archived_product_allocated_surface_m2","joint_overlay_depth_weighted_proxy_m3","fine_product_depth_weighted_proxy_m3","archived_product_depth_weighted_proxy_m3","joint_overlay_normalized_city_depth_m","fine_product_normalized_city_depth_m","archived_product_normalized_city_depth_m","joint_overlay_city_depth_rank","fine_product_city_depth_rank","archived_product_city_depth_rank","elapsed_seconds"]].to_csv(index=False)
    report = f"""# Joint-location overlay baseline

Completed {len(frame)} of {expected} requested cities. Results apply to the completed scope only. This comparison includes a conventional fine-grid overlay that preserves joint spatial position; a binary threshold is not used as a surrogate for all conventional overlays.

## Exact conventions

WSF2019 and WSF Evolution raw categorical maps are nearest-neighbour registered to a common 10 m World Mollweide grid strictly nested in the existing GHSL 100 m grid. Each coarse cell contains exactly 10 by 10 equal-area fine pixels. Processing uses {ROW_BLOCK} GHSL-row blocks; no large fine raster is saved.

At fine pixel j: S_j = 1[WSF2019=255], U_j = 1[WSF2019=1], and P_j = 1[1985 <= Evolution <= 2015]. WSF2019=0 is documented non-settlement. Evolution=0 is the not-historic-positive complement, not proven new construction. Value1 remains undocumented and does not enter S_j. Zeros are retained as valid source values. Missing/out-of-coverage has a separate sentinel and is never converted to zero. Every GHSL-valid FUA cell is required to have all 100 fine pixels covered by both sources.

s_i = mean_j S_j; p_i = mean_j P_j; u_i = mean_j U_j; t_i = mean_j [S_j*(1-P_j)]. Consequently max(0,s_i-p_i) <= t_i <= min(s_i,1-p_i). These bounds are verified on the common registration, rather than compared across mismatched grids.

Overlapping source tiles are ordered lexicographically by filename, and the first geometrically valid source value is retained. Zero is valid in this rule. All overlap events, disagreements in raw value and disagreements in binary class are counted, including FUA-only events. The source manifest records filenames, native geometry and SHA256 checked against the previous source audit. Overlap counts are events and can count a fine pixel more than once where more than two files overlap.

Three allocations use the same g_i=max(B2020-B2015,0) and released depth D_i:

1. Joint overlay: A_J = sum_i g_i*t_i; N_J = sum_i g_i*D_i*t_i.
2. Fine-grid marginal product: A_F = sum_i g_i*s_i*(1-p_i); N_F = sum_i g_i*D_i*s_i*(1-p_i).
3. Archived product: A_A = sum_i g_i*s_arch,i*(1-p_arch,i), and the analogous N_A. s_arch is endpoint_support_fraction, not the conditional endpoint_settlement_fraction.

N is the unnormalized depth-weighted proxy in m3, not a city mean. Normalized city depths are M_J=N_J/A_J, M_F=N_F/A_F and M_A=N_A/A_A, in metres. CSV ranks order these normalized depths from highest to lowest with minimum-rank ties. Spearman coefficients are descriptive rank correlations; no significance or independence claim is made. Partial-run ranks apply only to the completed city scope.

Absolute differences between normalized city depths are reported separately from differences in the unnormalized N proxy: the aggregate JSON contains their median and maximum, the city attaining each maximum, and Delhi, Guwahati and Sultanpur values. Top-ten membership uses depth descending and unit_key ascending to break ties; the overlap denominator is ten for the complete 91-city run.

Joint versus fine-grid product isolates the consequence of discarding joint location while holding the fine registration and tile merge convention fixed. Fine-grid product versus archived product includes registration and merge-convention differences. Cellwise absolute differences are reported as well as signed aggregate differences so cancellation remains visible. All depth measures are modelled depth-weighted proxies.

## Results

```json
{json.dumps(aggregate,indent=2)}
```

```csv
{table}
```

## Interpretation boundary

t is a map-specific intersection under explicit source-class and registration conventions. It does not establish true construction dates, and neither t nor a Frechet interval resolves the semantics of undocumented WSF2019=1 or the historical detection complement. Multiplying g by t remains proportional allocation of a 100 m GHSL building-surface increment; it does not locate that increment's actual subcell roof geometry. A correctly registered overlay can directly retain joint positions and should not be presented as inferior to marginal bounds merely because it is conventional. Marginal bounds are relevant when only marginal support is retained or exact joint geometry is unavailable under the stated data contract.

Deliverables: joint_overlay_city_summary.csv, joint_overlay_aggregate_summary.json, per-city joint_overlay_*.json with source/overlap details; datasets/joint_overlay/*t_s_p_u_coverage_100m.tif and positive-cell Parquet. Fraction maps outside the GHSL FUA mask are NaN.

## Source recovery and reproduction

Source identity mismatches found against the previous source audit are retained in joint_overlay_failures_pre_source_recovery_20261005.json and joint_overlay_verification_failed_identity_pre_additional_recovery_20261005.json. A decoder failure was also observed in the original WSF2019 78_28 tile. These findings do not establish when any file changed or became corrupt. The E: originals are preserved. Official-source re-fetches use fresh filenames under F:\\AcademicData\\IUFEE_revision_20261005\\raw\\WSF_source_recovery_20261005, are made read-only and are accepted only when their SHA256 is exactly equal to the old source audit. The recovery audit records all {len(overrides)} available recoveries, URLs, hashes, file sizes, HTTP headers and retrieval times. The override JSON maps original item IDs to these byte-identical recovered files; original filename order determines tile precedence. Final verification re-hashes every source actually used and compares file size and modification/creation timestamps before and after computation.

Reproduction on this host, explicitly using the source override manifest and forcing fresh city computation:

```powershell
{aggregate['reproduce_command']}
```

The script automatically reads results/joint_overlay_source_overrides.json; --recover-sources validates existing recovered files and fetches unresolved logged source identity failures. --force prevents reuse of earlier city caches. Only joint_overlay_verification.json with all_passed=true confirms the final run's internal checks.
"""
    (WORK / "results" / "JOINT_OVERLAY_REPORT.md").write_text(report,encoding="utf-8")
    return aggregate


def verify_outputs(records):
    source_records = {x["path"]:x for r in records for values in r["source_records"].values() for x in values}
    source_checks = []
    for path,record in sorted(source_records.items()):
        stat_before = source_stat(path)
        current = sha256(path)
        stat_after = source_stat(path)
        recovery = record.get("recovery_record")
        readonly = not bool(Path(path).stat().st_mode & stat.S_IWRITE)
        source_checks.append(dict(path=path,item_id=record["item_id"],current_sha256=current,
                                  sha256_matches_recorded_and_old_audit=current == record["source_sha256"] == record["prior_source_sha256"].upper(),
                                  recovered_source=bool(recovery), recovered_file_readonly=readonly if recovery else None,
                                  source_stat_at_initial_hash=record.get("source_stat_at_initial_hash"),
                                  source_stat_before_final_hash=stat_before,source_stat_after_final_hash=stat_after,
                                  source_stat_stable_during_final_hash=stat_before == stat_after,
                                  source_stat_stable_between_initial_and_final_hash=record.get("source_stat_at_initial_hash") == stat_after))
    city_checks = []
    for record in records:
        unit = record["unit_key"]
        data = pd.read_parquet(WORK / "datasets" / "joint_overlay" / f"{unit}_positive_cells.parquet")
        g = data.added_surface_m2.to_numpy(dtype="float64")
        depth = data.integrated_modelled_depth_m.to_numpy(dtype="float64")
        t,s,p = [data[c].to_numpy(dtype="float64") for c in ["joint_overlay_fraction","fine_s_fraction","fine_p_fraction"]]
        bound_error = max(float(np.max(np.maximum(0,s-p)-t)),float(np.max(t-np.minimum(s,1-p))),0.)
        errors = {}
        for name,fraction in [("joint_overlay",t),("fine_product",s*(1-p)),("archived_product",data.endpoint_support_fraction.to_numpy(dtype="float64")*(1-data.preexisting_detected_fraction.to_numpy(dtype="float64")))]:
            area,numerator = float(np.dot(g,fraction)),float(np.dot(g*depth,fraction))
            errors[f"{name}_surface_absolute_error_m2"] = abs(area-record[f"{name}_allocated_surface_m2"])
            errors[f"{name}_numerator_absolute_error_m3"] = abs(numerator-record[f"{name}_depth_weighted_proxy_m3"])
            errors[f"{name}_normalized_depth_absolute_error_m"] = abs(numerator/area-record[f"{name}_normalized_city_depth_m"])
        with rasterio.open(GHSL / f"{unit}.tif") as reference,rasterio.open(record["raster_path"]) as aligned:
            same_grid = bool(reference.shape == aligned.shape and reference.crs == aligned.crs and reference.transform.almost_equals(aligned.transform))
            i15 = next(i+1 for i,d in enumerate(reference.descriptions) if d and "E2015" in d)
            i20 = next(i+1 for i,d in enumerate(reference.descriptions) if d and "E2020" in d)
            old,new = reference.read(i15).astype("int32"),reference.read(i20).astype("int32")
            valid = (old != reference.nodata) & (new != reference.nodata)
            coverage = aligned.read(5)
            coverage_complete = bool((coverage[valid] == 1).all())
            raw_g = np.maximum(new-old,0)
            raw_g[~valid] = 0
            released_g_matches = bool(np.array_equal(raw_g[data.grid_row.to_numpy(),data.grid_column.to_numpy()],g) and np.count_nonzero(raw_g) == len(data))
        passed = bool(same_grid and coverage_complete and released_g_matches and bound_error < 1e-6 and max(errors.values()) < 1e-5 and record["class_partition_max_error"] < 1e-6)
        city_checks.append(dict(unit_key=unit,passed=passed,aligned_grid_matches=same_grid,
                                coverage_complete=coverage_complete,released_positive_g_matches=released_g_matches,
                                frechet_bound_max_violation=bound_error,allocation_recomputation_errors=errors,
                                independent_source_class_partition_max_error=record["class_partition_max_error"]))
    passed = all(x["passed"] for x in city_checks) and all(x["sha256_matches_recorded_and_old_audit"] and x["source_stat_stable_during_final_hash"] and x["source_stat_stable_between_initial_and_final_hash"] and (not x["recovered_source"] or x["recovered_file_readonly"]) for x in source_checks)
    result = dict(completed_utc=datetime.now(timezone.utc).isoformat(),all_passed=passed,completed_cities=len(records),
                  script_sha256=sha256(Path(__file__)),version=VERSION,
                  runtime=dict(python=platform.python_version(),rasterio=rasterio.__version__,gdal=rasterio.__gdal_version__,numpy=np.__version__,pandas=pd.__version__),
                  city_checks=city_checks,source_identity_stability_checks=source_checks,
                  interpretation="Internal numeric, geometry and source-identity audit; no construction-ground-truth or map-accuracy claim")
    (WORK / "results" / "joint_overlay_verification.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    if not passed:
        raise RuntimeError("Final joint overlay verification failed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope",choices=["pilot","all"],default="pilot")
    parser.add_argument("--recover-sources",action="store_true")
    parser.add_argument("--force",action="store_true",help="Recompute every requested city and source identity rather than reuse cached city outputs")
    args = parser.parse_args()
    (WORK / "datasets" / "joint_overlay").mkdir(parents=True,exist_ok=True)
    if args.recover_sources:
        recover_sources()
    catalog = catalog_sources()
    roster = pd.read_csv(ROSTER)
    roster = roster[roster.Cntry_ISO == "IND"]
    pilot = ["IND_FUA_09258","IND_FUA_10496","IND_FUA_07466"]
    keys = pilot if args.scope == "pilot" else pilot+[u for u in roster.unit_key if u not in pilot]
    records = []
    failures = []
    for unit in keys:
        row = roster[roster.unit_key == unit].iloc[0]
        try:
            records.append(process_city(row,catalog,force=args.force))
            write_report(records,len(keys))
        except Exception as exc:
            failure = dict(unit_key=unit,error=str(exc))
            failures.append(failure)
            (WORK / "results" / "joint_overlay_failures.json").write_text(json.dumps(failures,indent=2),encoding="utf-8")
            print(f"OVERLAY_FAILED {json.dumps(failure)}",flush=True)
            if args.scope == "pilot":
                raise
    if failures:
        raise RuntimeError(f"Overlay failed in {len(failures)} cities")
    verification = verify_outputs(records)
    total_bbox = 0
    for unit in roster.unit_key:
        with rasterio.open(GHSL / f"{unit}.tif") as src:
            total_bbox += src.width*src.height
    sample_bbox = sum(r["target_bbox_100m_cells"] for r in records)
    extrapolated = sum(r["elapsed_seconds"] for r in records)/sample_bbox*total_bbox
    status = dict(completed_cities=len(records),scope=args.scope,estimated_all91_processing_seconds=extrapolated,
                  total_all91_target_bbox_100m_cells=total_bbox,run_utc=datetime.now(timezone.utc).isoformat(),
                  script_sha256=sha256(Path(__file__)),all_checks_passed=verification["all_passed"])
    (WORK / "results" / "joint_overlay_run_status.json").write_text(json.dumps(status,indent=2),encoding="utf-8")
    final_frame = pd.read_csv(WORK / "results" / "joint_overlay_city_summary.csv").set_index("unit_key")
    for record in records:
        for name in ["joint_overlay","fine_product","archived_product"]:
            record[f"{name}_city_depth_rank"] = int(final_frame.loc[record["unit_key"],f"{name}_city_depth_rank"])
        (WORK / "results" / f"joint_overlay_{record['unit_key']}.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    (WORK / "results" / "joint_overlay_failures.json").write_text("[]",encoding="utf-8")
    print(f"OVERLAY_ALL_DONE {len(records)} estimate_all91_seconds={extrapolated:.1f}",flush=True)


if __name__ == "__main__":
    main()
