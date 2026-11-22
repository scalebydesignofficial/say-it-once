#!/usr/bin/env python3
"""Shared code for Say It Once: brand loading, slide HTML, and Chrome capture.

Uses only the Python standard library. Images are made by the Chrome (or Edge,
Brave, Chromium) already installed on the computer, so there is nothing to install.
"""
import base64
import concurrent.futures
import html
import json
import os
import pathlib
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design"
BRAND_DIR = ROOT / "brand"

SIZES = {"portrait": (1080, 1350), "square": (1080, 1080), "story": (1080, 1920)}

DEFAULT_BRAND = {
    "name": "Your Brand",
    "handle": "@yourhandle",
    "colors": {
        "bg": "#FAF7F2",
        "ink": "#1D1B20",
        "accent": "#2F5D62",
        "accent2": "#CFE3DD",
        "muted": "#6F6A73",
        "bg_dark": "#17141B",
    },
    "fonts": {"heading": "Playfair Display", "body": "Lato", "accent": "Caveat"},
    "size": "portrait",
    "layouts": {"carousel": ["editorial"], "quote": ["bold-block"]},
    "cta_label": "Follow for more",
    "logo": "brand/logo.png",
    "show_handle": True,
    "show_logo": True,
    "show_swipe": True,
    "show_page_numbers": True,
    "decor": "light",
    "decor_theme": "playful",
    "bg_style": "flat",
    "highlight": "layout",
    "photos": {"auto": True, "types": ["cover", "close", "quote"], "tone": "dark", "scrim": 0.55},
    "animation": {"seconds": 4.6, "fps": 24, "style": "words"},
}

PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")
TYPES = ("cover", "point", "list", "quote", "close", "stat", "versus", "checklist")


_FIT_JS = """
function fitAll(){
  document.querySelectorAll('.slide .content').forEach(function(c){
    var s=c.querySelector('.stack'); if(!s) return;
    var sl=c.closest('.slide');
    var cap=sl.classList.contains('slide--cover')?1.2:(sl.classList.contains('slide--list')||sl.classList.contains('slide--checklist')?1.25:(sl.classList.contains('slide--stat')?1.15:1.6));
    var f=1, g=0; c.style.setProperty('--fit','1');
    while(s.offsetHeight<c.clientHeight*0.5 && f<cap && g<40){ f+=0.04; c.style.setProperty('--fit',f.toFixed(3)); g++; }
    g=0;
    while(s.offsetHeight>c.clientHeight*0.94 && f>0.42 && g<120){ f-=0.025; c.style.setProperty('--fit',f.toFixed(3)); g++; }
  });
}
window.fitAll=fitAll;
(document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){
  fitAll(); if(window.buildAnim){ window.buildAnim(); } document.documentElement.setAttribute('data-ready','1');
});
"""


# ---------------------------------------------------------------- brand ----

def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def _merge(base, extra):
    out = json.loads(json.dumps(base))
    for key, val in (extra or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key].update(val)
        else:
            out[key] = val
    return out


def load_brand():
    return _merge(DEFAULT_BRAND, load_json(BRAND_DIR / "brand.json", {}))


def brand_is_set():
    return (BRAND_DIR / "brand.json").exists()


def norm_hex(value, fallback):
    v = str(value or "").strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        v = "#" + "".join(ch * 2 for ch in v[1:])
    return v.upper() if re.fullmatch(r"#[0-9a-fA-F]{6}", v) else fallback


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def on_color(bg):
    return "#FFFFFF" if contrast(bg, "#FFFFFF") >= contrast(bg, "#141414") else "#141414"


def font_catalog():
    return load_json(DESIGN / "fonts" / "fonts.json", {"families": [], "pairings": []})


def _stack_for(family):
    for f in font_catalog().get("families", []):
        if f["family"].lower() == str(family).lower():
            cat = f["category"]
            tail = {"serif": "Georgia, serif", "script": "cursive", "mono": "monospace"}.get(cat, "Arial, sans-serif")
            return f"'{f['family']}', {tail}"
    return f"'{family}', Arial, sans-serif"


