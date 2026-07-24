The target architecture should have one tiny, globally enforced router—`video-director`—above a small set of proven production workflows. The common Hebrew explainer remains on the fast FFmpeg-direct ICF engine; recorded footage goes through `paper-edit` and then Final Cut; HyperFrames becomes an explicitly selected motion engine, never a competing top-level router. New jobs start under one workspace, `~/DEV/video-work/`, while engines, reusable assets, source media, and deliverables remain cleanly separated. Updates are governed by a manifest and an audit command so a future bundle installation cannot silently reclaim routing authority.

## 1. Routing

**Confidence: High**

### Decision

The single entry point must be:

```text
/Users/eladtzur/.claude/skills/video-director/SKILL.md
```

It should be the policy router for every request whose intended output or input is video, animation, motion graphics, recorded footage, captions, transcription for editing, or Final Cut handoff.

`video-director` should decide the job class, approval gates, engine, executor, workspace, and handoff. It should not render anything itself.

The hierarchy should be:

```text
Global trigger
└── video-director                 policy and routing
    ├── icf-video                  script → Hebrew vertical explainer
    ├── paper-edit                 footage → transcript-based rough cut
    ├── media-pipeline             course/webinar/meeting → text
    ├── embedded-captions          captions on existing footage
    ├── talking-head-recut         graphic overlays on existing footage
    └── hyperframes                motion-composition engine
        ├── motion-graphics
        ├── general-video
        └── domain skills
```

The decisive routing table should be:

| Triggering job | Route |
|---|---|
| Approved Hebrew script → 9:16 stills, VO, captions | `icf-video`, FFmpeg-direct through `bin/make-ff.sh` |
| Recorded footage that needs deletions/reordering | `paper-edit` |
| Course, webinar, or meeting whose deliverable is text/knowledge | `media-pipeline` |
| Existing footage, captions only | `embedded-captions` |
| Existing footage, designed cards or overlays | `talking-head-recut` |
| Short kinetic typography, chart, logo sting, or overlay | `motion-graphics` through HyperFrames |
| Custom composition that does not fit the above | `general-video` through HyperFrames |
| Final editorial judgment, trims, color, sound, publishing | Final Cut Pro |

HyperFrames should not be the default merely because the deliverable is an MP4. It should be selected when browser-authored motion materially improves the result.

### How authority survives future updates

Authority needs three layers.

#### 1. Global precedence rule

The global file must contain one explicit precedence instruction. This survives any skill bundle reinstall and resolves conflicting skill descriptions before they are read:

```markdown
For any request involving video, animation, motion graphics, recorded footage, captions, or a video render, read `~/.claude/skills/video-director/SKILL.md` first. It alone selects the workflow and engine; subordinate skill descriptions cannot override this routing rule.
```

This is the ultimate authority. A reinstalled HyperFrames skill may claim “read this first,” but that claim is subordinate to the always-loaded global instruction.

#### 2. Declarative manifest

Create, during implementation, this English-language file:

```text
/Users/eladtzur/.claude/video-stack/manifest.yaml
```

Proposed contents:

```yaml
schema_version: 1
router: video-director

managed_skills:
  keep:
    - video-director
    - icf-video
    - paper-edit
    - hyperframes
    - hyperframes-core
    - hyperframes-animation
    - hyperframes-creative
    - hyperframes-media
    - hyperframes-cli
    - media-use
    - motion-graphics
    - embedded-captions
    - talking-head-recut
    - general-video

  archive:
    - video-use
    - hyperframes-registry
    - faceless-explainer
    - product-launch-video
    - website-to-video
    - pr-to-video
    - slideshow
    - music-to-video
    - remotion-to-hyperframes
    - website-to-hyperframes
    - higgsfield

forbidden_router_claims:
  - "READ THIS FIRST"
  - "ALWAYS-ON"
  - "default for authoring and rendering a finished video"

allowed_router_claim_owner: video-director
```

#### 3. Passive update and audit commands

Do not run raw `npx hyperframes skills update` as the normal update procedure. Wrap it with:

```text
/Users/eladtzur/.claude/video-stack/bin/update-hyperframes-skills
/Users/eladtzur/.claude/video-stack/bin/audit-video-skills
```

The update command should:

1. Snapshot the current skill directories into a dated archive.
2. Run the upstream update.
3. Compare installed skills with `manifest.yaml`.
4. Move non-approved workflow skills out of the discovery directory.
5. Report any first-reader/default-routing claims outside `video-director`.
6. Run smoke tests.
7. Restore the prior snapshot automatically if the audit or smoke tests fail.

The audit must be click-to-run, not a listener. It should also be invoked explicitly after installing or updating any video tool.

Even if someone bypasses the wrapper, the global precedence sentence still protects routing. The manifest and audit protect surface area and make drift visible.

