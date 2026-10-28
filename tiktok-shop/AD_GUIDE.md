# Writing TikTok Shop affiliate ads: product analysis, script, Flow prompts, captions

Every run makes ads for **2 products** from the owner's TikTok Shop showcase. Each ad is a **62–75 s** vertical video in natural **Taglish**, realistic UGC style ("a friend showing you something she actually uses"), ending with a nudge to the **yellow basket** where the affiliate product is attached.

## 1. Analyze the product (write `analysis` in prompts.json before any script)
Work only from the product listing (title, photos, description, specs, variants, price, reviews summary if shown). Record:
- **What it is and what it does**, in one plain sentence.
- **Who buys it** (e.g. busy moms, students in dorms, riders, small-condo renters, OFW families, pet owners).
- **The real-life problem** it solves in a Filipino setting (brownouts, humid weather, small spaces, commute, rainy season, tight budget, kids, pets).
- **How it is actually used**, step by step (open, attach, press, wipe, charge…), and the **moment it pays off** (the visible result).
- **3 concrete selling points** that the listing itself supports (size, capacity, material, battery, washable, foldable, included items, price vs. alternatives).
- **Exact look:** color, shape, size relative to a hand, logo/markings, packaging. This goes word for word into every prompt that shows the product (the **product sheet**).
- **Risks:** anything the listing doesn't prove. Don't claim it.

## 2. Pick the angle (one per ad; record it as `angle`)
Choose the angle that shows the product's use most clearly, and don't repeat the angle used for the same product before (`products.yaml → ads`):
- **Problem → solution:** show the annoying situation, then the product fixing it.
- **Day-in-the-life:** the product used naturally across a morning / commute / home routine.
- **Demo / how-to:** "Ganito siya gamitin" — 3 steps, then the result.
- **Before / after (only for visible, honest results)** — e.g. a tidy drawer, a dry shoe rack. Never for health, weight, skin or medical results.
- **"3 reasons why"**: three use cases, one per beat.
- **Gift idea / budget find:** who to give it to and why it's worth the price.

## 3. Script shape (62–75 s, about 70–90 spoken words in total — the per-clip caps in §4 set the ceiling; hero clips carry no words)
1. **Hook (clip 1, first 2 s spoken + a moving visual):** a relatable pain or curiosity — "Sino dito ang laging naiinis kapag…", "Hindi ko alam na kailangan ko pala 'to hanggang…", "Ito na yung pinaka-useful na nabili ko for under ₱300." Name the product category early (TikTok transcribes audio for search).
2. **Problem / context (1 clip).**
3. **Demo (2–4 clips):** the real usage steps from the analysis, one action per clip, hands and product clearly visible.
4. **Hero shots (`hero_clips_per_ad`, Veo 3.1 Fast, no voice-over):** slow close-up of the product working — texture, the result, the satisfying moment. Ambient/product sound only.
5. **Proof / selling points (1–2 clips):** the 3 points, said simply.
6. **Close (last narrated clip):** a soft call to action — "Naka-link siya sa yellow basket, check niyo yung price." Then the end card.

**Honesty rules (TikTok Shop + plain decency):**
- Only claims the listing supports. No invented numbers, awards, discounts, "sold out soon", or prices unless read from the listing that day (prices change — prefer "check the price sa yellow basket").
- **No fake testimonials:** the host demonstrates and recommends; she doesn't claim months of personal results, and never says she's a doctor, expert, or a real customer.
- No health, medical, weight-loss, skin-whitening or "cure" claims; no comparisons naming other brands; no copyrighted music, characters or celebrity likeness.
- Children may appear only incidentally and fully clothed in a family setting; never as the focus of a beauty/body product.
- Restricted/unsafe categories (weapons, adult products, supplements with health claims, vapes): mark the product `skip` with a note instead of making an ad.

### Shared quality rules (owner, 2026-10-28 — same as Kwento: Kilabot)
- **No repeated words** in the voice-over: never the same word twice in a row or twice in one clip's line, never the same two-word phrase in two clips; vary any word used in 3+ clips. `ads.py validate` and `qc.py` enforce it (`scripts/repeats.py`).
- **No dubbing:** only the person who is actually speaking may move their lips — the on-screen host, in sync. Bystanders, and anyone on screen while the host is off-screen, keep their lips closed. `ads.py validate` requires a lips sentence in every narrated prompt; in QC look at `check/lip_sheet.png` and fail any clip where the wrong person's mouth moves or the host's lips don't match the words.

