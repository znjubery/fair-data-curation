# 06 · Our six student datasets: layout and minimum metadata

**Idea:** fill **one study card** (`templates/study_card.yaml`, about 20 fields) and **one data dictionary** per dataset. Every other format (README, MIAPPE, Croissant, DataCite/DOI form, dataset card) is generated or copied from those two files. You never type the same fact twice.

> **Analogy: a passport.** You give your details once at the passport office; airlines, hotels and border control all read the same page. The study card is the passport; README, MIAPPE and Croissant are the places that read it.

**One-line version:** *collect ~20 facts once on the day, and every format can be built from them later; miss them on the day and no tool can recover them.*

---

## 1. The minimum core (every dataset)

| # | Field | Example | README | MIAPPE | Croissant | DOI form |
|---|---|---|:-:|:-:|:-:|:-:|
| 1 | Title | Maize tassel UAV images and 3D reconstructions, Ames 2026 | ✓ | ✓ | ✓ | ✓ |
| 2 | Short description (3–4 sentences) | what, where, when, how many | ✓ | ✓ | ✓ | ✓ |
| 3 | Steward (name, email, ORCID) | | ✓ | ✓ | ✓ | ✓ |
| 4 | Owner / PI | | ✓ | ✓ | ✓ | ✓ |
| 5 | Funding (agency + award no.) | NSF ... | ✓ | | ✓ | ✓ |
| 6 | Dates (start, end, each session) | ISO 8601 | ✓ | ✓ | ✓ | ✓ |
| 7 | Location (site name + lat/lon, or lab room) | | ✓ | ✓ | ✓ | |
| 8 | Device(s): model, serial, firmware | | ✓ | ✓ | ✓ | |
| 9 | Capture protocol (1 paragraph + settings) | | ✓ | ✓ | ✓ | |
| 10 | ID scheme (how files, plots, plants, episodes are named) | `2026_AEA_R03_C12_t01` | ✓ | ✓ | ✓ | |
| 11 | Biological material (species, genotype IDs) or "none" | Zea mays, B73 (PI 550473) | ✓ | ✓ | ✓ | |
| 12 | Variables: name, unit, method, ontology ID → **data dictionary** | | ✓ | ✓ | ✓ | |
| 13 | Ground truth / reference measurements + method | calipers, reference sensor | ✓ | ✓ | ✓ | |
| 14 | Processing: software + version + git commit | | ✓ | ✓ | ✓ | |
| 15 | File formats | LAZ, PLY, Parquet | ✓ | ✓ | ✓ | ✓ |
| 16 | License + access tier | CC BY 4.0, Tier 0 | ✓ | ✓ | ✓ | ✓ |
| 17 | Known limitations | | ✓ | | ✓ (RAI) | |
| 18 | Intended use / not suited for | | ✓ | | ✓ (RAI) | |
| 19 | Possible biases (genotypes, weather, sites covered) | | ✓ | | ✓ (RAI) | |
| 20 | Sensitive info removed? (GPS of farms, faces, serials) | | ✓ | | ✓ (RAI) | |

**On-the-day must-haves** (cannot be recovered later): 6, 8, 9, 10, 13, the calibration/reference files, and the per-session capture log.

MIAPPE applies only to **plant experiments** (c, d, e, f below). For (a) and (b) it is marked N/A, and the same fields go into README and Croissant.

---

## 2. One layout for all six

Every dataset uses the lab layout. The only things that change are the **session folders in `02_raw/`** and the **extra fields** listed per dataset.

```
<year>_<site-or-LAB>_<short-name>/
  README.md
  01_metadata/
    study_card.yaml        <- the passport (fill first)
    data_dictionary.csv
    capture_log.csv        <- one row per session, filled on the day
    ids.csv                <- plots/plants/objects/episodes -> genotype or object info
    links.csv              <- only if linked to another dataset
    (generated:) miappe.tsv  croissant.json  datacite.json
  02_raw/<NN_YYYY-MM-DD>/...   read-only
  03_processed/
  04_results/
  05_code/
  99_review/
```

