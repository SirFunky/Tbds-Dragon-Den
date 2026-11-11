"""Compile literal unit observations into reusable reference data, never approved army costs."""
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
FACTIONS={'concord':('iron-concord','Iron Concord'),'unmc':('unmc','UNMC'),
          'rebellion':('cybernetic-rebellion','Cybernetic Rebellion'),'avalon':('new-avalon','New Avalon')}
QUICK={'rebellion':{49:697,75:705,91:713,110:720,126:728},
       'avalon':dict(zip([65,77,92,108,130,143,159,171,188,201,220,234,252,266],
                        [285,289,296,300,307,311,318,322,329,333,340,344,351,355]))}
# Confirmed same-source cost observations; these are questions, not replacement prices.
COST_REVIEW={
 'concord:b0035':'The unit lists 8 pts; its listed chassis, weapons, and Discipline Drills total 9. No stock discount is specified.',
 'concord:b0039':'The unit lists 16 pts; its listed chassis, weapons, and Scorch Doctrine total 19. No stock discount is specified.',
 'concord:b0075':'The unit lists 35 pts; its listed components total 37. No replacement cost has been chosen.',
 'concord:b0080':'The unit lists 39 pts; its listed components total 43. No replacement cost has been chosen.',
 'unmc:b0061':'The unit lists 62 pts. Its equipment list and mode table also disagree about the Mech Mode blade; a complete authoritative configuration and cost are not established.',
 'unmc:b0171':'The unit lists 70 pts, while its explicit component prices total 67.',
 'rebellion:b0571':'The unit lists 24 pts, but its written chassis, weapon, and trait subtotals total 28. Quantum Echo is both charged and called free.',
 'rebellion:b0601':'The unit lists 29 pts, but its written subtotals total 37. Quantum Echo is also called free.',
 'avalon:b0065':'The listed 30 pts covers the chassis and laser bundle before the separately priced Overdrive and other systems. The source does not specify a stock discount.',
 'avalon:b0077':'The listed 35 pts differs from the 40-point sum of chassis, laser bundle, and Overdrive, before other systems.',
 'avalon:b0092':'The listed 60 pts differs from the 65-point sum of chassis, rapier, rifle, shield, and Advance Guard, before other systems.',
 'avalon:b0130':'The listed 70 pts differs from the 73-point sum of the identified priced components, before other systems.',
 'avalon:b0252':'The listed 90 pts differs from the 103-point sum of the identified priced components, before Shield-Wings.',
}

def clean(text):return re.sub(r'^[^A-Za-z0-9]+','',text).strip()
def slugify(text):return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')
def number(ref):return int(ref.split(':b')[1].split(':')[0])
def literal(text,ref):return {'text':text.strip(),'source_ref':ref}
def system_name(text):
    name=re.split(r'\s+[–—]\s+',text,maxsplit=1)[0] if re.search(r'\s[–—]\s',text) else text.split(':',1)[0]
    return re.sub(r'\s*\((?:\d+\s*pts?|Faction|Subfaction|Unique)\)\s*','',name,flags=re.I).strip()

def name_of(record):
    text=next(b['text'].strip() for b in record['source_blocks'] if b.get('text','').strip())
    if text.endswith(('Sentinels Unit','Swarm Synod Unit')):
        text=next(b['text'].strip() for b in record['source_blocks'][1:] if b.get('text','').strip())
    text=clean(text.split('\n')[0])
    text=re.sub(r'^(?:UNIT PROFILE:|Hero Mech:|Unit Example:)\s*','',text,flags=re.I)
    text=re.sub(r'\s*[—–-]\s*~?\s*\d+\s*pts.*$|\s+\d+\s*pts.*$','',text,flags=re.I)
    return text

