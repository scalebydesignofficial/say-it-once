"""Decoration pack: hand-drawn style shapes, doodles, and stickers as inline SVG.

Everything is drawn in code, so it is original, recolors to the brand, and needs no downloads.
Colors come from CSS variables set per slide tone (--c1 line, --c2 fill, --c3 secondary).
"""
import math
import random

# ------------------------------------------------------------- shape builders

def _ln(d, extra=""):
    return f'<path class="s" pathLength="1" d="{d}" {extra}/>'


def _fl(d, var="c2", extra=""):
    return f'<path class="f {var}" d="{d}" {extra}/>'


def _burst(n=14, r1=48, r2=34):
    pts = []
    for k in range(n * 2):
        r = r1 if k % 2 == 0 else r2
        a = math.pi * k / n - math.pi / 2
        pts.append(f"{50 + r * math.cos(a):.1f},{50 + r * math.sin(a):.1f}")
    return f'<polygon class="f c2" points="{" ".join(pts)}" stroke-linejoin="round"/>'


def _star5():
    pts = []
    for k in range(10):
        r = 46 if k % 2 == 0 else 20
        a = math.pi * k / 5 - math.pi / 2
        pts.append(f"{50 + r * math.cos(a):.1f},{52 + r * math.sin(a):.1f}")
    return f'<polygon class="f c1" points="{" ".join(pts)}" stroke-linejoin="round" stroke="currentColor" stroke-width="4"/>'


def _spiral():
    pts = []
    for k in range(0, 260):
        a = k * 0.11
        r = 2 + a * 2.6
        pts.append(f"{50 + r * math.cos(a):.1f} {50 + r * math.sin(a):.1f}")
    return _ln("M" + " L".join(pts))


def _dots(n=4, gap=22, r=3.6):
    out = []
    o = (100 - gap * (n - 1)) / 2
    for i in range(n):
        for j in range(n):
            out.append(f'<circle class="f c1" cx="{o + i * gap:.1f}" cy="{o + j * gap:.1f}" r="{r}"/>')
    return "".join(out)


def _plus_grid(n=3, gap=34, s=7):
    out = []
    o = (100 - gap * (n - 1)) / 2
    for i in range(n):
        for j in range(n):
            x, y = o + i * gap, o + j * gap
            out.append(_ln(f"M{x - s} {y} H{x + s} M{x} {y - s} V{y + s}"))
    return "".join(out)


def _asterisk():
    return "".join(_ln(f"M50 50 L{50 + 42 * math.cos(a):.1f} {50 + 42 * math.sin(a):.1f} M50 50 L{50 - 42 * math.cos(a):.1f} {50 - 42 * math.sin(a):.1f}")
                   for a in (math.pi / 2, math.pi / 2 + math.pi / 3, math.pi / 2 + 2 * math.pi / 3))


def _sun():
    rays = "".join(_ln(f"M{50 + 30 * math.cos(a):.1f} {50 + 30 * math.sin(a):.1f} L{50 + 46 * math.cos(a):.1f} {50 + 46 * math.sin(a):.1f}")
                   for a in [k * math.pi / 4 for k in range(8)])
    return '<circle class="s" cx="50" cy="50" r="18" pathLength="1"/>' + rays


def _flower():
    petals = "".join(f'<ellipse class="f c2" cx="50" cy="26" rx="13" ry="22" transform="rotate({k * 72} 50 50)" opacity=".9"/>' for k in range(5))
    return petals + '<circle class="f c1" cx="50" cy="50" r="10"/>'


def _sprig():
    stem = _ln("M50 96 C 49 70 52 40 58 6")
    leaves = ""
    for (y, side, s) in ((78, -1, 1.0), (62, 1, 0.95), (46, -1, 0.85), (32, 1, 0.75), (19, -1, 0.6)):
        x = 50 + (3 if side > 0 else -1)
        leaves += (f'<path class="f c2" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" '
                   f'd="M{x} {y} C {x + side * 26 * s} {y - 2} {x + side * 34 * s} {y - 18 * s} {x + side * 30 * s} {y - 26 * s} '
                   f'C {x + side * 10 * s} {y - 22 * s} {x + side * 2} {y - 10 * s} {x} {y} Z"/>')
    return stem + leaves


