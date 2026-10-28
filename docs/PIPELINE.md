# Kwento: Kilabot — the video pipeline and who does what

Decided by the owner on 2026-10-29. Every Kwento: Kilabot video goes through the same six specialists (skills from
https://github.com/syndeeann/custom-claude-skills), in this order. `docs/RUNBOOK.md` has the click-by-click
details for Flow, YouTube and Facebook; this file says **who owns each stage, what they hand on, and what the
next stage may reject.**

| # | Who | Skill | Job | Hands on |
|---|---|---|---|---|
| 1 | **Marites** | `storyteller` | Learns the concept, writes the horror story and the clip-by-clip script | script `.md` + `.prompts.json` → Senyorita |
| 2 | **Senyorita** | `ai-prompt-expert` | Turns the script into thorough, flawless Google Flow prompts | prompts `.md` + `.json` → Flow generation |
| 3 | Claude (runner) | — | Generates the clips in Flow and downloads them (RUNBOOK 3) | raw clips → Perpekto |
| 4 | **Perpekto** | `flow-clip-qa` | **Pass 1:** checks every clip, knowing the story | verdict per clip → Jaiman (or back to 3) |
| 5 | **Jaiman** | `video-editor` | Compiles the clips in the story's order into one video | final video + cut list → Perpekto |
| 6 | **Perpekto** | `flow-clip-qa` | **Pass 2:** checks the finished video | PASS → post; FAIL → back to Jaiman or 3 |
| 7 | Claude (runner) | — | Posts to **YouTube and Facebook**, only after Perpekto's pass 2 PASS (RUNBOOK 5) | links → Chelsea |
| 8 | **Chelsea** | `portfolio-updater` | Updates the portfolio with the posted video | live portfolio |

**Hard gates**
- Nothing reaches Flow until Marites's script and Senyorita's prompts both pass their lint and `reels.py validate`.
- Nothing is edited until Perpekto passes the clips (pass 1). Nothing is posted until Perpekto passes the final (pass 2).
  No PASS from Perpekto = no post, on either platform. A failed video is logged `failed` and never posted.
- Chelsea runs only after a video is actually posted (status `posted`). She never adds unposted or failed videos.
- Every skill checks, writes or edits; **the runner (Claude) is the only one that spends Flow credits and posts.**
- If a stage finds a problem that belongs to an earlier stage, it goes back there (see "Loops"); nobody patches
  another stage's work silently.

## Tell each skill the concept (the project brief)
Skills are project-independent: each one has a `kwento-kilabot` profile, but it still needs the story of this
project every time it is called. The runner **pastes this brief, plus its role block, into every skill call**
and tells the skill to use the `kwento-kilabot` profile.

> **Project: Kwento: Kilabot.** A Facebook Page + YouTube channel of Tagalog **horror stories** told by one calm
> off-screen narrator, as vertical 9:16 videos up to ~2 minutes made in Google Flow (Omni, Narrator character).
> Setting: dark foggy Philippine night, eerie, realistic, no gore or blood. Every story has a **twist in the last
> line**. It must never be boring: hook in the first 2 seconds, a mystery open early, every clip escalates, a
> midpoint turn, one quiet beat, then the twist. Theme families, rotated (never the same family twice in a row):
> Filipino folklore, abandoned buildings, call center (BPO) horrors, school horrors, kwentong pambata
> (spooky-but-safe for kids; no child on screen in a horror shot; YouTube "made for kids"). Stories are numbered
> "Kilabot #N". Adapt everything you do to this: horror, Tagalog, one narrator voice, a twist ending.

### Role block: Marites (storyteller)
- Read `docs/PROMPT_GUIDE.md` (story rules, theme families, kids-story safety) and `queue/topics.yaml`; continue the
  "Kilabot #N" numbering and avoid the creatures and twists of the last 6 stories.
- The runner gives you: theme family, clip count and length tier (≥400 credits → full ~2 min, 11–14 clips;
  200–399 → ~90 s, 8–9 clips; <200 → ~45 s, 4–5 clips). Per clip: 6 s ≤ 9 spoken words, 8 s ≤ 14, 10 s ≤ 18.
- Learn the concept, then write: the angle, the look anchors, one narration line per clip, and the twist line.
  Write the script into `video-projects/kwento-kilabot/script/NNN-slug.md`, run `script_lint.py` (no repeated words),
  export `NNN-slug.prompts.json`, push to the skills repo. Never invent a legend as "traditional" (use the Type and
  Notes lines).
- Also give the runner a one-line summary and the twist, for the queue and the captions.

### Role block: Senyorita (ai-prompt-expert)
- Input is Marites's script file, nothing else. Use her narration word for word and her look anchors verbatim.
- Platform: Google Flow, **Omni 1.1 Flash, Ingredients, 9:16, 720p, x1**; clip seconds 6, 8 or 10.
- Every narrated clip prompt must: start with the Narrator line ("The attached Narrator character is off-screen and
  does not appear; only his voice is heard as the voice-over."); contain the exact narration in quotes; state
  9:16; say nobody on screen moves their lips; end with "no subtitles, no on-screen text, no watermark, no logos,
  no gore, no blood". (These are what `reels.py validate` checks.)
- Faces away-only: people from behind, in silhouette or by their hands. Known Flow refusals to avoid: a second voice
  shouting, a covered body, a child on screen in a horror shot.
- Write `video-projects/kwento-kilabot/prompts/NNN-slug.md`, run `prompt_lint.py` with `--profile kwento-kilabot`
  and `--export-json`, push. Give each clip a **Review** line (what the clip must show), because Perpekto uses it.

### Role block: Perpekto (flow-clip-qa)
- Profile `kwento-kilabot`. **Know the story:** pass Marites's `NNN-slug.prompts.json` with `--script` (and the
  prompts file), so every clip is judged against the picture and line it is supposed to carry, in story order.
- **Pass 1 (raw clips):** one verdict per clip: right scene for its line; no text, subtitles, watermark or logo;
  no garbled faces or hands; characters consistent; foggy-night mood kept; narration present and not cut off;
  no repeated words; nobody lip-syncing the narrator (lip sheet). Report the cheapest fix per failing clip.
- **Pass 2 (final video + `edit.json`):** clips in the story's order, none missing, repeated or duplicated; voice-over
  in sync (≤ 60 ms); no black or frozen frames, no glitch at any join; video/audio length match; 720×1280, under
  9.5 MB (YouTube/Facebook upload limit for the runner); the end card reads correctly.
- Also run `python scripts/qc.py <run_dir>` (this repo's own gate); a failure in either one is a FAIL.
- Verdict and evidence only. Perpekto never regenerates, re-edits or posts.

### Role block: Jaiman (video-editor)
- Profile `kwento-kilabot`. **Know the story:** `plan --script NNN-slug.prompts.json` gives the clip order; never
  re-order the story. A clip missing or an extra take = stop and tell the runner.
- Trim each clip's unstable first/last half-second, keep the quiet beat and the pause before the twist, and land every
  narration line inside its own clip.
- Build with `scripts/assemble.py` (this project's finishing: frame-locked audio, end card, ≤ 9.5 MB) driven by
  the same `edit.json` (`n`, `start`, `end` in story order); then run `jaiman_edit.py check` on the result.
- Hand Perpekto the final video and `edit.json`, with what was and was not measured.

### Role block: Chelsea (portfolio-updater)
- Runs once the video is `posted`: `add --run-dir output/<date>-<topic_id>` (Stories studio, NEW badge for 7 days),
  then `publish`. Keeps the Kwento: Kilabot workflow on the portfolio the same as this file, and runs
  `sync-skills` when a skill changes. Reports pending manual analytics steps to the owner.

## Loops (who goes back to whom)
| Problem found | Goes back to | Fix |
|---|---|---|
| Script/prompt lint fails, repeated words, line too long for its clip | Marites / Senyorita | rewrite that line or prompt, re-lint |
| A clip shows the wrong scene, text, garbled face/hands, dubbing, or no narration (pass 1) | Runner → Flow | regenerate **only that clip** (softened if refused), re-download, Perpekto re-checks that clip |
| A line is too long for its clip (Jaiman) | Marites | shorten the line; regenerate that clip |
| Clips out of order, bad trim, out of sync, glitch at a join (pass 2) | Jaiman | fix `edit.json`, rebuild, Perpekto re-checks |
| Pass 2 fails because of a bad clip | Runner → Flow → Perpekto pass 1 | regenerate, re-check, re-edit |

At most 2 fix rounds per stage, within the credit cap. Still failing: `reels.py finish <topic_id> failed "<what>"`,
log it in the Video Log, do not post, say which clip and why.

## What each hand-off looks like
- Marites → Senyorita: `video-projects/kwento-kilabot/script/NNN-slug.md` and `.prompts.json` in the skills repo.
- Senyorita → runner: `video-projects/kwento-kilabot/prompts/NNN-slug.md` and `.json` in the skills repo.
- Runner → this repo: `python scripts/skills_bridge.py import <run_dir> --script <…prompts.json> --prompts <…json>`
  fills the run's `prompts.json` (clips, seconds, narration, prompts) from the two files; the runner then adds the
  captions (`docs/CAPTION_GUIDE.md`) and runs `reels.py validate` and `render`.
- Jaiman → Perpekto: `<run_dir>/<topic_id>-final.mp4` and `<run_dir>/edit.json`.
- Runner → Chelsea: the run folder with `run-log.md` ending in status `posted`.

## Setup each run needs
Attach with push access: `syndeeann/google-flow-reels-automation`, `syndeeann/custom-claude-skills` (Marites and
Senyorita save to it) and `syndeeann/my-portfolio` (Chelsea publishes to it). If a skill is not installed in the
session, read its `skills/<name>/SKILL.md` from the skills repo and follow it with its own scripts.
