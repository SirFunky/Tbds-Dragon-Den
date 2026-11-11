"""Ensure every affiliation, trait, and shared rule retains exact core evidence."""
import json
from pathlib import Path
from subfactions import affiliations

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'iron-stars/data/army-builder.json').read_text(encoding='utf-8'))
core=json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
blocks={b['id']:b.get('text','').strip() for b in core['blocks']}
expected=affiliations()
count=0
for faction in data['factions']:
    for key in ('affiliation_label','subfactions','shared_traits','affiliation_note'):
        assert faction[key]==expected[faction['id']][key]
    assert len({s['id'] for s in faction['subfactions']})==len(faction['subfactions'])
    for sub in faction['subfactions']:
        assert sub['name']==blocks[sub['source_ref']]
        for rule in sub['description']+([sub['trait']] if sub['trait'] else []):
            assert rule['text']==blocks[rule['source_ref']]
        count+=1
    for rule in faction['shared_traits']:
        if 'source_ref' in rule:assert rule['text']==blocks[rule['source_ref']]
        else:assert rule['text']=='\n'.join(blocks[ref] for ref in rule['source_refs'] if blocks[ref])
assert count==24
print('PASS: 24 affiliation names and all trait/shared-rule text match core v0.0.14 exactly; no invented Southern Cross subfactions or Living Dominion Host bonuses.')
