# Run pipeline

Goal: take everything they gave you and produce a complete, checked, ready-to-post pack with finished images and a calendar. Hands off. Do not stop to ask questions unless the material is missing or too thin.

## 0. Preflight

Run `python3 scripts/doctor.py`. If profile, voice, or design are missing, do the setup first (see `CLAUDE.md`). If no browser is found, tell them to install Google Chrome and stop.

Read: `config.json`, `brand/profile.md`, `brand/voice.md`, `brand/voice-samples.md`, `brand/offer.md`, `brand/brand.json`, and `examples/gold-standard.md`.

## 1. Gather the material

Sources are: every file in `inbox/` (not in `done/` or `_text/`), plus anything they pasted into the chat. If they pasted text, save it to `inbox/<short-slug>.txt` first.

- `.txt` and `.md`: use as is.
- `.docx`, `.srt`, `.vtt`, `.html`, `.pdf`: run `python3 scripts/extract_text.py <file>`. It writes plain text to `inbox/_text/`. If a PDF cannot be converted, read it directly.
- Anything else: ask them to save it as text or paste it in.

Each file is one source. For a course or series, sort by file name so lessons stay in order.

Tell them in one line what you found: "I found 3 lessons totaling about 7,400 words. Working on all of them."

If a source is under 800 words, halve every count and say so. Under 300 words, ask for more material instead of padding.

## 2. Set up the output folder

`outputs/<YYYY-MM-DD>-<short-batch-name>/`

For each source make a subfolder `NN-<source-slug>/`. Inside each:

```
00-extraction.md
00-review.md
carousels/NN-<slug>/carousel.json  (+ caption.md)
quote-graphics/quotes.json
reels/reel-NN.md and reel-NN.spoken.txt
short-videos/video-NN.md and video-NN.spoken.txt
threads.md
notes.md
talking-points.md
instagram-posts.md
facebook-posts.md
substack-articles/NN-<slug>.md
blog/NN-<slug>.md
emails.md
```

At the batch root: `plan.json`, `content-calendar.*`, `00-preview.html`, `00-start-here.md`.

## 3. Extract (per source)

Write `00-extraction.md`:

- **Core message** in one sentence.
- **Teaching points** numbered, in order.
- **Quotable lines**, tightened but faithful.
- **Stories and analogies**, only what is really in the source.
- **Beliefs or excuses the speaker challenges.**
- **What they tell the audience to do.**
- **Audience pain**: who this is for and what they are stuck on.
- **Scripture or references**, if any, with confidence (clear, garbled in transcript, inferred).
- **Risk list**: any claim, number, name, or line you could not trust.
- **Angle map**: one row per piece in the pack, each assigned a different teaching point, quote, story, or belief. No repeats. Include the talking points, Instagram posts, Story sequences, and Facebook posts in the map too.

## 4. Generate (per source)

Use `config.json` for which formats are on and how many of each. Before writing a format, read its spec in `formats/`. If you can run subagents, write the formats in parallel after the extraction is done. Each subagent must first read `brand/voice.md`, `brand/offer.md`, `config.json` rules, the angle map, and its format spec. If you cannot, do them one at a time.

Formats and their specs:

| Format | Spec | Output |
| --- | --- | --- |
| Carousels | `formats/carousels.md` | `carousel.json` + `caption.md` |
| Quote graphics | `formats/quote-graphics.md` | `quotes.json` |
| Talking reel scripts | `formats/reels.md` | `reel-NN.md` + `reel-NN.spoken.txt` |
| Short video spinoffs | `formats/short-videos.md` | `video-NN.md` + `video-NN.spoken.txt` |
| Threads | `formats/threads.md` | `threads.md` |
| Substack notes | `formats/substack-notes.md` | `notes.md` |
| Substack articles | `formats/substack-articles.md` | one file each |
| Blog posts | `formats/blog-posts.md` | one file each |
| Emails | `formats/emails.md` | `emails.md` |
| Talking points | `formats/talking-points.md` | `talking-points.md` |
| Instagram posts and Stories | `formats/instagram-posts.md` | `instagram-posts.md` |
| Facebook posts | `formats/facebook-posts.md` | `facebook-posts.md` |

Spread the ladder of next steps across the pack as described in `brand/offer.md`.

## 5. Check and fix

`python3 scripts/check.py outputs/<batch-folder>`

Fix every ERROR by rewriting the sentence from scratch in their voice. Fix WARN lines unless the wording is genuinely theirs and appears in the source. Re-run until zero errors.

## 6. Make the images

`python3 scripts/render.py outputs/<batch-folder>`

This makes PNGs for every carousel slide, a PDF per carousel, and a PNG for every quote graphic, in their design.

Then look at the work: open the first slide of every carousel and a few quote graphics with the Read tool. Check for text that is cut off or crammed, weak contrast, awkward line breaks, or a slide that is mostly empty. Shorten or reword the text in the JSON and re-render that carousel. Do not skip this.

`python3 scripts/preview.py outputs/<batch-folder>` builds `00-preview.html` so they can see every image at a glance.

## 6a. Animated versions (if `config.json` `video.enabled` is true and `doctor.py` shows ffmpeg)

`python3 scripts/animate.py outputs/<batch-folder>`

This writes, for each carousel, `carousel-animated.mp4` (all slides in one swipe-through video for Reels or Stories) and `animated/slide-NN.mp4` (one clip per slide, to post as video slides). For quote graphics it writes `animated/quote-NN.mp4`. It takes a minute or two per carousel. For a Story or Reel shape add `--size story`. Add the first frames to your check: pull one frame with ffmpeg (`ffmpeg -ss 2 -i file.mp4 -frames:v 1 frame.png`) and look at it. If ffmpeg is not installed, skip this step and mention in the final reply that animated versions are available once ffmpeg is installed.

If they have photos missing and said they use AI images, write `photo-prompts.md` for each carousel (see `formats/carousels.md`) before rendering.

## 6b. Look for gaps

Before you plan the calendar, ask yourself:
- Did any piece make a claim or tell a story that is not in the source?
- Did any two pieces feel like the same piece?
- Is every next step real (a link or keyword that exists)?
Fix what you find.

## 7. Plan and calendar

Follow `engine/04-calendar.md`. It produces `plan.json` and runs `python3 scripts/build_calendar.py`.

## 8. Review files and start-here

Per source, write `00-review.md`:
- **Verify before posting:** names, numbers, scripture references (if on), and anything from the extraction risk list.
- **Placeholders to swap:** links, keywords, anything unfilled.
- **Things I inferred** that the source did not say outright.
- **Left out** and why.

At the batch root, write `00-start-here.md`: what is in the pack (counts), how to open it (`00-preview.html`, `content-calendar.html`), the first three days of posting, and the verify list in plain words.

## 9. Reply

Short. What you made (counts and the total), where to open it, the first post they should publish tomorrow and why, and what to double-check. Move processed files from `inbox/` into `inbox/done/` (keep `_text/` as is).

Do not recap the steps.
