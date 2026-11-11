"""Check lore source fidelity, navigation, and publication reachability."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []; self.refs = []; self.sources = {}; self.current = None
        self.words = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        for key in ['href', 'src']:
            if attrs.get(key): self.refs.append(attrs[key])
        if attrs.get('data-source-ref'):
            self.current = attrs['data-source-ref']; self.text = []; self.source_tag = tag

    def handle_data(self, text):
        self.words.append(text)
        if self.current: self.text.append(text)

    def handle_endtag(self, tag):
        if self.current and tag == self.source_tag:
            self.sources[self.current] = ''.join(self.text); self.current = None


def main():
    doc = json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
    original = {b['id']: b['text'] for b in doc['blocks'] if 'text' in b}
    data = json.loads((ROOT/'iron-stars-tools/lore-content.json').read_text(encoding='utf-8'))
    paths = [ROOT/'iron-stars/universe/index.html'] + [ROOT/'iron-stars/universe'/s['id']/'index.html' for s in data['stories']]
    checked = links = 0
    for path in paths:
        html = path.read_text(encoding='utf-8'); page = Page(); page.feed(html)
        assert len(page.ids) == len(set(page.ids)), path
        assert html.count('<h1 ') == 1 and 'assets/universe.css' in html
        assert 'coming online' not in html and 'chatgpt.com' not in html
        assert '2067' not in html
        for ref, text in page.sources.items():
            assert text == original[ref], ref
            checked += 1
        for ref in page.refs:
            split = urlsplit(ref)
            if split.scheme or split.netloc: continue
            target = (path.parent/unquote(split.path)).resolve() if split.path else path
            assert target.is_file(), (path, ref)
            if split.fragment:
                parsed = Page(); parsed.feed(target.read_text(encoding='utf-8'))
                assert unquote(split.fragment) in parsed.ids, (path, ref)
            links += 1
    public = runpy.run_path(str(ROOT/'prepare-publication.py'))['collect_files']()
    assert set(paths) <= public
    assert ROOT/'iron-stars/assets/universe.css' in public
    assert not any(p.is_relative_to(ROOT/'iron-stars-tools') for p in public)
    renderer = runpy.run_path(str(ROOT/'iron-stars-tools/universe.py'))
    snapshots = json.loads((ROOT/'iron-stars-review/lore-story-snapshots.json').read_text(encoding='utf-8'))
    originals = {s['id']: s for s in snapshots['stories']}
    for story, path in zip(data['stories'], paths[1:]):
        assert story['markdown'] == originals[story['id']]['markdown'], story['id']
        assert story.get('appendices', []) == originals[story['id']]['appendices'], story['id']
        for version in [story] + story.get('appendices', []):
            rendered = renderer['fiction_html'](version['markdown'])
            assert rendered in path.read_text(encoding='utf-8'), story['id']
            assert ':chatgpt-content-reference' not in rendered
            parsed = Page(); parsed.feed(rendered)
            plain = re.sub(r'(?m)^>\s?', '', version['markdown'])
            plain = re.sub(r'(?m)^---\s*$', '', plain).replace('*', '').replace('_', '')
            assert re.sub(r'\s+', '', ''.join(parsed.words)) == re.sub(r'\s+', '', plain), story['id'] + ' narrative text lost in rendering'
    quiet = next(s for s in data['stories'] if s['id'] == 'quiet-ledger')
    assert quiet['kind'] == 'Short story'
    assert quiet['markdown'].endswith('And in the Iron Stars, it was often enough.')
    assert 'Ash never answered another comm.' in quiet['markdown']
    assert len(quiet['markdown'].split()) > 1400
    rebellion = next(s for s in data['stories'] if s['id'] == 'rebellion-combat-record')
    assert rebellion['markdown'].endswith('That was all that mattered.')
    assert len(rebellion['markdown'].split()) > 900
    peter = next(s for s in data['stories'] if s['id'] == 'unmc-peters-sortie')
    assert peter['markdown'].endswith('it was the only way through.')
    yelena = next(s for s in data['stories'] if s['id'] == 'concord-field-report')
    assert yelena['kind'] == 'Short story'
    assert yelena['markdown'].startswith('Yelena drove her scout mech through the dense forest,')
    assert yelena['markdown'].endswith('She would remember both.')
    assert 'The flyer’s head erupted in a spray of parts.' in yelena['markdown']
    mikael = next(s for s in data['stories'] if s['id'] == 'new-avalon-mikaels-first-watch')
    supplied = Path(mikael['chat']['source_file']).read_text(encoding='utf-8-sig').strip()
    assert mikael['markdown'] == supplied, 'Mikael narrative differs from author attachment'
    assert mikael['markdown'].endswith('He began to walk.')
    print(f'Universe verified: {len(paths)} pages, {checked} unchanged source passages, {links} local links; publication includes every lore page and stylesheet.')


if __name__ == '__main__':
    main()
