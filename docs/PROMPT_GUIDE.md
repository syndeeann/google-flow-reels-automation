# Writing Kwento: Kilabot scripts, Flow prompts and captions

Channel: **Kwento: Kilabot** — Tagalog horror stories based on Filipino folklore. Dark foggy night scenes, a slow eerie male narrator, and every video ends on a twist.

## Script
- Language: natural spoken **Tagalog** (not deep/formal Filipino; a few common English words are fine if that's how people talk). No English narration.
- One voice-over line per ~8-second clip, max `max_words_per_clip` words (default 15). The narrator is slow with pauses: read it aloud slowly; it must fit in 8 seconds.
- Story shape:
  - **Clip 1 = hook.** Drop the viewer into the dread in the first 2 seconds: a rule ("Huwag kang lilingon kapag may tumawag sa pangalan mo sa gabi."), an eerie detail, or "Totoo ito, nangyari sa probinsya namin."
  - **Middle clips = build.** One beat each; escalate. Show, don't explain. Name the creature only if it adds dread.
  - **Last clip = the twist.** A reveal that flips what came before (often recontextualizing the narrator or a "safe" character). End on the twist line itself, no moral, no outro, no call to action (the CTA lives in the caption). `video.cta_in_last_clip` is false.
- Use the topic's `folklore` and `notes`. If `notes` suggest a twist, you may improve it, but keep it a twist.
- Folklore should feel authentic: aswang, manananggal, tikbalang, kapre, tiyanak, duwende, white lady, santelmo, sigbin, etc., with provincial settings (kubo, bukid, balete, kawayan, lumang bahay na bato, sapa).

## Prompts
Every prompt must stand on its own. Veo does not remember the previous clip. Use this order:

1. **Format + camera:** "Vertical 9:16 video." plus a slow, ominous move (slow push-in, slow dolly through fog, static wide shot, slow pan to a dark doorway).
2. **Character sheet:** if a person recurs, paste the SAME sentence in every clip, word for word (age, face, hair, clothes). Put it in `character` in prompts.json too.
3. **Action:** what happens in these 8 seconds. Suggest the creature (silhouette, eyes in the dark, shadow on the wall, shape in the fog) more than you show it.
4. **Setting, light, style:** the brief's `look` (dark foggy night) plus scene details.
5. **Audio:** `Narrator voice-over in Tagalog (<brief.narrator>): "<exact voiceover line>"` plus ambience/SFX (crickets stopping, wind in bamboo, creaking floorboards, distant dog howl, low drone). No music with lyrics.
6. **Negatives last:** the brief's `negatives` (no subtitles, no on-screen text, no watermark, no logos, no gore, no blood).

Keep it horror, not gore: Flow refuses graphic violence, so imply it (sounds, shadows, aftermath kept off-screen). Avoid real people, real crimes, brand logos, copyrighted characters, and children in danger shown explicitly (imply instead).

## Caption (prompts.json → `caption_text`, `hashtags`)
- `caption_text`: 1–3 short Tagalog lines: a creepy hook + a teaser question ("Ikaw, lilingon ka ba?"). **Never reveal the twist.** No hashtags here.
- `hashtags`: 2–4 topic-specific tags, e.g. `["#Aswang", "#KwentongAswang"]`.
- `render` builds `caption.txt` = caption_text + the channel CTA + topic hashtags + channel hashtags (`config.yaml → caption`).

## prompts.json shape
```json
{
  "title": "Aswang sa Kabilang Bahay",
  "character": "<one-line character sheet, or empty string>",
  "narrator": "<exactly brief.narrator>",
  "clips": [
    {"voiceover": "<= max_words_per_clip words, Tagalog>", "visual": "<one line>", "prompt": "<full Flow prompt>"}
  ],
  "caption_text": "<hook + teaser, no twist spoiler>",
  "hashtags": ["#Aswang"]
}
```

## Example clip (hook)
```
Vertical 9:16 video. Slow push-in through thick fog toward a lone nipa hut on stilts, one window glowing with a dim oil lamp. A young Filipina woman, early 20s, long straight black hair, pale yellow duster dress, stands frozen at the window staring at the bamboo grove outside. Dark foggy night, thick low mist, cold blue moonlight, deep shadows, rural Philippine province, cinematic, realistic, slow ominous camera movement, subtle film grain. Narrator voice-over in Tagalog (slow, deep, eerie adult Filipino male voice, hushed Tagalog storytelling with long pauses): "Sa probinsya namin, may isang patakaran. Huwag kang sisilip sa bintana pagsapit ng hatinggabi." Crickets suddenly go silent, wind rustling bamboo, low droning tone. No subtitles, no on-screen text, no watermark, no logos, no gore, no blood.
```
