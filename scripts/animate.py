#!/usr/bin/env python3
"""Turn carousels and quote graphics into animated videos (MP4).

Usage:
    python3 scripts/animate.py <file-or-folder> [options]

For each carousel JSON this writes, next to it:
    carousel-animated.mp4      all slides in one video with swipe transitions (great as a Reel or Story)
    animated/slide-NN.mp4      one short clip per slide (post these as video slides in a carousel)
For each quote graphics JSON:
    animated/quote-NN.mp4

Options:
    --seconds 4.0      length of each slide clip
    --fps 24           frames per second
    --size NAME        portrait (1080x1350), square (1080x1080), or story (1080x1920)
    --audio FILE       add a music or voiceover track to the combined video
    --transition NAME  swipe style between slides: slideleft (default), fade, wipeleft, circleopen, slideup
    --no-combined / --no-slides / --no-quotes   skip a kind of output

Needs Chrome (or Edge, Brave, Chromium) and the free tool ffmpeg.
"""
import argparse
import concurrent.futures
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine_lib as E  # noqa: E402
import cdp  # noqa: E402
import render as R  # noqa: E402

LEAD = 0.35
SKIP = 0.25  # seconds trimmed from the start of stand-alone clips


def find_ffmpeg():
    env = os.environ.get("FFMPEG_PATH")
    if env and os.path.exists(env):
        return env
    return shutil.which("ffmpeg")


def need_ffmpeg():
    exe = find_ffmpeg()
    if not exe:
        sys.exit("Animated videos need the free tool ffmpeg, and it is not installed.\n"
                 "  Mac:     brew install ffmpeg\n"
                 "  Windows: winget install Gyan.FFmpeg   (or download from ffmpeg.org)\n"
                 "  Linux:   sudo apt install ffmpeg\n"
                 "Then run this again. Your still images and PDFs do not need it.")
    return exe


def capture_frames(html_path, w, h, fps, total):
    """Open the page, step through time, and return a list of JPEG frames."""
    b = cdp.Browser(w, h)
    try:
        b.open(html_path)
        n = int(round(total * fps))
        frames = []
        for k in range(n):
            b.eval(f"window.seek({k / fps:.4f})")
            frames.append(b.frame())
        return frames
    finally:
        b.close()


def encode(ffmpeg, frames, fps, out):
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "veryfast", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f)
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f"ffmpeg failed making {out}")


