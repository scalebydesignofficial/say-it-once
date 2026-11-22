#!/usr/bin/env python3
"""Carousel Studio: many layouts, a builder, a contact sheet, and a browser editor.

Usage:
    python3 scripts/carousel_studio.py gallery [--theme ID] [--photos DIR] [--out DIR]
    python3 scripts/carousel_studio.py new <folder> [--look editorial] [--theme brand] [--title "..."]
    python3 scripts/carousel_studio.py build <folder> [--format png|jpg]
    python3 scripts/carousel_studio.py sheet <folder>
    python3 scripts/carousel_studio.py edit <folder> [--no-open] [--port N]
    python3 scripts/carousel_studio.py themes

A carousel folder holds plan.json (the slides), photos/ (its pictures), and after a build:
slides/slide-01.png ..., contact-sheet.jpg (every slide on one page), and caption.txt.
Layouts live in design/carousel-studio/layouts.js and are shared with the editor, so the editor
shows exactly what the build makes.
"""
import argparse
import base64
import io
import json
import mimetypes
import pathlib
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402

STUDIO = E.DESIGN / "carousel-studio"
FONTS = E.DESIGN / "fonts"
W, H = 1080, 1350
PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")

# Old Say It Once slide types map onto Carousel Studio roles.
TYPE_TO_ROLE = {"cover": "cover", "point": "point", "list": "list", "checklist": "list", "quote": "quote",
                "close": "close", "stat": "stat", "versus": "compare"}


# ----------------------------------------------------------------- themes ----

def preset_themes():
    return E.load_json(STUDIO / "themes.json", {}).get("themes", [])


def _font_weights():
    out = {}
    for fam in E.load_json(FONTS / "fonts.json", {}).get("families", []):
        out[fam["family"]] = fam.get("weights", [400])
    return out


def _mix(a, b, t):
    """t of color a, the rest color b (hex)."""
    try:
        x = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
        y = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
        return "#" + "".join(f"{round(x[i] * t + y[i] * (1 - t)):02X}" for i in range(3))
    except (ValueError, AttributeError, IndexError):
        return None


def brand_theme():
    b = E.load_brand()
    c, f = b.get("colors", {}), b.get("fonts", {})
    head = f.get("heading") or "Playfair Display"
    weights = _font_weights().get(head, [700])
    return {
        "id": "brand", "name": "My brand",
        "colors": {"bg": c.get("bg"), "ink": c.get("ink"), "accent": c.get("accent"), "accent2": c.get("accent2"),
                   "muted": c.get("muted"), "dark": c.get("bg_dark") or c.get("ink"),
                   "paper": _mix(c.get("bg") or "#FFFFFF", "#FFFFFF", 0.45)},
        "fonts": {"head": head, "body": f.get("body") or "Poppins", "script": f.get("accent") or "Caveat"},
        "head_weight": max(w for w in weights if w <= 700) if any(w <= 700 for w in weights) else weights[0],
        "head_case": "none", "head_track": "-0.01em", "kicker": "script", "quote_italic": True, "radius": 30,
    }


def all_themes():
    return [brand_theme()] + preset_themes()


def resolve_theme(plan):
    want = plan.get("theme") or "brand"
    base = next((t for t in all_themes() if t["id"] == want), None) or brand_theme()
    t = json.loads(json.dumps(base))
    over = plan.get("theme_overrides") or {}
    for key, val in over.items():
        if isinstance(val, dict):
            t.setdefault(key, {}).update({k: v for k, v in val.items() if v})
        elif val not in (None, ""):
            t[key] = val
    return t


def ctx_base(plan):
    b = E.load_brand()
    return {
        "name": plan.get("name") or b.get("name") or "",
        "handle": plan.get("handle") or b.get("handle") or "",
        "show_handle": plan.get("show_handle", True),
        "show_numbers": plan.get("show_numbers", True),
        "show_swipe": plan.get("show_swipe", True),
    }


# ------------------------------------------------------------------ plans ----

