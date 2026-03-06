#!/usr/bin/env python3
"""
find_media.py
Search video files by business, type, name, status, size, or date.
Reads from media_inventory.csv. Optionally opens result in Finder.

Usage:
    python3 find_media.py --type course
    python3 find_media.py --business finance --type social
    python3 find_media.py --name "בלי לחץ"
    python3 find_media.py --status done
    python3 find_media.py --recent 30
    python3 find_media.py --large 500mb
    python3 find_media.py --type course --open   # open first result in Finder
"""

import csv
import argparse
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from config import VIDEO_EXTENSIONS

DEFAULT_CSV = Path(__file__).parent / "media_inventory.csv"


# ── Size parser ───────────────────────────────────────────────────────────────

def parse_size(size_str: str) -> int:
    """Parse size string like '500mb', '1.5gb', '100kb' → bytes."""
    m = re.match(r"([\d.]+)\s*(b|kb|mb|gb)?", size_str.lower())
    if not m:
        return 0
    num   = float(m.group(1))
    unit  = m.group(2) or "b"
    mult  = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}[unit]
    return int(num * mult)


def parse_size_field(size_str: str) -> int:
    """Parse size string from CSV like '1.5 GB' → bytes."""
    m = re.match(r"([\d.]+)\s*(B|KB|MB|GB|TB)", size_str.strip())
    if not m:
        return 0
    num  = float(m.group(1))
    unit = m.group(2)
    mult = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}[unit]
    return int(num * mult)


def parse_duration(dur_str: str) -> int:
    """Parse duration string '1:23:45' or '5:30' → seconds."""
    parts = dur_str.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except Exception:
        return 0


# ── Load inventory ────────────────────────────────────────────────────────────

def load_inventory(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        print(f"   Run: python3 media_inventory.py first")
        sys.exit(1)
    with open(csv_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── Filter ────────────────────────────────────────────────────────────────────

def filter_records(records: list[dict], args) -> list[dict]:
    results = records

    if args.business:
        q = args.business.lower()
        results = [r for r in results if q in r.get("business", "").lower()]

    if args.type:
        # Check against the 'folder' and 'name' fields for type keywords
        from config import TYPE_RULES
        type_lower = args.type.lower()
        # Find keywords for this type
        type_kws = []
        for type_tag, kws in TYPE_RULES:
            if type_tag == type_lower:
                type_kws = kws
                break
        if type_kws:
            results = [
                r for r in results
                if any(kw in r.get("folder", "") or kw in r.get("name", "") for kw in type_kws)
            ]
        else:
            # Fallback: search type string in folder/name
            results = [r for r in results if type_lower in r.get("folder", "").lower()]

    if args.name:
        q = args.name.lower()
        results = [r for r in results
                   if q in r.get("name", "").lower() or q in r.get("folder", "").lower()]

    if args.status:
        s = args.status.lower()
        if s in ("done", "finished", "מוכן"):
            results = [r for r in results if "מוכן" in r.get("status", "")]
        elif s in ("raw", "גלם"):
            results = [r for r in results if "גלם" in r.get("status", "")]

    if args.recent:
        cutoff = (datetime.now() - timedelta(days=args.recent)).strftime("%Y-%m-%d")
        results = [r for r in results if r.get("created", "") >= cutoff]

    if args.large:
        min_bytes = parse_size(args.large)
        results = [r for r in results if parse_size_field(r.get("size", "0 B")) >= min_bytes]

    if args.ext:
        ext = args.ext.lower().lstrip(".")
        results = [r for r in results if r.get("name", "").lower().endswith(f".{ext}")]

    return results


# ── Format output ──────────────────────────────────────────────────────────────

def format_size(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def print_results(results: list[dict], limit: int = 50):
    total_size = sum(parse_size_field(r.get("size", "0 B")) for r in results)
    total_dur  = sum(parse_duration(r.get("duration", "0")) for r in results)

    print(f"\n🔍 Found: {len(results)} files | {format_size(total_size)} | {format_duration(total_dur)}\n")

    shown = results[:limit]
    for r in shown:
        status_icon = {"✅ מוכן": "🟢", "🎬 גלם": "🎬", "🔄 לא ידוע": "⬜"}.get(r.get("status", ""), "⬜")
        print(f"  {status_icon} {r['name']}")
        print(f"     📁 {r['folder']}")
        print(f"     ⏱ {r['duration']:>7}  💾 {r['size']:>10}  📅 {r['created']}  🏷 {r['business']}")
        print()

    if len(results) > limit:
        print(f"  ... and {len(results) - limit} more (use --limit N to show more)\n")


def format_duration(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s   = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ── Open in Finder ─────────────────────────────────────────────────────────────

def open_in_finder(path_str: str):
    subprocess.run(["open", "-R", path_str])


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Search video inventory by tags, type, name, etc.")
    parser.add_argument("--csv",      default=str(DEFAULT_CSV),   help="Path to media_inventory.csv")
    parser.add_argument("--business", help="Filter by business: finance, therapy, training, personal")
    parser.add_argument("--type",     help="Filter by type: course, social, podcast, lecture, promo, raw, template")
    parser.add_argument("--name",     help="Search in filename or folder name")
    parser.add_argument("--status",   help="Filter by status: done, raw")
    parser.add_argument("--recent",   type=int, help="Modified in last N days")
    parser.add_argument("--large",    help="Larger than (e.g. 500mb, 1gb)")
    parser.add_argument("--ext",      help="File extension filter (mp4, mov, mkv)")
    parser.add_argument("--limit",    type=int, default=50, help="Max results to show (default 50)")
    parser.add_argument("--open",     action="store_true", help="Open first result folder in Finder")
    args = parser.parse_args()

    if not any([args.business, args.type, args.name, args.status, args.recent, args.large, args.ext]):
        parser.print_help()
        print("\n  Examples:")
        print("    python3 find_media.py --type course")
        print("    python3 find_media.py --business finance --type social")
        print("    python3 find_media.py --name 'בלי לחץ'")
        print("    python3 find_media.py --status done --large 500mb")
        print()
        return

    records = load_inventory(Path(args.csv))
    results = filter_records(records, args)

    if not results:
        print("\n  No results found.\n")
        return

    print_results(results, limit=args.limit)

    if args.open and results:
        path = Path(results[0]["full_path"])
        open_in_finder(str(path.parent))
        print(f"  📂 Opened in Finder: {path.parent.name}\n")


if __name__ == "__main__":
    main()
