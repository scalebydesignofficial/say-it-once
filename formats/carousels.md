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
Carousels are built by Carousel Studio (`python3 scripts/carousel_studio.py pack <batch>`). It puts photos on covers, closers and quotes by itself: first any picture made for that exact slide (see below), then the person's own photos in `brand/photos/`. You do not choose photo layouts. If they have no photos and want some, write `photo-prompts.json` in the carousel folder (see `engine/08-images.md`): 2 or 3 prompts, each tied to a slide number (the cover, the closer, a quote), with no text in the image, no people's faces, and plenty of calm space for words. Then `engine/08-images.md` explains making the pictures.

`"image"` and `"image_focus"` on a slide are not used any more. To pick a specific photo for one slide, give that slide `"photo": {"src": "file.jpg", "x": 50, "y": 30, "zoom": 1}` in the carousel's `plan.json`.

## Layouts and look
You do not pick layouts when you write `carousel.json`. The pack builder gives each carousel one of three looks (editorial, bold, soft) in turn and chooses a layout for every slide from its type. Write each slide's `type` carefully (`checklist` for steps, `versus` for a myth and truth, `stat` for a real number) because that is what picks the layout. A quote slide with an `attribution` (a name or a Scripture reference) is always given a layout that shows it. The person can change any layout later in the browser editor or by asking.

## Animation
Animated versions are made from the same slides by `scripts/animate.py` (text rises in line by line, photos drift, slides swipe together). Keep headlines short so they read well while they move.

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
