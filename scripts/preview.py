#!/usr/bin/env python3
"""Build a single page that shows every image in a finished pack.

Usage: python3 scripts/preview.py <batch-folder>
Writes 00-preview.html inside the folder.
"""
import html
import pathlib
import sys


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(sys.argv[1]).resolve()
    carousels = sorted({p.parent for p in root.rglob("slide-01.png")})
    quotes = sorted(root.rglob("quote-*.png"))
    h = ['<!doctype html><meta charset="utf-8"><title>Pack preview</title><style>'
         'body{font:15px system-ui,sans-serif;margin:24px;background:#f4f4f4;color:#222}'
         'h1{font-size:22px}h2{font-size:17px;margin:34px 0 8px}'
         '.row{display:flex;gap:10px;overflow-x:auto;padding-bottom:10px}'
         '.row img{height:360px;border-radius:6px;box-shadow:0 2px 8px #0002;flex:none}'
         '.grid{display:flex;flex-wrap:wrap;gap:10px}.grid img{height:260px;border-radius:6px;box-shadow:0 2px 8px #0002}'
         '</style><h1>Your pack</h1>']
    if carousels:
        h.append("<h1>Carousels</h1>")
    for c in carousels:
        rel = c.relative_to(root)
        h.append(f"<h2>{html.escape(str(rel))}</h2><div class='row'>")
        for s in sorted(c.glob("slide-*.png")):
            h.append(f"<img src='{html.escape(str(s.relative_to(root)))}'>")
        h.append("</div>")
    if quotes:
        h.append("<h1>Quote graphics</h1><div class='grid'>")
        for q in quotes:
            h.append(f"<img src='{html.escape(str(q.relative_to(root)))}'>")
        h.append("</div>")
    (root / "00-preview.html").write_text("".join(h), encoding="utf-8")
    print(f"Preview: {len(carousels)} carousels, {len(quotes)} quote graphics -> {root / '00-preview.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
