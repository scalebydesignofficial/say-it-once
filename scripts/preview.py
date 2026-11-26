#!/usr/bin/env python3
"""Build a single page that shows every image in a finished pack.

Usage: python3 scripts/preview.py <batch-folder>
Writes 00-preview.html inside the folder.
"""
import html
import pathlib
import sys
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(sys.argv[1]).resolve()
    carousels = sorted({p.parent for p in root.rglob("slide-01.png")})
    quotes = sorted(root.rglob("quote-*.png"))
    h = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pack preview</title>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;1,400&family=Inter+Tight:wght@400;500&family=DM+Mono:wght@500&display=swap"><style>'
         'body{font:16px/1.6 "Inter Tight",system-ui,sans-serif;margin:0;background:#131313;color:#F5F5F5;-webkit-font-smoothing:antialiased}'
         '.wrap{max-width:1200px;margin:0 auto;padding:48px 24px 64px}'
         '.k{font:500 12px "DM Mono",ui-monospace,monospace;letter-spacing:.24em;text-transform:uppercase;color:#B5B2AA;margin:0 0 12px}'
         'h1{font:400 clamp(40px,6vw,72px)/1 "Libre Caslon Text",Georgia,serif;letter-spacing:-.03em;margin:0 0 8px}'
         'h1 em{font-style:italic;color:#B5B2AA}'
         'h2{font:400 30px/1.1 "Libre Caslon Text",Georgia,serif;letter-spacing:-.02em;margin:56px 0 6px}'
         'h3{font:500 12px "DM Mono",ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:#B5B2AA;margin:28px 0 10px}'
         '.row{display:flex;gap:12px;overflow-x:auto;padding-bottom:12px}'
         '.row img{height:360px;border-radius:4px;border:1.5px solid #2E2E2E;box-shadow:0 14px 34px rgba(0,0,0,.45);flex:none}'
         '.grid{display:flex;flex-wrap:wrap;gap:12px}.grid img{height:260px;border-radius:4px;border:1.5px solid #2E2E2E;box-shadow:0 14px 34px rgba(0,0,0,.45)}'
         '@media (max-width:560px){.row img{height:280px}.grid img{height:200px}}'
         '</style><div class="wrap"><p class="k">Your content pack</p><h1>Every <em>picture</em></h1>']
    if carousels:
        h.append("<h2>Carousels</h2>")
    for c in carousels:
        rel = c.relative_to(root)
        h.append(f"<h3>{html.escape(str(rel))}</h3><div class='row'>")
        for s in sorted(c.glob("slide-*.png")):
            h.append(f"<img src='{html.escape(str(s.relative_to(root)))}'>")
        h.append("</div>")
    if quotes:
        h.append("<h2>Quote graphics</h2><div class='grid'>")
        for q in quotes:
            h.append(f"<img src='{html.escape(str(q.relative_to(root)))}'>")
        h.append("</div>")
    h.append("</div>")
    (root / "00-preview.html").write_text("".join(h), encoding="utf-8")
    print(f"Preview: {len(carousels)} carousels, {len(quotes)} quote graphics -> {root / '00-preview.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
