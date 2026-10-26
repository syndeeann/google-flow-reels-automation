---
name: flow-reel
description: Produce the next Kwento: Kilabot Reel from queue/topics.yaml in Google Flow, handle the owner's approve / redo / caption / reject reply (the owner posts manually), or add/plan topics. Use for "make the next Reel", "run the Flow pipeline", "approve", or a scheduled run of this repo.
---

# Flow Reel (Kwento: Kilabot)

1. Read `docs/RUNBOOK.md` and follow it step by step.
2. Write scripts, prompts and captions by `docs/PROMPT_GUIDE.md` (Tagalog, Filipino folklore, foggy night, slow eerie male narrator, twist ending).
3. Never post to Facebook: the owner approves each video and posts it manually (RUNBOOK steps 5–7).
4. To add a topic the owner describes, append it to `queue/topics.yaml` with a short kebab-case `id`, `status: ready` (or `draft` if they say not yet), `folklore`, and any `notes` (e.g. a twist idea). Commit and push.
5. To produce a topic right now that isn't in the queue, add it as `ready` at the top of the list first, then run the runbook.
