#!/usr/bin/env python3
"""Turn a plan.json into a day-by-day content calendar.

Usage:
    python3 scripts/build_calendar.py <path/to/plan.json>

Writes next to plan.json:
    content-calendar.csv    (open in Google Sheets or Excel, or import to a scheduler)
    content-calendar.md     (day by day, with check boxes)
    content-calendar.html   (printable)

plan.json looks like:
{
  "title": "November pack",
  "pieces": [
    {"id": "car-01", "format": "carousel", "platform": "instagram", "title": "...",
     "hook": "...", "stage": "reach", "day": 1, "slot": "morning",
     "file": "carousels/01-name/slide-01.png", "caption_file": "carousels/01-name/caption.md",
     "cta": "Comment HOUSE"},
    {"id": "thr-04", "format": "thread", "title": "...", "day": null, "status": "bank"}
  ]
}

"day" counts posting days, not calendar days: day 1 is the first posting day.
Pieces with no day (or status "bank") go to the content bank for later.
Cadence comes from config.json ("cadence").
"""
import csv
import datetime as dt
import html
import json
import pathlib
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FORMAT_LABEL = {
    "carousel": "Carousel", "quote": "Quote graphic", "reel": "Reel (talking)", "short-video": "Short video",
    "thread": "Thread", "note": "Substack note", "substack-article": "Substack article",
    "blog": "Blog post", "email": "Email", "instagram-post": "Instagram post", "story": "Story sequence",
    "facebook-post": "Facebook post",
}
DEFAULT_PLATFORM = {
    "carousel": "Instagram", "quote": "Instagram", "reel": "Instagram", "short-video": "TikTok",
    "thread": "Threads", "note": "Substack", "substack-article": "Substack", "blog": "Blog", "email": "Email",
    "instagram-post": "Instagram", "story": "Instagram", "facebook-post": "Facebook",
}
DEFAULT_SLOTS = {"morning": "8:00 AM", "midday": "12:00 PM", "evening": "7:00 PM"}


def load_cadence():
    try:
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {}
    cad = cfg.get("cadence", {})
    start = cad.get("start_date")
    if start:
        start = dt.date.fromisoformat(start)
    else:
        today = dt.date.today()
        start = today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)  # next Monday
    return {
        "start": start,
        "post_days": cad.get("post_days", [0, 1, 2, 3, 4, 5]),
        "slots": {**DEFAULT_SLOTS, **cad.get("slots", {})},
        "max_per_day": cad.get("max_pieces_per_day", 4),
        "horizon": cad.get("horizon_days", 30),
    }


