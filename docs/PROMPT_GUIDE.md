# Writing scripts and Flow prompts for vertical Reels

## Script
- One voice-over line per ~8-second clip, max `max_words_per_clip` words (default 20). Read it aloud: it must fit in 8 seconds.
- Clip 1 = hook. Make the viewer stop scrolling in the first 2 seconds (a question, a bold claim, a surprising visual).
- Middle clips = one idea each: show, don't list.
- Last clip = the CTA from the brief, said plainly.
- Write in the brief's `language`. Taglish is fine when the notes ask for it.

## Prompts
Every prompt must stand on its own. Veo does not remember the previous clip. Use this order:

1. **Format + camera:** "Vertical 9:16 video. Slow push-in close-up, handheld feel."
2. **Character sheet:** if a person recurs, paste the SAME sentence in every clip, word for word (age, face, hair, outfit). Put it in `character` in prompts.json too.
3. **Action:** what happens in these 8 seconds.
4. **Setting, light, style:** use the brief's `look` plus scene details.
5. **Audio:** `Narrator voice-over (<brief.narrator>): "<exact voiceover line>"` plus ambience/SFX. For on-camera speech use `She says: "<line>"` instead.
6. **Negatives last:** the brief's `negatives` (no subtitles, no on-screen text, no watermark, no logos).

Avoid: real people's names, celebrity likeness, brand logos/trademarks, copyrighted characters, text you want rendered in the video (add text overlays later in an editor).

## Example clip
```
Vertical 9:16 video. Slow push-in close-up on a tall iced latte with layered purple ube and milk, condensation on the glass. A young Filipina barista, mid-20s, shoulder-length wavy black hair, cream apron over a lilac shirt, slides the glass across a wooden counter and smiles. Cozy café on a rainy Manila afternoon, raindrops on the window, cinematic, realistic, soft natural light, shallow depth of field. Narrator voice-over (warm adult female, Filipino-English accent, friendly and calm): "Rainy day? This is your sign to try something purple." Soft rain ambience, gentle café chatter, ice clinking. No subtitles, no on-screen text, no watermark, no logos.
```
