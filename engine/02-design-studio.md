# Design studio

Goal: pick their brand look once, then every carousel and quote graphic is made in it automatically.

The studio is a web page (`design/studio.html`) that shows every layout with their colors and fonts, live. They can click around in it, or just tell you what they want in plain words. Both work.

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
- Tell them which layouts you recommend for carousels and which for quote graphics, and why, in one line each. Layouts: Editorial, Bold Block, Soft Card, Minimal, Spotlight (dark), Notebook (handwritten), Photo Card, Polaroid, Big Number, Banner, Chat Bubbles, Sticker Pop, Arch, Glow. Suggest by audience: Arch and Polaroid for faith and wellness, Big Number and Banner for teaching and frameworks, Chat Bubbles for relatable mindset content, Sticker Pop for bold or younger brands, Glow and Spotlight for business, Photo Card for photo-heavy brands. Two or three layouts rotate nicely across a pack. One keeps it very consistent. Use the same decoration style across all of them.
- If they want something the layouts do not do, you may edit that layout's `layout.css` copy under `design/layouts/`. Make a new folder for a custom layout rather than changing a built-in one, and add a `meta.json` with `label`, `vibe`, and `best_for`.

## Step 3b. Make it extra: photos, decorations, textures, motion

Ask once, in plain words, which of these they want. Offer it as a menu, and show a quick preview of the ones they pick.

- **Decorations.** Hand-drawn doodles, shapes, and stickers in their colors. `decor`: `none`, `light`, `rich`. Style `decor_theme`: `playful` (circles, squiggles, arrows, stars), `botanical` (sprigs, flowers, arches, soft shapes), `minimal` (rings, plus signs, fine lines), `bold` (bursts, zigzags, big shapes).
- **Background texture.** `bg_style`: `flat`, `mesh` (soft gradient glow), `grain`, `paper`, `dots`, `stripes`, `waves`, `grid`.
- **Highlighted words.** `highlight`: `layout` (each layout's own), `underline` (wavy), `circle` (hand-drawn), `marker` (highlighter), `box`.
- **Photo backgrounds.** They drop photos in `brand/photos/`. The engine puts them behind cover, closing, and quote slides with a readable overlay. Photo-first layouts: Photo Card and Polaroid. If they have no photos, offer image prompts for an AI image tool, or tell them to pick photos they have a license to use. Photo settings in `brand.json`: `photos.auto` (true or false), `photos.tone` (`dark` overlay with white text, or `light` overlay with dark text for bright photos), `photos.scrim` (0.3 to 0.8, how strong the overlay is).
- **Animation.** Every carousel and quote graphic can also come out as a short animated video: words reveal one by one, doodles draw themselves, photos slowly zoom, slides swipe into each other. This needs the free tool ffmpeg. `python3 scripts/doctor.py` says whether it is installed. If it is not, tell them how to install it (Mac: `brew install ffmpeg`, Windows: `winget install Gyan.FFmpeg`, Linux: `sudo apt install ffmpeg`) and carry on without video.

Save choices with `save_brand.py`, rebuild the studio with `python3 scripts/studio.py`, and tell them to refresh the page. The studio previews decorations, textures, and highlights live. Photos show on the studio slides when the buyer has some.

## Step 4. Show a real one

Make a real sample so they see actual images, not just the page:

1. `mkdir -p design/preview && cp examples/sample-carousel.json design/preview/carousel.json`
2. Edit that copy so the text mentions their topic. Include a few of the newer slide types (a `stat`, a `versus`, a `checklist`) so they see the range, plus their photos if they have any.
3. `python3 scripts/render.py design/preview`
4. Open the first, middle, and last PNG with the Read tool so you can see them. Check that text fits, colors have good contrast, and nothing is cut off. Fix and re-render if not.
5. Tell them where the images are (`design/preview/`) and show them.
6. If they chose animation and ffmpeg is installed, run `python3 scripts/animate.py design/preview --seconds 3` and tell them where `carousel-animated.mp4` is. It takes a minute or two.

## Step 5. Lock it in

Confirm: which layouts for carousels, which for quote graphics, whether to show their logo, handle, swipe hint, and page numbers. Save with `save_brand.py`. Then say: "Your design is saved. Drop in your first transcript whenever you are ready and say run it."

If they already gave you material, go straight to `engine/03-run-pipeline.md`.

## Notes

- Image sizes: portrait 1080 by 1350 (best for Instagram), square 1080 by 1080, story 1080 by 1920. Change with `size`.
- Everything is made by the Chrome (or Edge, Brave, Chromium) already on their computer. If `doctor.py` says no browser, tell them to install Google Chrome, which is free.
- Bundled fonts are open license and safe to use commercially. Custom fonts they add are their responsibility.
