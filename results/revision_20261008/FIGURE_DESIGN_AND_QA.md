# Figure design and verification, 8 October 2026

All five scientific figures were rebuilt from the recorded analysis outputs with the GitHub SciencePlots `science` and `nature` styles, the local figure skill, and a common Arial family. The design follows the Nature artwork principles of editable vector output, simple axis frames, compact white-space gutters, restrained colour, bold lowercase panel labels, and readable type. The target manuscript remains an IEEE letter; its figure numbering and captions are controlled by the manuscript editor.

| Output stem | Intended role | Native size | Minimum font | PDF raster images |
| --- | --- | --- | --- | --- |
| figure_1_frame | Main, study frame and source periods | 180 × 58 mm | 7 pt | 0 |
| figure_4_representation | Main, controlled representation comparison | 180 × 95 mm | 7 pt | 0 |
| figure_5_glad | Main, paired GLAD evidence | 180 × 58 mm | 7 pt | 0 |
| figure_2_cases | Supplement, three city examples | 180 × 60 mm | 7 pt | 0 |
| figure_3_case_maps | Supplement, native cell maps | 180 × 169 mm | 7 pt | 0 |

Every output has a PDF, an editable SVG with text retained as text, and a PNG exported at 1000 dpi. PDF fonts are embedded TrueType. The PNG density read from the file is 999.998 dpi because PNG stores resolution as integer pixels per metre. Vector files have no fixed raster resolution. At a 171 mm manuscript width, the 7 pt native text becomes approximately 6.65 pt; the compiled pages need to be checked at that actual placement by the main editor.

The representation figure uses distinct colours for support share and conditional depth. Numbers are outside the bars, with clear offsets from the zero line. The GLAD allocation panel keeps all recorded classes and uses no in-bar numbers. Its retention panel combines differing marker shapes and line styles, and its city scatter uses a clearly separated equality line. The case figure places conditional interval labels above the corresponding marks, avoiding a previous white annotation box that could obscure a circular data mark. The native cell maps use one shared colour scale per column to prevent label and colourbar congestion. The maps draw original 100 m cells as vector polygons without interpolation, smoothing, upsampling, or alteration of the measurement fields.

## Official boundary and Kashmir region symbols

The national boundaries and coastlines are the original line and Bézier paths recovered from the Chinese Ministry of Natural Resources standard map GS(2023)2761. The 106 land, 35 national-boundary and 12 coastline records remain exactly equal to the saved pre-correction records. The omitted Kashmir regional boundary (official drawing 1914) and military demarcation (official drawing 1913, items 14:54) have been restored as separate layers. The regional boundary retains the official dash pattern. The ceasefire representation retains all 40 independent short strokes forming the official crossed symbols; no continuous centreline or new national boundary was added. Kashmir region is labelled outside the map, and the two line categories are shown in the legend. Land fill is uniformly neutral. The 91 study locations use the existing registered positions. No substitute boundary, raster tracing, geometry smoothing, or new registration was introduced.

The reusable boundary JSON SHA256 is now `0a4e7fc724acdd01e16023ed114eb437dd9c478ca12c96486bfe8e8566e55a1c`, reflecting the two restored line categories and their explicit semantics. The source approval number identifies the official parent map. It does not assert separate official review of the research overlay. The map figure audit contains the current figure PDF hash, its current placement rectangle, and the Kashmir correction record.

## Completed checks

The script checks figure dimensions, font settings, every rendered text bounding box, text-to-text collisions, off-canvas text, PDF embedded-image objects, input hashes, and output hashes. Matplotlib ticks outside an axis range and all hidden map axes are excluded because they are not actually drawn. All five figures have zero rendered text-box collisions, no off-canvas text, and no embedded raster objects. Source-file hashes and every output hash are in `FIGURE_DESIGN_AND_QA.json`.

Actual preview images were opened and inspected after rendering. The main comparison and GLAD figures were inspected at the 180 dpi physical-size preview. The study map was inspected again after moving the Sultanpur label fully outside the map and correcting the truncated history arrow. The three-city figure was inspected after raising its interval labels. The nine-panel native cell maps were inspected after replacing individual colourbars with shared column scales. No clipping, text collision, leader line crossing through words, or unresolved annotation obstruction was seen. The ten-cell review markers remain source-derived markers and are allowed to coincide where the original cells are close.

The scientific quantities, experimental design, city selections, interval endpoints, and conclusions were retained. All plotting code is in `scripts/plot_nature_20261008.py`. Reproduction uses the dedicated scifig interpreter and the already installed, ABI-compatible GIS and parquet packages from the established analysis interpreter; no package installation or source-data mutation was required.

## Primary design references

- SciencePlots original repository: https://github.com/garrettj403/SciencePlots
- Nature initial-submission artwork guidance: https://www.nature.com/nature/for-authors/initial-submission
- Nature final-submission artwork guidance: https://www.nature.com/nature/for-authors/final-submission

Standalone figure verification: PASS. Manuscript-placement verification is owned by the main editor and must use the final compiled letter and supplement.

<!-- KASHMIR_VISUAL_REVIEW_20261008 -->
## Kashmir correction: completed placement review

The root agent inspected the official cropped Kashmir source, the corrected Figure 1 preview, and all five recompiled main pages. The Kashmir region label and its leader are outside the dense city cluster. The regional dashed sample and ceasefire crossed sample match their respective official map symbols. No clipping, text overlap, or leader crossing through words was observed. The one caption addition identifies these restored source geometries; all other manuscript text is exactly unchanged. Main page count remains five, and the four other PDFs are byte-identical to the earlier completed delivery. The original three geographic layers passed a separate read-only audit. See KASHMIR_MAP_CORRECTION.json and CITATION_CHECK_AFTER_MAP.json for the current-file checks.

<!-- MAP_LABEL_WHITE_SPACE_20261008 -->
## External labels and longer leaders

Delhi, Sultanpur and Kashmir region are placed in the left white margin; Guwahati and China are in the right white margin. Labels have transparent backgrounds and therefore do not mask geography. Every rendered text box is 2.5 pt outside the map frame, also verified against actual PDF word coordinates (all gaps at least 2 pt). Leader lengths are 24.04 to 51.87 pt and no leader intersects another text box. The source-period panel was repositioned to preserve white space, with its fields and data unchanged. All five recompiled main pages were visually inspected, and a separate read-only auditor checked the current main-page figure. Main TEX is byte-identical to the pre-label-adjustment backup; map geometry, 91 registered study points, scientific fields and other four figures are unchanged.