def from_pack_carousel(data):
    """Turn a Say It Once carousel.json into a Carousel Studio plan."""
    slides = []
    for s in data.get("slides", []):
        role = TYPE_TO_ROLE.get(s.get("type"), "point")
        n = {"role": role}
        for k in ("kicker", "headline", "body", "items", "number", "cta"):
            if s.get(k):
                n[k] = s[k]
        if s.get("type") == "quote":
            n["headline"] = s.get("text", "")
            if s.get("attribution"):
                n["sub"] = s["attribution"]
        if s.get("type") == "stat":
            n["headline"] = s.get("label", "")
        if s.get("type") == "versus":
            for k in ("left_label", "left", "right_label", "right"):
                if s.get(k):
                    n[k] = s[k]
        if s.get("type") == "close" and s.get("cta"):
            word = s["cta"].split()[-1]
            n["cta"] = word
        if isinstance(s.get("image"), str):
            n["photo"] = {"src": s["image"], "x": 50, "y": 50, "zoom": 1}
        slides.append(n)
    return {"title": data.get("title", ""), "look": "editorial", "theme": "brand", "caption": data.get("caption", ""),
            "slides": slides}


def load_plan(folder):
    folder = pathlib.Path(folder)
    p = folder / "plan.json"
    if p.exists():
        return E.load_json(p, {})
    old = folder / "carousel.json"
    if old.exists():
        plan = from_pack_carousel(E.load_json(old, {}))
        caption = folder / "caption.md"
        if caption.exists() and not plan.get("caption"):
            plan["caption"] = caption.read_text(encoding="utf-8").strip()
        save_plan(folder, plan)
        return plan
    sys.exit(f"No plan.json in {folder}. Make one with: python3 scripts/carousel_studio.py new {folder}")


def save_plan(folder, plan):
    folder = pathlib.Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def photo_dirs(folder):
    return [pathlib.Path(folder) / "photos", E.BRAND_DIR / "photos"]


def list_photos(folder):
    seen, out = set(), []
    for d in photo_dirs(folder):
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix.lower() in PHOTO_EXT and f.name not in seen:
                    seen.add(f.name)
                    out.append(f.name)
    return out


def find_photo(folder, name):
    if not name:
        return None
    p = pathlib.Path(name)
    if p.is_absolute() and p.exists():
        return p
    for d in photo_dirs(folder):
        if (d / name).exists():
            return d / name
    return None


# ---------------------------------------------------------------- the page ----

def _theme_font_loads(theme):
    f = theme.get("fonts", {})
    w = theme.get("head_weight", 700)
    return [f"{w} 80px '{f.get('head')}'", f"italic {w} 80px '{f.get('head')}'", f"400 40px '{f.get('body')}'",
            f"500 40px '{f.get('body')}'", f"600 40px '{f.get('body')}'", f"700 40px '{f.get('body')}'",
            f"700 60px '{f.get('script')}'"]


