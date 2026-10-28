#!/usr/bin/env python3
"""Helper CLI for the TikTok Shop affiliate ads pipeline (tiktok-shop/).

  python scripts/ads.py new <product>            # start (or resume) an ad for a product in products.yaml; prints the run folder
  python scripts/ads.py validate <run_dir>       # check prompts.json before spending Flow credits
  python scripts/ads.py render <run_dir>         # write prompts.md and caption.txt
  python scripts/ads.py length <run_dir>         # final video length without the end card (must be >= 60 s)
  python scripts/ads.py qc <run_dir> [fix note]   # Kilabot quality gate (scripts/qc.py) + 60 s rule; keeps fix history
  python scripts/ads.py review <run_dir> pass|fail [notes]   # record the visual review of check/qc_sheet.png
  python scripts/ads.py finish <ad_id> <status> [note]   # awaiting_approval/approved/posted are QC-gated
  python scripts/ads.py status                   # the product ledger

<product> is the ledger id or the TikTok product_id. Run folders contain brief.json with "topic_id" = ad id,
so scripts/assemble.py and scripts/qc.py work on them unchanged.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is missing. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "tiktok-shop"
CONFIG = BASE / "config.yaml"
LEDGER = BASE / "products.yaml"
OUTPUT = BASE / "output"
MANILA = dt.timezone(dt.timedelta(hours=8))

STATUSES = {"new", "in_progress", "prompts_only", "awaiting_approval", "approved", "posted", "rejected", "failed", "skip"}
RESUMABLE = {"in_progress", "prompts_only", "failed"}
WORD_CAP = {4: 6, 6: 9, 8: 14, 10: 18}
ANALYSIS_KEYS = ["what", "buyer", "problem", "usage_steps", "payoff", "selling_points", "product_sheet"]


def now() -> dt.datetime:
    return dt.datetime.now(MANILA)


def cfg() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}


def load_ledger() -> tuple[str, list[dict]]:
    text = LEDGER.read_text(encoding="utf-8")
    m = re.search(r"^products:", text, re.M)
    header = text[: m.start()] if m else ""
    data = yaml.safe_load(text) or {}
    return header, data.get("products") or []


def save_ledger(header: str, products: list[dict]) -> None:
    body = yaml.safe_dump({"products": products}, allow_unicode=True, sort_keys=False, width=120)
    LEDGER.write_text(header + body, encoding="utf-8")


def find_product(products: list[dict], key: str) -> dict:
    for p in products:
        if str(p.get("id")) == key or str(p.get("product_id")) == key:
            return p
    sys.exit(f"Product '{key}' not found in {LEDGER.relative_to(ROOT)} (add it in step 1 first)")


def find_ad(products: list[dict], ad_id: str) -> tuple[dict, dict]:
    for p in products:
        for a in p.get("ads") or []:
            if a.get("ad_id") == ad_id:
                return p, a
    sys.exit(f"Ad '{ad_id}' not found in {LEDGER.relative_to(ROOT)}")


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def resolve(arg: str) -> Path:
    p = Path(arg)
    return p if p.is_absolute() else ROOT / p


def words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text or "") if re.search(r"\w", w)])


def log(run_dir: Path, msg: str) -> None:
    with (run_dir / "run-log.md").open("a", encoding="utf-8") as f:
        f.write(f"- {now():%Y-%m-%d %H:%M} {msg}\n")


# ---------------------------------------------------------------- commands

def cmd_new(key: str) -> None:
    header, products = load_ledger()
    p = find_product(products, key)
    if p.get("status") == "skip":
        sys.exit(f"{p['id']} is marked skip: {p.get('note', '')}")
    ads = p.setdefault("ads", [])
    last = ads[-1] if ads else None
    if last and last.get("status") in RESUMABLE and (ROOT / last["run_dir"]).exists():
        print(last["run_dir"])  # resume: reuse prompts.json and the Flow project
        return
    c = cfg()
    a, f = c.get("ads", {}), c.get("flow", {})
    ad_id = f"{p['id']}-{len(ads) + 1}"
    run_dir = OUTPUT / f"{now():%Y-%m-%d}-{ad_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    brief = {
        "topic_id": ad_id,
        "ad_id": ad_id,
        "product": {k: p.get(k) for k in ("id", "name", "product_id", "url", "price", "commission", "sold", "category")},
        "previous_angles": [x.get("angle") for x in ads if x.get("angle")],
        "language": a.get("language"),
        "narrator": a.get("narrator"),
        "flow_character": a.get("flow_character"),
        "flow_character_voice": a.get("flow_character_voice"),
        "look": a.get("look"),
        "negatives": a.get("negatives"),
        "length_seconds_min": a.get("length_seconds_min", 60),
        "length_seconds_target": a.get("length_seconds_target", 68),
        "length_seconds_max": a.get("length_seconds_max", 75),
        "end_card": a.get("end_card"),
        "aspect_ratio": "9:16",
        "hero_model": f.get("hero_model"),
        "base_model": f.get("base_model"),
        "hero_clips_per_ad": f.get("hero_clips_per_ad", 2),
        "max_clips": f.get("max_clips_per_ad", 11),
        "flow_url": f.get("url"),
        "download_clips": f.get("download_clips", True),
    }
    (run_dir / "brief.json").write_text(json.dumps(brief, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ads.append({"ad_id": ad_id, "date": f"{now():%Y-%m-%d}", "run_dir": rel(run_dir), "status": "in_progress"})
    p["status"] = "in_progress"
    save_ledger(header, products)
    log(run_dir, f"started ad {ad_id} for {p.get('name')}")
    print(rel(run_dir))


def cmd_validate(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    path = run_dir / "prompts.json"
    if not path.exists():
        sys.exit(f"{rel(path)} is missing")
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"prompts.json is not valid JSON: {e}")
    errs, warns = [], []

    an = d.get("analysis") or {}
    for k in ANALYSIS_KEYS:
        if not an.get(k):
            errs.append(f"analysis.{k} is missing")
    if len(an.get("selling_points") or []) < 3:
        errs.append("analysis.selling_points needs 3 points")
    sheet = (an.get("product_sheet") or "").strip()
    if not d.get("angle"):
        errs.append("angle is missing")
    elif d["angle"] in (brief.get("previous_angles") or []):
        warns.append(f"angle '{d['angle']}' was already used for this product")
    if d.get("narrator") != brief.get("narrator"):
        errs.append("narrator must be exactly brief.narrator (config ads.narrator)")

    clips = d.get("clips") or []
    if not clips:
        errs.append("no clips")
    if len(clips) > brief.get("max_clips", 11):
        errs.append(f"{len(clips)} clips > max_clips {brief.get('max_clips')}")
    neg = (brief.get("negatives") or "").lower().rstrip(".")
    host = brief.get("flow_character") or "Ate Host"
    total, heroes, spoken = 0, 0, 0
    for i, c in enumerate(clips, 1):
        s = c.get("seconds")
        pr = c.get("prompt") or ""
        vo = (c.get("voiceover") or "").strip()
        dl = (c.get("dialogue") or "").strip()
        if not c.get("visual"):
            errs.append(f"clip {i}: visual is missing")
        if not pr.startswith("Vertical 9:16 video."):
            errs.append(f"clip {i}: prompt must start with 'Vertical 9:16 video.'")
        if neg and neg not in pr.lower():
            errs.append(f"clip {i}: prompt must end with the brief's negatives")
        if c.get("hero"):
            heroes += 1
            if s != 8:
                errs.append(f"clip {i} (hero, Veo 3.1 Fast): seconds must be 8")
            if vo or dl:
                errs.append(f"clip {i} (hero): no voice-over or dialogue (keeps one narrator voice)")
            if host.lower() in pr.lower():
                errs.append(f"clip {i} (hero): don't attach/mention {host}")
            if not re.search(r"no speech|no voice-over|no voiceover", pr, re.I):
                errs.append(f"clip {i} (hero): say 'no speech, no voice-over' in the prompt")
            if '"' in pr:
                errs.append(f"clip {i} (hero): no quoted text (Veo would speak it)")
            if sheet and sheet not in pr:
                errs.append(f"clip {i} (hero): paste the product_sheet word for word")
        else:
            if s not in WORD_CAP:
                errs.append(f"clip {i}: seconds must be one of {sorted(WORD_CAP)}")
            n = words(vo) + words(dl)
            if s in WORD_CAP and n > WORD_CAP[s]:
                errs.append(f"clip {i}: {n} spoken words > {WORD_CAP[s]} for {s}s (line gets cut off)")
            if vo:
                spoken += n
                if host.lower() not in pr.lower():
                    errs.append(f"clip {i}: narrated clip must use the attached {host} character")
                if f'"{vo}"' not in pr:
                    errs.append(f"clip {i}: the prompt must contain the exact voice-over in double quotes")
            elif not dl:
                warns.append(f"clip {i}: not hero and no voice-over — intended?")
        total += s if isinstance(s, (int, float)) else 0
    lo = brief.get("length_seconds_min", 60)
    hi = brief.get("length_seconds_max", 75)
    if total < lo + 6:
        errs.append(f"clips add up to {total}s; need >= {lo + 6}s raw so the edit stays >= {lo}s after trims")
    if total > hi + 7:
        errs.append(f"clips add up to {total}s; keep <= {hi + 7}s raw (final <= {hi}s fits the upload limit)")
    want = brief.get("hero_clips_per_ad", 2)
    if not 1 <= heroes <= 3:
        errs.append(f"{heroes} hero clips; use 1-3 (config: {want})")
    if spoken < 70:
        warns.append(f"only {spoken} spoken words; a 62-75 s ad usually has 80-105")
    if clips and not (clips[0].get("voiceover") or "").strip():
        errs.append("clip 1 must be the spoken hook")
    last_vo = next((c.get("voiceover") or "" for c in reversed(clips) if (c.get("voiceover") or "").strip()), "")
    if "basket" not in last_vo.lower():
        warns.append("last narrated line should point to the yellow basket")

    cap = (d.get("captions") or {}).get("tiktok") or ""
    if not cap.strip():
        errs.append("captions.tiktok is missing")
    tags = re.findall(r"#\w+", cap)
    if cap and not 3 <= len(tags) <= 5:
        errs.append(f"captions.tiktok has {len(tags)} hashtags; use 3-5")
    if len(cap) > 300:
        errs.append(f"captions.tiktok is {len(cap)} chars; keep <= 300")
    if re.search(r"₱|\bphp\s?\d|\bpesos?\b", cap, re.I):
        errs.append("captions.tiktok: no prices in the caption (they change); point to the yellow basket")
    if re.search(r"\b(like|share|tag)\b.{0,15}\b(this|mo|niyo|nyo|a friend)\b", cap, re.I):
        warns.append("caption may read as engagement bait")
    if not d.get("end_card"):
        errs.append("end_card is missing")
    claims = re.compile(r"\b(cure|gamot sa|guaranteed|100%|pampaputi|pampapayat|FDA[- ]approved|doctor)\b", re.I)
    for i, c in enumerate(clips, 1):
        if claims.search((c.get("voiceover") or "") + " " + (c.get("dialogue") or "")):
            errs.append(f"clip {i}: risky claim (health/guarantee/authority) — remove unless the listing proves it")

    for w in warns:
        print("WARN", w)
    if errs:
        print("\n".join("ERROR " + e for e in errs))
        sys.exit(1)
    print(f"OK: {len(clips)} clips ({heroes} hero), {total}s raw, {spoken} spoken words")


def cmd_render(run_dir: Path) -> None:
    d = json.loads((run_dir / "prompts.json").read_text(encoding="utf-8"))
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    an = d.get("analysis", {})
    out = [f"# {d.get('title', brief['ad_id'])}", "",
           f"Product: {brief['product'].get('name')} ({brief['product'].get('url') or 'no link'})",
           f"Angle: {d.get('angle')}", "", "## Analysis",
           f"- What: {an.get('what')}", f"- Buyer: {an.get('buyer')}", f"- Problem: {an.get('problem')}",
           "- Usage: " + " → ".join(an.get("usage_steps") or []), f"- Payoff: {an.get('payoff')}",
           "- Selling points: " + "; ".join(an.get("selling_points") or []),
           f"- Product sheet: {an.get('product_sheet')}",
           "- Don't claim: " + "; ".join(an.get("do_not_claim") or []), "", "## Clips"]
    for i, c in enumerate(d.get("clips", []), 1):
        model = brief.get("hero_model") if c.get("hero") else brief.get("base_model")
        out += ["", f"### Clip {i} — {c.get('seconds')}s · {model}{' · HERO' if c.get('hero') else ''}",
                f"Visual: {c.get('visual')}"]
        if c.get("voiceover"):
            out.append(f"Voice-over: {c['voiceover']}")
        out += ["", "```", c.get("prompt", ""), "```"]
    out += ["", "## TikTok caption", "", "```", (d.get("captions") or {}).get("tiktok", ""), "```"]
    (run_dir / "prompts.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (run_dir / "caption.txt").write_text((d.get("captions") or {}).get("tiktok", "") + "\n", encoding="utf-8")
    if d.get("angle"):  # remember the angle so later ads for this product pick a different one
        header, products = load_ledger()
        for p in products:
            for a in p.get("ads") or []:
                if a.get("ad_id") == brief["ad_id"]:
                    a["angle"] = d["angle"]
        save_ledger(header, products)
    print(f"Wrote {rel(run_dir / 'prompts.md')} and {rel(run_dir / 'caption.txt')}")


def cmd_length(run_dir: Path) -> None:
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    final = run_dir / f"{brief['ad_id']}-final.mp4"
    if not final.exists():
        sys.exit(f"{rel(final)} not found (run scripts/assemble.py first)")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(final)], capture_output=True, text=True).stdout.strip())
    card = 0.0
    ep = run_dir / "edit.json"
    if ep.exists():
        card = float((json.loads(ep.read_text(encoding="utf-8")).get("end_card") or {}).get("seconds", 0) or 0)
    content = dur - card
    lo, hi = brief.get("length_seconds_min", 60), brief.get("length_seconds_max", 75)
    print(f"total {dur:.1f}s, end card {card:.1f}s, content {content:.1f}s")
    if content < lo:
        sys.exit(f"TOO SHORT: content {content:.1f}s < {lo}s")
    if dur > hi + 4:
        print(f"WARN long: {dur:.1f}s may not fit the upload size limit at good quality")
    print("LENGTH OK")


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def content_seconds(run_dir: Path, brief: dict) -> float | None:
    final = run_dir / f"{brief['ad_id']}-final.mp4"
    if not final.exists():
        return None
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(final)], capture_output=True, text=True).stdout.strip() or 0)
    ep = run_dir / "edit.json"
    card = float((json.loads(ep.read_text(encoding="utf-8")).get("end_card") or {}).get("seconds", 0) or 0) \
        if ep.exists() else 0.0
    return dur - card


def set_ad_qc(ad_id: str, summary: dict) -> None:
    header, products = load_ledger()
    for p in products:
        for a in p.get("ads") or []:
            if a.get("ad_id") == ad_id:
                a["qc"] = summary
    save_ledger(header, products)


def qc_summary(q: dict) -> dict:
    vr = q.get("visual_review") or {}
    return {"passed": q.get("passed"), "visual": vr.get("result", "pending"),
            "worst_lag_ms": (q.get("info") or {}).get("worst_lag_ms"),
            "content_s": q.get("content_s"), "problems": q.get("problems") or [],
            "warnings": q.get("warnings") or [], "fixed": q.get("fixed") or [], "attempts": q.get("attempts", 0)}


def cmd_qc(run_dir: Path, fixed: str = "") -> None:
    """Same automatic quality gate as Kwento: Kilabot (scripts/qc.py), plus the ads' 60 s minimum.
    Keeps the fix history and attempt count across re-runs (qc.py rewrites qc.json each time)."""
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    qp = run_dir / "qc.json"
    prev = json.loads(qp.read_text(encoding="utf-8")) if qp.exists() else {}
    hist = list(prev.get("fixed") or [])
    if fixed:
        hist.append(f"{now():%Y-%m-%d %H:%M} {fixed}")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "qc.py"), str(run_dir)])
    if not qp.exists():
        sys.exit("qc.py wrote no qc.json")
    q = json.loads(qp.read_text(encoding="utf-8"))
    secs = content_seconds(run_dir, brief)
    lo = brief.get("length_seconds_min", 60)
    if secs is not None and secs < lo:
        q.setdefault("problems", []).append(f"ad content is {secs:.1f}s (end card excluded); must be >= {lo}s")
        q["passed"] = False
    q["content_s"] = round(secs, 2) if secs is not None else None
    q["fixed"] = hist
    q["attempts"] = int(prev.get("attempts", 0)) + 1
    final = run_dir / f"{brief['ad_id']}-final.mp4"
    q["final_md5"] = md5(final) if final.exists() else None
    q.setdefault("visual_review", {})["result"] = "pending"   # a new check always needs a new visual review
    q["visual_review"]["instructions"] = (q["visual_review"].get("instructions", "") +
        " Ads also: the product's shape, colour, size, logo and parts match the listing photos in every clip it "
        "appears; hands look natural (5 fingers, plausible grip); the Ate Host looks the same across clips.").strip()
    qp.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    set_ad_qc(brief["ad_id"], qc_summary(q))
    log(run_dir, f"QC attempt {q['attempts']}: {'PASS' if q['passed'] else 'FAIL'}"
                 + (f" — {'; '.join(q['problems'])}" if q.get("problems") else "") + (f" (fix: {fixed})" if fixed else ""))
    print(f"QC attempt {q['attempts']}: {'PASSED automatic checks — now do the visual review (ads.py review)' if q['passed'] else 'FAILED'}")
    sys.exit(0 if q["passed"] and r.returncode == 0 else 1)


def cmd_review(run_dir: Path, result: str, notes: str = "") -> None:
    """Record Claude's own look at check/qc_sheet.png (the second half of the Kilabot QC)."""
    if result not in ("pass", "fail"):
        sys.exit("review result must be pass or fail")
    brief = json.loads((run_dir / "brief.json").read_text(encoding="utf-8"))
    qp = run_dir / "qc.json"
    if not qp.exists():
        sys.exit("Run `ads.py qc <run_dir>` first")
    q = json.loads(qp.read_text(encoding="utf-8"))
    final = run_dir / f"{brief['ad_id']}-final.mp4"
    if not final.exists() or md5(final) != q.get("final_md5"):
        sys.exit("The final video changed since the last QC run — run `ads.py qc` again before reviewing")
    if result == "pass" and not q.get("passed"):
        sys.exit("Automatic checks failed — fix and re-run `ads.py qc`; the visual review can't override them")
    q["visual_review"]["result"] = result
    q["visual_review"]["notes"] = notes
    q["visual_review"]["at"] = f"{now():%Y-%m-%d %H:%M}"
    qp.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    set_ad_qc(brief["ad_id"], qc_summary(q))
    log(run_dir, f"visual review: {result}" + (f" — {notes}" if notes else ""))
    print(f"visual review: {result}")