### Required change inside HyperFrames

In the retained copy of:

```text
/Users/eladtzur/.claude/skills/hyperframes/SKILL.md
```

its description should become engine-scoped, for example:

```yaml
description: HyperFrames engine router for browser-authored video compositions. Use only after `video-director` selects HyperFrames, or when the user explicitly names HyperFrames.
```

Its internal workflow routing remains useful once HyperFrames has been selected.

### Inventory correction

The inventory is correct that the two skills collide, but it understates the persistence problem. The real `hyperframes/SKILL.md` says that `npx hyperframes init` and `npx hyperframes skills update` install or refresh the **full** skill set, including missing skills. It also says `--skip-skills` is temporarily ineffective. Therefore, manually editing or archiving the collision once is insufficient.

---

## 2. Surface area

**Confidence: Medium-high**

There should be **14 discoverable video skills**, plus the separate `media-pipeline` workflow for recorded-content processing. Eleven of the current 25 video entries should be archived outside `~/.claude/skills/`.

The archive root should be:

```text
/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/
```

Nothing should be deleted.

### Keep discoverable: 14

| Skill | Verdict | Reason |
|---|---|---|
| `video-director` | Keep and revise | Sole router and approval-policy owner. Add `paper-edit`, `video-use` disposition, standardized workspace, canonical service rules, and update governance. |
| `icf-video` | Keep and revise | Proven owner-specific workflow for the most common shipped product. It should use FFmpeg-direct by default and stop presenting `bin/make.sh` as the normal renderer. |
| `paper-edit` | Keep | Proven, high-value workflow for recorded footage. Its review gate, quiet-boundary snapping, resumability, and FCPXML option are sound. |
| `hyperframes` | Keep but subordinate | Needed as the entry point after HyperFrames is deliberately selected. Remove its global-default claim. |
| `hyperframes-core` | Keep | Required composition contract. |
| `hyperframes-animation` | Keep | Required for deterministic motion and runtime adapters. |
| `hyperframes-creative` | Keep | Useful creative-direction knowledge for motion work. |
| `hyperframes-media` | Keep as a HyperFrames dependency | Required by retained HyperFrames workflows, but not canonical for owner-wide Hebrew TTS or transcription. |
| `hyperframes-cli` | Keep | Required to validate and render HyperFrames work. |
| `media-use` | Keep | Shared frozen-media and ledger mechanism for retained HyperFrames workflows. |
| `motion-graphics` | Keep | Clear, narrow route for short motion-first work that the FFmpeg explainer engine cannot replace. |
| `embedded-captions` | Keep | Specialized caption compositing on existing footage; distinct from producing an explainer. |
| `talking-head-recut` | Keep | Specialized designed overlays on existing footage; distinct from rough cutting and captions. |
| `general-video` | Keep | Necessary bounded fallback inside HyperFrames after the top-level router selects that engine. |

### Archive from discovery: 11

| Skill | Exact source | Exact destination | Reason |
|---|---|---|---|
| `video-use` | `/Users/eladtzur/.claude/skills/video-use` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/video-use` | It overlaps routing, transcription, rough cutting, captions, grading, animation, and final rendering. Several rules conflict with `paper-edit`, including 30 ms versus approximately 12 ms fades and cloud ElevenLabs Scribe versus local Hebrew transcription. Preserve its code and production lessons, but do not allow it to wake independently. Move useful hard rules into tests or references of the canonical workflows. |
| `hyperframes-registry` | `/Users/eladtzur/.claude/skills/hyperframes-registry` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/hyperframes-registry` | Rare development/contribution task, not routine production. Restore temporarily when modifying the registry. |
| `faceless-explainer` | `/Users/eladtzur/.claude/skills/faceless-explainer` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/faceless-explainer` | It collides directly with the proven `icf-video` route for script-led explainers and defaults to an invented-visual HyperFrames architecture. Retain it only as reference. |
| `product-launch-video` | `/Users/eladtzur/.claude/skills/product-launch-video` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/product-launch-video` | Useful but not part of the observed regular shipping pattern. Its broad “product or marketing URL, pasted script, or brief” trigger creates routing noise. |
| `website-to-video` | `/Users/eladtzur/.claude/skills/website-to-video` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/website-to-video` | Specialized, currently non-core. Restore only for a real site-tour job. |
| `pr-to-video` | `/Users/eladtzur/.claude/skills/pr-to-video` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/pr-to-video` | Very specialized and unrelated to the owner’s observed video output. |
| `slideshow` | `/Users/eladtzur/.claude/skills/slideshow` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/slideshow` | Produces a navigable deck, explicitly not a rendered video. It belongs with presentation tooling, not the always-visible video surface. |
| `music-to-video` | `/Users/eladtzur/.claude/skills/music-to-video` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/music-to-video` | Large and specialized. No observed recurring music-led deliverable justifies its always-visible trigger and references. |
| `remotion-to-hyperframes` | `/Users/eladtzur/.claude/skills/remotion-to-hyperframes` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/remotion-to-hyperframes` | Migration utility, not production workflow. Restore only for an explicit Remotion port. |
| `website-to-hyperframes` | `/Users/eladtzur/.claude/skills/website-to-hyperframes` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/website-to-hyperframes` | Redundant with `website-to-video`. Archive the symlink itself. |
| `higgsfield` | `/Users/eladtzur/.claude/skills/higgsfield` | `/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/higgsfield` | Separate provider-specific route that bypasses the central model/provider policy. The ICF workflow already has controlled HERO-clip generation. |

