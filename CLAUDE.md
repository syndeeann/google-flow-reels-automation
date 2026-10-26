# Google Flow Reels automation

This repo turns a queue of topics into short vertical videos (Reels / TikTok / Shorts) made in Google Flow.

- Queue: `queue/topics.yaml` (status `ready` = produce next)
- Defaults: `config.yaml`
- Procedure: `docs/RUNBOOK.md`. Follow it exactly for "run the pipeline", "make the next Reel", or a scheduled run.
- Prompt rules: `docs/PROMPT_GUIDE.md`
- Helper CLI: `python scripts/reels.py next | validate | render | finish | status`
- Run outputs: `output/<date>-<topic_id>/` (brief.json, prompts.json, prompts.md, run-log.md). Video files are not committed.

Flow has no API; generation happens by operating flow.google.com in the built-in browser of the Claude desktop app on the user's computer, signed in to the user's Google account (Google AI Pro).

Commit messages: short, imperative ("Prompts: ube-latte", "Generated: ube-latte").