## 4. Clip plan and timing
- **Narrated clips (Omni 1.1 Flash, Ingredients mode, Ate Host character attached), with a safety margin so lines are never cut off:** ≤ 8 words → 6 s, 9–12 → 8 s, 13–16 → 10 s. Never more than 16 words.
- **Hero clips (Veo 3.1 Fast, 8 s):** `"hero": true`, `"voiceover": ""`. No narration, so the narrator's voice never changes model mid-ad.
- Typical 68 s ad: 6 narrated clips (8/8/10/8/10/8 s ≈ 52 s) + 2 hero clips (8 s each) ≈ 68 s before trims; plan **≥ 66 s of raw clips** so the edit stays above 60 s. That is about 70–90 spoken words in total.
- Put hero clips where the product is first shown working and right before the close.

## 5. Flow prompts — QC built in, right the first time
The quality check (`qc.py` + the visual review) rejects: lines cut off or missing, out-of-sync or mismatched audio, garbled hands or faces, a product that looks wrong or morphs, text/watermarks, black or frozen frames, wrong scenes, and clips that look like another clip. **Every prompt is written to prevent each of these before any credit is spent** — recreating a clip costs credits, so a clip that needs recreating is a prompt that was written wrong. Before writing, read `tiktok-shop/PROMPT_LESSONS.md` and apply every lesson.

