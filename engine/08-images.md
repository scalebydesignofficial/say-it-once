# Pictures (photos for carousels and quotes)

Goal: real pictures behind their covers, closers and quotes when they have no photos of their own, made from short written prompts by an image service they pay per picture. Their own photos always come first.

Use this when they say "make me photos", "make the images", "I have no photos", "add pictures to my carousels", or when a pack is being built and they have no photos in `brand/photos/`.

## Rules for every picture

- Never a picture of a real person. Never the owner's face or likeness (they use their own photos for that). No logos, no brand names, no characters from anything.
- No words, letters or numbers in the picture. The slide adds the words.
- Calm, uncluttered pictures with empty space where words can sit. Mood, light, places, objects, nature, textures.
- Match their world (`brand/profile.md`) and their colors (`brand/brand.json`). Faith content: quiet and warm, never churchy clip art.
- Say plainly that the pictures are AI-made if they ask. Never claim an AI picture is a real photo of a real place or person.

## Step 1. Write the prompts

For each carousel, write `photo-prompts.json` in that carousel's folder:

```json
{"images": [
  {"slide": 1, "prompt": "Soft morning light on a wooden kitchen table, an open journal and a coffee cup, shallow depth of field"},
  {"slide": 9, "prompt": "Warm sunrise through a window, curtains moving, quiet and hopeful"}
]}
```

- `slide` is the slide number the picture goes on. The cover, the closer and one quote are the best slides for a picture. Two or three pictures per carousel is plenty. Text-only slides look good too.
- One prompt is 1 to 3 sentences: the subject, the light, the feeling. No text, no people's faces.
- For mood pictures they can use on anything, write `brand/photo-prompts.json` with `{"name": "calm-sky", "prompt": "..."}` entries instead of slide numbers. Those land in `brand/photos/` and are used automatically on covers, closers and quotes.

## Step 2. Is a service set up?

Run `python3 scripts/make_images.py status`.

If it says no key, tell them in plain words: "To make real pictures I need a key from OpenAI or Google Gemini. It is like a password that lets me ask them for pictures, and they charge a few cents per picture. Set a monthly spending limit when you create it." Give the page: OpenAI keys are at platform.openai.com/api-keys, Gemini keys at aistudio.google.com/apikey. When they paste the key, save it with the Write tool to `brand/image-keys.json` as `{"openai": "..."}` or `{"gemini": "..."}`. Do not repeat the key back, do not put it anywhere else, and never put it in a command line. Tell them it stays on their computer.

If they would rather not, stop here. The prompts are saved, and they can paste them into any image tool and drop the files into the carousel's `photos/` folder named `slide-01.png`, `slide-09.png` and so on.

## Step 3. Ask before spending

Run `python3 scripts/make_images.py plan outputs/<batch-folder>`. Tell them how many pictures it will make and that the service charges for each one (check the current price on their service's pricing page; do not quote a number). Ask once: make them now, or just keep the prompts. Do not spend money without a yes.

## Step 4. Make them

`python3 scripts/make_images.py make outputs/<batch-folder>`

It skips pictures that already exist, so it is safe to run again. Look at each new picture with the Read tool. If one has words in it, a recognizable person, or is cluttered, delete that file, tweak the prompt in `photo-prompts.json`, and run the command again (it only makes what is missing).

## Step 5. Put them on the slides

`python3 scripts/carousel_studio.py pack outputs/<batch-folder>`

The pack builder sees the new pictures and puts each on its slide with a layout made for photos. Then continue with the rest of `engine/03-run-pipeline.md`.

## If something goes wrong

- "did not accept the key": the key was copied wrong or billing is not turned on for it. Ask them to create a new one.
- "said no": the service refused the prompt or the account. Reword the prompt, or tell them what the message said in plain words.
- Never retry in a loop. After one failure, explain and stop.
