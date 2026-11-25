# Carousel Studio

Make Instagram carousels with 36 layouts to choose from, then change anything in your browser before you post.

## How it works

1. **Words first.** Tell Claude what the carousel is about, or hand it your material. You get the slides as plain words to approve before anything is designed.
2. **Design.** Claude picks a layout for each slide and places your photos. Want to see every choice? Say **"show me the carousel layouts."**
3. **Beat sheet.** You get one picture with every slide numbered. Give notes by number: "make 3 a checklist, swap the photo on 1."
4. **Editor.** Say **"open my carousel editor."** It opens in your browser.
5. **Export.** Press **Export slides + caption.** You get every slide at Instagram size (1080 by 1350), your caption, and a zip with all of it.

## In the editor

- **Change words:** click them on the slide and type. Wrap a word in `**double stars**` to color it. In a list, Enter adds a line.
- **Change the layout:** the Layout tab shows your slide in every layout. Click one. "Use this layout on every point slide" matches them all.
- **Photos:** drag a photo on the slide to move it, scroll on it to zoom. The Photo tab adds new photos (drop them in) and swaps them.
- **Reorder:** drag slides up and down on the left. Duplicate and Delete are above the slide.
- **Theme:** pick one of 9 themes (yours is "My brand"), then change any color or font.
- **Caption:** write or paste it in the Caption tab and copy it with one click.
- **Undo:** the Undo button, or Cmd+Z (Ctrl+Z on Windows).

Your work saves as you go. Close the tab any time and say "open my carousel editor" to come back.

## The layouts

- **Photo-led:** full photo, framed photo, photo on top, arch window, polaroid, photo + card, magazine cover
- **Type-led:** big type, color block, editorial page, outline word, note card, big question, definition, sticker cover
- **Quote:** classic quote, quote on photo, post card, verse frame
- **Number:** giant number, progress ring, number + photo
- **Lists and steps:** numbered list, step timeline, checklist, four tiles, list + photo
- **Split and compare:** half photo, diagonal split, before / after, myth vs truth, this not that
- **Closer:** comment a word, save this, photo closer, follow me

Every layout works in every theme, with your fonts and colors.

## Make it move

Say **"animate this carousel."** You get one swipe-through video for a Reel or Story, plus a short clip for each slide. Text rises in line by line, photos drift slowly, and slides swipe into each other. This needs the free tool ffmpeg (Claude tells you if it is missing).

## No photos?

Say **"make me photos."** Claude writes a short description for each picture and, with your own OpenAI or Google Gemini key, makes them for you. The service charges a few cents per picture, and Claude asks before spending anything.

## Good to know

- You need Google Chrome (or Edge, Brave, Chromium) installed. The editor opens in whichever browser you use.
- Each carousel is one folder in `outputs/carousels/`: `plan.json` (the slides), `photos/`, and after export `slides/`, `caption.txt`, `contact-sheet.jpg` and a zip.
- Use photos you took or have the right to use.
