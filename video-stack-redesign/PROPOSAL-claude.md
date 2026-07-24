# Video Stack: Target Architecture

**Author:** Claude (Opus 4.8), independent reviewer
**Date:** 2026-07-24
**Status:** proposal only. Nothing on this machine was changed while writing it.

---

## The architecture in one paragraph

**One router, one engine folder, one job folder, and a config file that makes the routing
survive the next bundle install.** `video-director` is the only skill allowed to decide what
gets built; every other video skill becomes either an executor it calls or a reference file it
reads. The HyperFrames *renderer* stays (it is a real, working compositor that
`pipeline/lib/build.js` targets through the `npx hyperframes` npm package) but the HyperFrames
*skills bundle* stops being a router: 20 of its skills go to `off` in
`~/.claude/settings.json → skillOverrides`, a file no bundle reinstall can overwrite. All video
production moves into a new `~/DEV/video/` with three subtrees: `engine/` (the proven
pipeline, moved intact), `jobs/<date>-<slug>/` (one folder per video, identical layout whether
it is a build job or a cut job), and `archive/`. `~/Movies/` is not touched at all, ever, in
this plan. Six model-visible video skills remain out of the ~25 that exist today, and **not one
file is deleted to get there.** The entire surface-area reduction is one JSON key,
revertible in a single edit.

---

## Corrections to INVENTORY.md

The inventory is broadly accurate on the things that matter, but it is wrong or incomplete in
seven places, three of which change the design.

