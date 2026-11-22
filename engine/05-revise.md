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
| "Make it sound more like me" | Ask for one example of something that sounded right and one that did not. Update `brand/voice.md` and `brand/voice-samples.md`. Rewrite the pieces they pointed at. |
| "More of X" (more threads, more quotes) | Read the extraction, pick unused angles, add the new pieces, run the checks, and update the calendar. |
| "Take out the word Y" or "never say Y" | Add Y to `config.json` `rules.ban_words`. Fix existing pieces. |
| "Change the next step" | Update `brand/offer.md`, then fix the pieces and the plan. |
| "I do not like em dashes being banned" | Set `rules.ban_em_dash` false in `config.json`. |
| "Start fresh on this batch" | Confirm once, then re-run `engine/03-run-pipeline.md` into a new folder. Do not delete the old one. |

## After any change

1. Run `python3 scripts/check.py` on what you touched.
2. If images changed, look at them with the Read tool.
3. If the calendar is affected, update `plan.json` and run `build_calendar.py`.
4. Reply in one or two lines: what changed and where to look.

## Teach the engine

When they tell you what they like or hate, and it is a lasting preference (not only this piece), add it to `brand/voice.md` so the next run starts better. Say you did.
