#!/usr/bin/env python3
"""make_manifest.py: checksums + quality report for one organized dataset folder.

Usage (Python 3.8+, no installs):
    python make_manifest.py "path/to/2026_AEA_my-dataset"
    python make_manifest.py "path/to/folder" --id-regex "^\\d{4}_[A-Z]+_R\\d{2}_C\\d{2}"

Writes into <folder>/01_metadata/:
    MANIFEST.sha256   one line per file: <sha256>  <relative path>   (verify later with: sha256sum -c)
    manifest.csv      path, bytes, sha256, modified
    qc_report.md      problems found: junk files, duplicates, empty files, unsafe names,
                      files outside the numbered folders, long Windows paths, ID pattern misses
It also fills the sha256 of any croissant.json file entry whose contentUrl matches a real file.
Nothing is moved or deleted.
"""
import argparse, csv, hashlib, json, os, re, sys, time
from pathlib import Path

JUNK = re.compile(r"^(\.ds_store|thumbs\.db|desktop\.ini|~\$.*|\._.*|.*\.tmp)$", re.I)
UNSAFE = re.compile(r"[^A-Za-z0-9._\-]")
TOP = {"README.md", "00_docs", "01_metadata", "02_raw", "03_processed", "04_results", "05_code", "99_review", "splits", "LICENSE", "CITATION.cff"}
SKIP_DIRS = {".git", ".dvc", "__pycache__", ".ipynb_checkpoints"}
OWN = {"MANIFEST.sha256", "manifest.csv", "qc_report.md"}


def sha256(p, buf=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(buf), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--id-regex", default="", help="regular expression every data file name under 02_raw should match")
    a = ap.parse_args()
    root = Path(a.folder).resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    meta = root / "01_metadata"
    meta.mkdir(exist_ok=True)
    idre = re.compile(a.id_regex) if a.id_regex else None

    rows, seen = [], {}
    issues = {k: [] for k in ["junk", "duplicate", "empty", "unsafe name", "outside layout", "long path", "ID pattern"]}
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            p = Path(dp) / fn
            rel = p.relative_to(root).as_posix()
            if rel.startswith("01_metadata/") and fn in OWN:
                continue
            files.append((p, rel))
    t0 = time.time()
    for i, (p, rel) in enumerate(files, 1):
        size = p.stat().st_size
        digest = sha256(p)
        rows.append({"path": rel, "bytes": size, "sha256": digest,
                     "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(p.stat().st_mtime))})
        name = p.name
        if JUNK.match(name):
            issues["junk"].append(rel)
        elif digest in seen:
            issues["duplicate"].append(f"{rel}  (same bytes as {seen[digest]})")
        else:
            seen[digest] = rel
        if size == 0:
            issues["empty"].append(rel)
        if UNSAFE.search(name):
            issues["unsafe name"].append(rel)
        if rel.split("/")[0] not in TOP:
            issues["outside layout"].append(rel)
        if len(str(p)) > 240:
            issues["long path"].append(rel)
        if idre and rel.startswith("02_raw/") and not idre.search(name) and not name.startswith("_"):
            issues["ID pattern"].append(rel)
        if i % 200 == 0:
            print(f"  hashed {i}/{len(files)} files ({time.time() - t0:.0f} s)")

    # fill sha256 in croissant.json where contentUrl matches a file
    cj = meta / "croissant.json"
    filled = 0
    if cj.exists():
        try:
            doc = json.loads(cj.read_text(encoding="utf-8"))
            by_path = {r["path"]: r["sha256"] for r in rows}
            for d in doc.get("distribution", []):
                url = d.get("contentUrl", "")
                if url in by_path:
                    d["sha256"] = by_path[url]
                    filled += 1
            cj.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        except Exception as e:  # keep going; report it
            issues.setdefault("croissant.json", []).append(f"could not update: {e}")

    for r in rows:  # croissant.json may have changed: re-hash it
        if r["path"] == "01_metadata/croissant.json":
            r["sha256"] = sha256(cj)
            r["bytes"] = cj.stat().st_size
    with open(meta / "MANIFEST.sha256", "w", newline="\n") as f:
        for r in rows:
            f.write(f"{r['sha256']}  {r['path']}\n")
    with open(meta / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256", "modified"])
        w.writeheader()
        w.writerows(rows)

    total = sum(r["bytes"] for r in rows)
    n_issues = sum(len(v) for v in issues.values())
    with open(meta / "qc_report.md", "w", encoding="utf-8") as f:
        f.write(f"# QC report: {root.name}\n\n")
        f.write(f"- Files: {len(rows)}\n- Total size: {total / 1e9:.3f} GB\n- Problems found: {n_issues}\n")
        f.write(f"- croissant.json entries given a checksum: {filled}\n- Generated: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("Fix or move problem files to 99_review/, then run this script again.\n\n")
        for k, v in issues.items():
            f.write(f"## {k} ({len(v)})\n")
            f.write("".join(f"- {x}\n" for x in v[:200]) or "- none\n")
            if len(v) > 200:
                f.write(f"- ... and {len(v) - 200} more\n")
            f.write("\n")
    print(f"Done: {len(rows)} files, {total / 1e9:.3f} GB, {n_issues} problems.")
    print(f"Wrote {meta / 'MANIFEST.sha256'}, manifest.csv, qc_report.md")


if __name__ == "__main__":
    main()
