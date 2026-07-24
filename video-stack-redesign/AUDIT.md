# AUDIT: Video Stack Adjudicated Plan

Adversarial pre-execution audit of `DECISION.md`. Nothing was changed on this machine.
Read-only verification only. Date: 2026-07-24.

Method: the plan was reviewed by five dimension-scoped reviewers and then adjudicated.
This audit hunts the class those reviewers structurally cannot see: **what executing step N
does to step N-1, to a rollback path, or to something live and unrelated.**

Every finding is marked **CONFIRMED** (verified here, with the command or file:line) or
**UNVERIFIED** (looks wrong, could not be proven).

---

## The single most dangerous thing this plan misses

Step 1 is described as "one edit, reversible by deleting one block," and the whole first week
of value rests on it. Two things are wrong with that framing at once. First, the file it edits,
`~/.claude/settings.json` (19,344 bytes), is not a video config file: it is the live carrier of
the machine's **only** secret-leak prevention hook (`block-secrets-in-tool-args.sh`), 338
permission allow rules, 13 deny rules including `Bash(rm *)` and `Bash(sudo *)`, and
`defaultMode: acceptEdits`. A malformed edit takes all of that out simultaneously and silently,
leaving auto-accept on with no deny list and no secret hook. Second, `skillOverrides` is
**not documented as a supported key in `~/.claude/settings.json` at all**: the official settings
reference does not list it, and the only place Anthropic documents where it is written is the
skills page, which says the `/skills` menu saves it to `.claude/settings.local.json`. User scope
is also the **lowest-precedence** layer. So step 1 may be a silent no-op that nobody notices,
written into the one file whose corruption would be catastrophic, with no post-edit verification
step defined and no settings.json backup ever taken on this machine.

---

## Section 1. Plan steps that are actively WRONG or DANGEROUS

### W1. Step 1 turns off skills that three live, non-video business systems call by name
**CONFIRMED. Severity: critical.**

The 22-key off-list (`PROPOSAL-claude.md:151-177`) is treated as purely a video-routing change.
It is not. Three documents outside the video domain route to those exact names:

| File | Line | What it routes |
|---|---|---|
| `/Users/eladtzur/.claude/agents/content-deriver.md` | 26 | `deck` derivative to `hebrew-keynote-builder` **or `slideshow`** |
| same | 27 | `shorts` derivative to `hyperframes` / `faceless-explainer` / `motion-graphics` |
| same | 28 | `explainer-video` / `long-video` to `faceless-explainer` / `general-video` / `hyperframes` ("entry: read `hyperframes` skill first") |
| `/Users/eladtzur/.claude/skills/cco/CONTENT-MAP.md` | 38, 41, 42, 43 | the entire video and deck rows of the CCO format map, all 20 bundle names plus `video-use` and `higgsfield` |
| `/Users/eladtzur/.claude/skills/advertising/SKILL.md` | 10, 12, 281, 427, 447, 526 | ad-campaign creative generation: "Call `higgsfield` for video ads (image-to-video, cinematic motion)" |

The plan's only mitigation is in Q2: *"the rewritten `video-director` must name each `off` skill
and its path."* That covers **one** of the four documents. After step 1, `content-deriver`,
`cco/CONTENT-MAP.md` and `advertising` all point at names the model can no longer see, with
no path fallback, in a business system (the CCO content pipeline and the Meta ads workflow)
that has nothing to do with the video router collision this plan exists to fix.

`higgsfield` deserves separate mention: it is **not** part of the HyperFrames bundle, it was never
a router competitor for the owner's job types, it is not reinstalled by anything, and it is the
`advertising` skill's designated image-to-video engine. Turning it off is pure capability loss
with zero routing benefit.

**Fix.** Before step 1: enumerate every consumer of the 22 names outside
`~/.claude/skills/hyperframes*` and the bundle's own internal cross-references. Patch
`content-deriver.md`, `cco/CONTENT-MAP.md` and `advertising/SKILL.md` **in the same change as
step 1**, converting each name reference to a name-plus-path reference exactly as the plan
requires of `video-director`. Remove `higgsfield` from the off-list, or downgrade it to
`user-invocable-only` so `/higgsfield` still works while it stops competing in the listing.

---

### W2. Step 1's blast radius and rollback are both mis-stated
**CONFIRMED. Severity: critical.**

`~/.claude/settings.json` currently holds (verified by parsing the file):

