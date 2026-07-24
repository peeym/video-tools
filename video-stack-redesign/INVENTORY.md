# Video Stack Inventory — Facts Only

Generated 2026-07-24. This document contains **observed state only**. No proposal,
no assessment, no recommendation. It is the shared input for independent
architecture reviews.

Owner works primarily in Hebrew, on macOS (Darwin 24.6.0), with Final Cut Pro as the
finishing NLE. Two other machines exist: Omac (Mac, task daemon) and a Windows PC with
an RTX 3060 Ti (8 GB) reachable over Tailscale at 10.100.102.14. The PC was
unreachable at the time of this scan.

---

## 1. Skills — 25 video-related, 55 MB total

Total size of `~/.claude/skills/` is 1.7 GB across ~207 directories.

### 1a. Authored by the owner

| Skill | Installed | Size | Files | Stated role |
|---|---|---|---|---|
| `video-director` | 2026-07-03 | 20K | 3 | "ALWAYS-ON decision layer for ANY video request. Read this FIRST." Decision tree + 7-step approval workflow. Has `references/engines.md` (101 lines) and `planning/template.md`. |
| `icf-video` | 2026-07-01 | 8K | 1 | Script → branded 9:16 narrated video. Hebrew VO via ElevenLabs v3, Nano-Banana B-roll, Ken Burns, HTML effects library, outputs MP4 + Final Cut edit kit. |
| `paper-edit` | 2026-07-24 | 48K | 7 | Text-based rough cut. Local GPU transcription over Tailscale, transcript cleanup, local HTML strike-through review page, cut snapping to quiet points, ffmpeg render. Optional FCPXML output. |

`video-use` is a **symlink** to `~/DEV/video-use` (a git repo with `.venv`, 23 KB
SKILL.md, `poster.html`, helpers). Installed 2026-05-07. Describes conversational
video editing with hard production-correctness rules (subtitle ordering, lossless
concat, 30 ms audio fades, PTS shifting, word-boundary cuts).

### 1b. HyperFrames bundle — 15 skills, installed together 2026-07-01

Domain skills (the framework itself):

| Skill | Size | Files | Covers |
|---|---|---|---|
| `hyperframes` | 20K | 1 | Entry skill + intent router for the bundle |
| `hyperframes-core` | 104K | 13 | Composition contract, `data-*` timing attributes, determinism |
| `hyperframes-animation` | 38M | 116 | Motion rules, blueprints, transitions, 7 runtime adapters (GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU) |
| `hyperframes-creative` | 1.1M | 68 | Palettes, typography, narration, beat planning, brand direction |
| `hyperframes-media` | 1.4M | 40 | TTS (HeyGen / ElevenLabs / Kokoro), BGM, SFX, Whisper transcription, captions, background removal |
| `hyperframes-cli` | 68K | 7 | `npx hyperframes` commands; AWS Lambda cloud rendering |
| `hyperframes-registry` | 72K | 10 | Installable blocks and components |

Workflow skills (task entry points, all render through HyperFrames):

| Skill | Size | Files | Input it expects |
|---|---|---|---|
| `faceless-explainer` | 260K | 17 | Arbitrary text → explainer, ~30–90 s sweet spot |
| `product-launch-video` | 260K | 18 | Product/marketing URL or brief |
| `website-to-video` | 1.6M | 32 | General website URL, headless Chrome capture |
| `pr-to-video` | 324K | 21 | GitHub pull request via `gh` |
| `motion-graphics` | 156K | 23 | Short design-led piece, under ~30 s, no narration |
| `slideshow` | 80K | 2 | Presentation / pitch deck composition |
| `talking-head-recut` | 556K | 27 | Existing talking-head video + timed graphic overlay cards |
| `embedded-captions` | 3.6M | 144 | Talking-head video + captions; 32 visual identities, 2 engines |
| `music-to-video` | 6.2M | 132 | Music track → beat-synced video |
| `general-video` | 16K | 1 | Declared fallback when no specialized workflow fits |
| `media-use` | 108K | 19 | Resolves BGM/SFX/image/icon needs into frozen local files; HeyGen catalog |
| `remotion-to-hyperframes` | 352K | 70 | Port a Remotion project |

`website-to-hyperframes` is a symlink to `../../.agents/skills/website-to-hyperframes`,
which resolves to nothing (0 files).

