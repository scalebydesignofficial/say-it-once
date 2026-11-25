#!/usr/bin/env python3
"""Turn carousel and quote-graphic JSON files into PNG images (and a PDF per carousel).

Usage:
    python3 scripts/render.py <file-or-folder> [--layout NAME] [--no-pdf]

A carousel JSON has {"title", "slides": [...], "caption"}.
A quote-graphics JSON has {"quotes": [{"text", "ref"?}, ...]}.
Images are written next to the JSON file. Layout and colors come from brand/brand.json.
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def collect(target):
    target = pathlib.Path(target)
    if target.is_file():
        return [target]
    found = []
    for p in sorted(target.rglob("*.json")):
        if p.name.startswith("_") or "_html" in p.parts or p.name in ("plan.json",):
            continue
        if ".before-edit" in p.name or p.name.startswith("plan"):
            continue  # editor backups and plans are not content
        if (p.parent / "plan.json").exists():
            continue  # anything next to a Carousel Studio plan is made by Carousel Studio (scripts/carousel_studio.py pack)
        data = E.load_json(p, {})
        if isinstance(data, dict) and ("slides" in data or "quotes" in data):
            found.append(p)
    return found


def pick_layout(kind, brand, override, index, data):
    avail = E.list_layouts()
    if data.get("layout") in avail:
        return data["layout"]
    if override:
        if override not in avail:
            sys.exit(f"Unknown layout '{override}'. Choices: {', '.join(avail)}")
        return override
    chosen = [n for n in brand["layouts"].get(kind, []) if n in avail] or [next(iter(avail))]
    return chosen[index % len(chosen)]


def render_carousel(path, brand, layout, make_pdf):
    data = E.load_json(path, {})
    slides = data.get("slides") or []
    if not slides:
        print(f"skip {path}: no slides")
        return []
    w, h = E.SIZES.get(brand.get("size"), E.SIZES["portrait"])
    out_dir = path.parent
    html_dir = out_dir / "_html"
    html_dir.mkdir(exist_ok=True)
    logo = E.logo_uri(brand)
    font_base = (E.DESIGN / "fonts").resolve().as_uri() + "/"
    jobs, bodies = [], []
    seed = data.get("title") or path.parent.name
    E.assign_photos(slides, brand, offset=0)
    for i, s in enumerate(slides):
        s["_seed"] = seed
        body = E.build_slide(s, i, len(slides), brand, layout, "carousel", logo)
        bodies.append(body)
        hp = html_dir / f"slide-{i + 1:02d}.html"
        hp.write_text(E.page_html(body, brand, [layout], font_base), encoding="utf-8")
        jobs.append((hp, out_dir / f"slide-{i + 1:02d}.png", w, h))
    E.capture_many(jobs)
    made = [str(j[1]) for j in jobs]
    if make_pdf:
        hp = html_dir / "carousel.html"
        hp.write_text(E.page_html("".join(bodies), brand, [layout], font_base, pdf=True), encoding="utf-8")
        E.capture_pdf(hp, out_dir / "carousel.pdf")
        made.append(str(out_dir / "carousel.pdf"))
    return made


def render_quotes(path, brand, layout):
    data = E.load_json(path, {})
    quotes = data.get("quotes") or []
    w, h = E.SIZES.get(brand.get("size"), E.SIZES["portrait"])
    out_dir = path.parent
    html_dir = out_dir / "_html"
    html_dir.mkdir(exist_ok=True)
    logo = E.logo_uri(brand)
    font_base = (E.DESIGN / "fonts").resolve().as_uri() + "/"
    avail = [n for n in brand["layouts"].get("quote", []) if n in E.list_layouts()] or [layout]
    quotes = [({"text": q} if isinstance(q, str) else dict(q)) for q in quotes]
    E.assign_photos(quotes, {**brand, "photos": {**(brand.get("photos") or {}), "types": ["quote"]}} , offset=0)
    for q in quotes:
        q.setdefault("type", "quote")
    jobs = []
    for i, q in enumerate(quotes):
        q = {"text": q} if isinstance(q, str) else dict(q)
        q["_seed"] = f"{path.parent.name}-{i}"
        lay = layout if len(avail) == 1 else avail[i % len(avail)]
        body = E.build_slide(q, 0, 1, brand, lay, "single", logo)
        hp = html_dir / f"quote-{i + 1:02d}.html"
        hp.write_text(E.page_html(body, brand, [lay], font_base), encoding="utf-8")
        jobs.append((hp, out_dir / f"quote-{i + 1:02d}.png", w, h))
    E.capture_many(jobs)
    return [str(j[1]) for j in jobs]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--layout")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    if not E.find_chrome():
        sys.exit("No Chrome, Edge, Brave, or Chromium found. Install Google Chrome (free) and run this again.")
    brand = E.load_brand()
    files = collect(args.target)
    if not files:
        sys.exit(f"No carousel or quote JSON files found in {args.target}")

    total, car_i = 0, 0
    for f in files:
        data = E.load_json(f, {})
        try:
            if "quotes" in data:
                layout = pick_layout("quote", brand, args.layout, 0, data)
                made = render_quotes(f, brand, layout)
            else:
                layout = pick_layout("carousel", brand, args.layout, car_i, data)
                made = render_carousel(f, brand, layout, not args.no_pdf)
                car_i += 1
        except Exception as exc:  # keep going so one bad file does not stop the batch
            print(f"FAILED {f}: {exc}")
            continue
        total += len(made)
        print(f"ok  {f.parent.name}/{f.name}  layout={layout}  files={len(made)}")
    print(f"Done. {total} file(s) written.")


if __name__ == "__main__":
    main()
