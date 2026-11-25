# Design studio

Goal: pick their brand look once, then every carousel and quote graphic is made in it automatically.

The Design Studio is a web page (`design/studio.html`) where they pick their colors, fonts, name and handle, and watch every carousel layout change live in their choices. Their colors and fonts become the "My brand" theme in Carousel Studio, which makes all their carousels and quote graphics (36 layouts, see `engine/06-carousel-studio.md`).

## Step 1. What do they already have?

Ask (multiple choice):
- "I have brand colors and fonts"
- "I have a logo but no colors or fonts"
- "I have nothing yet, help me pick"

### I have them
Ask for the colors (hex codes like #4A1D5C, or color names, or tell them they can drop their logo and you will pull the colors from it) and font names. If they give fonts that are not bundled, ask if they have the font files. Files go in `brand/fonts/` and the engine uses them by name. If they do not have the files, pick the closest bundled pairing and say so.

### I have a logo
Ask them to drop it in `brand/` named `logo.png` (or .jpg, .svg). Open it and look at it. Suggest a palette that fits and confirm the exact hex codes with them before saving.

### Help me pick
Read `design/palettes.json` and `design/fonts/fonts.json`. Offer three palettes and two font pairings that fit their audience and voice (from `brand/profile.md` and `brand/voice.md`). Explain each in a few plain words.

## Step 2. Start the studio

1. Save a starting design with their name, handle, and best-guess colors and fonts:
   `python3 scripts/save_brand.py '{"name":"...","handle":"@...","colors":{...},"fonts":{"heading":"...","body":"...","accent":"..."},"size":"portrait","cta_label":"..."}'`
   Colors needed: `bg` (page), `ink` (text), `accent`, `accent2` (soft accent), `muted`, `bg_dark`. If they only gave one or two colors, derive the rest sensibly: light `bg`, dark readable `ink`, `accent2` a softer tint of the accent, `muted` a mid gray that matches. Keep contrast readable.
   Use their `cta_label` from `brand/offer.md` (for example "Comment GROW").
2. Build the page: `python3 scripts/studio.py`
3. Open `design/studio.html` for them. On a Mac run `open design/studio.html`. On Windows run `start design\studio.html`. On Linux run `xdg-open design/studio.html`. If you can drive a browser, use that. If none of that works, tell them the file to double-click.
4. Tell them: "This is your Design Studio. Every layout is shown in your colors. Click a color to change it, try the font pairings, and tick the layouts you like. When you are happy, press Copy my settings and paste it here. Or just tell me what to change."

## Step 3. Tweak until they love it

- If they paste a block of settings, run `python3 scripts/save_brand.py '<what they pasted>'`, then rebuild the studio.
- If they ask in plain words ("warmer accent", "bolder fonts", "I like the third one"), change `brand/brand.json` through `save_brand.py`, rebuild with `python3 scripts/studio.py`, and tell them to refresh the page.
- Layouts: show them what Carousel Studio can do with their colors: `python3 scripts/carousel_studio.py gallery --theme brand`, then show `design/carousel-studio/gallery/gallery-brand.jpg` with the Read tool. Each carousel in a pack automatically gets one of three looks (editorial, bold, soft), and any slide can be changed later.

## Step 3b. Photos and motion

Ask once, in plain words, which of these they want.

- **Photo backgrounds.** They drop photos in `brand/photos/`. Carousel Studio puts them behind covers, closing slides and quotes automatically. If they have no photos, offer to make pictures from written prompts with their own paid image service (`engine/08-images.md`), or tell them to use photos they have a license to use. Never download pictures from the web for them.
- **Animation.** Every carousel and quote graphic can also come out as a short animated video: text rises in line by line, photos drift slowly, slides swipe into each other. This needs the free tool ffmpeg. `python3 scripts/doctor.py` says whether it is installed. If not, tell them how (Mac: `brew install ffmpeg`, Windows: `winget install Gyan.FFmpeg`, Linux: `sudo apt install ffmpeg`) and carry on without video.
- **Theme tweaks.** In the browser editor they can change any color or font for one carousel, or pick one of 8 ready-made themes.

Save colors and fonts with `save_brand.py`, rebuild the Design Studio page with `python3 scripts/studio.py`, and tell them to refresh it.

## Step 4. Show a real one

Make a real sample so they see actual images, not just the page:

1. `python3 scripts/carousel_studio.py new design/preview --theme brand --title "Sample"` (starter slides in their design).
2. `python3 scripts/carousel_studio.py build design/preview`
3. Open `design/preview/contact-sheet.jpg` with the Read tool. Check that text fits, colors have good contrast, and nothing is cut off. Fix and rebuild if not.
4. Show them the contact sheet and tell them where the images are (`design/preview/slides/`).
5. If ffmpeg is installed and they want motion: `python3 scripts/animate.py design/preview --seconds 3` and tell them where `carousel-animated.mp4` is.

## Step 5. Lock it in

Confirm: which layouts for carousels, which for quote graphics, whether to show their logo, handle, swipe hint, and page numbers. Save with `save_brand.py`. Then say: "Your design is saved. Drop in your first transcript whenever you are ready and say run it."

If they already gave you material, go straight to `engine/03-run-pipeline.md`.

## Notes

- Image sizes: portrait 1080 by 1350 (best for Instagram), square 1080 by 1080, story 1080 by 1920. Change with `size`.
- Everything is made by the Chrome (or Edge, Brave, Chromium) already on their computer. If `doctor.py` says no browser, tell them to install Google Chrome, which is free.
- Bundled fonts are open license and safe to use commercially. Custom fonts they add are their responsibility.

## Small details per layout

A brand can set the color of three details, and they apply every time: the tape on note cards, the bookmark on save slides, and the circle on post cards. Save them in `brand/brand.json` under `layout_colors`, for example `{"layout_colors": {"note-card": {"tape": "#131313"}, "cta-save": {"bookmark": "#131313"}, "quote-post": {"avatar": "#131313"}}}`, using `python3 scripts/save_brand.py`. Without it, those details use the main accent color.
