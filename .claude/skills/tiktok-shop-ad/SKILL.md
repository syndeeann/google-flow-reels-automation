---
name: tiktok-shop-ad
description: Make TikTok Shop affiliate video ads (from the affiliate link the owner sends; 60s+, Taglish, Google Flow), send them for approval, and post an approved ad to TikTok with the product in the yellow basket. Use for "make today's ads", the "TikTok Shop daily ads" scheduled run, or the owner's approve / redo / change caption / reject replies about an ad id.
---

# TikTok Shop affiliate ads

0. **Start from the owner's affiliate link**: read name, photos, description and specs from the listing (RUNBOOK "Product input"); don't read the showcase. No link yet → ask for it.
1. Read `tiktok-shop/RUNBOOK.md` and follow it step by step. Defaults: `tiktok-shop/config.yaml`. Ledger: `tiktok-shop/products.yaml`.
2. Analyze each product and write scripts, prompts and captions by `tiktok-shop/AD_GUIDE.md` (honest claims only, Ate Host narrator, Veo 3.1 Fast hero clips without voice-over). **Write the QC rules into every prompt (AD_GUIDE §5) and apply `tiktok-shop/PROMPT_LESSONS.md`, so Flow's clips pass QC the first time** — recreations cost credits. Generate the 2-clip pilot first (RUNBOOK 5).
3. Quality check exactly like Kwento: Kilabot (RUNBOOK step 7): `ads.py qc` (runs `scripts/qc.py` + the 60 s rule) and `ads.py review` (your look at the contact sheet, incl. product accuracy); fix the cheapest way first (re-cut, re-download, trim); recreate a clip only when its generation is flawed, via `ads.py recreate` (capped, records a lesson). `ads.py finish` refuses awaiting_approval/approved/posted unless both passed on the exact file.
4. Reuse the shared tools unchanged: `scripts/assemble.py` (sync-locked edit), `scripts/qc.py` (quality gate); ad bookkeeping with `scripts/ads.py`; Flow downloads with `scripts/flow_download_ads.js`.
5. **Never post without the owner's approval of that exact video and caption.** Owner replies:
   - `approve <ad_id>` / `approve both` → `ads.py finish <ad_id> approved "…"`, then RUNBOOK step 8 (post with the product in the yellow basket).
   - `redo clip <n> of <ad_id>: …` → regenerate that clip in the ad's Flow project, re-edit, full QC again (step 7), send again (status `awaiting_approval`).
   - `change caption <ad_id>: …` → update `captions.tiktok`, `ads.py render`, send the new caption for approval.
   - `reject <ad_id>: …` → `ads.py finish <ad_id> rejected "<reason>"`.
6. Kwento: Kilabot replies (`approve`, `redo clip x of N` about a Kilabot story) belong to the `flow-reel` skill, not this one. Ad ids look like `<product-id>-<n>`.
