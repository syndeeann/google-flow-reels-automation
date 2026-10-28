# TikTok Shop affiliate ads

A second pipeline in this repo, separate from Kwento: Kilabot. Every day Claude:

1. reads your **TikTok Shop showcase** (your Chrome, signed in) and keeps `products.yaml` in sync
2. picks **2 products** (new ones first, best commission per sale; restricted categories skipped)
3. studies each listing — what it does, who buys it, how it's used in real Filipino life — and picks an ad angle
4. writes a **62–75 s Taglish** UGC-style script and Flow prompts (`AD_GUIDE.md`)
5. generates the clips in **Google Flow** on your computer: Omni 1.1 Flash with the **Ate Host** character for narrated clips, **Veo 3.1 Fast** for product hero shots
6. edits them with `scripts/assemble.py` (voice-over locked to picture, sync-checked) and runs **the same quality check as the Kilabot videos** — `scripts/qc.py` + Claude's visual review of the contact sheet, automatic fixes (up to 2 rounds) — plus the 60 s minimum and a product-accuracy check. An ad that fails can't be sent or posted.
7. sends you both videos and captions — **nothing is posted**
8. when you reply **`approve <ad_id>`**, posts that exact video to TikTok with the product in the **yellow basket**

Replies: `approve <ad_id>` · `approve both` · `redo clip <n> of <ad_id>: …` · `change caption <ad_id>: …` · `reject <ad_id>: …`

Files: `config.yaml` (defaults), `products.yaml` (ledger), `RUNBOOK.md` (procedure), `AD_GUIDE.md` (analysis/script/prompt/caption rules), `output/<date>-<ad_id>/` (one folder per ad; video files are not committed). Finished videos: `~/Downloads/TikTok Shop Ads/`.

Helper: `python scripts/ads.py new <product_id> | validate <run_dir> | render <run_dir> | length <run_dir> | qc <run_dir> [fix note] | review <run_dir> pass|fail [notes] | finish <ad_id> <status> [note] | status`

Needs: the Claude desktop app open on your computer at run time (Flow has no API), Google Flow signed in in its browser, Claude in Chrome connected with TikTok signed in.
