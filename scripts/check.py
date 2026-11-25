#!/usr/bin/env python3
"""Quality check for a finished pack: writing rules plus structure.

Usage:
    python3 scripts/check.py <folder-or-file>

Reads the rules in config.json ("rules"). Skips files that start with "00-".
Prints every problem with a file name and line, a summary, and (if turned on)
a list of scripture references to verify. Exit code 1 if any ERROR is found.
"""
import json
import pathlib
import re
import sys
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
EM, EN, SPARKLE = "—", "–", "✨"
ERR, WARN = "ERROR", "WARN"

BOOKS = (
    "Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|1 Samuel|2 Samuel|1 Kings|2 Kings|"
    "1 Chronicles|2 Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|"
    "Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|"
    "Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|1 Corinthians|2 Corinthians|Galatians|"
    "Ephesians|Philippians|Colossians|1 Thessalonians|2 Thessalonians|1 Timothy|2 Timothy|Titus|Philemon|"
    "Hebrews|James|1 Peter|2 Peter|1 John|2 John|3 John|Jude|Revelation"
)
SCRIPTURE = re.compile(r"\b(" + BOOKS + r")\s+(\d{1,3})(?::(\d{1,3})(?:[-" + EN + r"](\d{1,3}))?)?")

AI_WORDS = re.compile(
    r"\b(delve|tapestry|testament|pivotal|crucial|robust|foster|garner|showcase|underscore|meticulous|"
    r"intricate|vibrant|navigate|realm|elevate|seamless|leverage)\b", re.I)
AI_PHRASES = re.compile(r"\b(in today'?s|dive (in|into)|let'?s dive|in the world of|it'?s important to note)\b", re.I)
FORMAL = re.compile(r"\b(moreover|furthermore|additionally|consequently|in conclusion|in summary|thus)\b", re.I)
CHATBOT = re.compile(r"(I hope this helps|let me know if|certainly!|would you like me|as an AI)", re.I)
CONTRAST = [
    re.compile(r"\bnot (just|only|merely)\b", re.I),
    re.compile(r"\b(it'?s|this is|that'?s|this isn'?t|it isn'?t) not (about|a|an|just)\b[^.!?\n]{0,80}[,;.]\s*(it'?s|this is|that'?s|but)\b", re.I),
]
BRITISH = re.compile(r"\b(colour|favour|honour|neighbour|behaviour|realise|organise|centre|recognise|prioritise|apologise)\w*\b", re.I)
PLACEHOLDER = re.compile(r"\[(KEYWORD|LINK|TODO|INSERT|PLACEHOLDER)[^\]]*\]|\{\{[^}]*\}\}", re.I)

TEXT_KEYS = {"headline", "body", "kicker", "sub", "items", "text", "attribution", "ref", "cta", "caption", "number", "label", "left", "right", "left_label", "right_label"}


def load_rules():
    try:
        return json.loads((ROOT / "config.json").read_text(encoding="utf-8")).get("rules", {})
    except (OSError, ValueError):
        return {}


def strings_in_json(data, path=""):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in TEXT_KEYS or isinstance(v, (dict, list)):
                yield from strings_in_json(v, f"{path}.{k}" if path else k)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            yield from strings_in_json(v, f"{path}[{i}]")
    elif isinstance(data, str):
        yield path, data


def words(s):
    return len(re.findall(r"\S+", s))


