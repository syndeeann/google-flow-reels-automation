#!/usr/bin/env python3
"""Quality check a finished Reel before it is posted.

    python scripts/qc.py <run_dir>

Checks <run_dir>/<topic_id>-final.mp4 against prompts.json (the script), edit.json (the cut list) and the
source clips, and writes <run_dir>/qc.json + <run_dir>/check/qc_sheet.png. Exit code 0 = automatic checks
passed, 1 = failed. Posting also requires Claude's own look at qc_sheet.png (see RUNBOOK step 4b).

Automatic checks
  1. completeness/order  every script clip appears exactly once, in script order, and nothing extra
  2. duplicates          no two clips come from the same file or look/sound the same (download mix-ups)
  3. identity            each segment's audio matches ITS source clip better than any other clip
  4. sync                each segment's audio is aligned with its source clip (|lag| <= 60 ms)
  5. narration present   every clip with a voice-over/dialogue line actually has speech in it
  6. glitches            no black frames or frozen picture inside a clip, no audio dropouts or clipping
  7. format              720x1280 (or 1080x1920), 24 fps, H.264 + AAC, video/audio lengths match, size cap
What it can't check: the exact Tagalog words (no speech recognition available) — the narration-present and
identity checks catch missing, swapped or truncated lines, and the visual review catches wrong scenes.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble import FPS, lag_ms, pcm  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sh(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout + r.stderr


def probe(path: Path) -> dict:
    out = sh(["ffprobe", "-v", "error", "-show_entries",
              "stream=codec_type,codec_name,width,height,r_frame_rate,duration:format=duration,size",
              "-of", "json", str(path)])
    return json.loads(out)


def frame(path: Path, t: float, w: int = 64, h: int = 114) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, stdin=subprocess.DEVNULL).stdout
    return np.frombuffer(raw, np.uint8).astype(float).reshape(h, w) if len(raw) == w * h else np.zeros((h, w))


def speech_ratio(x: np.ndarray) -> float:
    """Share of 50 ms windows with voice-band energy well above the clip's quiet floor (x = 8 kHz mono pcm)."""
    if len(x) < 4000:
        return 0.0
    k = 400
    n = len(x) // k
    e = 20 * np.log10(np.sqrt((x[: n * k].reshape(n, k) ** 2).mean(1)) + 1)
    floor = np.percentile(e, 20)
    return float((e > max(floor + 12, e.max() - 25)).mean())


