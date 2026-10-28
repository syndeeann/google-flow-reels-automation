#!/usr/bin/env python3
"""Find repeated words in the narrator's script (owner, 2026-10-28: "remove the repeated words").

    python scripts/repeats.py <run_dir>      # prints problems/warnings, exit 1 on problems

Used by `reels.py validate` (before any Flow credits are spent) and by `qc.py` (final gate).

Problems (must be rewritten before generating):
  - the same word twice in a row ("ring ring", "papalapit nang papalapit")
  - a content word used twice inside one clip's line ("Walang gumagalaw. Walang tumitingin.")
  - the same two-word phrase in two different clips ("labintatlong ring" in clip 4 and clip 10)
Warnings (judgment call, keep only if it is the story's one deliberate callback):
  - a content word that shows up in 3 or more clips

Small Tagalog/English function words (ang, ng, sa, na, ko, the, a …) are ignored.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

STOP = set("""
ang ng nang sa na ay at si ni kay mga ko mo niya namin natin nila kami tayo sila ako ikaw ka siya ito iyan iyon yan yon 'yan 'yon
'to ito dito diyan doon roon rito pa din rin daw raw lang lamang ba po ho nga naman pala kasi kung kapag pag para pero o hindi
akong kong mong kang niyang naming nating di isa isang may mayroon meron ung yung ni'ya 'ko 'di nung noong sabi
the a an and or of to in on at is it i my me you he she we they his her for with but not this that
""".split())


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[\wñÑ'’-]+", text.lower().replace("’", "'")) if w.strip("'-")]


def content(ws: list[str]) -> list[str]:
    return [w for w in ws if w not in STOP and len(w) >= 3]


def check(clips: list[dict]) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    lines = [((c.get("voiceover") or "") + " " + (c.get("dialogue") or "")).strip() for c in clips]
    bigram_at: dict[str, set[int]] = defaultdict(set)
    word_at: dict[str, set[int]] = defaultdict(set)
    for n, line in enumerate(lines, 1):
        ws = words(line)
        for a, b in zip(ws, ws[1:]):
            if a == b and a not in {"'", "-"}:
                problems.append(f'clip {n}: "{a} {a}" — same word twice in a row')
        for a, mid, b in zip(ws, ws[1:], ws[2:]):
            if a == b and a not in STOP and mid in STOP:
                problems.append(f'clip {n}: "{a} {mid} {b}" — word repeated')
        cw = content(ws)
        seen = set()
        for w in cw:
            if w in seen:
                problems.append(f'clip {n}: "{w}" used twice in one line — "{line}"')
            seen.add(w)
            word_at[w].add(n)
        for a, b in zip(cw, cw[1:]):
            bigram_at[f"{a} {b}"].add(n)
    for bg, ns in bigram_at.items():
        if len(ns) > 1:
            problems.append(f'"{bg}" repeated in clips {sorted(ns)}')
    for w, ns in word_at.items():
        if len(ns) >= 3:
            warnings.append(f'"{w}" appears in {len(ns)} clips {sorted(ns)} — vary it unless it is the one deliberate callback')
    # de-duplicate messages, keep order
    return list(dict.fromkeys(problems)), list(dict.fromkeys(warnings))


def check_run(run_dir: Path) -> tuple[list[str], list[str]]:
    p = json.loads((run_dir / "prompts.json").read_text())
    return check(p.get("clips", []))


if __name__ == "__main__":
    probs, warns = check_run(Path(sys.argv[1]))
    for m in probs:
        print("PROBLEM:", m)
    for m in warns:
        print("warning:", m)
    print("repeats: " + ("FAIL" if probs else "OK"))
    sys.exit(1 if probs else 0)
