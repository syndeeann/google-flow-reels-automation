# Prompt lessons (read before writing any ad prompt)

Every time a Flow clip fails the quality check, the cause is recorded here with the prompt change that prevents it (`python scripts/ads.py recreate … "<lesson>"` appends it automatically). Apply every lesson to new prompts, so the same failure never costs credits twice.

Format: `- <date> · <ad_id> clip <n> · <QC problem> → <prompt rule that prevents it>`

## Lessons carried over from Kwento: Kilabot (same Flow models)
- 2026-10-27 · Kilabot · lines filling a whole clip were cut off at the end → keep words under the cap with a margin; the speech clause asks her to finish about one second early.
- 2026-10-27 · Kilabot · a second, shouting voice in a clip was refused twice → one speaker per clip; no other people talking.
- 2026-10-27 · Kilabot · Flow refused a prompt as possibly violating policy (credits refunded) → soften once (calmer wording), never retry the same text.

## Lessons from ads
