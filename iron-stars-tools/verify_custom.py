"""Check custom parts against published armory data and literal source evidence."""
import json
import re
from pathlib import Path
from urllib.parse import unquote,urlsplit
from custom_data import custom_catalog,interval
from verify_units import Page

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'iron-stars/data/army-builder.json').read_text(encoding='utf-8'))
assert data['custom']==custom_catalog(), 'Construction data is stale'
armory={p['id']:p for p in json.loads((ROOT/'iron-stars/data/armory.json').read_text(encoding='utf-8'))['components']}
sources={}
for path in (ROOT/'iron-stars-source/extracted').glob('*.json'):
    for block in json.loads(path.read_text(encoding='utf-8'))['blocks']:
        sources[block['id']]=block.get('text','')
        for row in block.get('rows',[]):
            sources[row['id']]=' | '.join(c['text'] for c in row['cells'])
            sources.update((c['id'],c['text']) for c in row['cells'])
armory_page=Page();armory_page.feed((ROOT/'iron-stars/armory/index.html').read_text(encoding='utf-8'))
for rule in data['custom']['transform_rules']:assert rule['text'].strip()==sources[rule['source_ref']].strip()
flyer=data['custom']['flyer_rule'];assert flyer['text']==sources[flyer['source_ref']]
for name in ('linked_rule','jetpack_rule'):
    rule=data['custom'][name];assert rule['text']==sources[rule['source_ref']]
policy=data['custom']['transform_policy']['factions']['unmc']
base_move=int(sources['unmc:b0066:r4:c2'].split()[0]);base_def=int(sources['unmc:b0066:r4:c3'][0])
assert policy['movement_offsets']==[0,int(sources['unmc:b0066:r3:c2'].split()[0])-base_move,int(sources['unmc:b0066:r2:c2'].split()[0])-base_move]
assert policy['defence_offsets']==[0,int(sources['unmc:b0066:r3:c3'][0])-base_def,int(sources['unmc:b0066:r2:c3'][0])-base_def]
for movement in data['custom']['movement_types']:
    for rule in movement['rules']:
        if rule['source_ref'].startswith('core:'):assert rule['text']==sources[rule['source_ref']]
        else:
            approved=json.loads((ROOT/'iron-stars-tools/approved-rules.json').read_text(encoding='utf-8'))['rules']
            original=next(r for r in approved if r['source_ref']==rule['source_ref'] and r['status']=='approved')
            assert rule['text']=='\n'.join(original['effects'])
for part in data['custom']['parts']:
    origin=armory[part['armory_id']]
    assert part['price']==origin['price'] and part['price'] is not None
    assert part['source_ref']==origin['source_ref'] and part['source_sha256']==origin['source_sha256']
    assert part['armory_id'] in armory_page.ids
    for detail in part['details']+part.get('help_keywords',[])+part.get('help_rules',[]):
        assert detail['text'] in sources[detail['source_ref']], (part['name'],detail)
    if part['kind']=='chassis':
        if 'mech_defence' in part:assert part['mech_defence']==sources[part['mech_defence_ref']]
        fields={d['label'].casefold():d['text'] for d in part['details']}
        assert part['movement']==interval(fields.get('move',fields.get('m','')))
        assert part['structure']==interval(fields.get('structure',fields.get('str','')))
assert any(p['name']=='Linewalker' and p['movement']==[12.5,12.5] for p in data['custom']['parts'])
assert not any(p['name']=='Sponsor Protocol' for p in data['custom']['parts'])
laser=next(p for p in data['custom']['parts'] if p['name']=='Medium Laser' and p['source_id']=='core')
assert laser['fp']==3
assert not any(d['label']=='Stock weapon profile' for d in laser['details']), 'Do not append superseded stock stats to a core profile'
page=ROOT/'iron-stars/army-builder/index.html';text=page.read_text(encoding='utf-8')
assert json.loads(re.search(r'<script type="application/json" id="army-data">(.*?)</script>',text,re.S)[1])==data
parsed=Page();parsed.feed(text)
assert len(parsed.ids)==len(set(parsed.ids))
assert {'custom-transform','custom-forms','custom-transform-rules','custom-flyer'}<=set(parsed.ids), 'Transform form UI is missing from generated page'
for url in parsed.links:
    split=urlsplit(url)
    if split.scheme or split.netloc:continue
    target=(page.parent/unquote(split.path)).resolve() if split.path else page
    assert target.is_file(),url
    if split.fragment:
        dest=Page();dest.feed(target.read_text(encoding='utf-8'));assert unquote(split.fragment) in dest.ids,url
print(f'PASS: {len(data["custom"]["parts"])} custom parts; current prices, exact source details, chassis values, stable data, Armory anchors, builder links and assets.')
