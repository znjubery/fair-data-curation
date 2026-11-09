# 03 · Data organization examples

Three worked examples from the kinds of data our group collects. Each shows **before → after**, the key metadata files, and the practices it uses. IDs, dates and counts are illustrative.

---

## Example 1: UAV-LiDAR + RGB maize field season (one site, many flights)

**Before**

```
LiDAR stuff/
  final_v3_REAL.laz
  cloud merged FINAL.las
  DJI_0001.JPG … DJI_2400.JPG
  plot map FINAL.xlsx
  heights.csv            <- no units, plot IDs like "3-12"
```

**After**

```
2025_AEA_maize-uav-lidar/
  README.md
  00_docs/
    flight_protocol.md
  01_metadata/
    ids.csv                      plot IDs + genotype + GRIN/G2F IDs
    plot_map.gpkg                plot polygons, EPSG:26915
    capture_log.csv              one row per flight (altitude, overlap, sensor, RTK base, weather)
    data_dictionary.csv          column, unit, ontology_id, value_type
    links.csv                    UAV ↔ LiDAR ↔ ground-truth pairs (direct, ±2 days)
    miappe.tsv
    croissant.json
    provenance.json
    MANIFEST.sha256
  02_raw/                        read-only
    01_2025-06-20/
      lidar/20250620_AEA_L1_f01.laz
      rgb/20250620_AEA_P1_0001.jpg …
      calib/20250620_AEA_panel.jpg
    02_2025-07-14/ …
  03_processed/
    01_2025-06-20/
      20250620_AEA_lidar_merged_v1.laz
      20250620_AEA_ortho_v1.tif
  04_results/
    plot_traits_v1.parquet       plot_id, date, PH_cm, LAI, value_type
  05_code/
    height_extraction.py         (git commit in provenance.json)
  99_review/
    possible_duplicates/
```

**Methods used:** stable plot IDs, Crop Ontology trait IDs, MIAPPE + Croissant, `value_type = derived` for heights, direct links between same-plot flights, CRS stated, duplicate check.

---

## Example 2: Hyperspectral maize ear turntable scans (lab, many ears)

**Before**

```
hyperspec/
  scan1.bil  scan1.hdr
  scan1.bil
  white.bil  dark.bil
  ear_list.xlsx        <- ear numbers typed by hand
```

**After**

```
2026_LAB_maize-ear-hyperspectral/
  README.md
  01_metadata/
    ids.csv                       ear_id → plot_id → genotype
    data_dictionary.csv
    sidecar_schema.md             what each per-scan JSON holds
    croissant.json
  02_raw/
    01_2026-09-10/
      E0001/
        E0001_20260910_view000.hdr
        E0001_20260910_view000.bil
        E0001_20260910_view000.json   <- sidecar: angle, exposure, lamp, wavelengths file
        …view015.*
      _refs/
        20260910_white.hdr/.bil
        20260910_dark.hdr/.bil
  03_processed/
    reflectance/E0001_20260910_view000_refl.zarr
    kernels_seg/E0001_masks_v1.png
  04_results/
    ear_traits_v1.csv             ear_id, kernel_rows, length_mm, mean_NDVI-like indices
  05_code/
```

**Ideas borrowed:** the **BIDS sidecar** (one small JSON per scan), and **Zarr** for large reflectance cubes. White/dark references live **with the session** they calibrate. Ear → plot → genotype is a **contextual** link to the field data.

---

## Example 3: Greenhouse roots + field plots + genotypes (multi-scale, for ML)

**Before:** three students, three folders, three ID schemes (`B73-rep2`, `pot17`, `2026_AEA_R03_C12`).

**After**

```
2026_maize-roots-to-field/
  README.md
  01_metadata/
    ids.csv                genotype_id, GRIN/G2F ID, greenhouse pot IDs, field plot IDs
    links.csv              greenhouse pot ↔ field plot = contextual (same genotype)
                           root scan ↔ rhizosphere sample = direct (same pot, same day)
    data_dictionary.csv
    croissant.json         includes RAI fields (limitations, intended use)
  02_raw/
    greenhouse/01_2026-03-02/ …
    field/01_2026-06-20/ …
    genotypes/maize_panel_B73v5.vcf.gz       (Tier 1: embargoed until publication)
  03_processed/
  04_results/
  splits/
    README.md              rule: no test genotype > 0.25 kinship to training; leave-season-out
    train_ids.txt  val_ids.txt  test_ids.txt
  05_code/
```

**Methods used:** ID backbone across scales, typed links with confidence, leakage-resistant splits, access tiers (genotypes embargoed, metadata open).

---

## Pattern to remember

```
ID first  →  raw is read-only  →  every derived file names its source and code  →  links say how strong  →  release = version + checksums + DOI
```