def brand_vars(brand):
    c = brand["colors"]
    d = DEFAULT_BRAND["colors"]
    col = {k: norm_hex(c.get(k), d[k]) for k in d}
    f = brand["fonts"]
    w, h = SIZES.get(brand.get("size"), SIZES["portrait"])
    return {
        "--w": f"{w}px", "--h": f"{h}px",
        "--bg": col["bg"], "--ink": col["ink"], "--accent": col["accent"],
        "--accent2": col["accent2"], "--muted": col["muted"], "--bg-dark": col["bg_dark"],
        "--on-accent": on_color(col["accent"]), "--on-accent2": on_color(col["accent2"]),
        "--on-dark": on_color(col["bg_dark"]),
        "--font-head": _stack_for(f.get("heading", "Playfair Display")),
        "--font-body": _stack_for(f.get("body", "Lato")),
        "--font-accent": _stack_for(f.get("accent") or f.get("heading", "Playfair Display")),
    }


def root_css(brand):
    inner = ";".join(f"{k}:{v}" for k, v in brand_vars(brand).items())
    return f":root{{{inner}}}"


# --------------------------------------------------------------- layouts ----

def list_layouts():
    out = {}
    base = DESIGN / "layouts"
    if base.exists():
        for d in sorted(base.iterdir()):
            if (d / "layout.css").exists():
                meta = load_json(d / "meta.json", {})
                meta.setdefault("label", d.name.replace("-", " ").title())
                out[d.name] = meta
    return out


def layout_css(name):
    css = (DESIGN / "layouts" / name / "layout.css").read_text(encoding="utf-8")
    return re.sub(r"\.L(?![A-Za-z0-9_-])", f".layout--{name}", css)


def base_css():
    return (DESIGN / "base.css").read_text(encoding="utf-8")


def fonts_css(font_base_uri):
    css = (DESIGN / "fonts" / "fonts.css").read_text(encoding="utf-8")
    css = css.replace("url('", "url('" + font_base_uri)
    return css + "\n" + custom_fonts_css()


_WEIGHTS = [("extrabold", 800), ("semibold", 600), ("extralight", 200), ("black", 900), ("heavy", 900),
            ("bold", 700), ("medium", 500), ("light", 300), ("thin", 100), ("regular", 400)]


def custom_fonts_css():
    """Fonts a buyer drops into brand/fonts/ (their own paid or licensed fonts)."""
    d = BRAND_DIR / "fonts"
    rules = []
    if not d.exists():
        return ""
    fmt = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in fmt:
            continue
        stem = f.stem
        family = re.split(r"[-_]", stem)[0]
        low = stem.lower()
        weight = next((w for key, w in _WEIGHTS if key in low), 400)
        style = "italic" if "italic" in low else "normal"
        rules.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"src:url('{f.resolve().as_uri()}') format('{fmt[f.suffix.lower()]}');}}"
        )
    return "\n".join(rules)


# ------------------------------------------------------------------ html ----

def md(text):
    s = html.escape(str(text if text is not None else "").strip())
    s = re.sub(r"\*\*(.+?)\*\*", r'<strong class="hl">\1</strong>', s, flags=re.S)
    return s.replace("\n", "<br>")


def logo_uri(brand):
    p = ROOT / str(brand.get("logo") or "")
    if not p.is_file():
        for ext in ("png", "jpg", "jpeg", "svg", "webp"):
            alt = BRAND_DIR / f"logo.{ext}"
            if alt.is_file():
                p = alt
                break
        else:
            return None
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".webp": "image/webp"}.get(p.suffix.lower(), "image/png")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def _corner(brand, logo, side):
    if side == "left_brand":
        if brand.get("show_logo") and logo:
            return f'<img class="logo" src="{logo}" alt="">'
        return f'<span class="brandname">{md(brand.get("name", ""))}</span>'
    return ""


def list_photos():
    d = BRAND_DIR / "photos"
    if not d.exists():
        return []
    return [p for p in sorted(d.iterdir()) if p.suffix.lower() in PHOTO_EXT and not p.name.startswith(("_", "."))]


