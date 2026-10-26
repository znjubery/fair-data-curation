# Contributing: feedback, missing features, and fixes

Everyone in the group is expected to (1) report problems, (2) say what is missing, and (3) push fixes or additions back to this repo.

## 1. Report a problem or a missing feature

Open a GitHub **issue** (Issues → New issue). One issue per problem or idea.

- **Problem:** what you ran, what you expected, what happened, plus a screenshot or terminal output and your OS (Windows/Mac/Linux, Nova, Jetstream2).
- **Missing:** what you needed the tool to do, for which data, and why. Label it `enhancement`.

## 2. Push a fix or addition (pull request)

Never push straight to `main`. Work on a branch and open a pull request so someone else checks it.

```bash
git clone https://github.com/znjubery/fair-data-curation.git
cd fair-data-curation
git checkout -b yourname/short-description          # e.g. theo/windows-long-paths
# ...edit, then test (below)...
git add -A
git commit -m "Short summary of the change (fixes #3)"
git push -u origin yourname/short-description
```

Then on GitHub click **Compare & pull request**, describe what you changed and how you tested it, and request a review from Zaki.

**No write access?** Click **Fork** on GitHub, clone your fork instead, push your branch there, and open the pull request from the fork. Or ask Zaki to add you as a collaborator.

## Where things live

| You want to change | Edit this | Notes |
|---|---|---|
| Run / undo / history logic used by both the app's `organize.py` and the CLI | `cli/fair_curate.py`, between `# >>> ENGINE` and `# <<< ENGINE` | Then run `python tools/sync_engine.py` so the app gets the same code. Never edit the engine inside the HTML by hand. |
| Command-line scanning and file-type rules | `cli/fair_curate.py` (`guess`, `find_date`, `build_plan`) | Keep rules the same as the app's `guess()` in the HTML. |
| App screens, interview, charts, file-type rules | `app/fair-folder-curator.html` | One self-contained file; open it in Chrome to test. |
| Docs, test tasks | `README.md`, `TESTING.md`, `CHANGELOG.md` | Add a line to CHANGELOG under "Unreleased". |

## Test before you push

```bash
python cli/fair_curate.py scan  test-folder --year 2025
python cli/fair_curate.py apply test-folder test-clean --run --yes
python cli/fair_curate.py undo  test-clean --yes                 # every file should come back
```

For app changes: open the HTML, click **Load example folder**, go through all four steps, export the kit, and run its `organize.py` preview, `--apply`, `--undo`. Use a copy of your data, never the only copy.
