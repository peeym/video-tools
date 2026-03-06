#!/usr/bin/env python3
"""
macos_tagger.py
Apply macOS Finder color labels to video files based on folder rules.
Non-destructive: never renames or moves files. Works safely with FCP.

Usage:
    python3 macos_tagger.py [--root ~/Movies] [--dry-run] [--reset]

Finder label colors:
    🔵 Blue   (4) = template     — keep permanently
    🟢 Green  (6) = used         — finished / active
    🟡 Yellow (3) = archived     — project done, raw not needed
    🟠 Orange (1) = check-gap    — gap in sequence, review manually
    🔴 Red    (2) = delete-candidate
"""

import subprocess
import argparse
import sys
import plistlib
from pathlib import Path
from config import FINDER_TAGS, FINDER_TAG_EMOJI, VIDEO_EXTENSIONS, classify_business, classify_type, UNKNOWN_BUSINESS

# ── Tagging rules (applied in order, first match wins) ────────────────────────

def determine_tag(path: Path) -> tuple[int, str]:
    """Return (label_index, reason) for a given file path."""
    path_str = str(path)
    parts    = path.parts

    # 1. Template / asset files — keep permanently
    template_markers = ["Motion Templates", "Visual_Elements", "stock", "01-sound", "03-Visual"]
    for marker in template_markers:
        if marker in path_str:
            return FINDER_TAGS["template"], f"template folder: {marker}"

    # 2. File is in a "מוכן" (finished) folder → green
    for part in parts:
        for kw in ["מוכן", "finished", "done", "מוכנים"]:
            if kw in part:
                return FINDER_TAGS["used"], f"in finished folder: {part}"

    # 3. File is in a "גלם" (raw) folder AND sibling "מוכן" folder exists → yellow
    for i, part in enumerate(parts):
        for kw in ["גלם", "raw", "footage"]:
            if kw in part:
                parent = Path(*parts[:i])
                sibling_done = any(
                    any(done_kw in str(s) for done_kw in ["מוכן", "finished", "done"])
                    for s in parent.iterdir()
                    if s.is_dir()
                ) if parent.exists() else False
                if sibling_done:
                    return FINDER_TAGS["archived"], f"raw with sibling finished folder"
                break

    # 4. Personal project folder → yellow
    personal_markers = ["Sharon", "שרון 70", "סרטי משפחה"]
    for marker in personal_markers:
        if marker in path_str:
            return FINDER_TAGS["archived"], f"personal project: {marker}"

    # 5. Old completed project: last modified > 180 days (checked by caller)
    # (handled separately in scan loop)

    return FINDER_TAGS["none"], "unreviewed"


# ── macOS Finder label via AppleScript ────────────────────────────────────────

def set_finder_label(path: Path, label_index: int) -> bool:
    """Set macOS Finder color label. Returns True on success."""
    script = f'tell application "Finder" to set label index of (POSIX file "{path}" as alias) to {label_index}'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    return result.returncode == 0


def get_finder_label(path: Path) -> int:
    """Read current macOS Finder label index."""
    script = f'tell application "Finder" to get label index of (POSIX file "{path}" as alias)'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except ValueError:
        return -1


# ── macOS text tags via xattr ──────────────────────────────────────────────────

def set_text_tags(path: Path, tags: list[str]) -> bool:
    """Set macOS Finder text tags (searchable via Spotlight & Finder sidebar)."""
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


def get_text_tags(path: Path) -> list[str]:
    """Read macOS Finder text tags."""
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


def build_text_tags(path: Path) -> list[str]:
    """Build list of text tags for a file: business + type."""
    business = classify_business(path)
    type_tag  = classify_type(path)

    tags = []
    # Business tag (clean, no emoji)
    business_clean = business.split(" ", 1)[-1] if " " in business else business
    if business_clean != UNKNOWN_BUSINESS.split(" ", 1)[-1]:
        tags.append(business_clean.lower().replace(" ", "-"))

    # Type tag
    if type_tag != "general":
        tags.append(type_tag)

    return tags


# ── Main scan + tag loop ───────────────────────────────────────────────────────

def run(root: Path, dry_run: bool = False, reset: bool = False):
    all_files = [
        p for p in root.rglob("*")
        if p.suffix.lower() in {e.lower() for e in VIDEO_EXTENSIONS}
        and p.is_file()
        and "Final Cut Backups" not in str(p)
        and ".fcpbundle" not in str(p)
    ]

    total   = len(all_files)
    counts  = {name: 0 for name in FINDER_TAGS}
    skipped = 0

    print(f"\n🏷️  {'DRY RUN — ' if dry_run else ''}Tagging {total} files in {root}")
    print(f"   (reset={reset})\n")

    for i, path in enumerate(all_files, 1):
        if reset:
            label, reason = FINDER_TAGS["none"], "reset"
        else:
            label, reason = determine_tag(path)

        tag_name = next((k for k, v in FINDER_TAGS.items() if v == label), "none")
        emoji    = FINDER_TAG_EMOJI.get(label, str(label))

        if label == FINDER_TAGS["none"]:
            skipped += 1
        else:
            counts[tag_name] = counts.get(tag_name, 0) + 1

        if not dry_run:
            ok = set_finder_label(path, label)
            if not reset:
                text_tags = build_text_tags(path)
                if text_tags:
                    set_text_tags(path, text_tags)
            status = "✓" if ok else "✗"
        else:
            status = "→"

        if label != FINDER_TAGS["none"] or dry_run:
            short = str(path.relative_to(root))
            if len(short) > 70:
                short = "..." + short[-67:]
            print(f"  [{i:4d}/{total}] {status} {emoji:<25} {short}")
            if dry_run and reason != "unreviewed":
                print(f"          reason: {reason}")

    # Summary
    print("\n" + "═" * 60)
    print("  Summary:")
    for tag_name, idx in FINDER_TAGS.items():
        count = counts.get(tag_name, 0)
        if count > 0:
            print(f"    {FINDER_TAG_EMOJI[idx]:<25} {count} files")
    print(f"    ⬜ unreviewed                  {skipped} files")
    print("═" * 60)
    if dry_run:
        print("\n  ⚠️  DRY RUN — no changes made. Remove --dry-run to apply.\n")
    else:
        print("\n  ✅ Done. Open Finder to see color labels.\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Apply macOS Finder color labels to video files")
    parser.add_argument("--root",    default=str(Path.home() / "Movies"), help="Root folder to scan")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be tagged, don't apply")
    parser.add_argument("--reset",   action="store_true", help="Remove all color labels (set to 0)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Folder not found: {root}")
        sys.exit(1)

    run(root, dry_run=args.dry_run, reset=args.reset)


if __name__ == "__main__":
    main()