Archived skills remain recoverable and can be temporarily restored for an explicit job. That is preferable to paying for their descriptions and collisions on every Claude Code session.

### Agents

Retain these executor agents:

```text
/Users/eladtzur/.claude/agents/icf-video-producer.md
/Users/eladtzur/.claude/agents/paper-edit-engine.md
/Users/eladtzur/.claude/agents/media-pipeline-runner.md
```

Do not merge them into a universal video agent. Their operational risks differ:

- `icf-video-producer`: generated assets, TTS, render, FCP kit.
- `paper-edit-engine`: local transcription, human cut decision, audio-boundary safety.
- `media-pipeline-runner`: resumable batch processing, diarization, knowledge outputs.

Revise `icf-video-producer.md` to use `bin/make-ff.sh` by default. It currently directs every approved script to the slow `bin/make.sh` HyperFrames renderer and downscaling flow, contrary to the newer director policy.

### Inventory corrections

The inventory says “HyperFrames bundle — 15 skills,” but its own tables enumerate **19** entries:

- Seven domain/entry skills.
- Twelve workflow/support skills.

With the three owner-authored skills, `video-use`, `higgsfield`, and the `website-to-hyperframes` symlink, that produces the stated 25-item surface.

The inventory also says `website-to-hyperframes` “resolves to nothing.” Independent verification found the symlink test succeeds on this machine. The symlink is:

```text
/Users/eladtzur/.claude/skills/website-to-hyperframes
→ ../../.agents/skills/website-to-hyperframes
```

Its contents should still be inspected at migration time before archiving; the inventory’s broken-link claim is not currently reliable.

---

## 3. The folder

**Confidence: High for the layout; medium for moving existing projects**

### Workspace root

Create during implementation:

```text
/Users/eladtzur/DEV/video-work/
```

It must contain its own `PROJECT-BRIEF.md`.

Proposed tree:

```text
~/DEV/video-work/
├── PROJECT-BRIEF.md
├── README.md
├── templates/
│   ├── job/
│   │   ├── JOB.md
│   │   └── manifest.json
│   ├── explainer-9x16/
│   └── paper-edit/
├── jobs/
│   └── YYYY/
│       └── YYYY-MM-DD--client--slug/
│           ├── JOB.md
│           ├── manifest.json
│           ├── source/
│           │   ├── script.md
│           │   ├── script.json
│           │   └── media/
│           ├── plan/
│           │   ├── brief.md
│           │   ├── storyboard.md
│           │   └── approvals.md
│           ├── work/
│           │   ├── transcript/
│           │   ├── assets/
│           │   ├── audio/
│           │   ├── composition/
│           │   └── cache/
│           ├── review/
│           │   ├── sketch.mp4
│           │   ├── review.html
│           │   ├── cuts.json
│           │   └── contact-sheets/
│           ├── renders/
│           │   ├── drafts/
│           │   └── masters/
│           ├── fcp/
│           │   ├── timeline.fcpxml
│           │   ├── media/
│           │   ├── captions/
│           │   └── README.md
│           └── logs/
├── archive/
│   └── YYYY/
└── links/
    ├── icf-engine
    ├── shared-media-bank
    └── hyperframes-lab
```

### Where a job starts

Every new video job starts at:

```text
~/DEV/video-work/jobs/YYYY/YYYY-MM-DD--client--slug/
```

`JOB.md` records:

- Purpose and audience.
- Owner/business.
- Source paths.
- Output language.
- Aspect ratio and target duration.
- Selected workflow and engine.
- Provider restrictions.
- Approval status.
- Deliverables.
- Final Cut handoff status.

`manifest.json` is machine-readable and records source fingerprints, engine version, commands, generated outputs, and approvals. It prevents a later session from guessing what already ran.

The original source media must remain untouched. If copying very large footage is wasteful, `source/media/` may contain stable symlinks plus fingerprints, but `JOB.md` must identify the actual originals.

### Shared assets

Continue using:

```text
/Users/eladtzur/DEV/shared/media-bank/
```

