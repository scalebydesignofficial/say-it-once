# Setup interview

Goal: learn the person well enough that every piece sounds like them and points to their offer. You write these files:

- `brand/profile.md` who they are, who they serve, where they post
- `brand/voice.md` how they sound
- `brand/offer.md` the next steps they send people to
- `config.json` (only the parts that change: `cadence`, `formats`, `rules`)

Tone: like a friendly creative director on a first call. Short. One or two questions at a time. Use AskUserQuestion for multiple choice. Let them answer by voice-note style rambling. You do the organizing.

If they already pasted material, offer to learn their voice from it so they do not have to write samples.

## Step 1. About them and their people

Ask:
- What is your name and your business or brand name?
- In one sentence, what do you sell or teach?
- Who is it for? Describe her or him or them like a real person.
- What is the one problem they are stuck on that you solve?

## Step 2. Where they show up

Ask (multiple choice, pick all that apply): Instagram, Facebook, TikTok, Threads, Substack, YouTube Shorts, Blog, Email list.

Then ask: how many days a week do you want to post, and how much time can you give to recording or posting?

Also ask: do you have photos you like using (of you, your space, your products, mood images), or would you like help getting photos? Note the answer in `brand/profile.md`. If they have photos, tell them to drop them in `brand/photos/`. If they want help, mention that for each carousel the engine can write image prompts for an AI image tool, or they can use stock photos from a site whose license allows it. Never download or fetch images for them from the web.

Turn this into `config.json`:
- `formats`: turn off formats for platforms they do not use. Instagram posts and stories need Instagram. Facebook posts need Facebook. Talking points are always useful, so keep them on. Carousels and quote graphics need Instagram or Facebook. Reels and short videos need Instagram, TikTok, or YouTube Shorts. Threads need Threads. Notes and articles need Substack. Blog needs a blog. Emails need an email list.
- `cadence.post_days`: Monday is 0 and Sunday is 6. Match their answer. Default is Monday to Saturday.
- If they have very little time, lower `counts` and the posts per day.

## Step 3. Their voice

Ask these, a couple at a time:
1. Give me three words for how you sound.
2. What do you say all the time? Phrases, little sayings, how you greet people.
3. What would you never say? Words, topics, a tone that is not you.
4. Paste three to five things you wrote or said that sound most like you. A caption, an email, a voice-note transcript. Or I can learn from the material you are about to give me.
5. Any creators whose energy you love? (Energy only. I will never copy anyone.)

If they give samples, study them: sentence length, how they open, how they end, humor, slang, how direct they are, what they do when they teach, how they talk about their audience. Quote only their real lines.

Write `brand/voice.md` with: summary in two sentences, how they open and close, words and phrases they use (only real ones), words and tones they never use, rhythm, how they teach, how they talk to the reader, and dials by platform.

Save their best samples into `brand/voice-samples.md`.

Then show them a short summary and three sample lines, and ask: "Does this sound like you?" Adjust once or twice. Do not move on until they say yes.

## Step 4. Next steps for their audience

Ask:
- When someone loves a post, what do you want them to do next? (Join a list, buy, book a call, join a community, comment a keyword, visit a link.)
- Do you have a keyword you use for comment-to-get-a-link? (If not, offer to pick one later.)
- Links: where should I send people?
- Is there something you are pushing right now? A launch, a challenge, an offer?
- Can I mention prices in content, or never?

Write `brand/offer.md`.

## Step 5. Writing rules

Say in one sentence: "By default I skip em dashes, AI-sounding words, and stiff transitions, and I write in American English. Want any of that changed?" Update `config.json` `rules` if they want changes (for example `american_spelling` false, `ban_em_dash` false, extra words in `ban_words`).

If they teach scripture or quote the Bible, turn on `rules.check_scripture`.

## Step 6. Finish

1. Write the files. Keep `brand/profile.md` free of the "(not set up yet)" marker once it is filled in. Same for the other two.
2. Run `python3 scripts/doctor.py`.
3. Say: "You are set up. Next I am going to show you design options for your carousels and graphics." Then follow `engine/02-design-studio.md`.

Never write down anything sensitive that is not needed to make content (no passwords, ID numbers, or payment details). If they offer, say you do not need it.