def posting_dates(start, post_days, count):
    d, out = start, []
    while len(out) < count:
        if d.weekday() in post_days:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    plan_path = pathlib.Path(sys.argv[1])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    pieces = plan.get("pieces", [])
    cad = load_cadence()
    base = plan_path.parent
    warnings = []

    ids = Counter(p.get("id") for p in pieces)
    for k, n in ids.items():
        if k and n > 1:
            warnings.append(f"Duplicate id: {k}")

    scheduled = [p for p in pieces if isinstance(p.get("day"), int) and p.get("status") != "bank"]
    bank = [p for p in pieces if p not in scheduled]
    if not scheduled:
        warnings.append("Nothing is scheduled. Every piece went to the content bank.")
        last_day = 0
    else:
        last_day = max(p["day"] for p in scheduled)
    dates = posting_dates(cad["start"], cad["post_days"], max(last_day, 1))

    rows = []
    for p in sorted(scheduled, key=lambda x: (x["day"], list(cad["slots"]).index(x.get("slot", "morning")) if x.get("slot", "morning") in cad["slots"] else 9)):
        date = dates[p["day"] - 1]
        slot = p.get("slot", "morning")
        fmt = p.get("format", "")
        rows.append({
            "date": date.isoformat(), "weekday": WEEKDAYS[date.weekday()], "day": p["day"], "slot": slot,
            "time": cad["slots"].get(slot, ""), "platform": p.get("platform") or DEFAULT_PLATFORM.get(fmt, ""),
            "format": FORMAT_LABEL.get(fmt, fmt), "title": p.get("title", ""), "hook": p.get("hook", ""),
            "stage": p.get("stage", ""), "file": p.get("file", ""), "caption_file": p.get("caption_file", ""),
            "cta": p.get("cta", ""), "id": p.get("id", ""), "video_file": p.get("video_file", ""),
        })
        for key in ("file", "caption_file", "video_file"):
            if p.get(key) and not (base / p[key]).exists():
                warnings.append(f"{p.get('id')}: {key} not found: {p[key]}")

    per_day = Counter(r["date"] for r in rows)
    for d, n in per_day.items():
        if n > cad["max_per_day"]:
            warnings.append(f"{d} has {n} pieces (max {cad['max_per_day']})")
    if last_day > cad["horizon"]:
        warnings.append(f"Plan runs {last_day} posting days, longer than the {cad['horizon']}-day horizon")
    by_day_fmt = defaultdict(list)
    for r in rows:
        by_day_fmt[r["day"]].append(r["format"])
    for d in sorted(by_day_fmt):
        if d - 1 in by_day_fmt and by_day_fmt[d][0] == by_day_fmt[d - 1][0]:
            warnings.append(f"Day {d} repeats the same main format as day {d - 1} ({by_day_fmt[d][0]})")

    # csv
    with open(base / "content-calendar.csv", "w", newline="", encoding="utf-8") as fh:
        cols = ["date", "weekday", "day", "slot", "time", "platform", "format", "title", "hook", "stage", "file", "caption_file", "video_file", "cta", "id"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
        for p in bank:
            w.writerow({"date": "BANK", "format": FORMAT_LABEL.get(p.get("format", ""), p.get("format", "")), "title": p.get("title", ""),
                        "hook": p.get("hook", ""), "stage": p.get("stage", ""), "file": p.get("file", ""), "id": p.get("id", "")})

    # markdown
    md = [f"# Content calendar: {plan.get('title', 'Your content')}", "",
          f"Starts {cad['start'].strftime('%A, %B %d')}. {len(rows)} pieces scheduled across {len(per_day)} posting days. {len(bank)} saved in the content bank.", ""]
    by_date = defaultdict(list)
    for r in rows:
        by_date[r["date"]].append(r)
    for date in sorted(by_date):
        items = by_date[date]
        d = dt.date.fromisoformat(date)
        md.append(f"## {d.strftime('%A, %B %d')} (Day {items[0]['day']})")
        for r in items:
            md.append(f"- [ ] **{r['time']}** {r['platform']} {r['format']}: {r['title']}")
            if r["hook"]:
                md.append(f"    - Hook: {r['hook']}")
            if r["file"]:
                md.append(f"    - Files: `{r['file']}`" + (f" and `{r['caption_file']}`" if r["caption_file"] else ""))
            if r["video_file"]:
                md.append(f"    - Animated version: `{r['video_file']}`")
            if r["cta"]:
                md.append(f"    - Next step for your audience: {r['cta']}")
        md.append("")
    if bank:
        md += ["## Content bank (post these later)", ""]
        for p in bank:
            md.append(f"- {FORMAT_LABEL.get(p.get('format', ''), p.get('format', ''))}: {p.get('title', '')}" + (f" (`{p['file']}`)" if p.get("file") else ""))
        md.append("")
    (base / "content-calendar.md").write_text("\n".join(md), encoding="utf-8")

    # html
    h = ['<!doctype html><meta charset="utf-8"><title>Content calendar</title><style>'
         'body{font:15px/1.45 system-ui,sans-serif;max-width:820px;margin:30px auto;padding:0 18px;color:#222}'
         'h1{font-size:24px}h2{font-size:16px;margin:26px 0 8px;padding-bottom:4px;border-bottom:2px solid #222}'
         '.item{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #eee}.time{width:78px;font-weight:700;flex:none}'
         '.meta{color:#666;font-size:13px}.tag{display:inline-block;background:#eee;border-radius:4px;padding:1px 7px;font-size:12px;margin-right:6px}'
         '@media print{body{margin:0}h2{break-after:avoid}.item{break-inside:avoid}}</style>',
         f"<h1>Content calendar: {html.escape(plan.get('title', 'Your content'))}</h1>"]
    for date in sorted(by_date):
        items = by_date[date]
        d = dt.date.fromisoformat(date)
        h.append(f"<h2>{d.strftime('%A, %B %d')} &middot; Day {items[0]['day']}</h2>")
        for r in items:
            h.append(f"<div class='item'><div class='time'>{html.escape(r['time'])}</div><div><span class='tag'>{html.escape(r['platform'])}</span>"
                     f"<span class='tag'>{html.escape(r['format'])}</span><strong>{html.escape(r['title'])}</strong>"
                     + (f"<div class='meta'>Hook: {html.escape(r['hook'])}</div>" if r["hook"] else "")
                     + (f"<div class='meta'>Files: {html.escape(r['file'])}</div>" if r["file"] else "")
                     + (f"<div class='meta'>Animated: {html.escape(r['video_file'])}</div>" if r["video_file"] else "")
                     + (f"<div class='meta'>Next step: {html.escape(r['cta'])}</div>" if r["cta"] else "") + "</div></div>")
    if bank:
        h.append("<h2>Content bank</h2><ul>" + "".join(f"<li>{html.escape(FORMAT_LABEL.get(p.get('format', ''), p.get('format', '')))}: {html.escape(p.get('title', ''))}</li>" for p in bank) + "</ul>")
    (base / "content-calendar.html").write_text("".join(h), encoding="utf-8")

    print(f"Calendar written: {len(rows)} scheduled, {len(bank)} in the bank, {len(per_day)} posting days")
    for wmsg in warnings:
        print("  WARN:", wmsg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
