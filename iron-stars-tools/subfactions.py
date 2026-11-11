"""Roster affiliations and traits from the latest core, with no legacy mechanics."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GROUPS={
 'iron-concord':('House',[332,336,340,344]),
 'unmc':('Megacorporation',[434,438,442,446]),
 'cybernetic-rebellion':('Machine Hive',[382,386,390,394]),
 'new-avalon':('Knightly Order',[287,291,295,299]),
 'fourth-imperium':('Imperial Arm',[487,491,495,499]),
 'living-dominion':('Wild Host',[548,551,554,557]),
 'southern-cross-compact':('Subfaction',[]),
}

def affiliations():
    doc=json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
    blocks={b['id']:b for b in doc['blocks']}
    def rule(n):
        b=blocks[f'core:b{n:04}'];return {'text':b['text'].strip(),'source_ref':b['id']}
    result={}
    for faction,(label,starts) in GROUPS.items():
        groups=[]
        for n in starts:
            name=rule(n)['text']
            details=[rule(i) for i in range(n+1,n+(3 if faction=='living-dominion' else 4))]
            trait=next((r for r in details if r['text'].startswith('Trait:')),None)
            if trait:
                trait={**trait,'name':re.split(r'\s+[–—]\s+',trait['text'].removeprefix('Trait:').strip(),maxsplit=1)[0]}
            groups.append({'id':re.sub('[^a-z0-9]+','-',name.lower()).strip('-'),'name':name,
                           'source_ref':rule(n)['source_ref'],'description':[d for d in details if not d['text'].startswith('Trait:')],
                           'trait':trait})
        shared=[]
        if faction=='living-dominion':shared=[{'name':'Renewal of Flesh',**rule(544)}]
        elif faction=='southern-cross-compact':
            shared=[{'name':'Field Expedients','text':'\n'.join(rule(n)['text'] for n in range(601,609) if rule(n)['text']),
                     'source_refs':[rule(n)['source_ref'] for n in range(601,609)]}]
        result[faction]={'affiliation_label':label,'subfactions':groups,'shared_traits':shared,
                         'affiliation_note':rule(547) if faction=='living-dominion' else None}
    return result
