"""Validate armory pricing, provenance, and public links."""
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from verify_units import Page
from pricing import Prices, key, base_name

root=Path(__file__).resolve().parents[1]
page=root/'iron-stars/armory/index.html'
r=json.loads((root/'iron-stars/data/armory.json').read_text(encoding='utf-8'))['components']
prices=Prices()
cache={}
def parse(path):
    if path not in cache:
        p=Page();p.feed(path.read_text(encoding='utf-8'));cache[path]=p
    return cache[path]
assert len({x['id'] for x in r})==len(r)
for x in r:
    definition=prices.find(x['source_id'],x['kind'],base_name(x['name']),x['variant'])
    assert x['price']==(definition['unit_price'] if definition else None),x['name']
    assert x['source_sha256']==prices.docs[x['source_id']]['sha256']
    assert x['source_ref'].split(':r')[0] in prices.blocks
    for d in x['details']:
        block=prices.blocks[d['source_ref'].split(':r')[0]]
        text=block.get('text','') if ':r' not in d['source_ref'] else next(c['text'] for row in block['rows'] for c in row['cells'] if c['id']==d['source_ref'])
        assert d['text'] in text,(x['name'],d)
for url in parse(page).links:
    s=urlsplit(url)
    if s.scheme or s.netloc:continue
    target=(page.parent/unquote(s.path)).resolve() if s.path else page
    assert target.is_file(),url
    if s.fragment:assert unquote(s.fragment) in parse(target).ids,url
assert not any(x['name']=='Sponsor Protocol' for x in r)
assert [x['price'] for x in r if x['name']=='Overdrive']==[2]
assert all(x['price'] is None for x in r if x['name']=='Singularity Pulse')
assert len([x for x in r if x['name']=='Command Uplink Node (new)'])==1
assert next(x for x in r if x['name']=='Iron Will')['details'][0]['source_ref']=='core:b0335'
print(f'PASS: {len(r)} armory components; exact source details, current prices, unknown costs, unique entries, file links and anchors.')