def _confetti():
    bits = [(14, 20, 12, 0, "c1"), (60, 10, 10, 30, "c2"), (84, 36, 11, -20, "c3"), (30, 56, 10, 50, "c3"),
            (70, 70, 13, 10, "c1"), (18, 84, 9, 70, "c2"), (50, 40, 8, -40, "c1")]
    out = []
    for x, y, s, rot, c in bits:
        out.append(f'<rect class="f {c}" x="{x}" y="{y}" width="{s}" height="{s * 0.45:.1f}" rx="2" transform="rotate({rot} {x} {y})"/>')
    out.append('<circle class="f c2" cx="42" cy="86" r="4"/><circle class="f c3" cx="88" cy="12" r="3.5"/><circle class="f c1" cx="8" cy="46" r="3.5"/>')
    return "".join(out)


def _tape():
    z = "M0 14 L4 8 L0 2 L4 -4 L96 -4 L100 2 L96 8 L100 14 L96 20 L4 20 Z"
    return f'<g transform="translate(0 40)"><path class="f c2" d="{z}" opacity=".75"/></g>'


def _sticky():
    return ('<path class="f c2" d="M8 8 H92 V70 L70 92 H8 Z"/>'
            '<path class="f c1" d="M92 70 L70 70 L70 92 Z" opacity=".35"/>'
            '<path class="s" d="M22 30 H76 M22 46 H62" opacity=".5"/>')


def _heart():
    return _ln("M50 88 C 10 58 6 30 28 20 C 42 14 50 26 50 32 C 50 26 58 14 72 20 C 94 30 90 58 50 88 Z")


def _heart_fill():
    return _fl("M50 88 C 10 58 6 30 28 20 C 42 14 50 26 50 32 C 50 26 58 14 72 20 C 94 30 90 58 50 88 Z", "c1")


# --------------------------------------------------------------------- library
# kind: "line" (stroke), "fill" (solid); size: typical width in u (min, max); aspect: h/w

