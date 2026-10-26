# FAIR Data Curation

Materials for making our lab's phenotyping data **F**indable, **A**ccessible, **I**nteroperable and **R**eusable, so it meets USDA/NSF data-sharing rules and survives the person who collected it.

Maintainer: Baskar Lab, Iowa State University.

## What's here

| Folder | Contents |
|---|---|
| `talk/FAIR_Data_Curation_Talk.pdf` | 20–25 min group-meeting talk, 14 slides, ISU/TrAC template. |
| `figures/` | Every image used in the talk: highlighted source excerpts, the FAIR score chart, and screenshots of the Folder Curator app. |
| `app/fair-folder-curator.html` | **FAIR Folder Curator**: load a messy folder, answer a short interview, review a numbered FAIR layout, and export `organize.py` plus README, MIAPPE, Croissant and FAIR-report files. |
| `cli/fair_curate.py` | **Command-line version** for Nova, Jetstream2, Globus endpoints or any folder a browser can't open. Same rules and layout; `scan`, `apply`, `runs`, `undo`. One file, Python 3.8+, no installs. |
| `TESTING.md` | **v0.2 test tasks for the group**, one section per person. |
| `CONTRIBUTING.md` | How to report problems, request missing features, and push fixes (branch + pull request). |
| `CHANGELOG.md` | What changed in each version. |
| `lesson/fair-data-for-phenotyping.html` | The 10-section FAIR lesson with the scoring math and the UAV-LiDAR worked example. |

## Quick start for lab members

1. Open `app/fair-folder-curator.html` in Chrome or Edge and drop in one of your data folders. Only file names, sizes, dates and file headers are read, on your own computer.
2. Answer the interview, check the plan, and export the kit.
3. Next to your messy folder, run:

   ```bash
   python organize.py "messy-folder" "clean-folder"            # preview, changes nothing
   python organize.py "messy-folder" "clean-folder" --apply    # copy into the new layout
   python organize.py "messy-folder" --inplace --apply         # or: rename inside the same folder, no copies
   python organize.py --runs "clean-folder"                    # run history
   python organize.py --undo "clean-folder"                    # reverse the latest run
   ```

   On Windows use `py` instead of `python`.

4. Fill in the blanks in the generated `README.md` (processing steps, license, trait IDs).

Next time, click **Load previous session** in step 1 and pick `01_metadata/curator_session.json`: your answers and every group setting come back. The app also remembers your last session for each folder name in this browser.

## On Nova, Jetstream2 or a Globus endpoint (no browser)

```bash
python cli/fair_curate.py scan  /work/mydata --year 2025 --site AEA      # prints a summary + writes mydata.plan.json / .plan.csv
python cli/fair_curate.py apply /work/mydata /work/mydata-fair           # dry run
python cli/fair_curate.py apply /work/mydata /work/mydata-fair --run --yes
python cli/fair_curate.py runs  /work/mydata-fair
python cli/fair_curate.py undo  /work/mydata-fair
```

- Edit the `new_path` column of `*.plan.csv` (or the groups in `*.plan.json`) and pass it with `--plan`.
- `--session curator_session.json` reuses answers and group settings made in the HTML app, and `apply --plan curator_session.json` runs a plan you built in the app.
- `--inplace` reorganizes inside the folder when there is no room for a copy.

## Version history for big data (DVC)

Every run is logged in `01_metadata/runs.json` with its own manifest, so any run can be undone. For version control of the data itself, put the organized folder under [DVC](https://dvc.org): `git init && dvc init && dvc add 02_raw 03_processed && git add . && git commit -m "organized v1"`. DVC keeps the large files out of git and lets you return to any commit.

The **curator agent** buttons (AI interview and AI planning) only work when the app is opened as its published Claude artifact. Opened as a local file, the rules-only path still works end to end. Saving the zip from a local file is also unavailable; use the **Copy organize.py** button.

## The lab layout in one picture

```
project-name/
  README.md        <- start here
  00_docs/         notes, protocols
  01_metadata/     plot map, calibration, manifest, MIAPPE, Croissant
  02_raw/          straight off the sensor, by session (01_2025-07-14/ ...)
  03_processed/    orthomosaics, point clouds, 3DGS
  04_results/      trait tables, models
  05_code/         scripts, git commit
  99_review/       possible duplicates
```

## Sources quoted in the talk

- Wilkinson et al. (2016), "The FAIR Guiding Principles for scientific data management and stewardship," *Scientific Data* 3:160018 (CC BY 4.0). Principle wording as listed at <https://www.go-fair.org/fair-principles/>.
- OSTP (2022), "Ensuring Free, Immediate, and Equitable Access to Federally Funded Research" (the Nelson memo; public domain).
- European Commission / PwC (2018), *Cost-benefit analysis for FAIR research data*.
- Colavizza et al. (2020), "The citation advantage of linking publications to research data," *PLOS ONE* 15(4):e0230416.
- Devaraju & Huber (2021), "An automated solution for measuring the progress toward FAIR research data" (F-UJI), *Patterns* 2(11):100370.
- NeurIPS 2026 Evaluations & Datasets hosting guidelines (Croissant + Responsible-AI metadata).

Excerpt images are retyped from these sources with highlighting added; they are not scans.
