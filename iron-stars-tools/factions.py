"""Source-driven faction encyclopedia. No inferred costs, stats, or heraldry."""
from html import escape
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SUBFACTION_HEADINGS={f'core:b{n:04}' for n in [287,291,295,299,332,336,340,344,382,386,390,394,434,438,442,446]}
# Ranges are editorial grouping only. Every paragraph retains its source wording.
FACTIONS=[
 {'id':'iron-concord','name':'Iron Concord','code':'IC','accent':'#e49a76','doc':'concord','quote':313,'overview':[316,317],'philosophy':[320,323],'doctrine':[326,329],'subfactions':[331,347],'summary':356,'example':[349,353],'extra':[358,361],'supplements':[],'note':None},
 {'id':'unmc','name':'United Nations Megacorporations (UNMC)','code':'UN','accent':'#8abde0','doc':'unmc','quote':415,'overview':[418,419],'philosophy':[422,425],'doctrine':[428,431],'subfactions':[433,449],'summary':460,'example':[451,457],'extra':[462,465],'supplements':[],'note':None},
 {'id':'cybernetic-rebellion','name':'Cybernetic Rebellion','code':'CR','accent':'#7ec8bf','doc':'rebellion','quote':363,'overview':[366,367],'philosophy':[370,373],'doctrine':[376,379],'subfactions':[381,397],'summary':408,'example':[399,405],'extra':[410,413],'supplements':[],'note':None},
 {'id':'new-avalon','name':'New Avalon','code':'NA','accent':'#b3b2e3','doc':'avalon','quote':268,'overview':[271,272],'philosophy':[275,278],'doctrine':[281,284],'subfactions':[286,302],'summary':311,'example':[304,308],'extra':None,'supplements':[],'note':None},
 {'id':'fourth-imperium','name':'Fourth Imperium','code':'IV','accent':'#d9bb77','doc':None,'quote':468,'overview':[470,472],'philosophy':[475,478],'doctrine':[481,484],'subfactions':[486,502],'summary':515,'example':[504,512],'extra':[517,521],'supplements':[],'note':None},
 {'id':'living-dominion','name':'Living Dominion','code':'LD','accent':'#a5c57d','doc':None,'quote':524,'overview':[526,529],'philosophy':[532,535],'doctrine':[538,541],'subfactions':[546,559],'summary':572,'example':[561,569],'extra':[574,577],'supplements':[],'core_rules':[[543,544]],'note':None},
 {'id':'southern-cross-compact','name':'Southern Cross Compact','code':'SC','accent':'#e0ac77','doc':None,'quote':580,'overview':[582,586],'philosophy':[589,592],'doctrine':[595,598],'subfactions':None,'summary':665,'example':None,'extra':[667,674],'supplements':[],'core_rules':[[600,662]],'note':'The Compact uses imported stock mechs rather than a native roster. The source gives no formal subfaction list. Chassis-tier tax mappings and eligibility of House/Order-exclusive imports still need confirmation; no eligible-unit list or replacement costs have been guessed.'},
]