```
UserPromptSubmit  -> session_log.py open
SessionEnd        -> session_log.py close
PreToolUse [Edit|Write|MultiEdit|NotebookEdit|Bash]
                  -> /Users/eladtzur/.claude/hooks/block-secrets-in-tool-args.sh
SessionStart      -> gsd-check-update.js, session-start-tracker.sh,
                     recent-activity-markers.py, dashboard-refresh.py
PostToolUse       -> gsd-context-monitor.js, stamp-authorship.py
Stop              -> session-stop-tracker.sh, stop-notification.sh
permissions.allow                 338 rules
permissions.deny                   13 rules
permissions.defaultMode           acceptEdits
permissions.additionalDirectories  24 entries
```

`permissions.deny` = `Bash(rm *)`, `Bash(rm)`, `Bash(rmdir *)`, `Bash(git push --force*)`,
`Bash(git push -f*)`, `Bash(git reset --hard*)`, `Bash(git clean*)`, `Bash(sudo *)`, `Bash(sudo)`,
`Bash(curl *| sh*)`, `Bash(curl *| bash*)`, `Bash(wget *| sh*)`, `Bash(wget *| bash*)`.

`~/.claude/CLAUDE.md` describes the secret hook as "now technically enforced" after the pattern
recurred "dozens of times." It lives in this file. So does the `rm` deny rule, next to
`defaultMode: acceptEdits`.

Also verified: `/Users/eladtzur/.claude/emergency/config-backup/` contains 20 files and **not one
of them is a settings.json backup**. It holds `CLAUDE.md.*` and `hooks.json.*` only. The Guardian
`auto-snapshot.sh` hook fires on Write/Edit, but it is registered in the legacy
`~/.claude/hooks.json`, not in the live `settings.json` hooks block, so its coverage of this
specific edit is **UNVERIFIED**.

**Fix.** Step 0 must be expanded from "back up settings.json" into a gate with three parts:
1. `cp ~/.claude/settings.json ~/.claude/emergency/config-backup/settings.json.$(date +%Y%m%d-%H%M%S)`
2. After the edit, `python3 -c "import json;json.load(open('...settings.json'))"` must exit 0.
3. **In a new session, prove the file still loads as configuration, not just as JSON.** Confirm
   the secret hook still blocks a planted placeholder-secret edit attempt, and confirm a denied
   command is still denied. Checking this in the same session that made the edit proves nothing:
   the settings were already loaded before the edit.

---

### W3. `skillOverrides` in `~/.claude/settings.json` may be a silent no-op
**UNVERIFIED, and it is the entire first week of value. Severity: critical.**

What is confirmed:
- The feature exists on this version. `~/.claude/cache/changelog.md:1200` = `## 2.1.129`, and
  `:1209` = the `skillOverrides` entry. `claude --version` = **2.1.178**. So 2.1.178 > 2.1.129.
- Plugin skills are exempt from `skillOverrides`, and none of the 22 are plugin skills
  (`~/.claude/plugins/` holds only marketplace metadata, no installed plugins). So the exemption
  does not bite.

What is **not** confirmed, and what the plan asserts without checking:
- The official settings reference (`code.claude.com/docs/en/settings`) does **not list
  `skillOverrides` in its settings table at all.** The only Anthropic documentation of where the
  key is written is the skills page: *"The `/skills` menu writes it for you ... then `Enter` to
  save to `.claude/settings.local.json`."* That is a **project-scoped local** file, not
  `~/.claude/settings.json`.
- Settings precedence is Managed > CLI args > `.claude/settings.local.json` > `.claude/settings.json`
  > `~/.claude/settings.json` (**lowest**). The plan writes to the weakest layer.
- Merge semantics for an object-valued key across scopes are unknown. If a project-level
  `skillOverrides` ever **replaces** rather than merges, all 22 keys vanish in that project with
  no error.
- Separately: the docs state `"off"` only began hiding skills from **Agent SDK and Remote Control
  callers as of v2.1.199**. This machine is 2.1.178, 21 versions short. Subagents dispatched
  through the SDK may still be advertised the off skills. The plan claims a clean 25 to 6 cut;
  on this version that is true for the terminal and the model's own listing, not necessarily for
  SDK-spawned agents.

**Fix, and it costs one minute.** Do not hand-write the block. Open `/skills`, highlight one
skill, press `Space` until it reads `off`, press `Enter`. Then look at which file Claude Code
actually wrote to and what shape it wrote. Put the 22-key block **there**. Confirm in a fresh
session that the skill is gone from `/`. Only then proceed. This single check removes the largest
silent-failure risk in the plan and validates the mechanism before 21 more keys ride on it.

---

### W4. Step 4 is not executable as written: not 7 references, and not one commit
**CONFIRMED. Severity: high.**

