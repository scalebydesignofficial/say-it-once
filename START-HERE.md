# Say It Once

Say it once. Drop in a transcript, a course lesson, a voice note, or any text. Get back a full pack in your voice and your brand: carousels and quote graphics as finished images and as animated videos, reel scripts you can record or paste into an AI avatar tool, short video spinoffs, talking points for lives and extra content, Instagram posts and Stories, Facebook posts, threads, Substack notes and articles, blog posts, emails, and a day-by-day content calendar.

You never type commands. You talk to it in plain words.

## Set up (about 10 minutes, once)

1. Install Google Chrome if you do not have it. It is free. The engine uses it to make your images.
2. Install Claude Code and open it inside this folder.
3. Say: **set me up**

It asks you a few questions about your business, your people, and how you sound. Then it opens your Design Studio so you can pick your colors, fonts, and carousel look.

## Every time after that

1. Put your material in the **inbox** folder (or paste it right into the chat).
2. Say: **run it**

When it finishes, open these:
- `outputs/<your batch>/00-preview.html` to see all your images
- `outputs/<your batch>/content-calendar.html` for what to post each day
- `outputs/<your batch>/00-start-here.md` for the first three days and a short list of things to double-check

## Make it look amazing

- 14 carousel designs. Pick one or let it rotate through a few.
- Decorations: hand-drawn doodles, shapes, and textures in your colors.
- Photo backgrounds: drop your photos in `brand/photos/` and they go behind your cover, closing, and quote slides.
- Animated carousels: words reveal one at a time, doodles draw themselves, slides swipe into each other. Post them as video slides, or as a Reel or Story. This needs a free tool called ffmpeg. Mac: `brew install ffmpeg`. Windows: `winget install Gyan.FFmpeg`. The setup check tells you if you have it.

## Things you can say

- "Show me designs" or "change my colors"
- "Make the reels shorter"
- "Redo carousel 3, punchier"
- "Try a different layout for this one"
- "Add my photos to the carousels"
- "Make the doodles more botanical"
- "Make me a carousel" or "Open my carousel editor" (36 layouts, edit in your browser, see CAROUSEL-STUDIO.md)
- "Animate this carousel for a Story"
- "Make me a 60 day calendar starting December 1"
- "Give me talking points for a Live"
- "More threads from this lesson"
- "This does not sound like me" (it will ask for an example and learn)

## Good to know

- It writes from your material. It will not make up stories, numbers, or quotes. Anything it was not sure about is listed in the review file. Read that list before you post.
- If you teach scripture, it paraphrases with a reference and lists every one for you to check against your own translation.
- It prepares everything. You publish. It never posts for you.
- Use your own fonts: drop the font files in `brand/fonts/` and name them like `Family-Bold.woff2`, `Family-Italic.ttf`. Then say "use my font."
- Bundled fonts are free open-license fonts (see `design/fonts/LICENSE-*.txt`).
- Short material makes a smaller pack. Under about 800 words you get half the usual amount.
- The image maker works with Chrome, Edge, Brave, or Chromium on Mac, Windows, or Linux.

## If something looks off

Say what you see: "the text is cut off on slide 4" or "the calendar skipped Sunday." It will fix it and re-check.