def select_data():
    docs={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'iron-stars-source/extracted').glob('*.json')}
    evidence=json.loads((ROOT/'iron-stars-review/source-precedence.json').read_text(encoding='utf-8'))['evidence']
    for key,doc in docs.items():
        digest=hashlib.sha256((ROOT/'iron-stars-source/originals'/doc['filename']).read_bytes()).hexdigest()
        assert digest==doc['sha256']==next(e['sha256'] for e in evidence if e['source_id']==key),'Source changed; review before rebuilding'
    def span(key,bounds):
        return [b for b in docs[key]['blocks'] if bounds[0]<=int(b['id'].split(':b')[1])<=bounds[1]] if bounds else []
    units=json.loads((ROOT/'iron-stars-source/content/unverified/units.json').read_text(encoding='utf-8'))['records']
    result=[]
    for config in FACTIONS:
        record={k:v for k,v in config.items() if k not in ['overview','philosophy','doctrine','subfactions','summary','example','extra','supplements','core_rules','quote']}
        record.update({'status':'alpha-source-reference','finalized':False,'source_version':'0.0.14',
          'development_status':'in-development' if config['id'] in ('fourth-imperium','living-dominion') else 'source-reference',
          'quote':span('core',[config['quote'],config['quote']])[0],
          'sections':{name:span('core',config.get(name)) for name in ['overview','philosophy','doctrine','subfactions','example','extra']},
          'playstyle':span('core',[config['summary'],config['summary']])[0],
          'rules':span('core',config.get('core_rules',[None])[0]) if config.get('core_rules') else [],
          'supplements':[{'source_id':config['doc'],'filename':docs[config['doc']]['filename'],'blocks':span(config['doc'],bounds)} for bounds in config['supplements']],
          'roster':[],
          'additional_rule_rows':[],
          'source_documents':[{'id':key,'filename':docs[key]['filename'],'sha256':docs[key]['sha256']} for key in ['core']+([config['doc']] if config['doc'] else [])]})
        for unit in units:
            if unit['source_id']!=config['doc'] or unit['record_type']!='roster-entry': continue
            first=next(b['text'].strip() for b in unit['source_blocks'] if b.get('text','').strip())
            if first.endswith(('Sentinels Unit','Swarm Synod Unit')):
                first=next(b['text'].strip() for b in unit['source_blocks'][1:] if b.get('text','').strip())
            first=first.split('\n')[0]
            name=re.sub(r'\s*[—–-]\s*~?\s*\d+\s*pts.*$','',first,flags=re.I)
            name=re.sub(r'\s+\d+\s*pts.*$','',name,flags=re.I)
            name=re.sub(r'^[^A-Za-z0-9]+','',name)
            record['roster'].append({'name':name,'source_ref':unit['source_refs'][0],'source_id':unit['source_id'],'status':'profile-and-cost-review-pending'})
        result.append(record)
    data={'schema_version':1,'status':'alpha-source-reference','finalized':False,'version':'0.0.14',
          'palette_note':'Website accents and abstract artwork placeholders are editorial design, not official faction heraldry.', 'factions':result}
    out=ROOT/'iron-stars/data/factions.json'; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data


def source_html(blocks):
    output=[]
    for block in blocks:
        if block['kind']!='paragraph' or not block.get('text','').strip(): continue
        text=escape(block['text']).replace('\n','<br>')
        # Source heading levels vary between faction profiles; use a consistent
        # semantic hierarchy without editing their heading wording.
        tag='h3' if block.get('style','').startswith('heading') or block['id'] in SUBFACTION_HEADINGS else 'p'
        output.append(f'<{tag} data-source-ref="{block["id"]}">{text}</{tag}>')
    return ''.join(output)


def summary_values(faction):
    return {r['cells'][0]['text']:r['cells'][1]['text'] for r in faction['playstyle']['rows'][1:]}


