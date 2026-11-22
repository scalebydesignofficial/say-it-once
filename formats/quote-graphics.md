# Quote graphics

Single scroll-stopping lines as finished images.

## Where it goes
`quote-graphics/quotes.json`

## JSON shape
```json
{"quotes": [
  {"text": "The line itself."},
  {"text": "A line from the teaching.", "ref": "optional small label under the line"}
]}
```
Wrap one key phrase in `**double asterisks**` on some of them.

## Rules
- 10 by default (see `config.json`). Each is 18 words or fewer. Shorter is better.
- Each line must stand alone with no context.
- Lift the speaker's own best lines and tighten them, or compress a teaching point into one sentence in their voice. Never invent a line the teaching does not support.
- A mix: some blunt truths, some permission-giving, some challenges, a couple that are tender.
- Use `ref` only for a real reference the person gave (for example a book or verse reference they used). Otherwise leave it out.
- No hashtags, no emoji, no attribution to anyone but the owner of the material.
