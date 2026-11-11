"""Organize private source observations; never resolve conflicts or publish rules."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'iron-stars-source'
CONTENT = SOURCE / 'content'
CATEGORIES = ('core-rules', 'terminology-keywords', 'factions', 'subfactions',
              'units', 'chassis', 'weapons', 'systems-traits', 'point-costs', 'missions', 'universe')
DOCS = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in (SOURCE/'extracted').glob('*.json')}
CAT = {key: [] for key in CATEGORIES}


def blocks(key, start, end):
    return [b for b in DOCS[key]['blocks'] if start <= int(b['id'].split(':b')[1]) <= end]


def observe(category, key, start, end, label=None, **extra):
    selected = blocks(key, start, end)
    record = {
        'id': f'{category}:{key}:{start:04}-{end:04}',
        'label': label or selected[0].get('text', '').strip(),
        'source_id': key, 'source_filename': DOCS[key]['filename'],
        'source_sha256': DOCS[key]['sha256'],
        'rules_version': '0.0.14' if key == 'core' else None,
        'version_basis': 'User identification and supplied filename; body says ALPHA' if key == 'core' else 'Not stated; filename copy suffix is not a version',
        'review_status': 'unverified', 'publication_status': 'private',
        'source_refs': [b['id'] for b in selected],
        'source_blocks': selected,
        **extra,
    }
    CAT[category].append(record)
    return record


def table_rows(category, key, number):
    table = blocks(key, number, number)[0]
    headers = [c['text'] for c in table['rows'][0]['cells']]
    for row in table['rows'][1:]:
        values = [c['text'] for c in row['cells']]
        if all(not v.strip() or v.strip() in ('---', '—', '–') for v in values):
            continue
        record = observe(category, key, number, number, values[0] or '(unnamed source row)', record_type='table-row')
        record['id'] += ':' + row['id'].rsplit(':', 1)[1]
        record['source_refs'] = [row['id']]
        record['source_blocks'] = [row]
        record['columns_as_written'] = headers
        record['values_as_written'] = values


# Chapters follow source heading boundaries; wording is never rewritten.
core = DOCS['core']['blocks']
starts = [int(b['id'].split(':b')[1]) for b in core if b.get('style') == 'heading 2' and int(b['id'].split(':b')[1]) < 266]
for i, start in enumerate(starts):
    end = (starts[i+1]-1) if i+1 < len(starts) else 265
    observe('core-rules', 'core', start, end, record_type='source-chapter')
observe('universe', 'core', 1, 9, 'Opening setting overview')
observe('universe', 'core', 676, 716, 'History of Iron Stars (source spelling retained in text)')
observe('missions', 'core', 253, 265, 'Secure the Relay')
observe('terminology-keywords', 'core', 40, 46, 'Unit stat terminology')
for table in [84, 232, 235, 238]:
    table_rows('terminology-keywords', 'core', table)

factions = [
    ('new-avalon', 'New Avalon', 267, 311, 'avalon', 1, 59),
    ('iron-concord', 'Iron Concord', 312, 361, 'concord', 1, 33),
    ('cybernetic-rebellion', 'Cybernetic Rebellion', 362, 413, 'rebellion', 1, 46),
    ('unmc', 'United Nations Megacorporations (UNMC)', 414, 465, 'unmc', 1, 45),
    ('fourth-imperium', 'Fourth Imperium', 467, 521, None, None, None),
    ('living-dominion', 'Living Dominion', 523, 577, None, None, None),
    ('southern-cross-compact', 'Southern Cross Compact', 579, 674, None, None, None),
]
for faction_id, name, start, end, doc, ds, de in factions:
    record = observe('factions', 'core', start, end, name, faction_id=faction_id,
                     coverage='Core profile and dedicated faction document' if doc else 'Core profile only; no dedicated faction roster supplied')
    if doc:
        observe('factions', doc, ds, de, name, faction_id=faction_id, record_type='faction-supplement')

subranges = {
    'core': [(287,290),(291,294),(295,298),(299,302),(332,335),(336,339),(340,343),(344,347),
             (382,385),(386,389),(390,393),(394,397),(434,437),(438,441),(442,445),(446,449),
             (487,490),(491,494),(495,498),(499,502),(548,550),(551,553),(554,556),(557,559)],
    'concord': [(14,14),(15,15),(16,16),(17,17)],
    'unmc': [(20,21),(22,23),(24,25),(26,27)],
    'avalon': [(25,25),(26,26),(27,27),(28,28)],
    'rebellion': [(21,21),(22,22),(23,23),(24,24),(300,302),(569,570)],
}
for key, ranges in subranges.items():
    for start, end in ranges:
        observe('subfactions', key, start, end, record_type='source-mention')

unit_ranges = {
    'core': [(205,210),(212,218),(220,226),(304,308),(349,353),(399,405),(451,457),(504,512),(561,569)],
    'concord': [(35,38),(39,42),(43,46),(47,68),(70,74),(75,79),(80,84),
                (89,108),(109,129),(130,147),(150,170),(171,188),(189,209),
                (211,236),(237,257),(258,280),(281,302),(303,329),(332,346),(347,357),(358,371)],
    'unmc': [(46,60),(61,87),(88,113),(114,133),(135,153),(154,169),(171,198)],
    'rebellion': [(49,73),(75,89),(91,108),(110,124),(126,141),(144,180),(182,225),(227,262),(264,298),
                  (303,333),(336,369),(371,404),(406,440),(444,470),(472,498),(500,530),(532,567),
                  (571,599),(601,629),(631,663),(665,693)],
    'avalon': [(65,75),(77,88),(92,106),(108,125),(130,141),(143,154),(159,169),
               (171,183),(188,199),(201,215),(220,232),(234,247),(252,264),(266,280)],
}
for key, ranges in unit_ranges.items():
    for start, end in ranges:
        record = observe('units', key, start, end, record_type='core-example' if key=='core' else 'roster-entry')
        record['cost_observations'] = []
        record['profile_observations'] = []
        for b in record['source_blocks']:
            value = b.get('text', '')
            if re.search(r'\d+\s*pts?\b', value, re.I):
                record['cost_observations'].append({'source_ref': b['id'], 'text_as_written': value})
            if re.search(r'\b(?:M:|Move:|Defence\s*:|D:|STR:|Chassis:|Structure:)', value, re.I) or b['kind']=='table':
                record['profile_observations'].append({'source_ref': b['id'], 'source_block': b})
        # Never choose a cost or profile from multiple observations automatically.
        record['approved_point_cost'] = None
        record['approved_profile'] = None

for key, ranges in {
    'rebellion': [(697,703),(705,711),(713,718),(720,726),(728,733)],
    'avalon': [(285,288),(289,292),(296,299),(300,303),(307,310),(311,314),(318,321),
               (322,325),(329,332),(333,336),(340,343),(344,347),(351,354),(355,358)]
}.items():
    for start, end in ranges:
        observe('units', key, start, end, record_type='quick-reference-variant', approved_point_cost=None, approved_profile=None)

for start,end,name in [(106,106,'Light Drone (spawned)'),(202,203,'Sky Reaver'),(204,206,'Blade Runner'),
                       (207,208,'Beamling'),(458,458,'Drone-Swarm Fragment'),(486,486,'Burrower Fragment'),
                       (517,517,'Swarm Fragment Drone (Hive-Crusher)'),(548,548,'Swarm Fragment Drone (Brood-Lord reference only)'),
                       (553,556,'Broodling Drone')]:
    observe('units','rebellion',start,end,name,record_type='spawned-unit-observation',approved_point_cost=None,approved_profile=None)

for key, numbers in {'core':[187], 'concord':[28], 'unmc':[35], 'rebellion':[30], 'avalon':[49]}.items():
    for number in numbers:
        table_rows('chassis',key,number)
for key, numbers in {'core':[192,194], 'concord':[30], 'unmc':[40,42], 'rebellion':[35,37], 'avalon':[52,55]}.items():
    for number in numbers:
        table_rows('weapons',key,number)
observe('weapons','concord',31,31,'Iron Concord melee weapon price list',record_type='inline-price-list')
for key, numbers in {'core':[197,235], 'concord':[33], 'unmc':[45], 'rebellion':[41], 'avalon':[58]}.items():
    for number in numbers:
        table_rows('systems-traits',key,number)

# Preserve unit-specific weapon/system wording as separate observations. A reused
# name is not evidence that two profiles have identical costs or effects.
for key, ranges in unit_ranges.items():
    for start,end in ranges:
        for b in blocks(key,start,end):
            text = b.get('text','')
            if b['kind']=='table':
                headers = ' '.join(c['text'] for c in b['rows'][0]['cells']).lower()
                category = 'weapons' if 'weapon' in headers else 'systems-traits' if any(t in headers for t in ('effect','trait','system')) and not any(t in headers for t in ('str','mode','base stats')) else None
                if category:
                    table_rows(category,key,int(b['id'].split(':b')[1]))
            elif re.search(r'\b(?:FP|ME)\s*\d',text):
                observe('weapons',key,int(b['id'].split(':b')[1]),int(b['id'].split(':b')[1]),record_type='unit-observation')
            elif re.search(r'\S.+\s[–—:]\s*\S',text) and not text.startswith(('Role:','Chassis:','Traits:','M:','Move:','Total','Cost','Drawback','Strengths','Weaknesses','Subfaction trait:','Subfaction Trait:')):
                observe('systems-traits',key,int(b['id'].split(':b')[1]),int(b['id'].split(':b')[1]),record_type='candidate-unit-rule', classification_status='Review classification; literal source text preserved')

for key,doc in DOCS.items():
    for b in doc['blocks']:
        if b['kind']=='table':
            for row in b['rows'][1:]:
                if any(re.search(r'\d+\s*pts?\b',c['text'],re.I) for c in row['cells']):
                    record=observe('point-costs',key,int(b['id'].split(':b')[1]),int(b['id'].split(':b')[1]),row['cells'][0]['text'],record_type='price-row')
                    record['id']+=':'+row['id'].rsplit(':',1)[1]
                    record['source_refs']=[row['id']]; record['source_blocks']=[row]
        elif re.search(r'\d+\s*pts?\b',b.get('text',''),re.I):
            observe('point-costs',key,int(b['id'].split(':b')[1]),int(b['id'].split(':b')[1]),record_type='cost-mention')

def main():
    for state in ['unverified','approved']:
        out=CONTENT/state; out.mkdir(parents=True,exist_ok=True)
        for category, records in CAT.items():
            data={'schema_version':1,'category':category,'review_status':state,
                  'publication_status':'private','records':records if state=='unverified' else []}
            target=out/(category+'.json')
            # Human approvals are a separate manual action; never overwrite them.
            if state=='approved' and target.exists():
                continue
            target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:len(v) for k,v in CAT.items()}
    (CONTENT/'inventory.json').write_text(json.dumps({'schema_version':1,'counts':summary,
        'approved_records':0,'note':'Counts represent source observations, not deduplicated canonical game entities.'},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':
    main()
