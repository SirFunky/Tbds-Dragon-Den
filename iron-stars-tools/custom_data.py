"""Price-backed custom construction parts, with stable identities and source evidence."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FACTIONS={'concord':'iron-concord','unmc':'unmc','rebellion':'cybernetic-rebellion','avalon':'new-avalon'}

# User clarification supersedes the generic two-mode example and explicitly
# directs use of the UNMC Interceptor mode table for movement and Defence.
TRANSFORM_POLICY={
    'source_ref':'user:2026-11-07-transform-clarification',
    'allowed_factions':['unmc','cybernetic-rebellion'],
    'shared_mech_stats':['structure'],
    'shared_systems':True,
    'factions':{
        'unmc':{'form_names':['Mech','Hybrid','Flyer'],'flyer_only':True,'fixed_names':True,
                'movement_offsets':[0,10,10],'defence_offsets':[0,-1,-2],
                'source_refs':['unmc:b0066:r4:c2','unmc:b0066:r4:c3','unmc:b0066:r3:c2','unmc:b0066:r3:c3','unmc:b0066:r2:c2','unmc:b0066:r2:c3','unmc:b0063:r4:c1']},
        'cybernetic-rebellion':{'form_names':['Mech','Alternate'],'flyer_only':False,'fixed_names':False,
                               'movement_offsets':[0,0],'defence_offsets':[0,0]},
    },
}

def interval(text):
    match=re.fullmatch(r'\s*(\d+(?:\.\d+)?)(?:\s*[–—-]\s*(\d+(?:\.\d+)?))?\s*(?:cm)?\s*',text)
    if not match:return None
    return [float(match[1]),float(match[2] or match[1])]

def custom_catalog():
    armory=json.loads((ROOT/'iron-stars/data/armory.json').read_text(encoding='utf-8'))['components']
    units=json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))['units']
    core=json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
    glossary=next(b for b in core['blocks'] if b['id']=='core:b0232')['rows'][1:]
    docs={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')}
    blocks={b['id']:b for doc in docs.values() for b in doc['blocks']}
    # Unique-component prices sometimes point to a breakdown or "as above".
    # Keep their actual effect and mode context available in the explanation.
    help_refs={'rebellion:b0392':[383,385,386],
               'rebellion:b0429':[419,421,422,423],
               'rebellion:b0561':[550,551,552,553,554,555,556]}
    parts=[]
    for item in armory:
        if item['price'] is None:continue
        # These explicitly named subfaction options need a subfaction selection;
        # a faction choice alone does not establish permission to use them.
        if item['name'] in ('Black Budget (SynCo)','Deep Strike (Stratos)'):continue
        identity='|'.join([item['source_id'],item['kind'],item['name'],item['variant'] or ''])
        part={**item,'id':'part-'+hashlib.sha256(identity.encode()).hexdigest()[:20],
              'armory_id':item['id'],'allowed_factions':None if item['source_id']=='core' else [FACTIONS[item['source_id']]]}
        # Explicit core faction locks override the general shared-cost table.
        if item['name']=='Drone Logic':part['allowed_factions']=['cybernetic-rebellion']
        if item['name']=='Command Network':part['allowed_factions']=['iron-concord']
        if item['name']=='Transform':part['allowed_factions']=TRANSFORM_POLICY['allowed_factions']
        if item['kind']=='chassis':
            fields={d['label'].casefold():d['text'] for d in item['details']}
            move=interval(fields.get('move',fields.get('m','')))
            structure=interval(fields.get('structure',fields.get('str','')))
            defence=fields.get('defence',fields.get('def',fields.get('d','')))
            if not move or not structure or not re.fullmatch(r'[2-6]\+',defence):continue
            part.update({'movement':move,'structure':structure,'defence':defence})
            if item['source_id']=='unmc' and item['name']=='UN Interceptor Frame':
                mech=next(r for r in blocks['unmc:b0066']['rows'] if r['id']=='unmc:b0066:r4')['cells'][2]
                part.update({'mech_defence':mech['text'],'mech_defence_ref':mech['id']})
        if item['kind']=='weapon':
            evidence=[]
            for unit in units:
                for c in unit['points']['calculation']['components']:
                    if c.get('price_source_ref')!=item['source_ref']:continue
                    for w in unit['weapons']:
                        if w['source_ref']==c['source_ref'] and w['kind']=='text':
                            evidence.append({'label':'Stock weapon profile','text':w['text'],'source_ref':w['source_ref']})
            # Only fill absent weapon stats. Older stock text must never be
            # appended alongside the newer core profile for the same component.
            has_stats=any(d['label'].lower() in ('fp','me','stats') or re.search(r'\b(?:FP|ME)\s+\d',d['text']) for d in item['details'])
            if evidence and not has_stats:part['details']=item['details']+[evidence[0]]
            fp=None
            for d in part['details']:
                if d['label'].lower()=='fp':
                    match=re.match(r'(\d+)',d['text'])
                    if match:fp=int(match[1]);break
                match=re.search(r'\bFP\s+(\d+)',d['text'])
                if match:fp=int(match[1]);break
            part['fp']=fp
        if item['kind']=='system':
            part['unique']=bool(re.search(r'\bunique\b',item['name'],re.I))
            part['requires_ammunition']=item['name'].startswith('Ammo Bin')
        part['help_keywords']=[]
        part['help_rules']=[{'label':'Source rule','text':blocks[f'rebellion:b{n:04}']['text'],
                            'source_ref':f'rebellion:b{n:04}'} for n in help_refs.get(item['source_ref'],[])]
        if item['kind']=='weapon':
            text=' '.join(d['text'] if d['label'].lower() not in ('fp','me') else d['label']+' '+d['text'] for d in part['details'] if d['label'].lower() not in ('notes','range'))
            for row in glossary:
                term=row['cells'][0]['text'].strip()
                if not term or term in ('Linked Costing:',):continue
                stem=re.sub(r'\s*\([^)]*\)','',term).removesuffix(' X').strip()
                if re.search(r'(?<!\w)'+re.escape(stem)+r'(?!\w)',text,re.I):
                    part['help_keywords'].append({'label':term,'text':row['cells'][1]['text'],'source_ref':row['cells'][1]['id']})
        parts.append(part)
    transform_action=blocks['core:b0159']
    flyer=next(r for r in blocks['core:b0235']['rows'] if r['cells'][0]['text']=='Flyer')['cells'][1]
    def movement_row(table,name):
        cell=next(r for r in blocks[table]['rows'] if r['cells'][0]['text']==name)['cells'][1]
        return {'text':cell['text'],'source_ref':cell['id']}
    movement_types=[]
    for name in ('Walker','Wheeled','Tracked','Hover','Flyer','Burrower'):
        if name=='Wheeled':
            approved=json.loads((ROOT/'iron-stars-tools/approved-rules.json').read_text(encoding='utf-8'))['rules']
            rule=next(r for r in approved if r['id']=='author:wheeled' and r['status']=='approved')
            rules=[{'text':'\n'.join(rule['effects']),'source_ref':rule['source_ref']}]
        else:
            rules=[movement_row('core:b0084' if name in ('Walker','Hover','Burrower') else 'core:b0235',name)]
            if name=='Tracked':rules.append(movement_row('core:b0235','Stable Platform'))
        movement_types.append({'id':name.lower(),'name':name,'rules':rules})
    linked=next(r for r in blocks['core:b0232']['rows'] if r['cells'][0]['text']=='Linked')['cells'][1]
    jetpack=next(r for r in blocks['core:b0235']['rows'] if r['cells'][0]['text']=='Jetpack')['cells'][1]
    return {'parts':parts,'jetpack_rule':{'text':jetpack['text'],'source_ref':jetpack['id']},'linked_rule':{'text':linked['text'],'source_ref':linked['id']},'movement_types':movement_types,'transform_policy':TRANSFORM_POLICY,'transform_rules':[
            {'text':transform_action['text'].strip(),'source_ref':transform_action['id']}],
            'flyer_rule':{'text':flyer['text'],'source_ref':flyer['id']},
            'faction_lock_ref':'core:b0201','unique_ref':'core:b0235:r11',
            'linked_ref':'core:b0232:r18','custom_forbidden':['southern-cross-compact']}
