# Captions and hooks for Facebook, Instagram and TikTok

Research summary, 2026-10-27. Sources at the bottom; most are marketing sites summarizing Meta and TikTok statements, so treat numbers as guidance and let Page Insights decide.

## What the platforms reward (all three agree)
- **Watching to the end.** Completion and rewatches are the strongest signals on all three. A short video people finish beats a long one they abandon. → Keep stories **45–60 seconds**, hook in the first 2–3 seconds, twist as the last line.
- **Shares and sends** (DMs) push a video to non-followers, especially on Instagram. Saves and real comments also count. Likes matter least.
- **Originality.** Meta demotes reposts and accounts that mostly repost; Instagram flags reused visuals/audio. Our videos are generated from our own scripts — upload the original file, never a re-download with another app's watermark.
- **Fresh and consistent.** Facebook says it surfaces far more same-day Reels and that posting more often helps; consistency also helps TikTok learn who the account is for.
- **No engagement bait.** Facebook demotes captions that beg for likes, shares or tags ("I-share mo 'to!", "Tag mo ang…"). Ask a genuine question instead.
- **Length placement.** Facebook: Reels under 90 s appear in more places. Instagram: up to 3 min can be recommended to non-followers. TikTok: completion matters more than length.

## Caption rules (write one set per video)
1. **Line 1 = hook + search words.** Start with the most unsettling line of the story or a curiosity gap, and include a phrase people search: *kwentong kilabot, kwentong katatakutan, Tagalog horror story, Filipino horror, aswang story, kwentong aswang*. Never spoil the twist.
2. **Line 2 = one-sentence tease** that makes them want the ending.
3. **Line 3 = one genuine question** viewers can answer from their own life ("May ganito rin ba sa probinsya niyo?", "Ikaw, bubuksan mo ba?"). No "like/share/tag" demands.
4. **Series line:** "Kilabot #N" and/or "Sundan ang Kwento: Kilabot para sa susunod na kwento."
5. **Hashtags:** 3–5 total (Instagram allows max 5). Mix 1–2 broad + 2–3 specific: `#KwentongKilabot #FilipinoHorror #KwentongAswang #TagalogHorrorStories #HorrorStoryPH`. Same set across platforms, adjusted per story.
6. Natural Taglish is fine; write how viewers actually search and talk. No keyword stuffing.

### Per platform
- **Facebook:** the full 4-part caption above. 3–5 hashtags at the end.
- **Instagram:** same text, ≤5 hashtags (hard limit), keywords in the first line (Instagram leans on keywords over hashtags). Instagram's non-follower ceiling is 3 min, so 1-minute stories are fine.
- **TikTok:** shorter: hook line + question + 3–5 hashtags. TikTok transcribes audio and reads on-screen text, so the spoken hook should contain the search words too (e.g. the narrator says "aswang" early).

## Hook formulas (Tagalog) for the spoken first line and caption line 1
- **The rule:** "Sa probinsya namin, may isang patakaran: huwag kang sasagot kapag may tumawag sa pangalan mo pagkalampas ng hatinggabi."
- **The confession:** "Hanggang ngayon, hindi ko pa rin sinasabi kay Mama kung ano talaga ang nakita ko noong gabing 'yon."
- **The impossible detail:** "Tatlo kaming umuwi galing sa lamay. Pero apat ang anino sa daan."
- **The number/price:** "Pitong libong piso. 'Yan ang presyo ng pagkalimot kay Papa."
- **The warning:** "Kapag may narinig kang 'tik-tik' na palayo… ibig sabihin, malapit na siya."
Pick the one that matches the story; the first 2 seconds must already be uneasy.

## Also generate per video
- **Pinned first comment:** a question in the narrator's voice that invites stories ("Anong pamahiin sa inyo ang hindi niyo sinusuway hanggang ngayon?").
- **2 reply templates** in the narrator's voice for the first hour of comments.

## Output format
`prompts.json` → `"captions": {"facebook": "...", "instagram": "...", "tiktok": "...", "pinned_comment": "...", "replies": ["...", "..."]}`; `caption_full` = the Facebook caption (what gets posted on the Page).

## Sources
- Buffer, "Inside the Facebook Algorithm in 2026" (Jan 2026): https://buffer.com/library/facebook-news-feed-algorithm/
- SocialPilot, "Instagram Reels Algorithm 2026": https://www.socialpilot.co/de/blog/instagram-reels-algorithm
- Darkroom, "TikTok Algorithm Guide 2026": https://www.darkroomagency.com/observatory/tiktok-algorithm-guide-2026-everything-we-know-about-how-videos-are-ranked
- Social Samosa, "Instagram limits number of hashtags to five per post": https://www.socialsamosa.com/news-2/instagram-hashtags-five-per-post-10923075
- Owner's "Story #1 + Facebook Growth Kit" (Oct 26, 2026): originality, watch-time, caption and engagement-bait findings.
