"""Regression checks for complete, source-backed premade print references."""
import json
from pathlib import Path
from pricing import key,base_name

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'iron-stars/data/army-builder.json').read_text(encoding='utf-8'))
units={u['id']:u for u in json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))['units']}
source={}
for path in (ROOT/'iron-stars-source/extracted').glob('*.json'):
    for block in json.loads(path.read_text(encoding='utf-8'))['blocks']:
        source[block['id']]=block.get('text','')
        for row in block.get('rows',[]):
            source[row['id']]=' | '.join(c['text'] for c in row['cells'])
            source.update((c['id'],c['text']) for c in row['cells'])
for unit in data['units']:
    ref=unit['reference'];original=units[unit['id']]
    quick=ref['quick_rules']
    assert sum(w['quantity'] for w in ref['battle_weapons'])==sum(c['quantity'] for c in original['points']['calculation']['components'] if c['kind']=='weapon' and c.get('included',True))
    assert all(set(w['source_refs'])<=set(source) for w in ref['battle_weapons'])
    assert all(r['source_refs'] and set(r['source_refs'])<=set(source) for r in quick)
    weapon_names={key(base_name(r['name'])) for r in quick if r['category']=='Weapons'}
    for component in original['points']['calculation']['components']:
        if component['kind']=='weapon' and component.get('included',True):assert key(base_name(component['name'])) in weapon_names,(unit['name'],component['name'])
    assert ref['profiles']==original['profiles']
    assert ref['chassis']==original['chassis']
    assert len(ref['weapons'])==len(original['weapons'])
    assert ref['mode_rules']==original['mode_rules']
    assert ref['special_rules']==original['special_rules']
    assert len(ref['spawned_units'])==len(original['spawned_units'])
    for weapon in ref['weapons']:
        for field in weapon['fields']:assert field['source_ref'] in source
    for system in ref['systems']:
        for rule in system['rules']:assert rule['text'] in source[rule['source_ref']],(unit['name'],system)
    for child in ref['spawned_units']:
        for rule in child['rules']:assert rule['text']==source[rule['source_ref']]
byid={u['id']:u['reference'] for u in data['units']}
trooper=byid['iron-concord-ironsworn-trooper']
assert [trooper['profiles'][0]['fields'][k]['text'] for k in ['movement','defence','structure']]==['15 cm','3+','2']
assert 'Scrap Rifle' in trooper['weapons'][0]['fields'][0]['text']
assert 'Iron Maul' in trooper['weapons'][1]['fields'][0]['text']
assert trooper['systems'][0]['name']=='Discipline Drills'
mortar=byid['iron-concord-auxilia-mortar-team']
assert not any(s['name']=='March of Steel' for s in mortar['systems']), 'Unselected upgrade must not print as installed'
commander=byid['iron-concord-line-commander-legate-frame']
assert any(r['source_ref']=='core:b0352' for s in commander['systems'] if s['name']=='Command Network' for r in s['rules'])
forge=byid['cybernetic-rebellion-bastion-class-fabricator-transformable-drone-forge']
assert len(forge['profiles'])==2 and len(forge['spawned_units'])==3
assert not byid['unmc-undf-vulture-stryker']['profiles'], 'Do not invent unspecified core-example stats'
print('PASS: 26 premade print references; profiles, weapons, current system rules, forms, spawned units, and optional-upgrade exclusion.')
