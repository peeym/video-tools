#!/usr/bin/env python3
"""
media_inventory.py
Scans a folder tree for video files and generates a full inventory
using ffprobe — no AI tokens, pure code.

Usage:
    python3 media_inventory.py [--root /path/to/scan] [--out report.md]
"""

import subprocess
import json
import os
import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from config import classify_business, classify_status, VIDEO_EXTENSIONS

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_ROOT = Path.home() / "Movies"

# ── Helpers ───────────────────────────────────────────────────────────────────


def format_duration(seconds: float) -> str:
    if seconds <= 0:
        return "—"
    td = timedelta(seconds=int(seconds))
    h, rem = divmod(td.seconds, 3600)
    m, s = divmod(rem, 60)
    if td.days > 0 or h > 0:
        return f"{td.days * 24 + h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_size(bytes_: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def probe_file(path: Path) -> dict:
    """Run ffprobe on a file, return metadata dict."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
    except Exception:
        return {}

    fmt = data.get("format", {})
    streams = data.get("streams", [])

    # Find video stream
    video_stream = next(
        (s for s in streams if s.get("codec_type") == "video"), {}
    )

    duration = float(fmt.get("duration", 0))
    size     = int(fmt.get("size", 0))
    width    = video_stream.get("width", 0)
    height   = video_stream.get("height", 0)
    codec    = video_stream.get("codec_name", "—")

    # Creation date: try format tags first, fall back to file mtime
    tags     = fmt.get("tags", {})
    created  = (
        tags.get("creation_time")
        or tags.get("date")
        or datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    )
    # Trim to date only
    if "T" in created:
        created = created[:10]

    return {
        "duration_sec": duration,
        "duration":     format_duration(duration),
        "size_bytes":   size,
        "size":         format_size(size),
        "resolution":   f"{width}×{height}" if width else "—",
        "codec":        codec,
        "created":      created,
    }


def scan(root: Path) -> list[dict]:
    """Walk root recursively and collect all video file records."""
    records = []
    all_files = [
        p for p in root.rglob("*")
        if p.suffix in VIDEO_EXTENSIONS and p.is_file()
        and "Final Cut Backups" not in str(p)   # skip FCP backups
        and ".fcpbundle" not in str(p)           # skip inside FCP bundles
    ]

    total = len(all_files)
    for i, path in enumerate(all_files, 1):
        print(f"\r  [{i}/{total}] {path.name[:50]:<50}", end="", flush=True)
        meta = probe_file(path)
        if not meta:
            continue

        rel = path.relative_to(root)
        records.append({
            "name":         path.name,
            "folder":       str(rel.parent),
            "business":     classify_business(path),
            "status":       classify_status(path),
            "duration":     meta["duration"],
            "duration_sec": meta["duration_sec"],
            "size":         meta["size"],
            "size_bytes":   meta["size_bytes"],
            "resolution":   meta["resolution"],
            "codec":        meta["codec"],
            "created":      meta["created"],
            "full_path":    str(path),
        })

    print()  # newline after progress
    return records


# ── Output ────────────────────────────────────────────────────────────────────

def write_markdown(records: list[dict], out_path: Path, root: Path):
    total_size = sum(r["size_bytes"] for r in records)
    total_duration = sum(r["duration_sec"] for r in records)

    by_business = {}
    for r in records:
        by_business.setdefault(r["business"], []).append(r)

    lines = [
        "# 🎬 Media Inventory",
        f"> נוצר: {datetime.now().strftime('%d/%m/%Y %H:%M')}  ",
        f"> שורש: `{root}`  ",
        f"> סה״כ: **{len(records)} קבצים** | **{format_size(total_size)}** | **{format_duration(total_duration)}**",
        "",
    ]

    for business, recs in sorted(by_business.items()):
        biz_size = sum(r["size_bytes"] for r in recs)
        biz_dur  = sum(r["duration_sec"] for r in recs)
        lines += [
            f"## {business}",
            f"> {len(recs)} קבצים | {format_size(biz_size)} | {format_duration(biz_dur)}",
            "",
            "| קובץ | תיקייה | סטטוס | אורך | גודל | רזולוציה | תאריך |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in sorted(recs, key=lambda x: x["folder"]):
            lines.append(
                f"| {r['name']} | {r['folder']} | {r['status']} "
                f"| {r['duration']} | {r['size']} | {r['resolution']} | {r['created']} |"
            )
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ Markdown → {out_path}")


def write_csv(records: list[dict], out_path: Path):
    fields = ["name", "folder", "business", "status",
              "duration", "size", "resolution", "codec", "created", "full_path"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    print(f"  ✅ CSV     → {out_path}")


def print_summary(records: list[dict]):
    print("\n" + "═" * 60)
    print(f"  סה״כ קבצים:  {len(records)}")
    print(f"  סה״כ גודל:   {format_size(sum(r['size_bytes'] for r in records))}")
    print(f"  סה״כ אורך:   {format_duration(sum(r['duration_sec'] for r in records))}")
    print()

    by_biz = {}
    for r in records:
        by_biz.setdefault(r["business"], []).append(r)
    for biz, recs in sorted(by_biz.items()):
        print(f"  {biz}: {len(recs)} קבצים | {format_size(sum(r['size_bytes'] for r in recs))}")

    print()
    by_status = {}
    for r in records:
        by_status.setdefault(r["status"], []).append(r)
    for status, recs in sorted(by_status.items()):
        print(f"  {status}: {len(recs)} קבצים")
    print("═" * 60)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Video media inventory using ffprobe")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root folder to scan")
    parser.add_argument("--out",  default="media_inventory",  help="Output filename (no extension)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Folder not found: {root}")
        sys.exit(1)

    out_md  = Path(args.out).with_suffix(".md")
    out_csv = Path(args.out).with_suffix(".csv")

    print(f"\n🔍 Scanning: {root}")
    print("  (skipping FCP bundles and backups)\n")

    records = scan(root)

    if not records:
        print("❌ No video files found.")
        sys.exit(1)

    print_summary(records)
    write_markdown(records, out_md,  root)
    write_csv(records, out_csv)
    print()


if __name__ == "__main__":
    main()