A lab-level **`dataset_registry.csv`** (one row per dataset: name, steward, owner, tier, status, DOI) ties all six together.

---

## 3. Dataset by dataset

### (a) PAR sensor data under different solar conditions (sensor calibration)

**What it is:** time series. Not a plant experiment, so MIAPPE is N/A.
**Format:** one tidy table (CSV for small, Parquet for large), one row per reading.

```
2026_AEA_par-sensor-calibration/
  01_metadata/  study_card.yaml  data_dictionary.csv  capture_log.csv  sensors.csv
  02_raw/01_2026-06-20/  logger_<sensor_id>_20260620.csv   reference_<model>_20260620.csv
  03_processed/  merged_readings_v1.parquet        (sensor + reference aligned in time)
  04_results/   calibration_fit_v1.json            (model, coefficients, R², RMSE per sensor)
```

**Extra fields:**
- `timestamp` with time zone (UTC offset), logging interval
- `sensor_id` (each unit), sensor model (e.g., BH1750), raw output and its unit (lux or counts)
- **Reference sensor:** model, serial, calibration certificate date, unit (µmol m⁻² s⁻¹)
- Sky condition per session (clear / partly cloudy / overcast) and how judged
- Solar zenith angle (computed from time + lat/lon; record the method), air temperature
- Mounting height, tilt, orientation, diffuser/cover; shading or reflections nearby
- Calibration model form (e.g., PAR = a·lux + b) and **validation split by day or sky condition**, not random rows

### (b) LeRobot training data for random objects

**What it is:** robot episodes. MIAPPE is N/A. Croissant is generated automatically if you push to the Hugging Face Hub.
**Format:** keep the **LeRobotDataset** format the library writes (Parquet frames + MP4 videos + `meta/`). Don't reorganize inside it; put our metadata around it.

```
2026_LAB_so101-random-objects/
  01_metadata/  study_card.yaml  objects.csv  data_dictionary.csv  capture_log.csv
  02_raw/lerobot_dataset/        <- exactly as LeRobot writes it (meta/, data/, videos/)
  02_raw/robot_calibration/      <- follower/leader calibration files
  04_results/  policy_eval_v1.csv
  splits/      README.md         <- held-out objects, not held-out frames
```

**Extra fields:**
- Robot type and version (e.g., SO-101 follower + leader), firmware, **calibration files**
- Control frequency (fps), joint names and units (degrees/radians), gripper range
- Cameras: name, model, resolution, fps, mount position (wrist/top/side), a photo of the setup
- `objects.csv`: object ID, name, photo, size (mm), mass (g), material, which episodes
- Task instruction text per episode, teleoperator, success/failure label per episode
- Scene: table surface, lighting, background, distractor objects
- Split rule: **leave-object-out** (test objects never seen in training)

### (c) Tassel images from UAV + 3D reconstruction

**What it is:** field plant experiment → MIAPPE applies.

```
2026_AEA_tassel-uav-3d/
  01_metadata/  study_card.yaml  ids.csv  plot_map.gpkg  capture_log.csv  data_dictionary.csv  links.csv
  02_raw/01_2026-07-22/  images/  flight_log/  gcp_rtk/
  03_processed/01_2026-07-22/  sfm/ (camera poses, sparse)  3dgs_or_nerf/ (PLY + transforms.json)  tassel_crops/
  04_results/  tassel_traits_v1.csv
```

**Extra fields:**
- Drone and camera model, lens, altitude, GSD (cm/px), front/side overlap, gimbal angle(s), flight pattern
- RTK/GCPs and **CRS (EPSG code)**
- Growth stage on the day (VT, R1), time of day, **wind speed** (tassels move; it limits 3D quality)
- Plot map → genotype (`ids.csv`)
- Reconstruction: software + version + settings (COLMAP, Metashape, 3DGS), outputs, scale reference
- Ground truth: tassel length, branch number, method, on which plants
- `links.csv`: same plants as (e) → **direct** if same day

### (d) Sorghum stalk panoramic imaging (stalk measurement)

**What it is:** plant experiment → MIAPPE applies.

