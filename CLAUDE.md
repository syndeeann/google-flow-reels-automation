# Google Flow Reels automation

This repo turns a queue of topics into short vertical videos made in Google Flow for the Facebook Page **Kwento: Kilabot** (Tagalog horror stories based on Filipino folklore).

**Six specialists make every video (owner, 2026-10-29): `docs/PIPELINE.md`.** Marites (`storyteller`) writes the story and script → Senyorita (`ai-prompt-expert`) writes the Flow prompts → Claude generates the clips in Flow → Perpekto (`flow-clip-qa`) checks every clip against the story → Jaiman (`video-editor`) compiles them in story order → Perpekto checks the finished video → only on a Perpekto PASS does Claude post to **YouTube and Facebook** → Chelsea (`portfolio-updater`) updates the portfolio. Skills come from https://github.com/syndeeann/custom-claude-skills; tell each one the project concept (PIPELINE.md has the brief and a role block per skill). No Perpekto PASS = no post, on either platform. No other owner approval step (standing approval, owner 2026-10-28). Then Claude **saves it in the Video Log artifact** (RUNBOOK 5b), where the owner can request corrections.

- Queue: `queue/topics.yaml` (status `ready` = produce next)
- Defaults: `config.yaml`
- **Setup status, decisions and next steps: `docs/HANDOFF.md`. Read it first when continuing setup.**
- Procedure: `docs/RUNBOOK.md`. Follow it exactly for "run the pipeline", "make the next Reel", or a scheduled run.
- **Pipeline and roles: `docs/PIPELINE.md`** (who owns each stage, the horror-story brief to give each skill, hand-offs, loops). Bridge: `python scripts/skills_bridge.py import <run_dir> --script … --prompts …`.
- Story + prompt rules: `docs/PROMPT_GUIDE.md` (Claude writes the stories: short 45–60 s Filipino horror with a twist)
- Captions/hooks for Facebook, Instagram, TikTok: `docs/CAPTION_GUIDE.md`
- Daily job: up to 3 videos per run, each quality-checked, posted to Facebook + YouTube, and saved in the Video Log (`docs/RUNBOOK.md` → Daily run)
- Helper CLI: `python scripts/reels.py next | validate | render | finish | status`; editing: `python scripts/assemble.py <run_dir>` (built-in A/V sync check); quality gate: `python scripts/qc.py <run_dir>` — never deliver a video that fails it; Flow downloads: `scripts/flow_download.js`
- Run outputs: `output/<date>-<topic_id>/` (brief.json, prompts.json, prompts.md, caption.txt, run-log.md). Video files are not committed.

Flow has no API; generation happens by operating flow.google.com in the built-in browser of the Claude desktop app on the user's computer, signed in to the user's Google account (Google AI Pro). Clips are joined with ffmpeg in the workspace. Posting: Claude in Chrome (owner's Chrome) → Meta Business Suite + YouTube Studio.

## Second pipeline: TikTok Shop affiliate ads (`tiktok-shop/`)
Separate from Kwento: Kilabot — different rules. On demand (owner 2026-10-28, no schedule): the owner sends each product's affiliate link; Claude reads the listing from it (no showcase reading) → 60–75 s Taglish UGC ads made in Flow (Omni + Ate Host for narration, Veo 3.1 Fast hero shots) → `assemble.py` → the same quality check as Kilabot (`qc.py` + visual review + auto-fix, via `ads.py qc` / `ads.py review`, QC-gated statuses) → sent to the owner. **Posting needs the owner's approval of each ad** (`approve <ad_id>`), then it's posted to TikTok with the product in the yellow basket. Procedure: `tiktok-shop/RUNBOOK.md`; writing rules: `tiktok-shop/AD_GUIDE.md`; helper: `python scripts/ads.py`; skill: `.claude/skills/tiktok-shop-ad`. Both pipelines share Flow credits; ads never spend below `tiktok-shop/config.yaml → flow.kilabot_floor`.

Commit messages: short, imperative ("Prompts: aswang-sa-kabilang-bahay", "Awaiting approval: …", "Posted: …").
