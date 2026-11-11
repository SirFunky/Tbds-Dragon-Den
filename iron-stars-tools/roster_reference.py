"""Self-contained premade roster references; never infer unspecified stats."""
import json
import re
from pathlib import Path
from pricing import base_name,key
from units import display_weapon_text

ROOT=Path(__file__).resolve().parents[1]

def references(units,parts):
    core=json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
    blocks={b['id']:b for doc in (json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')) for b in doc['blocks']}
    def source_rule(name,component,fallback):
        normalized=base_name(name)
        trait=next((b for b in core['blocks'] if re.match(r'Trait:\s*'+re.escape(normalized)+r'\s*[–—:]',b.get('text',''),re.I)),None)
        if trait:return [{'text':trait['text'],'source_ref':trait['id']}]
        part=next((p for p in parts if component and p['source_ref']==component.get('price_source_ref')),None)
        if part:
            rules=[{'text':d['text'],'source_ref':d['source_ref']} for d in part.get('help_rules',[])]
            if not rules:rules=[{'text':d['text'],'source_ref':d['source_ref']} for d in part['details'] if d['label'].lower() in ('description','effect','notes')]
            if rules:return rules
        return [fallback]
    result={}
    glossary=next(b for b in core['blocks'] if b['id']=='core:b0232')['rows'][1:]
    linked=next(r for r in glossary if r['cells'][0]['text']=='Linked')['cells'][1]
    movement_map={}
    for table in ('core:b0084','core:b0235'):
        for row in blocks[table]['rows'][1:]:
            if row['cells'][0]['text'] in ('Walker','Hover','Jetpack','Burrower','Flyer','Tracked','Stable Platform'):
                movement_map[row['cells'][0]['text']]=row['cells'][1]
    movement=list(movement_map.items())
    for unit in units:
        components=unit['points']['calculation']['components']
        systems=[];seen=set()
        for system in unit['systems']:
            name=base_name(system['name'])
            component=next((c for c in components if c['kind']=='system' and key(base_name(c['name']))==key(name)),None)
            if component and not component.get('included',True):continue
            seen.add(key(name))
            systems.append({'name':name,'rules':source_rule(name,component,{'text':system['description'],'source_ref':system['source_ref']}),
                'source_faction_bonus':bool('subfaction' in system['description'].lower() or component and component.get('basis')=='explicit-grant' and 'subfaction' in blocks.get(component.get('grant_ref'),{}).get('text','').lower())})
        for component in components:
            if component['kind']!='system' or not component.get('included',True) or key(base_name(component['name'])) in seen:continue
            fallback={'text':blocks.get(component['source_ref'],{}).get('text',component['name']),'source_ref':component['source_ref']}
            is_bonus=component.get('basis')=='explicit-grant' and 'subfaction' in blocks.get(component.get('grant_ref'),{}).get('text','').lower()
            systems.append({'name':component['name'],'rules':source_rule(component['name'],component,fallback),'source_faction_bonus':bool(is_bonus)})
        weapons=[]
        for weapon in unit['weapons']:
            if weapon['kind']=='text':
                text=weapon['text']
                # Core examples place actual stats in parentheses, which must
                # stay intact; older parenthetical keyword paraphrases do not.
                if re.search(r'\((?:FP|ME)\s*\d',text):text=re.sub(r':\s*\d+\s*pts?\s*$','',text).strip()
                else:text=display_weapon_text(text)
                fields=[{'label':'Profile','text':text,'source_ref':weapon['source_ref']}]
            else:
                fields=[{'label':h,'text':c['text'],'source_ref':c['id']} for h,c in zip(weapon['columns'],weapon['cells']) if 'cost' not in h.lower()]
            weapons.append({'fields':fields,'mode':weapon.get('mode'),
                            'availability':weapon.get('availability',[]),'drawbacks':weapon.get('drawbacks',[])})
        result[unit['id']]={'chassis':unit['chassis'],'profiles':unit['profiles'],'weapons':weapons,'systems':systems,
            'mode_rules':unit['mode_rules'],'special_rules':unit['special_rules'],
            'spawned_units':[{'name':child['name'],'rules':[{'text':b['text'],'source_ref':b['id']} for b in child['source_blocks'] if b.get('text','').strip()]} for child in unit['spawned_units']]}
        quick=[]
        battle_weapons=[]
        def add(category,name,text,refs,bonus=False):
            if text.strip():quick.append({'category':category,'name':name,'text':text,'source_refs':refs,'source_faction_bonus':bonus})
        for component in components:
            if component['kind']!='weapon' or not component.get('included',True):continue
            candidates=[p for p in parts if p['kind']=='weapon' and p['source_ref']==component.get('price_source_ref')]
            part=next((p for p in candidates if key(base_name(p['name']))==key(base_name(component['name'])) and (p.get('variant') or None)==(component.get('variant') or None)),None)
            if part is None:
                named=[p for p in candidates if key(base_name(p['name']))==key(base_name(component['name']))]
                part=named[0] if len(named)==1 else candidates[0] if len(candidates)==1 else None
            if not part:continue
            battle_weapons.append({'name':part['name'],'quantity':component['quantity'],'text':'\n'.join(d['text'] for d in part['details']),
                                   'source_refs':[d['source_ref'] for d in part['details']]})
            add('Weapons',part['name'],'\n'.join(d['label']+': '+d['text'] for d in part['details']),[d['source_ref'] for d in part['details']])
            for rule in part.get('help_keywords',[])+part.get('help_rules',[]):add('Weapon keywords',rule['label'],rule['text'],[rule['source_ref']])
            if component.get('linked'):add('Weapon keywords','Linked',linked['text'],[linked['id']])
        for system in systems:
            for rule in system['rules']:add('Systems & traits',system['name'],rule['text'],[rule['source_ref']],system['source_faction_bonus'])
        for weapon in weapons:
            # Preserve explicit availability/drawbacks even where the shared
            # component supplies the current weapon description above.
            for rule in weapon['availability']+weapon['drawbacks']:add('Unit rules',weapon.get('mode') or 'Weapon restrictions',rule['text'],[rule['source_ref']])
        for rule in unit['mode_rules']+unit['special_rules']:add('Unit rules',unit['name'],rule['text'],[rule['source_ref']])
        for child in result[unit['id']]['spawned_units']:
            for rule in child['rules']:add('Unit rules','Spawned unit: '+child['name'],rule['text'],[rule['source_ref']])
        explicit='\n'.join(r['text'] for r in unit['mode_rules']+unit['special_rules'])
        movement_names={s['name'] for s in systems if not s['source_faction_bonus']}
        for name,cell in movement:
            # A unit name containing "Walker" is not evidence of its movement
            # trait. Use named systems or explicit keyword/movement labels.
            if name in movement_names or re.search(r'\b(?:keyword|trait|movement)\s*:\s*'+re.escape(name)+r'\b',explicit,re.I):add('Movement',name,cell['text'],[cell['id']])
        if any(r['name']=='Tracked' and r['category']=='Movement' for r in quick):
            cell=next(cell for name,cell in movement if name=='Stable Platform');add('Movement','Stable Platform',cell['text'],[cell['id']])
        result[unit['id']]['quick_rules']=quick
        result[unit['id']]['battle_weapons']=battle_weapons
    return result
