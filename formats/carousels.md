# Carousels

Finished slide images for Instagram and Facebook. You write JSON. `scripts/render.py` turns it into PNGs and a PDF in the person's design.

## Where it goes
`carousels/NN-<slug>/carousel.json` and `carousels/NN-<slug>/caption.md`

## JSON shape
```json
{
  "title": "Internal name",
  "layout": "optional, a layout name; leave out to rotate through their picks",
  "slides": [
    {"type": "cover", "kicker": "short label", "headline": "The hook", "sub": "optional line"},
    {"type": "point", "kicker": "01", "headline": "One idea", "body": "One to three short sentences."},
    {"type": "list", "kicker": "The list", "headline": "Title", "items": ["short", "short", "short"]},
    {"type": "quote", "text": "A line worth screenshotting", "attribution": "optional"},
    {"type": "close", "headline": "The invitation", "body": "One line", "cta": "Comment GROW"}
  ],
  "caption": "see below"
}
```
Wrap one or two key words in `**double asterisks**` to highlight them. Do it on a few slides, not every slide.

## More slide types
Use these to make carousels feel designed, not just text on color. Use each only when the content truly fits.

```json
{"type": "stat", "kicker": "Real talk", "number": "20 min", "label": "is all you need to begin", "body": "optional line"}
{"type": "versus", "headline": "optional", "left_label": "Myth", "left": "the false belief", "right_label": "Truth", "right": "what is actually true"}
{"type": "checklist", "headline": "Before you post", "items": ["short", "short", "short"]}
```
- `stat`: one number or short phrase from the source that really is a number or a stat. Never make up a number.
- `versus`: a myth and truth pair the speaker really makes. Great for beliefs the teaching challenges.
- `checklist`: steps or reminders the teaching gives, 3 to 6 items.
- A `point` slide with a kicker that is just a number ("01", "02") shows a giant numeral in some layouts.

## Photos
A slide can take a photo background: add `"image": "file-name.jpg"` (a file in `brand/photos/`). Add `"image": false` to keep a slide plain. If the person has photos in `brand/photos/`, the engine puts them on cover, closing, and quote slides automatically, so you do not have to. Optional per slide: `"image_focus": "top"` (or "bottom", "left", "right", "center") to choose which part of the photo shows, and `"tone": "light"` for bright photos.

If they use AI or stock images and have none yet, write `photo-prompts.md` in the carousel folder: 3 to 5 image prompts that match the carousel's mood, with no text in the image, no people's faces unless they asked, and plenty of calm space for text. Tell them to save the images in `brand/photos/`.

## Decoration and animation
Decorations (doodles, shapes, textures) are added by the design settings. You do not write them. To turn them off for one slide add `"decor": "none"`.
Animated versions are made from the same JSON by `scripts/animate.py`. Keep headlines short, because animated text reveals word by word.

## Structure
- 6 to 10 slides. First is a `cover`, last is a `close` with the next step.
- Cover headline: 14 words or fewer. It must stop a scroll: a belief challenged, a truth named, a specific problem, or a promise the carousel really keeps.
- Each `point` slide holds one idea. Body 45 words or fewer, usually 15 to 30.
- `list` slides: 3 to 6 items, each 14 words or fewer.
- Use at most one `quote` slide. Use a `list` slide only when the content really is a list. Mix in a `stat`, `versus`, or `checklist` when the content fits it.
- Each slide should make sense alone and make the reader want the next one. End slides on a turn, not a summary.
- The close slide has exactly one next step in the exact wording from `brand/offer.md`.

## Caption (`caption.md`)
Plain text the person pastes in. 60 to 150 words. Opens with a line that is NOT a repeat of the cover. Adds something the slides did not say. Ends with the same single next step. Add 3 to 5 relevant hashtags at the end only if `brand/profile.md` says they use hashtags.

## Variety across a pack
Different openings: a challenged belief, a named feeling, a plain instruction, a question, a short story from the source. Different shapes: a few teaching carousels, one story-led, one list, one myth-vs-truth.
