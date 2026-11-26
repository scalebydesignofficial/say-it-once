# Run pipeline

Goal: take everything they gave you and produce a complete, checked, ready-to-post pack with finished images and a calendar. Hands off. Do not stop to ask questions unless the material is missing or too thin.

## 0. Preflight

Run `python3 scripts/doctor.py`. If profile, voice, or design are missing, do the setup first (see `CLAUDE.md`). If no browser is found, tell them to install Google Chrome and stop.

Read: `config.json`, `brand/profile.md`, `brand/voice.md`, `brand/voice-samples.md`, `brand/offer.md`, `brand/brand.json`, `examples/gold-standard.md`, `brand/copy-framework.md` (only if it has content), and `engine/copy-principles.md`. The last one decides what every piece is trying to do: make her reader feel seen, so she follows and engages.

## 0b. What should it make this time?

Unless they already said ("just carousels", "only the written posts", "a small pack"), ask once with AskUserQuestion, before you start work:

- Question 1, "What do you want from this?": **Everything my setup allows** (recommended), **Just the visuals** (carousels and quote graphics), **Just the written posts** (threads, notes, Instagram, Facebook, LinkedIn, Pinterest), **Let me pick** (then ask which of: visuals, video scripts, written posts, long-form (articles, blog, emails, YouTube)).
- Question 2, "How big?": **Standard** (recommended), **Small** (about half), **Big** (about one and a half times).

Skip the questions if they pasted nothing yet or said "just go": use everything and their saved size. Do not ask again for later sources in the same run.

Then run `python3 scripts/pack_plan.py --only <groups> --size <size> --words <length of the source>` (leave out `--only` for everything, and leave out `--size` to use their saved one). Its answer is the exact list of formats and how many of each to make. It already applies the on and off switches in `config.json`, the size, and the short-source rule. If its note says a format they asked for is switched off, offer to switch it on (`config.json` `formats`) and carry on without it unless they say yes.

If they say "make this my usual size from now on", save it: set `pack_size` in `config.json` to small, standard, or big.

## 1. Gather the material

Sources are: every file in `inbox/` (not in `done/` or `_text/`), plus anything they pasted into the chat. If they pasted text, save it to `inbox/<short-slug>.txt` first.

- `.txt` and `.md`: use as is.
- `.docx`, `.srt`, `.vtt`, `.html`, `.pdf`: run `python3 scripts/extract_text.py <file>`. It writes plain text to `inbox/_text/`. If a PDF cannot be converted, read it directly.
- Anything else: ask them to save it as text or paste it in.

Each file is one source. For a course or series, sort by file name so lessons stay in order.

Tell them in one line what you found: "I found 3 lessons totaling about 7,400 words. Working on all of them."

Short sources: `pack_plan.py` halves the counts under 800 words and says to ask for more material under 300. Tell them when that happens.

## 2. Set up the output folder

`outputs/<YYYY-MM-DD>-<short-batch-name>/`

For each source make a subfolder `NN-<source-slug>/`. Inside each:

