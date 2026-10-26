#!/usr/bin/env python3
"""Assemble a finished Reel from Flow clips: trim, join, sound bed, end card, loudness.

    python scripts/assemble.py <run_dir>

Reads <run_dir>/edit.json:
{
  "clips": [{"n": 1, "start": 0.4, "end": 8.0}, ...],          # story order; files clips/<topic_id>-clipNN.mp4
  "bed": {"clip": 22, "start": 5.6, "end": 6.8,                 # a sound lifted from one generated clip
          "every": 2.6, "gain_db": -26, "lowpass": 3000,
          "under": [1, 2, 3]},                                  # clip numbers that get the bed
  "end_card": {"text": "Line one\\nline two", "sub": "Kwento: Kilabot", "seconds": 3.5}
}
Writes <run_dir>/<topic_id>-final.mp4 (1080x1920, 24 fps, H.264/AAC, about -14 LUFS).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H, FPS, SR = 1080, 1920, 24, 48000


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + " ".join(cmd)[:500] + "\n" + r.stderr[-1500:])


def main(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    edit = json.loads((run_dir / "edit.json").read_text(encoding="utf-8"))
    tid = brief["topic_id"]
    tmp = Path(tempfile.mkdtemp(prefix="assemble-", dir=run_dir))
    bed = edit.get("bed")

    # 1. bed sample (looped later per segment)
    loop = None
    if bed:
        src = run_dir / "clips" / f"{tid}-clip{bed['clip']:02d}.mp4"
        sample = tmp / "sample.wav"
        dur = bed["end"] - bed["start"]
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(bed["start"]), "-t", str(dur), "-i", str(src), "-vn",
             "-ac", "2", "-ar", str(SR),
             "-af", f"afade=t=in:d=0.05,afade=t=out:st={dur-0.15:.2f}:d=0.15,lowpass=f={bed.get('lowpass', 3000)},"
                    f"volume={bed['gain_db']}dB,apad=whole_dur={bed['every']}", str(sample)])
        loop = sample

    # 2. each segment: trim, scale, per-clip loudness, optional bed, tiny audio fades
    segs = []
    for k, c in enumerate(edit["clips"]):
        src = run_dir / "clips" / f"{tid}-clip{c['n']:02d}.mp4"
        d = c["end"] - c["start"]
        out = tmp / f"seg{k:02d}.mp4"
        vf = f"scale={W}:{H}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p"
        af = (f"aresample={SR},aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2:LRA=11,"
              f"afade=t=in:d=0.06,afade=t=out:st={d-0.08:.2f}:d=0.08")
        inputs = ["-ss", str(c["start"]), "-t", f"{d:.3f}", "-i", str(src)]
        if loop and c["n"] in bed.get("under", []):
            inputs += ["-stream_loop", "-1", "-i", str(loop)]
            fc = (f"[0:v]{vf}[v];[0:a]{af}[a0];[1:a]atrim=0:{d:.3f},afade=t=in:d=0.3,afade=t=out:st={max(d-0.3,0):.2f}:d=0.3[b];"
                  f"[a0][b]amix=inputs=2:duration=first:normalize=0[a]")
        else:
            fc = f"[0:v]{vf}[v];[0:a]{af}[a]"
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", "-t", f"{d:.3f}",
             str(out).replace(".mp4", ".mkv")])
        segs.append(Path(str(out).replace(".mp4", ".mkv")))

    # 3. end card
    card = edit.get("end_card")
    if card:
        out = tmp / "card.mkv"
        lines = card["text"].split("\n")
        draws = []
        fs = 54
        y0 = int(H * 0.45) - (len(lines) * (fs + 22)) // 2
        for i, line in enumerate(lines):
            t = line.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
            draws.append(f"drawtext=fontfile={FONT}:text='{t}':fontsize={fs}:fontcolor=white:"
                         f"x=(w-text_w)/2:y={y0 + i * (fs + 22)}")
        if card.get("sub"):
            s = card["sub"].replace(":", "\\:")
            draws.append(f"drawtext=fontfile={FONT_LIGHT}:text='{s}':fontsize=40:fontcolor=white@0.6:"
                         f"x=(w-text_w)/2:y={int(H * 0.62)}")
        sec = card.get("seconds", 3.5)
        vf = ",".join(draws) + f",fade=t=in:st=0:d=0.6,format=yuv420p"
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={sec}",
             "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-t", str(sec), "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "pcm_s16le", str(out)])
        segs.append(out)

    # 4. concat + final loudness
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in segs))
    joined = tmp / "joined.mkv"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    final = run_dir / f"{tid}-final.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(joined), "-c:v", "copy",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(final)])
    total = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
                           capture_output=True, text=True).stdout.strip()
    print(f"{final} ({float(total):.1f}s)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).resolve())
