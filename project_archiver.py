#!/usr/bin/env python3
"""
project_archiver.py
Scans for video project folders and recommends archiving actions.
Does NOT move or delete anything — report only.

Usage:
    python3 project_archiver.py [--root ~/Movies]

A "project" is any folder that contains a גלם or מוכן subfolder.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from config import VIDEO_EXTENSIONS

# ── Thresholds ─────────────────────────────────────────────────────────────────

ACTIVE_DAYS    = 30   # Modified within 30 days = active
COMPLETE_DAYS  = 90   # No changes for 90 days = complete/archive candidate
STALE_DAYS     = 180  # No changes for 180 days = stale, strong archive candidate

RAW_KEYWORDS   = ["גלם", "raw", "footage"]
DONE_KEYWORDS  = ["מוכן", "finished", "done", "מוכנים"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def format_size(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def folder_video_size(path: Path) -> int:
    return sum(
        f.stat().st_size for f in path.rglob("*")
        if f.is_file() and f.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}
    )


def most_recent_mtime(path: Path) -> datetime:
    try:
        times = [
            datetime.fromtimestamp(f.stat().st_mtime)
            for f in path.rglob("*") if f.is_file()
        ]
        return max(times) if times else datetime.min
    except Exception:
        return datetime.min


def days_since(dt: datetime) -> int:
    return (datetime.now() - dt).days


# ── Project discovery ──────────────────────────────────────────────────────────

def find_projects(root: Path) -> list[dict]:
    """
    Walk root looking for "project containers" — folders that directly
    contain raw or finished subfolders.
    """
    projects = []
    seen     = set()

    for child in root.rglob("*"):
        if not child.is_dir():
            continue
        name = child.name

        is_raw  = any(kw in name for kw in RAW_KEYWORDS)
        is_done = any(kw in name for kw in DONE_KEYWORDS)

        if not (is_raw or is_done):
            continue

        parent = child.parent
        if parent in seen or parent == root:
            continue
        seen.add(parent)

        # Gather info about this project container
        siblings = [s for s in parent.iterdir() if s.is_dir()]
        raw_dirs  = [s for s in siblings if any(kw in s.name for kw in RAW_KEYWORDS)]
        done_dirs = [s for s in siblings if any(kw in s.name for kw in DONE_KEYWORDS)]

        raw_size  = sum(folder_video_size(d) for d in raw_dirs)
        done_size = sum(folder_video_size(d) for d in done_dirs)
        total_size = folder_size(parent)

        last_modified     = most_recent_mtime(parent)
        days_old          = days_since(last_modified)
        last_modified_str = last_modified.strftime("%Y-%m-%d") if last_modified != datetime.min else "unknown"

        # Determine status
        has_raw  = bool(raw_dirs)
        has_done = bool(done_dirs)

        if days_old <= ACTIVE_DAYS:
            status = "🟢 ACTIVE"
            recommendation = "Keep — recently modified"
        elif has_done and has_raw and days_old > COMPLETE_DAYS:
            status = "🟡 COMPLETED"
            recommendation = f"Archive raw ({format_size(raw_size)}) — done folder exists, {days_old}d ago"
        elif has_done and not has_raw:
            if days_old > STALE_DAYS:
                status = "🟠 STALE"
                recommendation = f"Archive whole project — {days_old}d since last change"
            else:
                status = "🟡 DONE"
                recommendation = "Finished — consider archiving"
        elif has_raw and not has_done:
            if days_old > STALE_DAYS:
                status = "🔴 ORPHAN RAW"
                recommendation = f"No finished version after {days_old}d — delete candidate"
            else:
                status = "⬜ IN PROGRESS"
                recommendation = "Raw only — editing in progress?"
        else:
            status = "❓ UNCLEAR"
            recommendation = "Review manually"

        projects.append({
            "name":         parent.name,
            "path":         str(parent.relative_to(root)),
            "full_path":    str(parent),
            "has_raw":      has_raw,
            "has_done":     has_done,
            "raw_dirs":     [d.name for d in raw_dirs],
            "done_dirs":    [d.name for d in done_dirs],
            "raw_size":     raw_size,
            "done_size":    done_size,
            "total_size":   total_size,
            "last_modified": last_modified_str,
            "days_old":     days_old,
            "status":       status,
            "recommendation": recommendation,
        })

    return sorted(projects, key=lambda x: x["days_old"], reverse=True)


# ── Report ────────────────────────────────────────────────────────────────────

def print_report(projects: list[dict], root: Path):
    total_raw_size = sum(p["raw_size"] for p in projects if "COMPLETED" in p["status"] or "ORPHAN" in p["status"])

    print(f"\n📁 Project Archiver Report — {root}")
    print(f"   {len(projects)} projects found | {format_size(total_raw_size)} potential raw savings\n")

    status_order = ["🔴 ORPHAN RAW", "🟠 STALE", "🟡 COMPLETED", "🟡 DONE", "🟢 ACTIVE", "⬜ IN PROGRESS", "❓ UNCLEAR"]

    for status_filter in status_order:
        group = [p for p in projects if p["status"] == status_filter]
        if not group:
            continue

        print(f"\n{'─' * 60}")
        print(f"  {status_filter}  ({len(group)} projects)")
        print(f"{'─' * 60}")

        for p in group:
            print(f"\n  📂 {p['name']}")
            print(f"     Path:     {p['path']}")
            print(f"     Last mod: {p['last_modified']} ({p['days_old']} days ago)")
            print(f"     Size:     total={format_size(p['total_size'])} | raw={format_size(p['raw_size'])} | done={format_size(p['done_size'])}")
            if p["raw_dirs"]:
                print(f"     Raw:      {', '.join(p['raw_dirs'])}")
            if p["done_dirs"]:
                print(f"     Done:     {', '.join(p['done_dirs'])}")
            print(f"     💡 {p['recommendation']}")

    print(f"\n{'═' * 60}")
    print(f"  💾 Archive raw folders of completed projects → save ~{format_size(total_raw_size)}")
    print(f"  ⚠️  This report is READ-ONLY. No files were moved.")
    print(f"{'═' * 60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Identify archivable video projects")
    parser.add_argument("--root", default=str(Path.home() / "Movies"), help="Root folder to scan")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Folder not found: {root}")
        sys.exit(1)

    print(f"\n🔍 Scanning projects in: {root}")
    projects = find_projects(root)
    print_report(projects, root)


if __name__ == "__main__":
    main()
