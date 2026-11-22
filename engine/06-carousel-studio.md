# Carousel Studio

Goal: one carousel, made with the person step by step: words first, then design, then a beat sheet of every slide, then the browser editor where they change anything and export.

Use this when they say "make me a carousel", "design this carousel", "open the carousel editor", "change the layout of slide 3", or want more layout choices than a run pack gives. A finished pack carousel (`outputs/<batch>/carousels/NN-x/`) can be opened here too: the studio reads its `carousel.json` and turns it into a `plan.json` the first time.

Everything lives in one folder per carousel. Put new ones in `outputs/carousels/<short-name>/` unless they name a place.

## Step 1. Words first (they approve before any design)

1. Write the slide script from their material, following `formats/carousels.md` for structure and the hard rules in `CLAUDE.md`. Run `python3 scripts/check.py` on it.
2. Show it as a short table in chat: slide number, kind of slide (cover, point, list, quote, number, compare, closer), and the words. Then ask once: "Want any words changed before I design it?"
3. Change what they ask. Do not design until they say the words are right.

## Step 2. Design pass

1. Make the folder: `python3 scripts/carousel_studio.py new <folder> --look <look> --theme <theme>`. Then replace the starter slides in `<folder>/plan.json` with the approved words.
2. Photos: copy the ones they give you into `<folder>/photos/`. Their saved photos in `brand/photos/` work too. Never invent or generate a photo of a real person.
3. Pick a layout for each slide that fits its words (a list gets a list layout, a number gets a number layout). Mix two or three families, not ten. Give photo slides a photo and set `y` so faces sit well (30 to 40 is usually right for portraits).
4. Show them the layout choices when it helps: `python3 scripts/carousel_studio.py gallery --theme <theme>` makes `design/carousel-studio/gallery/gallery-<theme>.jpg`. Show the image.

## Step 3. Beat sheet

`python3 scripts/carousel_studio.py build <folder>` makes every slide plus `contact-sheet.jpg` (all slides on one page, numbered, with each layout's name). Show them the contact sheet and ask for notes by slide number. Fix and rebuild until they say it looks good.

## Step 4. The editor

`python3 scripts/carousel_studio.py edit <folder>` opens the editor in their own browser (run it in the background; it keeps running while they edit). Tell them: "Click any words to change them, pick a new layout on the right, drag a photo to move it, drag slides on the left to reorder. When you love it, press Export." Export saves `slides/`, `caption.txt`, `contact-sheet.jpg` and a zip with all of it in the carousel folder.

Every change they make in the editor saves into `plan.json`, so you can keep working from it in chat. Read `plan.json` again before you change anything after they have edited.

## plan.json

```json
{
  "title": "Starting before you feel ready",
  "look": "editorial",
  "theme": "brand",
  "theme_overrides": {"colors": {"accent": "#B3264A"}, "fonts": {"head": "Playfair Display"}},
  "show_handle": true, "show_numbers": true, "show_swipe": true,
  "caption": "The words under the post.",
  "slides": [
    {"role": "cover", "layout": "photo-full", "kicker": "small label", "headline": "The **hook**", "body": "one line",
     "photo": {"src": "me.jpg", "x": 50, "y": 30, "zoom": 1}},
    {"role": "list", "layout": "checklist", "headline": "Title", "items": ["one", "two", "three"]},
    {"role": "stat", "layout": "stat-giant", "number": "80%", "headline": "what the number means"},
    {"role": "compare", "layout": "before-after", "left_label": "Before", "left": "...", "right_label": "After", "right": "...",
     "photo": {"src": "a.jpg"}, "photo2": {"src": "b.jpg"}},
    {"role": "quote", "layout": "quote-verse", "headline": "The quote", "sub": "Reference or name"},
    {"role": "close", "layout": "cta-comment", "headline": "The invitation", "cta": "WORD", "body": "one line"}
  ]
}
```

- Every layout reads the same fields, so switching layouts keeps the words. `**double stars**` color a word.
- `layout` is optional. Without it a slide uses the carousel's `look` for its `role`.
- Looks: `editorial`, `photo-story`, `bold`, `soft`. Themes: `python3 scripts/carousel_studio.py themes` (`brand` is their own design from `brand/brand.json`).
- Layout ids and what they show: see `design/carousel-studio/layouts.js` (each has a name, group and the fields it uses).
- Numbers and stats must come from the source. Never make one up.