def resolve_photo(name):
    if not name or not isinstance(name, str):
        return None
    for cand in (pathlib.Path(name), BRAND_DIR / "photos" / name, ROOT / name):
        if cand.is_file():
            return cand.resolve().as_uri()
    return None


def assign_photos(slides, brand, offset=0):
    """Give eligible slides a photo from brand/photos when the buyer has some and slides have none."""
    cfg = brand.get("photos") or {}
    pics = list_photos()
    if not pics or not cfg.get("auto", True):
        return
    k = offset
    for s in slides:
        if s.get("image") is False or s.get("image"):
            continue
        if s.get("type") in (cfg.get("types") or ["cover", "close", "quote"]):
            s["image"] = pics[k % len(pics)].name
            k += 1


def layout_meta(name):
    return list_layouts().get(name, {})


def _tone(layout, t):
    tones = layout_meta(layout).get("tones", {})
    return tones.get(t) or tones.get("*") or "light"


def build_slide(slide, i, total, brand, layout, mode="carousel", logo=None):
    t = slide.get("type")
    if t not in TYPES:
        t = "cover" if i == 0 else "close" if i == total - 1 else "point"
    if mode == "single":
        t = "quote"
    classes = ["slide", f"slide--{t}", f"layout--{layout}"]
    handle = brand.get("handle", "") if brand.get("show_handle") else ""
    kicker = slide.get("kicker")
    kclass = "kicker num" if (kicker and re.fullmatch(r"\s*\d{1,2}\s*[./)]?\s*", str(kicker))) else "kicker"
    stack = []

    if t == "cover":
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        stack.append(f'<h1 class="headline">{md(slide.get("headline", ""))}</h1>')
        if slide.get("sub"):
            stack.append(f'<p class="sub">{md(slide["sub"])}</p>')
    elif t == "point":
        head, body = slide.get("headline"), slide.get("body")
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        if head:
            stack.append(f'<h2 class="headline">{md(head)}</h2>')
        if body:
            stack.append(f'<p class="body">{md(body)}</p>')
        if not (head and body):
            classes.append("solo")
    elif t == "list":
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        if slide.get("headline"):
            stack.append(f'<h2 class="headline">{md(slide["headline"])}</h2>')
        items = slide.get("items") or []
        lis = "".join(f'<li><span class="n">{n}</span><span class="t">{md(it)}</span></li>' for n, it in enumerate(items, 1))
        stack.append(f'<ol class="items">{lis}</ol>')
    elif t == "checklist":
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        if slide.get("headline"):
            stack.append(f'<h2 class="headline">{md(slide["headline"])}</h2>')
        tick = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5 L10 18 L20 6"/></svg>'
        lis = "".join(f'<li><span class="box">{tick}</span><span class="t">{md(it)}</span></li>' for it in (slide.get("items") or []))
        stack.append(f'<ul class="checks">{lis}</ul>')
    elif t == "stat":
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        stack.append(f'<div class="stat-num">{md(slide.get("number") or slide.get("stat") or slide.get("headline") or "")}</div>')
        if slide.get("label"):
            stack.append(f'<div class="stat-label">{md(slide["label"])}</div>')
        if slide.get("body"):
            stack.append(f'<p class="body">{md(slide["body"])}</p>')
    elif t == "versus":
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        if slide.get("headline"):
            stack.append(f'<h2 class="headline">{md(slide["headline"])}</h2>')
        stack.append(
            '<div class="vs">'
            f'<div class="vs-card vs-a"><div class="vs-tag">{md(slide.get("left_label") or "Myth")}</div><div class="vs-text">{md(slide.get("left", ""))}</div></div>'
            f'<div class="vs-card vs-b"><div class="vs-tag">{md(slide.get("right_label") or "Truth")}</div><div class="vs-text">{md(slide.get("right", ""))}</div></div>'
            '</div>')
    elif t == "quote":
        text = slide.get("text") or slide.get("headline") or slide.get("body") or ""
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        stack.append(f'<blockquote class="qtext">{md(text)}</blockquote>')
        attr = slide.get("attribution") or slide.get("ref")
        if attr:
            stack.append(f'<div class="attr">{md(attr)}</div>')
    else:  # close
        if kicker:
            stack.append(f'<div class="{kclass}">{md(kicker)}</div>')
        stack.append(f'<h2 class="headline">{md(slide.get("headline", ""))}</h2>')
        if slide.get("body"):
            stack.append(f'<p class="sub">{md(slide["body"])}</p>')
        cta = slide.get("cta") or brand.get("cta_label") or ""
        if cta:
            stack.append(f'<div class="cta">{md(cta)}</div>')

    if mode == "single":
        top_l, top_r = _corner(brand, logo, "left_brand"), ""
        bot_l, bot_r = f"<span>{md(handle)}</span>" if handle else "", ""
    else:
        top_l = f'<span class="handle">{md(handle or brand.get("name", ""))}</span>'
        top_r = f'<span class="pagenum">{i + 1:02d} / {total:02d}</span>' if (brand.get("show_page_numbers") and t != "cover") else ""
        bot_l = _corner(brand, logo, "left_brand")
        bot_r = '<span class="swipe">Swipe &rarr;</span>' if (brand.get("show_swipe") and i < total - 1) else ""

    # ---- photo, texture, decoration
    meta = layout_meta(layout)
    photo_html = ""
    uri = resolve_photo(slide.get("image")) if slide.get("image") else None
    tone = _tone(layout, t)
    style = []
    if uri:
        pcfg = brand.get("photos") or {}
        mode_p = meta.get("photo_mode", "background")
        classes += ["has-photo", "photo-bg" if mode_p == "background" else "photo-frame"]
        scrim = slide.get("scrim", pcfg.get("scrim", 0.55))
        style.append(f"--scrim:{float(scrim):.2f}")
        if slide.get("image_focus"):
            style.append(f"--focus:{html.escape(str(slide['image_focus']))}")
        light = (slide.get("tone") or pcfg.get("tone") or "dark") == "light"
        if mode_p == "background":
            if light:
                classes.append("photo-light")
            tone = "light" if light else "dark"
        photo_html = f'<div class="photo" style="background-image:url(\'{uri}\')"></div><div class="scrim"></div>'
    classes.append(f"tone-{tone}")
    hl = brand.get("highlight") or "layout"
    if hl != "layout":
        classes.append(f"hl-{hl}")
    bg = brand.get("bg_style") or "flat"
    studio = bool(brand.get("_studio"))
    tex = f'<div class="texture t-{bg}"></div>' if (studio or bg not in ("flat", "none", "")) else ""
    import decor as _decor
    seed = slide.get("_seed") or brand.get("name", "x")
    if studio:  # the studio switches theme and amount live, so it carries every theme
        decor_html = "".join(f'<div class="decor decor-{th}">{_decor.make_decor("rich", th, seed, t, i)}</div>' for th in _decor.THEMES)
    else:
        deco_level = slide.get("decor", brand.get("decor", "light"))
        if "photo-bg" in classes and deco_level == "rich":
            deco_level = "light"
        decor_html = _decor.make_decor(deco_level, brand.get("decor_theme", "playful"), seed, t, i) if deco_level not in ("none", False) else ""
        decor_html = f'<div class="decor">{decor_html}</div>' if decor_html else ""
    st = f' style="{";".join(style)}"' if style else ""

    return (
        f'<section class="{" ".join(classes)}"{st}>{photo_html}<div class="deco"></div>{tex}{decor_html}<div class="inner">'
        f'<div class="top">{top_l}{top_r}</div>'
        f'<div class="content"><div class="stack">{"".join(stack)}</div></div>'
        f'<div class="bottom">{bot_l}{bot_r}</div></div></section>'
    )


