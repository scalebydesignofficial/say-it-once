#!/usr/bin/env python3
"""Save brand settings into brand/brand.json.

Usage:
    python3 scripts/save_brand.py '<json text>'
    python3 scripts/save_brand.py path/to/settings.json
    echo '<json text>' | python3 scripts/save_brand.py -

Merges what you give it into the existing file, checks the colors, fonts, and
layouts, and prints what it saved. This is what runs when someone pastes
settings from the Design Studio.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def read_input(arg):
    if arg == "-":
        return sys.stdin.read()
    if not arg.lstrip().startswith(("{", "[")):
        try:
            p = pathlib.Path(arg)
            if p.is_file():
                return p.read_text(encoding="utf-8")
        except OSError:
            pass
    return arg


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    try:
        new = json.loads(read_input(sys.argv[1]))
    except ValueError as exc:
        print(f"That is not valid JSON: {exc}")
        return 2
    if not isinstance(new, dict):
        print("Expected a JSON object.")
        return 2

    current = E.load_json(E.BRAND_DIR / "brand.json", {})
    merged = E._merge(E._merge(E.DEFAULT_BRAND, current), new)
    problems = []

    for k, v in (merged.get("colors") or {}).items():
        fixed = E.norm_hex(v, None)
        if fixed is None:
            problems.append(f"Color '{k}' is not a hex code like #AABBCC: {v}")
        else:
            merged["colors"][k] = fixed

    layouts = E.list_layouts()
    for kind in ("carousel", "quote"):
        chosen = [n for n in (merged.get("layouts") or {}).get(kind, []) if n in layouts]
        dropped = set((merged.get("layouts") or {}).get(kind, [])) - set(chosen)
        if dropped:
            problems.append(f"Unknown {kind} layout(s) removed: {', '.join(sorted(dropped))}")
        if not chosen:
            chosen = ["editorial"] if kind == "carousel" else ["bold-block"]
            problems.append(f"No {kind} layout picked, using {chosen[0]}")
        merged.setdefault("layouts", {})[kind] = chosen

    known = {f["family"].lower() for f in E.font_catalog().get("families", [])}
    custom = E.custom_fonts_css().lower()
    for role, fam in (merged.get("fonts") or {}).items():
        if fam and fam.lower() not in known and f"font-family:'{fam.lower()}'" not in custom:
            problems.append(f"Font '{fam}' ({role}) is not bundled and not in brand/fonts/. It will fall back to a plain font.")

    choices = {"decor": ("none", "light", "rich"), "decor_theme": ("playful", "botanical", "minimal", "bold"),
               "bg_style": ("flat", "mesh", "grain", "paper", "dots", "stripes", "waves", "grid"),
               "highlight": ("layout", "underline", "circle", "marker", "box")}
    for key, allowed in choices.items():
        if merged.get(key) not in allowed:
            problems.append(f"{key} '{merged.get(key)}' unknown, using '{E.DEFAULT_BRAND[key]}'. Choices: {', '.join(allowed)}")
            merged[key] = E.DEFAULT_BRAND[key]
    if merged.get("size") not in E.SIZES:
        problems.append(f"Size '{merged.get('size')}' unknown, using portrait")
        merged["size"] = "portrait"

    E.BRAND_DIR.mkdir(exist_ok=True)
    (E.BRAND_DIR / "brand.json").write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print("Saved brand/brand.json")
    print(f"  name: {merged.get('name')}   handle: {merged.get('handle')}")
    print(f"  colors: " + ", ".join(f"{k} {v}" for k, v in merged['colors'].items()))
    print(f"  fonts: " + ", ".join(f"{k} {v}" for k, v in merged['fonts'].items()))
    print(f"  size: {merged['size']}   carousel layouts: {', '.join(merged['layouts']['carousel'])}   quote layouts: {', '.join(merged['layouts']['quote'])}")
    print(f"  decorations: {merged['decor']} ({merged['decor_theme']})   texture: {merged['bg_style']}   highlight: {merged['highlight']}")
    for p in problems:
        print("  NOTE:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
