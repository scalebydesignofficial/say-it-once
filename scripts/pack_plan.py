#!/usr/bin/env python3
"""Work out exactly what to make for one source: which formats and how many of each.

Usage:
    python3 scripts/pack_plan.py [--only GROUP_OR_FORMAT,...] [--size small|standard|big] [--words N]

Reads config.json: "formats" (what is switched on), "counts" (how many per source), and "pack_size".
--only limits this run to some groups or formats (it never turns on something that is switched off in settings,
unless you add --force-on). --size overrides pack_size for this run. --words is the source length: under 800
words halves every count, under 300 means "ask for more material".

Groups:
    visuals     carousel, quote
    video       reel, short_video
    posts       thread, note, instagram_post, instagram_story, facebook_post, linkedin_post, pinterest_pin
    longform    substack_article, blog, email, youtube
    talking     talking_points

Prints JSON: {"make": {"carousel": 5, ...}, "skipped": [...], "note": "..."}
"""
import argparse
import json
import pathlib
import sys
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIZE = {"small": 0.5, "standard": 1.0, "big": 1.5}
GROUPS = {
    "visuals": ["carousel", "quote"],
    "video": ["reel", "short_video"],
    "posts": ["thread", "note", "instagram_post", "instagram_story", "facebook_post", "linkedin_post", "pinterest_pin"],
    "longform": ["substack_article", "blog", "email", "youtube"],
    "talking": ["talking_points"],
}
ALL = [f for g in GROUPS.values() for f in g]
# Stories are switched on and off with Instagram posts.
FOLLOWS = {"instagram_story": "instagram_post"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only")
    ap.add_argument("--size", choices=list(SIZE))
    ap.add_argument("--words", type=int)
    ap.add_argument("--force-on", action="store_true")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    on = cfg.get("formats", {})
    counts = cfg.get("counts", {})
    size = a.size or cfg.get("pack_size", "standard")
    if size not in SIZE:
        size = "standard"
    mult = SIZE[size]
    note = []
    if a.words is not None:
        if a.words < 300:
            print(json.dumps({"make": {}, "skipped": [], "note": "Source is under 300 words. Ask for more material instead of padding."}))
            return 0
        if a.words < 800:
            mult *= 0.5
            note.append("Source under 800 words: counts halved.")

    wanted = None
    if a.only:
        wanted = set()
        for tok in [x.strip() for x in a.only.split(",") if x.strip()]:
            if tok in GROUPS:
                wanted.update(GROUPS[tok])
            elif tok in ALL:
                wanted.add(tok)
            else:
                sys.exit(f"Unknown group or format '{tok}'. Groups: {', '.join(GROUPS)}. Formats: {', '.join(ALL)}")

    make, skipped = {}, []
    for f in ALL:
        enabled = bool(on.get(FOLLOWS.get(f, f), False))
        if wanted is not None and f not in wanted:
            continue
        if not enabled and not a.force_on:
            skipped.append(f)
            continue
        base = 1 if f == "talking_points" else int(counts.get(f, 0))
        n = 1 if f == "talking_points" else max(1, round(base * mult)) if base else 0
        if n:
            make[f] = n
    if wanted is not None:
        off = [f for f in skipped if f in wanted]
        if off:
            note.append("Switched off in settings, so not included: " + ", ".join(off) + ". Offer to switch them on.")
    note.append(f"Size: {size}.")
    print(json.dumps({"make": make, "skipped": skipped, "note": " ".join(note)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