def profiles(blocks):
    found=[]; fields={}; chassis=None
    def add(field,value,ref):
        if value and field not in fields:fields[field]=literal(value,ref)
    for b in blocks:
        if b['kind']=='table':
            headers=[c['text'].strip().lower() for c in b['rows'][0]['cells']]
            if ('m' in headers or 'move' in headers) and ('d' in headers or 'defence' in headers):
                for row in b['rows'][1:]:
                    rowfields={}; mode='Standard'
                    for header,cell in zip(headers,row['cells']):
                        if header=='mode':mode=cell['text'].strip()
                        field={'m':'movement','move':'movement','d':'defence','defence':'defence','str':'structure','structure':'structure'}.get(header)
                        if field:rowfields[field]=literal(cell['text'],cell['id'])
                    access={header:literal(cell['text'],cell['id']) for header,cell in zip(headers,row['cells']) if header in ['weapons','special rules','traits']}
                    found.append({'name':mode,'fields':rowfields,'source_ref':row['id'],'mode_details':access})
            elif headers[0]=='stat':
                for row in b['rows'][1:]:
                    field={'move':'movement','defence':'defence','str':'structure'}.get(row['cells'][0]['text'].strip().lower())
                    if field:add(field,row['cells'][1]['text'],row['cells'][1]['id'])
            elif headers[0].startswith('base stats'):
                for row in b['rows'][1:]:
                    value=row['cells'][0]['text']
                    for label,field in [('Move','movement'),('Structure','structure')]:
                        match=re.match(label+r':\s*(.+)',value)
                        if match:add(field,match[1],row['cells'][0]['id'])
            continue
        text=b.get('text',''); ref=b['id']
        match=re.search(r'\bChassis:\s*([^\n|]+)',text)
        if match and chassis is None:
            chassis=literal(re.split(r'\s*\(',match[1])[0].strip(' )'),ref)
        # Only explicit profile lines; a system's damage or movement bonus is not a base stat.
        for line in text.splitlines():
            line=clean(line)
            if re.match(r'(?:M|Move|D|Defence|STR|Structure|Stats)\s*:',line,re.I):
                for pattern,field in [(r'\b(?:M|Move)\s*:\s*(\d+(?:\.\d+)?\s*cm)','movement'),(r'\b(?:D|Defence)\s*:\s*(\d\+)','defence'),(r'\b(?:STR|Structure)\s*:\s*(\d+)','structure')]:
                    m=re.search(pattern,line,re.I)
                    if m:add(field,m[1],ref)
            elif line.startswith('Chassis:'):
                match=re.search(r'\((\d+(?:\.\d+)?\s*cm)\s*\|\s*Defence\s*(\d\+)\s*\|\s*STR\s*(\d+)',line,re.I)
                if match:
                    for field,value in zip(['movement','defence','structure'],match.groups()):add(field,value,ref)
    if not found and fields:found=[{'name':'Standard','fields':fields,'source_ref':next(iter(fields.values()))['source_ref']}]
    elif found:
        for form in found:
            for key,value in fields.items():form['fields'].setdefault(key,value)
    return found,chassis

def points_of(blocks):
    observations=[];seen_weapons=False
    for index,b in enumerate(blocks):
        if b['kind']!='paragraph':continue
        text=b['text']
        for line in text.splitlines():
            label=clean(line)
            if re.match(r'^(?:Weapons|Weapon Loadout|Weapons Loadout)\b',label,re.I):seen_weapons=True
            if index==0 or re.match(r'\s*(?:Total Cost:|Total\s*=)',line) or (not seen_weapons and re.match(r'\s*Cost:',line)):
                match=re.search(r'(~?\s*\d+)\s*pts?\b',line,re.I)
                if match:
                    # Total = 15 + ... = 44 pts: the regex finds the final amount.
                    observations.append({'value':int(re.sub(r'\D','',match[1])),'approximate':'~' in match[1],
                                         'text':match[0].strip(),'source_ref':b['id']})
    unique={v['value'] for v in observations}
    return {'observations':observations,'listed_value':observations[0]['value'] if observations else None,
            'filter_value':next(iter(unique)) if len(unique)==1 else None,
            'approximate':any(v['approximate'] for v in observations),'approved_value':None}

