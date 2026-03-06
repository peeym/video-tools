#!/usr/bin/env python3
"""
reorganize.py
Create the EDITING/ + READY/ folder structure and move finished content.
Reads the move plan from config.py. Never touches .fcpbundle files.

Usage:
    python3 reorganize.py --dry-run     # show what would move
    python3 reorganize.py               # execute moves + log everything
    python3 reorganize.py --undo        # reverse all moves from move_log.csv
"""

import argparse
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path
from config import MOVE_PLAN, CREATE_DIRS

ROOT     = Path.home() / "Movies"
LOG_FILE = Path(__file__).parent / "move_log.csv"


# ── Helpers ───────────────────────────────────────────────────────────────────

def format_size(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


# ── Dry run ───────────────────────────────────────────────────────────────────

def show_plan():
    print(f"\n📋 REORGANIZE DRY RUN — {ROOT}\n")

    print("  📁 Folders to CREATE:")
    for d in CREATE_DIRS:
        dest = ROOT / d
        status = "exists" if dest.exists() else "NEW"
        print(f"    [{status:6}] {d}")

    print(f"\n  📦 Folders to MOVE ({len(MOVE_PLAN)} moves):\n")
    total_size = 0
    missing    = []

    for src_rel, dst_rel in MOVE_PLAN:
        src = ROOT / src_rel
        dst = ROOT / dst_rel

        if not src.exists():
            missing.append(src_rel)
            print(f"    ⚠️  NOT FOUND: {src_rel}")
            continue

        size     = folder_size(src)
        total_size += size
        dst_status = "⚠️  DST EXISTS" if dst.exists() else "→"

        print(f"    {dst_status}  {src_rel}")
        print(f"         → {dst_rel}  ({format_size(size)})")

    print(f"\n  📊 Total to move: {format_size(total_size)}")
    if missing:
        print(f"  ⚠️  {len(missing)} sources not found (already moved or path changed)")

    print(f"\n  ⚠️  DRY RUN — nothing moved. Run without --dry-run to execute.\n")
    print(f"  ℹ️  .fcpbundle files are NEVER touched — move them via FCP: File → Move Library\n")


# ── Execute ───────────────────────────────────────────────────────────────────

def execute(root: Path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_rows  = []
    errors    = []

    # Step 1: Create empty directories
    print(f"\n📁 Creating folder structure...")
    for d in CREATE_DIRS:
        dest = root / d
        if not dest.exists():
            dest.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {d}")
        else:
            print(f"  · Exists:  {d}")

    # Step 2: Execute moves
    print(f"\n📦 Moving folders...")
    for src_rel, dst_rel in MOVE_PLAN:
        src = root / src_rel
        dst = root / dst_rel

        if not src.exists():
            print(f"  ⚠️  Skip (not found): {src_rel}")
            continue

        if dst.exists():
            print(f"  ⚠️  Skip (dest exists): {dst_rel}")
            continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            size = folder_size(src)
            shutil.move(str(src), str(dst))
            print(f"  ✓ {src_rel}")
            print(f"    → {dst_rel}  ({format_size(size)})")
            log_rows.append({
                "timestamp": timestamp,
                "action":    "move",
                "source":    str(src),
                "dest":      str(dst),
                "size":      size,
            })
        except Exception as e:
            print(f"  ✗ FAILED: {src_rel} → {e}")
            errors.append((src_rel, str(e)))

    # Step 3: Write log
    if log_rows:
        write_log(log_rows)
        print(f"\n  📄 Log saved: {LOG_FILE}")

    # Summary
    print(f"\n{'═' * 50}")
    print(f"  ✅ Moved: {len(log_rows)} folders")
    if errors:
        print(f"  ❌ Errors: {len(errors)}")
        for src, err in errors:
            print(f"     {src}: {err}")
    print(f"\n  ℹ️  Next: open FCP → File → Move Library to move .fcpbundle files")
    print(f"     Then run: python3 macos_tagger.py to re-tag the new structure\n")


# ── Undo ──────────────────────────────────────────────────────────────────────

def undo():
    if not LOG_FILE.exists():
        print(f"\n❌ No log file found at {LOG_FILE}\n")
        sys.exit(1)

    rows = list(csv.DictReader(open(LOG_FILE)))
    moves = [r for r in rows if r["action"] == "move"]

    if not moves:
        print("\n  Nothing to undo.\n")
        return

    print(f"\n↩️  Undoing {len(moves)} moves from {LOG_FILE}\n")
    for row in reversed(moves):
        src = Path(row["dest"])
        dst = Path(row["source"])
        if not src.exists():
            print(f"  ⚠️  Skip (not found): {src}")
            continue
        if dst.exists():
            print(f"  ⚠️  Skip (original exists): {dst}")
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"  ✓ Restored: {dst.name}")
        except Exception as e:
            print(f"  ✗ Failed: {src} → {e}")

    print("\n  ✅ Undo complete.\n")


# ── Log ───────────────────────────────────────────────────────────────────────

def write_log(rows: list[dict]):
    fields    = ["timestamp", "action", "source", "dest", "size"]
    file_mode = "a" if LOG_FILE.exists() else "w"
    with open(LOG_FILE, file_mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if file_mode == "w":
            w.writeheader()
        w.writerows(rows)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Reorganize Movies folder into EDITING/ + READY/")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without moving")
    parser.add_argument("--undo",    action="store_true", help="Reverse moves from move_log.csv")
    args = parser.parse_args()

    if args.undo:
        undo()
        return

    if args.dry_run:
        show_plan()
        return

    # Confirm before executing
    show_plan()
    answer = input("  Execute? [y/N] ").strip().lower()
    if answer != "y":
        print("  Cancelled.\n")
        return

    execute(ROOT)


if __name__ == "__main__":
    main()
