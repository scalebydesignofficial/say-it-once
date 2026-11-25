#!/usr/bin/env python3
"""Make real pictures from written image prompts, using OpenAI or Google Gemini.

Usage:
    python3 scripts/make_images.py status                      which service is set up
    python3 scripts/make_images.py plan <folder>               list what would be made (spends nothing)
    python3 scripts/make_images.py make <folder> [--only N]    make the pictures (spends money, a few cents each)
                                                [--redo] [--provider openai|gemini]

<folder> is a carousel folder, a whole pack, or `brand` for mood pictures. Every `photo-prompts.json` found is used:

    {"images": [
      {"slide": 1, "prompt": "Soft morning light on a kitchen table, an open Bible and a coffee cup"},
      {"name": "calm-sky", "prompt": "Gentle pastel sky at sunrise, lots of empty space"}
    ]}

    "slide": N   saves photos/slide-NN.png next to the carousel; the pack builder puts it on that slide
    "name": X    saves photos/X.png (in a carousel folder) or brand/photos/X.png (for brand/photo-prompts.json)

Your key: set OPENAI_API_KEY or GEMINI_API_KEY, or put it in brand/image-keys.json:
    {"openai": "sk-...", "gemini": "AI..."}
That file stays on your computer. It is never zipped, shared or sent anywhere except to the image service you chose.
Settings live in config.json under "images": provider (auto, openai, gemini), quality, style, model_openai, model_gemini.
"""
import argparse
import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

ROOT = E.ROOT
KEYS_FILE = E.BRAND_DIR / "image-keys.json"
DEFAULTS = {"provider": "auto", "quality": "medium", "style": "", "model_openai": "gpt-image-1",
            "model_gemini": "gemini-2.5-flash-image"}
# Added to every prompt. Pictures never carry words, logos, or real people.
GUARD = ("No text, letters, numbers, logos or watermarks anywhere in the picture. No recognizable real people. "
         "Leave calm, uncluttered space where words can sit on top. Vertical 4:5 composition.")


def settings():
    cfg = E.load_json(ROOT / "config.json", {}).get("images", {}) or {}
    return {**DEFAULTS, **cfg}


def get_key(provider):
    env = {"openai": ["OPENAI_API_KEY"], "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"]}[provider]
    for name in env:
        if os.environ.get(name):
            return os.environ[name].strip()
    return (E.load_json(KEYS_FILE, {}).get(provider) or "").strip()


def choose_provider(want="auto"):
    want = want or settings()["provider"]
    have = [p for p in ("openai", "gemini") if get_key(p)]
    if want in ("openai", "gemini"):
        if want not in have:
            sys.exit(f"No {want} key found. Put it in brand/image-keys.json or set the "
                     f"{'OPENAI_API_KEY' if want == 'openai' else 'GEMINI_API_KEY'} setting. (Nothing was spent.)")
        return want
    if not have:
        sys.exit("No image service is set up yet. You need a key from OpenAI or Google Gemini. (Nothing was spent.)")
    return have[0]


def post(url, headers, body, timeout=240):
    data = json.dumps(body).encode()
    last = None
    for attempt in range(3):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = json.loads(e.read()).get("error", {}).get("message", "")
            except Exception:  # noqa: BLE001
                pass
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(4 * (attempt + 1))
                last = f"{e.code} {detail}"
                continue
            if e.code in (401, 403):
                sys.exit("The image service did not accept the key. Check that it is copied in full and that billing is on for it.")
            sys.exit(f"The image service said no ({e.code}): {detail[:300] or 'no details'}")
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(3)
    sys.exit(f"Could not reach the image service ({last}). Check your internet and try again.")


