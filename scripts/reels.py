#!/usr/bin/env python3
"""Helper CLI for the Google Flow Reels pipeline.

Claude (or you) writes the script and prompts; this tool handles the
bookkeeping so every run is consistent:

  python scripts/reels.py next                 # claim the next "ready" topic, make its output folder
  python scripts/reels.py validate <run_dir>   # check prompts.json before spending Flow credits
  python scripts/reels.py render <run_dir>     # write prompts.md and caption.txt from prompts.json
  python scripts/reels.py join <run_dir> <clip1.mp4> <clip2.mp4> ...   # join clips into <topic_id>-final.mp4 (needs ffmpeg)
  python scripts/reels.py finish <topic_id> <status> [note]   # see VALID_STATUSES
  python scripts/reels.py status               # show the queue

Only dependency: PyYAML (pip install -r requirements.txt).
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is missing. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.yaml"
QUEUE = ROOT / "queue" / "topics.yaml"
OUTPUT = ROOT / "output"
MANILA = dt.timezone(dt.timedelta(hours=8))

VALID_STATUSES = {
    "draft", "ready", "in_progress", "prompts_only", "failed",
    "ready_to_post",      # passed QC; waiting to be posted (e.g. Chrome wasn't connected)
    "awaiting_approval",  # legacy: final video + caption sent to the owner; nothing posted
    "approved",           # owner approved this exact video + caption; posting in progress
    "posted",             # live on the Facebook Page
    "rejected",           # owner rejected it; not posted
    "done",               # legacy: clips generated (before the approval flow existed)
}


# ---------------------------------------------------------------- helpers

def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_topics() -> list[dict]:
    return load_yaml(QUEUE).get("topics") or []


def set_status(topic_id: str, status: str) -> None:
    """Change one topic's status in place, keeping the file's comments and layout."""
    if status not in VALID_STATUSES:
        sys.exit(f"Unknown status '{status}'. Use one of: {', '.join(sorted(VALID_STATUSES))}")
    lines = QUEUE.read_text(encoding="utf-8").splitlines(keepends=True)
    id_re = re.compile(r"^(\s*)-\s+id:\s*['\"]?" + re.escape(topic_id) + r"['\"]?\s*(#.*)?$")
    for i, line in enumerate(lines):
        m = id_re.match(line.rstrip("\n"))
        if not m:
            continue
        indent = len(m.group(1)) + 2  # keys inside the list item
        for j in range(i + 1, len(lines)):
            stripped = lines[j].strip()
            if re.match(r"^\s*-\s+id:", lines[j]):
                break  # reached next topic without a status line
            if stripped.startswith("status:"):
                lines[j] = " " * indent + f"status: {status}\n"
                QUEUE.write_text("".join(lines), encoding="utf-8")
                return
        lines.insert(i + 1, " " * indent + f"status: {status}\n")
        QUEUE.write_text("".join(lines), encoding="utf-8")
        return
    sys.exit(f"Topic id '{topic_id}' not found in {QUEUE.relative_to(ROOT)}")


def clips_for(length_seconds: int, clip_seconds: int) -> int:
    return max(1, round(length_seconds / clip_seconds))


def build_brief(topic: dict, cfg: dict) -> dict:
    v, voice, style, flow = cfg["video"], cfg["voice"], cfg["style"], cfg["flow"]
    cap, fb = cfg.get("caption", {}), cfg.get("facebook", {})
    length = int(topic.get("length_seconds", v["length_seconds"]))
    n = int(topic.get("clip_count", clips_for(length, v["clip_seconds"])))
    cap_clips = int(topic.get("max_clips", flow["max_clips_per_run"]))  # per-topic override, owner-approved only
    if n > cap_clips:
        n = cap_clips
    return {
        "topic_id": topic["id"],
        "topic": topic["topic"],
        "audience": topic.get("audience", ""),
        "folklore": topic.get("folklore", ""),
        "cta": topic.get("cta", cap.get("cta", "")),
        "cta_in_last_clip": bool(topic.get("cta_in_last_clip", v.get("cta_in_last_clip", True))),
        "caption_cta": cap.get("cta", ""),
        "caption_hashtags": cap.get("hashtags", ""),
        "caption_max_chars": int(cap.get("max_chars", 2200)),
        "facebook_page": fb.get("page_name", ""),
        "notes": topic.get("notes", ""),
        "aspect_ratio": v["aspect_ratio"],
        "length_seconds": length,
        "clip_count": n,
        "clip_count_fixed": "clip_count" in topic,
        "clip_seconds": v["clip_seconds"],
        "max_words_per_clip": int(topic.get("max_words_per_clip", v["max_words_per_clip"])),
        "max_clips": cap_clips,
        "language": topic.get("language", voice["language"]),
        "narrator": topic.get("narrator", voice["narrator"]),
        "look": topic.get("look", style["look"]),
        "negatives": style["negatives"],
        "outputs_per_prompt": flow["outputs_per_prompt"],
        "flow_url": flow["url"],
        "download_clips": flow["download_clips"],
    }


def word_count(text: str) -> int:
    return len(re.findall(r"[\w'’-]+", text))


# ---------------------------------------------------------------- commands

def cmd_next() -> None:
    cfg = load_yaml(CONFIG)
    topics = load_topics()
    # resume unfinished work first (earlier runs that stopped midway), then new topics
    topic = next((t for t in topics if t.get("status") in ("in_progress", "prompts_only")), None) \
        or next((t for t in topics if t.get("status") == "ready"), None)
    if topic is None:
        print("NO_READY_TOPIC")
        return
    existing = sorted(OUTPUT.glob(f"*-{topic['id']}"))
    if topic.get("status") in ("in_progress", "prompts_only") and existing:
        run_dir = existing[-1]  # resume in the original run folder
        log(run_dir, f"Resumed topic '{topic['id']}' (was {topic.get('status')}).")
        set_status(topic["id"], "in_progress")
        print(run_dir.relative_to(ROOT))
        return
    today = dt.datetime.now(MANILA).strftime("%Y-%m-%d")
    run_dir = OUTPUT / f"{today}-{topic['id']}"
    run_dir.mkdir(parents=True, exist_ok=True)
    brief = build_brief(topic, cfg)
    (run_dir / "brief.json").write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    set_status(topic["id"], "in_progress")
    log(run_dir, f"Claimed topic '{topic['id']}' ({brief['clip_count']} clips, {brief['aspect_ratio']}).")
    print(run_dir.relative_to(ROOT))


def cmd_validate(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    data = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    clips = data.get("clips") or []
    problems: list[str] = []

    if brief.get("clip_count_fixed", True) and len(clips) != brief["clip_count"]:
        problems.append(f"expected {brief['clip_count']} clips, found {len(clips)}")
    if not brief.get("clip_count_fixed", True) and not (4 <= len(clips) <= 16):
        problems.append(f"stories need 4-16 clips, found {len(clips)}")
    word_cap = {6: 9, 8: 14, 10: 18}

    character = (data.get("character") or "").strip()
    narrator = (data.get("narrator") or brief["narrator"]).strip()
    for i, c in enumerate(clips, 1):
        tag = f"clip {i}"
        vo, prompt = (c.get("voiceover") or "").strip(), (c.get("prompt") or "").strip()
        dialogue = (c.get("dialogue") or "").strip()  # on-camera line by another character
        if not vo and not dialogue:
            problems.append(f"{tag}: missing voiceover line (or dialogue)")
        if dialogue and dialogue not in prompt:
            problems.append(f"{tag}: prompt doesn't contain the exact dialogue line")
        secs = c.get("seconds")
        spoken = word_count(vo) + word_count(dialogue)
        if secs is not None:
            if secs not in word_cap:
                problems.append(f"{tag}: seconds must be 6, 8 or 10")
            elif spoken > word_cap[secs]:
                problems.append(f"{tag}: {spoken} spoken words won't fit in {secs}s (max {word_cap[secs]})")
        elif vo and word_count(vo) > brief["max_words_per_clip"]:
            problems.append(f"{tag}: voiceover has {word_count(vo)} words (max {brief['max_words_per_clip']})")
        if not prompt:
            problems.append(f"{tag}: missing prompt")
            continue
        if brief["aspect_ratio"] not in prompt:
            problems.append(f"{tag}: prompt doesn't state {brief['aspect_ratio']}")
        if vo and vo not in prompt:
            problems.append(f"{tag}: prompt doesn't contain the exact voiceover line in quotes")
        if character and character not in prompt:
            problems.append(f"{tag}: character sheet isn't repeated word-for-word (hurts consistency)")
        if vo and narrator and narrator not in prompt:
            problems.append(f"{tag}: narrator description isn't repeated word-for-word")
        if "no on-screen text" not in prompt.lower() and "no subtitles" not in prompt.lower():
            problems.append(f"{tag}: missing negatives (no subtitles / no on-screen text)")
    if clips and brief.get("cta") and brief.get("cta_in_last_clip", True):
        last = clips[-1].get("voiceover", "").lower()
        if not any(w in last for w in re.findall(r"\w{4,}", brief["cta"].lower())[:4]):
            problems.append("last clip doesn't seem to carry the CTA")

    caption_text = (data.get("caption_text") or "").strip()
    if data.get("caption_full"):
        if len(data["caption_full"]) > brief.get("caption_max_chars", 2200):
            problems.append("caption_full is too long")
    elif not caption_text:
        problems.append("missing caption_text (hook + teaser for the Facebook caption, no twist spoiler)")
    else:
        full = compose_caption(brief, data)
        if len(full) > brief.get("caption_max_chars", 2200):
            problems.append(f"caption is {len(full)} chars (max {brief.get('caption_max_chars', 2200)})")
        if "#" in caption_text:
            problems.append("caption_text has hashtags; put them in 'hashtags' instead")

    caps = data.get("captions")
    if caps is not None:
        yt = caps.get("youtube") or {}
        if not (yt.get("title") or "").strip() or len(yt.get("title", "")) > 100:
            problems.append("captions.youtube.title missing or over 100 characters")
        if not (yt.get("description") or "").strip():
            problems.append("captions.youtube.description missing")
        if any(ch in (yt.get("title", "") + yt.get("description", "")) for ch in "<>"):
            problems.append("captions.youtube: YouTube rejects < and > in titles/descriptions")
        for k in ("facebook", "instagram", "tiktok", "pinned_comment"):
            if not (caps.get(k) or "").strip():
                problems.append(f"captions.{k} missing")
        for k in ("facebook", "instagram", "tiktok"):
            n = len(re.findall(r"#\w+", caps.get(k) or ""))
            if not 3 <= n <= 5:
                problems.append(f"captions.{k}: {n} hashtags (use 3-5; Instagram allows max 5)")
        bait = re.compile(r"\b(i-?share|i-?tag|tag mo|tag a friend|like and share|share this)\b", re.I)
        for k in ("facebook", "instagram", "tiktok"):
            if bait.search(caps.get(k) or ""):
                problems.append(f"captions.{k}: engagement bait (like/share/tag demands get demoted)")

    if problems:
        print("INVALID")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print(f"OK: {len(clips)} clips ready for Flow")


def cmd_render(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    data = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    out = [f"# {data.get('title') or brief['topic']}", "",
           f"- Topic id: `{brief['topic_id']}`",
           f"- Format: {brief['aspect_ratio']}, {brief['length_seconds']}s, {brief['clip_count']} clips",
           f"- Narrator: {data.get('narrator') or brief['narrator']}", ""]
    if data.get("character"):
        out += ["**Character sheet** (repeated in every prompt):", "", f"> {data['character']}", ""]
    out += ["## Script", "", "| Clip | Voice-over | Visual |", "|---|---|---|"]
    for i, c in enumerate(data["clips"], 1):
        spoken = " ".join(x for x in [c.get("voiceover", ""), c.get("dialogue", "") and f"*{c['dialogue']}*"] if x)
        out.append(f"| {i} | {spoken} | {c.get('visual', '')} |")
    out += ["", "## Flow prompts (paste one per generation)", ""]
    for i, c in enumerate(data["clips"], 1):
        out += [f"### Clip {i}", "", "```", c["prompt"], "```", ""]
    caption = compose_caption(brief, data)
    out += ["## Facebook caption", "", "```", caption, "```", ""]
    (run_dir / "prompts.md").write_text("\n".join(out), encoding="utf-8")
    (run_dir / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    if data.get("captions"):
        c = data["captions"]
        txt = [f"=== Facebook (posted on the Page) ===\n{c['facebook']}", f"=== Instagram ===\n{c['instagram']}",
               f"=== TikTok ===\n{c['tiktok']}", f"=== Pinned first comment ===\n{c['pinned_comment']}"]
        if c.get("youtube"):
            y = c["youtube"]
            txt.append(f"=== YouTube Shorts ===\nTitle: {y['title']}\n\n{y['description']}\n\nTags: {', '.join(y.get('tags', []))}")
        if c.get("replies"):
            txt.append("=== Reply templates ===\n" + "\n".join("- " + r for r in c["replies"]))
        (run_dir / "captions.txt").write_text("\n\n".join(txt) + "\n", encoding="utf-8")
    print(f"Wrote {(run_dir / 'prompts.md').relative_to(ROOT)} and {(run_dir / 'caption.txt').relative_to(ROOT)}")


def compose_caption(brief: dict, data: dict) -> str:
    """captions.facebook, or caption_full, or caption_text + channel CTA + hashtags."""
    if (data.get("captions") or {}).get("facebook"):
        return data["captions"]["facebook"].strip()
    if (data.get("caption_full") or "").strip():  # owner-supplied caption, used verbatim
        return data["caption_full"].strip()
    parts = [(data.get("caption_text") or "").strip()]
    if brief.get("caption_cta"):
        parts.append(brief["caption_cta"])
    tags: list[str] = []
    for t in (data.get("hashtags") or []) + brief.get("caption_hashtags", "").split():
        t = t if t.startswith("#") else "#" + t
        if t.lower() not in {x.lower() for x in tags}:
            tags.append(t)
    if tags:
        parts.append(" ".join(tags))
    return "\n\n".join(p for p in parts if p)


def cmd_join(run_dir: Path, clips: list[Path]) -> None:
    """Join clips in the given order into one 1080x1920 H.264/AAC video, with a short fade-out at the end."""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is missing")
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    missing = [str(c) for c in clips if not c.is_file()]
    if missing:
        sys.exit("Missing clip files: " + ", ".join(missing))
    out = run_dir / f"{brief['topic_id']}-final.mp4"
    n = len(clips)
    inputs: list[str] = []
    for c in clips:
        inputs += ["-i", str(c)]
    has_audio = [bool(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(c)],
        capture_output=True, text=True).stdout.strip()) for c in clips]
    filt, labels = [], ""
    for i in range(n):
        filt.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                    f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,format=yuv420p[v{i}]")
        if has_audio[i]:
            filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:  # silent clip: add matching silence so concat lines up
            dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clips[i])],
                                 capture_output=True, text=True).stdout.strip() or "8"
            filt.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={dur}[a{i}]")
        labels += f"[v{i}][a{i}]"
    total = sum(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(c)],
                                     capture_output=True, text=True).stdout.strip() or 8) for c in clips)
    fade_start = max(0.0, total - 1.0)
    filt.append(f"{labels}concat=n={n}:v=1:a=1[vc][ac]")
    filt.append(f"[vc]fade=t=out:st={fade_start:.2f}:d=1[vout]")
    filt.append(f"[ac]afade=t=out:st={fade_start:.2f}:d=1[aout]")
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + r.stderr[-2000:])
    log(run_dir, f"Joined {n} clips into {out.name} ({total:.1f}s).")
    print(out)


def cmd_finish(topic_id: str, status: str, note: str = "") -> None:
    set_status(topic_id, status)
    runs = sorted(OUTPUT.glob(f"*-{topic_id}"))
    if runs:
        log(runs[-1], f"Finished with status '{status}'." + (f" {note}" if note else ""))
    print(f"{topic_id} -> {status}")


def cmd_status() -> None:
    for t in load_topics():
        print(f"{t.get('status', '?'):13} {t['id']}: {t.get('topic', '')[:70]}")


def log(run_dir: Path, message: str) -> None:
    stamp = dt.datetime.now(MANILA).strftime("%Y-%m-%d %H:%M")
    with (run_dir / "run-log.md").open("a", encoding="utf-8") as f:
        f.write(f"- {stamp} — {message}\n")


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "next":
        cmd_next()
    elif cmd in ("validate", "render") and args:
        run_dir = (ROOT / args[0]) if not Path(args[0]).is_absolute() else Path(args[0])
        (cmd_validate if cmd == "validate" else cmd_render)(run_dir)
    elif cmd == "join" and len(args) >= 2:
        run_dir = (ROOT / args[0]) if not Path(args[0]).is_absolute() else Path(args[0])
        cmd_join(run_dir, [Path(a) for a in args[1:]])
    elif cmd == "finish" and len(args) >= 2:
        cmd_finish(args[0], args[1], " ".join(args[2:]))
    elif cmd == "status":
        cmd_status()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