def qc_gate(ad: dict, status: str) -> None:
    """awaiting_approval / approved / posted need: automatic QC passed, visual review passed, and the final
    video on disk is the exact file that was checked (and, for posting, the exact file the owner approved)."""
    rd = ROOT / ad["run_dir"]
    brief = json.loads((rd / "brief.json").read_text(encoding="utf-8"))
    qp, final = rd / "qc.json", rd / f"{brief['ad_id']}-final.mp4"
    if not qp.exists():
        sys.exit(f"QC GATE: no qc.json — run `ads.py qc {ad['run_dir']}` first")
    q = json.loads(qp.read_text(encoding="utf-8"))
    if not q.get("passed"):
        sys.exit("QC GATE: automatic checks failed: " + "; ".join(q.get("problems") or []))
    if (q.get("visual_review") or {}).get("result") != "pass":
        sys.exit("QC GATE: visual review not passed (`ads.py review <run_dir> pass \"notes\"`)")
    if not final.exists():
        sys.exit(f"QC GATE: {brief['ad_id']}-final.mp4 is not in the run folder — stage it from "
                 "~/Downloads/TikTok Shop Ads/ first")
    h = md5(final)
    if h != q.get("final_md5"):
        sys.exit("QC GATE: the final video is not the file that passed QC — re-run QC and the visual review")
    if status == "posted" and ad.get("approved_md5") and h != ad["approved_md5"]:
        sys.exit("QC GATE: this file is not the version the owner approved — send it for approval again")
    if status == "posted" and not ad.get("approved_md5"):
        sys.exit("QC GATE: the owner hasn't approved this ad (`ads.py finish <ad_id> approved …` first)")
    if status == "approved":
        ad["approved_md5"] = h


