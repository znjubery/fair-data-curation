#!/usr/bin/env python3
"""Copy the shared run/undo engine from cli/fair_curate.py into the organize.py template inside app/fair-folder-curator.html.

Run after editing the ENGINE block:  python tools/sync_engine.py
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "cli", "fair_curate.py")
APP = os.path.join(ROOT, "app", "fair-folder-curator.html")
A, B = "# >>> ENGINE", "# <<< ENGINE"

cli = open(CLI, encoding="utf-8").read()
engine = cli[cli.index(A):cli.index(B) + len(B)]
if "`" in engine or "${" in engine:
    sys.exit("Engine contains ` or ${ which would break the JavaScript template string.")

BODY = r'''import argparse, base64, csv, datetime, hashlib, json, os, re, shutil, sys

PLAN_B64 = (
__PLAN__
)
EXTRA_B64 = (
__EXTRA__
)
DEFAULT_CHECKSUM = __CHK__
META_DIR = "__META__"

''' + engine + r'''


def main():
    ap = argparse.ArgumentParser(description="Organize a messy folder using a FAIR Folder Curator plan (v0.2).")
    ap.add_argument("source", nargs="?", help="the messy folder")
    ap.add_argument("dest", nargs="?", help="where the organized folder goes (outside the source); omit with --inplace")
    ap.add_argument("--apply", action="store_true", help="actually change files (default is a dry run)")
    ap.add_argument("--move", action="store_true", help="move instead of copy")
    ap.add_argument("--inplace", action="store_true", help="reorganize inside the messy folder itself (rename/move, no copies)")
    ap.add_argument("--checksum", action="store_true", default=DEFAULT_CHECKSUM, help="verify every file with SHA-256")
    ap.add_argument("--undo", metavar="FOLDER", help="reverse the latest run in this organized folder (an old manifest.csv path also works)")
    ap.add_argument("--id", help="with --undo: the run id to reverse (see --runs)")
    ap.add_argument("--runs", metavar="FOLDER", help="list the run history of an organized folder")
    ap.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    a = ap.parse_args()
    if a.runs:
        list_runs(a.runs)
    elif a.undo:
        undo_run(a.undo, a.yes, a.id)
    elif a.source and (a.dest or a.inplace):
        plan = json.loads(base64.b64decode(PLAN_B64).decode("utf-8"))
        extra = json.loads(base64.b64decode(EXTRA_B64).decode("utf-8"))
        mode = "inplace" if a.inplace else ("move" if a.move else "copy")
        run_plan(plan, extra, a.source, a.dest or a.source, mode, a.checksum, a.yes, a.apply, META_DIR,
                 undo_cmd="python %s --undo" % os.path.basename(sys.argv[0]))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
'''

app = open(APP, encoding="utf-8").read()
start = app.index("  const body = String.raw`") + len("  const body = String.raw`")
end = app.index("`;\n  return head + body.replace(\"__PLAN__\"")
app = app[:start] + BODY + app[end:]
open(APP, "w", encoding="utf-8").write(app)
print("engine synced: %d lines" % len(engine.splitlines()))
