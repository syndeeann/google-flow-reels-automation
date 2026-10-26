# google-flow-reels-automation

Automated short vertical videos (Reels / TikTok / Shorts) made with **Google Flow** (Veo) and written by **Claude**.

On a schedule, Claude takes the next topic from the queue and does the following:
1. writes a hook-first script in 8-second beats
2. writes one 9:16 Veo prompt per clip, with the voice-over line inside, so Veo generates the narration as native audio
3. validates and commits the script and prompts here
4. opens Google Flow in the Claude desktop app's browser (signed in to your account), generates the clips, and downloads them
5. marks the topic done and pushes a run log

## How to use

**Add a video:** edit `queue/topics.yaml` and add a topic with `status: ready`:

```yaml
  - id: rainy-day-promo
    status: ready
    topic: "Rainy-day 2-for-1 on hot drinks"
    cta: "Show this video at the counter"
    length_seconds: 15
```

You can also just tell Claude: "add a Reel about … to the queue".

**Change defaults:** edit `config.yaml` (length, narrator voice, visual style, credit cap).

**Check the queue:** `python scripts/reels.py status`

**Results:** `output/<date>-<topic_id>/prompts.md` has the script and every prompt (handy for pasting into Flow manually). The video clips are saved to your computer's Downloads folder.

## Requirements
- Google AI Pro/Ultra with access to Flow at flow.google.com
- The Claude desktop app open on your computer at schedule time, with flow.google.com allowed in its browser
- Python 3.9+ and `pip install -r requirements.txt` (only for the helper script)

If the computer is off at schedule time, the run still writes and commits the script and prompts, and marks the topic `prompts_only`. Set it back to `ready` to generate later.

## Layout
```
config.yaml             defaults
queue/topics.yaml       the queue
docs/RUNBOOK.md         step-by-step procedure Claude follows
docs/PROMPT_GUIDE.md    script & prompt rules
scripts/reels.py        queue + validation helper
output/                 one folder per run
.claude/skills/flow-reel  skill for working in this repo
```
