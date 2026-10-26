# Google Flow Reels automation

This repo turns a queue of topics into short vertical videos made in Google Flow for the Facebook Page **Kwento: Kilabot** (Tagalog horror stories based on Filipino folklore).

**Never post to the Facebook Page without the owner's explicit approval of that specific video and caption.** See the approval gate in `docs/RUNBOOK.md` (steps 5–7).

- Queue: `queue/topics.yaml` (status `ready` = produce next)
- Defaults: `config.yaml`
- **Setup status, decisions and next steps: `docs/HANDOFF.md`. Read it first when continuing setup.**
- Procedure: `docs/RUNBOOK.md`. Follow it exactly for "run the pipeline", "make the next Reel", or a scheduled run.
- Prompt rules: `docs/PROMPT_GUIDE.md`
- Helper CLI: `python scripts/reels.py next | validate | render | join | finish | status`
- Run outputs: `output/<date>-<topic_id>/` (brief.json, prompts.json, prompts.md, caption.txt, run-log.md). Video files are not committed.

Flow has no API; generation happens by operating flow.google.com in the built-in browser of the Claude desktop app on the user's computer, signed in to the user's Google account (Google AI Pro). Clips are joined with ffmpeg in the workspace. Posting goes through Claude in Chrome (the owner's Chrome, signed in to Facebook) via Meta Business Suite, only after approval.

Commit messages: short, imperative ("Prompts: aswang-sa-kabilang-bahay", "Awaiting approval: …", "Posted: …").
