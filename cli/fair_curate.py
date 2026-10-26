#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fair_curate.py - command-line FAIR Folder Curator (Baskar Lab, Iowa State University)

For folders that live on Nova, Jetstream, Globus endpoints, or anywhere a browser
can't reach. Same rules and layout as the HTML app. Python 3.8+, standard library only.

  python fair_curate.py scan  MESSY_FOLDER                     # writes MESSY_FOLDER.plan.json + .plan.csv, prints a summary
  python fair_curate.py apply MESSY_FOLDER CLEAN_FOLDER        # preview (dry run)
  python fair_curate.py apply MESSY_FOLDER CLEAN_FOLDER --yes --run   # copy into the new layout
  python fair_curate.py apply MESSY_FOLDER --inplace --run     # reorganize inside the same folder (no copy)
  python fair_curate.py runs  CLEAN_FOLDER                     # list run history
  python fair_curate.py undo  CLEAN_FOLDER                     # reverse the latest run

Edit the plan before applying: change the new_path column in *.plan.csv (or the
"answers" block in *.plan.json) and pass it with --plan.
Reuse answers from an earlier session (app or CLI): --session curator_session.json
"""
import argparse, base64, csv, datetime, hashlib, json, os, re, shutil, sys, unicodedata

VERSION = "0.2"

# >>> ENGINE (shared with the organize.py that the HTML app exports; keep in sync via tools/sync_engine.py)
RESERVED = {"CON", "PRN", "AUX", "NUL", *("COM%d" % i for i in range(1, 10)), *("LPT%d" % i for i in range(1, 10))}


def safe_rel(rel):
    """Make a planned relative path safe on Windows, macOS and Linux."""
    out = []
    for part in rel.split("/"):
        part = re.sub(r'[<>:"\\|?*\x00-\x1f]', "_", part).rstrip(" .") or "_"
        stem = part.split(".")[0].upper()
        if stem in RESERVED:
            part = "_" + part
        out.append(part)
    return "/".join(out)


def native(root, rel):
    """Absolute OS path for a plan path; long-path safe on Windows."""
    p = os.path.abspath(os.path.join(root, *rel.split("/")))
    if os.name == "nt" and len(p) >= 240 and not p.startswith("\\\\?\\"):
        p = "\\\\?\\" + p
    return p


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(buf), b""):
            h.update(chunk)
    return h.hexdigest()


def unique_target(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 2
    while os.path.exists("%s_%d%s" % (base, i, ext)):
        i += 1
    return "%s_%d%s" % (base, i, ext)


def confirm(msg, yes):
    if yes:
        return True
    try:
        return input(msg + " Type yes to continue: ").strip().lower() == "yes"
    except EOFError:
        return False


def _runs_file(dst, meta_dir):
    return os.path.join(dst, meta_dir, "runs.json")


def load_runs(dst, meta_dir):
    try:
        with open(_runs_file(dst, meta_dir), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return []


def save_runs(dst, meta_dir, runs):
    os.makedirs(os.path.join(dst, meta_dir), exist_ok=True)
    with open(_runs_file(dst, meta_dir), "w", encoding="utf-8") as fh:
        json.dump(runs, fh, indent=2)


def find_meta_dir(dst):
    for m in ("01_metadata", "metadata"):
        if os.path.isfile(os.path.join(dst, m, "runs.json")):
            return m
    return None


def run_plan(plan, extra, src, dst, mode, checksum, yes, apply, meta_dir, undo_cmd="python organize.py --undo"):
    """mode: copy | move | inplace. Returns the run record (or None for a dry run)."""
    src = os.path.abspath(src)
    dst = os.path.abspath(src if mode == "inplace" else dst)
    if not os.path.isdir(src):
        sys.exit("Source folder not found: " + src)
    if mode != "inplace" and (dst == src or dst.startswith(src + os.sep)):
        sys.exit("CLEAN_FOLDER must be outside MESSY_FOLDER. To reorganize inside the same folder use --inplace.")
    todo = [r for r in plan if r["action"] == "copy"]
    skipped = [r for r in plan if r["action"] != "copy"]
    for r in todo:
        r["new"] = safe_rel(r["new"])
    missing = [r for r in todo if not os.path.isfile(native(src, r["old"]))]
    total = sum(r["size"] for r in todo)
    verb = {"copy": "copy", "move": "move", "inplace": "rename in place"}[mode]
    print("Plan: %d files to %s (%.2f GB), %d skipped, %d missing in source." % (len(todo), verb, total / 1e9, len(skipped), len(missing)))
    for r in todo[:12]:
        print("  %s  ->  %s" % (r["old"], r["new"]))
    if len(todo) > 12:
        print("  ... and %d more" % (len(todo) - 12))
    if extra:
        print("Metadata files to write: " + ", ".join(sorted(extra)))
    if missing:
        print("%d planned files were not found (renamed or deleted since the plan was made), e.g.:" % len(missing))
        for r in missing[:10]:
            print("  " + r["old"])
    if not apply:
        print("\nDry run only. Nothing was changed. Add --apply to do it.")
        return None
    if mode != "copy" and not confirm("This will %s %d files inside %s." % (verb.upper(), len(todo), src), yes):
        sys.exit("Stopped. Nothing was changed.")
    if mode != "inplace" and os.path.isdir(dst) and os.listdir(dst) and not confirm(dst + " is not empty. New files will be added next to what is there.", yes):
        sys.exit("Stopped. Nothing was changed.")
    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    taken = {r["id"] for r in load_runs(dst, meta_dir)}
    base_id, k = run_id, 2
    while run_id in taken:
        run_id = "%s-%d" % (base_id, k)
        k += 1
    runs_dir = os.path.join(dst, meta_dir, "runs")
    os.makedirs(runs_dir, exist_ok=True)
    manifest_path = unique_target(os.path.join(runs_dir, run_id + "_manifest.csv"))
    ok = bad = 0
    with open(manifest_path, "w", newline="", encoding="utf-8") as mf:
        w = csv.writer(mf)
        w.writerow(["original_path", "new_path", "size_bytes", "sha256", "action", "status"])
        for r in skipped:
            w.writerow([r["old"], "", r["size"], "", r["action"], "not copied"])
        for i, r in enumerate(todo, 1):
            s = native(src, r["old"])
            if not os.path.isfile(s):
                w.writerow([r["old"], r["new"], r["size"], "", mode, "missing"])
                bad += 1
                continue
            t = native(dst, r["new"])
            if os.path.normcase(os.path.abspath(s)) == os.path.normcase(os.path.abspath(t)):
                w.writerow([r["old"], r["new"], r["size"], "", mode, "unchanged"])
                ok += 1
                continue
            if os.path.isfile(t) and os.path.getsize(t) == os.path.getsize(s) and (not checksum or sha256(t) == sha256(s)):
                w.writerow([r["old"], r["new"], r["size"], "", mode, "already there"])
                ok += 1
                continue
            t = unique_target(t)
            new_rel = os.path.relpath(t.replace("\\\\?\\", ""), dst).replace(os.sep, "/")
            try:
                os.makedirs(os.path.dirname(t), exist_ok=True)
                size0 = os.path.getsize(s)
                digest = sha256(s) if checksum else ""
                if mode == "copy":
                    shutil.copy2(s, t)
                else:
                    shutil.move(s, t)
                status = "ok"
                if os.path.getsize(t) != size0:
                    status = "SIZE MISMATCH"
                elif checksum and sha256(t) != digest:
                    status = "CHECKSUM MISMATCH"
                w.writerow([r["old"], new_rel, size0, digest, mode, status])
                ok += status == "ok"
                bad += status != "ok"
            except OSError as e:
                w.writerow([r["old"], r["new"], r["size"], "", mode, "error: %s" % e])
                bad += 1
            if i % 200 == 0:
                print("  %d/%d done" % (i, len(todo)))
    if mode == "inplace":  # tidy the old, now-empty folders (never the metadata folder)
        for root, dirs, files in os.walk(src, topdown=False):
            rel = os.path.relpath(root, src).replace(os.sep, "/")
            if root != src and not os.listdir(root) and not rel.startswith(meta_dir):
                os.rmdir(root)
    written = []
    for rel, text in extra.items():
        p = native(dst, rel)
        if os.path.exists(p):  # keep the user's edited README/metadata; write the new one beside it
            p = unique_target(p)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        written.append(os.path.relpath(p, dst).replace(os.sep, "/"))
    with open(os.path.join(dst, meta_dir, "manifest.csv"), "w", newline="", encoding="utf-8") as fh:
        fh.write(open(manifest_path, encoding="utf-8").read())
    runs = load_runs(dst, meta_dir)
    rec = {"id": run_id, "time": datetime.datetime.now().isoformat(timespec="seconds"), "mode": mode, "source": src,
           "dest": dst, "ok": ok, "problems": bad, "manifest": os.path.relpath(manifest_path, dst).replace(os.sep, "/"),
           "metadata_written": written, "undone": False}
    runs.append(rec)
    save_runs(dst, meta_dir, runs)
    print("\nDone: %d files %s, %d problems." % (ok, {"copy": "copied", "move": "moved", "inplace": "renamed"}[mode], bad))
    print("Run %s logged in %s/runs.json; manifest %s" % (run_id, meta_dir, rec["manifest"]))
    if bad:
        print("Check rows in the manifest whose status is not 'ok'.")
    print('Undo:   %s "%s"' % (undo_cmd, dst))
    return rec


def list_runs(dst):
    dst = os.path.abspath(dst)
    meta = find_meta_dir(dst)
    if not meta:
        sys.exit("No run history found in " + dst)
    for r in load_runs(dst, meta):
        print("%s  %-8s %5d ok %3d problems  %s%s" % (r["id"], r["mode"], r["ok"], r["problems"], r["source"], "   [undone]" if r.get("undone") else ""))


def undo_run(target, yes, run_id=None):
    """target: the organized folder (latest run is undone) or a manifest.csv path (older kits)."""
    target = os.path.abspath(target)
    if os.path.isfile(target):  # legacy: manifest path; we need dst = folder above metadata
        dst = os.path.dirname(os.path.dirname(target))
        if os.path.basename(os.path.dirname(target)) == "runs":
            dst = os.path.dirname(dst)
    else:
        dst = target
    meta = find_meta_dir(dst)
    runs = load_runs(dst, meta) if meta else []
    live = [r for r in runs if not r.get("undone") and (run_id is None or r["id"] == run_id)]
    if live:
        rec = live[-1]
        manifest = os.path.join(dst, *rec["manifest"].split("/"))
        source = rec["source"]
    elif os.path.isfile(target):
        rec, manifest, source = None, target, None
    else:
        sys.exit("Nothing to undo in " + dst)
    with open(manifest, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    moved = [r for r in rows if r["action"] in ("move", "inplace") and r["status"] == "ok"]
    copied = [r for r in rows if r["action"] == "copy" and r["status"] == "ok"]
    if moved and not source:
        sys.exit("This run moved files but no run history was found, so the original folder is unknown.")
    print("Undo run %s: %d files go back to their old names, %d copies deleted. Originals of copies are not touched." % (rec["id"] if rec else "(manifest)", len(moved), len(copied)))
    if not confirm("Proceed?", yes):
        sys.exit("Stopped. Nothing was changed.")
    for r in moved:
        t = native(dst, r["new_path"])
        o = native(source, r["original_path"])
        if not os.path.isfile(t):
            continue
        if os.path.exists(o):
            print("  skipped (original path is taken): " + r["original_path"])
            continue
        os.makedirs(os.path.dirname(o), exist_ok=True)
        shutil.move(t, o)
    for r in copied:
        t = native(dst, r["new_path"])
        if os.path.isfile(t) and os.path.getsize(t) == int(r["size_bytes"]):
            os.remove(t)
    keep = os.path.join(dst, meta or "metadata")
    for root, dirs, files in os.walk(dst, topdown=False):
        if root != dst and not root.startswith(keep) and not os.listdir(root):
            os.rmdir(root)
    if rec:
        rec["undone"] = True
        rec["undone_time"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_runs(dst, meta, runs)
    print("Undo finished. Run history and metadata files were kept in %s." % keep)
# <<< ENGINE


# ---------------------------------------------------------------- scanning and planning (port of the app's rules)
COMPOUND = [".tar.gz", ".vcf.gz", ".fastq.gz", ".fq.gz", ".nii.gz", ".csv.gz", ".txt.gz", ".hmp.txt"]
JUNK = re.compile(r"^(\.ds_store|thumbs\.db|ehthumbs\.db|desktop\.ini|\.localized)$|^~\$|^\._|\.tmp$|^\.~lock|\.crdownload$|\.part$", re.I)
JUNK_DIR = re.compile(r"(^|/)(\.git|__pycache__|\.ipynb_checkpoints|\$recycle\.bin)(/|$)", re.I)
CAT_NUM = {"docs": "00", "metadata": "01", "raw": "02", "processed": "03", "results": "04", "code": "05", "archive": "90", "other": "98"}
DT_ORDER = ["field_design", "calibration", "config", "uav_rgb", "uav_multispectral", "flight_logs", "lidar", "hyperspectral",
            "turntable_images", "photos", "video", "weather", "genotypes", "sequences", "orthomosaics", "lidar_processed",
            "3d_reconstruction", "point_clouds", "gaussian_splats", "meshes", "trait_tables", "models", "scripts", "notes", "archives", "unsorted"]
MON = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}


def split_ext(name):
    low = name.lower()
    for c in COMPOUND:
        if low.endswith(c) and len(low) > len(c):
            return name[:-len(c)], c
    i = name.rfind(".")
    return (name, "") if i <= 0 else (name[:i], name[i:].lower())


def has(e, lst):
    return e in lst


def guess(dir_, examples, e):
    t = (dir_ + "/" + " ".join(examples)).lower()
    first = (examples[0] if examples else "").lower()

    def R(cat, dtype, dated=False):
        return {"cat": cat, "dtype": dtype, "folder": cat + "/" + dtype + ("/{date}" if dated else ""), "rename": "keep", "dateSrc": "name", "exclude": False}
    if re.search(r"calib|panel|reflectance.?target|white.?ref|dark.?ref", t): return R("metadata", "calibration")
    if re.match(r"readme|license|licence", first): return R("docs", "notes")
    if has(e, [".las", ".laz", ".e57", ".ldr"]):
        return R("processed", "lidar_processed") if re.search(r"merged|clean|classif|filter|processed|final", t) else R("raw", "lidar", True)
    if has(e, [".ply", ".pcd", ".xyz", ".pts"]): return R("processed", "gaussian_splats" if re.search(r"splat|gauss|3dgs", t) else "point_clouds")
    if has(e, [".obj", ".glb", ".gltf", ".stl", ".fbx", ".mtl"]): return R("processed", "meshes")
    if has(e, [".hdr", ".bil", ".bip", ".bsq", ".envi", ".cue"]) or (re.search(r"hsi|hyper|spectral|hinalea|specim|resonon", t) and has(e, [".raw", ".h5", ".hdf5", ".tif", ".tiff", ".dat"])):
        return R("raw", "hyperspectral", True)
    if has(e, [".tif", ".tiff"]) and re.search(r"ortho|mosaic|dsm|dem|dtm|ndvi|index|chm", t): return R("processed", "orthomosaics")
    if has(e, [".jpg", ".jpeg", ".dng", ".tif", ".tiff", ".png"]) and re.search(r"dji|uav|drone|flight|mavic|phantom|m300|m350|m3m|p4|altum|micasense", t):
        ms = re.search(r"_ms_|multispec|nir|rededge|altum|micasense", t) and has(e, [".tif", ".tiff"])
        return R("raw", "uav_multispectral" if ms else "uav_rgb", True)
    if has(e, [".mrk", ".obs", ".nav", ".rtk", ".rtb", ".rpos", ".imu", ".clc", ".cli", ".sig", ".bin"]): return R("raw", "flight_logs", True)
    if has(e, [".jpg", ".jpeg", ".png", ".heic", ".dng", ".tif", ".tiff", ".bmp", ".cr2", ".cr3", ".nef", ".arw"]):
        return R("raw", "turntable_images" if re.search(r"turntable|ear|cob|kernel|tassel", t) else "photos", True)
    if has(e, [".mp4", ".mov", ".avi", ".mkv"]): return R("raw", "video", True)
    if has(e, [".vcf", ".vcf.gz", ".hmp", ".hmp.txt", ".bed", ".bim", ".fam", ".ped"]) or (re.search(r"snp|genotyp|hapmap", t) and has(e, [".txt", ".csv", ".tsv"])):
        return R("raw", "genotypes")
    if has(e, [".fastq", ".fq", ".fastq.gz", ".fq.gz", ".bam", ".sam", ".cram"]): return R("raw", "sequences")
    if has(e, [".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".txt", ".csv.gz", ".ods"]):
        if re.search(r"map|layout|design|field.?book|plot.?list|randomi|planting", t): return R("metadata", "field_design")
        if re.search(r"weather|climate|temp|rain|mesonet", t): return R("raw", "weather")
        return R("results", "trait_tables")
    if has(e, [".py", ".ipynb", ".r", ".rmd", ".m", ".sh", ".cpp", ".c", ".h", ".js", ".jl", ".sbatch", ".slurm", ".bat", ".ps1"]): return R("code", "scripts")
    if has(e, [".pdf", ".docx", ".doc", ".md", ".pptx", ".ppt", ".odt", ".rtf", ".key"]): return R("docs", "notes")
    if has(e, [".json", ".yaml", ".yml", ".xml", ".cfg", ".ini", ".toml"]):
        return R("processed", "3d_reconstruction") if re.search(r"transforms|colmap|cameras|poses|nerf|splat", t) else R("metadata", "config")
    if has(e, [".npy", ".npz", ".pt", ".pth", ".ckpt", ".onnx", ".pkl", ".h5", ".hdf5", ".safetensors"]): return R("results", "models")
    if has(e, [".zip", ".tar", ".tar.gz", ".7z", ".rar", ".gz"]): return R("archive", "archives")
    return R("other", "unsorted")


def find_date(s, year=None):
    m = re.search(r"(?<!\d)(20[0-3]\d)[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])", s)
    if m:
        return "%s-%s-%s" % m.groups()
    if not year:
        return None
    m = re.search(r"(?<![a-z])(jan|feb|mar|apr|may|jun|jul|aug|sept|sep|oct|nov|dec)[a-z]*[\s_-]*(\d{1,2})(?!\d)", s, re.I)
    if m and 1 <= int(m.group(2)) <= 31:
        return "%s-%02d-%02d" % (year, MON[m.group(1).lower()], int(m.group(2)))
    m = re.search(r"(?<!\d)(\d{1,2})[\s_-]*(jan|feb|mar|apr|may|jun|jul|aug|sept|sep|oct|nov|dec)[a-z]*(?![a-z])", s, re.I)
    if m and 1 <= int(m.group(1)) <= 31:
        return "%s-%02d-%02d" % (year, MON[m.group(2).lower()], int(m.group(1)))
    return None


def find_plot(s):
    m = re.search(r"(?<![a-z])(?:plot|plt|p)[-_ ]?(\d{2,5})(?!\d)", s, re.I)
    return "p" + m.group(1).zfill(4) if m else None


def clean_stem(stem, strip=True):
    s = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    if strip:
        s = re.sub(r"\s*[\(\[](copy|\d+)[\)\]]\s*$", "", s, flags=re.I)
        s = re.sub(r"\s+-\s+copy(\s*\(\d+\))?$", "", s, flags=re.I)
        for _ in range(2):
            s = re.sub(r"(^|[\s_-])(final|real|copy|new|latest)(?=$|[\s_-])", r"\1", s, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9.-]+", "_", s)
    s = re.sub(r"([_.-])\1+", r"\1", s)
    s = re.sub(r"[_-]{2,}", "_", s).strip("_.-")
    return s or "file"


def seg(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9._-]+", "_", s)).strip("_.")


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[._]+", "-", seg(s))).strip("-")


def fill_tpl(tpl, tok):
    s = re.sub(r"\{(\w+)\}", lambda m: tok.get(m.group(1), ""), tpl)
    return re.sub(r"[_-]{2,}", "_", s).strip("_-") or tok.get("stem") or "file"


def scan_folder(src):
    files = []
    for root, dirs, names in os.walk(src):
        dirs.sort()
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            try:
                st = os.stat(p)
            except OSError:
                continue
            d = rel.rsplit("/", 1)[0] if "/" in rel else ""
            stem, ext = split_ext(n)
            files.append({"path": rel, "dir": d, "name": n, "stem": stem, "ext": ext, "size": st.st_size,
                          "mtime": st.st_mtime, "junk": bool(JUNK.match(n) or JUNK_DIR.search(d))})
    seen = {}
    for f in files:
        if f["junk"]:
            continue
        k = (re.sub(r"[-_\s.]+", "_", clean_stem(f["stem"]).lower()), f["ext"], f["size"])
        f["dupOf"] = seen.get(k)
        seen.setdefault(k, f["path"])
    return files


def make_groups(files):
    live = [f for f in files if not f["junk"]]
    keyers = [lambda f: (f["dir"], f["ext"], re.sub(r"\d+", "#", f["stem"])), lambda f: (f["dir"], f["ext"]),
              lambda f: (f["dir"].split("/")[0], f["ext"]), lambda f: (f["ext"],)]
    for kf in keyers:
        g = {}
        for f in live:
            g.setdefault(kf(f), []).append(f)
        if len(g) <= 150:
            break
    groups = []
    for key, fs in sorted(g.items(), key=lambda kv: (kv[1][0]["dir"], re.sub(r"\d+", "#", kv[1][0]["stem"]))):
        f0 = fs[0]
        examples = list(dict.fromkeys(f["name"] for f in fs))[:3]
        gr = {"key": "\u0000".join(key), "dir": f0["dir"], "ext": f0["ext"], "pattern": re.sub(r"\d+", "#", f0["stem"]) + f0["ext"],
              "count": len(fs), "bytes": sum(f["size"] for f in fs), "examples": examples, "files": fs}
        gr.update(guess(f0["dir"], examples, f0["ext"]))
        groups.append(gr)
    for i, gr in enumerate(groups, 1):
        gr["id"] = "g%d" % i
    return groups


def file_date(f, src, year):
    if src == "none":
        return None
    if src == "modified":
        return datetime.date.fromtimestamp(f["mtime"]).isoformat()
    return find_date(f["name"], year) or find_date(f["dir"], year)


def build_plan(files, groups, answers, settings):
    site = slug(answers.get("site_code", ""))
    project = slug(answers.get("title", ""))[:40]
    year = (re.search(r"20[0-3]\d", str(answers.get("year", ""))) or [None])[0]
    num = settings.get("numbered", True)
    rows, pending, dates, subs = [], [], set(), {}
    for f in files:
        if f["junk"]:
            rows.append({"old": f["path"], "new": None, "size": f["size"], "action": "skip:junk"})
    for g in groups:
        seqs = {}
        ordered = sorted(((f, file_date(f, g["dateSrc"], year)) for f in g["files"]), key=lambda x: (x[1] or "9999", x[0]["mtime"], x[0]["path"]))
        for f, d in ordered:
            if g["exclude"]:
                rows.append({"old": f["path"], "new": None, "size": f["size"], "action": "skip:excluded"})
                continue
            plot = find_plot(f["name"]) or find_plot(f["dir"])
            seqs[d or ""] = seqs.get(d or "", 0) + 1
            parts = [p for p in g["folder"].replace("{date}", d or "undated").replace("{plot}", plot or "no-plot").split("/") if p]
            for p in parts:
                if re.match(r"^\d{4}-\d\d-\d\d$", p):
                    dates.add(p)
            if len(parts) > 1 and parts[0] in CAT_NUM:
                subs.setdefault(parts[0], set()).add(parts[1])
            pending.append((f, g, d, plot, seqs[d or ""], parts))
    session_of = {d: "%02d" % (i + 1) for i, d in enumerate(sorted(dates))}
    sub_num = {}
    for cat, s in subs.items():
        rank = lambda x: (DT_ORDER.index(x) if x in DT_ORDER else 500, x)
        for i, x in enumerate(sorted(s, key=rank)):
            sub_num[cat + "/" + x] = "%02d" % (i + 1)
    sessions = {d: {"n": n, "date": d, "dtypes": set()} for d, n in session_of.items()}

    def number(parts):
        if not num:
            return parts
        out = []
        for i, x in enumerate(parts):
            if i == 0 and x in CAT_NUM: x = CAT_NUM[x] + "_" + x
            elif i == 1 and (parts[0] + "/" + x) in sub_num: x = sub_num[parts[0] + "/" + x] + "_" + x
            elif re.match(r"^\d{4}-\d\d-\d\d$", x): x = session_of[x] + "_" + x
            elif x == "undated": x = "99_undated"
            out.append(x)
        return out
    used = set()

    def claim(p):
        base, ext = os.path.splitext(p)
        cand, n = p, 2
        while cand.lower() in used:
            cand = "%s_%d%s" % (base, n, ext)
            n += 1
        used.add(cand.lower())
        return cand
    for f, g, d, plot, seq, parts in pending:
        segs = number(parts)
        if f.get("dupOf") and settings.get("dupReview", True):
            segs = ["99_review" if num else "_review", "duplicates"] + segs
        if d and d in parts:
            sessions[d]["dtypes"].add(seg(g["dtype"]))
        stem = clean_stem(f["stem"], settings.get("strip", True))
        tok = {"date": d.replace("-", "") if d else "", "session": "s" + session_of[d] if d else "", "site": site,
               "dtype": seg(g["dtype"]), "plot": plot or "", "seq": "%04d" % seq, "stem": stem, "project": project}
        name = stem if g["rename"] == "keep" else fill_tpl("{session}_{date}_{site}_{dtype}_{plot}_{seq}" if g["rename"] == "seq" else settings.get("template", "{session}_{date}_{site}_{dtype}_{stem}"), tok)
        rows.append({"old": f["path"], "new": safe_rel(claim("/".join(segs) + "/" + name + f["ext"])), "size": f["size"], "action": "copy",
                     "dtype": seg(g["dtype"]), "group": g["id"], "dup": bool(f.get("dupOf"))})
    sess = [{"n": s["n"], "date": s["date"], "dtypes": sorted(s["dtypes"])} for s in sorted(sessions.values(), key=lambda s: s["date"])]
    return rows, sess


def fmt_bytes(b):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1000 or u == "TB":
            return ("%.0f %s" if b >= 100 or u == "B" else "%.1f %s") % (b, u)
        b /= 1000.0


def bar(frac, width=28):
    n = frac * width
    return "\u2588" * int(n) + ("\u258c" if n - int(n) >= 0.5 else "")


def print_summary(files, groups, rows, sessions):
    live = [f for f in files if not f["junk"]]
    print("\n%d files, %s, %d groups, %d junk, %d likely duplicates" % (len(live), fmt_bytes(sum(f["size"] for f in live)), len(groups),
                                                                  len(files) - len(live), sum(1 for f in live if f.get("dupOf"))))
    top = {}
    for r in rows:
        if r["new"]:
            k = r["new"].split("/")[0]
            c, b = top.get(k, (0, 0))
            top[k] = (c + 1, b + r["size"])
    mx = max((b for c, b in top.values()), default=1) or 1
    print("\nNew layout by size")
    for k in sorted(top):
        c, b = top[k]
        print("  %-14s %-29s %9s  %6d files" % (k, bar(b / mx), fmt_bytes(b), c))
    if sessions:
        print("\nSession calendar")
        for s in sessions:
            print("  s%s  %s  %s" % (s["n"], s["date"], ", ".join(s["dtypes"])))
    und = sum(1 for r in rows if r["new"] and "/99_undated/" in r["new"])
    uns = sum(1 for r in rows if r["new"] and r["new"].startswith(("98_other", "other")))
    if und or uns:
        print("\nCheck: %d files have no date (99_undated), %d files are unsorted." % (und, uns))


def session_payload(answers, settings, groups, rows, sessions, root_name):
    return {"tool": "fair-curate", "version": VERSION, "saved": datetime.datetime.now().isoformat(timespec="seconds"),
            "root_name": root_name, "answers": answers, "settings": settings,
            "groups": [{k: g[k] for k in ("id", "key", "dir", "ext", "pattern", "count", "bytes", "examples", "cat", "dtype", "folder", "rename", "dateSrc", "exclude")} for g in groups],
            "sessions": sessions, "rows": rows}


def write_readme(answers, sessions, rows, meta_dir):
    tree = {}
    for r in rows:
        if r["new"]:
            parts = r["new"].split("/")[:3]
            for i in range(1, len(parts)):
                k = "/".join(parts[:i])
                tree[k] = tree.get(k, 0) + 1
    lines = ["# " + (answers.get("title") or "Dataset"), "", answers.get("description", ""), "",
             "| Field | Value |", "|---|---|"]
    for k, lab in [("contact", "Contact"), ("institution", "Institution"), ("funding", "Funding"), ("organism", "Organism"),
                   ("site", "Site"), ("year", "Season"), ("license", "License"), ("doi", "DOI")]:
        if answers.get(k):
            lines.append("| %s | %s |" % (lab, answers[k]))
    lines += ["", "## Start here: follow the numbers", "", "00_docs → 01_metadata → 02_raw → 03_processed → 04_results → 05_code. "
              "Session numbers (s01, s02 …) are field days, shared by every sensor.", ""]
    if sessions:
        lines += ["| Session | Date | Data collected |", "|---|---|---|"] + ["| %s | %s | %s |" % (s["n"], s["date"], ", ".join(s["dtypes"])) for s in sessions] + [""]
    lines += ["## Folder layout", "", "```"] + ["%s%s/  (%d files)" % ("  " * k.count("/"), k.split("/")[-1], n) for k, n in sorted(tree.items())] + ["```", ""]
    if answers.get("processing"):
        lines += ["## Processing and provenance", "", answers["processing"], ""]
    lines += ["`%s/manifest.csv` maps every original path to its new path; `%s/runs.json` is the run history." % (meta_dir, meta_dir), "",
              "_Generated by fair_curate.py v%s on %s. Edit freely. For MIAPPE and Croissant files, load `%s/curator_session.json` into the HTML app._" % (VERSION, datetime.date.today(), meta_dir)]
    return "\n".join(lines) + "\n"


def load_session(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_scan(a):
    src = os.path.abspath(a.source)
    sess = load_session(a.session) if a.session else {}
    answers = dict(sess.get("answers", {}))
    settings = {"template": "{session}_{date}_{site}_{dtype}_{stem}", "strip": True, "dupReview": True, "numbered": True}
    settings.update(sess.get("settings", {}))
    if a.year:
        answers["year"] = a.year
    if a.site:
        answers["site_code"] = a.site
    if a.title:
        answers["title"] = a.title
    files = scan_folder(src)
    groups = make_groups(files)
    prev = {g["key"]: g for g in sess.get("groups", [])}
    reused = 0
    for g in groups:  # repopulate edits from a previous session (same folder + type + name pattern)
        p = prev.get(g["key"])
        if p:
            for k in ("cat", "dtype", "folder", "rename", "dateSrc", "exclude"):
                g[k] = p[k]
            reused += 1
    rows, sessions = build_plan(files, groups, answers, settings)
    print("Scanned %s" % src + (" (reused %d group settings from %s)" % (reused, a.session) if a.session else ""))
    print_summary(files, groups, rows, sessions)
    print("\nGroups (edit cat/dtype/folder/rename/dateSrc/exclude in the .plan.json, then scan again with --session):")
    for g in groups[:60]:
        print("  %-4s %-40s %5d  %-10s -> %s" % (g["id"], (g["dir"] + "/" if g["dir"] else "") + g["pattern"], g["count"], fmt_bytes(g["bytes"]), g["folder"]))
    out = a.out or (src.rstrip("/\\") + ".plan.json")
    payload = session_payload(answers, settings, groups, rows, sessions, os.path.basename(src))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    with open(out.replace(".json", ".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["original_path", "new_path", "size_bytes", "action"])
        for r in rows:
            w.writerow([r["old"], r["new"] or "", r["size"], r["action"]])
    print("\nPlan written: %s and %s" % (out, out.replace(".json", ".csv")))
    print("Next: python %s apply \"%s\" CLEAN_FOLDER --plan \"%s\"" % (os.path.basename(sys.argv[0]), a.source, out))


def read_plan(path):
    if path.endswith(".csv"):
        with open(path, encoding="utf-8") as fh:
            rows = [{"old": r["original_path"], "new": r["new_path"] or None, "size": int(r["size_bytes"] or 0),
                     "action": r["action"] if r["new_path"] else (r["action"] if r["action"].startswith("skip") else "skip:excluded")} for r in csv.DictReader(fh)]
        sib = path[:-4] + ".json"
        sess = load_session(sib) if os.path.isfile(sib) else {"answers": {}, "settings": {"numbered": True}, "sessions": []}
        sess["rows"] = rows
        return sess
    return load_session(path)


def cmd_apply(a):
    src = os.path.abspath(a.source)
    plan_path = a.plan or (src.rstrip("/\\") + ".plan.json")
    if not os.path.isfile(plan_path):
        sys.exit("No plan found at %s. Run: python %s scan \"%s\"" % (plan_path, os.path.basename(sys.argv[0]), a.source))
    sess = read_plan(plan_path)
    meta_dir = "01_metadata" if sess.get("settings", {}).get("numbered", True) else "metadata"
    rows = [dict(r) for r in sess["rows"]]
    for r in rows:
        if r.get("new") is None and r["action"] == "copy":
            r["action"] = "skip:excluded"
    sess["rows"] = rows
    extra = {"README.md": write_readme(sess.get("answers", {}), sess.get("sessions", []), rows, meta_dir),
             meta_dir + "/curator_session.json": json.dumps(sess, indent=1)}
    mode = "inplace" if a.inplace else ("move" if a.move else "copy")
    if mode != "inplace" and not a.dest:
        sys.exit("Give a CLEAN_FOLDER, or use --inplace to reorganize inside the messy folder.")
    run_plan(rows, extra, src, a.dest or src, mode, a.checksum, a.yes, a.run, meta_dir, undo_cmd="python %s undo" % os.path.basename(sys.argv[0]))


def main():
    ap = argparse.ArgumentParser(description="FAIR Folder Curator, command-line version %s (Baskar Lab, ISU)." % VERSION)
    sp = ap.add_subparsers(dest="cmd")
    s = sp.add_parser("scan", help="scan a folder and write an editable plan")
    s.add_argument("source"); s.add_argument("--out"); s.add_argument("--session", help="reuse answers and group edits from a curator_session.json or earlier .plan.json")
    s.add_argument("--year"); s.add_argument("--site", help="short site code used in file names"); s.add_argument("--title")
    p = sp.add_parser("apply", help="apply a plan (dry run unless --run)")
    p.add_argument("source"); p.add_argument("dest", nargs="?"); p.add_argument("--plan")
    p.add_argument("--run", "--apply", dest="run", action="store_true", help="actually change files")
    p.add_argument("--move", action="store_true"); p.add_argument("--inplace", action="store_true", help="rename/move inside the same folder")
    p.add_argument("--checksum", action="store_true"); p.add_argument("--yes", action="store_true")
    u = sp.add_parser("undo", help="reverse the latest run (or --id)"); u.add_argument("folder"); u.add_argument("--id"); u.add_argument("--yes", action="store_true")
    r = sp.add_parser("runs", help="list run history"); r.add_argument("folder")
    a = ap.parse_args()
    if a.cmd == "scan": cmd_scan(a)
    elif a.cmd == "apply": cmd_apply(a)
    elif a.cmd == "undo": undo_run(a.folder, a.yes, a.id)
    elif a.cmd == "runs": list_runs(a.folder)
    else: ap.print_help()


if __name__ == "__main__":
    main()
