#!/usr/bin/env python3
"""Update Say It Once to the latest version.

Usage:
    python3 scripts/update.py check     # is there a newer version? (changes nothing)
    python3 scripts/update.py apply     # download and install the latest version

What it touches: the engine (scripts, engine, formats, design, examples, guides, CLAUDE.md).
What it never touches: brand/ (your business, voice, design, photos), outputs/, inbox/, and your
settings in config.json (new settings are added, your choices are kept). It never deletes anything.
Every file it replaces is copied first into .update-backup/<date>/ so it can be undone.

Where it looks: update.json ({"repo": "owner/name", "branch": "main"}), a public GitHub repo.
"""
import datetime
import io
import json
import pathlib
import shutil
import ssl
import subprocess
import sys
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Never overwritten or removed. config.json is merged, not replaced.
PROTECTED_TOP = {"brand", "outputs", "inbox", ".update-backup", ".git"}
MERGE_FILES = {"config.json"}


def say(msg):
    print(msg, flush=True)


def settings():
    p = ROOT / "update.json"
    if not p.exists():
        sys.exit("No update.json found. Re-download Say It Once to get updates.")
    cfg = json.loads(p.read_text(encoding="utf-8"))
    repo = cfg.get("repo", "")
    if "/" not in repo or repo.startswith("OWNER/") or " " in repo:
        sys.exit("Updates are not switched on yet (the update address is not filled in).")
    return repo, cfg.get("branch", "main")


def fetch(url, timeout=60):
    """Download a web address. Uses Python, falls back to curl if this computer's certificates fail."""
    if not url.startswith("https://"):
        sys.exit("Refusing to download from a non-secure address.")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except (ssl.SSLError, urllib.error.URLError) as first:
        curl = shutil.which("curl")
        if not curl:
            raise SystemExit(f"Could not reach the update server: {first}")
        r = subprocess.run([curl, "-fsSL", "--max-time", str(timeout), url], capture_output=True)
        if r.returncode != 0:
            raise SystemExit("Could not reach the update server. Check your internet and try again.")
        return r.stdout


def vtuple(v):
    out = []
    for part in v.strip().lstrip("v").split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def local_version():
    p = ROOT / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "0.0.0"


def latest_version(repo, branch):
    raw = fetch(f"https://raw.githubusercontent.com/{repo}/{branch}/VERSION")
    return raw.decode("utf-8").strip()


def merge_config(old, new):
    """Keep every value the person has set. Add keys that are new."""
    if isinstance(old, dict) and isinstance(new, dict):
        merged = dict(old)
        for k, v in new.items():
            merged[k] = merge_config(old[k], v) if k in old else v
        return merged
    return old


def whats_new(text, since):
    """Pull the changelog entries newer than the version the person has."""
    lines, show = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            ver = ln[3:].split()[0] if ln[3:].strip() else "0"
            show = vtuple(ver) > vtuple(since)
        if show:
            lines.append(ln)
    return "\n".join(lines).strip()


def cmd_check():
    repo, branch = settings()
    have, latest = local_version(), latest_version(repo, branch)
    if vtuple(latest) > vtuple(have):
        say(f"UPDATE AVAILABLE: you have {have}, the latest is {latest}.")
    else:
        say(f"UP TO DATE: you have {have}.")


def cmd_apply():
    repo, branch = settings()
    have = local_version()
    latest = latest_version(repo, branch)
    if vtuple(latest) <= vtuple(have):
        say(f"UP TO DATE: you already have the latest ({have}). Nothing changed.")
        return
    say(f"Downloading {latest}...")
    data = fetch(f"https://codeload.github.com/{repo}/zip/refs/heads/{branch}", timeout=180)
    z = zipfile.ZipFile(io.BytesIO(data))
    names = [n for n in z.namelist() if not n.endswith("/")]
    if not names:
        sys.exit("The download was empty. Nothing changed.")
    prefix = names[0].split("/")[0] + "/"  # GitHub wraps everything in one folder

    backup = ROOT / ".update-backup" / datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    added = replaced = same = 0
    new_config_text = None
    for n in names:
        rel = pathlib.PurePosixPath(n[len(prefix):])
        if not rel.parts or rel.parts[0].startswith(".git") or ".." in rel.parts or rel.is_absolute():
            continue  # skip repo housekeeping and anything that tries to escape this folder
        if rel.parts[0] in PROTECTED_TOP or rel.name in {".DS_Store", ".gitignore"}:
            continue
        content = z.read(n)
        dest = ROOT.joinpath(*rel.parts)
        if str(rel) in MERGE_FILES:
            new_config_text = content
            continue
        if dest.exists():
            if dest.read_bytes() == content:
                same += 1
                continue
            bk = backup.joinpath(*rel.parts)
            bk.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, bk)
            replaced += 1
        else:
            added += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)

    # Settings: keep their choices, add anything new.
    if new_config_text is not None:
        cfg_path = ROOT / "config.json"
        new_cfg = json.loads(new_config_text.decode("utf-8"))
        if cfg_path.exists():
            old_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            merged = merge_config(old_cfg, new_cfg)
            if merged != old_cfg:
                backup.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cfg_path, backup / "config.json")
                cfg_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
                say("Added new settings to config.json (your choices were kept).")
        else:
            cfg_path.write_text(json.dumps(new_cfg, indent=2) + "\n", encoding="utf-8")

    # The Design Studio page has the person's design baked in, so rebuild it.
    try:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "studio.py")], cwd=ROOT, capture_output=True, timeout=120)
    except Exception:
        pass

    say(f"UPDATED: {have} -> {latest}. {replaced} file(s) improved, {added} new, your brand, outputs, inbox and settings untouched.")
    if backup.exists():
        say(f"Old versions of the replaced files are saved in {backup.relative_to(ROOT)}.")
    cl = ROOT / "CHANGELOG.md"
    if cl.exists():
        news = whats_new(cl.read_text(encoding="utf-8"), have)
        if news:
            say("\nWHAT'S NEW\n" + news)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("check", "apply"):
        sys.exit(__doc__)
    {"check": cmd_check, "apply": cmd_apply}[sys.argv[1]]()


if __name__ == "__main__":
    main()
