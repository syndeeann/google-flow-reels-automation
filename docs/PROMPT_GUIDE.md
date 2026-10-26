# Writing Kwento: Kilabot stories, Flow prompts and captions

Channel: **Kwento: Kilabot** — short Tagalog horror stories from Filipino folklore, always ending on a twist. Dark foggy night scenes, one low, tired, almost calm male narrator (the Flow **Narrator** character).

Claude writes the stories. The owner approves every finished video before anything is posted.

## Story rules
- **Short but interesting: 45–60 seconds**, 5–7 clips, about 80–110 spoken words in total. One idea, one creature, one twist.
- **Lean story** (when credits are low, see RUNBOOK Daily run): 4–5 clips, ~35–45 s, 55–75 words, ≤ 50 credits — hook, two beats, twist.
- **First person**, told by the Narrator as something that happened to him or his family. Relatable modern Filipino life (night shift, tricycle, sari-sari store, lamay, probinsya visit, OFW, group chat) colliding with old folklore.
- **Creatures and elementals:** aswang, manananggal, tiktik, wakwak, tikbalang, kapre, duwende, nuno sa punso, engkanto, diwata, tiyanak, sigbin, santelmo, white lady, berberoka, bungisngis, mangkukulam / barang, kambal-tuko, multo sa lumang bahay. Use authentic details (tiktik sound gets louder when it's far, aswang reflection upside down in the eyes, asin at bawang, "tabi-tabi po").
- **Variety:** don't reuse the creature or the twist type of the last 6 stories in `queue/topics.yaml`. Each day's 3 stories should use 3 different creatures and 3 different settings.
- **Shape:**
  1. **Hook (clip 1, first 2–3 s spoken):** a rule, a confession, an impossible detail, or a price (see `docs/CAPTION_GUIDE.md`). Say a searchable word early (e.g. "aswang").
  2. **Build (2–4 clips):** one escalating beat per clip. Show, don't explain.
  3. **Twist (last clip):** one line that flips everything (the narrator is the creature; the "rescuer" was the monster; the date shows he died years ago…). End on the twist line. No moral, no outro, no CTA spoken.
- Keep it horror, not gore: imply violence (shadows, sounds, aftermath off screen). No children harmed on screen, no real people, no real crimes, no brands.
- **Second voices are risky:** Flow refused a clip twice when another character shouted a line. Keep other characters' lines short and quiet (on-camera, spoken softly), or have the narrator quote them.
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
   - off screen: `The attached Narrator character is off-screen and does not appear; only his voice is heard as the voice-over.`
   - on screen: `The attached Narrator character is the young man in this scene (use his look); his voice is the voice-over.`
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
  "captions": {"facebook": "…", "instagram": "…", "tiktok": "…", "pinned_comment": "…", "replies": ["…", "…"]},
  "end_card": "<short question for the last card, ≤ 2 lines of ~30 chars>",
  "characters": {"<name>": "<sheet>"}
}
```
Captions follow `docs/CAPTION_GUIDE.md`.

## Example clip (hook, narrator off screen)
```
Vertical 9:16 video. The attached Narrator character is off-screen and does not appear; only his voice is heard as the voice-over. Slow push-in through thick fog toward a lone nipa hut on stilts, one window glowing with a dim oil lamp, bamboo grove swaying behind it. Dark foggy night, thick low mist, cold blue moonlight, deep shadows, rural Philippine province, cinematic, realistic, slow ominous camera movement, subtle film grain. Narrator voice-over in Tagalog (low, tired, almost calm adult Filipino male voice, hushed Tagalog storytelling, never shouting): "Sa probinsya namin, kapag mahina ang tiktik… ibig sabihin, nasa tabi mo na siya." Crickets suddenly go silent, a faint tik-tik call, low drone. No subtitles, no on-screen text, no watermark, no logos, no gore, no blood.
```
