# IUFEE spatial support audit: revision analysis code and derived results

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23243829.svg)](https://doi.org/10.5281/zenodo.23243829)


Reproducibility package for the study **Spatial Support Assumptions in Urban Change Exposure:
An Audit of 91 Indian Cities**. The study asks what is lost when a database stores separate
class fractions for each grid cell but discards the locations at which those classes coincide.
It compares a joint settlement overlay (J) with multiplication of its marginal fractions (F) and
with the archived product convention (A), holding source maps, registration, positive 2015 to 2020
building surface differences, hazard depths and target cells fixed across 91 Indian functional
urban areas and 1,259,886 grid cells.

## Contents

| Path | Content |
|---|---|
| scripts/ | Python analysis code: joint overlay baseline, GLAD cross-product comparison, sensitivity and hazard alternatives, diagnostics and decompositions, figure production |
| results/ | Derived tabular and numerical outputs: pooled and city summaries, per-cell J/F contributions (results/revision_20261007/diagnostics_cell_contributions.parquet), paired GLAD cell fractions (results/glad_cell_fractions/*.parquet), sensitivity tables, review-queue coverage and selected source review cells |

## Deliberately not redistributed

- **Parent products.** GHSL GHS-BUILT-S R2023A, GHS-FUA R2019A, WSF Evolution, WSF 2019,
  GLAD GLCLU v2 and GloFAS Flood Hazard v2.1.2 remain with their providers under their own terms;
  the scripts document the products used and the registration applied.
- **Official map geometry.** The study frame figure follows the Chinese official standard map
  GS(2023)2761. Its derived vector paths are not redistributed here.
- **Intermediate rasters and manuscript files** (submitted manuscript, figures, review
  correspondence) are outside this release.

## Environment

Python 3.12 with numpy, pandas, rasterio, pyproj, pyarrow, matplotlib and PyMuPDF.
Analyses are deterministic: no random seeds are used for the reported results.

## Reproduction entry points

1. scripts/joint_overlay_baseline.py - joint versus marginal overlay on the nested 10 m grid.
2. scripts/glad_cross_product.py - paired GLAD class allocation, composition and retention.
3. scripts/revision_sensitivity.py - weighting, threshold, hazard and QA alternatives.
4. scripts/plot_revision.py and scripts/plot_diagnostics_20261007.py - figure production.
5. Scripts named audit_* and finalize_* record the verification steps applied to the outputs.

Absolute paths inside the scripts reflect the original analysis machine; adapt the input roots
before rerunning.

## Data release cited by the manuscript

India Urban Flood Exposure Evidence (IUFEE) v1.2, Zenodo, doi:10.5281/zenodo.21916290
(concept doi:10.5281/zenodo.21916289).

## Licence

Code: MIT (LICENSE). Derived data and documentation: CC BY 4.0 (LICENSE-DATA).

## Citation

Zeng, Z., Tian, Y., and Zhang, J. (2026). *IUFEE spatial support audit: revision analysis code and derived results* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23243829

Concept DOI for all versions: https://doi.org/10.5281/zenodo.23243828
