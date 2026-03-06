#!/usr/bin/env python3
"""
check_restrictions.py
Scan video folders for README / license / attribution files that indicate usage restrictions.
Reports findings and optionally applies 'stock-credit' or 'stock-restricted' text tags.

Usage:
    python3 check_restrictions.py                        # scan ~/Movies, report only
    python3 check_restrictions.py --tag                  # also apply macOS text tags
    python3 check_restrictions.py --root ~/Downloads     # different root
    python3 check_restrictions.py --show-content         # print content of found files
"""

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path
from config import VIDEO_EXTENSIONS

DEFAULT_ROOT = Path.home() / "Movies"

# Files that suggest usage restrictions — name must strongly indicate it's a license/readme
# NOT any .pdf or .txt — only files whose name suggests they ARE a license/attribution file
RESTRICTION_PATTERNS = [
    "readme*", "READ ME*", "READ_ME*",
    "license*", "LICENSE*", "licence*", "LICENCE*",
    "attribution*", "ATTRIBUTION*",
    "credit*", "CREDIT*", "credits*", "CREDITS*",
    "terms*", "TERMS*",
    "rights*", "RIGHTS*",
    "copyright*", "COPYRIGHT*",
    "usage*", "USAGE*",
    "legal*", "LEGAL*",
    "about*the*music*", "music*info*",
]

# Keywords inside files that suggest restrictions
RESTRICTION_KEYWORDS = [
    "credit", "attribution", "license", "licence", "copyright",
    "permission", "restrict", "commercial", "non-commercial",
    "royalty", "rights reserved", "must credit", "must attribute",
    "cc by", "creative commons",
]

CREDIT_KEYWORDS = [
    "credit", "attribution", "must credit", "must attribute", "cc by",
    "creative commons", "by:", "author:", "creator:",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_restriction_files(folder: Path) -> list[Path]:
    """Find any README/license/notes files in a folder."""
    found = []
    for pattern in RESTRICTION_PATTERNS:
        for f in folder.glob(pattern):
            if f.is_file() and f not in found:
                found.append(f)
    return found


def analyze_file(path: Path) -> tuple[str, list[str]]:
    """
    Read a restriction file and determine severity.
    Returns: ('credit' | 'restricted' | 'info', [matching lines])
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return "info", []

    matches = [line.strip() for line in text.splitlines()
               if any(kw in line.lower() for kw in RESTRICTION_KEYWORDS) and line.strip()]

    if any(kw in text for kw in CREDIT_KEYWORDS):
        return "credit", matches[:5]
    elif any(kw in text for kw in RESTRICTION_KEYWORDS):
        return "restricted", matches[:5]
    return "info", matches[:3]


def set_text_tags(path: Path, new_tags: list[str]) -> bool:
    """Add tags without removing existing ones."""
    # Read current tags
    result = subprocess.run(
        ["xattr", "-px", "com.apple.metadata:_kMDItemUserTags", str(path)],
        capture_output=True, text=True
    )
    existing = []
    if result.returncode == 0:
        try:
            hex_str = result.stdout.strip().replace(" ", "").replace("\n", "")
            existing = plistlib.loads(bytes.fromhex(hex_str))
        except Exception:
            pass

    merged = list(dict.fromkeys(existing + new_tags))  # dedupe, preserve order
    plist_bytes = plistlib.dumps(merged, fmt=plistlib.FMT_BINARY)
    r = subprocess.run(
        ["xattr", "-wx", "com.apple.metadata:_kMDItemUserTags",
         plist_bytes.hex(), str(path)],
        capture_output=True
    )
    return r.returncode == 0


# ── Main scan ─────────────────────────────────────────────────────────────────

def scan(root: Path, apply_tags: bool, show_content: bool):
    video_exts = {e.lower() for e in VIDEO_EXTENSIONS}

    # Find all folders containing video files
    video_folders: dict[Path, list[Path]] = {}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in video_exts:
            folder = p.parent
            video_folders.setdefault(folder, []).append(p)

    print(f"\n🔍 Scanning {len(video_folders)} video folders in {root}\n")

    found_any = False
    credit_count = 0
    restricted_count = 0

    for folder, videos in sorted(video_folders.items()):
        restriction_files = find_restriction_files(folder)
        if not restriction_files:
            continue

        found_any = True
        rel = folder.relative_to(root)
        print(f"📁 {rel}")
        print(f"   Videos: {len(videos)}")

        folder_severity = "info"
        for rf in restriction_files:
            severity, lines = analyze_file(rf)
            if severity == "credit":
                folder_severity = "credit"
            elif severity == "restricted" and folder_severity != "credit":
                folder_severity = "restricted"

            icon = {"credit": "💛", "restricted": "🔴", "info": "ℹ️ "}.get(severity, "ℹ️ ")
            print(f"   {icon} {rf.name}  [{severity}]")

            if show_content and lines:
                for line in lines:
                    print(f"      → {line[:100]}")

        if folder_severity in ("credit", "restricted"):
            tag = "stock-credit" if folder_severity == "credit" else "stock-restricted"
            if folder_severity == "credit":
                credit_count += len(videos)
            else:
                restricted_count += len(videos)

            if apply_tags:
                tagged = 0
                for v in videos:
                    if set_text_tags(v, [tag]):
                        tagged += 1
                print(f"   {'✅' if tagged == len(videos) else '⚠️ '} Tagged {tagged}/{len(videos)} videos → {tag}")
            else:
                print(f"   → Would tag: {tag}  (run with --tag to apply)")

        print()

    if not found_any:
        print("  ✓ No restriction files found in any video folder.\n")
        return

    print("═" * 60)
    print(f"  💛 Needs credit:      {credit_count} videos")
    print(f"  🔴 Restricted use:    {restricted_count} videos")
    if not apply_tags:
        print("\n  ⚠️  Tags NOT applied. Run with --tag to apply.")
    else:
        print("\n  ✅ Tags applied.")
    print("═" * 60 + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Find README/license files near videos and flag usage restrictions"
    )
    parser.add_argument("--root",         default=str(DEFAULT_ROOT), help="Folder to scan")
    parser.add_argument("--tag",          action="store_true",        help="Apply macOS tags to flagged files")
    parser.add_argument("--show-content", action="store_true",        help="Print matching lines from restriction files")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"❌ Not found: {root}")
        sys.exit(1)

    scan(root, apply_tags=args.tag, show_content=args.show_content)


if __name__ == "__main__":
    main()
