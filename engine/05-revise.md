# Revise

They will ask you to change finished work in plain words. Do it, check it, and tell them what changed. Never regenerate a whole pack when a small change will do.

## Common asks

| They say | You do |
| --- | --- |
| "Make the reels shorter" | Rewrite the `reel-NN.md` and `.spoken.txt` files to the new length. Keep each hook. |
| "Redo carousel 3, punchier" | Rewrite that carousel's `carousel.json` and caption, run `check.py`, re-render just that folder: `python3 scripts/render.py <that carousel folder>`. |
| "Use a different layout for this one" | Set `"layout": "bold-block"` (or another layout name) in that `carousel.json`, then re-render that folder. |
| "Change my colors or fonts" | Follow `engine/02-design-studio.md`. Then re-render the whole batch: `python3 scripts/render.py <batch folder>`. |
| "Animate this carousel" or "make it a Story" | `python3 scripts/animate.py <carousel folder>` (add `--size story` for 9:16). Needs ffmpeg. |
| "Use my photos" or "lighter photos" | Photos go in `brand/photos/`. Change `photos.tone` to `light` or `photos.scrim` with `save_brand.py`, then re-render the batch. |
| "More doodles" or "less decoration" | Change `decor` and `decor_theme` with `save_brand.py`, then re-render. |
| "Make it more engaging", "stronger hook", "make it feel like she is talking to me" | Read `engine/copy-principles.md`. Rewrite the opening from scratch: find the mirror line, pick a different hook shape, cut warm-up. Keep their voice and the facts. Run the mirror test. |
| "Make it sound more like me" | Ask for one example of something that sounded right and one that did not. Update `brand/voice.md` and `brand/voice-samples.md`. Rewrite the pieces they pointed at. |
| "More of X" (more threads, more quotes) | Read the extraction, pick unused angles, add the new pieces, run the checks, and update the calendar. |
| "Take out the word Y" or "never say Y" | Add Y to `config.json` `rules.ban_words`. Fix existing pieces. |
| "Change the next step" | Update `brand/offer.md`, then fix the pieces and the plan. |
| "I do not like em dashes being banned" | Set `rules.ban_em_dash` false in `config.json`. |
| "Stop making blog posts" (or any format) | Set that format to `false` in `config.json` `formats` (stories follow Instagram posts; talking points can be switched off too). Say it is off and how to turn it back on. |
| "Start making LinkedIn" (or Pinterest, YouTube, any format) | Set it to `true` in `config.json` `formats`. If they have never posted there, ask where to send people from there, and add it to `brand/offer.md` if needed. |
| "Make fewer emails" or "I want more carousels" | Change that format's number in `config.json` `counts`. |
| "Make my packs bigger" or "smaller" | Set `pack_size` in `config.json` to `small`, `standard` or `big`. |
| "Only carousels this time" | Nothing is saved. Run `engine/03-run-pipeline.md` and use `pack_plan.py --only visuals` (or the format name). |
| "Start fresh on this batch" | Confirm once, then re-run `engine/03-run-pipeline.md` into a new folder. Do not delete the old one. |

## After any change

1. Run `python3 scripts/check.py` on what you touched.
2. If images changed, look at them with the Read tool.
3. If the calendar is affected, update `plan.json` and run `build_calendar.py`.
4. Reply in one or two lines: what changed and where to look.

## Teach the engine

When they tell you what they like or hate, and it is a lasting preference (not only this piece), add it to `brand/voice.md` so the next run starts better. Say you did.