def page_head(asset_url, font_css):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{asset_url('fonts/fonts.css')}">
<style>{font_css}</style>
<link rel="stylesheet" href="{asset_url('studio/layouts.css')}">
<script src="{asset_url('studio/layouts.js')}"></script>
<style>html,body{{margin:0;padding:0;background:#fff}}</style></head>"""


READY_JS = r"""
async function settle(el, loads){
  try{ await Promise.all((loads||[]).map(f=>document.fonts.load(f))); }catch(e){}
  await document.fonts.ready;
  await Promise.all([...el.querySelectorAll('img')].map(i=>i.decode().catch(()=>{})));
  el.querySelectorAll('.sio').forEach(s=>CarouselStudio.fit(s));
  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
}
"""


def file_asset_url(rel):
    top, rest = rel.split("/", 1)
    base = FONTS if top == "fonts" else STUDIO
    return (base / rest).resolve().as_uri()


class Shooter:
    """Opens headless Chrome once and photographs pages."""

    def __init__(self):
        import cdp
        self.b = cdp.Browser(W, H)

    def size(self, w, h):
        self.b.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)

    def open(self, path):
        self.b.open(path)

    def eval(self, js):
        return self.b.eval(js)

    def shot(self, out, w, h, fmt="png", quality=95):
        params = {"format": "jpeg" if fmt in ("jpg", "jpeg") else "png", "fromSurface": True, "captureBeyondViewport": True,
                  "clip": {"x": 0, "y": 0, "width": w, "height": h, "scale": 1}}
        if params["format"] == "jpeg":
            params["quality"] = quality
        r = self.b.call("Page.captureScreenshot", **params)
        pathlib.Path(out).write_bytes(base64.b64decode(r["data"]))

    def close(self):
        self.b.close()


# ------------------------------------------------------------------- build ----

def build(folder, fmt="png", quiet=False):
    folder = pathlib.Path(folder).resolve()
    plan = load_plan(folder)
    slides = plan.get("slides") or []
    if not slides:
        sys.exit("This plan has no slides yet.")
    if not E.find_chrome():
        sys.exit("I need Google Chrome (or Edge, Brave, Chromium) to make the images. Install Chrome, then try again.")
    theme = resolve_theme(plan)
    ctx = ctx_base(plan)
    ctx["theme"] = theme
    ctx["n"] = len(slides)
    photos = {}
    for s in slides:
        for key in ("photo", "photo2"):
            p = s.get(key)
            src = p.get("src") if isinstance(p, dict) else p
            found = find_photo(folder, src)
            if src and found:
                photos[src] = found.resolve().as_uri()
            elif src and not quiet:
                print(f"  note: photo '{src}' not found, that slide shows an empty photo spot")
    work = folder / "_studio"
    work.mkdir(exist_ok=True)
    page = work / "render.html"
    page.write_text(page_head(file_asset_url, E.custom_fonts_css()) + f"""<body><div id="stage"></div>
<script>{READY_JS}
const PLAN={json.dumps(plan, ensure_ascii=False)};
const CTX={json.dumps(ctx, ensure_ascii=False)};
const PHOTOS={json.dumps(photos)};
const LOADS={json.dumps(_theme_font_loads(theme))};
window.show=async function(i){{
  const c=Object.assign({{}},CTX,{{i:i,photoUrl:n=>PHOTOS[n]||n}});
  stage.innerHTML=CarouselStudio.render(PLAN.slides[i],c,PLAN);
  await settle(stage,LOADS); return CarouselStudio.layoutFor(PLAN.slides[i],PLAN);
}};
document.documentElement.setAttribute('data-ready','1');
</script></body></html>""", encoding="utf-8")
    out_dir = folder / "slides"
    if out_dir.exists():
        for old in out_dir.glob("slide-*.*"):
            old.unlink()
    out_dir.mkdir(exist_ok=True)
    ext = "jpg" if fmt in ("jpg", "jpeg") else "png"
    shooter = Shooter()
    made = []
    try:
        shooter.open(page)
        for i in range(len(slides)):
            layout = shooter.eval(f"show({i})")
            out = out_dir / f"slide-{i + 1:02d}.{ext}"
            shooter.shot(out, W, H, ext)
            made.append((out, layout))
            if not quiet:
                print(f"  slide {i + 1}: {layout}")
        sheet = contact_sheet(folder, plan, [m[0] for m in made], [m[1] for m in made], shooter)
    finally:
        shooter.close()
    cap = (plan.get("caption") or "").strip()
    (folder / "caption.txt").write_text(cap + "\n" if cap else "", encoding="utf-8")
    if not quiet:
        print(f"Made {len(made)} slides in {out_dir}")
        print(f"Contact sheet: {sheet}")
    return [m[0] for m in made], sheet


def contact_sheet(folder, plan, images, layouts, shooter=None):
    """Every slide on one page, numbered, with its kind of slide and layout name."""
    folder = pathlib.Path(folder)
    names = {}
    try:
        txt = (STUDIO / "layouts.js").read_text(encoding="utf-8")
        import re
        for m in re.finditer(r'id: "([^"]+)", name: "([^"]+)"', txt):
            names[m.group(1)] = m.group(2)
    except OSError:
        pass
    cols = 4 if len(images) > 6 else 3 if len(images) > 4 else max(1, len(images))
    tw, th, gap, pad, lab = 360, 450, 28, 44, 64
    rows = (len(images) + cols - 1) // cols
    sw = pad * 2 + cols * tw + (cols - 1) * gap
    sh = pad * 2 + 70 + rows * (th + lab) + (rows - 1) * gap
    cells = []
    for i, (img, lay) in enumerate(zip(images, layouts)):
        role = (plan["slides"][i].get("role") or "").strip()
        cells.append(f'<div class="c"><img src="{pathlib.Path(img).resolve().as_uri()}?t={time.time()}"><div class="l"><b>{i + 1}</b>'
                     f'<span>{role + " · " if role else ""}{names.get(lay, lay)}</span></div></div>')
    title = (plan.get("title") or folder.name).replace("<", "")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{file_asset_url('fonts/fonts.css')}">
<style>body{{margin:0;background:#F3F0EA;font-family:'DM Sans','Inter',sans-serif;color:#222}}
.w{{padding:{pad}px}} h1{{margin:0 0 26px;font:700 34px 'DM Sans',sans-serif}}
.g{{display:grid;grid-template-columns:repeat({cols},{tw}px);gap:{gap}px}}
.c img{{width:{tw}px;height:{th}px;display:block;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,.12)}}
.l{{height:{lab}px;display:flex;align-items:center;gap:12px;font-size:22px}} .l b{{font-size:26px}} .l span{{opacity:.7}}</style></head>
<body><div class="w"><h1>{title}</h1><div class="g">{''.join(cells)}</div></div>
<script>Promise.all([...document.images].map(i=>i.decode().catch(()=>{{}}))).then(()=>document.fonts.ready).then(()=>document.documentElement.setAttribute('data-ready','1'))</script></body></html>"""
    page = folder / "_studio" / "sheet.html"
    page.parent.mkdir(exist_ok=True)
    page.write_text(html, encoding="utf-8")
    own = shooter is None
    shooter = shooter or Shooter()
    try:
        shooter.size(sw, sh)
        shooter.open(page)
        out = folder / "contact-sheet.jpg"
        shooter.shot(out, sw, sh, "jpg", 90)
        shooter.size(W, H)
    finally:
        if own:
            shooter.close()
    return out


# ----------------------------------------------------------------- gallery ----

SAMPLE = {
    "cover": {"kicker": "for the woman who keeps waiting", "headline": "You don't need more **clarity.** You need a first step.",
              "body": "Swipe for the one thing that changes it.", "cta": "Swipe"},
    "point": {"kicker": "here's the truth", "headline": "Waiting to feel ready is still **waiting.**",
              "body": "Readiness shows up after you move, not before. Start small and let it find you on the way."},
    "list": {"kicker": "try this week", "headline": "Five small ways to move",
             "items": ["Write the one step on paper", "Give it ten minutes today", "Tell one friend", "Pray, then do it anyway", "Celebrate that you started"]},
    "quote": {"kicker": "say it with me", "headline": "A setback in God's hands can become a whole **setup.**", "sub": "Your name"},
    "stat": {"kicker": "real talk", "number": "80%", "headline": "of the plan shows up after you start",
             "body": "The rest of the path lights up one step at a time."},
    "compare": {"headline": "What we tell ourselves", "left_label": "Myth", "left": "I'll start when I feel ready.",
                "right_label": "Truth", "right": "Ready comes **after** you start."},
    "close": {"kicker": "hey, I'm so glad you're here", "headline": "Want the 7 day plan?", "cta": "MOVE",
              "body": "Comment the word and I'll send it to you."},
}
SAMPLE_BY_LAYOUT = {
    "definition": {"headline": "obedience", "kicker": "noun, /oh-bee-dee-ence/", "body": "Moving on what God already said, before you feel ready.",
                   "sub": "\"She chose obedience over comfort.\""},
    "question": {"kicker": "be honest", "headline": "What would you do if you **knew** it would work?"},
    "before-after": {"left_label": "Before", "left": "I'll do it when life calms down.", "right_label": "After", "right": "I do it in the middle of it."},
    "side-by-side": {"headline": "Small steps win", "left_label": "Not this", "left": "Waiting for the perfect plan", "right_label": "This",
                     "right": "Ten honest minutes a day"},
    "cta-save": {"headline": "Save this for the day you **doubt.**", "body": "Then send it to a woman who needs it.", "cta": "Save + share"},
    "cta-follow": {"headline": "Follow for faith-filled nudges", "body": "One small step at a time.", "cta": "Follow"},
    "quote-post": {"headline": "Being needed is NOT the same as being **supported.**"},
    "stat-ring": {"number": "3 of 4", "headline": "women say they're waiting on a feeling", "body": "Not a sign. A feeling."},
    "grid-four": {"kicker": "the four rhythms", "headline": "Build it weekly", "items": ["Rest on purpose", "Plan one brave thing", "Do it scared", "Look back and thank God"]},
    "outline-word": {"kicker": "remember this", "headline": "Start before you're **READY.**", "body": "Courage is a decision, not a feeling."},
    "color-block": {"kicker": "real talk", "headline": "Your yes doesn't need **everyone's** approval.", "body": "Just His, and yours."},
}


def gallery(theme_id=None, photo_dir=None, out_dir=None, quiet=False):
    """Every layout with sample words, on one page, in one theme."""
    out_dir = pathlib.Path(out_dir or (E.DESIGN / "carousel-studio" / "gallery")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = {"theme": theme_id or "brand"}
    theme = resolve_theme(plan)
    pics = []
    if photo_dir:
        pics = [p for p in sorted(pathlib.Path(photo_dir).iterdir()) if p.suffix.lower() in PHOTO_EXT]
    if not pics:
        pics = [p for p in sorted((E.BRAND_DIR / "photos").glob("*")) if p.suffix.lower() in PHOTO_EXT]
    pic_uris = [p.resolve().as_uri() for p in pics]
    ctx = ctx_base(plan)
    ctx["theme"] = theme
    page = out_dir / "gallery-render.html"
    page.write_text(page_head(file_asset_url, E.custom_fonts_css()) + f"""<body>
<style>body{{background:#EEEAE3;font-family:'DM Sans',sans-serif;color:#222}}
.wrap{{padding:48px 56px 60px;width:max-content}}
h1{{font:700 44px 'DM Sans',sans-serif;margin:0 0 6px}} .sub{{font-size:22px;opacity:.65;margin-bottom:24px}}
h2{{font:700 26px 'DM Sans',sans-serif;letter-spacing:.14em;text-transform:uppercase;margin:34px 0 16px;opacity:.75}}
.row{{display:flex;gap:26px;flex-wrap:nowrap}}
.cell{{width:324px}} .mini{{width:324px;height:405px;overflow:hidden;border-radius:10px;box-shadow:0 6px 18px rgba(0,0,0,.14);position:relative}}
.mini>.sio{{transform:scale(.3);transform-origin:0 0;position:absolute;left:0;top:0}}
.lab{{font-size:21px;margin-top:10px;display:flex;gap:10px}} .lab b{{min-width:28px}} .lab i{{font-style:normal;opacity:.55}}</style>
<div class="wrap" id="wrap"></div>
<script>{READY_JS}
const CTX={json.dumps(ctx, ensure_ascii=False)};
const PICS={json.dumps(pic_uris)};
const SAMPLE={json.dumps(SAMPLE, ensure_ascii=False)};
const BYL={json.dumps(SAMPLE_BY_LAYOUT, ensure_ascii=False)};
const LOADS={json.dumps(_theme_font_loads(theme))};
const ROWMAX=6;
(async function(){{
  const groups={{}}; CarouselStudio.LAYOUTS.forEach(d=>(groups[d.group]=groups[d.group]||[]).push(d));
  let html='<h1>Carousel Studio layouts</h1><div class="sub">'+CarouselStudio.LAYOUTS.length+' layouts · theme: {theme.get("name", "")}</div>';
  let n=0, pi=0;
  for(const g of Object.keys(groups)){{
    html+='<h2>'+g+'</h2>';
    const list=groups[g];
    for(let r=0;r<list.length;r+=ROWMAX){{
      html+='<div class="row">';
      for(const d of list.slice(r,r+ROWMAX)){{
        n++;
        const role=d.roles[0];
        const s=Object.assign({{role:role,layout:d.id}},SAMPLE[role],BYL[d.id]||{{}});
        if(d.photos>0 && PICS.length){{ s.photo={{src:PICS[pi++%PICS.length],x:50,y:22,zoom:1}}; }}
        if(d.photos>1 && PICS.length){{ s.photo2={{src:PICS[pi++%PICS.length],x:50,y:22,zoom:1}}; }}
        const c=Object.assign({{}},CTX,{{i:(role==='close'?6:role==='cover'?0:2),n:7}});
        html+='<div class="cell"><div class="mini">'+CarouselStudio.render(s,c,{{}})+'</div><div class="lab"><b>'+n+'</b><span>'+d.name+'</span></div></div>';
      }}
      html+='</div>';
    }}
  }}
  wrap.innerHTML=html;
  await settle(wrap,LOADS);
  document.documentElement.setAttribute('data-h', wrap.offsetHeight);
  document.documentElement.setAttribute('data-w', wrap.offsetWidth);
  document.documentElement.setAttribute('data-ready','1');
}})();
</script></body></html>""", encoding="utf-8")
    shooter = Shooter()
    try:
        shooter.size(2200, 1200)
        shooter.open(page)
        w = int(shooter.eval("+document.documentElement.getAttribute('data-w')"))
        h = int(shooter.eval("+document.documentElement.getAttribute('data-h')"))
        shooter.size(w, h)
        time.sleep(0.3)
        out = out_dir / f"gallery-{theme['id']}.jpg"
        shooter.shot(out, w, h, "jpg", 88)
    finally:
        shooter.close()
    if not quiet:
        print(f"Gallery: {out}")
    return out


# ------------------------------------------------------------------ editor ----

def new_carousel(folder, look="editorial", theme="brand", title=""):
    folder = pathlib.Path(folder)
    if (folder / "plan.json").exists():
        sys.exit(f"{folder} already has a plan.json. Open it with: python3 scripts/carousel_studio.py edit {folder}")
    (folder / "photos").mkdir(parents=True, exist_ok=True)
    plan = {"title": title or folder.name, "look": look, "theme": theme, "caption": "",
            "slides": [{"role": r, **{k: v for k, v in SAMPLE[r].items()}} for r in ("cover", "point", "list", "quote", "close")]}
    save_plan(folder, plan)
    print(f"Made {folder / 'plan.json'} with 5 starter slides.")


class EditorHandler(BaseHTTPRequestHandler):
    folder = None
    backed_up = False

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".woff2":
            ctype = "font/woff2"
        self._send(200, path.read_bytes(), ctype)

    def _safe(self, base, rel):
        base = pathlib.Path(base).resolve()
        p = (base / urllib.parse.unquote(rel)).resolve()
        return p if str(p).startswith(str(base)) else None

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        f = self.folder
        if p in ("/", "/index.html"):
            return self._file(STUDIO / "editor.html")
        if p.startswith("/studio/"):
            return self._file(self._safe(STUDIO, p[len("/studio/"):]) or "")
        if p.startswith("/fonts/"):
            return self._file(self._safe(FONTS, p[len("/fonts/"):]) or "")
        if p == "/brandfonts.css":
            css = E.custom_fonts_css()
            d = (E.BRAND_DIR / "fonts").resolve().as_uri()
            return self._send(200, css.replace(d + "/", "/brandfont/"), "text/css")
        if p.startswith("/brandfont/"):
            return self._file(self._safe(E.BRAND_DIR / "fonts", p[len("/brandfont/"):]) or "")
        if p.startswith("/photo/"):
            name = urllib.parse.unquote(p[len("/photo/"):])
            return self._file(find_photo(f, pathlib.Path(name).name) or "")
        if p.startswith("/out/"):
            return self._file(self._safe(f, p[len("/out/"):]) or "")
        if p == "/api/state":
            plan = load_plan(f)
            fonts = [x["family"] for x in E.load_json(FONTS / "fonts.json", {}).get("families", [])]
            custom = sorted({pathlib.Path(x).stem.split("-")[0].split("_")[0] for x in (E.BRAND_DIR / "fonts").glob("*")
                             if pathlib.Path(x).suffix.lower() in (".woff2", ".woff", ".ttf", ".otf")}) if (E.BRAND_DIR / "fonts").exists() else []
            return self._send(200, {"plan": plan, "themes": all_themes(), "photos": list_photos(f), "ctx": ctx_base(plan),
                                    "fonts": custom + fonts, "folder": str(f)})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        f = self.folder
        if u.path == "/api/save":
            plan = json.loads(self._body() or b"{}")
            if not EditorHandler.backed_up and (f / "plan.json").exists():
                shutil.copy2(f / "plan.json", f / "plan.before-edit.json")
                EditorHandler.backed_up = True
            save_plan(f, plan)
            return self._send(200, {"ok": True})
        if u.path == "/api/upload":
            q = urllib.parse.parse_qs(u.query)
            name = pathlib.Path(q.get("name", ["photo.jpg"])[0]).name
            stem, ext = pathlib.Path(name).stem, pathlib.Path(name).suffix.lower()
            if ext not in PHOTO_EXT:
                return self._send(400, {"error": "Photos need to be .jpg, .png or .webp"})
            d = f / "photos"
            d.mkdir(exist_ok=True)
            out, k = d / f"{stem}{ext}", 2
            while out.exists():
                out, k = d / f"{stem}-{k}{ext}", k + 1
            out.write_bytes(self._body())
            return self._send(200, {"ok": True, "name": out.name, "photos": list_photos(f)})
        if u.path == "/api/export":
            opts = json.loads(self._body() or b"{}")
            try:
                images, sheet = build(f, opts.get("format", "png"), quiet=True)
            except SystemExit as e:
                return self._send(500, {"error": str(e)})
            except Exception as e:  # noqa: BLE001
                return self._send(500, {"error": f"The export stopped: {e}"})
            zp = f / f"{f.name}-carousel.zip"
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                for img in images:
                    z.write(img, img.name)
                z.write(f / "caption.txt", "caption.txt")
                z.write(sheet, sheet.name)
            rel = lambda p: "/out/" + urllib.parse.quote(str(pathlib.Path(p).relative_to(f)))  # noqa: E731
            return self._send(200, {"ok": True, "slides": [rel(i) for i in images], "sheet": rel(sheet), "zip": rel(zp),
                                    "folder": str(f)})
        if u.path == "/api/reveal":
            target = f / "slides" if (f / "slides").exists() else f
            opener = {"darwin": ["open"], "win32": ["explorer"]}.get(sys.platform, ["xdg-open"])
            try:
                subprocess.Popen(opener + [str(target)])
            except OSError:
                pass
            return self._send(200, {"ok": True})
        return self._send(404, {"error": "not found"})


def free_port(start=8765):
    for port in range(start, start + 50):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0


def edit(folder, open_browser=True, port=None):
    folder = pathlib.Path(folder).resolve()
    load_plan(folder)
    (folder / "photos").mkdir(exist_ok=True)
    EditorHandler.folder = folder
    port = port or free_port()
    srv = ThreadingHTTPServer(("127.0.0.1", port), EditorHandler)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"Carousel editor for {folder.name}: {url}")
    print("Leave this running while you edit. Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# -------------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gallery")
    g.add_argument("--theme")
    g.add_argument("--photos")
    g.add_argument("--out")
    n = sub.add_parser("new")
    n.add_argument("folder")
    n.add_argument("--look", default="editorial")
    n.add_argument("--theme", default="brand")
    n.add_argument("--title", default="")
    b = sub.add_parser("build")
    b.add_argument("folder")
    b.add_argument("--format", default="png", choices=["png", "jpg"])
    s = sub.add_parser("sheet")
    s.add_argument("folder")
    e = sub.add_parser("edit")
    e.add_argument("folder")
    e.add_argument("--no-open", action="store_true")
    e.add_argument("--port", type=int)
    sub.add_parser("themes")
    a = ap.parse_args()
    if a.cmd == "gallery":
        gallery(a.theme, a.photos, a.out)
    elif a.cmd == "new":
        new_carousel(a.folder, a.look, a.theme, a.title)
    elif a.cmd == "build":
        build(a.folder, a.format)
    elif a.cmd == "sheet":
        folder = pathlib.Path(a.folder).resolve()
        plan = load_plan(folder)
        imgs = sorted((folder / "slides").glob("slide-*.*"))
        if not imgs:
            sys.exit("No slides yet. Run build first.")
        import re
        lays = [p.get("layout") or "" for p in plan.get("slides", [])]
        print(contact_sheet(folder, plan, imgs, lays))
    elif a.cmd == "edit":
        edit(a.folder, not a.no_open, a.port)
    elif a.cmd == "themes":
        for t in all_themes():
            print(f"{t['id']:18} {t['name']}  ({t['fonts']['head']} / {t['fonts']['body']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