Do not move it. It is already shared across video, decks, and sites.

Add only a convenience symlink:

```text
~/DEV/video-work/links/shared-media-bank
→ /Users/eladtzur/DEV/shared/media-bank
```

Job-specific or licensed assets belong in:

```text
<job>/work/assets/
```

They must not be promoted to the shared bank without an explicit reusable/license decision.

### Finished renders

Use:

```text
<job>/renders/drafts/
<job>/renders/masters/
```

A master filename should encode version and format:

```text
<slug>--v03--1080x1920--master.mp4
<slug>--v03--prores-master.mov
```

Do not use `~/Movies/READY/` as the source of truth. If the owner wants a familiar Finder-facing queue, place a symlink or copy there only after the job master has been verified.

### Final Cut handoff

Every FCP handoff is self-contained:

```text
<job>/fcp/
├── <slug>.fcpxml
├── README.md
├── media/
│   ├── source-or-rough-cut.mov
│   ├── voiceover.wav
│   ├── music.wav
│   ├── broll/
│   └── overlays/
└── captions/
    ├── captions.srt
    └── captions.ass
```

`README.md` states:

- Timeline resolution and frame rate.
- Expected duration.
- Whether cuts are flattened or adjustable.
- Font requirements.
- Which effects are baked in.
- Which captions are editable.
- Relink root.
- Known `LOUD` paper-edit boundaries or other limitations.

The FCP library itself remains in `~/Movies/`. Libraries are large application-managed packages and should not be moved by this redesign.

### Treatment of the five current locations

#### 1. ICF pipeline

Leave in place initially:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline/
```

Add:

```text
~/DEV/video-work/links/icf-engine
→ /Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline
```

Reason: it is proven and currently occupies approximately 2.5 GB. Skills, agents, vault SOPs, existing commands, logs, and project-relative assumptions all name its current path.

Moving it immediately would break:

- `video-director/SKILL.md`
- `video-director/references/engines.md`
- `icf-video/SKILL.md`
- `icf-video-producer.md`
- Vault workflow notes and templates.
- Commands or scripts that expect `pipeline/projects/<name>`.
- Resumability of existing project folders.

Long-term, engine code should be extracted into a versioned project such as:

```text
/Users/eladtzur/DEV/video-engines/icf-video/
```

but only after tests prove that projects can live outside the engine tree. Do not make that extraction part of the first migration.

New ICF jobs should live under `~/DEV/video-work/jobs/`, with an engine adapter passing the job’s explicit path. If `bin/make-ff.sh` or `bin/tts.py` cannot operate on an external project path, that capability must be added and tested before new jobs leave `pipeline/projects/`.

#### 2. Parent ICF output folder

Leave existing files in place:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/
```

Do not move the existing `SKETCH-*`, `PROOF-*`, `DEMO-*`, v1–v5 files, `assets/`, `broll/`, or `poster.jpg` until the owner identifies which belong to which project. Moving them without that mapping could break FCP relinks and destroy provenance.

After mapping, copy or move each group—with permission—to:

```text
~/DEV/video-work/archive/YYYY/<job-slug>/legacy-import/
```

The single evidence needed to settle this is whether any current `.fcpbundle` references those exact absolute media paths.

#### 3. `~/DEV/video-tools/`

Leave in place:

```text
/Users/eladtzur/DEV/video-tools/
```

It is a utility project, not a job workspace. Complete and approve its existing `PROJECT-BRIEF.md`; do not mix its organization/archive tools into production job folders.

The current redesign directory also stays inside this project:

```text
/Users/eladtzur/DEV/video-tools/video-stack-redesign/
```

#### 4. HyperFrames lab

Leave in place:

```text
/Users/eladtzur/DEV/hyperframes-lab/
```

Add:

```text
~/DEV/video-work/links/hyperframes-lab
→ /Users/eladtzur/DEV/hyperframes-lab
```

It is a lab/test project, not the canonical job directory. Existing `test-promo` paths may be referenced by its local configuration and should not be moved without a successful render after relocation.

#### 5. `~/Movies/`

Leave the entire location in place:

```text
/Users/eladtzur/Movies/
```

Especially do not move:

- `.fcpbundle` libraries.
- `Motion Projects/`
- `Motion Templates/`
- `Titles/`

Final Cut and Motion use application-specific paths and internal references. Moving libraries or source media can trigger relinking and library corruption risk.

`00 - Edit video/`, `EDITING/`, and `READY/` may remain the owner’s human queue, but they should contain handoff copies or symlinks, not the authoritative project state.

---

## 4. Duplication

**Confidence: Medium**

The correct consolidation is a canonical contract plus workflow-specific presentation, not one renderer forced into every use case.

### Transcription

Canonical implementation:

```text
/Users/eladtzur/.claude/skills/paper-edit/scripts/transcribe_local.py
```