Actual references to `~/DEV/ICF/content/insurance-video-v1` outside that tree: **15 files across
three unversioned locations.**

Skills (`~/.claude/skills/`, not a git repo):
- `video-director/SKILL.md:79`
- `video-director/references/engines.md:3`
- `icf-video/SKILL.md:9`
- `icf-fcpx/SKILL.md:26` (`cd ~/DEV/ICF/content/insurance-video-v1/pipeline`)
- `image-expand/SKILL.md:50, 89, 90, 92` (`:92` invokes `pipeline/bin/make-ff.sh`)

Claude project memory (`~/.claude/projects/-Users-eladtzur-DEV-ICF/memory/`, not a git repo):
- `icf-video-pipeline.md:10`
- `no-period-in-captions.md:14` (points at `pipeline/lib/build.js`, a caption rule that "applies
  to ALL videos")

Vault (separate repo, iCloud-synced), 8 notes:
- `04 - ספריה/ספריה — מפת ידע.md`
- `00 - דשבורד/Dashboard Lists.md`
- `02 - פרוייקטים/פעילים/Video Editing/עריכת וידאו — מפה ותכנון אוטומציה.md`
- `02 - פרוייקטים/פעילים/ICF/תכנים/SOP — מטקסט לסרטון (מערכת ההפקה).md`
- `02 - פרוייקטים/פעילים/ICF/תכנים/ביטוחים/סקריפט — סרטון ביטוח (תמונות+קול) — מנוע FFmpeg.md`
- `02 - פרוייקטים/פעילים/ICF/תכנים/_TEMPLATE — סקריפט סרטון.md`
- `02 - פרוייקטים/פעילים/ICF/סשן 2026-07-01 — מערכת טקסט-לסרטון.md`
- `02 - פרוייקטים/פעילים/ICF/תכנים/ביטוחים/סדרת פרסום ממומן — ביטוח (faceless).md`

`~/.claude/.git` does not exist. `~/DEV/ICF/.git` does not exist. The vault is a different repo.
**"In one commit" is impossible**, and with it goes step 4's stated reversibility: there is no
single revert.

**Fix.** Split step 4 into 4a (skills + project memory, no VCS, so take a timestamped copy of the
8 files first) and 4b (vault, one vault commit). Raise the count to 15. Add the two skills the
inventory missed (see W5). Gate 4b: the vault notes are Hebrew SOPs the owner reads, so a blind
`sed` across them is not appropriate.

---

### W5. The inventory undercounts the video surface, and two of the missed skills drive the engine
**CONFIRMED. Severity: high.**

`INVENTORY.md` §1 enumerates 25 video skills. Two more exist and appear nowhere in the inventory,
nowhere in the 22 off-keys, and nowhere in the "6 visible" target:

- **`icf-fcpx`** (`~/.claude/skills/icf-fcpx/SKILL.md`, 4,577 bytes, installed 2026-07-03).
  Description triggers include `'final cut'`, `'fcpx'`, `'פיינל קאט'`, `'קובץ לעריכה'`,
  `'תוציא לעריכה'`, `'שכבות לעריכה'`. This is a **fourth** competitor for Hebrew video routing,
  and it is the Final Cut handoff path the plan's Q6 procedure depends on.
- **`image-expand`** (`~/.claude/skills/image-expand/SKILL.md`) drives the engine directly:
  line 92 runs `bash ~/DEV/ICF/content/insurance-video-v1/pipeline/bin/make-ff.sh <project-dir>`.

Worse: `icf-fcpx/make_fcpx.py` is **14,310 bytes**, while `pipeline/bin/make_fcpx.py` is
**15,123 bytes**. Two diverged copies of the same script. The plan's Q4 counts three Final Cut
handoff implementations. There are four, two of which are copies of one file that have drifted
apart, and nobody knows which produced the last good handoff.

**Fix.** Re-derive the video skill census from disk rather than from the inventory. Add `icf-fcpx`
and `image-expand` to the step 4 repoint list. Decide `icf-fcpx`'s state explicitly (it is a
genuine router competitor, so leaving it `on` while turning 22 others off partly re-creates the
problem the plan is solving). Diff the two `make_fcpx.py` copies and pick a canonical one before
step 3 copies the engine, or the move will fossilize the divergence.

---

### W6. Ordering: step 5 operates on something step 3 already archived, and step 3's verification is under-specified
**CONFIRMED (contradiction), UNVERIFIED (intent). Severity: high.**

