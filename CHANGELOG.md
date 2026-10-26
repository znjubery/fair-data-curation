# Changelog

## v0.2 (2026-10-26): feedback from the Oct 26 group meeting

| Suggestion from the meeting | What changed |
|---|---|
| Re-enter info from earlier sessions | App: **Load previous session** reloads `curator_session.json` (answers + every group setting). The app also remembers the last session per folder name in your browser. CLI: `--session`. |
| Undo / version control like DVC | Every run is logged in `01_metadata/runs.json` with its own manifest. `--runs FOLDER` lists them; `--undo FOLDER` reverses the latest (or `--id`). Re-running is safe: files already in place are skipped. DVC recipe added to README. |
| Rename instead of copying the whole folder | New `--inplace` mode: rename/move inside the same folder, fully undoable. |
| CLI for Globus / Jetstream / Nova | New `cli/fair_curate.py` (`scan`, `apply`, `runs`, `undo`), standard library only. Uses the same rules and session file as the app. |
| Visualization | App step 3: **At a glance** panel with size per top folder and a field-day timeline (files per data type per session). CLI prints the same as text bars. |
| Windows file paths | Planned names are made Windows-safe (reserved names like `CON`, `AUX`; `: ? * < > |`; trailing dots/spaces) and long paths (>240 characters) use the `\\?\` prefix. Needs a real Windows test (see TESTING.md). |

Old kits still work: `--undo path/to/manifest.csv` is accepted.

## v0.1 (2026-10-26)

First release: talk, FAIR Folder Curator app, FAIR lesson.
