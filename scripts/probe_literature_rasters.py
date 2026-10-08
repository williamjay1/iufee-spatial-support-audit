"""Read-only public raster access probes; no validation labels are produced."""
import json
import time
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

ENV = dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="1")
SOURCES = [
    ("GLAD_v2_2015", "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/2015/30N_090E.tif"),
    ("GLAD_v2_2020", "https://storage.googleapis.com/earthenginepartners-hansen/GLCLU2000-2020/v2/2020/30N_090E.tif"),
    ("IO_2020", "https://s3.us-west-2.amazonaws.com/io-10m-annual-lulc/46R_2020.tif"),
]
records = []
for name, url in SOURCES:
    start = time.perf_counter()
    rec = {"name": name, "url": url, "point_lon_lat": [91.75, 26.15]}
    try:
        with rasterio.Env(**ENV):
            with rasterio.open(url) as src:
                x, y = transform("EPSG:4326", src.crs, [91.75], [26.15])
                row, col = src.index(x[0], y[0])
                arr = src.read(1, window=Window(col, row, 32, 32))
                vals, counts = np.unique(arr, return_counts=True)
                rec.update(status="success", crs=str(src.crs), transform=list(src.transform), width=src.width, height=src.height, block_shapes=src.block_shapes, image_structure=src.tags(ns="IMAGE_STRUCTURE"), native_value_counts=dict(zip(vals.tolist(), counts.tolist())), sample_shape=list(arr.shape))
    except Exception as exc:
        rec.update(status="failed", error=str(exc))
    rec["elapsed_seconds"] = round(time.perf_counter() - start, 3)
    records.append(rec)
    print(json.dumps(rec), flush=True)

out = Path(r"D:\MLWork\IUFEE_revision_20261005\results\public_raster_access_probe.json")
out.write_text(json.dumps(records, indent=2), encoding="utf-8")