| # | Inventory claim | What is actually true | Impact |
|---|---|---|---|
| 1 | "`website-to-hyperframes` is a symlink to `../../.agents/skills/website-to-hyperframes`, **which resolves to nothing (0 files)**" | It resolves fine. The target is `/Users/eladtzur/.agents/skills/website-to-hyperframes` (`../..` from `~/.claude/skills/` is `~/`, not `~/.claude/`). It contains `SKILL.md` (6,548 bytes) + a `references/` dir, and its description is a live, aggressive router: *"Even if the user just pastes a URL, this is the skill to use."* | **Material.** This is a *third* skill competing for video routing, and the inventory declared it dead. It must be explicitly turned off. |
| 2 | "HyperFrames bundle, **15 skills**" | 20. Seven domain skills + twelve workflow skills (the inventory's own table lists 12, including `media-use`) + `website-to-hyperframes`. Total video-adjacent surface incl. `higgsfield` and `video-use` = 22. | Minor, but the count in any migration checklist must be 20/22, not 15. |
| 3 | "No resident background listeners" implied as current state (constraint §8 records only the *preference*) | Two LaunchAgents exist and **both are loaded right now**: `com.eladtzur.auto-transcribe` (PID 759, `RunAtLoad` + `KeepAlive`, polling `~/DEV/auto-transcribe/inbox`) and `com.eladtzur.video-weekly` (Mondays 09:00, drives the `video-with-claude` KB refresh). | **Material.** The stated preference is already being violated, by a *transcription* daemon, i.e. inside the exact capability that has five implementations. |
| 4 | Five locations hold video work | Six. `~/DEV/auto-transcribe/` (inbox/, done/, transcripts/, `transcribe-watcher.sh`, live logs) is a seventh transcription implementation *and* a working directory, and the inventory mentions it only in the duplication list. | Minor. |
| 5 | `~/Movies/`: "4 `.fcpbundle` FCP libraries" | Five live libraries (`כלכלה מעשית`, `סרטי משפחה`, `Untitled` at root; `פודקאסט אפרת אלעד`, `פודקאסט אושר ועושר` inside `00 - Edit video/`) plus ~40 more inside `Final Cut Backups.localized/`. Total `~/Movies` = **461 GB**; free disk = 69 GB. | **Material.** Free space is 15% of the tree in question. Any "copy then verify" plan that touches `~/Movies` is impossible. Reinforces: do not touch `~/Movies`. |
| 6 | `~/DEV/video-tools/` script list | Omits `tag_videos.py` (the 5-dimension tagger, the actual entry point per its own `CLAUDE.md`), `config.py` (single source of truth for all rules), `media_inventory.csv/.md`, `move_log.csv` (the undo ledger for a past 111 GB reorganize), and `snapshots/`. | **Material.** `move_log.csv` + `snapshots/` are the rollback for previously-moved media. Moving this folder puts a real undo path at risk. |
| 7 | `/transcribe` skill | Its file is `skill.md`, lowercase. It works only because APFS here is case-insensitive. | Minor, but it is a latent break if anything ever syncs to a case-sensitive volume. |

Two more things the inventory did not have, both verified and both load-bearing:

- **`~/DEV/ICF` is not a git repository.** There is no history to preserve and no `git mv`
  safety net for moving `content/insurance-video-v1/`. Copy-then-verify is the only safe move.
  Size: `pipeline/` = 2.5 GB, whole `insurance-video-v1/` = 2.8 GB.
- **The engine scripts are already relocatable.** Both `make.sh` and `make-ff.sh` compute
  `PIPE="$(cd "$(dirname "$0")/.." && pwd)"`: pipeline root is derived from the script's own
  location, and `PROJ="$(cd "$1" && pwd)"` accepts any absolute path. Moving `pipeline/`
  wholesale, and putting projects somewhere else entirely, is safe at the shell level. This is
  the single most important verification in this document, because it turns Q3 from a rewrite
  into a `cp -a`.

**Where the inventory is right and it matters:** the router collision is real and is quoted
accurately; `bin/make-ff.sh` and `bin/ffrender.py` exist and are the newest things in the
pipeline (Jul 3, vs. the HyperFrames path's Jul 1); `paper-edit` is complete and self-contained
(6 scripts, all present); the PC was unreachable during the scan and I could not reach it either.

---

## The diagnosis the inventory stops short of

The inventory records that two skills claim "read this first." That is the symptom. The disease
is that **five documents disagree about which engine is the default, and the four that are wrong
are the four that are easy to find.**

| Document | What it says the default is | Written |
|---|---|---|
| `hyperframes/SKILL.md` | HyperFrames, for everything, explicitly over other installed tools | Jul 1 |
| `video-with-claude/README.md` §2 | "**HyperFrames** (default)" | Jul 2 |
| `icf-video/SKILL.md` | `bin/make.sh`: the HyperFrames flow. Warns about 4K, 10-min timeouts, "15-25 min for a ~2 min video" | Jul 1 |
| `pipeline/README.md` | `bin/make.sh`. Does not mention `make-ff.sh`, `ffrender.py`, `genimg.py`, `img2video.py`, `make_fcpx.py`, or `ingest-voice.sh` at all | Jul 1 |
| `video-director/references/engines.md` | **FFmpeg-direct**, 1–3 min, native 1080×1920. HyperFrames = "LAST RESORT" | Jul 3 |

Exactly one document describes the engine that actually solves Elad's most common job, and it is
a `references/` file two hops down from a skill that another skill's description is actively
telling the model to ignore. The FFmpeg-direct engine is the newest, fastest and most correct
thing in the stack, and it is the least discoverable thing in the stack.

**Second measured finding.** There are 173 skills with frontmatter installed, whose
`name` + `description` total **81,574 characters ≈ 20,400 tokens**. Claude Code budgets the
skill listing at ~1% of the context window and drops the descriptions of least-used skills first
when it overflows. On a 1M-context model that budget is ~10,000 tokens: **the listing is
roughly 2× over budget today**, and on a 200k model it would be 10× over. The HyperFrames bundle
plus `higgsfield` and `video-use` account for 3,544 of those tokens, **17.4% of the entire
listing**, for capabilities that have produced exactly one artifact on this machine: a single
test render in `~/DEV/hyperframes-lab/test-promo/renders/` dated 2026-05-06, untouched since.

That reframes surface-area reduction. It is not a token-saving measure, which would rank second
in Elad's priority order. **It is a correctness measure**, which ranks first: while the listing
is over budget, which skills the model can see at all is nondeterministic, and `video-director`
is a small, recently-installed skill competing against 22 loud ones. Cutting the surface is how
you make the router reliably visible.

---

# 1. Routing

**Confidence: high.** The mechanism is documented in the installed changelog and the version
here supports it.

### The single entry point is `video-director`

Not because it was installed later, but because it is the only artifact in the stack that
encodes what Elad actually ships. It knows: 9:16 is the default, never hard-crop a head, titles
come from Elad's written Hebrew and never from a transcript, no long render without an approved
sketch, Hebrew VO is `eleven_v3` voice "Efi", Final Cut is the finisher.

`hyperframes` knows none of that. Its own text sets **16:9 as the default** and says to use 9:16
"only for a named vertical destination." Its twelve workflows are built around inputs Elad does
not have: a SaaS product URL, a GitHub pull request, a Remotion project, a music track. Its
`/faceless-explainer`, the nearest match to Elad's job, invents every visual from an LLM and has
no concept of a Hebrew RTL burned caption. Handing Elad's daily job to that router does not
produce a worse video; it produces a *different, wrong* video, 30–40 minutes later.

`video-director` is also incomplete and must be rewritten (see §2), but it is incomplete in the
way a correct thing is incomplete. `hyperframes` is complete and wrong.

### The mechanism, in three layers

Only layer 1 is enforcement. Layers 2 and 3 are the parts that keep layer 1 honest over time.

#### Layer 1: `skillOverrides` in `~/.claude/settings.json` (the actual fix)

Claude Code 2.1.131+ implements a per-skill override with four states; this machine runs 2.1.178.
The changelog entry is unambiguous:

> `skillOverrides` setting now works: `off` hides from model and `/`, `user-invocable-only`
> hides from model only, `name-only` collapses description

This is the right mechanism for four independent reasons, and I do not think any other mechanism
qualifies:

1. **It lives outside the skill folders.** `npx skills add heygen-com/hyperframes --all` and
   `npx hyperframes skills update` rewrite `~/.claude/skills/<name>/SKILL.md`. Neither can touch
   `~/.claude/settings.json`. Editing the bundled skills' own frontmatter
   (adding `disable-model-invocation: true`) would work today and be silently reverted by the next
   `npx hyperframes init`, which the bundle's own SKILL.md says runs automatically at the start
   of every creation workflow. **That is exactly the "works today, drifts on next install"
   failure the brief rules out.**
2. **`off` removes the description from context entirely,** so it also recovers the 3,544
   tokens of listing budget, which is the correctness issue above.
3. **It deletes nothing.** Files stay on disk, readable with the Read tool, satisfying the
   no-delete constraint completely and making rollback a one-line edit.
4. **It does not touch the renderer.** Verified: `pipeline/bin/render.sh` invokes
   `npx --yes hyperframes render`, the **npm package**. Skills and npm packages are separate
   installs. Setting the `hyperframes` *skill* to `off` has zero effect on the kinetic engine.

The concrete block to add to `~/.claude/settings.json`:

```json
{
  "skillOverrides": {
    "hyperframes":              "off",
    "website-to-hyperframes":   "off",
    "faceless-explainer":       "off",
    "product-launch-video":     "off",
    "website-to-video":         "off",
    "pr-to-video":              "off",
    "motion-graphics":          "off",
    "slideshow":                "off",
    "talking-head-recut":       "off",
    "embedded-captions":        "off",
    "music-to-video":           "off",
    "general-video":            "off",
    "remotion-to-hyperframes":  "off",
    "media-use":                "off",
    "hyperframes-core":         "off",
    "hyperframes-animation":    "off",
    "hyperframes-creative":     "off",
    "hyperframes-media":        "off",
    "hyperframes-cli":          "off",
    "hyperframes-registry":     "off",
    "higgsfield":               "off",
    "video-use":                "off"
  }
}
```

Twenty-two keys. Every one of those directories stays exactly where it is. `video-director`
reaches the ones it still needs (`hyperframes-core` for the composition contract,
`hyperframes-cli` for render flags) by **reading the file at its path**, which is what
`references/engines.md` already does for its own content. An `off` skill is a document, not a
competitor.

#### Layer 2: three lines in `~/.claude/CLAUDE.md`

Detailed in §5. Deliberately minimal, and deliberately **not** routing text: the routing
conflict is a precedence problem, and precedence is now solved in settings.json. Duplicating
trigger words into the global file would pay twice for the same wake-up.

#### Layer 3: a checked-in allowlist and a click-to-run drift check

The failure mode layer 1 cannot cover: a future bundle version ships a skill under a **new
name**, which arrives `on` by default because there is no key for it.

`~/DEV/video/bin/video-router-check.sh` (passive, run by hand or by Claude as step 0 of
`video-director` when anything looks off, no LaunchAgent, no fswatch):

1. Scan every `~/.claude/skills/*/SKILL.md` frontmatter for video trigger words
   (`video`, `render`, `animation`, `motion`, `caption`, `subtitle`, `סרטון`, `וידאו`).
2. Diff that set against `~/DEV/video/router-allowlist.txt` (checked in, 6 names).
3. Print anything present but neither allowlisted nor keyed in `skillOverrides`, with the
   suggested `"off"` line ready to paste.
4. Also assert `hyperframes` is still `off` and that `video-director/SKILL.md` still
   contains the path to `~/DEV/video/engine/`.

Run it after any `npx skills add`, any HyperFrames workflow, and as the first step of the first
video job of any month. It takes under a second and prints nothing when the world is correct.

### What I rejected

- **Renaming or editing the bundled skills' descriptions.** Overwritten by the next `init`.
- **A `UserPromptSubmit` hook that injects "read video-director first".** Tempting: it would be
  free on non-video prompts. But it puts routing logic in a shell script the model cannot see,
  it fires on Hebrew/English keyword matches that will misfire, and it makes debugging a bad
  route require reading `hooks.json`. Skill routing should be legible in skill land.
  Reconsider only if layer 1 measurably fails.
- **Uninstalling the bundle.** Violates the no-delete constraint, throws away a genuinely
  excellent authoring contract in `hyperframes-core`, and is not reversible in one edit.

---

# 2. Surface area

**Confidence: high on the keeps, high on the offs, medium on `embedded-captions` and
`video-use`: both flagged with the specific test that would settle them.**

**Six model-visible video skills. Three agents. Zero deletions.**

### Keep and leave alone (3)

| Skill | Why |
|---|---|
| `paper-edit` | Newest thing in the stack (2026-07-24), self-contained, 6 scripts all present, and the only Hebrew-correct route for job (b). Local `ivrit-ai/whisper-large-v3-ct2` beats every cloud option on Hebrew and costs nothing. The `snap_cuts.py` LOUD/quiet/silent grading is a genuinely original piece of craft. Do not touch it. |
| `media-pipeline` | Different job from everything else: recordings → readable text, at course/webinar scale, from Drive/YouTube/Vimeo. Has a working reference implementation (livat-hazugiyut) and a runner agent. Out of `video-director`'s scope by design. |
| `convert` | Generic file conversion (ffmpeg/ImageMagick/pandoc). Not a video-production skill; it just happens to handle video. No conflict. |

### Keep but rewrite (3)

| Skill | What is wrong | The rewrite |
|---|---|---|
| `video-director` | Its decision tree omits `paper-edit` (created 3 weeks after it), omits `video-use`, omits `media-pipeline`, and its "where things live" section points at a path that this proposal moves. Its Step 1 table is otherwise correct and should survive verbatim. | Add three rows: *own footage → rough cut* → `paper-edit`; *recording → text* → `media-pipeline`; *conversational edit of finished footage* → the production-rules reference. Repoint all paths to `~/DEV/video/`. Add the `bin/new-job.sh` first step. Keep the description **short**: it is paid on every request. |
| `icf-video` | Stale by two days and one engine. Documents `bin/make.sh`, the 4K/timeout/downscale dance, and "15-25 min for a ~2 min video". All of these describe the engine `engines.md` now calls a last resort. A model reading this skill in isolation will build the slow video. | Make `make-ff.sh` the documented flow. Demote the 4K/timeout section to "only if you deliberately chose the kinetic engine." Keep the name (renaming breaks `icf-video-producer`, two vault SOP notes, and `engines.md` for no gain) but state in line 1 that it serves both businesses, not only ICF. |
| `transcribe` | Duplicates a better implementation and has a cloud fallback (OpenRouter Groq Whisper) that sends audio off-machine: fine for a public clip, wrong by default for a client meeting or unpublished course. Also its file is `skill.md`, lowercase. | Reduce to a ~15-line wrapper that calls the canonical `paper-edit/scripts/transcribe_local.py`. Rename the file to `SKILL.md`. Make the cloud fallback opt-in with an explicit flag and a one-line warning, never automatic. |

### Turn off: the HyperFrames bundle, all 20 (`skillOverrides: "off"`)

Files stay. Descriptions leave the listing.

| Skill | Verdict | Reason |
|---|---|---|
| `hyperframes` | **off** | The single highest-value override. It is the skill asserting default status over `video-director`. Its capability map survives as a document at a known path. |
| `website-to-hyperframes` | **off** | The inventory's "0 files" is wrong; it is live and it is the most aggressive router of all ("Even if the user just pastes a URL, this is the skill to use"). Also a duplicate of `website-to-video`. |
| `product-launch-video`, `website-to-video`, `pr-to-video`, `remotion-to-hyperframes` | **off** | Inputs Elad does not have: a SaaS product URL, a site tour, a GitHub PR, a Remotion project. Nothing in the inventory or on disk suggests he has ever produced one of these. |
| `music-to-video` | **off** | 6.2 MB, 132 files. Beat-synced lyric video. Not on the list of things he ships. |
| `faceless-explainer` | **off** | The one that looks like Elad's job and is not. Its premise is *every visual is LLM-invented*. Elad's explainers use real Nano-Banana stills of ordinary Israelis, or his own photos, with documentary realism as an explicit rule. It also has no Hebrew RTL caption concept. `make-ff.sh` does this job better and 20× faster. |
| `motion-graphics`, `slideshow` | **off** | `presentation-builder` and `hebrew-keynote-builder` already serve decks and are RTL-aware; `slideshow` outputs a web deck, not a Keynote file, and Elad finishes in Keynote. `motion-graphics` is a sub-10-second unnarrated form he does not ship. |
| `talking-head-recut` | **off** | Overlay cards on footage. He does this in Final Cut, which he knows well. |
| `general-video` | **off** | Declared fallback for a router that is being turned off. Turning off the router while leaving its fallback on is the worst of both. |
| `media-use` | **off** | Media resolver keyed to the HeyGen catalog. `~/DEV/shared/media-bank/` is the existing, working equivalent and is already referenced by `engines.md` §6. |
| `hyperframes-core`, `-animation`, `-creative`, `-media`, `-cli`, `-registry` | **off as skills, retained as reference** | These are the good part of the bundle. `hyperframes-core` is the authoring contract that `pipeline/lib/build.js` targets, and `hyperframes-cli` documents the render flags that `render.sh` sets. They must remain readable, and they will, by path. They should never be *routed to*, because they are not workflows. |

### Turn off: adjacent (2)

| Skill | Verdict | Reason and the evidence that would reverse it |
|---|---|---|
| `higgsfield` | **off** | Direct duplicate of `bin/img2video.py`, which is already wired into the working pipeline (Replicate Seedance/Kling, native 9:16, reads `motion-prompts.json`, drops clips where `ffrender.py` expects them). Integrated beats standalone. Higgsfield's distinctive feature, Soul ID character consistency, serves the AI-influencer-persona idea that lives in the KB as research, not as a shipped job. **Reverse if:** Elad decides to build a synthetic presenter, at which point Soul ID has no equivalent in the stack. |
| `video-use` | **off, and harvest** | 23 KB of real craft: subtitle ordering, lossless concat, 30 ms audio fades, PTS shifting, word-boundary cuts. But it transcribes via ElevenLabs Scribe (cloud, per-minute credits) where `paper-edit` uses local `ivrit-ai` Hebrew for free, and its territory otherwise overlaps `paper-edit` almost exactly. Quality is priority #1 and on Hebrew, local wins. **Action:** before turning it off, copy its hard production-correctness rules into `~/.claude/skills/video-director/references/production-rules.md`. The `~/DEV/video-use/` git repo stays where it is, untouched. |

### Leave entirely alone (out of scope, do not include in this migration)

`live-transcribe`, `live-transcribe-read`, `live-transcribe-stop` (live mic dictation, a
different job); `gsap`, `lottie`, `three`, `animejs`, `css-animations`, `waapi` (web-animation
skills symlinked from `~/.agents/skills/`, they serve web work); `presentation-builder`,
`hebrew-keynote-builder` (decks); `yemot-voiceover` (IVR phone lines, Efrat's domain);
`visual-content` (stills). Noting that the six animation symlinks do consume listing budget and
are a reasonable second-pass target, but they are not video, and mixing them in muddies a clean
migration.

### The genuinely uncertain one

**`embedded-captions`**: I recommend `off`, at ~60% confidence, and I want to be explicit about
why the confidence is not higher. It is the most substantial workflow skill in the bundle
(3.6 MB, 144 files, 32 visual identities, local Whisper + RVM matting so the subject occludes
the captions). Nothing in Elad's stack does subject-occluding captions. Its `anchor` identity,
a quiet verbatim lower-third rail, is a sane default and would suit a podcast clip.

The reason to turn it off anyway: its catalog is 32 *English typographic* identities, and
nothing in its description, its trigger list, or its 32 identity names mentions RTL or Hebrew. A
caption engine that mis-orders Hebrew is worse than no caption engine, and the kinetic-captions
wiki entry (`video-production/wiki/kinetic-text-captions`) explicitly flags "Hebrew RTL gotchas"
as a known hazard in this exact category.

**The single piece of evidence that settles it:** run it once on a 30-second Hebrew talking-head
clip with the `anchor` identity and look at one frame. If the Hebrew renders right-to-left with
correct final-letter forms, promote it to `name-only` and make it the canonical caption engine
for existing footage. If it does not, `off` is correct and permanent. This costs about ten
minutes and should be step 7 of the migration, not a blocker for steps 1–6.

### Agents: keep all three, change nothing

`icf-video-producer`, `paper-edit-engine`, `media-pipeline-runner`. Each pairs 1:1 with a kept
skill, the pattern is consistent, and `paper-edit-engine` already carries `model: opus` and an
explicit "never routes Hebrew to a cheaper model" clause. `icf-video-producer` needs one edit:
repoint it at `~/DEV/video/engine/` and at `make-ff.sh`. `visual-content` is stills, unrelated,
leave it.

### The count

| | Before | After |
|---|---|---|
| Model-visible video skills | ~25 | **6** (`video-director`, `icf-video`, `paper-edit`, `media-pipeline`, `transcribe`, `convert`) |
| Video agents | 3 | 3 |
| Files deleted | n/a | **0** |
| Listing tokens recovered | n/a | ~3,544 (17.4% of the whole skill listing) |
| Steps to revert everything in this section | n/a | **1** (delete one JSON key) |

---

# 3. The folder

**Confidence: high on the design, high on the safety of the engine move (verified at the shell
level), high on leaving `~/Movies` alone.**

## The tree

```
~/DEV/video/                          # NEW. The one place Claude does video work.
├── PROJECT-BRIEF.md                  # per the global rule; tier warm, not ice
├── CLAUDE.md                         # project-scoped: engine defaults, gates, paths
├── README.md                         # 20 lines: what lives where, what to run
├── router-allowlist.txt              # 6 names, input to video-router-check.sh
│
├── engine/                           # ← MOVED intact from ICF/content/insurance-video-v1/pipeline/
│   ├── bin/
│   │   ├── make-ff.sh                # ⭐ DEFAULT: tts → ffrender. 1–3 min, native 1080×1920
│   │   ├── ffrender.py               # the FFmpeg-direct compositor
│   │   ├── make.sh                   # kinetic path: tts → build.js → render.sh (HyperFrames)
│   │   ├── render.sh                 #   (npx hyperframes render, the npm pkg, not the skill)
│   │   ├── tts.py                    # ⭐ CANONICAL TTS: ElevenLabs v3, voice Efi, + per-cue timing
│   │   ├── genimg.py                 # realistic b-roll stills (documentary, not the ad booster)
│   │   ├── broll.sh                  # prompt → still (Gemini Nano Banana)
│   │   ├── img2video.py              # ⭐ CANONICAL image→video: Replicate Seedance/Kling
│   │   ├── make_fcpx.py              # ⭐ CANONICAL FCPXML for built videos
│   │   └── ingest-voice.sh           # Elad's own recorded VO instead of TTS
│   ├── lib/                          # effects.js, theme.css, build.js
│   ├── config.json  EFFECTS.md  effects-gallery.html  gallery-assets/
│   └── README.md                     # REWRITTEN, currently documents only the slow path
│
├── jobs/                             # one folder per video. Same layout for build and cut jobs.
│   └── 2026-07-24-keren-kaspit/
│       ├── JOB.md                    # brief · engine chosen + why · gate log · output paths
│       ├── script.json               # build jobs: the single source of truth
│       ├── source/                   # cut jobs: SYMLINK to the original in ~/Movies (never a copy)
│       ├── assets/                   # b-roll stills, AI clips, master.mp3, built.json
│       ├── paper-edit/               # cut jobs: transcript → clean → review.html → cuts → snapped
│       ├── renders/                  # sketch-*.mp4, v1.mp4, v2.mp4 …
│       └── fcp-kit/                  # ⭐ THE HANDOFF: master.mp4 + voiceover.mp3 + broll/ + .fcpxml + README
│
├── shared/
│   ├── media-bank -> ~/DEV/shared/media-bank/    # symlink to the existing reusable-stills bank
│   ├── brand.md                      # navy/gold, Heebo / Suez One / Frank Ruhl (from engines.md §6)
│   └── voices.md                     # voice_id pointers only, NEVER a key (keys stay in ~/.claude/secrets/)
│
├── archive/                          # finished jobs + retired experiments
│
└── bin/
    ├── new-job.sh                    # scaffold jobs/YYYY-MM-DD-<slug>/ from template. build | cut
    ├── to-fcp.sh                     # assemble fcp-kit/, open it in Finder
    └── video-router-check.sh         # the §1 layer-3 drift check
```

## The six questions this tree answers

**Where does a new job start.** `~/DEV/video/bin/new-job.sh <slug> build|cut`. It creates the
dated folder, writes `JOB.md` from a template with the gate checklist pre-filled, and for a cut
job symlinks the source. Passive, click-to-run, no listener. This is also the answer to "an
efficient folder where Claude works on video": the first thing any video request does is create
its own dated workspace, so a job is never scattered and never nameless.

**Per-job layout.** Identical for both job types: the same seven children, some empty depending
on type. This matters more than it looks: it means `to-fcp.sh` and any future tooling can
operate on a job without asking what kind it is, and it means Elad can find any past video's
script, its b-roll, its transcript and its FCP kit in the same four places every time.

**Shared assets.** `~/DEV/video/shared/`. `media-bank` is a symlink, not a copy. The bank
already exists at `~/DEV/shared/media-bank/`, is already referenced by `engines.md` §6, and is
already tagged `reusable-media`. Duplicating it would guarantee drift. `brand.md` and `voices.md`
are new, short, and consolidate facts currently scattered across `engines.md`, `icf-video`, and
`config.json`.

**Where finished renders go.** They stay in `jobs/<job>/renders/` until finishing. The
**deliverable** (the thing Elad publishes) goes to `~/Movies/READY/<Finance|Efrat|Personal|Training>/`,
which already exists with exactly those four subfolders. I am deliberately not inventing a new
delivery location: `READY/` is his own established convention and `video-tools`'s `reorganize.py`
already knows it.

**Handoff to Final Cut.** `bin/to-fcp.sh <job>` builds `jobs/<job>/fcp-kit/` and reveals it in
Finder. It picks the generator by job type: `engine/bin/make_fcpx.py` for a built video (a
multi-clip timeline with the b-roll track and separated audio), `paper-edit`'s `--fcpxml` for a
cut (one clip per kept range, every cut still adjustable). Both write the **same folder layout**:
master MP4, `voiceover.mp3`, `broll/`, the `.fcpxml`, and a README naming the target library.
Elad imports into `כלכלה מעשית.fcpbundle` for finance, `פודקאסט אפרת אלעד.fcpbundle` for the
podcast. Unifying at the *destination* rather than the *generator* is the right call: the two
generators produce structurally different timelines and merging them would lose the thing that
makes each correct.

**What happens to the existing locations.** Below.

## Verdict per existing location

| Location | Verdict | Exact destination | What breaks / risk |
|---|---|---|---|
| `~/DEV/ICF/content/insurance-video-v1/pipeline/` (2.5 GB) | **MOVE** (copy → verify → archive the original) | `~/DEV/video/engine/` | **The scripts themselves survive**: `make.sh`/`make-ff.sh` derive `PIPE` from `$(dirname $0)/..`, so the pipeline root travels with them; `PROJ="$(cd "$1" && pwd)"` accepts any absolute path. What breaks is **documentation**: `video-director/SKILL.md` step 4, `references/engines.md` (3 path references), `icf-video/SKILL.md` line 9, the `icf-video-producer` agent, `pipeline/README.md`, and two vault SOP notes (`SOP — מטקסט לסרטון`, `וורקפלואו — הפקת סרטון`). All must change in one commit. `~/DEV/ICF` is **not a git repo**, so there is no `git mv` and no history: copy-then-verify is mandatory. Risk: **medium**, entirely on the doc-reference side. |
| `~/DEV/ICF/content/insurance-video-v1/pipeline/projects/` (9 projects) | **MOVE** with date prefixes | `~/DEV/video/jobs/2026-07-<name>/` | Each project is self-contained (`script.json` uses relative `assets/` paths). Suggest: `insurance-ff` → `2026-07-03-insurance-ff` etc.; `night` and `insurance-sketch` are experiments → `archive/`. Risk: **low**. |
| `~/DEV/ICF/content/insurance-video-v1/` (8 loose MP4s + `assets/`, `broll/`, `poster.jpg`, ~275 MB) | **ARCHIVE** (ask first) | `~/DEV/video/archive/2026-07-insurance-v1/` | Nothing. These are finished and intermediate outputs (`SKETCH-*`, `PROOF-*`, `DEMO-*`, v1–v5). Keeping them next to the engine that made them preserves the only record of how the pipeline evolved. Risk: **none**. |
| `~/DEV/video-tools/` | **LEAVE IN PLACE** | n/a (stays) | It is a **media-library** tool, not a video-*production* tool: `tag_videos.py` + `config.py` tag 532 files / 295 GB in `~/Movies` across 5 dimensions, `reorganize.py` moved 111 GB, and `move_log.csv` + `snapshots/` are the **undo ledger for those moves**. Folding it into `~/DEV/video/` would merge two unrelated jobs and put a live rollback path at risk. Its own PROJECT-BRIEF is an unreviewed AI draft (`brief-status: ai-drafted-needs-elad-review`, tier `ice`, every section TBD). That is evidence it is dormant infrastructure, not active production. **Action:** link it from `~/DEV/video/README.md` as "the library tool," and leave everything else alone. |
| `~/DEV/hyperframes-lab/` | **ARCHIVE** (ask first) | `~/DEV/video/archive/hyperframes-lab-2026-05/` | Nothing. One `test-promo/` with a single render dated 2026-05-06, untouched for 2.5 months. Risk: **none**. |
| `~/DEV/auto-transcribe/` | **RETIRE the daemon, keep the folder** (ask first) | plist → `~/Library/LaunchAgents/disabled/` (Elad's own existing pattern, 8 plists already there) | The `com.eladtzur.auto-transcribe` LaunchAgent is **running right now** (PID 759, `KeepAlive`), polls an inbox, and violates the recorded no-resident-listeners preference. Its `transcribe-watcher.sh` becomes a manual script that calls the canonical transcriber. `~/DEV/auto-transcribe/transcripts/` and `done/` stay put; they hold real output. Risk: **low, but ask**: Elad may be actively dropping files into that inbox. |
| `~/Movies/` (461 GB) | **DO NOT TOUCH. AT ALL. IN ANY STEP.** | n/a | Five live `.fcpbundle` libraries plus ~40 backup bundles. Final Cut stores **absolute paths to external media**; moving a single source file breaks the link and the repair is manual, per clip, per library. Free disk is 69 GB against a 461 GB tree, so there is no copy-then-verify option here even in principle. `~/DEV/video/jobs/*/source/` reaches into `~/Movies` **by symlink only, read-only**. This is the one hard prohibition of the entire plan. |

**What the new folder does not do:** it does not become the home for finished media. `~/Movies`
remains the media library and `~/DEV/video` remains the workshop. Keeping that line sharp is what
stops `~/DEV/video` from growing into a second 400 GB tree that iCloud, Time Machine and git all
have opinions about.

---

# 4. Duplication

**Confidence: high on transcription, TTS and image→video; high on the captions *split*; medium
on whether `media-pipeline` should be forced onto the same transcriber (flagged).**

The principle: for each capability, the canonical implementation is the one **already coupled to
something that works**, not the one with the most features. Coupling is what makes it correct;
features are what made the duplicates.

### Transcription: 6 implementations (inventory said 5)

**Canonical: `~/.claude/skills/paper-edit/scripts/transcribe_local.py`.** PC GPU over Tailscale,
`ivrit-ai/whisper-large-v3-ct2`, word-level timings, handles Tailscale being down, audio
extraction, upload and PC cleanup. It is the only one using a Hebrew-specific model, it is free,
and nothing leaves the house.

I considered lifting it out of the skill folder into `~/DEV/video/engine/bin/transcribe.py` for
tidiness and decided **against**: it is invoked via `${CLAUDE_SKILL_DIR}`, it works today, and
"it currently works" carries weight per the brief. Everyone else calls it at its absolute path.

| Duplicate | Disposition |
|---|---|
| `/transcribe` (faster-whisper `medium` + OpenRouter Groq fallback) | **Rewrite as a wrapper.** ~15 lines calling the canonical script. Its Groq fallback silently sends audio to a third party, acceptable for a public clip, wrong by default for a client meeting. Make it an explicit opt-in flag with a printed warning. (Groq is US-hosted, so not a China-policy violation, but it is still an unannounced data boundary crossing.) |
| `~/DEV/auto-transcribe/transcribe-watcher.sh` | **Retire the daemon** (§3). Keep the script as a manual batch runner that calls the canonical transcriber. |
| `hyperframes-media` Whisper | **Unreachable** once the skill is `off`. No further action. |
| `live-transcribe*` | **Not a duplicate.** Live mic dictation, ElevenLabs Scribe v2 Realtime, a different job. Leave alone. |
| `media-pipeline` local transcription | **Keep as a second canonical, with a stated boundary.** Two canonicals are fine when the boundary is crisp, and here it is: **`paper-edit` = one file you are going to edit; `media-pipeline` = many files you are going to read.** Different outputs (word timings for cutting vs. speaker-labeled prose), different scale, different runner agent. **Uncertainty:** I did not read `media-pipeline`'s transcription script and cannot say whether it uses the same model. **The evidence that settles it:** diff its model string against `ivrit-ai/whisper-large-v3-ct2`. If identical, collapse it onto the canonical script and delete the duplicate call site. If it uses a batch-optimized path, leave both and document why. |

### Captions: 5 implementations

There is no single canonical, and forcing one would be wrong. The honest split is **by input**,
and it falls directly out of `video-director`'s hard rule #1 ("captions come from Elad's correct
written text, never from a transcription"):

| Input | Canonical | Why it must be this one |
|---|---|---|
| Video **built from a script** | `engine/bin/ffrender.py` burned Hebrew ASS | It is the only implementation that takes caption text from `script.json` (Elad's written Hebrew) rather than from a transcript. It also owns the RTL forcing (RLM prefix for leading digits), the safe-zone margins, the gold key word, and the no-trailing-period rule. Those are not styling preferences; they are the accumulated fixes. |
| Video that is **footage** | `paper-edit` transcript → `.srt` emitted beside `rough-cut.mp4` | The cleaned, human-corrected transcript already exists at this point with exact timings. Generating captions from anything else would re-introduce the errors stage 2 just removed. **Small addition needed:** have `render_cut.py` write `rough-cut.srt` from `clean.json` in the same pass. Then burn with ffmpeg, or let Final Cut import the SRT. |
| any other | `embedded-captions`, `hyperframes-media`, `video-use` captions | **Retired by override.** See §2 for the one test that could promote `embedded-captions` back for the footage case. |

### TTS: 3 implementations

**Canonical: `engine/bin/tts.py`.** ElevenLabs `eleven_v3` (Hebrew-native, never
`multilingual_v2`), cloned voice "Efi", key sourced from `~/.claude/secrets/elevenlabs.env` and
never passed as an argument. The reason it is canonical is not the model choice: it is that it
emits **per-cue timing into `built.json`**, which is what locks every caption and every cut to
the voice. A TTS that returns only audio cannot replace it without rebuilding the whole timing
chain. `hyperframes-media` TTS (HeyGen / ElevenLabs / Kokoro) is retired by override.
`yemot-voiceover` is a different domain entirely (IVR phone menus, Efrat's project), leave it
alone; it is not a duplicate of anything here.

`engine/bin/ingest-voice.sh` is the sanctioned escape hatch when Elad records himself (the
quality ceiling, per `engines.md` §4), and it feeds the same timing chain.

### Final Cut handoff: 3 implementations

**Unify the destination, keep both generators.**

- `engine/bin/make_fcpx.py`: canonical for **built** videos. Emits a timeline with the b-roll
  track and separated audio.
- `paper-edit --fcpxml`: canonical for **cuts**. Emits one clip per kept range so every cut
  stays adjustable (`Select All → Create Compound Clip` to flatten).
- `icf-video-producer`'s "edit kit" is not a third implementation; it calls `make_fcpx.py`.
  Just repoint it.

These produce structurally different timelines by design and merging them would destroy what
makes each right. They unify at the interface: both write into `jobs/<job>/fcp-kit/` with the
same five items, and `bin/to-fcp.sh` chooses the generator from the job type. One destination,
one folder shape, two generators.

### Image → video: 3 implementations

**Canonical: `engine/bin/img2video.py`** (Replicate, default `bytedance/seedance-1-lite`, native
9:16, reads `motion-prompts.json`, writes clips where `ffrender.py` already knows to look). The
hybrid pattern in `engines.md` §3 (2–3 HERO stills animated, everything else free Ken Burns)
is the right default and should be stated in `video-director`. `higgsfield` retired by override.

**Unresolved:** the `video-with-claude` KB's "one-key principle" says a single `fal.ai` key
fronts Seedance, Veo 3.1, Kling, Hailuo, LTX and Wan behind identical endpoints, which would be
a genuinely better gateway than Replicate. The inventory says the fal.ai key status was not
verified and I did not verify it either (reading the key registry is out of scope for a design
task). **The evidence that settles it:** `grep -ci 'fal\.ai\|fal_key' ~/DEV/shared/API-KEYS-REGISTRY.md`.
That returns a count, not a value. If it is zero, the KB's central recommendation is aspirational and should
be labelled as such in `README.md`, because a document that says "get a fal.ai key" reads, three
months later, like a document that says "we use fal.ai."

---

# 5. Waking up: what goes in the global instruction file

**Confidence: high.** This is the section where I most want to be held to the numbers.

## The answer: three lines, ~60 tokens, and none of them are routing

```markdown
# Video
- Any video request → the `video-director` skill decides the engine and owns the gates.
  It is the only video entry point; HyperFrames is an engine behind it, never a router.
- Video work starts in `~/DEV/video/` (`bin/new-job.sh`). Never start a video job elsewhere.
- Never run a full render before Elad has approved a low-res sketch.
```

## Why so little

The instinct is to put trigger words in `CLAUDE.md` because the stored memory says Elad does not
type skill names. **That instinct is wrong here, and acting on it is the expensive mistake.**

Skill `name` + `description` are already loaded into every request, in every project. That is
how skills work. `video-director`'s description already carries a rich Hebrew and English trigger
list ('סרטון', 'וידאו', 'בנה סרטון', 'faceless', 'reel', 'שורט', 'render video', 'סרטון מהטקסט',
and a dozen more). Copying any of that into `CLAUDE.md` pays for the same wake-up twice, forever,
on every request in every project, including every request that has nothing to do with video,
which is the overwhelming majority.

The wake-up was never broken. **Precedence** was broken, and §1 fixes precedence in
`settings.json`, which costs zero tokens per request. Once `hyperframes` and its 21 companions
are `off`, `video-director`'s description is uncontested, and the global file has nothing left to
do for routing.

## The boundary, stated as a test

> **Does this need to be true when no video skill has fired?**
> Yes → global file. No → skill.

Three things pass that test, and I could not construct a fourth.

**Line 1 passes** as insurance against one specific, measured failure. There are 173 skills with
frontmatter installed, totalling **~20,400 tokens** of name + description. Claude Code budgets
the skill listing at ~1% of context and drops the least-used skills' descriptions first when it
overflows. On a 1M-context model that is ~10,000 tokens: the listing is **about 2× over budget
right now**. When `video-director`'s description is the one that gets dropped, the entire
architecture in §1 silently stops working and the failure is invisible. One sentence in the
global file is the cheapest possible backstop for that. It is also true when no skill has fired,
by construction.

**Line 2 passes** because folder placement is decided *before* any skill loads. If Elad says
"תעשה מזה סרטון" while sitting in `~/DEV/storm-eye-site`, the very first move, creating a
working directory, happens in the wrong place unless something already loaded says otherwise.
The global file already carries the equivalent rule for `~/DEV/_inbox/`; this is the same shape
of rule for the same reason.

**Line 3 passes** because it is the one rule whose violation is expensive and whose violation
path bypasses skills entirely. Two HyperFrames renders have already failed on this machine after
30–40 minutes and **deleted their own frames on failure**. If Elad or Claude reaches for a raw
`ffmpeg` or `npx hyperframes render` command without going through `video-director`, only a
global rule stands between that and another 40 lost minutes. It is also the highest-leverage
sentence in the whole stack per token: it protects Elad's #1 priority (a good result) and his #3
(time) simultaneously.

## What must NOT go in the global file

Everything else. Specifically, and each for a stated reason:

| Do not add | Where it belongs | Why not global |
|---|---|---|
| The engine decision tree (FFmpeg-direct / HyperFrames / Replicate / FCP) | `video-director/SKILL.md` step 1 | It changes whenever an engine is added. A global file that changes is a global file nobody trusts. |
| Trigger word lists (Hebrew or English) | skill `description:` | Already loaded on every request. Duplicating them is paying twice for one wake-up. |
| The 7-step workflow and gate definitions | `video-director` step 2 + `JOB.md` template | ~400 tokens. Needed on maybe 2% of requests. |
| Engine paths, script names, flags | `references/engines.md` | Changes on the day `~/DEV/video/` is created and again on every refactor. |
| Anything at all about HyperFrames | `skillOverrides` + `references/engines.md` | Naming it globally re-elevates the thing being demoted. `settings.json` handles it silently and for free. |
| Which model handles Hebrew | already in `CLAUDE.md` §Model Routing | Present, correct, do not duplicate under a video heading. |
| Which transcriber is canonical | `video-director` + `paper-edit` | Only matters once a transcription is actually requested. |
| Caption rules (no trailing period, RTL, safe zones) | `ffrender.py` + `references/engines.md` | Enforced in code, which is stronger than enforced in prose. |

## The one thing I would reconsider, and what would change my mind

If, six months out, Elad reports that video requests still land in the wrong place, the next
lever is **not** more `CLAUDE.md` text. It is a `UserPromptSubmit` hook that greps the prompt
for video words and injects one line only when it matches. That is free on the 98% of prompts
that are not about video, where `CLAUDE.md` text is not. I am not proposing it now because it
hides routing logic in a shell script, it will misfire on Hebrew keyword matches, and layer 1
should be given a fair trial first. **The evidence that would trigger it:** two or more video
requests in a month that reach a non-`video-director` path.

**And one thing I could not determine:** whether `~/.claude/CLAUDE.md` content is authoritative
over a skill's `description` when the two conflict in the model's judgment. The Claude Code docs
do not state a precedence between them. This is precisely why I have put the enforcement in
`settings.json`, which is a deterministic filter rather than a persuasion contest. But it means
line 1 above is a *backstop of unverified strength*, not a guarantee. **The evidence that would
settle it:** with `skillOverrides` temporarily removed, ask for a video and see whether the
`CLAUDE.md` line alone beats `hyperframes`'s description. I would not run that test; I would just
keep the deterministic filter.

---

# 6. The procedure

**Confidence: high on job (a); it mirrors an existing, approved vault workflow. High on job (b);
it follows `paper-edit`'s own documented stages.**

The gates exist for one reason: **every gate sits immediately before the step that gets
expensive.** A gate that does not have an expensive step behind it is ceremony and should be
removed.

## (a) A script becomes a finished 9:16 Hebrew explainer

Source of truth for the human-facing version stays in the vault:
`ICF/תכנים/וורקפלואו — הפקת סרטון (ידני-מהיר).md`.

| # | Step | Command | Gate |
|---|---|---|---|
| 0 | Scaffold | `~/DEV/video/bin/new-job.sh <slug> build` | |
| 1 | Claude writes the script into Obsidian from `_TEMPLATE — סקריפט סרטון.md`: per scene, screen-title + VO + image + effect. **Hebrew, Opus, new tab.** | | **GATE 1: Elad edits and approves the script** |
| 2 | Convert to `jobs/<job>/script.json` (cue array) + write b-roll prompts | | |
| 3 | Images: generate, or Elad supplies, or a mix | `engine/bin/genimg.py` / `broll.sh` → `assets/` | **GATE 2: approve images** |
| 3b | *(optional)* mark 2–3 HERO stills for real motion | `engine/bin/img2video.py <job>` | folded into gate 3 |
| 4 | VO + timing | `engine/bin/tts.py <job>` → `assets/master.mp3`, `built.json` | **GATE 3: listen to the VO** |
| 5 | Sketch: 540×960, `ultrafast`, first 3 cues. **Seconds.** | `engine/bin/make-ff.sh jobs/<job> --sketch` | **GATE 4: approve the sketch** |
| 6 | Full render: native 1080×1920, 1–3 min | `engine/bin/make-ff.sh jobs/<job>` | **GATE 5: approve v1**; feedback re-runs step 6 only |
| 7 | Handoff | `~/DEV/video/bin/to-fcp.sh <job>` → `fcp-kit/` | |
| 8 | Finish in Final Cut → export → `~/Movies/READY/Finance/` | | |

**Why each gate exists:**

- **Gate 1 (script).** The words are the product. Everything downstream is derived from them, and
  a wording change is nearly free here and costs a re-render and a re-VO anywhere later. It is
  also the only Hebrew-judgment step, so it is the one place a human must be in the loop
  regardless of cost.
- **Gate 2 (images).** The two visible failures in this format are a cropped head and stock-photo
  clichés. Both are image failures, both are obvious in a thumbnail, and both are invisible in
  a script. Catching them costs seconds; catching them after the VO costs a full rebuild.
- **Gate 3 (VO).** `eleven_v3` mispronounces Hebrew names and financial terms. A mispronounced
  word survives every subsequent step and lands in the published video. Thirty seconds of
  listening prevents it, and there is no automated check that can.
- **Gate 4 (sketch).** The reason `video-director` exists. Two renders on this machine failed at
  30–40 minutes and deleted their own frames. The sketch is the *same engine* run smaller, so it
  is a true preview, not an approximation. **Never skipped, not even when Elad is confident.**
- **Gate 5 (v1).** Feedback rounds must be cheap and bounded: they re-run step 6 only, because
  script/images/VO are already frozen by gates 1–3.

**Model routing:** the script, the caption text and any Hebrew judgment run on **Opus**, on
Claude, never elsewhere. Steps 2, 4, 5, 6 are mechanical and belong in the `icf-video-producer`
agent. No part of this touches a China-hosted model. Note also that the script *is* Elad's
business thinking, so it would be forbidden even if quality were equal.

## (b) Recorded footage becomes a rough cut ready for Final Cut

| # | Step | Command | Gate |
|---|---|---|---|
| 0 | Scaffold + **symlink** the source from `~/Movies/00 - Edit video/…` into `jobs/<job>/source/`: never copy, never move | `~/DEV/video/bin/new-job.sh <slug> cut` | |
| 0b | **Precondition:** PC reachable over Tailscale. If not, say so and stop. | `ssh pc "echo ok"` | hard stop, not a fallback |
| 1 | Transcribe locally. ~40 min per hour of footage, background it. | `paper-edit/scripts/transcribe_local.py` → `paper-edit/transcript.json` | |
| 2 | Claude cleans the transcript: mishearings, punctuation, sentence boundaries. **Timings never touched.** Anything uncertain is left alone and listed with its timecode. | `corrections.json` → `apply_corrections.py` → `clean.json` | **GATE 1: Elad reviews the uncertain list** |
| 3 | Build the review page; Elad strikes through what goes | `make_proxy.py` + `build_review.py` → `review.html` | **GATE 2: Elad exports `cuts.json`** |
| 4 | Snap every boundary to the nearest quiet point (±10 frames) and grade it | `snap_cuts.py --search-frames 10` → `cuts.snapped.json` | **GATE 3: Elad rules on every `LOUD` boundary** |
| 5 | Render from the **original**, ~12 ms fade at every join. `prores` if it goes to a grade, `high` otherwise. Emit `rough-cut.srt` in the same pass. | `render_cut.py --quality high --fcpxml` | |
| 6 | Handoff | `~/DEV/video/bin/to-fcp.sh <job>` → `fcp-kit/` → import into the right `.fcpbundle` | |

**Why each gate exists:**

- **Step 0b is a hard stop, not a gate, and that is the point.** If the PC is down the correct
  behaviour is to say so and wait, not to silently fall back to a cloud transcriber. For Hebrew,
  a cloud fallback is both a quality downgrade and, for client or unpublished material, a data
  boundary crossed without asking. The global "never block if a machine is down" preference does
  not apply to a step whose only alternative is worse output.
- **Gate 1 (corrections).** A "corrected" mishearing that was actually right silently changes
  what Elad said on camera. `paper-edit` already instructs Claude to flag its uncertainties with
  timecodes; the gate is Elad reading that short list, not the whole transcript.
- **Gate 2 (the strike-through).** This is not a checkpoint, it is *the human edit*. The entire
  skill exists to move the editorial decision onto text where it is fast, and then get out of
  the way. Claude must stop completely and wait.
- **Gate 3 (LOUD boundaries).** The single most valuable automated finding in the stack: a
  boundary the machine can **detect** but cannot **fix**. A `LOUD` cut is an audible click that
  survives into the finished piece. Every one gets reported with its timecode and Elad decides: accept it,
  or move the cut. Silently rendering over them would waste the analysis entirely.

**Model routing:** transcript cleanup is Hebrew judgment → **Opus**, on Claude. `paper-edit-engine`
already declares `model: opus` and "never routes Hebrew to a cheaper model." Everything else is
shell.

## What both procedures share

`JOB.md` in every job folder carries the gate checklist, and each gate is timestamped as it
passes. That single file is what makes a job resumable by a different session, a different agent,
or Elad three weeks later, and it is what `paper-edit`'s existing "Resuming" section is already
doing informally by inspecting which artefacts exist.

---

# 7. Migration

**Confidence: high on the ordering and on the single irreversible item.**

The plan is deliberately shaped so that **the highest-value step is also the lowest-risk step and
comes first.** Steps 1 and 2 deliver the entire routing and surface-area fix (the part paid on every
request forever) and neither one moves a single byte of video.

### Step 0: preconditions (no changes)

```
cp ~/.claude/settings.json ~/.claude/emergency/config-backup/settings.json.pre-video-$(date +%F)
python3 ~/.claude/scripts/claude-cleanup.py health
df -h ~            # need >3 GB free for step 3. Currently 69 GB. OK.
ssh pc "echo ok"   # PC was unreachable during the inventory scan and during this review
```

Record which of the 22 override targets exist today, so step 1 does not key a name that has
already changed.

---

### Step 1: `skillOverrides` · **the whole of §1 and §2**

Add the 22-key block to `~/.claude/settings.json`. Nothing else.

- **Reversible:** yes, completely. Delete the key, or restore the step-0 backup.
- **Irreversible:** nothing.
- **Risk:** low. No file is created, moved or deleted.
- **Must be true before step 2:** run three real requests and observe which skill fires.
  *"תעשה סרטון מהסקריפט הזה"* → `video-director`; *"תעשה rough cut לקובץ הזה"* → `paper-edit`;
  *"תמלל את הוובינר"* → `media-pipeline`. And confirm `hyperframes` fires on none of them.
- **Rollback if it goes wrong:** restore the backup file. One command.

This is where I would stop and let a week pass before doing anything else. If the routing is
right, most of the daily pain is already gone, and every remaining step is optional
housekeeping.

---

### Step 2: the three `CLAUDE.md` lines + rewrite `video-director`

Add the `# Video` block from §5. Rewrite `video-director/SKILL.md` to add `paper-edit`,
`media-pipeline` and the production rules to its decision tree, and create
`references/production-rules.md` by harvesting `video-use`'s hard rules. **Do not yet change any
path**: `~/DEV/video/` does not exist yet. Paths change in step 4.

- **Reversible:** yes. Backup `CLAUDE.md` to `~/.claude/emergency/config-backup/` first, per the
  Guardian rule; snapshot the skill file.
- **Risk:** low.
- **Must be true before step 3:** a video request routes correctly *and* the rewritten decision
  tree sends a "rough cut" request to `paper-edit`.

---

### Step 3: create `~/DEV/video/` and **copy** the engine

`mkdir`, `git init`, `PROJECT-BRIEF.md`, `CLAUDE.md`, `README.md`, `bin/*.sh`, `router-allowlist.txt`,
then `cp -a ~/DEV/ICF/content/insurance-video-v1/pipeline/ ~/DEV/video/engine/`.

**Copy, not move.** `~/DEV/ICF` is not a git repo, so there is no history and no `git mv`. The
original stays exactly where it is and keeps working the whole time.

- **Must be true before step 4:** a known-good job re-renders **from the new location** with
  byte-identical or visually identical output. Use `insurance-ff-sk`: it is already a sketch
  project, so the verification takes seconds. The shell-level relocation safety is already
  verified (`PIPE` derives from `$(dirname $0)/..`), but verify the render anyway.
- **Reversible:** delete `~/DEV/video/engine/`. Nothing else has changed.
- **Risk:** low. 2.5 GB against 69 GB free.
- **`.gitignore` before the first commit:** `engine/projects/`, `jobs/*/renders/`, `jobs/*/assets/`,
  `jobs/*/source/`, `archive/`, `*.mp4`, `*.mov`, `*.mp3`, `*.png`. The repo tracks the engine and
  the job *documents*, never the media. The global `~/.gitignore_global` already blocks media, but
  make it explicit here.

---

### Step 4: repoint every reference, in one commit

`video-director/SKILL.md` (step 4) · `video-director/references/engines.md` (3 refs) ·
`icf-video/SKILL.md` (line 9 + the whole engine section) · `~/.claude/agents/icf-video-producer.md` ·
`engine/README.md` (**rewrite**: it currently documents only the slow path and omits six of the
ten scripts) · vault `SOP — מטקסט לסרטון (מערכת ההפקה).md` · vault
`וורקפלואו — הפקת סרטון (ידני-מהיר).md`.

- **Must be true before step 5:** a fresh session, given "בנה סרטון מהסקריפט", reaches
  `~/DEV/video/engine/bin/make-ff.sh` and not the old path.
- **Reversible:** `git revert` in `~/DEV/video`, plus the Guardian snapshots for the two skill
  files and the agent. Vault notes are in iCloud version history.
- **Risk:** medium. This is the step where a missed reference produces a confusing half-migrated
  state. `grep -rl "insurance-video-v1" ~/.claude ~/DEV/video "$VAULT"` must return zero hits
  before this step is called done.
- **Do NOT delete or move the original `pipeline/` here.** Leave it in place for a 30-day soak.

---

### Step 5: move the 9 projects into `jobs/`

Rename with date prefixes. `night` and `insurance-sketch` go to `archive/` instead; they are
experiments, not jobs.

- **Must be true before step 6:** one moved project re-renders from its new path.
- **Reversible:** move back; each project is self-contained.
- **Risk:** low.

---

### Step 6: retire the transcription daemon · **ASK FIRST**

```
launchctl unload ~/Library/LaunchAgents/com.eladtzur.auto-transcribe.plist
mv ~/Library/LaunchAgents/com.eladtzur.auto-transcribe.plist ~/Library/LaunchAgents/disabled/
```

`disabled/` already exists with 8 plists. This is Elad's own established pattern, not a new one.
`~/DEV/auto-transcribe/transcripts/` and `done/` stay untouched.

- **Ask first because** it is running right now (PID 759) and Elad may be actively using the
  drop folder.
- **Reversible:** move the plist back and `launchctl load`. Fully.
- **Also decide here:** `com.eladtzur.video-weekly` (Mondays 09:00, drives the `video-with-claude`
  KB refresh). It is a scheduled job, not a watcher, so it sits on the edge of the
  no-resident-listeners rule rather than clearly violating it. **My recommendation: keep it**,
  but note it in the brief so it is a known, chosen listener rather than a forgotten one.

---

### Step 7: the `embedded-captions` Hebrew test

One 30-second Hebrew talking-head clip, `anchor` identity, look at one frame. Promote to
`name-only` if the RTL is correct; leave `off` permanently if not. ~10 minutes. Independent of
everything else.

---

### Step 8: archive the leftovers · **ASK FIRST, each one separately**

| Move | Size |
|---|---|
| `~/DEV/ICF/content/insurance-video-v1/*.mp4` + `assets/` + `broll/` + `poster.jpg` → `~/DEV/video/archive/2026-07-insurance-v1/` | ~275 MB |
| `~/DEV/hyperframes-lab/` → `~/DEV/video/archive/hyperframes-lab-2026-05/` | small |
| *(after the 30-day soak)* `~/DEV/ICF/content/insurance-video-v1/pipeline/` → `~/DEV/video/archive/pipeline-old-2026-07/` | 2.5 GB |

Nothing goes to `~/.Trash/` in this plan. Everything goes to `archive/`.

---

### Step 9: the knowledge bases

Keep both; give each a job. `video-production/` = the human wiki (playbooks, paradigms, Elad's
stack). `video-with-claude/` = the tool radar (weekly, model prices, what exists now). Two
corrections:

- `video-production/INDEX.md` "Powers" advertises *"A **planned** `/video-faceless` skill (the
  daily machine)"*. That skill does not exist and never will under that name. Repoint it at
  `video-director` + `engine/bin/make-ff.sh`, which **is** the daily machine and already works.
- `video-with-claude/README.md` §2 calls HyperFrames the default. Correct it to FFmpeg-direct,
  and label the fal.ai "one-key principle" as a recommendation-not-yet-adopted unless the key
  check in §4 comes back positive.

---

## Irreversible: flagged explicitly

1. **`~/Movies/`, anything at all.** Final Cut libraries store absolute paths to external media.
   Moving one source file breaks the link, and the repair is manual, per clip, across five live
   libraries. There is no undo. Compounding it: free disk is 69 GB against a 461 GB tree, so
   copy-then-verify is not even physically available. **This plan touches `~/Movies` exactly
   once, in read-only symlinks from `jobs/*/source/`, and never otherwise.**
2. **Deleting the original `pipeline/` after step 4.** `~/DEV/ICF` has no git history, so a
   deletion is unrecoverable outside Time Machine. Hence: 30-day soak, then archive, never
   delete.
3. **`~/DEV/video-tools/move_log.csv` and `snapshots/`.** These are the undo ledger for a past
   111 GB reorganize of `~/Movies`. Moving that folder, or running its scripts with different
   relative paths, could sever a rollback path for media moves already made. It is left in place
   for exactly this reason.

## Not irreversible, but worth naming

**`npx hyperframes init` re-installs the full skill set to disk**: the bundle's own SKILL.md
says every creation workflow scaffolds with `init`, and that `--skip-skills` is currently
neutered. That will **not** resurrect the overrides, because `skillOverrides` is keyed by name in
`settings.json` and files on disk cannot change it. But a future bundle version shipping a skill
under a **new name** will arrive `on`. That is the one hole in layer 1, and it is exactly what
`bin/video-router-check.sh` (§1 layer 3) exists to catch.

---

# Confidence, and what I could not determine

| Section | Confidence | Basis |
|---|---|---|
| 1 Routing | **High** | `skillOverrides` verified in the installed changelog (shipped 2.1.131; this machine runs 2.1.178). Verified `render.sh` uses the npm package, not the skill, so the override cannot break the renderer. |
| 2 Surface area | **High** on keeps and offs; **medium** on `embedded-captions` and `video-use` | Read all 22 frontmatter descriptions directly, plus the full text of the 4 skills that matter. Both medium calls have a named one-shot test attached. |
| 3 The folder | **High** | Verified the engine scripts derive their own root from `$(dirname $0)/..` and accept absolute project paths, which is what makes the move safe. Verified `~/DEV/ICF` is not a git repo, `~/DEV/video` is free as a name, and disk headroom is adequate. |
| 4 Duplication | **High** on transcription/TTS/image-to-video and on the caption split; **medium** on `media-pipeline` | The `media-pipeline` transcriber is the one implementation I did not read. |
| 5 Global file | **High** on the boundary and the three lines; **medium** on the strength of line 1 as a backstop | The 20,400-token listing measurement is mine and reproducible. The CLAUDE.md-vs-description precedence is undocumented, which is why enforcement sits in `settings.json` instead. |
| 6 The procedure | **High** | Both procedures follow documents that already exist and already work. |
| 7 Migration | **High** | Ordering derives from the reversibility of each step, which I checked individually. |

### Could not determine

1. **Whether the skill listing is truncating right now.** I measured 173 skills ≈ 20,400 tokens
   against a ~1%-of-context budget and concluded it is roughly 2× over on a 1M model. I did not
   observe an actual truncation. **Evidence that settles it:** run `/context` in a fresh session
   and check whether the skill listing reports as truncated. This matters because it is the
   strongest single argument for §2, and it is the justification for line 1 of §5.
2. **Whether `~/.claude/CLAUDE.md` outranks a skill `description:` in a conflict.** Undocumented.
   Directly relevant to how much weight line 1 of §5 can bear.
3. **Whether `media-pipeline` uses the same Hebrew model as `paper-edit`.** Determines whether
   §4 has one canonical transcriber or two. **Evidence:** diff the model string against
   `ivrit-ai/whisper-large-v3-ct2`.
4. **Whether `embedded-captions` renders Hebrew RTL correctly.** Determines whether the stack has
   a subject-occluding caption engine or not. **Evidence:** one 30-second test clip, one frame.
5. **Whether a `fal.ai` key exists.** Determines whether the `video-with-claude` KB's central
   recommendation is adopted policy or an aspiration mislabelled as a decision.
   **Evidence:** `grep -ci 'fal\.ai\|fal_key' ~/DEV/shared/API-KEYS-REGISTRY.md`, which returns a count, not a value.
6. **PC / Ollama availability.** Unreachable during the inventory scan and unverified by me.
   `paper-edit` and `media-pipeline` both hard-depend on it for Hebrew transcription. If the PC
   is durably unavailable, job (b) has no correct path at all and that becomes the highest
   priority in the whole stack, above everything in this document.
7. **Whether any of the 12 HyperFrames workflow skills has ever produced an artifact Elad kept.**
   I found exactly one HyperFrames output on disk (`hyperframes-lab/test-promo/renders/`, dated
   2026-05-06) plus the pipeline's own `make.sh` renders, which use the **npm renderer** rather
   than the workflow skills. I am confident enough to recommend `off` for all 12, and turning
   them off is a one-line revert. But if Elad says one of them produced something he kept, that
   one comes back to `name-only` and I would want to know which.

---

## One-page summary of every change

| # | Change | Files touched | Reversible |
|---|---|---|---|
| 1 | 22 `skillOverrides` keys → `off` | `~/.claude/settings.json` | one edit |
| 2 | 3 lines under a `# Video` heading | `~/.claude/CLAUDE.md` | one edit |
| 3 | Rewrite the decision tree; add `production-rules.md` | `video-director/` | snapshot |
| 4 | Make `make-ff.sh` the documented flow | `icf-video/SKILL.md` | snapshot |
| 5 | Reduce to a wrapper; fix `skill.md` → `SKILL.md` | `transcribe/` | snapshot |
| 6 | New working root | `~/DEV/video/` (new, git) | delete |
| 7 | Copy the engine, then archive the original after 30 days | `insurance-video-v1/pipeline/` → `~/DEV/video/engine/` | copy first |
| 8 | 9 projects → dated job folders | → `~/DEV/video/jobs/` | move back |
| 9 | Unload the transcription daemon | plist → `LaunchAgents/disabled/` | reload |
| 10 | Archive `hyperframes-lab`, the 8 loose MP4s | → `~/DEV/video/archive/` | move back |
| 11 | Fix the phantom `/video-faceless` and the "HyperFrames is default" line | 2 KB files | git |
| | **Left untouched on purpose** | `~/Movies/` · `~/DEV/video-tools/` · `~/DEV/video-use/` · all 3 agents · all 205 skill directories on disk | |

**Files deleted: zero. Steps that reach into `~/Movies`: zero.**
