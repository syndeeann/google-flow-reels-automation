---
name: flow-reel
description: Produce the next vertical Reel from queue/topics.yaml in Google Flow, or add/plan topics. Use for "make the next Reel", "run the Flow pipeline", or a scheduled run of this repo.
---

# Flow Reel

1. Read `docs/RUNBOOK.md` and follow it step by step.
2. Write scripts and prompts by `docs/PROMPT_GUIDE.md`.
3. To add a topic the user describes, append it to `queue/topics.yaml` with a short kebab-case `id`, `status: ready` (or `draft` if they say not yet), and any overrides they gave. Commit and push.
4. To produce a topic right now that isn't in the queue, add it as `ready` at the top of the list first, then run the runbook.
