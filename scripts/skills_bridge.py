#!/usr/bin/env python3
"""Carry Marites's script and Senyorita's prompts into a run folder's prompts.json.

    python scripts/skills_bridge.py import <run_dir> --script NNN-slug.prompts.json --prompts NNN-slug.json

Marites (storyteller) exports <script>.prompts.json; Senyorita (ai-prompt-expert) exports <prompts>.json.
Both list clips by number. This fills <run_dir>/prompts.json:
  clips[i] = {seconds, voiceover, dialogue, visual (Marites's draft picture), prompt (Senyorita's Flow prompt)}
Existing keys (captions, end_card, narrator, characters ...) are kept. Fails if the two files disagree on
clip numbers, seconds or narration, so Flow never gets a prompt for a different line than the script.
Then add the captions and run `python scripts/reels.py validate <run_dir>`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def merge(script: dict, prompts: dict) -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    s = {c["n"]: c for c in script.get("clips", [])}
    p = {c["n"]: c for c in prompts.get("clips", [])}
    if sorted(s) != sorted(p):
        problems.append(f"clip numbers differ: script {sorted(s)} vs prompts {sorted(p)}")
    if sorted(s) != list(range(1, len(s) + 1)):
        problems.append("script clips must be numbered 1..N without gaps")
    clips = []
    for n in sorted(set(s) & set(p)):
        sc, pc = s[n], p[n]
        sv, pv = (sc.get("voiceover") or "").strip(), (pc.get("voiceover") or "").strip()
        if sc.get("seconds") != pc.get("seconds"):
            problems.append(f"clip {n}: seconds {sc.get('seconds')} (script) vs {pc.get('seconds')} (prompts)")
        if sv.lower() != pv.lower() and not (sv in ("", "none") and pv in ("", "none")):
            problems.append(f"clip {n}: narration differs between script and prompts")
        vo = "" if sv.lower() == "none" else sv
        clips.append({"seconds": sc.get("seconds"), "voiceover": vo, "dialogue": "",
                      "visual": (sc.get("visual") or "").strip(), "prompt": (pc.get("visual") or "").strip()})
    return clips, problems


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] != "import":
        print(__doc__)
        return 2
    run_dir = Path(argv[1])
    args = dict(zip(argv[2::2], argv[3::2]))
    if "--script" not in args or "--prompts" not in args:
        print("need --script and --prompts")
        return 2
    script, prompts = load(args["--script"]), load(args["--prompts"])
    clips, problems = merge(script, prompts)
    if problems:
        print("MISMATCH")
        for m in problems:
            print(" -", m)
        return 1
    target = run_dir / "prompts.json"
    data = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    data["clips"] = clips
    data.setdefault("title", script.get("title") or prompts.get("title") or "")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(clips)} clips written to {target}. Add captions, then: python scripts/reels.py validate {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