`higgsfield` (12K, 2026-05-07) is separate from the bundle: cinematic image-to-video,
Soul ID character consistency.

### 1c. Adjacent skills that touch video

`transcribe`, `live-transcribe`, `live-transcribe-read`, `live-transcribe-stop`,
`convert`, `media-pipeline`, `gsap`, `lottie`, `three`, `animejs`, `lottie-generator`,
`css-animations`, `presentation-builder`, `hebrew-keynote-builder`, `slideshow`,
`website-to-video`, `visual-content`.

---

## 2. Router collision (verbatim from the two `description:` fields)

`video-director`:
> ALWAYS-ON decision layer for ANY video request. Read this FIRST, before touching
> any video tool, then follow the decision tree to pick the RIGHT engine and honor
> the 7-step approval workflow.

Its body states: "HyperFrames is slow (frame-by-frame screenshots). It is the *last
resort* for image+voice videos, and heavy HyperFrames renders run on **Omac**, not the
Mac."

`hyperframes`:
> READ THIS FIRST for any request to make, create, edit, animate, or render a
> video, animation, or motion graphic ... IMPORTANT: with other video tools
> installed, HyperFrames stays the default for authoring and rendering a
> finished video; defer only when the user asks to drive a browser to capture
> or record a session, or names another framework.

Both claim first-read priority. `hyperframes` explicitly asserts default status over
other installed video tools. `video-director` ranks HyperFrames last for the owner's
most common job type.

Additionally, `hyperframes` was installed 2026-07-01 and `video-director` on
2026-07-03. `video-director` does not mention `paper-edit` (created 2026-07-24) or
`video-use` anywhere in its decision tree.

---

## 3. Agents — 3 video-specific

| Agent | Pairs with | Stated role |
|---|---|---|
| `icf-video-producer` | skill `icf-video` | Autonomously produces branded ICF vertical video from an approved script. Vault script → script.json → B-roll → VO → build → render → 1080p downscale → Final Cut edit kit. |
| `paper-edit-engine` | skill `paper-edit` | Runs the paper-edit pipeline end to end. Explicitly never routes Hebrew to a cheaper model. |
| `media-pipeline-runner` | skill `media-pipeline` | Orchestrates transcribe → diarize → light-edit for a course / webinar / meeting from Drive, YouTube, Vimeo, or local files. |

Adjacent: `visual-content` (stills: flyers, banners, thumbnails, YouTube covers via
HTML/CSS → Playwright export).

Each of the three follows the same pattern: one skill defines the procedure, one agent
executes it autonomously.

---

## 4. Where video work physically happens — 5 locations

| Path | Contents |
|---|---|
| `~/DEV/ICF/content/insurance-video-v1/pipeline/` | The working FFmpeg-direct engine. `bin/` holds `make-ff.sh`, `make.sh`, `ffrender.py`, `genimg.py`, `img2video.py`, `tts.py`, `broll.sh`, `ingest-voice.sh`, `make_fcpx.py`, `render.sh`. Plus `lib/`, `projects/`, `config.json`, `EFFECTS.md`, `effects-gallery.html`, `gallery-assets/`. |
| `~/DEV/ICF/content/insurance-video-v1/` (parent) | 8 finished/intermediate MP4s including `SKETCH-*`, `PROOF-*`, `DEMO-*`, and versioned cuts v1–v5. Plus `assets/`, `broll/`, `poster.jpg`. |
| `~/DEV/video-tools/` | Python scripts for media organization: `find_media.py`, `media_inventory.py`, `reorganize.py`, `macos_tagger.py`, `project_archiver.py`, `gap_detector.py`, `folder_snapshot.py`, `check_restrictions.py`, `delete_report.py`. Has PROJECT-BRIEF.md (marked `brief-status: ai-drafted-needs-elad-review`, all sections TBD, tier `ice`). |
| `~/DEV/hyperframes-lab/` | One project: `test-promo/` with `index.html`, `hyperframes.json`, `renders/`, `AGENTS.md`, `CLAUDE.md`. |
| `~/Movies/` | `00 - Edit video/`, `EDITING/`, `READY/`, 4 `.fcpbundle` FCP libraries (`כלכלה מעשית`, `סרטי משפחה`, `Untitled`, plus podcast), `Motion Projects/`, `Motion Templates/`, `Titles/`, `שיווק עין הסערה/`. |

