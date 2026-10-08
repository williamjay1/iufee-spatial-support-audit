"""GLAD v2 paired-year cross-product consistency on the exact GHSL study grids.

This is a consistency comparison, not ground truth or an area accuracy estimate.
Native class pairs are encoded before average reprojection. All five fractions
share exactly the same pair support. No AI-assisted validation labels are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests
import rasterio
from affine import Affine
from rasterio.enums import Resampling
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window

WORK = Path(r"D:\MLWork\IUFEE_revision_20261005")
RAW = Path(r"F:\AcademicData\IUFEE_revision_20261005\raw\GLAD_v2_native_windows_20261005")
GHSL = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\ghsl_built_s_100m\study_units")
ROSTER = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\roster\study_unit_roster.csv")
CELLS = Path(r"D:\codex\sci\remote_sensing_sci_novelty_audit\guangzhou_india_flood_exposure_study\grsl_submission_2026\zenodo_release\IUFEE_v1_2\data\database_v1_2\expansion_cells_100m")
BASE = "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2"
RES = 0.00025
CLASS_NAMES = ["new_built", "stable_built", "absent_both", "built_loss", "missing_pair"]
FORMULA_VERSION = "GLADpair_v2_joint_s_endpoint_support"
ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
           GDAL_HTTP_TIMEOUT="120", GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="2",
           CPL_VSIL_CURL_CHUNK_SIZE="1048576", CPL_VSIL_CURL_CACHE_SIZE="134217728",
           GDAL_HTTP_MULTIRANGE="YES", GDAL_CACHEMAX=256)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def source_header(url):
    r = requests.head(url, timeout=45)
    r.raise_for_status()
    keep = ["etag", "last-modified", "content-length", "accept-ranges", "x-goog-generation", "x-goog-hash"]
    headers = {k: r.headers.get(k) for k in keep}
    if headers["accept-ranges"] != "bytes":
        raise RuntimeError(f"Server does not advertise byte ranges: {url}; whole-tile downloads are disabled")
    return headers


def native_pair(unit, bounds):
    """Read only tile windows, preserving native pixels in immutable F: files."""
    left, bottom, right, top = bounds
    # Two native pixels of margin cover numerical transform error at the target edge.
    c0 = math.floor((left + 180) / RES) - 2
    c1 = math.ceil((right + 180) / RES) + 2
    r0 = math.floor((90 - top) / RES) - 2
    r1 = math.ceil((90 - bottom) / RES) + 2
    shape = (r1 - r0, c1 - c0)
    native_transform = Affine(RES, 0, -180 + c0 * RES, 0, -RES, 90 - r0 * RES)
    arrays = {year: np.full(shape, 255, dtype="uint8") for year in [2015, 2020]}
    records = []
    lon_first = math.floor((native_transform.c + 1e-9) / 10) * 10
    lon_last = math.floor((-180 + c1 * RES - 1e-9) / 10) * 10
    lat_first = math.floor((90 - r1 * RES + 1e-9) / 10) * 10 + 10
    lat_last = math.ceil((native_transform.f - 1e-9) / 10) * 10
    for lat in range(lat_first, lat_last + 1, 10):
        for lon in range(lon_first, lon_last + 1, 10):
            tile = f"{lat:02d}N_{lon:03d}E"
            tc0 = round((lon + 180) / RES)
            tr0 = round((90 - lat) / RES)
            wc0, wc1 = max(c0, tc0), min(c1, tc0 + 40000)
            wr0, wr1 = max(r0, tr0), min(r1, tr0 + 40000)
            if wc1 <= wc0 or wr1 <= wr0:
                continue
            window = Window(wc0-tc0, wr0-tr0, wc1-wc0, wr1-wr0)
            for year in [2015, 2020]:
                stem = f"{unit}_GLADv2_{year}_{tile}_r{int(window.row_off)}c{int(window.col_off)}_h{int(window.height)}w{int(window.width)}_native_20261005"
                path = RAW / (stem + ".tif")
                sidecar = RAW / (stem + ".json")
                url = f"{BASE}/{year}/{tile}.tif"
                if (path.exists() or sidecar.exists()) and not (path.exists() and sidecar.exists()):
                    # An interrupted write is preserved; new retrieval gets a new name.
                    # Completed retries can be reused without modifying any raw record.
                    completed_retries = [p for p in sorted(RAW.glob(stem + "_retry_*.json")) if p.with_suffix(".tif").exists()]
                    if completed_retries:
                        sidecar = completed_retries[-1]
                        path = sidecar.with_suffix(".tif")
                    else:
                        incomplete = dict(original_file=str(path), original_sidecar=str(sidecar),
                                          preserved_without_overwrite=True, detected_utc=utcnow())
                        audit_path = WORK / "results" / f"glad_incomplete_raw_{unit}_{year}_{tile}.json"
                        audit_path.write_text(json.dumps(incomplete, indent=2), encoding="utf-8")
                        if path.exists():
                            os.chmod(path, stat.S_IREAD)
                        if sidecar.exists():
                            os.chmod(sidecar, stat.S_IREAD)
                        retry_stem = stem + f"_retry_{time.time_ns()}"
                        path = RAW / (retry_stem + ".tif")
                        sidecar = RAW / (retry_stem + ".json")
                if path.exists() and sidecar.exists():
                    rec = json.loads(sidecar.read_text(encoding="utf-8"))
                    if sha256(path) != rec["sha256"]:
                        raise RuntimeError(f"Raw cache integrity mismatch: {path}")
                    with rasterio.open(path) as local:
                        arr = local.read(1)
                    print(f"RAW_REUSE {unit} {year} {tile} {arr.shape}", flush=True)
                else:
                    if path.exists() or sidecar.exists():
                        raise RuntimeError(f"Incomplete immutable raw record; do not overwrite: {path}")
                    headers = source_header(url)
                    begin = time.perf_counter()
                    print(f"READ_START {unit} {year} {tile} window={window}", flush=True)
                    with rasterio.Env(**ENV), rasterio.open(url) as src:
                        if src.crs.to_epsg() != 4326 or src.shape != (40000, 40000):
                            raise RuntimeError("Unexpected GLAD native grid")
                        expected = Affine(RES, 0, lon, 0, -RES, lat)
                        if not src.transform.almost_equals(expected):
                            raise RuntimeError("GLAD tile alignment differs from documented grid")
                        arr = src.read(1, window=window)
                        win_transform = src.window_transform(window)
                        source_tags = src.tags()
                        source_nodata = src.nodata
                    profile = dict(driver="GTiff", width=arr.shape[1], height=arr.shape[0], count=1,
                                   dtype="uint8", crs="EPSG:4326", transform=win_transform,
                                   nodata=255, compress="deflate", tiled=True, blockxsize=256, blockysize=256)
                    with rasterio.open(path, "w", **profile) as dst:
                        dst.write(arr, 1)
                        dst.set_band_description(1, f"GLAD_v2_land_cover_{year}_native_codes")
                    rec = dict(unit_key=unit, year=year, tile=tile, source_url=url,
                               source_header=headers, source_crs="EPSG:4326", source_nodata=source_nodata,
                               source_tags=source_tags, window_pixel=[int(window.col_off), int(window.row_off), int(window.width), int(window.height)],
                               window_transform=list(win_transform), output_file=str(path),
                               bytes=path.stat().st_size, sha256=sha256(path), accessed_utc=utcnow(),
                               access_method="GDAL /vsicurl byte-range city window; no full tile download",
                               license="CC BY 4.0 (GLAD public download page)",
                               native_class_legend="250 Built-up; 255 No data; annual map codes",
                               elapsed_seconds=round(time.perf_counter()-begin, 3))
                    sidecar.write_text(json.dumps(rec, indent=2), encoding="utf-8")
                    os.chmod(path, stat.S_IREAD)
                    os.chmod(sidecar, stat.S_IREAD)
                    print(f"READ_DONE {unit} {year} {tile} {rec['elapsed_seconds']}s {rec['bytes']} bytes", flush=True)
                arrays[year][wr0-r0:wr1-r0, wc0-c0:wc1-c0] = arr
                records.append(rec)
    return arrays[2015], arrays[2020], native_transform, records


def align_pair(a, b, native_transform, target):
    pair_valid = (a != 255) & (b != 255)
    a_built, b_built = a == 250, b == 250
    # One exhaustive mutually exclusive native classification, including missing.
    codes = np.full(a.shape, 4, dtype="uint8")
    codes[pair_valid & ~a_built & b_built] = 0
    codes[pair_valid & a_built & b_built] = 1
    codes[pair_valid & ~a_built & ~b_built] = 2
    codes[pair_valid & a_built & ~b_built] = 3
    out = np.empty((5, target.height, target.width), dtype="float32")
    for idx in range(5):
        binary = (codes == idx).astype("float32")
        reproject(binary, out[idx], src_transform=native_transform, src_crs="EPSG:4326",
                  dst_transform=target.transform, dst_crs=target.crs,
                  resampling=Resampling.average, src_nodata=None, dst_nodata=np.nan,
                  init_dest_nodata=True, num_threads=2)
    if not np.allclose(out.sum(axis=0), 1, atol=1e-4):
        raise RuntimeError("Paired category fractions do not partition each target cell")
    return out


def summarize(unit_row, df, fractions, ghsl_valid, g_grid):
    rr, cc = df.grid_row.to_numpy(), df.grid_column.to_numpy()
    g = df.added_surface_m2.to_numpy(dtype="float64")
    support = df.endpoint_support_fraction.to_numpy(dtype="float64")
    preexisting = df.preexisting_detected_fraction.to_numpy(dtype="float64")
    joint = g * support * (1 - preexisting)
    cov = 1 - fractions[4, rr, cc]
    record = dict(unit_key=unit_row.unit_key, eFUA_name=unit_row.eFUA_name,
                  positive_cells=len(df), ghsl_valid_cells=int(ghsl_valid.sum()),
                  ghsl_added_surface_m2=float(g.sum()), joint_screened_surface_m2=float(joint.sum()),
                  pair_covered_ghsl_g_m2=float(np.dot(g, cov)),
                  pair_covered_joint_m2=float(np.dot(joint, cov)),
                  pair_coverage_g_weighted=float(np.dot(g, cov)/g.sum()))
    for idx, name in enumerate(CLASS_NAMES):
        f = fractions[idx, rr, cc].astype("float64")
        record[f"g_weighted_{name}_fraction"] = float(np.dot(g, f)/g.sum())
        record[f"joint_weighted_{name}_fraction"] = float(np.dot(joint, f)/joint.sum()) if joint.sum() else None
        record[f"g_allocated_{name}_m2"] = float(np.dot(g, f))
        record[f"joint_allocated_{name}_m2"] = float(np.dot(joint, f))
        if idx < 4:
            record[f"g_covered_{name}_fraction"] = float(np.dot(g, f)/np.dot(g, cov))
            record[f"joint_covered_{name}_fraction"] = float(np.dot(joint, f)/np.dot(joint, cov)) if np.dot(joint, cov) else None
        df[f"glad_{name}_fraction"] = f.astype("float32")
    df["glad_pair_coverage_fraction"] = cov.astype("float32")
    df["joint_screened_surface_m2"] = joint
    # Area means on GHSL-valid cells; GLAD built class includes roads, mixed cells.
    record["glad_new_class_area_within_fua_m2"] = float(np.sum(fractions[0, ghsl_valid], dtype="float64") * 10000)
    pos = ghsl_valid & (g_grid > 0)
    zero = ghsl_valid & (g_grid == 0)
    for label, mask in [("positive", pos), ("zero_change", zero)]:
        coverage = np.sum(1 - fractions[4, mask], dtype="float64")
        record[f"{label}_control_cells"] = int(mask.sum())
        record[f"{label}_cellarea_new_fraction_covered"] = float(np.sum(fractions[0, mask], dtype="float64") / coverage) if coverage else None
    zero_rate = record["zero_change_cellarea_new_fraction_covered"]
    positive_rate = record["positive_cellarea_new_fraction_covered"]
    record["new_class_enrichment_positive_vs_zero"] = positive_rate / zero_rate if zero_rate else None
    return record, df


def process_city(unit_row):
    begin = time.perf_counter()
    unit = unit_row.unit_key
    out_json = WORK / "results" / f"glad_{unit}_summary.json"
    if out_json.exists():
        previous = json.loads(out_json.read_text(encoding="utf-8"))
        if previous.get("formula_version") == FORMULA_VERSION:
            return previous
    aligned = WORK / "datasets" / "glad_aligned" / f"{unit}_GLADv2_2015_2020_pair_fractions.tif"
    with rasterio.open(GHSL / f"{unit}.tif") as target:
        descriptions = target.descriptions
        idx15 = [i+1 for i, x in enumerate(descriptions) if x and "E2015" in x]
        idx20 = [i+1 for i, x in enumerate(descriptions) if x and "E2020" in x]
        if len(idx15) != 1 or len(idx20) != 1:
            raise RuntimeError(f"Missing or ambiguous epoch band descriptions for {unit}")
        old = target.read(idx15[0]).astype("int32")
        new = target.read(idx20[0]).astype("int32")
        ghsl_valid = (old != target.nodata) & (new != target.nodata)
        g_grid = np.maximum(new-old, 0)
        g_grid[~ghsl_valid] = 0
        bounds = transform_bounds(target.crs, "EPSG:4326", *target.bounds, densify_pts=41)
        if aligned.exists():
            with rasterio.open(aligned) as aligned_src:
                if aligned_src.count != 5 or aligned_src.shape != target.shape or not aligned_src.transform.almost_equals(target.transform) or aligned_src.crs != target.crs:
                    raise RuntimeError(f"Cached aligned geometry mismatch: {unit}")
                fractions = aligned_src.read()
            records = [json.loads(p.read_text(encoding="utf-8")) for p in RAW.glob(f"{unit}_*.json")]
            print(f"ALIGNED_REUSE {unit}; recomputing weights with {FORMULA_VERSION}", flush=True)
        else:
            a, b, native_transform, records = native_pair(unit, bounds)
            fractions = align_pair(a, b, native_transform, target)
            del a, b
        df = pd.read_parquet(CELLS / f"{unit}.parquet")
        rr, cc = df.grid_row.to_numpy(), df.grid_column.to_numpy()
        if not np.array_equal(g_grid[rr, cc], df.added_surface_m2.to_numpy()):
            raise RuntimeError(f"Published positive cells do not match two GHSL epochs: {unit}")
        if len(df) != np.count_nonzero(g_grid):
            raise RuntimeError(f"Published positive support differs from GHSL: {unit}")
        record, df = summarize(unit_row, df, fractions, ghsl_valid, g_grid)
        profile = target.profile.copy()
        profile.update(count=5, dtype="float32", nodata=np.nan)
        if not aligned.exists():
            with rasterio.open(aligned, "w", **profile) as dst:
                dst.write(fractions)
                for i, name in enumerate(CLASS_NAMES, 1):
                    dst.set_band_description(i, f"GLADv2_{name}_fraction")
                dst.update_tags(paired_support="native pair classification before average reprojection",
                                comparison_type="cross-product consistency; not ground truth", ghsl_source=str(GHSL / f"{unit}.tif"))
        df.to_parquet(WORK / "results" / "glad_cell_fractions" / f"{unit}.parquet", index=False, compression="zstd")
    record.update(native_windows=len(records), aligned_raster=str(aligned), formula_version=FORMULA_VERSION,
                  elapsed_seconds=round(time.perf_counter()-begin, 3), completed_utc=utcnow(),
                  source_manifests=[str(RAW / (Path(r["output_file"]).stem + ".json")) for r in records])
    out_json.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"CITY_DONE {unit} {unit_row.eFUA_name} gnew={record['g_covered_new_built_fraction']:.6f} jointnew={record['joint_covered_new_built_fraction']:.6f} sec={record['elapsed_seconds']}", flush=True)
    return record


def write_report(records, expected_n):
    frame = pd.DataFrame(records).sort_values("unit_key").reset_index(drop=True)
    frame.to_csv(WORK / "results" / "glad_city_summary.csv", index=False)
    # Read only completed-city records; another worker may be writing a new sidecar.
    manifest_paths = sorted({p for r in records for p in r["source_manifests"]})
    manifests = [json.loads(Path(p).read_text(encoding="utf-8")) for p in manifest_paths]
    (WORK / "results" / "glad_source_manifest.json").write_text(json.dumps(manifests, indent=2), encoding="utf-8")
    aggregate = dict(completed_cities=len(frame), expected_cities=expected_n, built_code=250, nodata_code=255, formula_version=FORMULA_VERSION,
                     class_order=CLASS_NAMES, date_utc=utcnow(), ghsl_added_surface_m2=float(frame.ghsl_added_surface_m2.sum()),
                     joint_screened_surface_m2=float(frame.joint_screened_surface_m2.sum()),
                     positive_cells=int(frame.positive_cells.sum()), raw_window_files=len(manifests),
                     raw_window_total_bytes=sum(x["bytes"] for x in manifests))
    for name in CLASS_NAMES[:4]:
        aggregate[f"g_covered_{name}_fraction"] = float(frame[f"g_allocated_{name}_m2"].sum()/frame.pair_covered_ghsl_g_m2.sum())
        aggregate[f"joint_covered_{name}_fraction"] = float(frame[f"joint_allocated_{name}_m2"].sum()/frame.pair_covered_joint_m2.sum())
    aggregate["pair_coverage_g_weighted"] = float(frame.pair_covered_ghsl_g_m2.sum()/frame.ghsl_added_surface_m2.sum())
    aggregate["city_g_new_fraction_quantiles"] = {str(q): float(frame.g_covered_new_built_fraction.quantile(q)) for q in [0,.1,.25,.5,.75,.9,1]}
    aggregate["city_joint_new_fraction_quantiles"] = {str(q): float(frame.joint_covered_new_built_fraction.quantile(q)) for q in [0,.1,.25,.5,.75,.9,1]}
    aggregate["cities_joint_new_greater_than_g_new"] = int((frame.joint_covered_new_built_fraction > frame.g_covered_new_built_fraction).sum())
    if "positive_pair_covered_cell_equivalents" in frame and frame.positive_pair_covered_cell_equivalents.notna().all():
        positive_rate = float(frame.positive_glad_new_class_area_m2.sum()/10000/frame.positive_pair_covered_cell_equivalents.sum())
        zero_rate = float(frame.zero_change_glad_new_class_area_m2.sum()/10000/frame.zero_change_pair_covered_cell_equivalents.sum())
        aggregate.update(positive_cellarea_new_fraction_covered=positive_rate,
                         zero_change_cellarea_new_fraction_covered=zero_rate,
                         pooled_new_class_enrichment_positive_vs_zero=positive_rate/zero_rate,
                         glad_new_class_fraction_in_positive_ghsl_cells=float(frame.positive_glad_new_class_area_m2.sum()/frame.glad_new_class_area_within_fua_m2.sum()),
                         raw_ghsl_negative_change_cells=int(frame.raw_ghsl_negative_change_cells.sum()))
    (WORK / "results" / "glad_aggregate_summary.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    table = frame[["unit_key", "eFUA_name", "positive_cells", "g_covered_new_built_fraction", "joint_covered_new_built_fraction", "g_covered_stable_built_fraction", "g_covered_absent_both_fraction", "g_covered_built_loss_fraction", "new_class_enrichment_positive_vs_zero"]].to_csv(index=False)
    report = f"""# GLAD paired-year cross-product consistency

