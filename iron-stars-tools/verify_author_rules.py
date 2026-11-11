"""Verify author additions without rewriting or attributing them to the DOCX."""
import json
from pathlib import Path
from html.parser import HTMLParser
from rulebook import selected_data, glossary_terms, anchor
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'iron-stars/data/rulebook.json').read_text(encoding='utf-8'))
assert data==selected_data()
source=json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
originals={b['id']:b for b in source['blocks']}
for chapter in data['chapters']:
    for block in chapter['blocks']:assert block==originals[block['id']]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.author=[];self.search=[];self.text=[]
    def handle_data(self,text):self.text.append(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a and a['href'].startswith('#'):self.links.append(a['href'][1:])
        if 'data-author-source' in a:self.author.append(a['data-author-source'])
        if 'data-search-entry' in a:self.search.append(a.get('id'))
page=Page();text=(ROOT/'iron-stars/rules/index.html').read_text(encoding='utf-8');page.feed(text)
assert len(page.ids)==len(set(page.ids));assert set(page.links)<=set(page.ids)
for rule in data['author_additions']:
    assert rule['status']=='approved' and rule['source_ref'].startswith('user:')
    assert rule['after'] in originals
    assert anchor(rule['id']) in page.search
    assert glossary_terms(data)[rule['name']]==anchor(rule['id'])
    assert rule['source_ref'] in page.author
    assert all(effect in ''.join(page.text) for effect in rule['effects'])
print('PASS: approved author effects, separate author provenance, unchanged source blocks, generated data, search entries, keyword index, unique IDs and direct anchors.')
