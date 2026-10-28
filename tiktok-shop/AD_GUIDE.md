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

## 3. Script shape (62–75 s, about 80–105 spoken words in total — the per-clip caps in §4 set the ceiling; hero clips carry no words)
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

## 4. Clip plan and timing
- **Narrated clips (Omni 1.1 Flash, Ingredients mode, Ate Host character attached):** ≤ 9 words → 6 s, 10–14 → 8 s, 15–18 → 10 s. Never more than 18 words (the end gets cut off). Taglish is spoken a little faster, but keep to these caps.
- **Hero clips (Veo 3.1 Fast, 8 s):** `"hero": true`, `"voiceover": ""`. They carry no narration so the narrator's voice never changes model mid-ad.
- Typical 68 s ad: 6 narrated clips (8/8/10/8/10/8 s ≈ 52 s) + 2 hero clips (8 s each) ≈ 68 s before trims; trims usually take ~0.5–1 s per clip, so plan **≥ 66 s of raw clips** to stay above 60 s after editing.
- Put hero clips where the product is first shown working and right before the close.

## 5. Flow prompts
Every prompt stands alone (the model doesn't remember other clips). Order:
1. `Vertical 9:16 video.` + the host line:
   - host on screen: `The attached Ate Host character is the woman in this scene (use her look); her voice is the voice-over, speaking to camera like a friend.`
   - host off screen (hands-only demo): `The attached Ate Host character is off-screen; only her voice is heard as the voice-over. Only her hands appear.`
   - hero clip: no host line, nothing attached.
2. **Product sheet** (word for word, every clip that shows the product) + "exactly as in the attached product photo" when the photo is attached.
3. Camera + action for these seconds: one clear action (handheld close-up of hands opening the lid; slow push-in on the drawer as it slides shut…). Hands must be doing simple, physically plausible things.
4. Setting/light: `ads.look` + the scene (small condo kitchen, sari-sari store counter, jeep stop on a rainy afternoon, bedroom desk…).
5. Audio: `Voice-over in Taglish (<ads.narrator>): "<exact line>"` + 1–2 natural sounds (click of the lid, rain outside, kitchen sizzle). Hero clips: sounds only, `no speech, no voice-over`.
6. Negatives last: `ads.negatives`.

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
    {"seconds": 8, "hero": false, "voiceover": "…", "dialogue": "", "visual": "…", "prompt": "…"},
    {"seconds": 8, "hero": true,  "voiceover": "",  "dialogue": "", "visual": "…", "prompt": "…"}
  ],
  "captions": {"tiktok": "<full caption exactly as posted>", "pinned_comment": "<optional, a question>"},
  "end_card": "Tap the yellow basket\npara makita ang presyo"
}
```
`python scripts/ads.py validate <run_dir>` checks length, word caps, hero clips, prompt structure and captions before any credits are spent.

## Example narrated clip (demo, hands only)
```
Vertical 9:16 video. The attached Ate Host character is off-screen; only her voice is heard as the voice-over. Only her hands appear. A compact white 3-tier plastic spice rack with pull-out drawers and rounded edges, about the width of two hands, exactly as in the attached product photo. Handheld close-up: her hand slides the middle drawer out, sets a small jar of garlic powder inside, and pushes it shut with a soft click. Bright natural daylight, small Filipino condo kitchen with a tiled backsplash, handheld smartphone-style UGC camera, realistic skin and hands, true-to-life product colors and scale, shallow depth of field, crisp detail. Voice-over in Taglish (warm, friendly, conversational Filipina woman in her late 20s, natural Taglish, upbeat but not shouty): "Dati, kalat-kalat yung spices ko. Ngayon, isang hila lang, kita mo na lahat." Soft click of the drawer, faint kitchen ambience. No subtitles, no on-screen text, no watermark, no logos other than what is printed on the product itself, no distorted hands, no extra fingers, no morphing product.
```
