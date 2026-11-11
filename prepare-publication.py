"""Copy the site's reachable pages, assets and downloads into publicering/.

Does not publish anything online. Existing output must be empty to avoid
shipping stale files; source files and archives are never removed.
"""
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "publicering"
URLS = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("href", "src", "xlink:href", "poster"):
            if attrs.get(attr):
                self.links.append(attrs[attr])

def resolve_local(source, url):
    parsed = urlsplit(url.strip())
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    raw = unquote(parsed.path)
    path = ((ROOT if raw.startswith("/") else source.parent) / raw.lstrip("/")).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Reference outside the website: {source}: {url}")
    if path.is_dir():
        path /= "index.html"
    if not path.is_file():
        raise FileNotFoundError(f"Missing reference: {source.relative_to(ROOT)} -> {url}")
    # Windows ignores case; the hosting filesystem may not.
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        if part not in {entry.name for entry in current.iterdir()}:
            raise ValueError(f"Case mismatch: {source.relative_to(ROOT)} -> {url}")
        current /= part
    if parsed.fragment and path.suffix.lower() == ".html":
        target = References()
        target.feed(path.read_text(encoding="utf-8"))
        if unquote(parsed.fragment) not in target.ids:
            raise ValueError(f"Missing section: {source.relative_to(ROOT)} -> {url}")
    return path

def collect_files():
    pending = deque([ROOT / "index.html"])
    found = set()
    while pending:
        path = pending.popleft()
        if path in found:
            continue
        found.add(path)
        if path.suffix.lower() not in {".html", ".css", ".svg"}:
            continue
        content = path.read_text(encoding="utf-8")
        refs = []
        if path.suffix.lower() in {".html", ".svg"}:
            parser = References()
            parser.feed(content)
            refs.extend(parser.links)
        refs.extend(match[1] for match in URLS.findall(content))
        for url in refs:
            target = resolve_local(path, url)
            if target:
                pending.append(target)
    return found

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.digest()

if __name__ == "__main__":
    files = collect_files()
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise RuntimeError("publicering/ is not empty. Archive or empty that output folder before rebuilding.")
    OUTPUT.mkdir(exist_ok=True)
    for source in sorted(files):
        target = OUTPUT / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert digest(source) == digest(target), target
    size = sum(p.stat().st_size for p in files)
    print(f"Prepared {len(files)} files in {OUTPUT}; {size / 1024**2:.1f} MB.")
    print("All local paths and filename casing checked. Every copied file matches its source, including the full rule PDF.")
