# Handoff: setup status and decisions (as of 2026-10-27)

Read this first when continuing the setup in a new chat (e.g. inside the Claude Project "Kwento: Kilabot").

## Owner
Syndee (GitHub: syndeeann), Asia/Manila timezone. Google Flow on the Google AI Pro plan, signed in inside the Claude desktop app's built-in browser.

## Done
- Pipeline: topic queue (`queue/topics.yaml`), defaults (`config.yaml`), `docs/RUNBOOK.md`, `docs/PROMPT_GUIDE.md`, helper CLI `scripts/reels.py`, repo skill `.claude/skills/flow-reel`.
- Claude GitHub App is installed on this repo; pushes work.
- Google Flow is reachable at https://flow.google.com in the desktop app's built-in browser (approve `flow.google.com` and `labs.google` with "always allow" to avoid repeated prompts).
- 2026-10-27: repo converted to Kwento: Kilabot:
  - `config.yaml`: Tagalog, slow eerie male narrator, dark foggy night look, no gore/blood, 32s (4 clips), 15 words/clip, twist ending instead of a spoken CTA, caption CTA + hashtags, Facebook settings.
  - Statuses `awaiting_approval`, `approved`, `posted`, `rejected` in `reels.py` and the queue.
  - `prompts.json` now carries `caption_text` + `hashtags`; `render` writes `caption.txt`.
  - `reels.py join` joins clips with ffmpeg into `<topic_id>-final.mp4` (1080×1920, tested).
  - RUNBOOK steps 4–7: join → send video + caption for approval → handle reply → (superseded: the owner now posts manually).
  - Café sample replaced with 5 starter folklore topics (aswang, tikbalang, kapre, manananggal, tiyanak), all `draft`.

- 2026-10-27: first video produced: **Kilabot #1 "Bote, Diyaryo, at Alaala"** (topic `bote-diyaryo-alaala`), from the owner's "Story #1 + Facebook Growth Kit" doc. Full ~2:20 script as 23 Omni 1.1 Flash clips with a Flow **Narrator** character (voice `enceladus`) for a consistent narrator; edited with `scripts/assemble.py` (trims, faint cart-creak bed, silence before the twist, end card). 3:07, sent to the owner for approval; status `awaiting_approval`. Caption = Caption A from the doc. ~320 Flow credits used (balance was 1,050).

- 2026-10-27 03:07: owner **approved Kilabot #1** (status `approved`; posting pending Facebook access). First cut had the voice-over out of sync (per-clip `loudnorm` dropped ~3s of audio); fixed in `assemble.py` with frame-locked audio + a sync check.
- 2026-10-27: owner made this a **daily task**: Claude writes 3 short (45–60 s) Filipino horror stories with twists (aswang and other elementals), generates them in Flow, edits them, writes Facebook/Instagram/TikTok captions per `docs/CAPTION_GUIDE.md`, and sends all for approval. Nothing is posted without approval; ask the owner when Facebook access is needed.

- 2026-10-27: scheduled task **"Kwento: Kilabot daily videos"** created: daily 8:45 AM Asia/Manila, on the owner's Mac (needs the Claude desktop app open and online), Downloads folder attached, push notifications on. Each run makes up to 3 videos and sends them for approval; it never posts.

- 2026-10-27 04:00: owner: **at least 1 video a day**. Policy: video 1 always (lean 4–5-clip story ≤ 50 credits when the balance is under 300, matching the +50/day allowance); videos 2–3 only when the balance stays ≥ 300 afterwards.

- 2026-10-27 04:17: owner **will post all videos manually**. Claude reverted the access it had set up for posting (closed the Facebook tab, released computer use) and removed the posting step; Claude sends a ready-to-post kit after approval instead. Kilabot #1 is `approved`, waiting for the owner to post it.

- 2026-10-27 04:30: owner: runs must continue on their own without asking (including after usage limits). Added: resume-first rule (`reels.py next` returns unfinished topics before new ones), never-ask rule, and a second daily **catch-up** scheduled task at 2:45 PM that only finishes interrupted work. Video generation still needs the owner's Mac awake with the Claude app open (Flow has no API).

