# google-flow-reels-automation

Automated vertical Reels for the Facebook Page **Kwento: Kilabot** — Tagalog horror stories based on Filipino folklore — made with **Google Flow** (Veo) and written by **Claude**.

On a schedule, Claude takes the next topic from the queue and does the following:
1. writes a Tagalog horror script in 8-second beats: hook, build, twist ending
2. writes one 9:16 Veo prompt per clip (dark foggy night, slow eerie male narrator as Veo native audio) and a Facebook caption
3. validates and commits the script, prompts and caption here
4. opens Google Flow in the Claude desktop app's browser (signed in to your account), generates the clips, and downloads them
5. joins the clips into one video and sends it to you with the caption — **nothing is posted yet**
6. when you reply **approve**, posts that exact video + caption to the Page via Meta Business Suite in your Chrome, and sends you the link (or: redo clip N / change caption / reject)

## How to use

**Add a video:** edit `queue/topics.yaml` and add a topic with `status: ready`:

```yaml
  - id: duwende-sa-punso
    status: ready
    topic: "Isang batang nakatapak sa punso at simula noon may kasama na siyang hindi nakikita"
    folklore: "Duwende"
    notes: "Twist idea: ..."
    length_seconds: 32
```

You can also just tell Claude: "add a story about the white lady to the queue".

**Change defaults:** edit `config.yaml` (length, narrator voice, visual style, caption CTA/hashtags, credit cap, Facebook Page).

**Check the queue:** `python scripts/reels.py status`

**Results:** `output/<date>-<topic_id>/prompts.md` has the script and every prompt (handy for pasting into Flow manually). `caption.txt` has the caption. Clips go to your Downloads folder; the joined video to `Downloads/Kwento Kilabot/`.

## Requirements
- Google AI Pro/Ultra with access to Flow at flow.google.com
- The Claude desktop app open on your computer at schedule time, with flow.google.com allowed in its browser
- Claude in Chrome connected, with your Chrome signed in to Facebook (for posting after approval)
- Python 3.9+ and `pip install -r requirements.txt` (only for the helper script); ffmpeg for joining clips

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
