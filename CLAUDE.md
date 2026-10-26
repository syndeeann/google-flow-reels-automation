# Google Flow Reels automation

This repo turns a queue of topics into short vertical videos made in Google Flow for the Facebook Page **Kwento: Kilabot** (Tagalog horror stories based on Filipino folklore).

**No owner approval: every video must pass the quality check** (`scripts/qc.py` + Claude's look at the contact sheet, RUNBOOK step 4b) and is then delivered as a ready-to-post kit. **Claude doesn't upload or publish** to Facebook/YouTube (browser file upload is blocked by safety controls); the owner posts. See `docs/RUNBOOK.md` steps 4b–7.

- Queue: `queue/topics.yaml` (status `ready` = produce next)
- Defaults: `config.yaml`
- **Setup status, decisions and next steps: `docs/HANDOFF.md`. Read it first when continuing setup.**
- Procedure: `docs/RUNBOOK.md`. Follow it exactly for "run the pipeline", "make the next Reel", or a scheduled run.
- Story + prompt rules: `docs/PROMPT_GUIDE.md` (Claude writes the stories: short 45–60 s Filipino horror with a twist)
- Captions/hooks for Facebook, Instagram, TikTok: `docs/CAPTION_GUIDE.md`
- Daily job: up to 3 videos per run, each quality-checked and delivered ready to post (`docs/RUNBOOK.md` → Daily run)
- Helper CLI: `python scripts/reels.py next | validate | render | finish | status`; editing: `python scripts/assemble.py <run_dir>` (built-in A/V sync check); quality gate: `python scripts/qc.py <run_dir>` — never deliver a video that fails it; Flow downloads: `scripts/flow_download.js`
- Run outputs: `output/<date>-<topic_id>/` (brief.json, prompts.json, prompts.md, caption.txt, run-log.md). Video files are not committed.

Flow has no API; generation happens by operating flow.google.com in the built-in browser of the Claude desktop app on the user's computer, signed in to the user's Google account (Google AI Pro). Clips are joined with ffmpeg in the workspace. The owner posts the videos to Facebook and YouTube.

Commit messages: short, imperative ("Prompts: aswang-sa-kabilang-bahay", "Awaiting approval: …", "Posted: …").
