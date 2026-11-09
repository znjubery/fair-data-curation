# 02 · Other common data-organization formats

Our numbered lab layout (`00_docs … 05_code, 99_review`) is one choice. Other communities use their own. Knowing them helps you read other people's data and package ours for their tools.

> **Analogy: shipping containers.** Every port uses the same container size, so any crane can lift any box. Each format below is a "container standard" agreed on by one community.

## A. Folder layouts

| Layout | Community | Top-level idea | When to use it here |
|---|---|---|---|
| **Our lab layout** | Baskar Lab | numbered pipeline stages: docs → metadata → raw → processed → results → code | default for every lab project |
| **Cookiecutter Data Science** | data science / ML | `data/raw, data/interim, data/processed, notebooks, src, models, reports` | ML projects with many notebooks |
| **BIDS** | neuroimaging | strict names: `sub-01/ses-01/anat/sub-01_ses-01_T1w.nii` + JSON sidecar per file | as a model: one sidecar JSON per image works well for hyperspectral and turntable scans |
| **ISA-Tab** | life sciences (MIAPPE uses it) | three tables: Investigation → Study → Assay | when a repository asks for MIAPPE in ISA-Tab |
| **Hugging Face dataset** | ML | `train/ val/ test/` (or a loading script) + `README.md` dataset card | releasing an ML benchmark |

Side by side, for the same LiDAR project:

```
OUR LAB LAYOUT                    COOKIECUTTER DATA SCIENCE       HUGGING FACE DATASET
maize-lidar-2025/                 maize-lidar-2025/               maize-lidar-2025/
  README.md                         README.md                       README.md   (dataset card)
  00_docs/                          references/                     data/
  01_metadata/                      data/external/                    train-*.parquet
  02_raw/01_2025-07-14/             data/raw/                         test-*.parquet
  03_processed/                     data/interim/                   croissant.json (auto)
  04_results/                       data/processed/
  05_code/                          src/  notebooks/  models/
  99_review/                        reports/figures/
```

**Mapping:** `02_raw` = `data/raw`; `03_processed` = `data/interim` + `data/processed`; `04_results` = `reports` + `models`; `05_code` = `src` + `notebooks`.

## B. Packaging formats (a folder + a description of it)

| Format | What it adds | File | Good for |
|---|---|---|---|
| **BagIt** | checksums for every file, so a transfer can be verified | `bagit.txt`, `manifest-sha256.txt`, `data/` | moving TB of data to Box, Globus, NRP; archives |
| **RO-Crate** | JSON-LD description of files, people, software, and how they connect | `ro-crate-metadata.json` | packaging data + code + workflow together; Zenodo/WorkflowHub |
| **Frictionless Data Package** | table schemas (column types, units, missing-value codes) | `datapackage.json` | CSV trait tables that must validate automatically |
| **Croissant** | ML view of a dataset: files, record fields, splits, Responsible-AI notes | `croissant.json` | any ML dataset; required by NeurIPS dataset submissions |

They stack. A release can be a **BagIt** bag whose `data/` folder holds our lab layout, with a `croissant.json` and an `ro-crate-metadata.json` inside.

## C. Metadata standards (what the description says)

| Standard | Describes | Notes |
|---|---|---|
| **MIAPPE** | plant phenotyping experiments | checklist at <https://github.com/MIAPPE/MIAPPE> |
| **MIxS** | soil and microbiome samples | needed for NCBI BioSample submission |
| **DataCite** | citation: creators, title, year, publisher, DOI | what every DOI repository asks for |
| **Darwin Core** | species occurrences, specimens | field surveys, insects, weeds |
| **DCAT / schema.org Dataset** | catalog entries | how Google Dataset Search finds data |
| **PROV-O** | provenance (what produced what) | used by large data commons for lineage |

## D. Documentation formats (for people)

| Format | Key questions it answers |
|---|---|
| **README** (our template) | what, who, where, when, how, license, how to cite |
| **Datasheets for Datasets** (Gebru et al.) | motivation, composition, collection, preprocessing, uses, distribution, maintenance |
| **Data card / dataset card** (Hugging Face, Google) | short version of a datasheet at the top of the dataset page |

## E. File formats by data type

| Data | Open format | Must travel with it |
|---|---|---|
| UAV RGB / multispectral | GeoTIFF, JPG/TIFF with EXIF | calibration panel, flight log, CRS |
| LiDAR / SfM points | LAS/LAZ (COPC for cloud viewing) | CRS (EPSG) in header, software version |
| NeRF / 3DGS | PLY + `transforms.json` | camera poses, training settings, commit |
| Meshes | PLY / OBJ / glTF | units, scale, coordinate frame |
| Hyperspectral | ENVI `.hdr`+`.bil`, or HDF5/Zarr | wavelengths, white/dark references |
| Large arrays, time series | Zarr, HDF5, NetCDF | dimension names and units |
| Tables | CSV (small), Parquet (large) | data dictionary with units + ontology IDs |
| Genotypes | VCF (`.vcf.gz`), HapMap | reference genome version (e.g., B73 v5) |
| Sequence reads | FASTQ (deposit at NCBI SRA) | BioSample + MIxS |
| Geospatial vectors | GeoPackage, GeoJSON (avoid shapefile for new work) | CRS |
| Images for ML | PNG/JPG + COCO or YOLO labels | label schema, split lists |

## Which one should I use?

1. **Inside the lab:** our numbered layout + README + `01_metadata/`.
2. **Sharing a big transfer:** wrap it as a **BagIt** bag.
3. **Publishing for ML:** add **Croissant** (+ RAI fields) and a dataset card.
4. **Publishing for plant science:** add **MIAPPE**; soil/microbe data adds **MIxS**.
5. **Data + code + workflow together:** **RO-Crate**.