Step 3: "Create `~/DEV/video/`, **copy** the engine, verify a render, only then archive the original."
Step 5: "Move the 9 pipeline projects into `jobs/` with date prefixes."

The 9 projects live at `pipeline/projects/`. Either step 3's "the engine" includes `projects/`
(in which case step 5 is moving folders out of an archive two steps later), or it does not
(in which case step 3 archives the original **with the 9 projects inside it** and the plan never
says where they went). Either reading is a defect. The plan does not define what "the engine" is
at the directory level.

Second problem in the same step: **"verify a render" names no engine.** The pipeline has two,
with disjoint dependency sets:
- FFmpeg-direct (`bin/make-ff.sh` -> `bin/tts.py` -> `bin/ffrender.py`), needs
  `~/.claude/secrets/elevenlabs.env` and local ffmpeg. This is the path the plan's own Q1 analysis
  calls primary and fastest.
- HyperFrames (`bin/make.sh` -> `lib/build.js` -> `bin/render.sh` -> `npx --yes hyperframes render`),
  needs Node >= 22 and network access (npm registry, Google Fonts, telemetry).

Verifying one proves nothing about the other. Given the plan's whole thesis is that FFmpeg-direct
is the correct default, verifying only the HyperFrames path would be verification in the wrong
world.

Third: **the plan misidentifies its own point of no return.** It gates steps 1, 3, 6 and 8 with
ASK, and leaves steps 4 and 5 ungated. But step 4 (repoint every pointer to the new location,
no VCS, no single revert) and step 3's final sub-action (archive the original) together form the
real irreversibility. After both, every document names a location whose contents were never
independently proven, and the original is in an archive with no commit to revert.

**Fix.** Re-sequence:
```
3a  create ~/DEV/video/, cp -a the engine (define: bin/ lib/ config.json EFFECTS.md
    gallery-assets/, and state explicitly whether projects/ comes along)
3b  verify BOTH engines from the NEW location, each producing a real output file,
    with the ORIGINAL renamed out of reach for the duration of the test
5   move the 9 projects into jobs/  (ASK: this moves files, per CLAUDE.md)
4   repoint all 15 references, split 4a skills+memory / 4b vault  (ASK for 4b)
3c  archive the original  <-- LAST. This is the true point of no return.
```

---

### W7. "Jobs reach into `~/Movies` by read-only symlink only" names a control that does not exist
**CONFIRMED. Severity: high, because it is the plan's one hard prohibition.**

macOS has no read-only symlink. A symlink carries no permissions of its own; every access
resolves to the target and inherits the target's permissions. `~/Movies` is owned by the user and
writable. Therefore anything writing to a path under a job's symlinked folder writes **into the
461 GB tree of live Final Cut libraries**, and the named mechanism prevents exactly nothing.

Operations that follow symlinks and would amplify a mistake into `~/Movies`:
`cp -RL`, `rsync -L` / `--copy-links`, `tar -h`, `du -L`, `find -L`, `ffmpeg -y` writing to a path
under the link, Python `shutil.copytree` (follows symlinks by **default**), and any glob that
expands through the link. Note that `~/.claude/settings.json` denies `Bash(rm *)` for Claude, but
that rule does not cover `shutil.rmtree`, `os.remove`, `mv`, or ffmpeg overwrite.

Two facts that raise the stakes:
- **`~/Movies` is being written by a third party right now.** `/Users/eladtzur/Movies/.mExtension/`
  is **root-owned, mode 0777**, last modified 2026-07-23 22:48, containing `.fcp`, `.haze`,
  `.hollow`, `.metadata`, `.shadow` (a MotionVFX plugin store). Two `.fcpbundle` libraries carry
  the same 22:50 timestamp. This is a live, actively-mutating tree.
- **There is no backup.** See W8.

Arithmetic confirmed: `du -sh ~/Movies` = **461G**. `df` on `/System/Volumes/Data`: 823 GiB used,
**60 GiB available**, 94% capacity. The plan says 64 GB free; it has dropped 4 GB since the scan.
6.5% free on the volume. Copy-then-verify inside `~/Movies` is arithmetically impossible, exactly
as the plan says.

**Fix.** State honestly that the prohibition is a **convention, not a control**, then add controls
that are real:
1. Symlink individual **files**, never a directory. A file symlink cannot be written *through*
   into a sibling.
2. Ban `-L` / `-h` / `--copy-links` / `follow_symlinks=True` in every script under `~/DEV/video/bin/`,
   and have `video-router-check.sh` assert their absence.
3. Every job script writes output to an **absolute** path under `jobs/<id>/renders/`, never a
   relative path that could resolve through a link.