def collect(target):
    t = pathlib.Path(target)
    if t.is_file():
        return [t]
    out = []
    for p in sorted(t.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".txt", ".json") and not p.name.startswith("00-") \
                and "_html" not in p.parts and p.name not in ("plan.json",) and ".before-edit" not in p.name and not p.name.startswith("content-calendar"):
            out.append(p)
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    rules = load_rules()
    files = collect(sys.argv[1])
    if not files:
        print("No files to check.")
        return 0

    banned = [w for w in rules.get("ban_words", []) if w]
    banned_rx = re.compile(r"\b(" + "|".join(re.escape(w) for w in banned) + r")(s|ed|ing)?\b", re.I) if banned else None
    errors = warns = 0
    scripture = {}

    def report(level, name, where, label, text):
        nonlocal errors, warns
        if level == ERR:
            errors += 1
        else:
            warns += 1
        snip = text.strip().replace("\n", " ")
        snip = snip[:84] + "..." if len(snip) > 87 else snip
        print(f"{level:5} {name}:{where}  {label}  |  {snip}")

    def scan(name, where, text):
        if rules.get("ban_em_dash", True) and EM in text:
            report(ERR, name, where, "em dash", text)
        if re.search(r"\s" + EN + r"\s", text):
            report(ERR, name, where, "spaced en dash used like a dash", text)
        if rules.get("ban_sparkle", True) and SPARKLE in text:
            report(ERR, name, where, "sparkle emoji", text)
        if banned_rx and banned_rx.search(text):
            report(ERR, name, where, f"banned word: {banned_rx.search(text).group(0)}", text)
        if rules.get("ban_formal_transitions", True) and FORMAL.search(text):
            report(ERR, name, where, f"formal transition: {FORMAL.search(text).group(0)}", text)
        if CHATBOT.search(text):
            report(ERR, name, where, "chatbot leftover", text)
        if PLACEHOLDER.search(text):
            report(ERR, name, where, "unfilled placeholder", text)
        if rules.get("warn_contrast_framing", True) and any(rx.search(text) for rx in CONTRAST):
            report(WARN, name, where, "contrast framing", text)
        if rules.get("warn_ai_words", True) and (AI_WORDS.search(text) or AI_PHRASES.search(text)):
            report(WARN, name, where, "AI-sounding wording", text)
        if rules.get("american_spelling", True) and BRITISH.search(text):
            report(WARN, name, where, "British spelling", text)
        if rules.get("check_scripture", False):
            for m in SCRIPTURE.finditer(text):
                scripture.setdefault(m.group(0).strip(), set()).add(name)

    for f in files:
        name = f"{f.parent.name}/{f.name}" if f.parent.name not in ("outputs",) else f.name
        if f.suffix == ".json":
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                report(ERR, name, "-", "invalid JSON", "")
                continue
            for path, s in strings_in_json(data):
                scan(name, path, s)
            slides = data.get("slides")
            if isinstance(slides, list):
                if not 5 <= len(slides) <= 12:
                    report(WARN, name, "slides", f"{len(slides)} slides (aim for 6 to 10)", "")
                if slides and slides[0].get("type") != "cover":
                    report(WARN, name, "slides[0]", "first slide is not a cover", "")
                if slides and slides[-1].get("type") != "close":
                    report(WARN, name, f"slides[{len(slides) - 1}]", "last slide is not a close with a next step", "")
                for i, s in enumerate(slides):
                    if s.get("type") == "cover" and words(s.get("headline", "")) > 14:
                        report(WARN, name, f"slides[{i}]", "cover headline over 14 words", s.get("headline", ""))
                    if words(s.get("body", "")) > 45:
                        report(WARN, name, f"slides[{i}]", "body over 45 words", s.get("body", ""))
                    for it in s.get("items", []) or []:
                        if words(it) > 14:
                            report(WARN, name, f"slides[{i}]", "list item over 14 words", it)
                    if len(s.get("items", []) or []) > 6:
                        report(WARN, name, f"slides[{i}]", "more than 6 list items", "")
                if not data.get("caption"):
                    report(WARN, name, "caption", "carousel has no caption", "")
            quotes = data.get("quotes")
            if isinstance(quotes, list):
                for i, q in enumerate(quotes):
                    text = q if isinstance(q, str) else q.get("text", "")
                    if words(text) > 18:
                        report(WARN, name, f"quotes[{i}]", "quote over 18 words", text)
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            scan(name, n, line)
            if re.match(r"^\s*\d+/\s", line) and len(line) > 500:
                report(WARN, name, n, "thread post over 500 characters", line)
            m = re.match(r"^\*\*Subject:\*\*\s*(.+)", line)
            if m and len(m.group(1)) > 60:
                report(WARN, name, n, "subject line over 60 characters", line)

    print(f"\n{errors} error(s), {warns} warning(s)")
    if scripture:
        print("\nSCRIPTURE TO VERIFY (check against your translation)")
        for ref in sorted(scripture):
            print(f"  {ref}  ({', '.join(sorted(scripture[ref]))})")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
