"""Build a source-traceable armory using the unit calculator's price resolver."""
from pathlib import Path
from html import escape
import json
from pricing import Prices, key, base_name

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'core':'Core components', 'concord':'Iron Concord', 'unmc':'UNMC',
          'rebellion':'Cybernetic Rebellion', 'avalon':'New Avalon'}

def compile_armory():
    prices = Prices()
    units = json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))['units']
    records = {}
    def add(namespace, kind, name, variant, ref):
        name = base_name(name)
        definition = prices.find(namespace, kind, name, variant)
        origin = definition['source_id'] if definition else namespace
        variant = definition['variant'] if definition else variant
        identity = (origin, kind, key(base_name(definition['name']) if definition else name), variant)
        if identity not in records:
            source_ref = definition['source_ref'] if definition else ref
            block = prices.blocks[source_ref.split(':r')[0]]
            details = []
            if block['kind'] == 'table':
                row_id = source_ref.rsplit(':c', 1)[0]
                row = next((r for r in block['rows'] if r['id'] == row_id), None)
                if row:
                    details = [{'label':h['text'], 'text':c['text'], 'source_ref':c['id']}
                               for h,c in zip(block['rows'][0]['cells'],row['cells'])
                               if 'cost' not in h['text'].lower() and c != row['cells'][0]]
            elif definition:
                text = block['text']
                if block['id']=='concord:b0031':
                    text = next(line for line in text.splitlines() if key(line.split('|')[0])==key(name))
                details = [{'label':'Source entry', 'text':text, 'source_ref':block['id']}]
            if key(name)=='iron will':
                latest = next(b for b in prices.docs['core']['blocks'] if 'Trait: Iron Will' in b.get('text',''))
                details = [{'label':'Core rule', 'text':latest['text'], 'source_ref':latest['id']}]
            records[identity] = {'id':f'component-{len(records)+1}', 'name':definition['name'] if definition else name,
                'kind':kind, 'variant':variant, 'source_id':origin, 'source_label':LABELS[origin],
                'price':definition['unit_price'] if definition else None, 'source_ref':source_ref,
                'source_filename':prices.docs[origin]['filename'], 'source_sha256':prices.docs[origin]['sha256'],
                'details':details, 'used_by':[]}
        return records[identity]
    for (namespace,kind,name,variant), definition in prices.entries.items():
        add(namespace,kind,definition['name'],variant,definition['source_ref'])
    for unit in units:
        for component in unit['points']['calculation']['components']:
            if component.get('basis') not in ('component-price','missing-price'): continue
            if component['name'] in ('Chassis not specified','Backup Conversion Mode'): continue
            entry = add(unit['source']['id'],component['kind'],component['name'],component.get('variant'),component['source_ref'])
            if unit['id'] not in [u['id'] for u in entry['used_by']]:
                entry['used_by'].append({'id':unit['id'],'name':unit['name']})
    result = {'core_rules_version':'0.0.14','status':'beta','components':sorted(records.values(),key=lambda r:(r['name'].casefold(),r['source_id'],r['variant'] or ''))}
    (ROOT/'iron-stars/data/armory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def render_armory():
    data = compile_armory()
    cards = []
    for r in data['components']:
        title = r['name'] + (' — '+r['variant'].title() if r['variant'] else '')
        price = str(r['price'])+(' pt' if r['price']==1 else ' pts') if r['price'] is not None else 'Price not specified'
        details = ''.join(f'<dt>{escape(d["label"])}</dt><dd>{escape(d["text"]).replace(chr(10),"<br>")}</dd>' for d in r['details'])
        uses = ''.join(f'<li><a href="../units/{u["id"]}/index.html">{escape(u["name"])}</a></li>' for u in r['used_by'])
        source = f'<p class="small-note">{escape(r["source_filename"])}<br>Reference: {escape(r["source_ref"])}</p>'
        rule = '<a href="../rules/index.html#rule-'+r['source_ref'].split(':c')[0].replace(':','-')+'">Read core rule ↗</a>' if r['source_id']=='core' and ':r' in r['source_ref'] else ''
        cards.append(f'<article class="armory-card" id="{r["id"]}" data-kind="{r["kind"]}" data-source="{r["source_id"]}" data-priced="{str(r["price"] is not None).lower()}"><div class="armory-meta"><span>{escape(r["source_label"])} / {r["kind"].title()}</span><strong>{price}</strong></div><h2>{escape(title)}</h2><dl>{details}</dl>{rule}<details><summary>Source and unit references</summary>{source}'+(f'<ul>{uses}</ul>' if uses else '<p>No linked premade profile.</p>')+'</details></article>')
    options = ''.join(f'<option value="{k}">{v}</option>' for k,v in LABELS.items())
    return '''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span>/</span><span aria-current="page">Armory</span></nav>
<section class="section-intro"><p class="eyebrow">IRON STARS / Equipment reference</p><h1>Armory</h1><p class="lead">Find weapons, systems, and chassis. Equip your force with the latest available component prices.</p><p class="small-note">Beta · Core v0.0.14 prices take precedence for matching components. Distinct faction and Prototype/Experimental components retain their specific prices. Source labels identify the document, not an equipment permission. Premades pay the full component cost.</p></section>
<form class="armory-filters" id="armory-filters" role="search" aria-label="Filter armory"><label>Search equipment<input id="armory-search" type="search" placeholder="Try laser, shield, or Heavy…"></label><label>Component type<select id="armory-kind"><option value="">All types</option><option value="weapon">Weapons</option><option value="system">Systems &amp; traits</option><option value="chassis">Chassis</option></select></label><label>Component source<select id="armory-source"><option value="">All sources</option>'''+options+'''</select></label><label>Price availability<select id="armory-priced"><option value="">All entries</option><option value="true">Price available</option><option value="false">Price not specified</option></select></label><button class="button" type="reset">Reset filters</button></form>
<p class="small-note">Prices are for the named component or package before additional quantities or linked-weapon costs. A missing price is not zero. Explicit free grants apply only where the unit or subfaction grants them.</p>
<p id="armory-count" role="status">'''+str(len(cards))+''' components</p><noscript><p>All components are listed below. Enable JavaScript to filter them.</p></noscript><p id="armory-empty" hidden>No matching equipment. Try another search or reset the filters.</p><div class="armory-grid">'''+''.join(cards)+'</div>'