4. If real enforcement is wanted, mount a read-only APFS snapshot of `~/Movies` and link into
   that instead. That is the only mechanism on this OS that makes "read-only" true.

---

### W8. There is no backup of anything this plan moves
**CONFIRMED. Severity: high.**

```
$ tmutil destinationinfo
tmutil: No destinations configured.
$ tmutil latestbackup
Failed to mount backup destination ... Code=17
```

`~/Movies` and `~/DEV` are both `[Included]` in Time Machine's scope, and Time Machine has no
destination, so neither is backed up. `~/DEV/ICF` is **not a git repository** (verified). The
engine is 2.5 GB (`pipeline/`) inside a 2.8 GB tree with no version history and no off-machine
copy. `~/.claude/` is not a git repository either.

Every "Reversible? Yes" in the plan's step table therefore reduces to: a second copy on the same
disk, on a volume that is 94% full, with no snapshot and no off-machine copy. That is not a
rollback, it is a hope.

**Fix.** Before step 3, either configure a Time Machine destination, or `git init` + first commit
inside `~/DEV/ICF/content/insurance-video-v1/pipeline/` (it is 2.5 GB, mostly `projects/` renders,
so gitignore `projects/*/renders/` and `*.log` and the commit stays small), or take one external
copy of the pipeline. This is a prerequisite, not a nicety. It also needs a human decision
(hardware / purchase).

---

## Section 2. New problems found, ranked by business impact

### N1. A third skill root exists, and the mirror mechanism that created it is destructive
**CONFIRMED. Severity: medium-high.**

`INVENTORY.md` §8b C1 states: *"There are TWO skill install roots, not one."* There are at least
**three**.

`/Users/eladtzur/.openclaw/skills/` holds **27 entries**, every one a symlink of the form
`<name> -> ../../.claude/skills/<name>`, all timestamped **2026-07-01 19:41**, the same minute as
the bundle install. This includes all 20 bundle skills plus `animejs`, `css-animations`, `gsap`,
`lottie`, `tailwind`, `three`, `waapi`.

Source, in the hyperframes npm package (`~/.npm/_npx/110f701c48e68d66/node_modules/hyperframes`,
version 0.7.69):

- `dist/cli.js:91672` `mirrorGlobalSkills()` walks `AGENT_GLOBAL_DIRS`, a table of **78 agent
  skill directories** (`cli.js:91554-91620`), and mirrors `~/.claude/skills` into every one whose
  parent directory already exists. Source and `~/.agents/skills` are skipped.
- `dist/cli.js:91655` `linkOrCopy()` runs
  **`rmSync(targetSkill, { recursive: true, force: true })`** before creating the symlink.
- Called from `mirrorToInstalledAgents()` (`cli.js:91869`), which runs at the end of every
  `installSkills()`.

Consequences the plan does not account for:
- `~/.codex/skills/` **now exists** (created 2026-07-20 by Codex itself, holding 5 `.system`
  skills). The next `npx hyperframes init` will create HyperFrames mirrors there too.
- `skillOverrides` in `~/.claude/settings.json` governs **Claude Code only**. It does not govern
  OpenClaw's skill root or Codex's. On those tools the router collision the plan exists to solve
  is untouched.
- Any future "clean up disk" pass on `~/.claude/skills/hyperframes*` leaves `~/.openclaw/skills/`
  full of dangling symlinks.

**Fix.** Correct §8b C1 to three roots. Add `~/.openclaw/skills/` and `~/.codex/skills/` to
`video-router-check.sh`'s scan. Decide explicitly whether OpenClaw should see the bundle at all;
if not, the mirror needs removing after every `init`, which is a durable-drift problem
`skillOverrides` cannot solve.

### N2. Step 1 is a Mac-only edit, but the plan's own engine doc sends heavy renders to Omac
**UNVERIFIED (Omac unreachable during this audit). Severity: medium-high.**

`INVENTORY.md` §2 quotes `video-director`: *"heavy HyperFrames renders run on **Omac**, not the
Mac."* Omac runs `claude -p` through the task daemon and therefore reads **its own**
`~/.claude/settings.json`, which nothing in this plan touches. Per `~/.claude/CLAUDE.md`, there is
deliberately no continuous cross-machine sync. So on the exact machine that runs the heavy
renders, all 22 skills stay `on` and the router collision persists in full.

**Fix.** Determine whether Omac carries the bundle. If it does, step 1 needs a second, explicitly
scheduled application on Omac, and the drift check needs to run there too. Add this to the plan as
a named step, not a footnote.