def sniff_ext(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if b[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return ".webp"
    return ".png"


def make_openai(prompt, cfg):
    base = os.environ.get("SIO_OPENAI_BASE", "https://api.openai.com/v1")
    r = post(f"{base}/images/generations", {"Authorization": "Bearer " + get_key("openai")},
             {"model": cfg["model_openai"], "prompt": prompt, "size": "1024x1536", "quality": cfg["quality"], "n": 1})
    return base64.b64decode(r["data"][0]["b64_json"])


def make_gemini(prompt, cfg):
    base = os.environ.get("SIO_GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta")
    url = f"{base}/models/{cfg['model_gemini']}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": "4:5"}}}
    r = post(url, {"x-goog-api-key": get_key("gemini")}, body)
    for cand in r.get("candidates", []):
        for part in (cand.get("content") or {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    sys.exit("The image service answered but sent no picture (it may have refused the prompt). Try rewording it.")


def jobs_for(target):
    """Every picture that the prompt files under target ask for: (out_path, prompt)."""
    target = pathlib.Path(target) if str(target) != "brand" else E.BRAND_DIR
    files = [target / "photo-prompts.json"] if target.is_file() is False and (target / "photo-prompts.json").exists() else []
    files += [p for p in sorted(target.rglob("photo-prompts.json")) if p not in files and not any(x.startswith("_") for x in p.relative_to(target).parts)]
    jobs = []
    for f in files:
        data = E.load_json(f, {})
        in_brand = f.parent == E.BRAND_DIR
        photos = (E.BRAND_DIR / "photos") if in_brand else f.parent / "photos"
        for it in data.get("images", []):
            prompt = (it.get("prompt") or "").strip()
            if not prompt:
                continue
            if it.get("slide"):
                stem = f"slide-{int(it['slide']):02d}"
            elif it.get("name"):
                stem = "".join(ch for ch in it["name"] if ch.isalnum() or ch in "-_") or "image"
            else:
                continue
            existing = next((photos / f"{stem}{e}" for e in (".png", ".jpg", ".jpeg", ".webp") if (photos / f"{stem}{e}").exists()), None)
            jobs.append({"folder": f.parent.name, "stem": stem, "dir": photos, "prompt": prompt, "existing": existing})
    return jobs


def cmd_status():
    cfg = settings()
    for p in ("openai", "gemini"):
        print(f"  {p:7} {'key found' if get_key(p) else 'no key'}")
    try:
        print(f"Will use: {choose_provider(cfg['provider'])}")
    except SystemExit as e:
        print(e)


def cmd_plan(target, redo):
    jobs = jobs_for(target)
    todo = [j for j in jobs if redo or not j["existing"]]
    for j in jobs:
        print(f"  {j['folder']}/{j['stem']}: " + ("already made" if j["existing"] and not redo else "to make") + f"  | {j['prompt'][:80]}")
    print(f"{len(todo)} picture(s) to make, {len(jobs) - len(todo)} already made.")
    return todo


def cmd_make(target, only, redo, provider):
    cfg = settings()
    jobs = jobs_for(target)
    todo = [j for j in jobs if redo or not j["existing"]]
    if only:
        todo = todo[:only]
    if not todo:
        print("Nothing to make. Every picture in the prompt files already exists.")
        return
    prov = choose_provider(provider or cfg["provider"])
    maker = make_openai if prov == "openai" else make_gemini
    made = 0
    for j in todo:
        full = j["prompt"] + (" Style: " + cfg["style"] if cfg.get("style") else "") + " " + GUARD
        data = maker(full, cfg)
        j["dir"].mkdir(parents=True, exist_ok=True)
        if j["existing"]:
            j["existing"].unlink()
        out = j["dir"] / f"{j['stem']}{sniff_ext(data)}"
        out.write_bytes(data)
        made += 1
        print(f"ok  {j['folder']}/{out.name}  ({prov})")
    print(f"Made {made} picture(s). Rebuild the carousels so they show up: python3 scripts/carousel_studio.py pack <batch-folder>")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    p = sub.add_parser("plan")
    p.add_argument("target")
    p.add_argument("--redo", action="store_true")
    m = sub.add_parser("make")
    m.add_argument("target")
    m.add_argument("--only", type=int)
    m.add_argument("--redo", action="store_true")
    m.add_argument("--provider", choices=["openai", "gemini"])
    a = ap.parse_args()
    if a.cmd == "status":
        cmd_status()
    elif a.cmd == "plan":
        cmd_plan(a.target, a.redo)
    else:
        cmd_make(a.target, a.only, a.redo, a.provider)


if __name__ == "__main__":
    main()