```
00-extraction.md
00-review.md
carousels/NN-<slug>/carousel.json  (+ caption.md, photo-prompts.json)
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
linkedin-posts.md
pinterest-pins.md
youtube.md
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
- **Mirror lines**: 5 to 10 specific moments, thoughts, or feelings her reader has, in plain words her reader would use, taken from the source, `brand/profile.md`, and its "In her people's words" notes. Never invented quotes from real people.
- **Scripture or references**, if any, with confidence (clear, garbled in transcript, inferred).
- **Risk list**: any claim, number, name, or line you could not trust.
- **Angle map**: one row per piece in the pack, each assigned a different teaching point, quote, story, or belief. No repeats. Include the talking points, Instagram posts, Story sequences, and Facebook posts in the map too. Give each row a mirror line from the list above and a hook shape from `engine/copy-principles.md`, and vary both across the pack.

## 4. Generate (per source)

Use the answer from `scripts/pack_plan.py` (step 0b) for which formats to make and how many of each. Before writing a format, read its spec in `formats/`. If you can run subagents, write the formats in parallel after the extraction is done. Each subagent must first read `brand/voice.md`, `brand/offer.md`, `config.json` rules, `engine/copy-principles.md`, the angle map, and its format spec. If you cannot, do them one at a time.

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
| LinkedIn posts | `formats/linkedin-posts.md` | `linkedin-posts.md` |
| Pinterest pins | `formats/pinterest-pins.md` | `pinterest-pins.md` |
| YouTube titles and descriptions | `formats/youtube-long-form.md` | `youtube.md` |

Spread the ladder of next steps across the pack as described in `brand/offer.md`.

## 5. Check and fix

`python3 scripts/check.py outputs/<batch-folder>`

Fix every ERROR by rewriting the sentence from scratch in their voice. Fix WARN lines unless the wording is genuinely theirs and appears in the source. Re-run until zero errors.

## 6. Make the images

First, pictures (only if the person wants them; see `engine/08-images.md`). Then:

`python3 scripts/carousel_studio.py pack outputs/<batch-folder>`

This builds every carousel and quote graphic with the Carousel Studio layouts, in their design: `slide-NN.png` and a `carousel.pdf` per carousel (the PDF is also the file for a LinkedIn document post), `quote-NN.png` for the quote graphics, and a `contact-sheet.jpg` per carousel. Each carousel gets its own look in turn (editorial, bold, soft) so the batch has variety. Photos go on covers, closers and quotes when the person has photos or pictures were made for the slide. A quote with a name or a Scripture reference always gets a layout that shows it.

Then look at the work: open the contact sheet of every carousel and one quote graphic contact sheet with the Read tool. Check for text that is cut off or crammed, weak contrast, awkward line breaks, or a slide that is mostly empty. Shorten or reword the text in `carousel.json` and run the same command again (it rebuilds anything whose words changed). To change one slide's layout, set `"layout"` on that slide in `plan.json` (see `engine/06-carousel-studio.md`). Do not skip this.

`python3 scripts/preview.py outputs/<batch-folder>` builds `00-preview.html` so they can see every image at a glance.

If they edited a carousel in the browser editor, the pack keeps their edits (it only rebuilds the images) and tells you "kept your edits". Make later word changes in that carousel's `plan.json`, not `carousel.json`.

## 6a. Animated versions (if `config.json` `video.enabled` is true and `doctor.py` shows ffmpeg)

`python3 scripts/animate.py outputs/<batch-folder>`

This writes, for each carousel, `carousel-animated.mp4` (all slides in one swipe-through video for Reels or Stories) and `animated/slide-NN.mp4` (one clip per slide, to post as video slides). For quote graphics it writes `animated/quote-NN.mp4`. Text rises in line by line, photos drift slowly, and slides swipe into each other. It takes a minute or two per carousel. For a Story shape add `--size story` (the slide sits centered on the taller canvas). Add the first frames to your check: pull one frame with ffmpeg (`ffmpeg -ss 2 -i file.mp4 -frames:v 1 frame.png`) and look at it. If ffmpeg is not installed, skip this step and mention in the final reply that animated versions are available once ffmpeg is installed.

## 6b. Look for gaps

Before you plan the calendar, ask yourself:
- Does every piece pass the mirror test in `engine/copy-principles.md`? Could her reader say "that is me" within the first three lines, and does the first line hit one clear gut-level need (the primal layer)? Rewrite the opening of any that could be about anyone.
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

## 8b. Make the visual page (always)

Every run ends with one visual page the person can open without touching a folder. Run:

`python3 scripts/build_artifact.py outputs/<batch-folder>`

This first brings everything up to date: it rebuilds every slide and quote graphic from the latest plans (so edits made in Carousel Studio carry over), re-renders the swipe-through video of any carousel whose slides changed, and then builds the page. It can take a few minutes the first time. The page has download buttons (all slides as a zip, the PDF, the video, each quote, all quotes as a zip), so the person never has to open a folder.

It writes `outputs/_pages/<batch-folder>/index.html` and the full-quality videos in `f/`, listed in `files.json`. Publish with the Artifact tool: `file_path` is that `index.html`, `root` is that `outputs/_pages/<batch-folder>` folder, `files` is the content of `files.json`, `capabilities` is `{"downloads": true}` (this is what lets the buttons save files), `icon` is "library", and the title comes from the page. Call the Artifact `quickstart` first if you have not this session, and read the `artifact-capabilities` skill. Reuse the same URL for later runs of the same batch (pass `url`). Give the person the link in the reply. If publishing is not available, say so in one plain line and point them to `00-preview.html` instead.

**Any time the person says they changed, edited, or exported a carousel** (in Carousel Studio or by asking you), or says the page looks out of date, run the same command again and republish to the same URL. That keeps the images, PDF, videos and downloads on the page in line with what they made.

## 9. Reply

Short. What you made (counts and the total), the link to the visual page, where else to open it, the first post they should publish tomorrow and why, and what to double-check. Move processed files from `inbox/` into `inbox/done/` (keep `_text/` as is).

Do not recap the steps.
