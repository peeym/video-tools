# Video Stack — Adjudicated Plan

Synthesis of two independent proposals (`PROPOSAL-claude.md`, `PROPOSAL-codex.md`)
against `INVENTORY.md` + its §8b corrections. Nothing has been executed. This document
is the plan, not a record of work done.

Priority order set by the owner, and applied as the tiebreaker throughout:
**good result → token saving → time saving.**

---

## The architecture in one paragraph

One router, `video-director`, sits above three proven production routes: `icf-video`
(script → Hebrew 9:16 explainer, FFmpeg-direct), `paper-edit` (footage → rough cut →
Final Cut), and `media-pipeline` (recordings → text). The HyperFrames bundle stops
being a competing router and becomes an engine that `video-director` selects
deliberately, enforced by `skillOverrides` in `settings.json` rather than by editing
files the bundle reinstalls. All video work happens in one new workspace,
`~/DEV/video/`, with one dated folder per job and an identical layout for every job
type. `~/Movies` is never touched.

---

## Where the two reviewers disagreed, and the ruling

### Q1 Routing — **Claude's mechanism wins outright**

Codex proposed a precedence sentence in the global file, plus
`~/.claude/video-stack/manifest.yaml`, plus wrapper scripts
(`update-hyperframes-skills`, `audit-video-skills`) with snapshot/restore.

Claude proposed `skillOverrides` in `~/.claude/settings.json`.

**Ruling: `skillOverrides`.** Verified in the Claude Code changelog on this machine:

> `skillOverrides` setting now works: `off` hides from model and `/`,
> `user-invocable-only` hides from model only, `name-only` collapses description

It beats the manifest approach on every axis that matters here:

| | `skillOverrides` | manifest + wrapper + audit |
|---|---|---|
| Survives `npx hyperframes init` | Yes. `init` writes to skill dirs, never to `settings.json` | Only if the wrapper is always used |
| Machinery to build and maintain | None. Platform native | 2 shell scripts, a YAML schema, snapshot/restore logic |
| Rollback | Delete a line | Restore a dated snapshot |
| Recovers listing tokens | Yes, `off` removes the description from context | No. Files move but the mechanism is bespoke |
| Failure mode | Skill silently visible if key missing | Wrapper bypassed → full drift |

Codex built a careful solution to a problem the platform already solves. That is the
value of running two lineages: neither of them alone would have produced both the
discovery of the self-reinstall (Codex) and the native fix for it (Claude).

**What survives from Codex:** its layer-3 concern. A future bundle version can ship a
skill under a **new name**, which arrives `on` because no key exists for it.
`skillOverrides` cannot cover an unknown name. Both reviewers independently arrived at
the same answer: a passive, click-to-run drift check. Adopted, as
`~/DEV/video/bin/video-router-check.sh`, run by hand, never a LaunchAgent.

### Q2 Surface area — **Claude's cut, with Codex's caveat attached**

Codex: 25 → 14 visible. Claude: 25 → 6 visible.

The gap is entirely about the HyperFrames domain skills and the three
existing-footage workflows. Codex keeps them visible because they are genuinely
useful. Claude turns them off because **an `off` skill is still readable by path**:
`video-director` can open `hyperframes-core/SKILL.md` when it actually needs the
composition contract, without that skill competing for every video request.

**Ruling: Claude's cut.** The readability argument defeats Codex's reason for keeping
them visible. But Codex's caveat is adopted as a hard requirement: **the rewritten
`video-director` must name each `off` skill and its path**, or the capability becomes
unreachable in practice. An off skill that nothing points at is a deleted skill with
extra steps.

**Measured justification for cutting, verified independently:** 173 skills carry
descriptions totalling ~19,800 tokens. The 25 video skills are ~3,940 of them, **20% of
the entire skill listing**, loaded on every request in every project. This is filed
under priority 1 (good result), not priority 2 (token saving): a listing that large
makes which skills the model actually sees non-deterministic.

**Both reviewers flagged the same two as genuinely uncertain.** Neither guessed:

| Skill | The open question | The test that settles it |
|---|---|---|
| `embedded-captions` | 32 caption identities, but no evidence any of them handles Hebrew RTL correctly | Run one identity on a 15-second Hebrew clip. If the RTL renders correctly it is worth keeping reachable; if not, it is dead weight for this owner |
| `video-use` | Overlaps `paper-edit` on rough cutting but carries production rules `paper-edit` lacks. Its rules conflict: 30 ms fades vs ~12 ms, cloud Scribe vs local Hebrew ASR | Decide whether its hard-rules section is worth extracting into `video-director`'s references before turning it off |

### Q3 The folder — **Claude's tree**