def join_clips(ffmpeg, clips, durations, out, transition, xfade, audio=None):
    if len(clips) == 1:
        shutil.copy(clips[0], out)
        return
    cmd = [ffmpeg, "-y", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", str(c)]
    parts, last, acc = [], "[0:v]", durations[0]
    for k in range(1, len(clips)):
        off = acc - xfade
        tag = f"[v{k}]"
        parts.append(f"{last}[{k}:v]xfade=transition={transition}:duration={xfade}:offset={off:.3f}{tag}")
        last = tag
        acc = off + durations[k] if False else acc + durations[k] - xfade
    total = acc
    cmd += ["-filter_complex", ";".join(parts), "-map", last]
    if audio:
        cmd += ["-i", str(audio), "-map", f"{len(clips)}:a", "-shortest"]
        cmd += ["-af", f"afade=t=out:st={max(0, total - 1):.2f}:d=1"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "veryfast", "-movflags", "+faststart"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += [str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg could not join the clips: {r.stderr[-400:]}")


def build_pages(data, path, brand, layout, w, h, seconds, mode):
    html_dir = path.parent / "_html"
    html_dir.mkdir(exist_ok=True)
    logo = E.logo_uri(brand)
    font_base = (E.DESIGN / "fonts").resolve().as_uri() + "/"
    pages = []
    if mode == "carousel":
        slides = data.get("slides") or []
        seed = data.get("title") or path.parent.name
        E.assign_photos(slides, brand)
        for i, s in enumerate(slides):
            s["_seed"] = seed
            body = E.build_slide(s, i, len(slides), brand, layout, "carousel", logo)
            hp = html_dir / f"anim-slide-{i + 1:02d}.html"
            hp.write_text(E.page_html(body, brand, [layout], font_base, anim={"dur": seconds + LEAD, "lead": LEAD}), encoding="utf-8")
            pages.append(hp)
    else:
        quotes = [({"text": q} if isinstance(q, str) else dict(q)) for q in (data.get("quotes") or [])]
        E.assign_photos(quotes, {**brand, "photos": {**(brand.get("photos") or {}), "types": ["quote"]}})
        avail = [n for n in brand["layouts"].get("quote", []) if n in E.list_layouts()] or [layout]
        for i, q in enumerate(quotes):
            q["_seed"] = f"{path.parent.name}-{i}"
            q.setdefault("type", "quote")
            lay = avail[i % len(avail)]
            body = E.build_slide(q, 0, 1, brand, lay, "single", logo)
            hp = html_dir / f"anim-quote-{i + 1:02d}.html"
            hp.write_text(E.page_html(body, brand, [lay], font_base, anim={"dur": seconds + LEAD, "lead": LEAD}), encoding="utf-8")
            pages.append(hp)
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--seconds", type=float)
    ap.add_argument("--fps", type=int)
    ap.add_argument("--size", choices=list(E.SIZES))
    ap.add_argument("--audio")
    ap.add_argument("--layout")
    ap.add_argument("--transition", default="slideleft")
    ap.add_argument("--no-combined", action="store_true")
    ap.add_argument("--no-slides", action="store_true")
    ap.add_argument("--no-quotes", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    ffmpeg = need_ffmpeg()
    if not E.find_chrome():
        sys.exit("No Chrome, Edge, Brave, or Chromium found. Install Google Chrome (free) and run this again.")
    brand = E.load_brand()
    if args.size:
        brand["size"] = args.size
    acfg = brand.get("animation") or {}
    seconds = args.seconds or float(acfg.get("seconds", 4.0))
    fps = args.fps or int(acfg.get("fps", 24))
    w, h = E.SIZES.get(brand.get("size"), E.SIZES["portrait"])
    files = R.collect(args.target)
    if not files:
        sys.exit(f"No carousel or quote JSON files found in {args.target}")
    total_s = seconds + LEAD

    made, car_i = 0, 0
    for f in files:
        data = E.load_json(f, {})
        is_quotes = "quotes" in data
        if is_quotes and args.no_quotes:
            continue
        try:
            layout = R.pick_layout("quote" if is_quotes else "carousel", brand, args.layout, 0 if is_quotes else car_i, data)
            pages = build_pages(data, f, brand, layout, w, h, seconds, "quotes" if is_quotes else "carousel")
            if not pages:
                continue
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
                all_frames = list(ex.map(lambda p: capture_frames(p, w, h, fps, total_s), pages))
            out_dir = f.parent / "animated"
            skip = int(round(SKIP * fps))
            if is_quotes:
                for i, fr in enumerate(all_frames):
                    encode(ffmpeg, fr[skip:], fps, out_dir / f"quote-{i + 1:02d}.mp4")
                    made += 1
            else:
                if not args.no_slides:
                    for i, fr in enumerate(all_frames):
                        encode(ffmpeg, fr[skip:], fps, out_dir / f"slide-{i + 1:02d}.mp4")
                        made += 1
                if not args.no_combined:
                    with tempfile.TemporaryDirectory() as td:
                        clips, durs = [], []
                        for i, fr in enumerate(all_frames):
                            use = fr[skip:] if i == 0 else fr
                            cp = pathlib.Path(td) / f"c{i:02d}.mp4"
                            encode(ffmpeg, use, fps, cp)
                            clips.append(cp)
                            durs.append(len(use) / fps)
                        join_clips(ffmpeg, clips, durs, f.parent / "carousel-animated.mp4", args.transition, 0.5, args.audio)
                    made += 1
                car_i += 1
        except Exception as exc:
            print(f"FAILED {f}: {exc}")
            continue
        print(f"ok  {f.parent.name}/{f.name}  layout={layout}")
    print(f"Done. {made} video file(s) written.")


if __name__ == "__main__":
    main()
