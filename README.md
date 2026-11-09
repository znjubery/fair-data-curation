# FAIR Data Curation · Start here

Turn your messy data folder into a clean, documented dataset that others can **F**ind, **A**ccess, **I**nteroperate with and **R**euse, as NSF and USDA require.

**One line:** describe your data once (study card), organize the folder (Curator), check it (manifest), then deposit it for a DOI.

## The 4 steps

1. **Scan your folder: FAIR Folder Curator.** Open [`app/fair-folder-curator.html`](app/fair-folder-curator.html) in Chrome or Edge. Drop in your folder, press *Read embedded metadata*, and save the session (`curator_session.json`). Nothing is uploaded.
2. **Describe it: Study Card Builder.** Open [`app/study-card-builder.html`](app/study-card-builder.html) in Chrome or Edge. Pick your dataset type, press *Import from Curator session*, fill the rest, and *Download all files*. This writes the README, data dictionary, sensors, protocol, MIAPPE, Croissant and DOI files. Save your progress (.json).
3. **Organize it: Curator again.** Press *Load study card (.json)*. The interview asks only what is still missing. Check the plan, export the kit, and run `organize.py` (preview first, then `--apply`).
4. **Check and share.** Run [`tools/make_manifest.py`](tools/make_manifest.py): `python tools/make_manifest.py "path/to/your-dataset"` (Windows: `py`). Fix what `qc_report.md` lists, deposit to a repository for a DOI, put the DOI back in the builder (step 12), and tick the finish checklist.

## Which file do I open?

| I want to… | Open |
|---|---|
| Describe my dataset (one time, fills every format) | [`app/study-card-builder.html`](app/study-card-builder.html) |
| Organize a messy folder into the lab layout | [`app/fair-folder-curator.html`](app/fair-folder-curator.html) |
| Checksums + quality report | [`tools/make_manifest.py`](tools/make_manifest.py) |
| Organize on Nova / Jetstream2 / Globus (no browser) | [`tools/fair_curate.py`](tools/fair_curate.py) (see [`docs/07_reference.md`](docs/07_reference.md)) |
| Fill-in files by hand | [`templates/`](templates/) (start with [`study_card.yaml`](templates/study_card.yaml)) |
| Learn FAIR, see examples, prepare a paper | [`docs/`](docs/) (start with [`docs/README.md`](docs/README.md)) |

## The lab layout

```
2026_AEA_my-dataset/
  README.md  00_docs/  01_metadata/  02_raw/ (read-only)  03_processed/  04_results/  05_code/  99_review/
```

## Help

- Stuck or found a bug: open a GitHub issue, or ask on the lab Slack.
- Before you deposit or share: ask your PI to approve the license and access tier.

Instructor and maintainer material (talks, figures, test plan, contributing guide, changelog) is in [`instructor/`](instructor/).

## Contributors

- **Zaki Jubery** — creator and maintainer · Department of Mechanical Engineering and Translational AI Center (TrAC), Iowa State University · [@znjubery](https://github.com/znjubery)
- Baskar Lab group members — testing and feedback (see [`instructor/CONTRIBUTING.md`](instructor/CONTRIBUTING.md) to add yourself)

Baskar Lab, Iowa State University. To cite this toolkit, see [`CITATION.cff`](CITATION.cff).