def role_of(blocks):
    for b in blocks:
        for line in b.get('text','').splitlines():
            m=re.match(r'Role:\s*(.+)',clean(line),re.I)
            if m:return literal(m[1],b['id'])
        if b['kind']=='table':
            headers=[c['text'].strip() for c in b['rows'][0]['cells']]
            if headers==['Type','Description']:
                row=b['rows'][1];return literal(row['cells'][0]['text'],row['id'])
    return None

def role_tags(role):
    text=(role or {}).get('text','').lower()
    patterns={'Command':r'command|leader|lieutenant','Recon':r'recon|scout|observer|harass|skirmish|flank',
      'Assault':r'assault|brawl|melee|line.?break|shock|duel','Fire support':r'fire|snip|artillery|suppress|ranged|long.range|gun',
      'Support':r'support|repair|escort|bodyguard|protect|transport|deployment|attrition|control|anchor',
      'Battle line':r'battle line|infantry|trooper|frontline'}
    return [tag for tag,pattern in patterns.items() if re.search(pattern,text)]

def subfaction(key,start):
    if key=='concord':
        for lo,hi,name in [(89,147,'House Draughan'),(150,209,'House Vexillis'),(211,329,'House Romanow'),(332,371,'House Kaelstrom')]:
            if lo<=start<=hi:return name
    if key=='rebellion':
        if 144<=start<=298:return 'The Warmachines'
        if 444<=start<=567:return 'The Swarm Synod'
    # No Avalon Order keyword is assigned just because a unit name sounds related.
    return None

