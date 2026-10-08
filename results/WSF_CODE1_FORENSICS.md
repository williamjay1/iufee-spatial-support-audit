# WSF2019 native value-1 forensics

Read-only inspection of two preselected source tiles; no original TIFF was copied, changed, moved or deleted.

Complete native counts and source SHA256 match the prior audit: True. Total neighbourhood samples: 5000 (maximum 5000).

## WSF2019_v1_78_16

Native code1 pixels: 21178; pixel fraction 0.00418777%. nodata=None; mask flags=[['all_valid']]; sampled mask values={255: 3500}. Palette present: False.

Code1-bearing native blocks: 450 of 1936. Within tile edge distances (pixels): {'0': 1, '1': 1, '5': 1, '10': 1, '100': 1}. Within 512-pixel block edge distances: {'0': 189, '1': 361, '2': 513, '5': 1062}.

Eight-neighbour counts from 3500 sampled native code1 centres: {0: 10750, 1: 11329, 255: 5921}; fractions: {'0': 0.38392857142857145, '1': 0.40460714285714283, '255': 0.21146428571428572}. Neighbourhood case counts: {'any_255': 2238, 'any_0': 2893, 'any_1': 3158, 'all_0': 83, 'all_255': 12}.

Existing overview factors: [2, 4, 8, 16, 32]. Native value1 already exists before any downstream rendering or reprojection. Full metadata and coarsest overview read are in the JSON.

## WSF2019_v1_70_22

Native code1 pixels: 4450; pixel fraction 0.00087999%. nodata=None; mask flags=[['all_valid']]; sampled mask values={255: 1500}. Palette present: False.

Code1-bearing native blocks: 245 of 1936. Within tile edge distances (pixels): {'0': 0, '1': 1, '5': 5, '10': 8, '100': 230}. Within 512-pixel block edge distances: {'0': 28, '1': 64, '2': 97, '5': 217}.

Eight-neighbour counts from 1500 sampled native code1 centres: {1: 3439, 255: 3866, 0: 4695}; fractions: {'0': 0.39125, '1': 0.28658333333333336, '255': 0.32216666666666666}. Neighbourhood case counts: {'any_255': 1189, 'any_0': 1273, 'any_1': 1246, 'all_0': 37, 'all_255': 16}.

Existing overview factors: [2, 4, 8, 16, 32]. Native value1 already exists before any downstream rendering or reprojection. Full metadata and coarsest overview read are in the JSON.

## Interpretation

Value 1 is present in native source pixels, so it is not solely a downstream overview/display/resampling artifact. Source TIFF masks treat the sampled value-1 pixels as valid; nodata=None does not exclude them. SHA256 and complete native histograms are checked against the prior source audit.

No TIFF metadata, mask, palette or local neighbourhood pattern identifies the true semantic class or the source-generation mechanism of code 1. Validity in a raster mask is not semantic validity.

Retain code 1 as undocumented; exclude it from documented-class support and disclose uncertainty. Do not recode it to settlement or non-settlement based on this inspection.

Elapsed 5.451 seconds. Spatial concentration and neighbour composition are descriptive checks and do not establish how code1 was generated.