### N3. Step 9 collides with a running LaunchAgent the plan never mentions
**CONFIRMED. Severity: medium.**

`com.eladtzur.video-weekly` is **loaded** (`launchctl list`), `StartCalendarInterval` Weekday 1
Hour 9, running `/Users/eladtzur/.claude/scripts/video-weekly-update.sh`, which refreshes
`~/DEV/wiki/kb/video-with-claude/`. That is precisely one of the two KBs step 9 reconciles, and
step 9 carries **no gate**. Reconcile the KBs on a Sunday and Monday 09:00 overwrites the work.

The plan's "Findings neither reviewer was asked for" lists **one** resident listener. There are
two in the video domain, and **16 LaunchAgents are loaded overall** on a machine whose recorded
preference (`feedback_no-resident-listeners.md`) is to avoid them.

**Fix.** Add "unload `com.eladtzur.video-weekly` before step 9, decide its fate with the same ASK
gate as step 6" to the plan.

### N4. `npx --yes hyperframes` is unpinned and self-updating, so step 3's verification decays
**CONFIRMED. Severity: medium.**

`pipeline/bin/render.sh:6` and `:11` call `npx --yes hyperframes lint` and
`npx --yes hyperframes render` with **no version constraint**. Two versions are already cached on
disk: `0.7.26` and `0.7.69`. Additionally, every hyperframes command fires
`checkForUpdate()` and, on a hit, `scheduleBackgroundInstall()` (`dist/cli.js:195328-195335`):
the engine silently updates itself in the background.

The plan calls this engine "proven" and verifies it once, in step 3. That verification expires the
next time upstream publishes.

**Fix.** Pin it: `npx --yes hyperframes@0.7.69`. One-line change, makes the step 3 verification
mean something, and costs nothing.

### N5. `off` skills on 2.1.178 are still advertised to Agent SDK callers
**CONFIRMED via docs, behavior UNVERIFIED on this version. Severity: low-medium.**

The skills documentation: *"As of v2.1.199, `"off"` also hides the skill from the command lists
advertised to Remote Control clients and to Agent SDK callers, not only the terminal `/` menu."*
This machine is 2.1.178. The plan's "25 to 6 visible" is therefore true for the terminal and the
main model context, and possibly false for subagents dispatched through the SDK, which is how
`icf-video-producer`, `paper-edit-engine`, `media-pipeline-runner` and `content-deriver` run.

**Fix.** Either accept it and note it, or upgrade to >= 2.1.199 before step 1 and re-verify.

### N6. `~/DEV/video/` as designed violates four of the owner's own project rules
**CONFIRMED. Severity: low-medium, but it is a stated hard constraint.**

`~/.claude/CLAUDE.md` requires, for any new `~/DEV/` project:
- `PROJECT-BRIEF.md` ("Every DEV project carries a PROJECT-BRIEF.md")
- `git init`, `.gitignore`, `gh repo create peeym/<name> --private`
- an entry in `~/.claude/project-registry.json` ("single source of truth")
- and per `feedback_brief-infrastructure.md`, a Services & Infrastructure section listing every
  external tool (here: ElevenLabs, Replicate, HeyGen, fal.ai, the PC GPU over Tailscale, npm).

Step 3 creates the folder with none of these. Separately, CLAUDE.md states "Ask before deleting or
moving files"; **steps 4 and 5 both move/edit files and neither has an ASK gate**, and step 5
moves 9 project folders.

`~/DEV/video` does not currently exist (verified), so this is all greenfield and cheap to get
right at creation.

---

## Section 3. Verified clean. Do not re-litigate these.

1. **`skillOverrides` cannot be overwritten by the bundle. CONFIRMED, and strongly.**
   Grepped the entire installed `hyperframes@0.7.69` package (`dist/` + `bin/`, 22 MB) for
   `settings.json`, `settings.local.json`, `skillOverrides`: **zero matches.** The only `.claude`
   references in the whole CLI are `claudeHome` at `dist/cli.js:91639`
   (`env.CLAUDE_CONFIG_DIR || ~/.claude`), used solely to locate the *skills* directory at
   `:91676`. `init` and `skills update` shell out to `npx skills add`, which writes
   `~/.claude/skills/<name>/`. There is no path by which the bundle reaches `settings.json`.
   **The enforcement layer is sound.** (Caveat: this is verified for 0.7.69. It is a property of
   the current implementation, not a contract. `video-router-check.sh` should re-assert it.)

