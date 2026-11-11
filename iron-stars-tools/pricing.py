"""Traceable component pricing. Unknown prices never become zero or a stock-total remainder."""
from collections import Counter
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]

def key(text):
    text=text.casefold().replace('’',"'").replace('–','-').replace('—','-')
    return re.sub(r'\s+',' ',text).strip(' .:')

def amount(text):
    match=re.search(r'(?<![\w.])([+-]?\d+)\s*pts?\b',text,re.I)
    return int(match[1]) if match else None

def linked_cost(base,quantity):
    """First three copies at base price, fourth at 2x, fifth at 3x, etc."""
    if not isinstance(quantity,int) or quantity<1:raise ValueError('Quantity must be a positive integer')
    return sum(base*(1 if i<3 else i-1) for i in range(quantity))

class Prices:
    def __init__(self):
        self.docs={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')}
        self.blocks={b['id']:b for doc in self.docs.values() for b in doc['blocks']}
        self.entries={}
        tables={'core':{'chassis':[187],'weapon':[192,194],'system':[197]},
          'concord':{'chassis':[28],'weapon':[30],'system':[33]},
          'unmc':{'chassis':[35],'weapon':[40,42],'system':[45,195]},
          'rebellion':{'chassis':[30],'weapon':[35,37],'system':[41]},
          'avalon':{'chassis':[49],'weapon':[52,55],'system':[58]}}
        for namespace,groups in tables.items():
            for kind,numbers in groups.items():
                for number in numbers:
                    table=self.blocks[f'{namespace}:b{number:04}']
                    headers=[c['text'].lower() for c in table['rows'][0]['cells']]
                    for row in table['rows'][1:]:
                        if row['cells'][0]['text'].strip()=='Sponsor Protocol':continue
                        for column,header in enumerate(headers):
                            if 'cost' not in header:continue
                            value=amount(row['cells'][column]['text'])
                            if value is None:continue
                            variant='prototype' if 'prototype' in header else 'experimental' if 'experimental' in header else None
                            self.put(namespace,kind,row['cells'][0]['text'],value,row['cells'][column]['id'],variant)
        # The newer core's explicitly priced named example components are also
        # valid prices; these do not turn example unit totals into component costs.
        for ref,name,kind in [('core:b0207','Beam Rapier','weapon'),('core:b0208','Knight Rifle','weapon'),
          ('core:b0214','Twin Autocannons','weapon'),('core:b0215','Shock Blade','weapon'),
          ('core:b0216','Command Network','system'),('core:b0217','Smoke Launcher','system'),
          ('core:b0222','Rail Carbine','weapon'),('core:b0223','Missile Swarm','weapon'),
          ('core:b0225','Targeting Network','system')]:
            self.put('core',kind,name,amount(self.blocks[ref]['text']),ref)
        for line in self.blocks['concord:b0031']['text'].splitlines():
            name=line.split('|')[0].strip();self.put('concord','weapon',name,amount(line),'concord:b0031')
        # Explicit prices for unique components not in the general armories.
        # Each regex must match that component's own stated price in its source.
        inline=[
          ('concord:b0061','system','Reinforced Cooling',r'\((\d+) pts\)'),
          ('rebellion:b0152','weapon','Ravager Melee Laser',r'\((\d+) pts\)'),
          ('rebellion:b0156','weapon','Ravager Laser Pods',r'\((\d+) pts\)'),
          ('rebellion:b0214','system','Fabricator Protocols',r'\((\d+) pts'),
          ('rebellion:b0236','weapon','Mech Fists',r'\((\d+) pts'),
          ('rebellion:b0241','system','Stable Platform',r'\((\d+) pts\)'),
          ('rebellion:b0273','weapon','Laser Sword',r'\((\d+) pts\)'),
          ('rebellion:b0311','weapon','Dual Laser Daggers',r'\((\d+) pts\)'),
          ('rebellion:b0363','system','Transport',r'Transport (\d+) pts'),
          ('rebellion:b0392','system','Field Repair',r'\((\d+) pts\)'),
          ('rebellion:b0429','system','Heavy Transport',r'\((\d+) pts\)'),
          ('rebellion:b0463','weapon','Swarm Blades',r'\((\d+) pts\)'),
          ('rebellion:b0464','system','Swarm Mass',r'Swarm Mass (\d+) pts'),
          ('rebellion:b0491','weapon','Chitin Blades',r'\((\d+) pts\)'),
          ('rebellion:b0492','system','Burrower',r'Burrower (\d+) pts'),
          ('rebellion:b0512','weapon','Chitin Slam',r'\((\d+) pts\)'),
          ('rebellion:b0524','system','Swarm Vulnerability',r'Swarm Vulnerability (-\d+) pts'),
          ('rebellion:b0541','weapon','Plasma Cannon',r'\((\d+) pts\)'),
          ('rebellion:b0543','weapon','Hive Claws',r'\((\d+) pts\)'),
          ('rebellion:b0561','system','Brood Spawning',r'Brood Spawning (\d+) pts'),
          ('rebellion:b0579','weapon','Automatic Laser Array',r'\((\d+) pts\)'),
          ('rebellion:b0582','weapon','Reinforced Fists',r'\((\d+) pts\)'),
          ('rebellion:b0609','weapon','Automatic Laser Rifle',r'\((\d+) pts\)'),
          ('rebellion:b0611','weapon','Combat Strike',r'\((\d+) pts\)'),
          ('rebellion:b0639','weapon','Laser HMG',r'\((\d+) pts\)'),
          ('rebellion:b0673','weapon','Heavy Automated Laser Carbine',r'\((\d+) pts\)'),
          ('rebellion:b0675','weapon','Plasma Sword',r'\((\d+) pts\)'),
          ('unmc:b0126','weapon','Light Autocannon Array',r'Cost: (\d+) pts'),
          ('unmc:b0183','weapon','VX-20C Cascade Missile Pod',r'Cost: (\d+) pts'),
          ('unmc:b0187','weapon','M-55 Autocannon',r'Cost: (\d+) pts'),
          ('unmc:b0191','weapon','Archon Heavy Power Fist',r'Cost: (\d+) pts'),
        ]
        for ref,kind,name,pattern in inline:
            match=re.search(pattern,self.blocks[ref]['text'])
            if not match:raise ValueError('Component price evidence changed: '+ref+' '+name)
            self.put(ref.split(':')[0],kind,name,int(match[1]),ref)

    def put(self,namespace,kind,name,value,ref,variant=None):
        if value is None:return
        # User clarified Scout armory entries are individual components too.
        # The premade's three installed guns are charged separately, with no discount.
        source_name=name
        name={'3× Medium Lasers (Scout)':'Medium Laser (Scout)',
              '3× Medium Lasers+ (Scout)':'Medium Laser+ (Scout)'}.get(name,name)
        self.entries[(namespace,kind,key(base_name(name)),variant)]={'name':name.strip(),'unit_price':value,
          'source_name':source_name,
          'source_ref':ref,'source_id':namespace,'variant':variant,
          'source_filename':self.docs[namespace]['filename'],'source_sha256':self.docs[namespace]['sha256']}

    def find(self,namespace,kind,name,variant=None):
        # Distinct explicitly named Prototype/Experimental parts retain their
        # own variant price. A generic core part is not that named variant.
        if variant:
            return self.entries.get((namespace,kind,key(name),variant)) or self.entries.get(('core',kind,key(name),None)) or self.entries.get((namespace,kind,key(name),None))
        result=self.entries.get(('core',kind,key(name),None)) or self.entries.get((namespace,kind,key(name),None))
        if result is None and kind=='system' and key(name)=='stable platform':
            result=self.entries.get(('rebellion','system','stable platform',None))
        return result

    def block_text(self,ref):return self.blocks[ref]['text']

def base_name(name):
    name=re.sub(r'\s*\((?:House[^)]*|[^)]*pts[^)]*|Faction|Subfaction|Unique|Experimental|Stable|new|immune[^)]*|[+]\d[^)]*)\)','',name,flags=re.I)
    return re.sub(r'\s+',' ',name).strip(' .:')

# Explicitly named chassis and source package associations. Generic tier words
# use the current core table; unique named frames keep their own armory price.
CHASSIS={
 'concord:b0211':('Unique Hero Chassis','concord:b0214'),
 'unmc:b0061':('UN Interceptor Frame','unmc:b0035:r3:c1'),
 'rebellion:b0049':('Adaptive Medium','rebellion:b0045:r2:c2'),
 'rebellion:b0075':('Hive Heavy','rebellion:b0045:r3:c2'),
 'rebellion:b0091':('Adaptive Medium','rebellion:b0045:r4:c2'),
 'rebellion:b0110':('Ascendant Core','rebellion:b0045:r5:c2'),
 'rebellion:b0126':('Drone (Light)','rebellion:b0045:r6:c2'),
}
for refs,name in [([65,77],'Flyer Scout'),([92,108],'Errant Frame'),([130,143],'Black Knight'),
                 ([159,171],'Light'),([188,201],'Castellan'),([220,234],'Lancer-Archon'),([252,266],'Seraphim Frame')]:
    row={'Flyer Scout':2,'Errant Frame':3,'Black Knight':4,'Castellan':5,'Lancer-Archon':6,'Seraphim Frame':7}.get(name)
    for ref in refs:CHASSIS[f'avalon:b{ref:04}']=(name,'avalon:b0157' if name=='Light' else f'avalon:b0049:r{row}:c1')

# Additional paid/required components explicitly present in the source profile
# but omitted by the display-oriented equipment extractor.
EXTRA={
 'concord:b0347':[('Saturation Fire Protocol','concord:b0353')],
 'concord:b0358':[('Saturation Fire Protocol','concord:b0367')],
 'rebellion:b0227':[('Stable Platform','rebellion:b0241')],
 'rebellion:b0532':[('Transform','rebellion:b0537:r2:c4')],
 'avalon:b0108':[('Advance Guard','avalon:b0122')],
 'avalon:b0143':[('Advance Guard','avalon:b0150')],
 'avalon:b0077':[('Flyer','avalon:b0083')],
 'core:b0399':[('Drone Logic','core:b0405'),('Hardened Carapace','core:b0405')],
}

def weapon_component(weapon,unit):
    ref=weapon['source_ref'];quantity=1;linked=False;ambiguity=None;variant=None
    if weapon['kind']=='table-row':
        fields={header.lower():cell['text'] for header,cell in zip(weapon['columns'],weapon['cells'])}
        text=fields.get('weapon','');name=text
    else:
        text=weapon['text'];name=text
        # FP-only lines inherit the weapon name printed immediately above.
        if re.match(r'^(?:\d+[×x]\s*)?(?:FP|ME)\b',name):name=weapon.get('name_context') or name
        else:name=re.split(r'\s*[–—]\s*(?:FP|ME)|\s*\((?:FP|ME)|\s*\b(?:FP|ME)\s*\d',name,maxsplit=1)[0]
        name=re.sub(r'^(?:Right Arm|Left Arm|Center Torso):\s*','',name)
        name=re.sub(r'^[^A-Za-z0-9]+','',name)
    # Descriptive follow-on lines are not additional physical weapons.
    if text.strip().startswith(('(Each arm','(Two FP')):return None
    name=name.strip(' :–—-')
    if 'Missile' in name and 'Pod' in name:
        # 20x/6x inside a pod name is its payload, not 20 or 6 separate pods.
        name=re.sub(r'\s*\(\d+x\)','',name,flags=re.I)
    match=re.search(r'^(\d+)\s*[×x]\s*|\b(\d+)x\s+Linked|\s*[×x]\s*(\d+)\s*$|\(x(\d+)\)',name,re.I)
    if match:
        quantity=int(next(v for v in match.groups() if v));name=(name[:match.start()]+name[match.end():]).strip()
    if re.search(r'\bQuad[- ]Linked\b',name,re.I):quantity=4;linked=True;name=re.sub(r'Quad[- ]Linked\s*','',name,flags=re.I)
    elif re.search(r'\bTwin[- ]Linked\b',name,re.I):quantity=2;linked=True;name=re.sub(r'Twin[- ]Linked\s*','',name,flags=re.I)
    if 'Linked' in name:linked=True;name=re.sub(r'\bLinked\s*','',name)
    name=re.sub(r'\s*\((?:Right[^)]*|Left[^)]*|Torso|Center[^)]*|melee fallback|fallback melee|Torso-mounted|linked pods)\)','',name,flags=re.I).strip()
    name=re.sub(r'\bLasers\b','Laser',name)
    source=unit['source_refs'][0]
    # These are source-declared bundled weapons, not a guess at an unlisted price.
    overrides={
      ('rebellion:b0144','rebellion:b0152'):('Ravager Melee Laser',1,False),
      ('rebellion:b0144','rebellion:b0156'):('Ravager Laser Pods',1,False),
      ('rebellion:b0144','rebellion:b0158'):('Missile Cluster',2,True),
      ('unmc:b0171','unmc:b0182'):('VX-20C Cascade Missile Pod',2,False),
      ('unmc:b0171','unmc:b0186'):('M-55 Autocannon',1,False),
      ('unmc:b0171','unmc:b0190'):('Archon Heavy Power Fist',2,False),
    }
    if (source,ref) in overrides:name,quantity,linked=overrides[(source,ref)]
    if source=='unmc:b0061' and ref=='unmc:b0071':
        name='Micro-Missile Swarm';quantity=4
        ambiguity='The entry combines four missile swarms as FP 12 but does not specify whether they are a Linked system. Linking changes the fourth component’s price.'
    if source=='unmc:b0135' and ref=='unmc:b0147':
        name='Arm Cannon (base FP 2)';quantity=4;linked=True
        return {'name':name,'kind':'weapon','quantity':quantity,'groups':2,'linked':linked,'source_ref':ref,'variant':None,'mode':weapon.get('mode'),'ambiguity':None}
    if source=='unmc:b0154' and ref=='unmc:b0166':
        # Preserve the unpriced name. Do not equate Great Cannon with Heavy Cannon
        # merely because their numeric profiles look similar.
        name='Great Cannon';quantity=2;linked=True
    if source=='unmc:b0088' and ref=='unmc:b0099':name='Heavy Cannon Battery';quantity=2
    if source=='unmc:b0088' and ref in ('unmc:b0102','unmc:b0105'):name='Missile Pod (Hammernet FP 2)';quantity=3
    if name.startswith('Unarmed Combat (Mech Fists)'):name='Mech Fists'
    name=re.sub(r'\s*\(HALC\)','',name)
    if unit['source']['id']=='avalon':
        variant=(unit['configuration'] or '').lower() or None
        aliases={
          'Prototype Medium Laser':'Medium Laser (Scout)', 'Experimental Medium Laser':'Medium Laser+ (Scout)',
          'Prototype Beam Rapier':'Beam Rapier','Experimental Beam Rapier':'Beam Rapier+',
          'Prototype Knight Rifle':'Knight Rifle','Overcharged Rifle Prototype':'Overcharged Rifle',
          'Prototype Great Beam Claymore':'Great Beam Claymore','Experimental Great Beam Claymore':'Great Beam Claymore+',
          'Prototype Phase Dagger':'Phase Dagger','Experimental Phase Dagger':'Phase Dagger+',
          'Shield Halberd (Prototype)':'Shield Halberd','Shield Halberd Overcharger':'Shield Halberd+',
          'Prototype Beam Lance':'Beam Lance','Experimental Sun-Lance':'Sun-Lance',
          'Judicator Blade (Prototype)':'Judicator Blade','Judicator Blade Overcharger':'Judicator Blade+',
        }
        name=aliases.get(name,name)
    return {'name':name,'kind':'weapon','quantity':quantity,'groups':1,'linked':linked,
            'source_ref':ref,'variant':variant,'mode':weapon.get('mode'),'ambiguity':ambiguity}

def plan_for(unit,prices):
    namespace=unit['source']['id'];first=unit['source_refs'][0]
    chassis=CHASSIS.get(first)
    if chassis is None and unit['chassis']:
        name=unit['chassis']['text']
        name=re.split(r'\s*(?:=|\d+\s*pts|\()',name)[0].strip()
        name=re.sub(r'^(Light|Medium|Heavy|Elite) Frame$',r'\1',name,flags=re.I)
        chassis=(name,unit['chassis']['source_ref'])
    if chassis is None:
        # Explicit source breakdowns state the chassis tier for these units.
        for ref in unit['source_refs']:
            text=prices.blocks[ref].get('text','')
            match=re.search(r'(?im)^(?:Base Chassis:\s*|Chassis:\s*)?(Light|Medium|Heavy|Elite) chassis:|^(?:Chassis:\s*)(Light|Medium|Heavy|Elite)\b|^Base Chassis:\s*(Light|Medium|Heavy|Elite)\b',text)
            if match:chassis=(next(v for v in match.groups() if v),ref);break
    if unit['chassis'] is None and chassis:
        unit['chassis']={'text':chassis[0],'source_ref':chassis[1]}
    components=[{'name':chassis[0] if chassis else 'Chassis not specified','source_ref':chassis[1] if chassis else first,
                 'kind':'chassis','quantity':1,'groups':1,'linked':False,'variant':None}]
    groups=[]
    for weapon in unit['weapons']:
        component=weapon_component(weapon,unit)
        if component:groups.append(component)
    # A weapon retained in a second transformation mode is still one installed
    # component. Identical copies in the same mode/mount remain separate copies.
    seen={}
    for component in groups:
        identity=(key(component['name']),component['quantity'],component['linked'],component['variant'])
        mode=component.get('mode')
        if mode and identity in seen and mode!=seen[identity]:continue
        if mode:seen[identity]=mode
        components.append(component)
    systems=[]
    for system in unit['systems']:
        name=base_name(system['name'])
        if name in ('Sponsor Protocol','Knightly Perfection','Mech Mode','Fighter Mode') or name.startswith('Costly,'):continue
        if name.startswith('Stable Platform:'):name='Stable Platform'
        if namespace=='core' and name.startswith('Drone Logic') and ',' in name:continue
        variant=None
        if namespace=='avalon':
            aliases={'Prototype Shield Array':'Shield Array','Experimental Energy Shield':'Experimental Shield',
                     'Tower Shield Array+':'Tower Shield+','Guardian Field Projector':'Guardian Field Projector'}
            name=aliases.get(name,name)
            variant=(unit['configuration'] or '').lower() or None
        # Source calls this third-action system "Overheat"; its own cost is
        # explicit. It is not a charge for the weapon's Overheat keyword.
        systems.append({'name':name,'source_ref':system['source_ref'],'kind':'system','quantity':1,'groups':1,'linked':False,'variant':variant,
                        'optional':bool(re.search(r'\(\s*optional\b',system['description'],re.I))})
    for name,ref in EXTRA.get(first,[]):
        systems.append({'name':name,'source_ref':ref,'kind':'system','quantity':1,'groups':1,'linked':False,
                        'variant':(unit['configuration'] or '').lower() if namespace=='avalon' else None})
    # An explicit free subfaction grant is priced once at zero, not purchased
    # again using a generic optional-system price. Evidence is retained per unit.
    grants={}
    for ref in unit['source_refs']:
        for line in prices.blocks[ref].get('text','').splitlines():
            match=re.search(r'Subfaction [Tt]rait:\s*(.+?)\s*(?:=|is)?\s*free\s*\.?$',line,re.I)
            if match:grants[key(match[1])]=ref
            if 'Tracked free with Tank Mode' in line:grants['tracked']=ref
    for name,ref in grants.items():
        if not any(key(s['name'])==name for s in systems):systems.append({'name':name.title(),'source_ref':ref,'kind':'system','quantity':1,'groups':1,'linked':False,'variant':None})
    dedup=set()
    for system in systems:
        identity=key(system['name'])
        if identity in dedup:continue
        dedup.add(identity)
        if identity in grants:system.update({'granted':True,'grant_ref':grants[identity]})
        if identity=='flyer' and chassis and chassis[0]=='Flyer Scout':
            system.update({'granted':True,'grant_ref':'avalon:b0049:r2','grant_reason':'Included in the explicitly priced Flyer Scout chassis.'})
        components.append(system)
    # Standard keyword Linked describes a cost formula on the weapon, not an
    # extra independently purchased trait with another unknown price.
    components=[c for c in components if not (c['kind']=='system' and key(c['name'])=='linked')]
    return components

def calculate(components,namespace,prices):
    rows=[];missing=[];subtotal=0
    for component in components:
        row=dict(component)
        row['included']=not component.get('optional',False)
        definition=prices.find(namespace,component['kind'],component['name'],component.get('variant'))
        if component.get('granted'):
            row.update({'unit_price':0,'total':0,'price_source_ref':component['grant_ref'],
                        'price_source_id':component['grant_ref'].split(':')[0],'basis':'explicit-grant'})
        elif definition is None:
            row.update({'unit_price':None,'total':None,'price_source_ref':None,'basis':'missing-price'})
            if row['included']:missing.append(component['name'])
        elif component.get('ambiguity'):
            row.update({'unit_price':definition['unit_price'],'total':None,'price_source_ref':definition['source_ref'],
              'price_source_id':definition['source_id'],'basis':'unresolved-grouping',
              'alternatives':{'separate':definition['unit_price']*component['quantity'],'linked':linked_cost(definition['unit_price'],component['quantity'])}})
            missing.append(component['name']+' (linking needs confirmation)')
        else:
            base=definition['unit_price'];qty=component['quantity'];groups=component.get('groups',1)
            total=(linked_cost(base,qty) if component.get('linked') else base*qty)*groups
            row.update({'unit_price':base,'total':total,'price_source_ref':definition['source_ref'],
                        'price_source_id':definition['source_id'],'basis':'component-price'})
            if component.get('linked'):
                row['linked_formula_ref']='core:b0232:r18'
                row['copy_prices']=[base*(1 if i<3 else i-1) for i in range(qty)]
        if row['total'] is not None and row['included']:subtotal+=row['total']
        rows.append(row)
    return {'status':'complete' if not missing else 'incomplete','total':subtotal if not missing else None,
            'known_subtotal':subtotal,'missing_components':list(dict.fromkeys(missing)),
            'components':rows,'policy':'latest-component-prices','authorized_by':'User requested recalculation using latest component prices',
            'formula':'Chassis + all installed weapons + paid systems and traits; explicit grants once; linked escalation per core v0.0.14.'}

def reprice(units):
    prices=Prices()
    report=[]
    for unit in units:
        calculation=calculate(plan_for(unit,prices),unit['source']['id'],prices)
        unit['points']['calculation']=calculation
        unit['points']['filter_value']=calculation['total']
        unit['points']['approximate']=False # The active total is arithmetic, not the approximate stock heading.
        # Preserve literal source observations, but do not keep obsolete
        # stock-vs-components warnings after the user authorizes recalculation.
        unit['review_notes']=[note for note in unit['review_notes'] if 'quick-reference' in note]
        if unit['source_refs'][0]=='unmc:b0061':
            unit['review_notes'].append('The mode table says Mech Mode has the Rail Carbine only, while the equipment list also gives it a Plasma Blade. The missile grouping also needs confirmation.')
        if unit['source_refs'][0]=='rebellion:b0532':
            unit['review_notes'].append('Transform is listed in the source profile, but no alternate form is defined. Its current component price is included in this calculation.')
        report.append({'id':unit['id'],'name':unit['name'],'source_ref':unit['source_refs'][0],
            'original_totals':unit['points']['observations'],'calculation':calculation})
    export={'schema_version':1,'policy':'latest-component-prices','core_rules_version':'0.0.14',
            'price_definitions':list(prices.entries.values()),'units':report}
    (ROOT/'iron-stars/data/pricing.json').write_text(json.dumps(export,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    complete=[row for row in report if row['calculation']['total'] is not None]
    changed=[row for row in complete if row['original_totals'] and row['original_totals'][0]['value']!=row['calculation']['total']]
    lines=['# Iron Stars component cost recalculation','',
      'The user authorized replacing stock totals with calculations from the latest matching component prices. Original DOCX files and printed totals are unchanged.','',
      f'{len(complete)} complete calculations; {len(report)-len(complete)} incomplete calculations; {len(changed)} complete totals differ from their source heading.','',
      '## Pricing policy','',
      '- Core v0.0.14 prices override matching shared components in earlier sources.',
      '- Distinct named faction and Prototype/Experimental components use their specific prices. Similar-looking weapons are not silently equated.',
      '- Dedicated component price lists are preferred over copied per-unit prices in the same source; explicit unique-component prices fill gaps.',
      '- Generic chassis tiers use current core prices. Specifically named frames retain their own priced identity.',
      '- Linked copies cost base/base/base/2×base/3×base/etc.; independent linked groups are priced separately.',
      '- A component retained across transformation modes is charged once. Different installed components remain separate costs.',
      '- Explicit free subfaction grants and included chassis features are not bought twice. Optional upgrades are separate from the base cost.',
      '- Unknown prices and unclear linking never become zero or a remainder inferred from an old stock total.',
      '- Components present in the profile are included even if omitted from the old breakdown, e.g. Brood-Lord Transform.',
      '- Sponsor Protocol and universal Knightly Perfection are excluded as previously directed.','',
      '## Results','', '| Unit | Original source totals | Current total | Known subtotal | Missing prices or details |',
      '| --- | --- | --- | --- | --- |']
    missing=Counter()
    for row in report:
        calc=row['calculation'];old=', '.join(dict.fromkeys(v['text'] for v in row['original_totals'])) or 'Not specified'
        current=str(calc['total']) if calc['total'] is not None else 'Incomplete'
        lines.append('| '+row['name'].replace('|','/')+' | '+old+' | '+current+' | '+str(calc['known_subtotal'])+' | '+', '.join(calc['missing_components'])+' |')
        missing.update(calc['missing_components'])
    lines.extend(['','## Missing component prices and construction details','',
                  '| Component or detail | Profiles affected |','| --- | --- |'])
    lines.extend(f'| {name} | {count} |' for name,count in sorted(missing.items()))
    lines.extend(['','## Reproduce and verify','',
      'Run `py -B iron-stars-tools/build.py`, `py -B iron-stars-tools/test_pricing.py`, and `py -B iron-stars-tools/verify_units.py` from the repository root. The build regenerates this report and `iron-stars/data/pricing.json`, which records every component, quantity, formula, grant, and source reference. Each unit page has a Point calculation table.',
      '', 'Cost recalculation does not decide which of two conflicting loadouts is current, invent future faction rosters, or authorize production deployment.'])
    (ROOT/'iron-stars-review/RECALCULATED-COSTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return export