Codex: `~/DEV/video-work/` with `jobs/YYYY/YYYY-MM-DD--client--slug/` and a deep
per-job tree (`plan/`, `work/`, `review/`, `renders/`, `fcp/`, `logs/`).

Claude: `~/DEV/video/` with `jobs/YYYY-MM-DD-slug/` and seven children.

**Ruling: Claude's**, on evidence rather than taste. It verified three things Codex
assumed:

1. The engine scripts derive their own root (`PIPE` from `$(dirname $0)/..`), so moving
   the pipeline does not break them. What breaks is **documentation**: 7 files
   including two vault SOP notes. That reframes the move from "risky" to "a rename
   commit".
2. `~/Movies` is **461 GB against 64 GB free**. Copy-then-verify is not merely unwise
   there, it is arithmetically impossible. Confirmed by `df`/`du`.
3. `~/Movies/READY/` already exists with exactly the four subfolders finished
   deliverables should land in, and `video-tools/reorganize.py` already knows them. No
   new delivery convention needs inventing.

Codex's deeper per-job tree is more structure than the work needs. Claude's flat seven
children keep both job types identical, which is what lets one `to-fcp.sh` operate on
any job without branching.

### Q5 The global file — **Claude's minimalism**

Codex wants an explicit precedence sentence in `~/.claude/CLAUDE.md`.
Claude wants three lines, ~60 tokens, and **no routing text at all**.

**Ruling: Claude.** Once `hyperframes` is `off`, there is no competitor left to
establish precedence over, so a precedence sentence is dead text paid for on every
request in every project forever. The boundary test Claude proposes is the right one:
*does this need to be true when no video skill has fired?* Only facts that pass that
test belong in the global file.

### Q6 and Q7 — no material disagreement

Both converge on the same gates and a similar migration order. Claude's ordering is
adopted because it front-loads the highest value at the lowest risk.

---

## What actually gets done, in order

**Nothing in this list has been started. Every step marked ASK stops for approval.**

| # | Step | Reversible? | Gate |
|---|---|---|---|
| 0 | Preconditions. No changes. Confirm Claude Code version supports `skillOverrides`, back up `settings.json` to `~/.claude/emergency/config-backup/` | n/a | — |
| 1 | **`skillOverrides` block into `~/.claude/settings.json`.** 22 keys. This alone delivers §1 and §2 in full | Yes, delete the block | ASK |
| 2 | Three lines into `~/.claude/CLAUDE.md` + rewrite `video-director` to add `paper-edit`, `media-pipeline`, and the paths of every `off` skill | Yes | ASK |
| 3 | Create `~/DEV/video/`, **copy** the engine, verify a render, only then archive the original | Yes, original untouched until verified | ASK |
| 4 | Repoint all 7 documentation references in one commit | Yes | — |
| 5 | Move the 9 pipeline projects into `jobs/` with date prefixes | Yes | — |
| 6 | Retire the `com.eladtzur.auto-transcribe` daemon to `~/Library/LaunchAgents/disabled/` | Yes | **ASK** |
| 7 | The `embedded-captions` Hebrew RTL test | n/a, a test | — |
| 8 | Archive leftovers: `hyperframes-lab`, the 8 loose MP4s | Yes | **ASK, each separately** |
| 9 | Reconcile the two wiki KBs | Yes | — |

**Claude's recommendation, adopted: do step 1, then stop for a week.** It is one edit,
it is reversible by deleting one block, and it resolves the router collision, the
surface-area problem and the token load in a single move. Everything after it is
cleanup that benefits from a week of knowing step 1 held.

## The one hard prohibition

`~/Movies` is not touched in any step, by any tool, at any point. Five live
`.fcpbundle` libraries plus ~40 backup bundles, Final Cut stores absolute paths to
external media, and there is not enough free disk to copy anything. Jobs reach into it
by **read-only symlink only**.

## Findings neither reviewer was asked for

1. `com.eladtzur.auto-transcribe` is a `KeepAlive` LaunchAgent **running right now**
   (PID 759) that polls an inbox. This violates the recorded no-resident-listeners
   preference. Verified via `launchctl list`. Step 6, ask first: the owner may be
   actively dropping files into it.
2. The HyperFrames bundle exists as **two separate copies** (`~/.agents/skills/` and
   `~/.claude/skills/`), verified by inode, roughly 110 MB duplicated. `skillOverrides`
   makes this harmless from a routing standpoint, but it is worth knowing before any
   future "clean up disk" pass touches one root and not the other.
3. `~/DEV/video-tools/`, the project this planning folder currently sits inside, is a
   **media-library** tool, not a video-production tool. Its `move_log.csv` and
   `snapshots/` are the live undo ledger for a 111 GB reorganization of `~/Movies`.
   It stays exactly where it is. This planning folder should move to `~/DEV/video/`
   when that is created.