def equipment(blocks):
    weapons=[]; systems=[]; mode_rules=[]; section=None; mode=None; pending=[]; in_cost=False
    stop=re.compile(r'^(?:Role(?:\s*&\s*Tactics)?|Tactics\s*&\s*Role|Tactical Use|Total Cost Breakdown|Total Cost|Stats|Base Stats|Chassis|Strengths|Weaknesses|Recommended Use|Faction Trait)\b',re.I)
    for b in blocks:
        if b['kind']=='table':
            headers=[c['text'].strip() for c in b['rows'][0]['cells']]
            low=[h.lower() for h in headers]
            if 'weapon' in low or ('stats' in low and any('mount' in h or h=='arm' for h in low)):
                for row in b['rows'][1:]:
                    cells={h:c for h,c in zip(headers,row['cells'])}
                    weapons.append({'kind':'table-row','columns':headers,'cells':row['cells'],'source_ref':row['id'],'mode':mode})
            elif low and low[0] in ['system','trait'] and 'effect' in low:
                for row in b['rows'][1:]:
                    if row['cells'][0]['text'].strip()=='Sponsor Protocol':continue
                    systems.append({'name':row['cells'][0]['text'],'description':row['cells'][1]['text'],
                                    'source_ref':row['id'],'mode':mode})
            continue
        for line in b.get('text','').splitlines():
            line=line.strip()
            if not line:continue
            label=clean(line)
            if label.startswith('Total Cost Breakdown'):in_cost=True;section=None;continue
            if in_cost:
                if re.match(r'^(?:Role\s*&\s*Tactics|Tactics\s*&\s*Role)',label):in_cost=False
                continue
            if re.match(r'^Mode\s+\d+\s*[–—-]',label):mode=label;section=None;pending=[];continue
            if re.search(r'Weapons disabled|Melee Disabled|Only available in|Available in all modes|Mech Mode Only|Switching modes|Cannot attack in melee while transformed|Start the game in any mode|no melee in tank mode',line,re.I):
                if re.match(r'Only available in|Available in all modes|Mech Mode Only',label,re.I) and weapons:
                    weapons[-1].setdefault('availability',[]).append(literal(line,b['id']))
                else:mode_rules.append(literal(line,b['id']))
            if re.match(r'^(?:Weapons|Weapon Loadout|Weapons Loadout|Ranged Weapons|Melee Weapons)\b',label,re.I):section='weapons';pending=[];continue
            if re.match(r'^(?:Systems|Traits?|Special Rules)\b',label,re.I):
                section='systems';pending=[]
                if ':' not in label or not label.split(':',1)[1].strip():continue
                line=label.split(':',1)[1].strip();label=line
            if stop.match(label):section=None;pending=[];continue
            if label.startswith(('Knightly Perfection','Sponsor Protocol')):continue
            if re.search(r'\b(?:FP|ME)\s*\d',line):
                if section=='systems' and not re.match(r'^(?:FP|ME)\s*\d',line):
                    systems.append({'name':system_name(label),
                                    'description':line,'source_ref':b['id'],'mode':mode})
                else:
                    weapons.append({'kind':'text','text':line,'name_context':pending[-1] if pending else None,
                                    'source_ref':b['id'],'mode':mode})
                    pending=[]
            elif section=='systems':
                # Preserve individual named effects and their drawback continuation.
                if re.match(r'^(?:Drawback:|On |1[–—-]3|4[–—-]6)',label) and systems:
                    systems[-1]['description']+='\n'+line
                elif re.search(r'\s[–—]\s|\([+]|\(\d+\s*pts?\)|:',label):
                    systems.append({'name':system_name(label),
                                    'description':line,'source_ref':b['id'],'mode':mode})
                elif systems:systems[-1]['description']+='\n'+line
            elif section=='weapons' and re.match(r'^Drawback:',label) and weapons:
                weapons[-1].setdefault('drawbacks',[]).append(literal(line,b['id']))
            elif section=='weapons' and ('Shield' in label or 'shield' in label) and not re.search(r'\b(?:FP|ME)\s*\d',line):
                systems.append({'name':re.split(r'\s*\(',label,maxsplit=1)[0],'description':line,'source_ref':b['id'],'mode':mode})
            elif section=='weapons' or re.match(r'^(?:Mode\s*\d|Mech Mode|Flight Mode)',label):pending.append(line)
            elif re.search(r'\b(?:Gun|Cannon|Cannons|Missile|Rifle|Blade|Talons|Spiker|Carbine|Knife|Laser|Lasers|Fists)\b',label,re.I):
                pending.append(line)
    for weapon in weapons:
        text=weapon.get('text','') if weapon['kind']=='text' else ' | '.join(c['text'] for c in weapon['cells'])
        weapon['statistics']={field:match[1] if match else None for field,match in [
            ('fp',re.search(r'\bFP\s*(\d+)',text)),('me',re.search(r'\bME\s*(\d+)',text)),
            ('range_cm',re.search(r'(\d+(?:\.\d+)?)\s*cm',text))]}
    return weapons,systems,mode_rules