def cmd_finish(ad_id: str, status: str, note: str = "") -> None:
    if status not in STATUSES:
        sys.exit(f"Unknown status '{status}'. Use one of: {', '.join(sorted(STATUSES))}")
    header, products = load_ledger()
    p, a = find_ad(products, ad_id)
    if status in ("awaiting_approval", "approved", "posted"):
        qc_gate(a, status)
    a["status"] = status
    if note:
        a["note"] = note
        if status == "posted" and note.startswith("http"):
            a["link"] = note
    a["updated"] = f"{now():%Y-%m-%d %H:%M}"
    p["status"] = status
    save_ledger(header, products)
    rd = ROOT / a["run_dir"]
    if rd.exists():
        log(rd, f"status → {status}" + (f" ({note})" if note else ""))
    print(f"{ad_id}: {status}")


def cmd_status() -> None:
    _, products = load_ledger()
    if not products:
        print("Ledger is empty — sync the showcase (RUNBOOK step 1).")
        return
    for p in products:
        last = (p.get("ads") or [{}])[-1]
        extra = f"  last ad {last.get('ad_id')} {last.get('status')}" if last else ""
        print(f"{p.get('status', 'new'):18} {p.get('id'):30} {p.get('commission', '')!s:10} {p.get('name', '')[:40]}{extra}")


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "new" and len(args) == 1:
        cmd_new(args[0])
    elif cmd in ("validate", "render", "length") and len(args) == 1:
        {"validate": cmd_validate, "render": cmd_render, "length": cmd_length}[cmd](resolve(args[0]))
    elif cmd == "qc" and len(args) >= 1:
        cmd_qc(resolve(args[0]), " ".join(args[1:]))
    elif cmd == "review" and len(args) >= 2:
        cmd_review(resolve(args[0]), args[1], " ".join(args[2:]))
    elif cmd == "finish" and len(args) >= 2:
        cmd_finish(args[0], args[1], " ".join(args[2:]))
    elif cmd == "status" and not args:
        cmd_status()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
