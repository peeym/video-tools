#!/usr/bin/env python3
"""
delete_report.py
Reads macOS Finder color labels from all video files and generates
a deletion candidate report. Interactive: prompts before moving to Trash.

Usage:
    python3 delete_report.py [--root ~/Movies] [--trash]

Never uses rm — always moves to ~/.Trash/ per CLAUDE.md rules.
"""

import subprocess
import argparse
import sys
from pathlib import Path
from config import FINDER_TAGS, FINDER_TAG_EMOJI, FINDER_TAG_NAMES, VIDEO_EXTENSIONS

TRASH = Path.home() / ".Trash"

# ── Read Finder label via AppleScript ─────────────────────────────────────────

def get_finder_label(path: Path) -> int:
    script = f'tell application "Finder" to get label index of (POSIX file "{path}" as alias)'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def get_all_labels(root: Path) -> list[dict]:
    """Scan all video files and read their current Finder label."""
    all_files = [
        p for p in root.rglob("*")
        if p.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}
        and p.is_file()
        and "Final Cut Backups" not in str(p)
        and ".fcpbundle" not in str(p)
    ]

    total = len(all_files)
    results = []

    print(f"\n🔍 Reading labels for {total} files...")
    for i, path in enumerate(all_files, 1):
        print(f"\r  [{i}/{total}]", end="", flush=True)
        label = get_finder_label(path)
        if label != 0:
            results.append({
                "path":       path,
                "label":      label,
                "tag_name":   FINDER_TAG_NAMES.get(label, f"label-{label}"),
                "size":       path.stat().st_size,
            })
    print()
    return results


# ── Format helpers ─────────────────────────────────────────────────────────────

def format_size(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


# ── Report ─────────────────────────────────────────────────────────────────────

def print_report(labeled: list[dict], root: Path):
    from collections import defaultdict
    by_tag = defaultdict(list)
    for r in labeled:
        by_tag[r["label"]].append(r)

    print(f"\n📋 Finder Labels Report — {root}")
    print(f"   {len(labeled)} tagged files found\n")

    # Show all labeled groups
    for label_idx in sorted(by_tag.keys()):
        group     = by_tag[label_idx]
        tag_name  = FINDER_TAG_NAMES.get(label_idx, f"label-{label_idx}")
        emoji     = FINDER_TAG_EMOJI.get(label_idx, str(label_idx))
        total_sz  = sum(r["size"] for r in group)

        print(f"  {emoji}  {len(group)} files | {format_size(total_sz)}")
        for r in sorted(group, key=lambda x: x["size"], reverse=True)[:10]:
            rel = str(r["path"].relative_to(root))
            print(f"    {format_size(r['size']):>10}  {rel}")
        if len(group) > 10:
            print(f"    ... and {len(group) - 10} more")
        print()


# ── Move to Trash ──────────────────────────────────────────────────────────────

def move_to_trash(files: list[Path]) -> int:
    moved = 0
    for path in files:
        dest = TRASH / path.name
        # Avoid collision
        if dest.exists():
            dest = TRASH / f"{path.stem}_{path.stat().st_ino}{path.suffix}"
        try:
            path.rename(dest)
            print(f"  🗑️  {path.name} → Trash")
            moved += 1
        except Exception as e:
            print(f"  ❌ Failed: {path.name} — {e}")
    return moved


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Report and optionally trash delete-candidate files")
    parser.add_argument("--root",  default=str(Path.home() / "Movies"), help="Root folder to scan")
    parser.add_argument("--trash", action="store_true", help="Interactively move delete-candidates to Trash")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Folder not found: {root}")
        sys.exit(1)

    labeled = get_all_labels(root)

    if not labeled:
        print("\n  ⬜ No tagged files found. Run macos_tagger.py first.\n")
        return

    print_report(labeled, root)

    if args.trash:
        delete_candidates = [
            r["path"] for r in labeled
            if r["label"] == FINDER_TAGS["delete-candidate"]
        ]
        if not delete_candidates:
            print("  ✅ No delete-candidates found. Nothing to trash.\n")
            return

        total_size = sum(r["size"] for r in labeled if r["label"] == FINDER_TAGS["delete-candidate"])
        print(f"  🔴 {len(delete_candidates)} delete-candidate files | {format_size(total_size)}")
        answer = input(f"\n  Move these {len(delete_candidates)} files to Trash? [y/N] ").strip().lower()

        if answer == "y":
            moved = move_to_trash(delete_candidates)
            print(f"\n  ✅ Moved {moved} files to Trash. Freed ~{format_size(total_size)}.\n")
        else:
            print("\n  Cancelled — no files moved.\n")
    else:
        print("  💡 Run with --trash to interactively move delete-candidates to Trash.\n")


if __name__ == "__main__":
    main()