LIB = {
    "scribble_circle": dict(kind="line", size=(24, 34), aspect=0.8, svg=lambda: _ln("M52 8 C 20 6, 3 34, 9 60 C 15 90, 54 98, 80 84 C 98 72, 98 30, 70 14 C 56 6, 36 8, 22 22"), anim="draw"),
    "squiggle": dict(kind="line", size=(18, 28), aspect=0.3, svg=lambda: _ln("M4 50 Q 16 14 28 50 T 52 50 T 76 50 T 98 50"), anim="draw"),
    "arrow_curve": dict(kind="line", size=(16, 24), aspect=0.8, svg=lambda: _ln("M10 84 C 16 34, 56 18, 86 36 M68 20 L88 36 L70 54"), anim="draw"),
    "arrow_right": dict(kind="line", size=(14, 22), aspect=0.5, svg=lambda: _ln("M6 50 H88 M64 26 L90 50 L64 74"), anim="draw"),
    "spiral": dict(kind="line", size=(12, 18), aspect=1, svg=_spiral, anim="draw"),
    "zigzag": dict(kind="line", size=(16, 24), aspect=0.4, svg=lambda: _ln("M4 64 L20 30 L36 64 L52 30 L68 64 L84 30 L98 60"), anim="draw"),
    "wave3": dict(kind="line", size=(16, 24), aspect=0.6, svg=lambda: "".join(_ln(f"M4 {y} Q 16 {y - 14} 28 {y} T 52 {y} T 76 {y} T 98 {y}") for y in (24, 50, 76)), anim="draw"),
    "ring": dict(kind="line", size=(12, 24), aspect=1, svg=lambda: '<circle class="s" cx="50" cy="50" r="40" pathLength="1"/>', anim="draw"),
    "arch": dict(kind="line", size=(14, 22), aspect=1.3, svg=lambda: _ln("M18 96 V50 A32 32 0 0 1 82 50 V96 M32 96 V52 A18 18 0 0 1 68 52 V96"), anim="draw"),
    "check": dict(kind="line", size=(10, 16), aspect=1, svg=lambda: _ln("M12 54 L38 80 L90 18", 'stroke-width="9"'), anim="draw"),
    "corner": dict(kind="line", size=(10, 16), aspect=1, svg=lambda: _ln("M10 46 V10 H46", 'stroke-width="5"'), anim="draw"),
    "plus_grid": dict(kind="line", size=(12, 18), aspect=1, svg=_plus_grid, anim="pop"),
    "asterisk": dict(kind="line", size=(9, 14), aspect=1, svg=_asterisk, anim="pop"),
    "sun": dict(kind="line", size=(14, 20), aspect=1, svg=_sun, anim="pop"),
    "heart": dict(kind="line", size=(9, 14), aspect=1, svg=_heart, anim="draw"),
    "heart_fill": dict(kind="fill", size=(8, 13), aspect=1, svg=_heart_fill, anim="pop"),
    "burst": dict(kind="fill", size=(16, 26), aspect=1, svg=_burst, anim="pop"),
    "star5": dict(kind="fill", size=(8, 13), aspect=1, svg=_star5, anim="pop"),
    "dots_grid": dict(kind="fill", size=(12, 18), aspect=1, svg=_dots, anim="pop"),
    "flower": dict(kind="fill", size=(12, 20), aspect=1, svg=_flower, anim="pop"),
    "sprig": dict(kind="fill", size=(11, 17), aspect=1.4, svg=_sprig, anim="pop"),
    "confetti": dict(kind="fill", size=(14, 22), aspect=1, svg=_confetti, anim="pop"),
    "tape": dict(kind="fill", size=(18, 26), aspect=0.5, svg=_tape, anim="pop"),
    "sticky": dict(kind="fill", size=(14, 20), aspect=1, svg=_sticky, anim="pop"),
    "half_circle": dict(kind="fill", size=(22, 36), aspect=0.5, svg=lambda: _fl("M4 90 A46 46 0 0 1 96 90 Z"), anim="pop"),
    "blob1": dict(kind="fill", size=(34, 52), aspect=1, svg=lambda: _fl("M50 6 C76 2 96 22 92 50 C88 78 66 96 42 92 C16 88 4 64 10 40 C16 18 32 8 50 6 Z"), anim="pop", big=True),
    "blob2": dict(kind="fill", size=(34, 52), aspect=1, svg=lambda: _fl("M30 10 C58 -2 90 14 94 44 C98 74 70 98 40 92 C12 86 -4 60 6 36 C10 24 18 14 30 10 Z"), anim="pop", big=True),
    "circle_fill": dict(kind="fill", size=(24, 44), aspect=1, svg=lambda: '<circle class="f c2" cx="50" cy="50" r="48"/>', anim="pop", big=True),
}

THEMES = {
    "playful": ["scribble_circle", "squiggle", "arrow_curve", "burst", "asterisk", "blob1", "dots_grid", "zigzag", "star5", "confetti", "spiral", "tape", "heart", "check", "circle_fill"],
    "botanical": ["sprig", "flower", "arch", "sun", "half_circle", "ring", "blob2", "heart", "wave3", "dots_grid", "tape", "squiggle", "circle_fill"],
    "minimal": ["ring", "plus_grid", "squiggle", "arrow_right", "half_circle", "dots_grid", "corner", "circle_fill", "asterisk"],
    "bold": ["burst", "zigzag", "blob1", "asterisk", "star5", "arrow_right", "plus_grid", "half_circle", "ring", "tape", "sticky", "heart_fill", "circle_fill"],
}

# Slots are CSS positions in slide units (u = 1% of slide width). Biggest items go to the corners.
BIG_SLOTS = {
    "corner_tr": "right:-9u;top:-9u", "corner_bl": "left:-9u;bottom:-9u",
    "corner_br": "right:-9u;bottom:-9u", "corner_tl": "left:-9u;top:-9u",
}
SMALL_SLOTS = {
    "edge_r": "right:-3.2u;top:27%", "edge_l": "left:-3.2u;top:55%", "edge_r2": "right:-3.2u;top:63%",
    "edge_l2": "left:-3.2u;top:20%", "edge_r3": "right:-3.2u;top:44%", "edge_l3": "left:-3.2u;top:38%",
}