_TONE_HL_CSS = '''
.slide.tone-light{--hl-line:var(--accent);--hl-fill:color-mix(in srgb,var(--accent2) 85%,transparent);--hl-ink:var(--on-accent)}
.slide.tone-accent{--hl-line:var(--on-accent);--hl-fill:color-mix(in srgb,var(--on-accent) 28%,transparent);--hl-ink:var(--accent)}
.slide.tone-dark{--hl-line:var(--accent2);--hl-fill:color-mix(in srgb,var(--accent) 65%,transparent);--hl-ink:var(--on-accent2)}
'''


def page_html(body, brand, layouts, font_base_uri, pdf=False, anim=None):
    """anim: None for a still image, or {"dur": seconds, "lead": seconds} for an animatable page."""
    import decor as _decor
    w, h = SIZES.get(brand.get("size"), SIZES["portrait"])
    css = [fonts_css(font_base_uri), root_css(brand), base_css(), _decor.DECOR_CSS, _TONE_HL_CSS]
    css += [layout_css(n) for n in layouts]
    if pdf:
        css.append(f"@page{{size:{w}px {h}px;margin:0}}html,body{{background:none}}"
                   ".slide{break-after:page;page-break-after:always}")
    root_attr, pre = "", ""
    if anim:
        import animation as _anim
        css.append(_anim.ANIM_CSS)
        root_attr = f' class="anim" style="--dur:{anim.get("dur", 4)}s"'
        pre = f'<script>window.__LEAD={anim.get("lead", 0.35)};window.__DUR={anim.get("dur", 4)};{_anim.ANIM_JS}</script>'
    return (
        f'<!doctype html><html{root_attr}><head><meta charset="utf-8">'
        f'<style>{chr(10).join(css)}</style></head><body>{body}{pre}<script>{_FIT_JS}</script></body></html>'
    )


