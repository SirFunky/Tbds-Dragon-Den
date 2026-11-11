"""Check faction source fidelity, anchors, packaging, and file-based navigation."""
from html.parser import HTMLParser
import json
from pathlib import Path
import runpy
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.refs=[]; self.source_text={}; self.current=None; self.text=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for attr in ['href','src']:
            if attrs.get(attr):self.refs.append(attrs[attr])
        if attrs.get('data-source-ref'):
            assert self.current is None
            self.current=attrs['data-source-ref']; self.source_tag=tag; self.text=[]
        if tag=='br' and self.current:self.text.append('\n')
    def handle_data(self,text):
        if self.current:self.text.append(text)
    def handle_endtag(self,tag):
        if self.current and tag == self.source_tag:
            self.source_text[self.current]=''.join(self.text); self.current=None

def main():
    data=json.loads((ROOT/'iron-stars/data/factions.json').read_text(encoding='utf-8'))
    assert {f['id'] for f in data['factions']}=={'iron-concord','unmc','cybernetic-rebellion','new-avalon','fourth-imperium','living-dominion','southern-cross-compact'}
    assert not data['finalized'] and all(not f['finalized'] for f in data['factions'])
    original={}
    for path in (ROOT/'iron-stars-source/extracted').glob('*.json'):
        for block in json.loads(path.read_text(encoding='utf-8'))['blocks']:
            original[block['id']]=block
            for row in block.get('rows',[]):original[row['id']]=row
    checked=links=rosters=0
    for f in data['factions']:
        page=ROOT/'iron-stars/factions'/f['id']/'index.html'
        parsed=Page();parsed.feed(page.read_text(encoding='utf-8'))
        assert len(parsed.ids)==len(set(parsed.ids)),f['id']+' duplicate anchor'
        assert {'overview','philosophy','doctrine','playstyle','subfactions','faction-rules','roster'}<=set(parsed.ids)
        selected=[f['quote'],f['playstyle']]+f['rules']
        for group in f['sections'].values():selected.extend(group)
        for supplement in f['supplements']:selected.extend(supplement['blocks'])
        for block in selected:
            assert block==original[block['id']]
            if block['kind']=='paragraph' and block.get('text','').strip():
                assert parsed.source_text[block['id']]==block['text'],'Wording changed: '+block['id']
                checked+=1
        for extra in f['additional_rule_rows']:assert extra['row']==original[extra['row']['id']]
        for unit in f['roster']:
            assert unit['source_ref'] in original
            rosters+=1
        for url in parsed.refs:
            split=urlsplit(url)
            if split.scheme or split.netloc:continue
            target=(page.parent/unquote(split.path)).resolve() if split.path else page
            assert target.is_file(),(page,url)
            if split.fragment:
                dest=Page();dest.feed(target.read_text(encoding='utf-8'))
                assert unquote(split.fragment) in dest.ids,(page,url)
            links+=1
    public=runpy.run_path(str(ROOT/'prepare-publication.py'))['collect_files']()
    assert ROOT/'iron-stars/data/factions.json' in public
    assert not any(p.is_relative_to(ROOT/'iron-stars-source') or p.is_relative_to(ROOT/'iron-stars-review') for p in public)
    print(f'PASS: 7 factions, {checked} exact source paragraphs/headings, {rosters} roster references, {links} file links/assets, unique IDs and valid anchors.')
    print(f'PASS: {len(public)} reachable public files; faction data included, private sources excluded.')

if __name__=='__main__':main()