Completed {len(frame)} of {expected_n} requested Indian functional urban areas. This is a comparison of different mapping products and definitions, not accuracy validation against ground truth.

## Design

- GLAD v2 annual land-cover maps for 2015 and 2020, native 0.00025-degree grid. Official legend confirms Built-up = 250 and No data = 255. Codes 251–253 are not annual-map gain classes.
- Pre-specified technical pilots: Delhi, Guwahati, Sultanpur; all 91 cities follow the identical procedure.
- Read-only city windows are extracted by HTTP byte ranges and saved unchanged as uint8 native rasters to F:. Each record lists source URL, HTTP ETag, pixel window, CRS, access time, SHA256, license and retrieval method. No full 10-degree tile is downloaded.
- At each native pixel, the 2015/2020 pair enters exactly one of: new built (non-built then built), stable built, absent both, built loss, missing pair. Each class indicator is average-reprojected to the exact GHSL 100 m grid; the five fractions sum to one. Missing coverage remains explicit. Fractions are reported conditional on valid pair coverage.
- GHSL g = max(B2020-B2015,0) is checked cell-by-cell against the released positive-cell database. Joint weight is g*s*(1-p), with s = endpoint_support_fraction = documented fraction times settlement fraction conditional on documentation, and p = preexisting_detected_fraction. s is not the conditional endpoint_settlement_fraction. This weight is a screen and does not establish temporal truth.
- GHSL-valid dual-epoch raster pixels define the study-unit area; these masks encode the FUA boundary. Area-weighted comparison of positive GHSL increment cells and g=0 controls is descriptive; the raw negative-change count is checked separately. Cells are spatially dependent and no iid significance test is claimed.

