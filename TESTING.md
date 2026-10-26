# v0.2 testing: tasks for the group

Goal: by **Monday, Nov 9, 2026** every member has organized one real dataset with the tool and reported problems.
Work on a **copy or small subset** of your data, never the only copy.

Three things are expected from everyone (details in [CONTRIBUTING.md](CONTRIBUTING.md)):

1. **Feedback**: report each problem as its own GitHub issue (what you ran, what you expected, what happened, screenshot or terminal output).
2. **What's missing**: open an `enhancement` issue for anything the tool should do for your data but doesn't.
3. **Push**: fix at least one thing you found (a bug, a file-type rule, a doc gap) on a branch and open a pull request.

## Everyone

1. Download the repo (green **Code** button → Download ZIP, or `git clone`).
2. Open `app/fair-folder-curator.html` in Chrome or Edge, load a small subset of your data (50–500 files), answer the interview, check **At a glance** in step 3, and export the kit.
3. Run the preview, then `--apply`, then `--runs`, then `--undo`, then `--apply` again (commands are in `HOW_TO_RUN.txt` in the kit).
4. Fill the blanks in the generated `README.md` and note your FAIR score (step 4) before and after.
5. Reply to the issue **"v0.2 check-in"** with: dataset name, number of files, FAIR % before → after, the time it took, and links to the issues and pull request you opened.

## Harish: genotype data and session reload

1. Repeat the genotype dataset from the meeting with v0.2.
2. Close the browser, reopen the app, and click **Load previous session** with `01_metadata/curator_session.json`. Check that every answer and group setting came back. Then load the folder again without the file and check the "Restored from your last session" banner.
3. Edit two groups, export again, and confirm `--apply` on the existing clean folder adds only the changes (files already in place are reported as "already there").
4. Report anything the app classified wrong for genotype files (VCF, HapMap, PLINK).

## Theo: Windows paths and rename-in-place

On a Windows PC, with `py` instead of `python`:

1. Make a test folder with: a path longer than 260 characters, a file named `CON.txt` and one named `aux.csv`, a folder name ending in a space or a dot, and names with spaces and non-English characters.
2. Run the kit's `organize.py` preview, `--apply`, `--runs`, `--undo`. Check every file came back exactly (compare file counts and sizes).
3. Test `--inplace --apply` and `--undo` on a copy of a real subset. Report whether File Explorer, OneDrive or Box sync interfered.
4. Test a folder on a mapped network drive or Box Drive if you use one.

## Kibona: command line on Jetstream2 / Nova / Globus

1. Copy `cli/fair_curate.py` to a Jetstream2 VM or Nova and pick a dataset that arrived by Globus (or a subset).
2. Run `scan` (with `--year` and `--site`), open the `.plan.csv`, change two `new_path` values, and `apply --plan file.plan.csv` (dry run, then `--run --yes`).
3. Try `apply --plan curator_session.json` with a session file made in the HTML app for the same folder.
4. Time it on a large folder (≥10,000 files or ≥100 GB) with and without `--checksum`, and report the times.
5. Try the DVC recipe in the README on the organized folder and note what was confusing.

## Ravi, Maryam, Antriksh, Som

1. Do the **Everyone** steps on one of your own datasets.
2. Each pick one extra check and say which in the check-in issue:
   - **Ravi**: a 3D reconstruction folder (images + `transforms.json` + PLY/splats). Are camera poses kept next to their outputs?
   - **Maryam**: hyperspectral or other lab-instrument data. Does each header file stay with its data file?
   - **Antriksh**: a mixed folder with code, notebooks and results. Are scripts, results and processed data separated sensibly?
   - **Som**: tables only (CSV/Excel). Check that the MIAPPE sheet and Croissant file in the kit make sense for your traits.
