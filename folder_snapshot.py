#!/usr/bin/env python3
"""
folder_snapshot.py
Save / diff / restore a directory tree snapshot.
Run before any reorganization so you can always go back.

Usage:
    python3 folder_snapshot.py save              # snapshot ~/Movies
    python3 folder_snapshot.py save --root ~/Movies --label before-reorg
    python3 folder_snapshot.py list              # show saved snapshots
    python3 folder_snapshot.py diff snap1 snap2  # compare two snapshots
    python3 folder_snapshot.py restore snap1     # recreate missing folders
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


# ── Save ──────────────────────────────────────────────────────────────────────

def save(root: Path, label: str):
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    ts    = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug  = label.replace(" ", "-").replace("/", "-") if label else "snapshot"
    fname = SNAPSHOT_DIR / f"{ts}_{slug}.txt"

    dirs = sorted(
        p for p in root.rglob("*")
        if p.is_dir()
        and ".fcpbundle" not in str(p)
        and "Final Cut Backups" not in str(p)
    )

    lines = [f"# Snapshot of {root}", f"# Saved: {datetime.now()}", f"# Dirs: {len(dirs)}", ""]
    for d in dirs:
        lines.append(str(d.relative_to(root)))

    fname.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📸 Snapshot saved: {fname.name}")
    print(f"   Root:  {root}")
    print(f"   Dirs:  {len(dirs)}")
    print(f"   File:  {fname}\n")
    return fname


# ── List ──────────────────────────────────────────────────────────────────────

def list_snapshots():
    if not SNAPSHOT_DIR.exists() or not list(SNAPSHOT_DIR.glob("*.txt")):
        print("\n  No snapshots found.\n")
        return
    snaps = sorted(SNAPSHOT_DIR.glob("*.txt"))
    print(f"\n📂 Snapshots ({len(snaps)}):\n")
    for s in snaps:
        lines = [l for l in s.read_text().splitlines() if not l.startswith("#") and l.strip()]
        print(f"  {s.name}  ({len(lines)} dirs)")
    print()


# ── Diff ──────────────────────────────────────────────────────────────────────

def load_dirs(path: Path) -> set[str]:
    return {
        l.strip()
        for l in path.read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#")
    }


def diff(snap_a: str, snap_b: str):
    def resolve(name: str) -> Path:
        # Accept full path or just filename
        p = Path(name)
        if p.exists():
            return p
        candidate = SNAPSHOT_DIR / name
        if candidate.exists():
            return candidate
        # try prefix match
        matches = sorted(SNAPSHOT_DIR.glob(f"*{name}*"))
        if matches:
            return matches[0]
        print(f"❌ Snapshot not found: {name}")
        sys.exit(1)

    pa, pb = resolve(snap_a), resolve(snap_b)
    dirs_a, dirs_b = load_dirs(pa), load_dirs(pb)

    added   = sorted(dirs_b - dirs_a)
    removed = sorted(dirs_a - dirs_b)

    print(f"\n📊 Diff: {pa.name}  →  {pb.name}\n")
    if added:
        print(f"  ✅ Added ({len(added)}):")
        for d in added:
            print(f"     + {d}")
    if removed:
        print(f"\n  ❌ Removed ({len(removed)}):")
        for d in removed:
            print(f"     - {d}")
    if not added and not removed:
        print("  ✓ No differences\n")
    print()


# ── Restore ───────────────────────────────────────────────────────────────────

def restore(snap_name: str, root: Path, dry_run: bool):
    matches = sorted(SNAPSHOT_DIR.glob(f"*{snap_name}*")) if not Path(snap_name).exists() else [Path(snap_name)]
    if not matches:
        print(f"❌ Snapshot not found: {snap_name}")
        sys.exit(1)
    snap_path = matches[0]
    dirs = [l.strip() for l in snap_path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]

    missing = [d for d in dirs if not (root / d).exists()]

    if not missing:
        print(f"\n  ✓ All {len(dirs)} folders already exist. Nothing to restore.\n")
        return

    print(f"\n🔁 {'DRY RUN — ' if dry_run else ''}Restore from: {snap_path.name}")
    print(f"   Missing folders: {len(missing)} of {len(dirs)}\n")
    for d in missing:
        print(f"  {'→' if dry_run else '+'} {d}")
        if not dry_run:
            (root / d).mkdir(parents=True, exist_ok=True)

    if dry_run:
        print("\n  ⚠️  DRY RUN — no folders created. Remove --dry-run to apply.\n")
    else:
        print(f"\n  ✅ Recreated {len(missing)} folders.\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Snapshot, diff, and restore folder structures")
    sub = parser.add_subparsers(dest="cmd")

    p_save = sub.add_parser("save", help="Save current folder tree")
    p_save.add_argument("--root",    default=str(Path.home() / "Movies"))
    p_save.add_argument("--label",   default="", help="Label for the snapshot file")

    sub.add_parser("list", help="List saved snapshots")

    p_diff = sub.add_parser("diff", help="Compare two snapshots")
    p_diff.add_argument("snap_a")
    p_diff.add_argument("snap_b")

    p_restore = sub.add_parser("restore", help="Recreate missing folders from snapshot")
    p_restore.add_argument("snapshot")
    p_restore.add_argument("--root",    default=str(Path.home() / "Movies"))
    p_restore.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.cmd == "save":
        root = Path(args.root).expanduser().resolve()
        if not root.exists():
            print(f"❌ Root not found: {root}")
            sys.exit(1)
        save(root, args.label)

    elif args.cmd == "list":
        list_snapshots()

    elif args.cmd == "diff":
        diff(args.snap_a, args.snap_b)

    elif args.cmd == "restore":
        root = Path(args.root).expanduser().resolve()
        restore(args.snapshot, root, args.dry_run)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
