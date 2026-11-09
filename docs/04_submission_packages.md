# 04 · Preparing data for a conference or journal submission

A paper submission needs a **frozen, citable slice** of your curated project, not the whole working folder. Make it from the curated folder; never hand-copy files.

> **Analogy: a museum exhibit.** The museum (your curated project) keeps everything. For an exhibit (a paper), you pick the objects that tell this story, label them for visitors, and ship them in a crate with a packing list.

*Venue rules change every year. Re-check the current call for papers before each deadline. Rules below were checked in November 2026.*

---

## Step 1: the submission package layout

```
submission_<venue><year>_<short-title>/        e.g. submission_NeurIPS2026_maize-lidar/
  README.md                  what this package is, how it maps to the paper
  DATA_AVAILABILITY.md       the statement that goes in the paper
  CITATION.cff               how to cite the data and code
  LICENSE                    CC BY 4.0 (data), MIT/Apache-2.0 (code)
  data/                      only what the paper uses (or a link + loader if too large)
  metadata/
    croissant.json           core + RAI fields (ML venues)
    miappe.tsv               (plant-science venues)
    data_dictionary.csv
    provenance.json          paper figure/table → script → git commit
    MANIFEST.sha256
  code/
    reproduce_fig3.py …      one script per figure/table
    environment.yml
  splits/                    exact train/val/test ID lists used in the paper
  REVIEW_ACCESS.md           anonymous link for reviewers (if double-blind)
```

**Paper-to-data map** (put in `provenance.json` or the README):

| Paper item | Data files | Script | Commit |
|---|---|---|---|
| Fig. 3 | `data/plot_traits_v1.parquet` | `code/reproduce_fig3.py` | `a1b2c3d` |
| Table 2 | `splits/test_ids.txt` + model outputs | `code/eval.py` | `a1b2c3d` |

---

## Step 2: venue-specific requirements

### NeurIPS Evaluations & Datasets track (and other ML dataset tracks)

- New datasets must be **hosted and documented at submission**, not later. Data and code are **not** supplementary material for this track.
- **Croissant metadata is required, with both core and Responsible-AI (RAI) fields.** Missing RAI fields get flagged in review.
- Preferred hosts: **Harvard Dataverse, Kaggle, Hugging Face, OpenML**. They auto-generate core Croissant; **you add the RAI fields** (limitations, biases, intended use, collection process). Validate with the online Croissant validator.
- Self-hosting (e.g., NRP, Box) is allowed, but then you write the Croissant file yourself.
- Must be **public by camera-ready**.
- Can be single-blind if the data reveals the institution; say so in the submission.

### CVPR / ICCV / ECCV / WACV (vision conferences)

- Double-blind: **no author names, ISU, grant IDs, or identifying links** in the paper or supplement. CVPR 2026 bans external links that add content; put samples in the supplement zip.
- If you claim the dataset as a contribution, it must be **public with a stable URL by camera-ready** (ECCV makes this a hard rule for the Datasets/Benchmarks contribution type).
- Strip EXIF GPS/serials from sample images in the supplement if they identify the site or team.
- CVPR 2026 also requires a **Compute Reporting Form** with the supplement.

### Journals: Scientific Data (data descriptor), Plant Phenomics, Computers and Electronics in Agriculture, etc.

- **Deposit first, then submit.** Scientific Data requires the data in an approved repository before review; it can stay private until publication, with confidential reviewer access.
- Repository must give a **DOI**; data cited in the reference list.
- **Data Availability** and **Code Availability** sections are required.
- Non-proprietary formats, open license (CC0 or CC BY 4.0) unless an exception is justified.

### ASME IMECE, ASABE, NAPPN and other engineering/ag conferences

- Usually no hosting rule, but **cite a DOI** anyway: it makes the paper reproducible and the data citable.
- Funder rules still apply: NSF and USDA expect data supporting publications to be shared (DOI, public access policy).

---

## Step 3: the data availability statement

**Open data:**
> The data supporting this study are available in [Repository] at https://doi.org/10.xxxx/xxxxx under a CC BY 4.0 license. Code is available at https://github.com/… (commit a1b2c3d) under the MIT license.

**Restricted data (Tier 1/2):**
> Plot-level traits and metadata are openly available at https://doi.org/10.xxxx/xxxxx. Genotype data are restricted under a data-use agreement with [partner] and are available from the corresponding author on reasonable request, subject to that agreement.

**Double-blind review:**
> An anonymized copy of the data is available to reviewers at [anonymous link]; a DOI will be provided at publication.

---

## Step 4: checklist before you press submit

- [ ] Package built **from the curated folder** by a script (not by hand)
- [ ] Only the data the paper uses; everything else linked by DOI
- [ ] Every figure/table maps to a script + commit
- [ ] Split ID lists included; leakage audit passed
- [ ] `croissant.json` validates (core + RAI) — ML venues
- [ ] MIAPPE / MIxS filled — plant/soil venues
- [ ] License files present; access tier stated
- [ ] Double-blind: no names, ISU, grant IDs, GPS in EXIF, or identifying URLs
- [ ] DOI reserved (Zenodo/ISU DataShare/Dataverse allow reserving before publishing)
- [ ] Checksums written; a labmate downloaded and reproduced one figure
- [ ] Data and code made public by camera-ready

## Repositories at a glance

| Repository | DOI | Restricted access | Croissant | Notes |
|---|---|---|---|---|
| ISU DataShare | yes | no (open only) | no | ISU institutional; CC0 or CC BY |
| Zenodo | yes | yes (restricted files) | no | links to GitHub releases |
| Harvard Dataverse | yes | yes | auto (core) | NeurIPS preferred |
| Hugging Face | yes (on request) | gated datasets | auto (core) | NeurIPS preferred; ML community |
| Ag Data Commons (USDA) | yes | — | no | USDA-funded data |
| CyVerse Data Commons | yes | — | no | large plant datasets |
| NCBI SRA / BioSample | accession | embargo | no | sequence reads, with MIxS |

**Sources:** NeurIPS 2026 E&D Call for Papers and Hosting Guidelines; NeurIPS RAI metadata blog (May 2026); CVPR 2026 Author Guidelines and Compute Reporting; ECCV 2026 Author Practices; Scientific Data Guide to Authors and data deposition policy.