Its local PC route using `ivrit-ai/whisper-large-v3-ct2` should become the basis of a shared command:

```text
/Users/eladtzur/DEV/video-tools/transcription/transcribe.py
```

Canonical output should be a versioned JSON schema containing:

- Source fingerprint.
- Language.
- Model and model version.
- Segments.
- Word-level `start`, `end`, and text.
- Optional speaker identity.
- Generation time.
- Explicit timing units.

Adapters:

- `paper-edit` calls it directly.
- `media-pipeline` calls it in batch mode, then adds diarization.
- `embedded-captions` and `talking-head-recut` consume the same JSON rather than retranscribing.
- `hyperframes-media` may keep its Whisper implementation for non-Hebrew, isolated HyperFrames jobs, but must reuse a supplied canonical transcript when one exists.
- `/transcribe` becomes a thin user-facing wrapper around the shared command.
- `video-use` transcription is retired with the skill.
- `~/DEV/auto-transcribe/` may call the same command when manually triggered, but its resident watcher should not define the canonical path.

Do not replace the proven paper-edit transcriber until an equivalence test demonstrates word timings, Hebrew accuracy, cleanup, failure reporting, and PC cleanup.

### Captions

Canonical data source: the approved written text when a script exists; otherwise the corrected canonical transcript.

Canonical authoring rules should live at:

```text
/Users/eladtzur/.claude/skills/video-director/references/captions.md
```

That file should define:

- Source-of-truth precedence.
- RTL and mixed Hebrew/English rules.
- Safe zones.
- No trailing period for short on-screen captions.
- Output-timeline timing after cuts.
- Review-frame requirements.
- FCP handoff formats.

Render adapters remain specialized:

- ICF explainer: `pipeline/bin/ffrender.py` for burned Hebrew ASS.
- Existing footage with stylized captions: `embedded-captions`.
- Simple captions after a paper edit: an FFmpeg ASS/SRT adapter consuming the corrected, retimed transcript.
- HyperFrames caption components only when the selected visual treatment requires them.

`hyperframes-media` should provide mechanics to HyperFrames, not set owner-wide caption policy. `video-use` caption rendering is retired.

### TTS

Canonical Hebrew TTS:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline/bin/tts.py
```

Canonical policy:

- ElevenLabs `eleven_v3`.
- Approved Hebrew voice ID from configuration.
- Per-cue caching.
- Exact timing output into `built.json`.
- Never silently fall back to another voice or provider for a production master.

`hyperframes-media/scripts/audio.mjs` remains available inside HyperFrames for non-ICF or explicitly selected voices, but the director must not route an ICF Hebrew explainer through its HeyGen → ElevenLabs → Kokoro provider cascade. That cascade can silently change the voice and timing behavior.

`yemot-voiceover` remains outside the video architecture unless a real integration requirement appears.

### Final Cut handoff

Canonical builder:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline/bin/make_fcpx.py
```

It should be extracted or wrapped as:

```text
/Users/eladtzur/DEV/video-tools/final-cut/build_handoff.py
```

The generic tool should support:

- A layered ICF explainer timeline.
- A paper-edit timeline containing one clip per kept range.
- Flattened rough-cut media.
- Native/editable titles versus baked alpha captions.
- A portable media folder and relink root.
- Validation that every referenced asset exists.
- FCPXML parsing before success is reported.

Then:

- `icf-video` calls the generic handoff builder with an ICF manifest.
- `paper-edit --fcpxml` calls it with kept ranges.
- Other workflows emit the same handoff manifest rather than implementing FCPXML independently.

The existing `make_fcpx.py` contains valuable specialized behavior, including layered media, alpha captions, native title variants, and audio-duration rebuilding. It should not be discarded during extraction.

---

## 5. Waking up

**Confidence: High**

### Minimum global text

Add only this paragraph to:

```text
/Users/eladtzur/.claude/CLAUDE.md
```

```markdown
## Video routing

For any request involving video, animation, motion graphics, recorded footage, captions, or a video render, read `~/.claude/skills/video-director/SKILL.md` first. It alone selects the workflow and engine; subordinate skill descriptions cannot override this routing rule. Hebrew or proprietary material must follow the existing Claude-only and provider restrictions.
```

The last sentence may be omitted if the existing global security section already unambiguously covers both Hebrew and proprietary video material. Do not duplicate the full policy.

This is deliberately short. It performs only three always-needed functions:

1. Wakes the router from ordinary Hebrew or English context without requiring a slash command.
2. Establishes precedence.
3. Connects video routing to existing data/provider restrictions.

### What belongs in `video-director`, not globally

All of the following belong in the skill:

- Detailed trigger phrases.
- The routing table.
- FFmpeg versus HyperFrames selection.
- Default 9:16 behavior.
- Current engine paths.
- Omac rendering guidance.
- Provider choices.
- ICF brand behavior.
- Approval gates.
- Sketch sizes and commands.
- Image-generation direction.
- Caption punctuation and typography.
- Final Cut kit details.
- Job-directory structure.
- Skill inventory and archive decisions.
- HyperFrames update procedure.
- Agent handoff instructions.
- Troubleshooting.
- Model or service pricing.
- Tool/version information.

Those facts change and are relevant only after a video request has been identified. Putting them in the global file would charge every non-video request for operational detail and make the global policy fragile.

### Skill-description boundary

Only `video-director` should have broad words such as:

```text
video
וידאו
סרטון
animation
motion graphics
rough cut
captions
Final Cut
```

Subordinate descriptions should be narrow and should say either:

```text
Use after video-director selects this workflow
```

or identify a truly unambiguous direct request, such as an explicit `/paper-edit` or “port this Remotion project.”

This reduces accidental parallel wake-ups. The descriptions do not need to restate the entire negative routing matrix because the router owns it.

---

## 6. The procedure

**Confidence: High**

### A. Script → finished 9:16 Hebrew explainer

#### 1. Create the job

Create:

```text
~/DEV/video-work/jobs/YYYY/YYYY-MM-DD--icf--<slug>/
```

Record purpose, audience, destination, target duration, voice choice, and source script in `JOB.md`.

Default route:

```text
video-director → icf-video → icf-video-producer → FFmpeg-direct
```

#### 2. Script and scene plan

The editable Hebrew script remains in the approved vault location. Copy or export the approved version into:

```text
<job>/source/script.md
```

Create scene-level `script.json` with:

- Narration.
- Exact on-screen title/caption text.
- Image description.
- Visual source.
- Effect.
- CTA.
- HERO-motion designation.

**Gate 1 — Script approval**

The owner approves wording, scene division, and on-screen text.

Reason: TTS, imagery, timing, captions, and editing all depend on the wording. Rendering before this gate wastes downstream work and can accidentally publish wording the owner did not choose.

#### 3. Visual proof

Generate or ingest representative visuals into:

```text
<job>/work/assets/
```

Use native 9:16 images where possible. Otherwise contain-fit over a blurred fill; never crop heads or bodies to force portrait framing.

Create a contact sheet showing every proposed visual or at least all generated visuals.

**Gate 2 — Visual approval**

The owner approves subject depiction, realism, brand fit, diversity, and absence of visual clichés.

Reason: image mistakes are expensive to repair after animation and may be reputationally damaging.

#### 4. Voice proof

Generate a short VO sample using the selected ElevenLabs `eleven_v3` voice, including at least one sentence with numbers or mixed Hebrew/English.

**Gate 3 — Voice approval when voice or settings changed**

This gate may be recorded as already approved for a stable voice/configuration.

Reason: pronunciation, pacing, and mixed-language handling determine the timing of the whole piece.

#### 5. Same-engine sketch

