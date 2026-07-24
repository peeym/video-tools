# Design Brief — Video Stack Architecture

Read `INVENTORY.md` in this same folder first. It is facts only. Nothing has been
changed yet and nothing may be changed by you.

## Your task

Design the target architecture for how one person's Claude Code installation should
be organized to do video work. Produce a proposal, not an implementation.

You are one of several independent reviewers working from the same inventory. Do not
try to guess what the others will say. Design what you actually think is right.

## What the owner asked for, verbatim

- "אני רוצה לעשות סדר בסקילים ובסוכנים" (I want to put the skills and agents in order)
- "ושתהיה תקיה יעילה שבה קלוד עובד על וידאו" (and to have an efficient folder where
  Claude works on video)
- "לחשוב על ארכיטקטורה טובה, לתכנן ועדיין לא לגעת. כשיהיה ברור אז לאחד הכל עם נוהל
  עבודה יעיל" (think about good architecture, plan and still do not touch. When it is
  clear, then unify everything with an efficient working procedure)
- Priority order, explicit: **"קודם תוצאה טובה, אחכ חיסכון בטוקנים, אחכ חיסכון בזמן"**
  (first a good result, then token saving, then time saving)

Note the priority order carefully. Output quality outranks cost. Do not propose
anything that trades video quality for a cheaper token bill. Cost matters only as a
tiebreaker between options of equal quality.

## What the owner actually ships

Hebrew-language video for a financial-coaching business and a facilitation business.
Concretely, from the inventory: 9:16 narrated explainers built from stills plus voice
plus burned Hebrew captions; rough cuts of his own recorded footage handed to Final
Cut Pro for finishing; course lessons; webinar and meeting recordings turned into
text. He knows Final Cut Pro well and does not know Apple Motion.

## Questions your proposal must answer

1. **Routing.** Two skills each claim "read this first" and one of them claims default
   status over all other installed video tools. What is the correct single entry point,
   and what exact mechanism keeps it authoritative as skills are added or updated later?
   A fix that works today but drifts the next time a bundle is installed is not a fix.

2. **Surface area.** 25 video skills exist. How many should there be? Give the specific
   keep / merge / archive verdict per skill, with your reason. Where you are unsure,
   say what evidence would settle it rather than guessing.

3. **The folder.** Design the working directory. Give the concrete tree. Answer: where
   does a new video job start, what does the per-job layout look like, where do shared
   assets live, where do finished renders go, how does a job get handed to Final Cut,
   and what happens to the five locations that currently hold video work. State
   explicitly which existing paths you would move and which you would leave in place,
   and what breaks if they move.

4. **Duplication.** Transcription has at least five implementations, captions five,
   TTS three, Final Cut handoff three. Which is canonical for each, and how do the
   others get retired or made to call the canonical one?

5. **Waking up.** The global instruction file has no video section, and a stored
   memory records that the owner does not type skill names. What is the minimum text
   that must exist in the global instruction file, and what belongs in a skill instead?
   Be specific about the boundary. Assume every line added to the global file is paid
   for on every single request in every project, forever.

6. **The procedure.** Describe the standard working procedure end to end for the two
   most common jobs: (a) a script becomes a finished 9:16 Hebrew explainer, (b) recorded
   footage becomes a rough cut ready for Final Cut. Name the approval gates and say why
   each one exists.

7. **Migration.** Order the work. What is step one, what must be true before step two,
   and what is the rollback if a step goes wrong. Flag anything irreversible.

## Constraints you may not violate

- Hebrew content stays on Claude. It is never routed to a cheaper or non-Claude model.
- China-hosted models are forbidden for anything of the owner's: his thinking, his
  business material, his clients, his unpublished content, his code that ships.
- Nothing is deleted. Retiring something means moving it to an archive folder or to
  `~/.Trash/`, and it must be asked about first.
- No resident background listeners. Passive, click-to-run triggers are preferred over
  LaunchAgents, fswatch, or Hammerspoon.
- Skills and config files are written in English.
- The three working engines described in the inventory are known to work and have
  produced finished videos. Treat "it currently works" as evidence with weight.

## Output format

Markdown. Lead with a one-paragraph statement of the architecture in plain language,
then answer the seven questions in order. Be concrete: name paths, name files, name
skills. Where you would delete or move something, say exactly what and exactly where to.

State your confidence per section, and list explicitly what you could not determine
from the inventory. A reviewer who flags an unknown is more useful than one who fills
it with a plausible guess.