2. **Turning the `hyperframes` skill off cannot break the kinetic engine. CONFIRMED.**
   `render.sh:6,11` invoke `npx --yes hyperframes`, which resolves from the npm registry into
   `~/.npm/_npx/<hash>/node_modules/hyperframes` (two copies on disk). Nothing in that resolution
   path reads `~/.claude/skills`. Verified further at the code level: `render` triggers only
   `checkSkillsForUpdate()` (`cli.js:195338-195339`), a 24-hour-cached GitHub manifest check that
   prints a notice and writes counters. `installSkills()` is reached **only** from `updateSkills()`
   and `init`, never from `render`. The plan's claim is correct. Step 1 cannot break step 3's
   engine, and a render does not silently reinstall skills.

3. **The engine is relocatable. CONFIRMED.**
   `bin/make.sh:4` and `bin/make-ff.sh:7` both compute `PIPE="$(cd "$(dirname "$0")/.." && pwd)"`;
   `bin/render.sh` uses only `$PROJ`. **Zero** `/Users/eladtzur` literals in `pipeline/bin/`,
   `pipeline/lib/`, or `pipeline/config.json`. The only external dependency is
   `source ~/.claude/secrets/elevenlabs.env` (exists, 80 bytes, mode 0600), which is outside the
   pipeline and unaffected by the move. Node v25.6.1 and ffmpeg/ffprobe are present. Q3's claim
   that this is "a rename commit" rather than a rewrite holds at the shell level.

4. **The token measurement. CONFIRMED, and more precisely than claimed.**
   Measured across all 197 directories under `~/.claude/skills/` that contain a `SKILL.md`:
   70,603 characters of name+description, approximately **19,600 tokens**. The 22 off-list skills
   account for 14,130 characters, approximately **3,925 tokens**, = **20.0%** of the listing.
   The plan said ~19,800 / ~3,940 / 20%. Correct. (Skill count is 197, not 173, which does not
   change the conclusion.)

5. **`~/Movies` arithmetic. CONFIRMED.** 461 GB against 60 GB free (94% capacity). `READY/`
   exists with exactly `Efrat`, `Finance`, `Personal`, `Training`, and
   `video-tools/config.py:52-78` already maps into them. `move_log.csv` (2,104 bytes, 2026-02-24)
   and `snapshots/` (3 files, 1.6 MB each) exist and are the real undo ledger for the past 111 GB
   reorganization. Leaving `~/DEV/video-tools/` in place is right.

6. **Step 6 is safe, and safer than the plan believes. CONFIRMED.**
   `com.eladtzur.auto-transcribe` is PID 759, up 2 days 1 hour. `transcribe.log` shows it has
   processed **exactly one file, on 2026-03-09**; every subsequent entry is a
   `=== Watcher started ===` restart line, 15 of them across 4.5 months. `inbox/` holds only that
   one job's four output files; `done/` holds one `.wav`. Nothing consumes its output: the only
   references anywhere are `transcribe/skill.md:92-97` (documentation *of* the daemon) and
   `scripts/build-briefs.py:214,323` (a brief generator). `paper-edit/SKILL.md:16` uses
   "auto-transcribe" as a generic noun, not as a reference to this system. **The ASK gate's stated
   reason ("the owner may be actively dropping files into it") is answerable from the log rather
   than from the owner.** Retiring it is a clean win.

7. **HyperFrames skills are not plugin skills**, so the documented plugin exemption from
   `skillOverrides` does not apply. `~/.claude/plugins/` contains only marketplace metadata
   (`known_marketplaces.json`, `install-counts-cache.json`, `blocklist.json`), no installed
   plugins.

8. **§8b C2 is right:** `website-to-hyperframes` resolves to
   `/Users/eladtzur/.agents/skills/website-to-hyperframes` and is a live skill. It is correctly
   included in the 22.

9. **The `off`-but-readable-by-path argument is sound.** The Read tool works on any path
   regardless of skill state, so `hyperframes-core/SKILL.md` remains reachable. Q2's ruling is
   correct in mechanism. Its *execution* requirement (name each off skill and its path) is the
   part that is under-scoped, see W1.

---

## Section 4. Missing prerequisites, including what needs a human decision