# ---------------------------------------------------------------- chrome ----

def find_chrome():
    env = os.environ.get("CHROME_PATH")
    if env and os.path.exists(env):
        return env
    system = platform.system()
    candidates = []
    if system == "Darwin":
        for app in ("Google Chrome", "Microsoft Edge", "Brave Browser", "Chromium"):
            candidates.append(f"/Applications/{app}.app/Contents/MacOS/{app}")
            candidates.append(os.path.expanduser(f"~/Applications/{app}.app/Contents/MacOS/{app}"))
    elif system == "Windows":
        roots = [os.environ.get(k) for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
        for r in filter(None, roots):
            candidates += [
                os.path.join(r, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(r, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(r, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge", "brave-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


_calib = {}
_calib_lock = threading.Lock()


def _png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def _run_chrome(extra, timeout=90):
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError(
            "No Chrome, Edge, Brave, or Chromium found. Install Google Chrome (free), "
            "or set the CHROME_PATH environment variable to your browser."
        )
    with tempfile.TemporaryDirectory(prefix="engine-chrome-") as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", "--allow-file-access-from-files",
               "--force-device-scale-factor=1", "--disable-dev-shm-usage", f"--user-data-dir={profile}"]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.append("--no-sandbox")
        cmd += extra
        return subprocess.run(cmd, capture_output=True, timeout=timeout)


def capture_png(html_path, png_path, w, h):
    uri = pathlib.Path(html_path).resolve().as_uri()
    with _calib_lock:
        off = _calib.get("off")
    ww, wh = (w + off[0], h + off[1]) if off else (w, h)
    for attempt in range(3):
        if os.path.exists(png_path):
            os.remove(png_path)
        _run_chrome([f"--screenshot={png_path}", f"--window-size={ww},{wh}", "--virtual-time-budget=8000", uri])
        size = _png_size(png_path) if os.path.exists(png_path) else None
        if size is None:
            continue
        if size == (w, h):
            with _calib_lock:
                _calib["off"] = (ww - w, wh - h)
            return
        ww += w - size[0]
        wh += h - size[1]
    raise RuntimeError(f"Could not render {png_path} at {w}x{h}")


def capture_pdf(html_path, pdf_path):
    uri = pathlib.Path(html_path).resolve().as_uri()
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    _run_chrome([f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer", "--virtual-time-budget=8000", uri])
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"Could not make {pdf_path}")


def capture_many(jobs, workers=4):
    """jobs: list of (html_path, png_path, w, h). The first one runs alone to calibrate."""
    if not jobs:
        return
    capture_png(*jobs[0])
    rest = jobs[1:]
    if rest:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            for fut in [ex.submit(capture_png, *j) for j in rest]:
                fut.result()