COUNTS = {"none": (0, 0), "light": (1, 2), "rich": (3, 5)}


def _pos(spec):
    out = []
    for part in spec.split(";"):
        k, v = part.split(":")
        if v.endswith("u"):
            n = v[:-1]
            v = f"calc(var(--u) * {n})"
        out.append(f"{k}:{v}")
    return ";".join(out)


def render_item(name, slot_css, size_u, rot, c, delay_idx):
    spec = LIB[name]
    w = size_u
    h = size_u * spec["aspect"]
    cvar = {"c1": "var(--c1)", "c2": "var(--c2)", "c3": "var(--c3)"}[c]
    return (f'<div class="dc dc-{name}" data-a="{spec["anim"]}" data-i="{delay_idx}" style="{_pos(slot_css)};'
            f'width:calc(var(--u) * {w:.1f});height:calc(var(--u) * {h:.1f});color:{cvar};rotate:{rot}deg">'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" aria-hidden="true">{spec["svg"]()}</svg></div>')


def make_decor(level, theme, seed, slide_type, index):
    """Return the HTML for the decoration layer of one slide."""
    lo, hi = COUNTS.get(level, (0, 0))
    if hi == 0:
        return ""
    rng = random.Random(f"{seed}-{index}-{slide_type}")
    names = [n for n in THEMES.get(theme, THEMES["playful"]) if n in LIB]
    n_items = rng.randint(lo, hi)
    if slide_type in ("cover", "close") and level == "rich":
        n_items = min(hi + 1, 6)
    if slide_type == "list" and level == "rich":
        n_items = max(lo, n_items - 1)
    big = [n for n in names if LIB[n].get("big")]
    small = [n for n in names if not LIB[n].get("big")]
    items, used_slots, used_names = [], set(), set()

    # one big soft shape in a corner, when the theme has them
    if big and (level == "rich" or rng.random() < 0.6):
        slot = rng.choice(list(BIG_SLOTS))
        name = rng.choice(big)
        size = rng.uniform(*LIB[name]["size"])
        items.append(render_item(name, BIG_SLOTS[slot], size, rng.randint(-25, 25), "c2", 0))
        used_slots.add(slot)
        used_names.add(name)
        n_items -= 1

    slots = [s for s in SMALL_SLOTS if s not in used_slots]
    rng.shuffle(slots)
    for k in range(max(0, n_items)):
        if not slots or not small:
            break
        slot = slots.pop()
        pool = [n for n in small if n not in used_names] or small
        name = rng.choice(pool)
        used_names.add(name)
        spec = LIB[name]
        size = rng.uniform(*spec["size"])
        size = min(size, 10.5 if spec['kind'] == 'line' else 12.5)
        rot = rng.randint(-18, 18)
        col = "c1" if spec["kind"] == "line" else rng.choice(["c1", "c2", "c2"])
        if spec["kind"] == "line" and rng.random() < 0.3:
            col = "c3"
        items.append(render_item(name, SMALL_SLOTS[slot], size, rot, col, k + 1))
    return "".join(items)


DECOR_CSS = """
.slide .decor{position:absolute;inset:0;z-index:1;pointer-events:none;overflow:hidden}
.slide .dc{position:absolute;transform-origin:center}
.slide .dc svg{width:100%;height:100%;overflow:visible;display:block}
.slide .dc .s{fill:none;stroke:currentColor;stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}
.slide .dc .f{fill:currentColor;stroke:none}
.slide .dc .c1{fill:var(--c1)}.slide .dc .c2{fill:var(--c2)}.slide .dc .c3{fill:var(--c3)}
.slide .dc-star5 polygon{stroke:var(--c1)}
.slide .dc-sprig .f{stroke:var(--c1)}
.slide .dc-sticky .s{stroke:var(--c3)}
.slide.tone-light{--c1:var(--accent);--c2:var(--accent2);--c3:var(--ink)}
.slide.tone-accent{--c1:var(--on-accent);--c2:color-mix(in srgb,var(--on-accent) 22%,var(--accent));--c3:var(--accent2)}
.slide.tone-dark{--c1:var(--accent2);--c2:color-mix(in srgb,var(--accent) 70%,transparent);--c3:#ffffff}
"""
