"""
config.py — shared configuration for all video-tools scripts.
Business classification, status detection, and Finder tag definitions.
"""

from pathlib import Path

# ── Video file extensions ──────────────────────────────────────────────────────

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv",
    ".MOV", ".MP4", ".MKV", ".AVI", ".M4V", ".WMV",
}

# ── Business Rules ─────────────────────────────────────────────────────────────
# Ordered list of (label, keywords). First match wins.

BUSINESS_RULES = [
    ("🎨 תבניות",      ["Motion Templates", "Visual_Elements", "stock phootage", "stock footage", "01-sound", "03-Visual"]),
    ("🧠 טיפול",       ["עין הסערה", "מובחנות"]),
    ("🏢 צור הדרכות",  ["הדרכות עובדים", "צור הדרכות"]),
    ("👤 אישי",        ["Sharon", "שרון 70", "סרטי משפחה"]),
    ("💰 פיננסים",     [
        "ICF", "כלכלה מעשית", "אושר ועושר", "בלי לחץ", "זוגיות וכסף",
        "פיננסים", "ולידציה", "פרקש", "השקעות", "מסודרים",
        "וובינרים", "הרצאה", "פודקאסט", "ימות המשיח",
        "הזמנה", "background ICF", "polywiz", "גליון שנתי",
    ]),
]

UNKNOWN_BUSINESS = "❓ לא ידוע"

# ── Type Rules ─────────────────────────────────────────────────────────────────
# Content type classification — ordered, first match wins.
# Used as macOS text tags: searchable via Spotlight and Finder sidebar.

TYPE_RULES = [
    ("raw",      ["גלם", "OBS", "raw", "footage", "P110"]),
    ("template", ["Motion Templates", "Visual_Elements", "_Assets", "stock", "01-sound", "03-Visual", "Logos", "Arrows"]),
    ("podcast",  ["פודקאסט", "Podcast", "אושר ועושר"]),
    ("course",   ["קורס", "מפגש", "שיעור", "lesson", "מסודרים", "זוגיות וכסף", "מובחנות", "בלי לחץ"]),
    ("social",   ["VEED", "FCPX", "Social", "social", "reels", "ICF Edit"]),
    ("lecture",  ["הרצאה", "וובינר", "webinar", "כנס", "Webinar"]),
    ("promo",    ["הזמנה", "promo", "פרומו"]),
]

UNKNOWN_TYPE = "general"

# Folder-to-READY destination mapping (used by reorganize.py)
# (source relative to ~/Movies, destination relative to ~/Movies)
MOVE_PLAN = [
    ("זוגיות וכסף פרקים מוכנים",                                           "READY/Finance/זוגיות וכסף"),
    ("מסודרים2 פרקים מוכנים",                                              "READY/Finance/מסודרים"),
    ("00 - Edit video/עין הסערה מוכן",                                     "READY/Efrat/עין הסערה"),
    ("00 - Edit video/המדריך להשקעות - מוכן",                              "READY/Finance/המדריך להשקעות"),
    ("00 - Edit video/סדרה חינמית בלי לחץ/פרקים מוכנים לחץ כלכלי",        "READY/Finance/בלי לחץ"),
    ("00 - Edit video/פודקאסט אושר ועושר/סרטונים מוכנים אושר ועושר",       "READY/Finance/Podcast"),
    ("00 - Edit video/ICF Edit video /סרטונים מוכנים ICF",                 "READY/Finance/ICF Social"),
    ("00 - Edit video/Sharon 70",                                           "READY/Personal/Sharon 70"),
    ("00 - Edit video/03-Visual_Elements",                                  "EDITING/_Assets/Visual Elements"),
    ("00 - Edit video/01-sound",                                            "EDITING/_Assets/Music"),
    ("00 - Edit video/00-stock phootage",                                   "EDITING/_Assets/Stock Footage"),
    ("הדרכות עובדים",                                                       "READY/Training"),
    ("קורס מובחנות מצולם",                                                  "READY/Efrat/מובחנות"),
    ("הקלטות וובינרים",                                                     "READY/Finance/Webinars"),
]

# Empty folders to create on reorganize
CREATE_DIRS = [
    "EDITING/_Assets/Graphics & Logos",
    "EDITING/_Assets/Titles",
    "EDITING/_Assets/Intros & Outros",
    "EDITING/_Assets/SFX",
    "EDITING/Projects",
    "READY/Finance",
    "READY/Efrat",
    "READY/Training",
    "READY/Personal",
]

# ── Status Rules ───────────────────────────────────────────────────────────────

RAW_KEYWORDS  = ["גלם", "raw", "footage", "OBS"]
DONE_KEYWORDS = ["מוכן", "finished", "done", "מוכנים"]

# ── 5-Dimension Text Tag Rules ─────────────────────────────────────────────────
# Each dimension: ordered list of (tag, [keywords]).
# First match wins within each dimension.
# A file can get one tag per dimension → up to 5 tags total.
# All rules match against the full file path string.

