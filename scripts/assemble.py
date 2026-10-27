#!/usr/bin/env python3
"""Assemble a finished Reel from Flow clips: trim, join, sound bed, end card, loudness, sync check.

    python scripts/assemble.py <run_dir>

Reads <run_dir>/edit.json:
{
  "clips": [{"n": 1, "start": 0.4, "end": 8.0}, ...],          # story order; files clips/<topic_id>-clipNN.mp4
  "bed": {"clip": 22, "start": 5.6, "end": 6.8,                 # a sound lifted from one generated clip
          "every": 2.6, "gain_db": -8, "lowpass": 2800,
          "under": [1, 2, 3]},                                  # clip numbers that get the bed
  "end_card": {"text": "Line one\\nline two", "sub": "Kwento: Kilabot", "seconds": 3.5}
}
Writes <run_dir>/<topic_id>-final.mp4: 720x1280 (Flow's native size), 24 fps, H.264/AAC, about -14 LUFS,
under 9.5 MB (two-pass, bitrate from the size budget) so Claude in Chrome can upload it, even for ~2 min stories.

Sync rules (learned the hard way): every segment's audio is cut/padded to EXACTLY its video frame count
before joining, and no look-ahead filters (loudnorm) are used per segment — they drop the last seconds of
audio and shift everything after. The script cross-checks every segment against its source clip at the end.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS, SR = 720, 1280, 24, 48000


def run(cmd: list[str]) -> str:
    r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", *cmd] if cmd[0] != "ffprobe" else cmd,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + " ".join(cmd)[:600] + "\n" + r.stderr[-1500:])
    return r.stdout + r.stderr


def loudness(src: Path, start: float, dur: float) -> float:
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-ss", str(start), "-t", str(dur), "-i", str(src),
                        "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else -20.0


def wav_samples(p: Path) -> int:
    with wave.open(str(p)) as w:
        return w.getnframes()


def pcm(path: Path, start: float = 0, dur: float | None = None) -> np.ndarray:
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start)] + (["-t", str(dur)] if dur else []) + \
          ["-i", str(path), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL).stdout
    return np.frombuffer(raw, np.int16).astype(float)


def lag_ms(ref: np.ndarray, sig: np.ndarray, max_ms: int = 1500) -> float:
    """Offset of ref inside sig (positive = sig audio is late), via normalized cross-correlation of envelopes."""
    def env(x):
        k = 80  # 10 ms at 8 kHz
        n = len(x) // k
        e = np.abs(x[: n * k]).reshape(n, k).mean(1)
        return (e - e.mean()) / (e.std() + 1e-9)
    a, b = env(ref), env(sig)
    m = max_ms // 10
    best, arg = -1e9, 0
    for s in range(-m, m + 1):
        if s >= 0:
            x, y = a[: len(a) - s], b[s: s + len(a) - s]
        else:
            x, y = a[-s:], b[: len(a) + s]
        n = min(len(x), len(y))
        if n < 50:
            continue
        c = float(np.dot(x[:n], y[:n]) / n)
        if c > best:
            best, arg = c, s
    return arg * 10.0


def main(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    edit = json.loads((run_dir / "edit.json").read_text(encoding="utf-8"))
    tid = brief["topic_id"]
    tmp = Path(tempfile.mkdtemp(prefix="assemble-", dir=run_dir))
    bed = edit.get("bed") or {}

    loop = None
    if bed:
        src = run_dir / "clips" / f"{tid}-clip{bed['clip']:02d}.mp4"
        loop = tmp / "bed.wav"
        dur = bed["end"] - bed["start"]
        run(["-ss", str(bed["start"]), "-t", str(dur), "-i", str(src), "-vn", "-ac", "2", "-ar", str(SR),
             "-af", f"afade=t=in:d=0.05,afade=t=out:st={dur-0.15:.2f}:d=0.15,lowpass=f={bed.get('lowpass', 3000)},"
                    f"volume={bed['gain_db']}dB,apad=whole_dur={bed['every']}", str(loop)])

    vsegs, asegs, plan = [], [], []
    t = 0.0
    for k, c in enumerate(edit["clips"]):
        src = run_dir / "clips" / f"{tid}-clip{c['n']:02d}.mp4"
        avail = int(run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v",
                         "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(src)]).strip())
        frames = min(int((c["end"] - c["start"]) * FPS), avail - int(round(c["start"] * FPS)))
        d = frames / FPS                      # exact segment length
        S = frames * SR // FPS                # exact audio samples
        gain = max(-12.0, min(12.0, -16.0 - loudness(src, c["start"], d)))
        v = tmp / f"v{k:02d}.mkv"
        run(["-ss", f"{c['start']:.3f}", "-i", str(src), "-frames:v", str(frames), "-an",
             "-vf", f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(v)])
        vf_got = int(run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v",
                          "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(v)]).strip())
        if vf_got != frames:
            sys.exit(f"segment {k} (clip {c['n']}): video {vf_got} frames, expected {frames}")
        a = tmp / f"a{k:02d}.wav"
        base = (f"[0:a]aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo,volume={gain:.2f}dB,"
                f"afade=t=in:d=0.05,afade=t=out:st={max(d-0.08,0):.3f}:d=0.08,apad=whole_len={S},atrim=end_sample={S}")
        if loop and c["n"] in bed.get("under", []):
            fc = (base + "[a0];"
                  f"[1:a]atrim=end_sample={S},afade=t=in:d=0.3,afade=t=out:st={max(d-0.3,0):.3f}:d=0.3[b];"
                  f"[a0][b]amix=inputs=2:duration=first:normalize=0,atrim=end_sample={S}[a]")
            inputs = ["-ss", f"{c['start']:.3f}", "-t", f"{d + 0.5:.3f}", "-i", str(src),
                      "-stream_loop", "-1", "-i", str(loop)]
        else:
            fc = base + "[a]"
            inputs = ["-ss", f"{c['start']:.3f}", "-t", f"{d + 0.5:.3f}", "-i", str(src)]
        run([*inputs, "-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le", "-ar", str(SR), str(a)])
        got = wav_samples(a)
        if got != S:
            sys.exit(f"segment {k} (clip {c['n']}): audio {got} samples, expected {S}")
        vsegs.append(v); asegs.append(a)
        plan.append((c["n"], src, c["start"], d, t))
        t += d

    card = edit.get("end_card")
    if card:
        sec = card.get("seconds", 3.5)
        frames = round(sec * FPS); S = frames * SR // FPS
        lines = card["text"].split("\n")
        fs = 36
        y0 = int(H * 0.45) - (len(lines) * (fs + 14)) // 2
        draws = []
        for i, line in enumerate(lines):
            tx = line.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019")
            draws.append(f"drawtext=fontfile={FONT}:text='{tx}':fontsize={fs}:fontcolor=white:"
                         f"x=(w-text_w)/2:y={y0 + i * (fs + 14)}")
        if card.get("sub"):
            s = card["sub"].replace(":", "\\:")
            draws.append(f"drawtext=fontfile={FONT_LIGHT}:text='{s}':fontsize=26:fontcolor=white@0.6:"
                         f"x=(w-text_w)/2:y={int(H * 0.62)}")
        v = tmp / "vcard.mkv"
        run(["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-frames:v", str(frames),
             "-vf", ",".join(draws) + ",fade=t=in:st=0:d=0.6,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(v)])
        a = tmp / "acard.wav"
        run(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-af", f"atrim=end_sample={S}",
             "-c:a", "pcm_s16le", str(a)])
        vsegs.append(v); asegs.append(a)

    (tmp / "v.txt").write_text("".join(f"file '{p.name}'\n" for p in vsegs))
    (tmp / "a.txt").write_text("".join(f"file '{p.name}'\n" for p in asegs))
    run(["-f", "concat", "-safe", "0", "-i", str(tmp / "v.txt"), "-c", "copy", str(tmp / "video.mkv")])
    run(["-f", "concat", "-safe", "0", "-i", str(tmp / "a.txt"), "-c", "copy", str(tmp / "audio.wav")])
    nframes = int(run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v",
                       "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(tmp / "video.mkv")]).strip())
    nsamp = wav_samples(tmp / "audio.wav")
    if nsamp != nframes * SR // FPS:
        sys.exit(f"joined audio {nsamp} samples vs video {nframes} frames — not equal")

    # final static gain to -14 LUFS with a peak limiter (no look-ahead that changes timing)
    whole = loudness(tmp / "audio.wav", 0, nsamp / SR)
    g = -14.0 - whole
    final = run_dir / f"{tid}-final.mp4"
    # size cap: Claude in Chrome uploads files < 10 MB, so every video (up to ~2 min) is fitted under max_mb
    # with a two-pass encode (bitrate from the size budget; preset slow keeps dark scenes clean at low rates)
    max_mb = float(edit.get("max_mb", 9.5))
    secs = nframes / FPS
    abr = 96
    vkbps = int(min(1400, max(300, max_mb * 8000 / secs * 0.94 - abr)))
    common = ["-i", str(tmp / "video.mkv"), "-i", str(tmp / "audio.wav"), "-map", "0:v", "-map", "1:a",
              "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vkbps}k", "-maxrate", f"{int(vkbps*1.5)}k",
              "-bufsize", f"{3*vkbps}k"]
    passlog = str(tmp / "x264pass")
    run(common + ["-pass", "1", "-passlogfile", passlog, "-an", "-f", "mp4", "/dev/null"])
    run(common + ["-pass", "2", "-passlogfile", passlog,
         "-af", f"volume={g:.2f}dB,alimiter=limit=0.85:attack=5:release=50:level=disabled",
         "-c:a", "aac", "-b:a", f"{abr}k", "-movflags", "+faststart", str(final)])

    # sync check: each segment of the final vs its source clip
    worst = 0.0
    for n, src, st, d, t0 in plan:
        lag = lag_ms(pcm(src, st, d), pcm(final, t0, d))
        worst = max(worst, abs(lag))
        print(f"clip {n:02d} at {t0:7.2f}s  lag {lag:+.0f} ms")
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)]))
    print(f"{final} ({dur:.1f}s, {final.stat().st_size/1e6:.1f} MB, worst lag {worst:.0f} ms)")
    if worst > 60:
        sys.exit("SYNC CHECK FAILED")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).resolve())