def index_content(data):
    cards=[]
    for i,faction in enumerate(data['factions'],1):
        values=summary_values(faction)
        coverage='Faction in development · current core profile available' if faction['development_status']=='in-development' else 'Faction roster supplied · profiles under review' if faction['doc'] else 'Imported stock units · eligibility under review'
        cards.append(f'''<a class="faction-card" href="{faction['id']}/index.html" style="--faction-accent:{faction['accent']}"><span class="faction-card-top"><span>{i:02} / {faction['code']}</span><span aria-hidden="true">↗</span></span><h2>{escape(faction['name'])}</h2><p>{escape(values['Role'])}</p><dl><dt>Strengths</dt><dd>{escape(values['Strengths'])}</dd><dt>Weaknesses</dt><dd>{escape(values['Weaknesses'])}</dd></dl><span class="roster-status">{coverage}</span></a>''')
    return f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span aria-hidden="true">/</span><span aria-current="page">Factions</span></nav><section class="faction-index-intro"><p class="eyebrow">THE POWERS / FACTION ENCYCLOPEDIA</p><h1 id="title">Choose your allegiance.</h1><p class="lead">Seven factions. Explore their beliefs, battlefield doctrines, and the forces that shape their wars.</p><p class="faction-status">Core v0.0.14 · Alpha source reference</p></section><div class="faction-grid">{''.join(cards)}</div><aside class="faction-reference-note"><h2>Reading the faction profiles</h2><p>Faction descriptions and gameplay text use core rules v0.0.14. The supplied faction documents provide the separate roster name indexes. Rule descriptions remain source wording, with review notes where details are incomplete. Website accent colours and abstract placeholders are not official heraldry.</p><a class="text-link" href="../rules/index.html">Open the core rulebook ↗</a></aside>'''


def detail_content(faction, unit_links=None):
    f=faction; values=summary_values(f)
    toc=[('overview','Background'),('philosophy','Ideology'),('doctrine','Doctrine'),('playstyle','Playstyle'),('subfactions','Subfactions'),('faction-rules','Faction rules'),('roster','Unit roster')]
    nav=''.join(f'<a href="#{ident}">{name}</a>' for ident,name in toc)
    parts=[f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../index.html">Iron Stars</a><span aria-hidden="true">/</span><a href="../index.html">Factions</a><span aria-hidden="true">/</span><span aria-current="page">{escape(f['name'])}</span></nav><section class="faction-hero"><div><p class="eyebrow">FACTION DOSSIER / {f['code']}</p><h1 id="title">{escape(f['name'])}</h1><blockquote data-source-ref="{f['quote']['id']}">{escape(f['quote']['text'])}</blockquote><p class="faction-status">Core v0.0.14 · Alpha source reference</p><a class="button" href="#roster">Explore the roster <span aria-hidden="true">↓</span></a></div><div class="faction-art" role="img" aria-label="Abstract artwork placeholder for {escape(f['name'],quote=True)}"><span class="art-label">FACTION ARTWORK / RESERVED</span><span class="faction-monogram" aria-hidden="true">{f['code']}</span><span class="art-caption">Abstract placeholder · no official insignia</span></div></section><nav class="faction-sections" aria-label="On this faction page">{nav}</nav><div class="faction-profile">''']
    if f['development_status']=='in-development':
        parts.append('<aside class="faction-reference-note"><h2>Faction in development</h2><p>This page presents all currently available material for this faction. Its full army list, unit profiles, and point costs are still being developed.</p></aside>')
    for ident,title in toc[:3]:
        parts.append(f'<section id="{ident}" aria-labelledby="{ident}-title"><p class="eyebrow">{title}</p><h2 id="{ident}-title">'+{'overview':'Background','philosophy':'Beliefs & society','doctrine':'Military doctrine'}[ident]+'</h2>'+source_html(f['sections'][ident])+'</section>')
    parts.append('<section id="playstyle" aria-labelledby="playstyle-title"><p class="eyebrow">On the tabletop</p><h2 id="playstyle-title">Strengths & weaknesses</h2><dl class="playstyle-grid">')
    for row in f['playstyle']['rows'][1:]:
        parts.append(f'<div data-source-row="{row["id"]}"><dt>{escape(row["cells"][0]["text"])}</dt><dd>{escape(row["cells"][1]["text"])}</dd></div>')
    parts.append('</dl></section><section id="subfactions" aria-labelledby="subfactions-title"><p class="eyebrow">Within the faction</p><h2 id="subfactions-title">Subfactions</h2>')
    parts.append(source_html(f['sections']['subfactions']) if f['sections']['subfactions'] else '<p>The supplied core describes mercenary companies as an optional narrative choice, rather than a list of formal subfactions with separate traits.</p>')
    parts.append('</section><section id="faction-rules" aria-labelledby="faction-rules-title"><p class="eyebrow">Source rules / Alpha reference</p><h2 id="faction-rules-title">Faction rules</h2>')
    if f['rules']: parts.append(source_html(f['rules']))
    elif f['id']=='cybernetic-rebellion': parts.append('<p>The core describes morale immunity in the doctrine above and rules for individual machine hives in the subfaction section. It does not give a separate named universal faction rule.</p>')
    elif f['id']=='fourth-imperium': parts.append('<p>The core supplies the Imperial Arm traits above. A separate universal faction rule is not specified.</p>')
    else: parts.append('<p>The faction’s rules and subfaction traits from core v0.0.14 are shown above.</p>')
    for supplement in f['supplements']:
        parts.append(f'<div class="supplement"><p class="source-label">Additional source: {escape(supplement["filename"])}</p>{source_html(supplement["blocks"])}</div>')
    if f['note']:
        parts.append(f'<aside class="faction-review"><strong>Needs clarification</strong><p>{escape(f["note"])}</p></aside>')
    parts.append('<a class="text-link" href="../../rules/index.html#glossary">Read shared keyword definitions ↗</a></section>')
    parts.append('<section id="roster" aria-labelledby="roster-title"><p class="eyebrow">Forces & availability</p><h2 id="roster-title">Unit roster</h2>')
    if f['roster']:
        parts.append('<p class="roster-notice">Source roster · Open a unit to view its profile, loadout, and any source review notes.</p><ul class="roster-list">')
        for u in f['roster']:
            unit_id=(unit_links or {}).get(u['source_ref'])
            name=f'<a href="../../units/{unit_id}/index.html">{escape(u["name"])} ↗</a>' if unit_id else escape(u['name'])
            parts.append(f'<li data-roster-ref="{u["source_ref"]}">{name}</li>')
        parts.append('</ul>')
    elif f['id']=='southern-cross-compact':
        parts.append('<p class="roster-notice">Imported stock roster · No eligible-unit list has been finalized.</p><p>The core permits eligible non-Hero, non-Unique stock mechs from Iron Concord, UNMC, and New Avalon. Cybernetic Rebellion imports are forbidden. Read the full procurement restrictions and import taxes above.</p><div class="roster-sources"><a href="../iron-concord/index.html#roster">Iron Concord roster ↗</a><a href="../unmc/index.html#roster">UNMC roster ↗</a><a href="../new-avalon/index.html#roster">New Avalon roster ↗</a></div>')
    else:
        parts.append('<p class="roster-notice">Roster in development · The core example below is all the unit material currently available. Full profiles and point costs have not yet been developed.</p>')
    if f['sections']['example']:
        parts.append('<details class="unit-example"><summary>Unit example from the core rules</summary>'+source_html(f['sections']['example'])+'</details>')
    parts.append(f'<a class="text-link" href="../../units/index.html#{f["id"]}">Browse this faction in the unit database ↗</a></section>')
    if f['sections']['extra']:
        parts.append('<section class="faction-extra" aria-label="More from the core profile">'+source_html(f['sections']['extra'])+'</section>')
    sources=''.join(f'<li>{escape(s["filename"])}</li>' for s in f['source_documents'])
    parts.append(f'<section class="faction-sources"><h2>Sources</h2><ul>{sources}</ul><p>Faction descriptions and gameplay text use core v0.0.14. Faction documents are used only for the roster name indexes on these pages. Unresolved rules are reference material, not finalized army-building decisions.</p><a class="text-link" href="../index.html">← All seven factions</a></section></div>')
    return ''.join(parts)


def render_factions(unit_links=None):
    data=select_data()
    pages=[{'slug':'factions','name':'Factions','content':index_content(data),'accent':'#f2944a','description':'Explore the seven IRON STARS factions, their backgrounds, doctrines, subfactions, and roster availability.'}]
    for faction in data['factions']:
        pages.append({'slug':'factions/'+faction['id'],'name':faction['name'],'content':detail_content(faction,unit_links),
                      'accent':faction['accent'],'description':summary_values(faction)['Role']+' — faction background, subfactions, and source rules for IRON STARS.'})
    return pages
