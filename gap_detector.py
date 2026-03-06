#!/usr/bin/env python3
"""
gap_detector.py
Finds numbered sequences in video filenames and reports gaps.

Example: if you have ep1, ep2, ep4, ep5 → gap at ep3
Also finds: raw files with no corresponding finished version.

Usage:
    python3 gap_detector.py [--root ~/Movies] [--csv media_inventory.csv] [--tag]
"""

import re
import csv
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from macos_tagger import set_finder_label
from config import FINDER_TAGS, VIDEO_EXTENSIONS

# ── Number extraction ──────────────────────────────────────────────────────────

NUMBER_PATTERN = re.compile(
    r'^(.*?)[\s\-_]+(\d+)[\s\-_]?(.*)$'
)


def extract_series(filename: str) -> tuple[str, int] | None:
    """
    Try to extract (series_prefix, episode_number) from a filename.
    Returns None if no number found.
    """
    stem = Path(filename).stem
    m = NUMBER_PATTERN.match(stem)
    if not m:
        return None
    prefix = m.group(1).strip()
    number = int(m.group(2))
    # Filter out camera filenames like P1100326
    if re.match(r'^[A-Z]+$', prefix):
        return None
    # Filter out date-based filenames like 2025-08-07
    if re.match(r'^\d{4}-\d{2}-\d{2}', prefix):
        return None
    # Minimum prefix length
    if len(prefix) < 3:
        return None
    return prefix, number


# ── Load files ────────────────────────────────────────────────────────────────

def load_from_csv(csv_path: Path) -> list[dict]:
    with open(csv_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_from_scan(root: Path) -> list[dict]:
    records = []
    for p in root.rglob("*"):
        if (p.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}
                and p.is_file()
                and "Final Cut Backups" not in str(p)
                and ".fcpbundle" not in str(p)):
            records.append({
                "name":      p.name,
                "folder":    str(p.relative_to(root).parent),
                "full_path": str(p),
            })
    return records


# ── Gap detection ─────────────────────────────────────────────────────────────

def find_gaps(records: list[dict]) -> list[dict]:
    """
    Group files by (folder, series_prefix) and find gaps in episode numbers.
    Returns list of gap reports.
    """
    # Group by folder + series prefix
    series: dict[tuple, dict[int, str]] = defaultdict(dict)

    for r in records:
        result = extract_series(r["name"])
        if result is None:
            continue
        prefix, number = result
        key = (r["folder"], prefix)
        series[key][number] = r["full_path"]

    gaps = []
    for (folder, prefix), episodes in series.items():
        if len(episodes) < 2:
            continue

        nums     = sorted(episodes.keys())
        min_n    = nums[0]
        max_n    = nums[-1]
        expected = set(range(min_n, max_n + 1))
        found    = set(nums)
        missing  = sorted(expected - found)

        if missing:
            gaps.append({
                "folder":   folder,
                "series":   prefix,
                "found":    nums,
                "missing":  missing,
                "files":    episodes,
                "range":    f"{min_n}–{max_n}",
            })

    return gaps


# ── Raw-without-finished detection ───────────────────────────────────────────

def find_orphan_raw(root: Path) -> list[dict]:
    """
    Find folders named 'גלם'/'raw'/'footage' that have NO sibling 'מוכן' folder.
    These are raw footage never edited.
    """
    orphans = []
    raw_keywords  = ["גלם", "raw", "footage"]
    done_keywords = ["מוכן", "finished", "done", "מוכנים"]

    for folder in root.rglob("*"):
        if not folder.is_dir():
            continue
        folder_name = folder.name
        if any(kw in folder_name for kw in raw_keywords):
            parent = folder.parent
            siblings = [s.name for s in parent.iterdir() if s.is_dir() and s != folder]
            has_done = any(
                any(kw in sib for kw in done_keywords)
                for sib in siblings
            )
            if not has_done:
                files = list(folder.rglob("*"))
                video_files = [
                    f for f in files
                    if f.is_file() and f.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}
                ]
                if video_files:
                    total_size = sum(f.stat().st_size for f in video_files)
                    orphans.append({
                        "folder":      str(folder.relative_to(root)),
                        "full_path":   str(folder),
                        "file_count":  len(video_files),
                        "total_size":  total_size,
                    })

    return orphans


# ── Report ────────────────────────────────────────────────────────────────────

def format_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def print_report(gaps: list[dict], orphans: list[dict], tag: bool = False):
    print(f"\n🔍 Gap Detector Report")
    print(f"   {len(gaps)} series with gaps | {len(orphans)} orphan raw folders\n")

    if gaps:
        print("─" * 60)
        print("📊 SEQUENCE GAPS")
        print("─" * 60)
        for g in sorted(gaps, key=lambda x: x["series"]):
            print(f"\n  Series:  {g['series']}")
            print(f"  Folder:  {g['folder']}")
            print(f"  Found:   {g['found']}")
            print(f"  Missing: {g['missing']}  ← GAPS")
            if tag:
                # Tag files adjacent to gaps as check-gap
                for num in g["missing"]:
                    for adjacent in [num - 1, num + 1]:
                        if adjacent in g["files"]:
                            path = Path(g["files"][adjacent])
                            set_finder_label(path, FINDER_TAGS["check-gap"])
                            print(f"  🟠 Tagged: ep{adjacent} ({path.name})")

    if orphans:
        print("\n" + "─" * 60)
        print("📁 ORPHAN RAW FOLDERS (no matching finished folder)")
        print("─" * 60)
        for o in orphans:
            print(f"\n  Folder: {o['folder']}")
            print(f"  Files:  {o['file_count']} | Size: {format_size(o['total_size'])}")
            if tag:
                folder_path = Path(o["full_path"])
                for f in folder_path.rglob("*"):
                    if f.is_file() and f.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}:
                        set_finder_label(f, FINDER_TAGS["check-gap"])
                print(f"  🟠 Tagged all files as check-gap")

    if not gaps and not orphans:
        print("  ✅ No gaps or orphan folders found!\n")

    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Find sequence gaps and orphan raw footage")
    parser.add_argument("--root", default=str(Path.home() / "Movies"), help="Root folder to scan")
    parser.add_argument("--csv",  default="",    help="Use existing CSV instead of re-scanning")
    parser.add_argument("--tag",  action="store_true", help="Apply 🟠 check-gap tags to affected files")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Folder not found: {root}")
        sys.exit(1)

    if args.csv:
        csv_path = Path(args.csv)
        print(f"\n📂 Loading from CSV: {csv_path}")
        records = load_from_csv(csv_path)
    else:
        print(f"\n📂 Scanning: {root}")
        records = load_from_scan(root)

    print(f"   {len(records)} video files loaded")

    gaps    = find_gaps(records)
    orphans = find_orphan_raw(root)

    print_report(gaps, orphans, tag=args.tag)


if __name__ == "__main__":
    main()