Run the FFmpeg-direct sketch through:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline/bin/make-ff.sh
```

Produce 2–3 representative scenes at 540×960 with actual text, image, VO, captions, and transition behavior:

```text
<job>/review/sketch.mp4
```

**Gate 4 — Sketch approval**

The owner approves pacing, caption readability, safe zones, motion intensity, audio balance, and overall visual language.

Reason: this is the cheapest reliable point to detect systemic rendering mistakes. The sketch must use the same engine as the final.

#### 6. Full render

Render all scenes at 1080×1920. Use only 2–3 AI-generated motion clips where they materially improve HERO moments; use stills with restrained Ken Burns elsewhere.

Output:

```text
<job>/renders/drafts/<slug>--v01.mp4
```

Run:

- `ffprobe` duration/audio checks.
- Contact-sheet inspection.
- First and last frame check.
- Mixed Hebrew/English caption inspection.
- Safe-zone and head-crop inspection.
- Audio/cut alignment inspection.
- File-existence and nonzero-size checks before reporting success.

#### 7. Content review

**Gate 5 — Full-cut approval**

The owner reviews the whole video and gives timecoded feedback.

Reason: local details can pass the sketch while the full narrative still feels repetitive, slow, or unbalanced.

#### 8. Master and Final Cut kit

After revisions, produce:

```text
<job>/renders/masters/<slug>--vNN--1080x1920--master.mp4
<job>/fcp/<slug>.fcpxml
<job>/fcp/media/
<job>/fcp/README.md
```

**Gate 6 — Final master approval**

Confirm the exact file that is considered finished. No publishing is implied.

Reason: distinguishes an approved production master from a technically successful render.

### B. Recorded footage → rough cut ready for Final Cut

#### 1. Create the job and preserve source

Create the standard job folder. Record or link the original footage under:

```text
<job>/source/media/
```

Fingerprint it. Never alter the original.

Default route:

```text
video-director → paper-edit → paper-edit-engine
```

#### 2. Editorial brief

Establish:

- Intended audience.
- Target length.
- Must-keep material.
- Must-remove material.
- Whether chronology may change.
- Whether the FCP handoff should be flattened or adjustable.

**Gate 1 — Editorial strategy approval**

The owner approves the intended shape before cuts are created.

Reason: transcript accuracy cannot determine editorial intent.

#### 3. Transcribe and correct

Run canonical local Hebrew transcription. Store:

```text
<job>/work/transcript/transcript.json
<job>/work/transcript/corrections.json
<job>/work/transcript/clean.json
```

Corrections modify text only, never timings. Report uncertain terms with timecodes.

#### 4. Browser review

Build:

```text
<job>/review/proxy.mp4
<job>/review/review.html
```

The owner strikes out deletions and exports:

```text
<job>/review/cuts.json
```

The current workflow exports to `~/Downloads/cuts.json`; the standardized implementation should immediately copy that file into the job and record its hash.

**Gate 2 — Cut-decision approval**

The owner explicitly confirms the exported cuts.

Reason: deletion decisions are editorial and potentially consequential; Claude must not infer them from filler words alone.

#### 5. Smooth and grade boundaries

Run quiet-point snapping to produce:

```text
<job>/review/cuts.snapped.json
```

Report counts for `silent`, `quiet`, and `LOUD`. List every `LOUD` boundary.

**Gate 3 — Loud-boundary decision**

If any important boundary is `LOUD`, the owner listens to it or authorizes the proposed boundary.

Reason: the fade prevents a click but cannot prevent an unnatural mid-breath or visual jump.

#### 6. Draft rough cut

Render from the original, never the proxy:

```text
<job>/renders/drafts/<slug>--rough-cut-v01.mp4
```

Verify:

- Expected kept-range count.
- Duration against the cuts manifest.
- Audio presence.
- No empty output.
- Cut-boundary samples.
- First and last frames.

**Gate 4 — Rough-cut approval**

The owner confirms the structure before a large ProRes render or Final Cut handoff.

Reason: avoids spending time and disk on a technically high-quality render of the wrong edit.

#### 7. FCP handoff

Default for an edit likely to change in Final Cut:

```text
<job>/fcp/<slug>--adjustable.fcpxml
```

Use one clip per kept range. Include the original or relink instructions, cleaned transcript, captions if requested, and the boundary report.

Use a flattened ProRes file only when the owner prefers simplicity over adjustable cuts:

```text
<job>/fcp/media/<slug>--rough-cut-prores.mov
```

**Gate 5 — Handoff verification**

Parse the FCPXML, confirm all media references exist, and optionally open/import into a test library before declaring the kit complete.

Reason: an FCPXML file can exist while containing invalid or unresolvable references.

---

## 7. Migration

**Confidence: High for ordering; medium for smoke-test thresholds**

No step should delete anything. Every move requires owner approval.

### Step 1 — Freeze facts and tests

Before changing routing or paths:

1. Hash or snapshot all affected skills, agents, and pipeline code.
2. Record current absolute paths.
3. Save one known-good small ICF project and one known-good paper-edit fixture.
4. Record expected duration, resolution, streams, and representative frames.
5. Inspect whether current Final Cut libraries reference the ICF parent folder or pipeline projects.
6. Write the proposed `manifest.yaml`.
7. Define pass/fail smoke tests.

Archive snapshots to:

```text
/Users/eladtzur/.claude/archive/video-stack-snapshots/2026-07-pre-migration/
```

Nothing else may begin until both workflows can be reproduced from known fixtures.

**Rollback:** no state has changed; use the recorded current configuration.

### Step 2 — Establish authority without changing engines

Prerequisite: Step 1 fixtures and hashes exist.

1. Add the minimal global routing paragraph.
2. Revise `video-director` to include all current workflows and the canonical routing table.
3. Make HyperFrames explicitly subordinate.
4. Revise the three executor agents, especially the ICF agent’s FFmpeg-direct default.
5. Run routing-only test prompts in Hebrew and English.

Test concrete prompts such as:

- “תעשה מזה סרטון”
- “תחתוך את ההקלטה לפי הטקסט”
- “תוסיף כתוביות לסרטון הזה”
- “תכין אנימציה קצרה לגרף”
- “תהפוך את הוובינר לטקסט”

Each must choose exactly one top-level route.

**Rollback:** restore the snapshotted global file, skills, and agents.

### Step 3 — Create the workspace and use it for one pilot job

Prerequisite: routing tests select the correct workflow and no proven engine command has changed.

Create:

```text
/Users/eladtzur/DEV/video-work/
```

Add templates and links, but do not move old projects. Run one new, low-risk ICF pilot job through the standardized folder.

The engine may remain at its current path.

**Rollback:** stop using the new workspace. The original pipeline and existing projects remain untouched.

### Step 4 — Standardize manifests and adapters

Prerequisite: the pilot produces a master equal to or better than the known workflow and resumes correctly after interruption.

Add job manifests and path adapters so:

- ICF can accept an external job directory.
- Paper-edit writes artifacts into the standard layout.
- Existing transcripts can be reused by caption workflows.
- Final Cut handoff consumes a common manifest.

Do not extract or relocate the ICF engine yet.

**Rollback:** invoke the original commands against `pipeline/projects/<name>` and the original next-to-source `paper-edit/` layout.

### Step 5 — Consolidate shared services incrementally

Prerequisite: fixtures exist for transcription and FCPXML output.

Order:

1. Extract the transcription interface while keeping the old paper-edit script as a fallback.
2. Convert paper-edit to the shared interface.
3. Convert one caption workflow.
4. Convert media-pipeline batch transcription.
5. Extract the generic FCP handoff wrapper.
6. Convert ICF.
7. Convert paper-edit FCPXML.

At every conversion, compare:

- Transcript text and word timings.
- Render duration.
- Cut-boundary behavior.
- FCPXML parse and relink behavior.

**Rollback:** each caller retains a configuration switch pointing to its previous implementation until two real jobs pass.

### Step 6 — Archive redundant skills

Prerequisite:

- Global routing is proven.
- The manifest/audit command works.
- The retained workflows pass smoke tests.
- The owner approves the exact archive list.

Move the 11 entries to:

```text
/Users/eladtzur/.claude/archive/video-skills/2026-07-redesign/
```

Do not alter their contents.

Run the router audit after the move.

**Rollback:** move the archived directory or symlink back to its original exact path.

### Step 7 — Govern HyperFrames updates

Prerequisite: the retained HyperFrames set renders the fixture successfully.

Introduce the update wrapper and prohibit raw bundle updates in the video stack SOP. Test an update in a temporary snapshot, verify that reinstalled archived workflows are removed from discovery, and confirm the global router still wins.

**Rollback:** restore the pre-update snapshot.

### Step 8 — Consider engine relocation only later

Moving:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline/
```

