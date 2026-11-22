#!/usr/bin/env python3
"""Check that the engine is ready to run. Prints what is set up and what is missing.

Usage: python3 scripts/doctor.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402


def line(ok, label, fix=""):
    print(f"  [{'OK' if ok else 'NEEDS ATTENTION'}] {label}" + (f"  ->  {fix}" if (fix and not ok) else ""))


def filled(p, min_chars=80):
    return p.exists() and len(p.read_text(encoding="utf-8").strip()) >= min_chars and "(not set up yet)" not in p.read_text(encoding="utf-8")


def main():
    root = E.ROOT
    print("Say It Once check\n")
    print("Tools")
    line(sys.version_info >= (3, 8), f"Python {sys.version.split()[0]}", "install Python 3.8 or newer")
    chrome = E.find_chrome()
    line(bool(chrome), f"Browser for making images: {chrome or 'none found'}", "install Google Chrome (free)")
    import shutil, os
    ff = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")
    print(f"  [{'OK' if ff else 'OPTIONAL'}] Animated videos (ffmpeg): {ff or 'not installed. Images work fine without it. For animated carousels install the free ffmpeg.'}")
    pics = E.list_photos()
    print(f"  [OK] Photos in brand/photos: {len(pics)}" if pics else "  [OPTIONAL] No photos in brand/photos yet. Add some for photo backgrounds.")
    line((E.DESIGN / "fonts" / "fonts.css").exists(), "Bundled fonts", "the design/fonts folder is missing, re-unzip the engine")
    print("\nYour setup")
    line(filled(root / "brand" / "profile.md"), "Business and audience profile (brand/profile.md)", "say 'set me up' and answer a few questions")
    line(filled(root / "brand" / "voice.md"), "Voice guide (brand/voice.md)", "say 'set me up'")
    line(E.brand_is_set(), "Design chosen (brand/brand.json)", "say 'open the design studio'")
    sources = [p for p in (root / "inbox").glob("*") if p.is_file() and not p.name.startswith(("README", "."))]
    print(f"\nInbox: {len(sources)} file(s) waiting")
    runs = [p for p in (root / "outputs").glob("*") if p.is_dir()]
    print(f"Past runs: {len(runs)}")
    ready = bool(chrome) and filled(root / "brand" / "profile.md") and E.brand_is_set()
    print("\n" + ("Ready. Drop a transcript in inbox/ and say 'run it'." if ready else "Not ready yet. Fix the items above first."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