## Aggregate results

```json
{json.dumps(aggregate, indent=2)}
```

The numerical allocation in square metres is GHSL added building surface weighted by GLAD class fractions. It is not GLAD building surface and should not be interpreted as an accurate confirmed area. GLAD built-up includes buildings, roads and mixed pixels; GHSL is building surface. Shared Landsat and other mapping inputs mean strict statistical independence is not established. The public v2 page does not document the full 2015 training lineage. This limits the interpretation to agreement across mapping pipelines.

## City data

```csv
{table}
```

## Deliverables

- glad_city_summary.csv and glad_aggregate_summary.json: city and pooled descriptive results.
- glad_cell_fractions/*.parquet: released positive cells plus GLAD fractions and joint-screen weight, Zstandard compressed.
- datasets/glad_aligned/*pair_fractions.tif: five-band aligned fraction maps, exact GHSL geometry.
- glad_source_manifest.json: complete immutable raw-window provenance records.

Official download page: https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/download.html
Official legend: https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/legend.xlsx
Paper: Potapov et al. (2022), doi:10.3389/frsen.2022.856903. The 2022 paper describes the initial mapping pipeline; it does not fully document the v2 2015 update.
"""
    (WORK / "results" / "CROSS_PRODUCT_REPORT.md").write_text(report, encoding="utf-8")


def finalize_controls(records):
    """Add pooled control denominators using processed D: fractions, no new retrieval."""
    for record in records:
        unit = record["unit_key"]
        with rasterio.open(GHSL / f"{unit}.tif") as src:
            i15 = next(i+1 for i, d in enumerate(src.descriptions) if "E2015" in d)
            i20 = next(i+1 for i, d in enumerate(src.descriptions) if "E2020" in d)
            old, new = src.read(i15).astype("int32"), src.read(i20).astype("int32")
            valid = (old != src.nodata) & (new != src.nodata)
            positive, zero = valid & (new > old), valid & (new <= old)
            record["raw_ghsl_negative_change_cells"] = int((valid & (new < old)).sum())
        with rasterio.open(record["aligned_raster"]) as src:
            fraction_new, missing = src.read(1), src.read(5)
        for label, mask in [("positive", positive), ("zero_change", zero)]:
            record[f"{label}_pair_covered_cell_equivalents"] = float(np.sum(1-missing[mask], dtype="float64"))
            record[f"{label}_glad_new_class_area_m2"] = float(np.sum(fraction_new[mask], dtype="float64") * 10000)
        total_new = record["glad_new_class_area_within_fua_m2"]
        record["glad_new_class_fraction_in_positive_ghsl_cells"] = record["positive_glad_new_class_area_m2"]/total_new if total_new else None
        path = WORK / "results" / f"glad_{unit}_summary.json"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return records


def verify_outputs(records):
    """Audit completed outputs against their stored fields and immutable sources."""
    checks = []
    for record in records:
        unit = record["unit_key"]
        data = pd.read_parquet(WORK / "results" / "glad_cell_fractions" / f"{unit}.parquet")
        g = data.added_surface_m2.to_numpy(dtype="float64")
        expected_joint = g * data.endpoint_support_fraction.to_numpy(dtype="float64") * (1-data.preexisting_detected_fraction.to_numpy(dtype="float64"))
        stored_joint = data.joint_screened_surface_m2.to_numpy()
        joint_error = float(np.max(np.abs(expected_joint-stored_joint)))
        fractions = data[[f"glad_{x}_fraction" for x in CLASS_NAMES]].to_numpy(dtype="float64")
        partition_error = float(np.max(np.abs(fractions.sum(axis=1)-1)))
        numerator = float(np.dot(g, data.glad_new_built_fraction.to_numpy(dtype="float64")))
        g_new_error = abs(numerator-record["g_allocated_new_built_m2"])
        with rasterio.open(GHSL / f"{unit}.tif") as reference, rasterio.open(record["aligned_raster"]) as aligned:
            same_grid = reference.shape == aligned.shape and reference.crs == aligned.crs and reference.transform.almost_equals(aligned.transform)
        check = dict(unit_key=unit, positive_cells=len(data), joint_weight_max_absolute_error=joint_error,
                     fraction_partition_max_absolute_error=partition_error, g_new_numerator_absolute_error=g_new_error,
                     aligned_grid_matches_ghsl=same_grid, formula_version=record["formula_version"])
        check["passed"] = joint_error < 1e-8 and partition_error < 1e-5 and g_new_error < 1e-5 and same_grid and record["formula_version"] == FORMULA_VERSION
        checks.append(check)
    manifests = [json.loads(Path(p).read_text(encoding="utf-8")) for p in sorted({p for r in records for p in r["source_manifests"]})]
    raw_checks = []
    for rec in manifests:
        path = Path(rec["output_file"])
        raw_checks.append(dict(file=str(path), sha256_matches=sha256(path) == rec["sha256"],
                               readonly=not bool(path.stat().st_mode & stat.S_IWRITE),
                               byte_ranges_advertised=rec["source_header"]["accept-ranges"] == "bytes"))
    result = dict(completed_utc=utcnow(), script_sha256=sha256(Path(__file__)), invocation=sys.argv,
                  runtime=dict(python=platform.python_version(), rasterio=rasterio.__version__,
                               gdal=rasterio.__gdal_version__, numpy=np.__version__, pandas=pd.__version__, requests=requests.__version__),
                  formula_version=FORMULA_VERSION, city_checks=checks, raw_source_checks=raw_checks,
                  all_passed=all(x["passed"] for x in checks) and all(x["sha256_matches"] and x["readonly"] and x["byte_ranges_advertised"] for x in raw_checks),
                  interpretation="Internal computation/provenance audit, not mapping accuracy validation")
    (WORK / "results" / "glad_verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    if not result["all_passed"]:
        raise RuntimeError("GLAD output verification failed; consult glad_verification.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=["pilot", "all"], default="pilot")
    parser.add_argument("--workers", choices=[1, 2], type=int, default=1)
    args = parser.parse_args()
    for p in [RAW, WORK / "datasets" / "glad_aligned", WORK / "results" / "glad_cell_fractions"]:
        p.mkdir(parents=True, exist_ok=True)
    roster = pd.read_csv(ROSTER)
    roster = roster[roster.Cntry_ISO == "IND"]
    pilot = ["IND_FUA_09258", "IND_FUA_10496", "IND_FUA_07466"]
    keys = pilot if args.scope == "pilot" else pilot + [x for x in roster.unit_key if x not in pilot]
    records = []
    failures = []
    rows = [roster[roster.unit_key == unit].iloc[0] for unit in keys]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_city, row): row for row in rows}
        for future in as_completed(futures):
            row = futures[future]
            try:
                records.append(future.result())
                write_report(records, len(keys))
            except Exception as exc:
                failure = dict(unit_key=row.unit_key, eFUA_name=row.eFUA_name, error=str(exc), failed_utc=utcnow())
                failures.append(failure)
                (WORK / "results" / "glad_failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
                print(f"CITY_FAILED {json.dumps(failure)}", flush=True)
                if args.scope == "pilot":
                    raise
    if failures:
        raise RuntimeError(f"{len(failures)} city processing failures; consult glad_failures.json")
    records = finalize_controls(records)
    write_report(records, len(keys))
    verify_outputs(records)
    (WORK / "results" / "glad_failures.json").write_text("[]", encoding="utf-8")
    print(f"ALL_DONE {len(records)} cities", flush=True)


if __name__ == "__main__":
    main()
