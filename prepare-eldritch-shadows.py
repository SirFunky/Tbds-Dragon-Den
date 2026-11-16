"""Validate clean Eldritch Shadows routes; --package prepares an upload ZIP."""
import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import threading
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parent
SECTION = ROOT / 'eldritch-shadows'
LEGACY = ROOT / 'Eldritch shadows'
ARCHIVE = ROOT / 'uppdatering-eldritch-shadows-1.0.zip'
publication = runpy.run_path(str(ROOT / 'prepare-publication.py'))
References = publication['References']
resolve_local = publication['resolve_local']
URLS = publication['URLS']


def section_files():
    return sorted(p for p in SECTION.rglob('*') if p.is_file() and p.suffix in {
        '.html', '.css', '.js', '.svg', '.png', '.pdf', '.docx', '.json'
    })


def redirects():
    return sorted(p for p in LEGACY.rglob('*.html') if 'Old' not in p.parts)


def refresh_pdf_links():
    key = hashlib.sha256((SECTION / 'rulebook.pdf').read_bytes()).hexdigest()[:12]
    path = SECTION / 'index.html'
    text = path.read_text(encoding='utf-8')
    text, count = re.subn(r'rulebook\.pdf(?:\?v=[a-f0-9]+)?', f'rulebook.pdf?v={key}', text)
    assert count == 5, f'Expected five rulebook links, found {count}'
    path.write_text(text, encoding='utf-8')


def validate():
    files = section_files()
    for filename in ['index.html', 'contact.html']:
        entry = (ROOT / filename).read_text(encoding='utf-8')
        assert 'href="eldritch-shadows/"' in entry, filename
        assert 'EldritchShadowsPublicEnglishPdfUpdated.html' not in entry, filename
    assert (SECTION / 'rulebook.pdf').read_bytes().startswith(b'%PDF-')
    key = hashlib.sha256((SECTION / 'rulebook.pdf').read_bytes()).hexdigest()[:12]
    landing = (SECTION / 'index.html').read_text(encoding='utf-8')
    assert landing.count(f'rulebook.pdf?v={key}') == 5
    for page in files:
        if page.suffix not in {'.html', '.css', '.svg'}:
            continue
        content = page.read_text(encoding='utf-8')
        refs = References()
        if page.suffix in {'.html', '.svg'}:
            refs.feed(content)
        links = refs.links + [match[1] for match in URLS.findall(content)]
        for link in links:
            target = resolve_local(page, link)
            parsed = urlsplit(link)
            if parsed.fragment and not parsed.path:
                assert unquote(parsed.fragment) in refs.ids, (page, link)
            if target and page.suffix == '.html':
                assert not target.is_relative_to(LEGACY), (page, link)
        if page.suffix == '.html':
            assert 'EldritchShadowsPublicEnglishPdfUpdated' not in content
            assert 'Eldritch%20shadows' not in content
            canonical = 'https://tbddragonden.com/eldritch-shadows/'
            if page.name != 'index.html':
                canonical += page.relative_to(SECTION).as_posix()
            elif page.parent != SECTION:
                canonical += page.parent.relative_to(SECTION).as_posix() + '/'
            assert f'rel="canonical" href="{canonical}"' in content, page

    # Changing paths on the same origin must preserve existing browser saves.
    for filename in ['character-sheet.js', 'questionnaire.js']:
        assert (SECTION / filename).read_bytes() == (LEGACY / filename).read_bytes()
    for page in (SECTION / 'pregens').glob('*.json'):
        assert json.loads(page.read_text(encoding='utf-8')) == json.loads((LEGACY / 'pregens' / page.name).read_text(encoding='utf-8'))

    rules = re.findall(r'RedirectMatch 301 "([^"]+)" "([^"]+)"', (LEGACY / '.htaccess').read_text(encoding='utf-8'))
    js_checks = []
    for page in redirects():
        content = page.read_text(encoding='utf-8')
        assert 'location.search + location.hash' in content
        target = re.search(r'<meta http-equiv="refresh" content="0; url=([^"]+)"', content)[1]
        assert resolve_local(page, target)
        matches = [re.sub(pattern, replacement.replace('$1', r'\g<1>'), '/' + page.relative_to(ROOT).as_posix())
                   for pattern, replacement in rules if re.search(pattern, '/' + page.relative_to(ROOT).as_posix())]
        assert matches == [target], (page, matches, target)
        script = re.search(r'<script>(.*?)</script>', content, re.S)[1]
        js_checks.append({'script': script, 'expected': target + '?test=1#start-playing'})
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node.js is required to verify legacy redirect behavior.')
    check_js = '''const fs = require('fs'), vm = require('vm');
for (const test of JSON.parse(fs.readFileSync(0, 'utf8'))) {
  let result;
  vm.runInNewContext(test.script, {location: {search:'?test=1', hash:'#start-playing', replace: value => result = value}});
  if (result !== test.expected) throw Error(result);
}'''
    subprocess.run([node, '-e', check_js], input=json.dumps(js_checks), text=True, check=True)

    # Check direct navigation with a real static server, including encoded old URLs.
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)
        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        routes = {
            '/eldritch-shadows/': b'<h1 id="hero-heading">Eldritch Shadows</h1>',
            '/eldritch-shadows/questionnaire.html': b'GDA Questionnaire',
            '/eldritch-shadows/character-sheet.html': b'id="character-sheet"',
            '/eldritch-shadows/pregens/': b'Meet your next character',
            '/eldritch-shadows/rulebook.pdf?v=' + key: b'%PDF-',
            '/Eldritch%20shadows/EldritchShadowsPublicEnglishPdfUpdated.html': b'location.replace("/eldritch-shadows/"',
        }
        for route, expected in routes.items():
            with urlopen(f'http://127.0.0.1:{server.server_port}{route}', timeout=10) as response:
                assert response.status == 200 and expected in response.read(), route
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print(f'PASS: {len(files)} section files; local links, anchors, casing and canonical URLs.')
    print(f'PASS: {len(js_checks)} legacy redirects preserve query strings and anchors; 301 patterns agree.')
    print('PASS: direct HTTP routes, PDF download, unchanged character files and browser storage keys.')
    print('Server-side 301 execution requires Apache/LiteSpeed; static fallback behavior checked locally.')


def package():
    files = sorted(set(section_files() + redirects() + [LEGACY / '.htaccess'] + [ROOT / name for name in [
        'index.html', 'contact.html', 'style.css', 'site-header.css',
        'Eldritch shadows/IconDragonDenSketchEmbedded.svg', 'Eldritch shadows/IconRuneStarEmbedded.svg'
    ]]))
    for source in files:
        assert source.stat().st_size < 100 * 1024**2, source
        target = ROOT / 'publicering' / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert source.read_bytes() == target.read_bytes()
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as output:
        for source in files:
            output.write(source, source.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCHIVE) as output:
        assert output.testzip() is None
        assert len(output.namelist()) == len(files)
        for source in files:
            assert output.read(source.relative_to(ROOT).as_posix()) == source.read_bytes()
    print(f'PASS: {len(files)} publication copies and ZIP entries match sources; {ARCHIVE.stat().st_size / 1024**2:.1f} MB.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='store_true')
    args = parser.parse_args()
    if args.package:
        refresh_pdf_links()
    validate()
    if args.package:
        package()
