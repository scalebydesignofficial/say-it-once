#!/usr/bin/env python3
"""Turn a source file into plain text the engine can read.

Usage:
    python3 scripts/extract_text.py <file> [out.txt]

Handles .txt .md (copied as is), .docx, .srt and .vtt (caption files), .html, and
.pdf (needs the free pdftotext tool; if missing, the engine reads the PDF directly).
Writes to inbox/_text/<name>.txt unless you give an output path.
"""
import html.parser
import pathlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
for _s in (sys.stdout, sys.stderr):  # Windows consoles can choke on curly quotes and emoji; never crash on printing
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent


def docx_text(path):
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = []
    for p in root.iter(ns + "p"):
        paras.append("".join(t.text or "" for t in p.iter(ns + "t")))
    return "\n\n".join(x for x in paras if x.strip())


def caption_text(path):
    lines, last = [], None
    for raw in pathlib.Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.upper().startswith("WEBVTT") or re.fullmatch(r"\d+", s) or "-->" in s or s.startswith(("NOTE", "Kind:", "Language:")):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        if s and s != last:
            lines.append(s)
            last = s
    return " ".join(lines)


class _Strip(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "br", "div", "h1", "h2", "h3", "li"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_text(path):
    p = _Strip()
    p.feed(pathlib.Path(path).read_text(encoding="utf-8", errors="replace"))
    return re.sub(r"\n{3,}", "\n\n", "".join(p.out)).strip()


def pdf_text(path):
    exe = shutil.which("pdftotext")
    if not exe:
        sys.exit("pdftotext is not installed. The engine can read this PDF directly instead. Just point it at the file.")
    return subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    src = pathlib.Path(sys.argv[1])
    if not src.is_file():
        sys.exit(f"Not found: {src}")
    ext = src.suffix.lower()
    if ext in (".txt", ".md"):
        text = src.read_text(encoding="utf-8", errors="replace")
    elif ext == ".docx":
        text = docx_text(src)
    elif ext in (".srt", ".vtt"):
        text = caption_text(src)
    elif ext in (".html", ".htm"):
        text = html_text(src)
    elif ext == ".pdf":
        text = pdf_text(src)
    else:
        sys.exit(f"Unsupported file type: {ext}. Paste the text into the chat or save it as .txt")
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) == 3 else ROOT / "inbox" / "_text" / (src.stem + ".txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{len(text.split())} words -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