**Prompt order** (every prompt stands alone; the model doesn't remember other clips):
1. `Vertical 9:16 video.` + the host line:
   - host on screen: `The attached Ate Host character is <ads.host_sheet>; her voice is the voice-over, speaking to camera like a friend. Only her lips move, in sync with her words; anyone else on screen keeps their lips closed.`
   - host off screen (hands-only demo): `The attached Ate Host character is off-screen; only her voice is heard as the voice-over. Only her hands appear. Nobody on screen moves their lips.`
   - hero clip: no host line, nothing attached.
2. **Product sheet** word for word in every clip that shows the product, + `exactly as in the attached product photo` when the photo is attached.
3. **One shot, one action** for these seconds: the clip's `shot` (close-up, medium, wide, overhead, macro, POV, over-the-shoulder) + one simple, slow, physically plausible action. No "then … then …" chains.
4. Setting/light: `ads.look` + the scene.
5. Audio: `Voice-over in Taglish (<ads.narrator>): "<exact line>"` + 1–2 natural sounds. Hero clips: sounds only.
6. **Quality clauses** from `config.yaml → ads.quality`, word for word:
   - every clip: `all` + `text`
   - narrated: `speech`; hero: `hero`
   - clip shows the product: `product`; hands visible: `hands`; host on screen: `face`
7. Negatives last: `ads.negatives`.

**Rules that prevent each QC failure:**
| QC failure | Prevented in the prompt by |
|---|---|
| line cut off / no narration heard | safety-margin word caps (§4); the `speech` clause (half-second lead-in, finish 1 s early); short sentences; numbers written as words |
| voice-over out of sync / wrong voice | one speaker only (`no other voices`); host always via the attached character; no dialogue from other people |
| garbled hands | hands do one simple, slow action (hold, slide, press, pour, place, wipe); `hands` clause. Avoid typing, writing, tying, sewing, threading, knitting, shuffling, counting money, playing instruments, and fingers interlocking with small parts |
| garbled or changing face | host on screen only in medium/close shots facing camera, `host_sheet` word for word, `face` clause; hands-only demos when possible |
| product looks wrong / morphs | product photo attached + product sheet word for word + `product` clause; the product stays whole and in view; no transforming actions the listing doesn't show (folding, unfolding, assembling) unless they are the product's real feature, shown slowly |
| text or watermark | `text` clause; never ask for signs, labels that read, screens, menus, posters, newspapers, price tags, packaging close-ups with writing |
| black / frozen frames, jump cuts | `all` clause (one continuous shot); a moving camera or subject in every clip (slow push-in, slow pan, gentle handheld) |
| wrong scene | the visual described concretely (place, light, object positions), not as a mood |
| redundant clip | every clip gets a different `shot` from the clip before it and a different action; no two clips share the same shot + visual |

`python scripts/ads.py validate <run_dir>` refuses prompts that break these rules (missing clauses, words over the cap, risky actions or text-prone objects, repeated shots, missing product sheet or host sheet) — fix and re-validate until OK before generating anything.

**Product look must match reality:** attach the product's main listing photo as an ingredient in Flow whenever possible (RUNBOOK step 4) and describe it exactly. Reject any clip where the product's shape, color, logo or size is wrong — that misrepresents what the buyer gets.

## 6. Captions (TikTok)
- **Line 1:** hook + search words (category + use: "portable fan para sa commute", "kitchen organizer small space").
- **Line 2:** the main benefit in one sentence.
- **Line 3:** a genuine question ("Ano pinaka-hassle sa kusina niyo?"). No "like/share/tag" bait.
- 3–5 hashtags: 1–2 broad (`#TikTokShopPH #TikTokMadeMeBuyIt`) + 2–3 specific to the product/use.
- ≤ 300 characters total. Don't put prices in the caption.
- Add an `#ad`-style disclosure only if TikTok's own commercial-content toggle isn't available; normally the yellow basket + toggle disclose the affiliate link.

## 7. prompts.json
```json
{
  "title": "<Product short name> — <angle>",
  "product_id": "<products.yaml id>",
  "analysis": {"what": "…", "buyer": "…", "problem": "…", "usage_steps": ["…"], "payoff": "…",
               "selling_points": ["…", "…", "…"], "product_sheet": "…", "do_not_claim": ["…"]},
  "angle": "problem-solution",
  "narrator": "<exactly config ads.narrator>",
  "clips": [
    {"seconds": 8, "hero": false, "host": "off_screen", "shows_product": true, "hands": true,
     "shot": "close-up", "voiceover": "…", "dialogue": "", "visual": "…", "prompt": "…"},
    {"seconds": 8, "hero": true,  "host": "none", "shows_product": true, "hands": false,
     "shot": "macro", "voiceover": "",  "dialogue": "", "visual": "…", "prompt": "…"}
  ],
  "captions": {"tiktok": "<full caption exactly as posted>", "pinned_comment": "<optional, a question>"},
  "end_card": "Tap the yellow basket\npara makita ang presyo"
}
```
Per clip: `host` = `on_screen` | `off_screen` | `none`; `shows_product`, `hands` (hands visible) and `shot` drive which quality clauses `validate` requires. `python scripts/ads.py validate <run_dir>` checks length, word caps, hero clips, prompt structure, the quality clauses and captions before any credits are spent.

## Example narrated clip (demo, hands only)
```
Vertical 9:16 video. The attached Ate Host character is off-screen; only her voice is heard as the voice-over. Only her hands appear. A compact white 3-tier plastic spice rack with pull-out drawers and rounded edges, about the width of two hands, exactly as in the attached product photo. Close-up, gentle handheld: her hand slowly slides the middle drawer out, showing neat rows of small spice jars inside. Bright natural daylight, real Filipino home or everyday location, handheld smartphone-style UGC camera, realistic skin and hands, true-to-life product colors and scale, shallow depth of field, crisp detail, small Filipino condo kitchen with a plain tiled backsplash. Voice-over in Taglish (warm, friendly, conversational Filipina woman in her late 20s, natural Taglish, upbeat but not shouty, like a friend recommending something she really uses): "Dati, kalat-kalat yung spices ko. Ngayon, isang hila lang, kita mo na lahat." Soft slide of the drawer, faint kitchen ambience. One continuous shot with no cuts, no transitions and no sudden zooms. Absolutely no text, letters, numbers, captions or watermarks appear anywhere in the frame. She begins speaking after a brief half-second pause and finishes the whole line at a calm, natural pace about one second before the clip ends; no other voices. The product keeps exactly the same shape, colour, size and markings for the whole clip and never morphs, bends, melts or changes. Natural, anatomically correct hands with five fingers each, moving slowly and simply with a realistic grip. No subtitles, no on-screen text, no watermark, no logos other than what is printed on the product itself, no distorted hands, no extra fingers, no morphing product.
```