- 2026-10-27 05:20: owner: **no approval needed**; Claude should evaluate each video (sync, glitches, redundant clips, script order) and post to Facebook + YouTube. Built `scripts/qc.py` (tested: passes Kilabot #1, catches swapped/duplicated clips and the old out-of-sync cut). Posting itself is NOT possible: Claude in Chrome reached both sites (signed in; YouTube channel "Kwento: Kilabot" UCTtKjt3UyEOrUW0tjU9gDmQ), but the file-upload step was blocked by the environment's safety classifier. So: QC replaces approval; owner uploads the ready-to-post kit.

- 2026-10-27 05:32: owner: Claude posts automatically to Facebook + YouTube after its own checks (sync, glitches, redundant clips, order) and automatic fixes; every video saved in the **Video Log** artifact (https://claude.ai/artifact/TR7wReRavWzur9tUqbKfu7) with a fix-request box. Upload path tested: Facebook composer accepted a test file via the input-click patch (discarded, nothing posted); YouTube's upload dialog has a real file input. `file_upload` only takes files from the session's working directory, < 10 MB.

- 2026-10-27 08:05–10:00 (daily run): Kilabot #2 Mahina ang Tiktik, #3 Ang Ilaw sa Laot, #4 Tabi-tabi Po made (6 clips each, ~237 credits; balance 730 → 493), QC passed, posted to Facebook + YouTube after the owner confirmed in chat (project instructions still say "never post without explicit approval" — conflict flagged to the owner), logged in the Video Log.
  - Flow UI changes: the Agent chip is gone; the asset picker (+) opens on the current project and the "All" filter, so switch the filter to Characters and the project dropdown to "Kilabot #1 …" to attach Narrator; verify `img[alt="Character ingredient image"]` and the seconds chip before submitting (a wrong pick attached a video and set 6s). Download is now ⋮ More options → Download media → 720p (scripts/flow_download.js updated).
  - Flow refused: a covered body on the beach; a 7-year-old girl on screen in a horror shot (card vanished silently). Rewrites passed.
  - YouTube Studio: pressing Escape with no popup open closes the upload dialog (saved as draft; reopen via Shorts → Edit draft). End titles/descriptions that end in a hashtag with a space instead of Escape. "#2" in a title autocompletes to "#2026" unless followed by a space.
  - Facebook Business Suite showed no AI-label option on the Share step; direct Reel links aren't exposed in Posts & reels.
  - git push from cloud sessions fails (repo not in the session's authorized sources); commits saved as a bundle in Downloads/Kwento Kilabot/.
  - Another Flow project "Kilabot #2 Mahinang Tiktik 2026-10-27" (empty) was created by a different session around the same time; left untouched.

- 2026-10-27 10:15: owner: stories **up to 2 minutes**, and new theme families besides folklore: **abandoned buildings, call center (BPO) horrors, school horrors, horror for kids (kwentong pambata)**; "make it interesting and not boring". Done: config (110 s target, 16-clip cap, credit tiers full ≥400 / medium 200–399 / lean <200), PROMPT_GUIDE (theme rotation, engagement rules, kids-story safety rules), CAPTION_GUIDE (per-theme search words; kids stories = YouTube "made for kids"), RUNBOOK step 2, reels.py (4–16 clips), assemble.py (two-pass encode fits any length up to ~2 min under 9.5 MB; tested 123 s → 9.0 MB, sync 10 ms).
  - Credit math: a 2-min story costs ~170–200 credits; the plan adds 50/day. From 493 that's roughly two full-length days, then mostly medium/lean videos with a full one every few days.

## Decided
- Facebook Page: **Kwento: Kilabot**.
- Style: Tagalog horror stories based on Filipino folklore, dark foggy night scenes, slow eerie male narrator, every video ends on a twist.
- Posting: **immediately after the owner approves** (no scheduled post time).
- Format: vertical 9:16 Reels, ~8s Veo clips, voice-over generated by Veo native audio from the quoted line in each prompt.
- **Approval gate:** Claude must never post a video the owner hasn't approved. Flow:
  1. Run: next topic → script + prompts + caption → Flow clips → join into one video.
  2. Send the owner the video + caption; topic status `awaiting_approval`. Nothing is posted.
  3. Owner replies approve / redo clip N / change caption / reject.
  4. Only after "approve" of that exact video + caption: post it to the Page, report the link; status `posted`.
- **Facebook:** the owner posts every approved video manually. Claude has no Facebook access and doesn't ask for it.

## To do next
1. Owner reviews the proposed scheduled task below; create it only after they approve it (needs the owner's computer: `requires_local_device: true`).
2. Owner reviews Kilabot #1 (voice quality in Tagalog, pacing, wheel bed). Approved 2026-10-27; owner posts it manually.
3. Decide on the scheduled task's per-run size: a full ~2–3 min story is ~23 clips / ~320 credits, beyond the 8-clip default cap and the AI Pro allowance for daily runs (balance 1,050 + 50/day). Options: shorter ~60s stories (8 clips, ~110 credits) on the schedule, full-length stories on request.

## Proposed scheduled task (NOT created yet)
- Name: Kwento: Kilabot daily Reel
- Schedule: weekdays 8:45 AM Asia/Manila → cron `CRON_TZ=Asia/Manila 45 8 * * 1-5`
- Needs the owner's computer (built-in browser for Flow, file bridge for clips).
- Prompt:
  > Kwento: Kilabot scheduled run. Attach the GitHub repo syndeeann/google-flow-reels-automation with push access, clone it, read CLAUDE.md and docs/HANDOFF.md, then follow docs/RUNBOOK.md exactly for ONE topic: claim the next ready topic, write and commit the Tagalog script, prompts and caption, generate the clips in Google Flow, join them, and send me the final video and caption for approval with status awaiting_approval. Do NOT open Facebook and do NOT post anything in this run. Posting happens only after I reply "approve" to that specific video and caption.