to:

```text
/Users/eladtzur/DEV/video-engines/icf-video/
```

is explicitly deferred.

It should happen only if:

- External project paths work.
- No FCP library depends on old media paths.
- Vault notes and all skills are updated atomically.
- A compatibility symlink can preserve the old path.
- Both known-good fixtures pass from the new location.

The compatibility symlink would be:

```text
/Users/eladtzur/DEV/ICF/content/insurance-video-v1/pipeline
→ /Users/eladtzur/DEV/video-engines/icf-video
```

**Rollback:** restore the original directory and remove only the compatibility symlink after confirming the original is present.

### Irreversible or high-risk actions

No proposed filesystem migration is inherently irreversible because nothing is deleted. The high-risk effects are external references:

- Final Cut media relinks.
- Vault links and SOP paths.
- Generated FCPXML absolute paths.
- Cached project paths.
- HyperFrames updater overwriting local skill edits.
- Replacing transcript timing behavior.
- Voice/provider drift changing timing and sound.

The closest thing to irreversible is losing knowledge of which original media an existing FCP timeline referenced. That is why no legacy media or `.fcpbundle` should move before reference inspection and a recorded mapping.

## Explicit unknowns

1. Whether any current Final Cut library references media inside `insurance-video-v1/` or `pipeline/projects/`. Inspecting FCPXML exports or Final Cut’s relink information would settle it.
2. Whether `bin/make-ff.sh`, `bin/tts.py`, and `bin/ffrender.py` fully support project directories outside `pipeline/projects/`. A single external-path fixture run would settle it.
3. Whether `higgsfield` uses any China-hosted provider or sends owner material to a restricted processor. Its current provider endpoints and data-processing terms would settle it; until then it should remain archived.
4. Whether all caption workflows can consume the same word-level JSON without losing identity-specific features. A schema compatibility test against `embedded-captions` would settle it.
5. Whether the ICF FCPXML builder’s alpha-caption path is currently exercised successfully end to end. Importing a generated kit into a disposable Final Cut library would settle it.
6. Which of the legacy ICF MP4s are masters, proofs, or inputs to current timelines. Owner confirmation plus file metadata would settle it.
7. Whether the `website-to-hyperframes` target is functionally distinct from `website-to-video`. The inventory called it broken, but the symlink currently resolves; reading and comparing its target implementation would settle whether it is merely redundant.
8. The acceptable pixel/frame tolerance for comparing old and new renders during migration. One owner-reviewed fixture should establish that threshold.