Per-skill working-directory conventions currently in effect:
- `paper-edit` → a `paper-edit/` subfolder next to the source video
- `music-to-video` → `videos/<project>/`
- `icf-video` → scripts live in the Obsidian vault, renders in the pipeline folder
- `hyperframes` → project folders with `hyperframes.json`

---

## 5. Knowledge base — 2 separate wikis

| KB | Files | Cadence | Content |
|---|---|---|---|
| `~/DEV/wiki/kb/video-with-claude/` | README + `weekly-update.md` + `CHANGELOG.md` + 5 research files | refreshed weekly | Tool/model map. Best-value picks table by category. Centers on a `fal.ai` key as the single lever for most video models. Updated 2026-07-02. |
| `~/DEV/wiki/kb/video-production/` | INDEX + 12 wiki entries + `topics.yaml` + `CHANGES.md` | ad hoc | Production playbooks: 3 paradigms, owner's stack (FCP as hub, VEED, Canva), talking-head, b-roll/faceless, kinetic captions, slideshow, own-footage editing, daily video Gantt, Claude Code pipelines, tools/pricing 2026. |

Cross-referenced from other KBs: `prompts/video-prompts`, `web-stack/hyperframes-video-as-code`,
`facilitation/presentations-html-video-pipeline`, `facilitation/storm-eye-video-catalog`,
`zug/video-tools-research`, `podcasting-il/02-recording-video`.

`video-production/INDEX.md` lists under "Powers": "A **planned** `/video-faceless`
skill (the daily machine)". A skill by that name does not exist; `faceless-explainer`
(HyperFrames bundle) does.

---

## 6. Global instructions

`~/.claude/CLAUDE.md` contains **no video section**. The only two occurrences of the
word "video" are incidental, both inside the File Drops section (`~/DEV/_inbox/`
accepts videos; confirm before deleting large video files).

Consequence of record: all video routing logic exists only inside skill `description:`
fields, which are matched against the user's phrasing.

A stored memory, `feedback_skills-wake-by-context.md`, records: "Elad doesn't type
skill names. Every skill needs rich proactive triggers. Route by context, not by
/name."

---

## 7. Overlapping capabilities (observed, not judged)