```
2026_AEA_sorghum-stalk-panorama/
  01_metadata/  study_card.yaml  ids.csv  capture_log.csv  data_dictionary.csv
  02_raw/01_2026-08-10/  <stalk_id>/  frame_000.jpg …
  03_processed/  panoramas/<stalk_id>_pano_v1.tif   masks/
  04_results/  stalk_traits_v1.csv   (diameter_mm, internode_length_mm, …)
```

**Extra fields:**
- Camera, lens, focal length, distance to stalk, how frames were captured (rotating rig / slider / walk-by)
- **Scale reference in frame** (checkerboard or ruler; size in mm) → px-to-mm conversion
- Stitching software + version + settings
- Stalk ID → plant → plot → genotype; growth stage; which internodes were measured
- Ground truth: calipers/tape, units, who measured, and on how many stalks

### (e) Tassel images from a handheld camera + 3D reconstruction

**What it is:** plant experiment → MIAPPE applies. Same as (c) but close-range.

```
2026_AEA_tassel-handheld-3d/
  01_metadata/  study_card.yaml  ids.csv  capture_log.csv  data_dictionary.csv  links.csv
  02_raw/01_2026-07-22/<tassel_id>/  img_000.jpg …
  03_processed/<tassel_id>/  colmap/  3dgs/  mesh/
  04_results/  tassel_traits_v1.csv
```

**Extra fields:**
- Camera, focal length, aperture/ISO/shutter, number of images, capture path (orbit, heights)
- **In situ or detached** tassel; background (cloth/board); lighting
- **Scale marker** (ArUco/checkerboard size) → metric scale
- Reconstruction software + settings; ground-truth measurements
- `links.csv`: tassel_id ↔ the same plant in (c); this pairing is what makes the two datasets useful together

### (f) Hyperspectral 3D imaging of maize ears (Hinalea)

**What it is:** plant material in the lab → MIAPPE applies (observation unit = ear).

```
2026_LAB_maize-ear-hyperspectral-3d/
  01_metadata/  study_card.yaml  ids.csv  capture_log.csv  data_dictionary.csv  wavelengths.csv
  02_raw/01_2026-09-10/
    E0001/  E0001_view000.hdr/.bil  E0001_view000.json (angle, exposure)  …
    _refs/  white_<time>.hdr/.bil  dark_<time>.hdr/.bil
  03_processed/  reflectance/ (Zarr or ENVI)   pointcloud_spectral/E0001_v1.ply
  04_results/  ear_traits_v1.csv
```

**Extra fields:**
- Camera model and serial, **wavelength list** (centers + FWHM), spectral range, bands
- Integration time, gain, lens, working distance, illumination (lamp type, warm-up time)
- **White and dark references for every session** (time-stamped), reference panel reflectance
- Turntable step angle, number of views, ear orientation, background
- Ear ID → plot → genotype; harvest date; moisture/drying state
- Processing: radiometric calibration, registration of views to 3D, software + commit
- Ground truth: kernel rows, ear length, composition (if measured), method

---

## 4. Summary: which formats each dataset gets

| Dataset | README | MIAPPE | Croissant | Special format kept as-is | DOI home |
|---|:-:|:-:|:-:|---|---|
| a. PAR calibration | ✓ | N/A | ✓ | tidy time series (Parquet) | Zenodo / ISU DataShare |
| b. LeRobot | ✓ | N/A | ✓ (auto on HF) | LeRobotDataset | Hugging Face (+DOI) |
| c. Tassel UAV 3D | ✓ | ✓ | ✓ | images + PLY + `transforms.json` | Zenodo / CyVerse |
| d. Sorghum panorama | ✓ | ✓ | ✓ | images + panoramas | Zenodo / ISU DataShare |
| e. Tassel handheld 3D | ✓ | ✓ | ✓ | images + PLY + `transforms.json` | Zenodo / CyVerse |
| f. Hyperspectral ear 3D | ✓ | ✓ | ✓ | ENVI/Zarr + spectral PLY | Zenodo / CyVerse |

**Links between them:** (c) ↔ (e) direct (same tassels, same day); (f) ↔ field plots contextual (same genotype); (a) supports any canopy-light dataset as a calibration input.
