# Writing Kwento: Kilabot stories, Flow prompts and captions

Channel: **Kwento: Kilabot** — short Tagalog horror stories from Filipino folklore, always ending on a twist. Dark foggy night scenes, one low, tired, almost calm male narrator (the Flow **Narrator** character).

Claude writes the stories. Every finished video must pass the quality check (RUNBOOK step 4b); Claude posts it to Facebook + YouTube.

## Story rules (owner, 2026-10-27: up to 2 minutes, more themes, never boring)
- **Length by credits** (RUNBOOK Daily run): **full ~2 min** (100–120 s, 11–14 clips, ~170–200 spoken words) when the Flow balance is ≥ 400; **medium ~90 s** (8–9 clips) at 200–399; **lean ~45 s** (4–5 clips, ≤ 50 credits) below 200. One story, one threat, one twist — a long story gets more beats, not more ideas.
- **First person**, told by the Narrator as something that happened to him, his family or his co-workers/classmates. Relatable modern Filipino life.
- **Rotate the theme family** (look at the last 6 stories in `queue/topics.yaml`; don't repeat the family twice in a row, and use different families on the same day):
  1. **Filipino folklore** — aswang, manananggal, tiktik, wakwak, tikbalang, kapre, duwende, nuno sa punso, engkanto, diwata, tiyanak, sigbin, santelmo, white lady, berberoka, bungisngis, mangkukulam / barang, kambal-tuko. Authentic details (tiktik louder when far, upside-down reflection in an aswang's eyes, asin at bawang, "tabi-tabi po").
  2. **Abandoned buildings** — the half-built mall, the closed hospital wing, the old hotel in Baguio, the burned cinema, the empty resort, the condemned ancestral house. Urban explorers, a security guard on graveyard shift, a vlogger filming "for content". Fear from space: corridors, stairwells, a door that is open now but was closed.
  3. **Call center horrors** — BPO graveyard shift in Ortigas/Makati/IT Park: the 3 AM caller who knows your name, the 13th floor that the elevator skips, the seat nobody takes, the headset that whispers between calls, the night-shift team lead who isn't on the roster. Ground it in real details (AHT, queue, "Thank you for calling…", pantry, smoke break, sleeping pods).
  4. **School horrors** — the old building's CR, the music room piano, the class picture with an extra student, the night before the exam in the library, the retreat house, the guard who says the school has no 4th floor. Narrator is a teacher, a guard, or an adult remembering high school (keep child characters off-screen or in non-threatening shots — Flow refuses children in horror shots).
  5. **Kwentong pambata (horror for kids)** — spooky but SAFE, ~6–12 years old: mischievous duwende, a kapre who is lonely, a ghost who just wants his lost toy back, the monster under the bed who is scared of the kid. Rules: no blood, no death of children, no screaming jump-scares, no harm to animals; scary-fun tension that ends warm, funny or clever (the twist can be sweet). Narrator stays the same voice but gentle ("Lola style"). Mark these `audience: kids` in the queue — on YouTube they must be set to **"Yes, it's made for kids"** (law, not optional), and the caption skips adult hashtags.
- **Make it interesting, never boring:**
  - **Hook in the first 2 s** with a specific, strange detail (rule, confession, impossible detail, price, warning — CAPTION_GUIDE). Never open with setting description.
  - **Open a loop early** ("Hanggang ngayon, hindi ko alam kung sino ang sumagot sa tawag na 'yon.") and pay it off only at the end.
  - **Escalate every clip**: each beat must be worse, closer or stranger than the last; a long story gets a **midpoint turn** (~60 s: the narrator realizes the rule was wrong / the helper is lying / it already happened before).
  - **Specific beats over summary**: one concrete sound or object per clip (the cold coffee left on desk 13, the sapatos lined up outside the CR).
  - **Vary the shots**: wide establishing, close-ups of objects/hands, POV down a corridor, over-the-shoulder, a static "something moves in the background" shot. Never two similar shots in a row.
  - **Breathing room**: one near-silent beat before the twist (a short line or 6 s clip).
  - **Twist that re-reads the story** in the last line (the narrator is the ghost; the caller was calling from the future; the abandoned building was never abandoned; the kid saved the monster). No moral, no outro, no CTA spoken.
- **No repeated words in the narration** (owner, 2026-10-28): never the same word twice in a row or twice in one clip's line ("papalapit nang papalapit", "Walang gumagalaw. Walang tumitingin." → rewrite), never the same two-word phrase in two clips, and vary any word that would show up in 3+ clips. `reels.py validate` and `qc.py` enforce this with `scripts/repeats.py`.
- Keep it horror, not gore: imply violence (shadows, sounds, aftermath off screen). No children harmed or in danger on screen, no real people, no real crimes, no real company/school/building names, no brands.
- **No dubbing** (owner, 2026-10-28): on-screen characters sometimes lip-sync the narrator's voice-over. Every narrated clip says nobody on screen moves their lips (lines above + the `negatives`); `reels.py validate` rejects a narrated prompt without "lips". Prefer faces in profile, from behind, half in shadow or busy with an action (holding a phone to the ear, looking at a screen) during narration; for a face close-up write "lips pressed together, silent". Never write "his voice is the voice-over" for an on-screen person without the closed-lips sentence.
- **Second voices are risky:** Flow refused a clip twice when another character shouted a line. Keep other characters' lines short and quiet, or have the narrator quote them. Also refused: a covered body; a child on screen in a horror shot.
- Title format: `Kilabot #N: <Tagalog title>`; N continues from the last number in the queue.

## Clip timing (Flow Omni 1.1 Flash: 4/6/8/10 s)
Count narration + dialogue words per clip:
| words | clip length | credits |
|---|---|---|
| ≤ 9 | 6 s | 10 |
| 10–14 | 8 s | 12 |
| 15–18 | 10 s | 15 |
Never more than 18 words in one clip (it gets cut off at the end). Put `"seconds"` on every clip in prompts.json.

## Prompts
Every prompt stands on its own (the model doesn't remember other clips). Order:
1. `Vertical 9:16 video.` + the Narrator line:
   - off screen: `The attached Narrator character is off-screen and does not appear; only his voice is heard as the voice-over. Anyone on screen keeps their lips closed and does not speak.`
   - on screen: `The attached Narrator character is the young man in this scene (use his look). His voice is an inner-monologue voice-over recorded separately: his lips stay closed and still the whole time, he never speaks or mouths the words.`
   - clip where only another character speaks: no Narrator line, and don't attach the character in Flow.
2. Camera + action for these seconds (slow push-in, static wide, slow pan to a doorway…). Suggest the creature (silhouette, eyes in the dark, shadow, sound) more than show it.
3. Setting/light: the brief's `look` + scene details (Metro Manila street or province, as the story needs).
4. Audio: `Narrator voice-over in Tagalog (<brief.narrator>): "<exact line>"` + 2–3 specific sounds (crickets stopping, tiktik calls, wind in bamboo, creaking floorboards, distant dog howl, low drone). For on-camera speech: `The old woman says quietly in Tagalog: "<line>"`.
5. Negatives last: the brief's `negatives`.

Recurring non-narrator characters: write one character sheet sentence and paste it word for word in every clip they appear in.

## prompts.json
```json
{
  "title": "Kilabot #2: …",
  "character": "",
  "narrator": "<exactly brief.narrator>",
  "clips": [
    {"seconds": 8, "voiceover": "…", "dialogue": "", "visual": "…", "prompt": "…"}
  ],
  "caption_full": "<the Facebook caption, exactly as it will be posted>",
  "caption_text": "<line 1 of the caption>",
  "hashtags": [],
  "captions": {"facebook": "…", "instagram": "…", "tiktok": "…", "youtube": {"title": "…", "description": "…", "tags": ["…"]}, "pinned_comment": "…", "replies": ["…", "…"]},
  "end_card": "<short question for the last card, ≤ 2 lines of ~30 chars>",
  "characters": {"<name>": "<sheet>"}
}
```
Captions follow `docs/CAPTION_GUIDE.md`.

## Example clip (hook, narrator off screen)
```
Vertical 9:16 video. The attached Narrator character is off-screen and does not appear; only his voice is heard as the voice-over. Slow push-in through thick fog toward a lone nipa hut on stilts, one window glowing with a dim oil lamp, bamboo grove swaying behind it. Dark foggy night, thick low mist, cold blue moonlight, deep shadows, rural Philippine province, cinematic, realistic, slow ominous camera movement, subtle film grain. Narrator voice-over in Tagalog (low, tired, almost calm adult Filipino male voice, hushed Tagalog storytelling, never shouting): "Sa probinsya namin, kapag mahina ang tiktik… ibig sabihin, nasa tabi mo na siya." Crickets suddenly go silent, a faint tik-tik call, low drone. No subtitles, no on-screen text, no watermark, no logos, no gore, no blood.
```
