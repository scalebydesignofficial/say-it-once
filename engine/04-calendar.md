# Content calendar

Goal: a day-by-day plan of what to post, where, and when, built from the pieces in a batch. Less planning for them, more posting.

## Inputs

- Every piece made in the batch (read each source's folders)
- `config.json` `cadence` (start date, posting days, horizon in days, max pieces per day, time slots)
- `brand/profile.md` (platforms, time available) and `brand/offer.md` (what they are pushing)

If `cadence.start_date` is null the script starts on the next Monday.

## Write `plan.json` at the batch root

```json
{
  "title": "Batch name",
  "pieces": [
    {"id": "s1-car-01", "format": "carousel", "platform": "Instagram",
     "title": "Short title", "hook": "The opening line they will see",
     "stage": "reach", "day": 1, "slot": "morning",
     "file": "01-lesson/carousels/01-name/slide-01.png",
     "caption_file": "01-lesson/carousels/01-name/caption.md",
     "cta": "The one next step in plain words"}
  ]
}
```

Fields:
- `format`: carousel, quote, reel, short-video, thread, note, substack-article, blog, email, instagram-post, story, facebook-post, linkedin-post, pinterest-pin, youtube
- `video_file`: optional path to an animated version (for example `01-lesson/carousels/01-name/carousel-animated.mp4`)
- `stage`: reach, warm, or ready (see `brand/offer.md`)
- `day`: posting day number (1 is the first posting day). Leave it out or use `"status": "bank"` for pieces saved for later.
- `slot`: morning, midday, or evening
- `file` and `caption_file`: paths relative to `plan.json`. They must exist.

## How to schedule

1. **Pick the horizon.** Fill the `horizon_days` window from `config.json`. Choose the strongest pieces for the window. Put the rest in the content bank (no `day`). A big batch will have far more pieces than days. That is fine and good: the bank is the next two months.
2. **Strongest first.** Open with the single best scroll-stopper from the batch, not the most general piece.
3. **Arc.** Use the stage mix across the window: about 40 percent reach, 35 percent warm, 25 percent ready. Start with reach and trust, move into teaching and story, and end the window with a clear invitation. Do not put a hard next step in the first three days.
4. **Variety.** Never the same main format two days in a row. If reels are on, at least two a week. Carousels two or three a week. Quote graphics fill gaps and can post alongside a heavier piece.
5. **Each day:** one main piece (carousel, reel, or short video), plus optional supporting pieces (a thread, a note, a quote graphic). Respect `max_pieces_per_day`.
6. **Long form.** One Substack article and one blog post per week if those are on. Emails on two fixed weekdays (usually Tuesday and Thursday). Put long-form on days with a lighter main piece.
7. **Slots.** Scroll content (carousels, quotes) in the morning. Text pieces (threads, notes, Facebook posts, LinkedIn posts, Instagram text posts) at midday. Pinterest pins and YouTube uploads in the evening. Story sequences in the afternoon or evening. Video (reels, short videos) in the evening. Emails in the morning.
8. **Multiple sources.** For a course or series, keep lesson order: the first lesson's best pieces lead. For unrelated sources, interleave them so no two days feel the same.
9. **Spread one source out.** Pieces from the same source should not all land the same week unless it is a launch or a series.
10. **Match their time.** If they said they have little time, schedule fewer pieces per day and group video days.

## Then

1. Run `python3 scripts/build_calendar.py outputs/<batch-folder>/plan.json`.
2. Read the warnings it prints (missing files, heavy days, repeated formats) and fix `plan.json`. Re-run until clean.
3. Tell them: "Open content-calendar.html for the day-by-day view. The CSV opens in Google Sheets or Excel, and imports into most schedulers."

## If they ask for a calendar later

For "make me a 60-day calendar" or "start on December 1": update `config.json` `cadence` (`horizon_days`, `start_date` as YYYY-MM-DD), pull more pieces out of the bank, rewrite `plan.json`, and run the script again.

## Batch tasks

In `00-start-here.md`, add a short "this week" list: when to record reels, when to schedule emails, when to review the scripture or fact list. Keep it to five lines.