TAG_RULES = {

    # ── Dimension 1: Status ──────────────────────────────────────────────────
    "status": [
        ("raw",      ["גלם", "raw footage", "OBS", "P110", "footage"]),
        ("final",    ["READY/", "מוכן", "finished", "done", "מוכנים"]),
        ("archived", ["Sharon 70", "archive"]),
        ("template", ["Motion Templates", "EDITING/_Assets", "_Assets"]),
    ],

    # ── Dimension 2: Source ──────────────────────────────────────────────────
    "source": [
        ("ai",          ["Alpha Turbo", "runway", "midjourney", "AI-gen", "ai-gen",
                         "stable-diffusion", "sora", "kling"]),
        ("stock",       ["stock videos", "stock footage", "00-stock", "pexels",
                         "pixabay", "pond5", "shutterstock", "envato", "storyblocks"]),
        ("screen-rec",  ["OBS", "screen-rec", "Screen Recording"]),
        ("recorded",    ["גלם", "P110", "footage"]),
    ],

    # ── Dimension 3: Content Type ────────────────────────────────────────────
    "content": [
        ("animation",    ["Motion Templates", "animation"]),
        ("graphic",      ["Visual Elements", "Visual_Elements", "Graphics & Logos",
                          "Logos", "arrows", "Arrows"]),
        ("music",        ["EDITING/_Assets/Music", "01-sound", "SFX",
                          "EDITING/_Assets/SFX"]),
        ("broll",        ["stock videos", "B-Roll", "broll", "Stock Footage"]),
        ("talking-head", ["מפגש", "הרצאה", "שיעור", "episode", "פרק"]),
        ("intro",        ["Intros & Outros", "intro", "outro"]),
        ("title",        ["EDITING/_Assets/Titles", "title"]),
    ],

    # ── Dimension 4: Business ────────────────────────────────────────────────
    # Reuses BUSINESS_RULES keywords — mapped to clean tag names
    "business": [
        ("template",  ["Motion Templates", "Visual_Elements", "stock footage",
                       "01-sound", "03-Visual", "_Assets"]),
        ("efrat",     ["עין הסערה", "מובחנות"]),
        ("tzur-ltd",  ["הדרכות עובדים", "צור הדרכות"]),
        ("personal",  ["Sharon", "שרון 70", "סרטי משפחה"]),
        ("finance",   ["ICF", "כלכלה מעשית", "אושר ועושר", "בלי לחץ",
                       "זוגיות וכסף", "פיננסים", "ולידציה", "פרקש",
                       "השקעות", "מסודרים", "וובינרים", "הרצאה",
                       "פודקאסט", "ימות המשיח", "הזמנה", "polywiz"]),
    ],

    # ── Dimension 5: Project ─────────────────────────────────────────────────
    "project": [
        ("icf",                ["ICF", "ICF Edit"]),
        ("podcast",            ["פודקאסט", "אושר ועושר"]),
        ("בלי-לחץ",            ["בלי לחץ"]),
        ("מסודרים",            ["מסודרים"]),
        ("עין-הסערה",          ["עין הסערה"]),
        ("מובחנות",            ["מובחנות"]),
        ("זוגיות-וכסף",        ["זוגיות וכסף"]),
        ("המדריך-להשקעות",     ["המדריך להשקעות"]),
        ("וובינרים",           ["וובינרים", "Webinars"]),
        ("הדרכות",             ["הדרכות עובדים"]),
        ("שרון-70",            ["Sharon 70", "שרון 70"]),
    ],
}

# ── Finder Label Indices ───────────────────────────────────────────────────────
# macOS Finder label index (0=none, 1=orange, 2=red, 3=yellow, 4=blue, 5=purple, 6=green, 7=gray)

FINDER_TAGS = {
    "none":             0,
    "template":         4,   # 🔵 Blue  — keep permanently
    "used":             6,   # 🟢 Green — finished/active
    "archived":         3,   # 🟡 Yellow — project done, raw not needed
    "delete-candidate": 2,   # 🔴 Red   — candidate for deletion
    "check-gap":        1,   # 🟠 Orange — gap in sequence, review manually
}

FINDER_TAG_NAMES = {v: k for k, v in FINDER_TAGS.items()}
FINDER_TAG_EMOJI = {
    0: "⬜ none",
    1: "🟠 check-gap",
    2: "🔴 delete-candidate",
    3: "🟡 archived",
    4: "🔵 template",
    5: "🟣 purple",
    6: "🟢 used",
    7: "⚫ gray",
}

# ── Classifier Functions ───────────────────────────────────────────────────────

def classify_business(path) -> str:
    path_str = str(path)
    for label, keywords in BUSINESS_RULES:
        for kw in keywords:
            if kw in path_str:
                return label
    return UNKNOWN_BUSINESS


def classify_type(path) -> str:
    path_str = str(path)
    for type_tag, keywords in TYPE_RULES:
        for kw in keywords:
            if kw in path_str:
                return type_tag
    return UNKNOWN_TYPE


def classify_status(path) -> str:
    path_str = str(path)
    for part in Path(path_str).parts:
        for kw in DONE_KEYWORDS:
            if kw in part:
                return "✅ מוכן"
        for kw in RAW_KEYWORDS:
            if kw in part:
                return "🎬 גלם"
    return "🔄 לא ידוע"


# ── Self-test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n📋 Business Categories:")
    print(f"  {'Label':<20} {'Keywords'}")
    print("  " + "─" * 70)
    for label, kws in BUSINESS_RULES:
        print(f"  {label:<20} {', '.join(kws[:5])}{'...' if len(kws) > 5 else ''}")
    print(f"  {'fallback':<20} {UNKNOWN_BUSINESS}")

    print("\n🏷️  Finder Tags:")
    for name, idx in FINDER_TAGS.items():
        print(f"  {FINDER_TAG_EMOJI.get(idx, idx):<25} index={idx}  name={name}")

    print("\n✅ config.py OK\n")