def compile_units():
    docs={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')}
    evidence=json.loads((ROOT/'iron-stars-review/source-precedence.json').read_text(encoding='utf-8'))['evidence']
    for key,doc in docs.items():
        digest=hashlib.sha256((ROOT/'iron-stars-source/originals'/doc['filename']).read_bytes()).hexdigest()
        assert digest==doc['sha256']==next(e['sha256'] for e in evidence if e['source_id']==key)
    source=json.loads((ROOT/'iron-stars-source/content/unverified/units.json').read_text(encoding='utf-8'))['records']
    units=[]
    for entry in source:
        if entry['record_type']!='roster-entry':continue
        key=entry['source_id'];blocks=entry['source_blocks'];start=number(entry['source_refs'][0]);name=name_of(entry)
        faction,faction_name=FACTIONS[key]
        forms,chassis=profiles(blocks);cost=points_of(blocks);role=role_of(blocks)
        if key=='avalon':
            # Each Prototype/Experimental pair has an explicit parent-frame role;
            # use that role rather than classifying its later narrative sales copy.
            role_block=dict(zip([65,77,92,108,130,143,159,171,188,201,220,234,252,266],
                                [63,63,93,109,128,128,157,157,186,186,218,218,250,250]))[start]
            role=role_of([next(b for b in docs[key]['blocks'] if number(b['id'])==role_block)])
        child_ranges={('rebellion',91):[(106,106,'Light Drone (Spawned)')],
          ('rebellion',182):[(202,203,'Sky Reaver'),(204,206,'Blade Runner'),(207,208,'Beamling')],
          ('rebellion',532):[(553,556,'Broodling Drone')]}.get((key,start),[])
        child_blocks={b['id'] for lo,hi,_ in child_ranges for b in blocks if lo<=number(b['id'])<=hi}
        spawned=[{'name':name,'source_blocks':[b for b in blocks if lo<=number(b['id'])<=hi]} for lo,hi,name in child_ranges]
        weapons,systems,mode_rules=equipment([b for b in blocks if b['id'] not in child_blocks])
        notes=[]
        if len({o['value'] for o in cost['observations']})>1:
            notes.append('This entry prints different total costs: '+', '.join(dict.fromkeys(o['text'] for o in cost['observations']))+'. No final cost has been selected.')
        if entry['source_refs'][0] in COST_REVIEW:notes.append(COST_REVIEW[entry['source_refs'][0]])
        alternate=[]
        quick_start=QUICK.get(key,{}).get(start)
        if quick_start:
            quick=next(u for u in source if u['source_id']==key and number(u['source_refs'][0])==quick_start)
            quickforms,_=profiles(quick['source_blocks'])
            # The Rebellion quick sheet calls Defence "A"; retain that literal
            # observation rather than silently reinterpreting it as Defence.
            quick_text='\n'.join(b.get('text','') for b in quick['source_blocks'])
            if key=='rebellion':
                alternate=[{'label':'Quick-reference entry','profiles':quickforms,'source_refs':quick['source_refs'],
                            'profile_text':[literal(b['text'],b['id']) for b in quick['source_blocks'] if re.search(r'\bM:',b.get('text',''))]}]
                notes.append('The detailed entry and quick-reference sheet in this document give different profiles. Both are retained below; their revision order is unknown.')
            elif (key,start) in [('avalon',92),('avalon',108),('avalon',143),('avalon',266)]:
                notes.append('The detailed entry and quick-reference sheet list different systems. No equipment has been added from the quick sheet.')
                alternate=[{'label':'Quick-reference systems','profiles':[],'source_refs':quick['source_refs'],
                    'profile_text':[literal(b['text'],b['id']) for b in quick['source_blocks'] if b.get('text','').startswith('Systems:')]}]
        if len({o['value'] for o in cost['observations']})>1 or entry['source_refs'][0] in COST_REVIEW:
            cost['filter_value']=None
        identity=faction+'-'+slugify(name)
        units.append({'id':identity,'name':name,'faction':faction,'faction_name':faction_name,
          'subfaction':subfaction(key,start),'role':role,'role_tags':role_tags(role),
          'chassis':chassis,'points':cost,'profiles':forms,'alternate_observations':alternate,
          'weapons':weapons,'systems':systems,'mode_rules':mode_rules,'spawned_units':spawned,'special_rules':[],
          'configuration':'Experimental' if name.startswith('Experimental ') else 'Prototype' if name.startswith('Prototype ') else None,
          'artwork':None,'core_rules_version':'0.0.14','source_version':None,
          'publication_status':'reference','approved_for_army_builder':False,
          'review_notes':notes,'source':{'id':key,'filename':docs[key]['filename'],'sha256':docs[key]['sha256']},
          'source_refs':entry['source_refs']})
    # Distinct latest-core examples are useful references, but missing statistics
    # stay null. Generic chassis-tier ranges are not invented unit statistics.
    for start,end,extra_start,extra_end,faction,name in [
        (205,210,304,308,'new-avalon','Knight-Errant Frame'),
        (212,218,349,353,'iron-concord','Legate-Class Linewalker'),
        (220,226,451,457,'unmc','UNDF Vulture-Stryker'),
        (399,405,399,405,'cybernetic-rebellion','Crawler-Class Enforcer')]:
        blocks=[b for b in docs['core']['blocks'] if start<=number(b['id'])<=end]
        extra=[b for b in docs['core']['blocks'] if extra_start<=number(b['id'])<=extra_end]
        cost=points_of(blocks)
        for b in blocks:
            if b.get('text','').strip().startswith('Total:'):
                m=re.search(r'(\d+)\s*pts',b['text'])
                if m:cost={'observations':[{'value':int(m[1]),'approximate':False,'text':m[0],'source_ref':b['id']}], 'listed_value':int(m[1]),'filter_value':int(m[1]),'approximate':False,'approved_value':None}
        forms,chassis=profiles(blocks);weapons,systems,mode_rules=equipment(blocks)
        for b in blocks:
            if re.match(r'^(?:Shield Array|Command Network|Smoke Launcher|Transform|Targeting Network):',b.get('text','').strip()):
                systems.append({'name':b['text'].split(':')[0].strip(),'description':b['text'].strip(),'source_ref':b['id'],'mode':None})
        if not weapons:
            for b in blocks:
                if re.search(r'\b(?:FP|ME)\s*\d',b.get('text','')):weapons.append({'kind':'text','text':b['text'].strip(),'name_context':None,'source_ref':b['id'],'mode':None})
        faction_name=next(v[1] for v in FACTIONS.values() if v[0]==faction)
        units.append({'id':faction+'-'+slugify(name),'name':name,'faction':faction,'faction_name':faction_name,
          'subfaction':None,'role':None,'role_tags':[],'chassis':chassis,'points':cost,'profiles':forms,
          'alternate_observations':[],'weapons':weapons,'systems':systems,'mode_rules':mode_rules,'spawned_units':[],'special_rules':[
              literal(b['text'],b['id']) for b in extra if b.get('text','').strip() and not b.get('style','').startswith('heading')],
          'configuration':'Core example','artwork':None,'core_rules_version':'0.0.14','source_version':'0.0.14',
          'publication_status':'reference','approved_for_army_builder':False,'review_notes':[],
          'source':{'id':'core','filename':docs['core']['filename'],'sha256':docs['core']['sha256']},
          'source_refs':list(dict.fromkeys(b['id'] for b in blocks+extra))})
    assert len({u['id'] for u in units})==len(units)
    for unit in units:
        for weapon in unit['weapons']:
            if 'statistics' not in weapon:
                text=weapon.get('text','')
                weapon['statistics']={field:match[1] if match else None for field,match in [
                    ('fp',re.search(r'\bFP\s*(\d+)',text)),('me',re.search(r'\bME\s*(\d+)',text)),
                    ('range_cm',re.search(r'(\d+(?:\.\d+)?)\s*cm',text))]}
    runpy.run_path(str(ROOT/'iron-stars-tools/pricing.py'))['reprice'](units)
    data={'schema_version':1,'core_rules_version':'0.0.14','publication_status':'reference',
          'factions':[{'id':id,'name':name,'status':'reference'} for id,name in FACTIONS.values()]+
             [{'id':'fourth-imperium','name':'Fourth Imperium','status':'in-development'},
              {'id':'living-dominion','name':'Living Dominion','status':'in-development'},
              {'id':'southern-cross-compact','name':'Southern Cross Compact','status':'import-roster-pending'}],
          'units':units}
    out=ROOT/'iron-stars/data/units.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data

if __name__=='__main__':
    data=compile_units(); print('Compiled',len(data['units']),'source unit references.')
