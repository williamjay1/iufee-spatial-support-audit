"""Read-only native-pixel forensics for undocumented WSF2019 value 1.

No semantic recoding is performed. Spatial patterns do not determine a class.
Two preselected tiles, a maximum of 5000 neighbourhood samples in total.
"""
from __future__ import annotations
import hashlib
import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

ROOT = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\raw\wsf_evidence\WSF_2019")
AUDIT = Path(r"E:\science\India_Flood_Remote_Sensing_IEEE\data\derived\iufee_v1\source_plan\wsf_source_semantic_audit.csv")
OUT = Path(r"D:\MLWork\IUFEE_revision_20261005\results")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for part in iter(lambda: stream.read(1048576), b""):
            h.update(part)
    return h.hexdigest().upper()


def inspect_tile(row, cap):
    start = time.perf_counter()
    path = ROOT / f"{row.item_id}.tif"
    digest = sha256(path)
    old_counts = {int(k): int(v) for k, v in json.loads(row.native_value_counts_json).items()}
    counts = np.zeros(256, dtype="int64")
    coords = []
    block_counts = []
    with rasterio.open(path, "r") as src:
        namespaces = src.tag_namespaces()
        tags = {ns: src.tags(ns=ns) for ns in namespaces}
        tags["default"] = src.tags()
        try:
            palette = src.colormap(1)
            palette_info = dict(present=True, entries=len(palette), selected={str(v): palette.get(v) for v in [0, 1, 255]})
        except ValueError as exc:
            palette_info = dict(present=False, error=str(exc))
        print(f"NATIVE_SCAN_START {row.item_id} shape={src.shape}", flush=True)
        for (block_row, block_col), window in src.block_windows(1):
            arr = src.read(1, window=window)
            counts += np.bincount(arr.ravel(), minlength=256)
            yy, xx = np.nonzero(arr == 1)
            if len(yy):
                coords.append(np.column_stack([yy + int(window.row_off), xx + int(window.col_off)]))
                block_counts.append(dict(block_row=block_row, block_col=block_col, code1_count=len(yy)))
        positions = np.concatenate(coords, axis=0) if coords else np.empty((0, 2), dtype="int64")
        native_counts = {int(i): int(counts[i]) for i in np.flatnonzero(counts)}
        n = len(positions)
        edge = np.minimum.reduce([positions[:, 0], positions[:, 1], src.height-1-positions[:, 0], src.width-1-positions[:, 1]])
        bh, bw = src.block_shapes[0]
        block_edge = np.minimum.reduce([positions[:, 0] % bh, positions[:, 1] % bw,
                                        bh-1-positions[:, 0] % bh, bw-1-positions[:, 1] % bw])
        sample_idx = np.random.default_rng(20261005).choice(n, size=min(n, cap), replace=False)
        sample = positions[sample_idx]
        grouped = defaultdict(list)
        for y, x in sample:
            grouped[(int(y // bh), int(x // bw))].append((int(y), int(x)))
        neighbours = Counter()
        sample_masks = Counter()
        sample_center_values = Counter()
        neighbourhood_cases = Counter()
        examples = []
        for (br, bc), points in grouped.items():
            r0, c0 = max(0, br*bh-1), max(0, bc*bw-1)
            r1, c1 = min(src.height, (br+1)*bh+1), min(src.width, (bc+1)*bw+1)
            win = Window(c0, r0, c1-c0, r1-r0)
            arr = src.read(1, window=win)
            masks = src.read_masks(1, window=win)
            for y, x in points:
                sample_masks[int(masks[y-r0, x-c0])] += 1
                sample_center_values[int(arr[y-r0, x-c0])] += 1
                vals = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        if 0 <= y+dy < src.height and 0 <= x+dx < src.width:
                            vals.append(int(arr[y+dy-r0, x+dx-c0]))
                neighbours.update(vals)
                neighbourhood_cases["any_255"] += int(255 in vals)
                neighbourhood_cases["any_0"] += int(0 in vals)
                neighbourhood_cases["any_1"] += int(1 in vals)
                neighbourhood_cases["all_0"] += int(bool(vals) and all(v == 0 for v in vals))
                neighbourhood_cases["all_255"] += int(bool(vals) and all(v == 255 for v in vals))
                if len(examples) < 12:
                    lon, lat = src.xy(y, x)
                    examples.append(dict(native_row=y, native_column=x, lon=lon, lat=lat,
                                         mask=int(masks[y-r0, x-c0]), neighbours=vals))
        overview_factor = src.overviews(1)[-1] if src.overviews(1) else None
        overview_info = None
        if overview_factor:
            overview = src.read(1, out_shape=(max(1,round(src.height/overview_factor)), max(1,round(src.width/overview_factor))), resampling=Resampling.nearest)
            h = np.bincount(overview.ravel(), minlength=256)
            overview_info = dict(requested_factor=overview_factor, out_shape=list(overview.shape),
                                 values={str(i): int(h[i]) for i in np.flatnonzero(h)},
                                 note="Nearest read at existing coarsest overview scale; not a substitute for the native scan")
        total_blocks = sum(1 for _ in src.block_windows(1))
        result = dict(item_id=row.item_id, source_path=str(path), source_size_bytes=path.stat().st_size,
                      source_sha256=digest, old_audit_sha256=row.source_sha256,
                      sha256_matches_old_audit=digest == row.source_sha256.upper(),
                      native_shape=list(src.shape), native_dtype=src.dtypes[0], native_crs=str(src.crs),
                      native_transform=list(src.transform), native_nodata=src.nodata,
                      color_interpretation=[x.name for x in src.colorinterp], color_table=palette_info,
                      mask_flags=[[x.name for x in band] for band in src.mask_flag_enums],
                      tags_by_namespace=tags, overviews=src.overviews(1), coarsest_overview_check=overview_info,
                      metadata_note="DERIVED_SUBDATASETS is a GDAL-advertised virtual derived view and is not evidence of original WSF generation provenance",
                      native_counts={str(k): v for k, v in native_counts.items()},
                      old_audit_counts={str(k): v for k, v in old_counts.items()},
                      native_counts_match_old_audit=native_counts == old_counts,
                      code1_count_native=n, code1_pixel_fraction=n/(src.width*src.height),
                      code1_native_row_min=int(positions[:,0].min()), code1_native_row_max=int(positions[:,0].max()),
                      code1_native_column_min=int(positions[:,1].min()), code1_native_column_max=int(positions[:,1].max()),
                      code1_pixels_within_tile_edge={str(distance): int((edge <= distance).sum()) for distance in [0,1,5,10,100]},
                      code1_pixels_within_native_block_edge={str(distance): int((block_edge <= distance).sum()) for distance in [0,1,2,5]},
                      total_native_blocks=total_blocks, native_blocks_containing_code1=len(block_counts),
                      top_native_blocks_by_code1=sorted(block_counts, key=lambda x: x["code1_count"], reverse=True)[:20],
                      neighbour_sample_count=len(sample), sample_selection="fixed-seed simple random without replacement from all native code1 positions",
                      sample_code1_center_value_counts=dict(sample_center_values), sample_mask_counts=dict(sample_masks),
                      neighbour_counts=dict(neighbours), neighbour_total=sum(neighbours.values()),
                      neighbour_fractions={str(k): v/sum(neighbours.values()) for k, v in sorted(neighbours.items())},
                      neighbourhood_case_counts=dict(neighbourhood_cases), examples=examples,
                      elapsed_seconds=round(time.perf_counter()-start,3))
    print(f"NATIVE_SCAN_DONE {row.item_id} code1={n} sample={len(sample)} elapsed={result['elapsed_seconds']}", flush=True)
    return result


def main():
    begin = time.perf_counter()
    audit = pd.read_csv(AUDIT)
    audit = audit[audit.collection_id == "WSF_2019"]
    highest = audit.sort_values("undocumented_value_1_pixel_count", ascending=False).iloc[0]
    first = audit[audit.item_id == "WSF2019_v1_70_22"].iloc[0]
    results = [inspect_tile(highest, 3500), inspect_tile(first, 1500)]
    matched = all(x["sha256_matches_old_audit"] and x["native_counts_match_old_audit"] for x in results)
    output = dict(completed_utc=datetime.now(timezone.utc).isoformat(), selection="highest old-audit native code1 count plus the original first inspected 70_22 tile",
                  source_audit=str(AUDIT), source_audit_sha256=sha256(AUDIT), tiles_checked=2,
                  native_counting="full native block scan, no reprojection or resampling", sample_total=sum(x["neighbour_sample_count"] for x in results),
                  no_raw_copies_or_modifications=True, prior_audit_confirmed=matched, results=results,
                  interpretation={
                      "established":"Value 1 is present in native source pixels, so it is not solely a downstream overview/display/resampling artifact. Source TIFF masks treat the sampled value-1 pixels as valid; nodata=None does not exclude them. SHA256 and complete native histograms are checked against the prior source audit.",
                      "not_established":"No TIFF metadata, mask, palette or local neighbourhood pattern identifies the true semantic class or the source-generation mechanism of code 1. Validity in a raster mask is not semantic validity.",
                      "recommended_handling":"Retain code 1 as undocumented; exclude it from documented-class support and disclose uncertainty. Do not recode it to settlement or non-settlement based on this inspection."},
                  elapsed_seconds=round(time.perf_counter()-begin,3))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "WSF_CODE1_FORENSICS.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
    paragraphs = ["# WSF2019 native value-1 forensics", "", "Read-only inspection of two preselected source tiles; no original TIFF was copied, changed, moved or deleted.", "",
                  f"Complete native counts and source SHA256 match the prior audit: {matched}. Total neighbourhood samples: {output['sample_total']} (maximum 5000).", ""]
    for r in results:
        paragraphs += [f"## {r['item_id']}", "", f"Native code1 pixels: {r['code1_count_native']}; pixel fraction {r['code1_pixel_fraction']:.8%}. nodata={r['native_nodata']}; mask flags={r['mask_flags']}; sampled mask values={r['sample_mask_counts']}. Palette present: {r['color_table']['present']}.", "",
                       f"Code1-bearing native blocks: {r['native_blocks_containing_code1']} of {r['total_native_blocks']}. Within tile edge distances (pixels): {r['code1_pixels_within_tile_edge']}. Within 512-pixel block edge distances: {r['code1_pixels_within_native_block_edge']}.", "",
                       f"Eight-neighbour counts from {r['neighbour_sample_count']} sampled native code1 centres: {r['neighbour_counts']}; fractions: {r['neighbour_fractions']}. Neighbourhood case counts: {r['neighbourhood_case_counts']}.", "",
                       f"Existing overview factors: {r['overviews']}. Native value1 already exists before any downstream rendering or reprojection. Full metadata and coarsest overview read are in the JSON.", ""]
    paragraphs += ["## Interpretation", "", output["interpretation"]["established"], "", output["interpretation"]["not_established"], "", output["interpretation"]["recommended_handling"], "", f"Elapsed {output['elapsed_seconds']} seconds. Spatial concentration and neighbour composition are descriptive checks and do not establish how code1 was generated."]
    (OUT / "WSF_CODE1_FORENSICS.md").write_text("\n".join(paragraphs),encoding="utf-8")
    if not matched:
        raise RuntimeError("Source identity or native counts differ from the prior audit")
    print(f"FORENSICS_DONE prior_audit_confirmed={matched} elapsed={output['elapsed_seconds']}",flush=True)


if __name__ == "__main__":
    main()
