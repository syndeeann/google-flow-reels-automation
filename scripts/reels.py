#!/usr/bin/env python3
"""Helper CLI for the Google Flow Reels pipeline.

Claude (or you) writes the script and prompts; this tool handles the
bookkeeping so every run is consistent:

  python scripts/reels.py next                 # claim the next "ready" topic, make its output folder
  python scripts/reels.py validate <run_dir>   # check prompts.json before spending Flow credits
  python scripts/reels.py render <run_dir>     # write prompts.md (copy/paste-friendly) from prompts.json
  python scripts/reels.py finish <topic_id> <status> [note]   # done | prompts_only | failed | ready
  python scripts/reels.py status               # show the queue

Only dependency: PyYAML (pip install -r requirements.txt).
"""

from __future__ import annotations

import datetime as dt
import json
import re
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

VALID_STATUSES = {"draft", "ready", "in_progress", "prompts_only", "done", "failed"}


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
    length = int(topic.get("length_seconds", v["length_seconds"]))
    n = clips_for(length, v["clip_seconds"])
    if n > flow["max_clips_per_run"]:
        n = flow["max_clips_per_run"]
    return {
        "topic_id": topic["id"],
        "topic": topic["topic"],
        "audience": topic.get("audience", ""),
        "cta": topic.get("cta", ""),
        "notes": topic.get("notes", ""),
        "aspect_ratio": v["aspect_ratio"],
        "length_seconds": length,
        "clip_count": n,
        "clip_seconds": v["clip_seconds"],
        "max_words_per_clip": v["max_words_per_clip"],
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
    busy = [t["id"] for t in topics if t.get("status") == "in_progress"]
    if busy:
        print(f"WARNING: still in_progress from an earlier run: {', '.join(busy)}", file=sys.stderr)
    topic = next((t for t in topics if t.get("status") == "ready"), None)
    if topic is None:
        print("NO_READY_TOPIC")
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

    if len(clips) != brief["clip_count"]:
        problems.append(f"expected {brief['clip_count']} clips, found {len(clips)}")

    character = (data.get("character") or "").strip()
    narrator = (data.get("narrator") or brief["narrator"]).strip()
    for i, c in enumerate(clips, 1):
        tag = f"clip {i}"
        vo, prompt = (c.get("voiceover") or "").strip(), (c.get("prompt") or "").strip()
        if not vo:
            problems.append(f"{tag}: missing voiceover line")
        elif word_count(vo) > brief["max_words_per_clip"]:
            problems.append(f"{tag}: voiceover has {word_count(vo)} words (max {brief['max_words_per_clip']}) — won't fit in {brief['clip_seconds']}s")
        if not prompt:
            problems.append(f"{tag}: missing prompt")
            continue
        if brief["aspect_ratio"] not in prompt:
            problems.append(f"{tag}: prompt doesn't state {brief['aspect_ratio']}")
        if vo and vo not in prompt:
            problems.append(f"{tag}: prompt doesn't contain the exact voiceover line in quotes")
        if character and character not in prompt:
            problems.append(f"{tag}: character sheet isn't repeated word-for-word (hurts consistency)")
        if narrator and narrator not in prompt:
            problems.append(f"{tag}: narrator description isn't repeated word-for-word")
        if "no on-screen text" not in prompt.lower() and "no subtitles" not in prompt.lower():
            problems.append(f"{tag}: missing negatives (no subtitles / no on-screen text)")
    if clips and brief.get("cta"):
        last = clips[-1].get("voiceover", "").lower()
        if not any(w in last for w in re.findall(r"\w{4,}", brief["cta"].lower())[:4]):
            problems.append("last clip doesn't seem to carry the CTA")

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
        out.append(f"| {i} | {c['voiceover']} | {c.get('visual', '')} |")
    out += ["", "## Flow prompts (paste one per generation)", ""]
    for i, c in enumerate(data["clips"], 1):
        out += [f"### Clip {i}", "", "```", c["prompt"], "```", ""]
    (run_dir / "prompts.md").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {(run_dir / 'prompts.md').relative_to(ROOT)}")


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
    elif cmd == "finish" and len(args) >= 2:
        cmd_finish(args[0], args[1], " ".join(args[2:]))
    elif cmd == "status":
        cmd_status()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