| # | Prerequisite | Who decides |
|---|---|---|
| P1 | Resolve **where** `skillOverrides` is actually read from, via `/skills` + `Space` + `Enter`, before writing 22 keys anywhere | Claude, 1 minute, blocking on step 1 |
| P2 | A backup destination, or a git repo inside `pipeline/`, or one external copy. There is currently **none** | **Human**: hardware/purchase call |
| P3 | Keep or drop `higgsfield` in the advertising workflow. Turning it off removes image-to-video from live ad campaigns for zero routing benefit | **Human**: business call |
| P4 | Which `make_fcpx.py` is canonical: `icf-fcpx/`'s 14,310-byte copy or `pipeline/bin/`'s 15,123-byte copy | **Human**: only he knows which produced the last good Final Cut handoff |
| P5 | Whether `icf-fcpx` stays `on`. It is a genuine fourth router competitor with Hebrew triggers | **Human** |
| P6 | The 8 vault notes in step 4b are Hebrew SOPs he reads. Repointing them changes working documents | **Human**: review, not sed |
| P7 | Does Omac carry the bundle, and does step 1 need applying there | Claude, needs Omac reachable |
| P8 | `~/DEV/video/` project scaffolding: PROJECT-BRIEF.md, git init, `gh repo create peeym/video --private` (public vs private is his call), project-registry.json entry | **Human** for repo visibility, Claude for the rest |
| P9 | `com.eladtzur.video-weekly` fate, same ASK gate as step 6 | **Human** |

---

## Section 5. Verdict

**Safe to execute as written: NO.**

Not because the architecture is wrong. The adjudication is good, the mechanism choice
(`skillOverrides` over a bespoke manifest) is correct and independently verified here, the token
measurement is accurate to within 1%, the engine-relocatability finding is real and load-bearing,
and the `~/Movies` prohibition is right. The problems are all in the *consequences* of the steps,
which is exactly what five dimension-scoped reviewers could not see.

Three things must change before step 1 runs:
1. Prove where `skillOverrides` is actually read from (W3). One minute.
2. Patch `content-deriver.md`, `cco/CONTENT-MAP.md` and `advertising/SKILL.md` in the same change,
   and drop or downgrade `higgsfield` (W1).
3. Back up `settings.json` and define a post-edit verification that runs in a **new session**
   and proves the deny rules and the secret hook still load (W2).

With those three, step 1 becomes what the plan claims it is, and the "do step 1, then stop for a
week" recommendation is sound.

Steps 3, 4 and 5 must be re-sequenced (W6) and must not run at all until a backup exists (W8).

### Where the plan's own estimate is wrong

| Plan says | Reality |
|---|---|
| "7 documentation references, in one commit" | 15 files, 3 unversioned locations, no repo spans them. **No single commit exists.** |
| 25 video skills, 22 off, 6 visible | At least 27 exist. `icf-fcpx` and `image-expand` are unaccounted for; `icf-fcpx` is a fourth router competitor. |
| "TWO skill install roots" (§8b C1) | Three: `~/.claude/skills`, `~/.agents/skills`, `~/.openclaw/skills`. A fourth (`~/.codex/skills`) will be created by the next `init`. |
| Step 1 "reversible by deleting one block" | The file also carries the only secret-leak hook, 13 deny rules, and `acceptEdits`. Backup + JSON validation + new-session verification required. |
| One resident LaunchAgent in the video domain | Two (`auto-transcribe`, `video-weekly`), and 16 loaded overall. |
| Step 6 needs an ASK because "the owner may be actively dropping files into it" | The log answers it: one file, 2026-03-09, nothing since. Ask anyway out of courtesy, but the risk is nil. |
| Jobs reach `~/Movies` "by read-only symlink" | No such thing on macOS. The prohibition is a convention with no enforcement. |
| Free disk 64 GB | 60 GB, and falling. 94% capacity. |
| Everything is "Reversible? Yes" | No Time Machine destination, `~/DEV/ICF` is not a git repo, `~/.claude` is not a git repo. Reversibility rests on one same-disk copy. |

### Realistic timeline

The plan implies step 1 is a single edit plus a week of observation. Corrected:

- **Step 0 + P1 + W2 (verify mechanism, back up, define the post-edit check):** 1 hour.
- **W1 (audit all consumers of the 22 names, patch 3 documents):** 2 to 3 hours. This is real work
  and it is the difference between step 1 being a fix and being an outage in the CCO pipeline.
- **Step 1 + the observation week:** as planned, and worth it.
- **P2 (backup) before anything moves:** blocking, human-dependent, unknown duration.
- **Steps 3 to 5 re-sequenced, with both engines verified and 15 references repointed across
  3 locations:** a full day, not an afternoon. The `make_fcpx.py` divergence (P4) may add more.
- **Steps 6 to 9:** as planned, plus the `video-weekly` unload.

The week-one estimate holds only if W1 is done first. If step 1 ships without it, the failure will
surface days later inside a content or ad-campaign job, far from its cause, which is the worst
possible place to discover it.
