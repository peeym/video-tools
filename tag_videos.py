#!/usr/bin/env python3
"""
tag_videos.py
Apply 5-dimension macOS text tags to all video files.
Tags are searchable via Spotlight and visible in Finder sidebar.

Dimensions: status · source · content · business · project

Usage:
    python3 tag_videos.py --dry-run          # preview tags, no changes
    python3 tag_videos.py                    # apply to ~/Movies
    python3 tag_videos.py --root ~/Movies    # explicit root
    python3 tag_videos.py --show-all         # show untagged files too
    python3 tag_videos.py --file path/to/file.mp4   # tag a single file
    python3 tag_videos.py --report           # show tag distribution summary
"""

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from config import VIDEO_EXTENSIONS, TAG_RULES

DEFAULT_ROOT = Path.home() / "Movies"


# ── Tag computation ────────────────────────────────────────────────────────────

def compute_tags(path: Path) -> dict[str, str]:
    """Return {dimension: tag} for each dimension that matches."""
    path_str = str(path)
    result = {}
    for dimension, rules in TAG_RULES.items():
        for tag, keywords in rules:
            if any(kw in path_str for kw in keywords):
                result[dimension] = tag
                break
    return result


def tags_to_list(dim_tags: dict[str, str]) -> list[str]:
    """Convert dimension→tag dict to flat list for xattr."""
    return list(dim_tags.values())


# ── xattr read/write ───────────────────────────────────────────────────────────

def get_current_tags(path: Path) -> list[str]:
    result = subprocess.run(
        ["xattr", "-px", "com.apple.metadata:_kMDItemUserTags", str(path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    try:
        hex_str = result.stdout.strip().replace(" ", "").replace("\n", "")
        return plistlib.loads(bytes.fromhex(hex_str))
    except Exception:
        return []


def set_tags(path: Path, tags: list[str]) -> bool:
    try:
        plist_bytes = plistlib.dumps(tags, fmt=plistlib.FMT_BINARY)
        result = subprocess.run(
            ["xattr", "-wx", "com.apple.metadata:_kMDItemUserTags",
             plist_bytes.hex(), str(path)],
            capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


def merge_tags(existing: list[str], new_tags: list[str]) -> list[str]:
    """Add new tags without removing manually-set ones."""
    return list(dict.fromkeys(existing + new_tags))


# ── Format ─────────────────────────────────────────────────────────────────────

DIM_ICONS = {
    "status":   "📍",
    "source":   "📡",
    "content":  "🎬",
    "business": "🏢",
    "project":  "📁",
}


def format_dim_tags(dim_tags: dict[str, str]) -> str:
    parts = []
    for dim, tag in dim_tags.items():
        parts.append(f"{DIM_ICONS.get(dim, '·')} {tag}")
    return "  ".join(parts) if parts else "—"


# ── Main scan ──────────────────────────────────────────────────────────────────

def run(root: Path, dry_run: bool, show_all: bool, single_file: Path | None):
    if single_file:
        files = [single_file]
    else:
        exts = {e.lower() for e in VIDEO_EXTENSIONS}
        files = [
            p for p in root.rglob("*")
            if p.is_file()
            and p.suffix.lower() in exts
            and ".fcpbundle" not in str(p)
            and "Final Cut Backups" not in str(p)
        ]

    total        = len(files)
    tagged_count = 0
    skipped      = 0
    tag_stats    = defaultdict(lambda: defaultdict(int))  # dim → tag → count

    print(f"\n🏷️  {'DRY RUN — ' if dry_run else ''}Tagging {total} files\n")

    for i, path in enumerate(files, 1):
        dim_tags = compute_tags(path)
        new_tags = tags_to_list(dim_tags)

        for dim, tag in dim_tags.items():
            tag_stats[dim][tag] += 1

        if not new_tags:
            skipped += 1
            if show_all:
                rel = str(path.relative_to(root)) if not single_file else path.name
                print(f"  [{i:4d}/{total}] ⬜  {rel[:70]}")
            continue

        tagged_count += 1
        rel = str(path.relative_to(root)) if not single_file else path.name
        if len(rel) > 70:
            rel = "…" + rel[-69:]

        status = "→" if dry_run else ""
        if not dry_run:
            existing = get_current_tags(path)
            merged   = merge_tags(existing, new_tags)
            ok       = set_tags(path, merged)
            status   = "✓" if ok else "✗"

        print(f"  [{i:4d}/{total}] {status}  {rel}")
        print(f"           {format_dim_tags(dim_tags)}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(f"  Tagged:    {tagged_count} files")
    print(f"  No match:  {skipped} files\n")

    for dim in TAG_RULES:
        if tag_stats[dim]:
            print(f"  {DIM_ICONS.get(dim, '·')} {dim}:")
            for tag, count in sorted(tag_stats[dim].items(), key=lambda x: -x[1]):
                print(f"      {tag:<30} {count}")
    print("═" * 60)

    if dry_run:
        print("\n  ⚠️  DRY RUN — no changes made. Remove --dry-run to apply.\n")
    else:
        print("\n  ✅ Done. Search tags in Spotlight or Finder sidebar.\n")


# ── Report ─────────────────────────────────────────────────────────────────────

def report(root: Path):
    """Show current tag distribution across all video files."""
    exts  = {e.lower() for e in VIDEO_EXTENSIONS}
    files = [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
        and ".fcpbundle" not in str(p)
        and "Final Cut Backups" not in str(p)
    ]

    tag_counts: dict[str, int] = defaultdict(int)
    untagged = 0

    for f in files:
        tags = get_current_tags(f)
        if not tags:
            untagged += 1
        for t in tags:
            tag_counts[t] += 1

    print(f"\n📊 Tag report — {len(files)} files in {root}\n")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 40)
        print(f"  {tag:<30} {count:>4}  {bar}")
    print(f"\n  {'(no tags)':<30} {untagged:>4}")
    print()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Apply 5-dimension text tags to video files")
    parser.add_argument("--root",     default=str(DEFAULT_ROOT))
    parser.add_argument("--dry-run",  action="store_true", help="Preview only")
    parser.add_argument("--show-all", action="store_true", help="Show untagged files too")
    parser.add_argument("--file",     help="Tag a single file")
    parser.add_argument("--report",   action="store_true", help="Show current tag distribution")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Not found: {root}")
        sys.exit(1)

    if args.report:
        report(root)
        return

    single = Path(args.file).expanduser().resolve() if args.file else None
    run(root, dry_run=args.dry_run, show_all=args.show_all, single_file=single)


if __name__ == "__main__":
    main()