Transcription appears in at least five independent implementations:
- `paper-edit/scripts/transcribe_local.py` (PC GPU, `ivrit-ai/whisper-large-v3-ct2`)
- `/transcribe` skill
- `/live-transcribe` skill (+ `-read`, `-stop`)
- `hyperframes-media` (Whisper via the bundle's audio engine)
- `media-pipeline` / `media-pipeline-runner`
- `~/DEV/auto-transcribe/` (a DEV project)

Caption burning appears in: `paper-edit` (transcript is available post-cut),
`icf-video` (burned Hebrew ASS), `embedded-captions` (32 identities),
`hyperframes-media`, `video-use`.

TTS appears in: `icf-video` (`bin/tts.py`, ElevenLabs v3, voice "Efi"),
`hyperframes-media` (HeyGen / ElevenLabs / Kokoro), `yemot-voiceover`.

Image-to-video appears in: `icf-video` (`bin/img2video.py` → Replicate Seedance/Kling),
`higgsfield`, `video-with-claude` KB (fal.ai as the recommended single gateway).

Final Cut handoff appears in: `paper-edit` (`--fcpxml`), `icf-video`
(`bin/make_fcpx.py`, "Final Cut edit kit"), `icf-video-producer` agent.

---

## 8. Hard constraints of record

From `~/.claude/CLAUDE.md` and stored memories:

- Hebrew content and Hebrew writing stay on Claude. Never routed to a cheaper model.
- China-hosted models (DeepSeek, Kimi, GLM, Qwen, MiniMax) are default-deny. The
  owner's own thinking, business strategy, and proprietary material must never be sent
  there.
- Opus is the quality default. Haiku/Sonnet for mechanical subagents only.
- Delegation to agent teams costs roughly 7× a standard session, because each
  teammate reloads CLAUDE.md, MCP schemas, and skill descriptions independently.
- Deleting or moving files requires asking first; deletion means moving to
  `~/.Trash/`, never `rm`.
- Files are never saved to `~/` or a working-directory root.
- All skills and config files are written in English. Hebrew is for chat only.
- Every DEV project carries a `PROJECT-BRIEF.md`.
- Preference recorded: prefer passive triggers (click-to-run) over resident listeners
  (LaunchAgents, fswatch, Hammerspoon).

Stated priority order for this redesign, from the owner, verbatim:
**"קודם תוצאה טובה, אחכ חיסכון בטוקנים, אחכ חיסכון בזמן"**
(first a good result, then token saving, then time saving).

---

## 8b. CORRECTIONS — added 2026-07-24 after independent verification

Three errors in the original scan above. All three were caught by the Codex reviewer
and then verified directly. They are material to the design.

### C1. There are TWO skill install roots, not one

`~/.agents/skills/` (55 MB, 27 skills) is the HyperFrames install root. It holds the
full bundle plus `animejs`, `css-animations`, `gsap`, `lottie`, `tailwind`, `three`,
`waapi`.

`~/.claude/skills/` holds a **second, separate copy** of the same bundle. Verified by
inode: `~/.agents/skills/hyperframes/SKILL.md` is inode 132319688 and
`~/.claude/skills/hyperframes/SKILL.md` is inode 132319686. Different inodes, identical
18033-byte content. Not hardlinks. Two real copies, both dated 2026-07-01 19:41.
Combined footprint of the duplicated bundle is roughly 110 MB.

Only these `~/.claude/skills/` entries are symlinks rather than copies:

| Entry | Target |
|---|---|
| `animejs`, `css-animations`, `gsap`, `lottie`, `tailwind`, `three`, `waapi` | `../../.agents/skills/<name>` |
| `website-to-hyperframes` | `../../.agents/skills/website-to-hyperframes` |
| `video-use` | `/Users/eladtzur/DEV/video-use` |
| `astro-static-perf` | `/Users/eladtzur/DEV/site-toolkit/skills/astro-static-perf` |

Any archive or removal plan must address both roots. Handling only `~/.claude/skills/`
leaves the bundle intact and discoverable in the other root.

### C2. `website-to-hyperframes` is NOT broken

Section 1b above states it "resolves to nothing (0 files)". That is wrong. It resolves
to `~/.agents/skills/website-to-hyperframes/`, which contains a 6548-byte `SKILL.md`
and a `references/` directory. The original scan used `find <dir> -type f`, which does
not traverse a symlink without `-L`, so it reported 0 files for a working skill.

### C3. The bundle reinstalls itself — archiving is not durable

This is the most consequential correction. Verbatim from
`~/.claude/skills/hyperframes/SKILL.md` line 88:

> `npx hyperframes init` checks the installed skills against the latest on GitHub and
> installs/refreshes the **full** set whenever anything is out of date or missing — so
> a freshly init'd project always has the complete, latest set ... **The creation
> workflows scaffold with `init`**, so starting a new project always runs this check
> and pulls our latest skills from GitHub when they're stale. The `--skip-skills` flag
> is currently neutered (a temporary measure while the skills.sh registry catches up):
> passing it no longer skips the check, so every `init` checks GitHub.

And line 93:

> **Update:** `npx hyperframes skills update` — pulls the full set to the latest,
> **installing any not yet present** (same as init's install step).

And `hyperframes-cli/SKILL.md` line 12 confirms the same behaviour independently.

Consequence of record: any skill moved out of the discovery directory is reinstalled
the next time a HyperFrames creation workflow scaffolds a project, because scaffolding
calls `init`, and `init` treats a missing skill as stale and refetches the full set.
A one-time archive silently reverts itself, with no error and no notification.

The only documented opt-out is the environment variable `HYPERFRAMES_SKIP_SKILLS=1`.
`--skip-skills` does not work.

---

## 9. Environment facts

- `hf` CLI installed at `/opt/homebrew/bin/hf`
- `codex` CLI installed at `/opt/homebrew/bin/codex`, version 0.144.6, authenticated
- No `gemini`, `llm`, or `ollama` CLI on this Mac
- A Gemini API key exists in `~/DEV/shared/API-KEYS-REGISTRY.md`
- PC at 10.100.102.14 did not respond to an Ollama health check during this scan
- ElevenLabs key is in the registry; `fal.ai` key status not verified in this scan
- HyperFrames requires Node.js >= 22 and FFmpeg; supports AWS Lambda cloud rendering
- Project registry entry: `video-tools` ↔ vault `Video Editing`, tier `ice`,
  aliases: video, וידאו, fcp, final cut, video tools
