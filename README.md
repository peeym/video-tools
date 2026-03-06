# Video Tools

A Python CLI toolset for managing large video libraries on macOS. Provides 5-dimension Finder tagging, inventory scanning, smart reorganization, and safe archiving.

## Tools

| Tool | What it does |
|------|-------------|
| `tag_videos.py` | 5-dimension tagger (status, source, content, business, project) |
| `macos_tagger.py` | Finder color labels + text tags via AppleScript |
| `media_inventory.py` | ffprobe scan → CSV + Markdown report |
| `find_media.py` | Search inventory by any criteria |
| `reorganize.py` | Move files to EDITING/READY structure (`--undo` supported) |
| `folder_snapshot.py` | Snapshot/diff/restore before bulk operations |
| `check_restrictions.py` | Detect stock footage with usage restrictions |
| `gap_detector.py` | Find gaps in numbered file sequences |
| `project_archiver.py` | Archive completed projects |
| `config.py` | Single source of truth for all rules and tag definitions |

## Design Principles

- **Never delete** — all moves logged, always reversible
- **Snapshot before bulk ops** — `folder_snapshot.py` creates restore points
- **macOS native** — uses Finder color labels and xattr tags
- **Single config** — all business rules, tag definitions, and move plans in `config.py`

## Requirements

- macOS
- Python 3.6+
- ffprobe (from ffmpeg) for media scanning
- No pip packages needed

## Usage

```bash
# Scan and tag all videos
python3 tag_videos.py ~/Movies

# Generate inventory report
python3 media_inventory.py ~/Movies

# Reorganize into EDITING/READY structure
python3 reorganize.py --dry-run
python3 reorganize.py

# Search inventory
python3 find_media.py "keyword"
```

## License

MIT