def main(run_dir: Path) -> int:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    data = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    edit = json.loads((run_dir / "edit.json").read_text(encoding="utf-8"))
    tid = brief["topic_id"]
    final = run_dir / f"{tid}-final.mp4"
    script = data["clips"]
    cuts = edit["clips"]
    problems, warnings, info = [], [], {}

    # 1. completeness / order
    ns = [c["n"] for c in cuts]
    if ns != list(range(1, len(script) + 1)):
        problems.append(f"cut list clips {ns} != script clips 1..{len(script)} in order (missing, extra, repeated or out of order)")

    # 2. duplicates by file hash and by look
    srcs = {c["n"]: run_dir / "clips" / f"{tid}-clip{c['n']:02d}.mp4" for c in cuts}
    hashes = {}
    for n, p in srcs.items():
        if not p.exists():
            problems.append(f"clip {n}: source file missing")
            continue
        hashes.setdefault(hashlib.md5(p.read_bytes()).hexdigest(), []).append(n)
    for h, group in hashes.items():
        if len(group) > 1:
            problems.append(f"clips {group} are the same file (download mix-up)")
    mids = {}
    for c in cuts:
        p = srcs[c["n"]]
        if p.exists():
            mids[c["n"]] = frame(p, (c["start"] + c["end"]) / 2)
    keys = list(mids)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = mids[keys[i]], mids[keys[j]]
            if a.std() < 3 or b.std() < 3:
                continue
            diff = float(np.abs(a - b).mean())
            if diff < 4.0:
                problems.append(f"clips {keys[i]} and {keys[j]} look identical (mean pixel diff {diff:.1f}) — redundant clip?")

    # 3-5. per-segment identity, sync, narration
    src_audio = {c["n"]: pcm(srcs[c["n"]], c["start"], c["end"] - c["start"]) for c in cuts if srcs[c["n"]].exists()}
    t = 0.0
    seg_times = []
    worst = 0.0
    for c in cuts:
        n = c["n"]
        d = int((c["end"] - c["start"]) * FPS) / FPS
        seg_times.append((n, t, d))
        if n not in src_audio:
            t += d
            continue
        out = pcm(final, t, d)
        lag = lag_ms(src_audio[n], out)
        worst = max(worst, abs(lag))
        if abs(lag) > 60:
            problems.append(f"clip {n} at {t:.1f}s: voice-over out of sync by {lag:+.0f} ms")

        def corr(a, b):
            m = min(len(a), len(b)) // 80 * 80
            if m < 800:
                return -1.0
            ea = np.abs(a[:m]).reshape(-1, 80).mean(1); eb = np.abs(b[:m]).reshape(-1, 80).mean(1)
            m2 = min(len(ea), len(eb)); ea, eb = ea[:m2], eb[:m2]
            return float(np.corrcoef(ea, eb)[0, 1]) if ea.std() > 0 and eb.std() > 0 else -1.0
        own = corr(src_audio[n], out)
        others = [(corr(src_audio[k], out), k) for k in src_audio if k != n]
        best_other = max(others) if others else (-1.0, None)
        if own < 0.5 or best_other[0] > own + 0.05:
            problems.append(f"clip {n} at {t:.1f}s: audio doesn't match its own clip (own {own:.2f}, clip {best_other[1]} {best_other[0]:.2f})")

        line = (script[n - 1].get("voiceover") or "") + (script[n - 1].get("dialogue") or "") if n <= len(script) else ""
        sr = speech_ratio(out)
        if line.strip() and sr < 0.15:
            problems.append(f"clip {n} at {t:.1f}s: little or no narration heard (speech {sr:.0%}) — line missing or cut")
        # audio dropout: a fully silent stretch >= 0.7 s in the middle of a narrated clip
        if line.strip() and len(out) > 16000:
            k = 400
            e = 20 * np.log10(np.sqrt((out[: len(out) // k * k].reshape(-1, k) ** 2).mean(1)) + 1)
            dead = e < 5
            run = best = 0
            for v in dead[4:-4]:
                run = run + 1 if v else 0
                best = max(best, run)
            if best * 0.05 >= 0.7:
                warnings.append(f"clip {n} at {t:.1f}s: {best*0.05:.1f}s of total silence inside the clip (check for a dropout)")
        t += d
    info["worst_lag_ms"] = worst

    # 6. picture glitches (whole video; end card excluded)
    story_end = t
    blk = sh(["ffmpeg", "-nostdin", "-v", "info", "-t", f"{story_end:.2f}", "-i", str(final), "-vf",
              "blackdetect=d=0.4:pic_th=0.98", "-an", "-f", "null", "-"])
    for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", blk):
        problems.append(f"black frames {float(s):.1f}–{float(e):.1f}s")
    frz = sh(["ffmpeg", "-nostdin", "-v", "info", "-t", f"{story_end:.2f}", "-i", str(final), "-vf",
              "freezedetect=n=0.0015:d=2.5", "-an", "-f", "null", "-"])
    for s in re.findall(r"freeze_start: ([\d.]+)", frz):
        warnings.append(f"picture frozen for 2.5s+ from {float(s):.1f}s (fine for a static shot — check the sheet)")
    vol = sh(["ffmpeg", "-nostdin", "-v", "info", "-i", str(final), "-af", "volumedetect", "-vn", "-f", "null", "-"])
    m = re.search(r"max_volume: (-?[\d.]+) dB", vol)
    if m and float(m.group(1)) > -0.3:
        warnings.append(f"audio peaks at {m.group(1)} dB (possible clipping)")

    # 7. format
    pr = probe(final)
    v = next((s for s in pr["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
    if (v.get("width"), v.get("height")) not in ((720, 1280), (1080, 1920)):
        problems.append(f"resolution {v.get('width')}x{v.get('height')} is not vertical 9:16")
    if v.get("codec_name") != "h264" or a.get("codec_name") != "aac":
        problems.append("codecs must be H.264 + AAC")
    vd, ad = float(v.get("duration", 0)), float(a.get("duration", 0))
    if abs(vd - ad) > 0.4:
        problems.append(f"video {vd:.2f}s vs audio {ad:.2f}s")
    size_mb = int(pr["format"]["size"]) / 1e6
    info.update(duration=round(vd, 2), size_mb=round(size_mb, 2))
    if size_mb >= 10:
        warnings.append(f"file is {size_mb:.1f} MB — over the 10 MB browser upload limit; the posting step can't upload it")

    # contact sheet for the visual review: 2 frames per clip, labelled with clip number and the script's visual
    chk = run_dir / "check"
    chk.mkdir(exist_ok=True)
    tiles = []
    for n, t0, d in seg_times:
        for frac, tag in ((0.25, "a"), (0.75, "b")):
            out = chk / f"qc_{n:02d}{tag}.png"
            label = f"{n}"
            sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t0 + d * frac:.2f}", "-i", str(final), "-frames:v", "1",
                "-vf", f"scale=180:320,drawtext=fontfile={FONT}:text='{label}':x=6:y=6:fontsize=26:fontcolor=yellow:"
                       "box=1:boxcolor=black@0.6", str(out)])
            tiles.append(out)
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    lst = chk / "qc_list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in tiles))
    sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-vf", f"tile={cols}x{rows}:padding=4", "-frames:v", "1", str(chk / "qc_sheet.png")])
    # Lip-sync sheet (owner, 2026-10-28: on-screen characters sometimes "dub" the narration).
    # Only clips that show a person: 4 larger frames spread over the clip, so Claude can see whether
    # anyone's mouth opens/moves with the voice-over. No face model is available in the workspace,
    # so this is a visual check (RUNBOOK 4b), not an automatic one.
    people = re.compile(r"\b(man|woman|guard|agent|boy|girl|lola|lolo|mother|father|teacher|student|vendor|"
                        r"old|young man|person|people|face|character is the)\b", re.I)
    lip_tiles = []
    for n, t0, d in seg_times:
        c = script[n - 1] if n <= len(script) else {}
        if "is off-screen" in c.get("prompt", "") and not people.search(c.get("visual", "")):
            continue
        if not people.search(c.get("visual", "") + " " + c.get("prompt", "")[:400]):
            continue
        for k, frac in enumerate((0.15, 0.38, 0.62, 0.85)):
            out = chk / f"lip_{n:02d}{k}.png"
            sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t0 + d * frac:.2f}", "-i", str(final), "-frames:v", "1",
                "-vf", f"scale=360:640,drawtext=fontfile={FONT}:text='{n}.{k + 1}':x=8:y=8:fontsize=30:fontcolor=yellow:"
                       "box=1:boxcolor=black@0.6", str(out)])
            lip_tiles.append(out)
    lip_clips = sorted({int(p.name[4:6]) for p in lip_tiles})
    if lip_tiles:
        ll = chk / "lip_list.txt"
        ll.write_text("".join(f"file '{p.name}'\n" for p in lip_tiles))
        sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(ll),
            "-vf", f"tile=4x{len(lip_tiles) // 4}:padding=4", "-frames:v", "1", str(chk / "lip_sheet.png")])
    visuals = {str(n): (script[n - 1].get("visual", "") if n <= len(script) else "") for n, _, _ in seg_times}

    # Repeated words in the narrator's script (owner, 2026-10-28)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from repeats import check as _repeat_check
    rep_p, rep_w = _repeat_check(script)
    problems += [f"repeated words in script: {m}" for m in rep_p]
    warnings += [f"repeated words in script: {m}" for m in rep_w]

    result = {"passed": not problems, "problems": problems, "warnings": warnings, "info": info,
              "visual_review": {"sheet": "check/qc_sheet.png", "expected_visuals": visuals,
                                "lip_sheet": "check/lip_sheet.png" if lip_tiles else None, "lip_check_clips": lip_clips,
                                "instructions": "Two frames per clip (a = 25%, b = 75%). Confirm each clip shows its "
                                                "expected visual, clips are in story order, no clip repeats, no "
                                                "text/watermark/garbled faces, characters stay consistent."}}
    (run_dir / "qc.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("passed", "problems", "warnings", "info")}, indent=2, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1]).resolve()))
