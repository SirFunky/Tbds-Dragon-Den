"""Static unit catalog and reusable source-profile components."""
from html import escape
import json
from pathlib import Path
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]

def keyword_renderer():
    helper=runpy.run_path(str(ROOT/'iron-stars-tools/rulebook.py'))
    terms=helper['glossary_terms'](helper['selected_data']())
    terms.update({'Overdrive':'rule-core-b0197-r2','Shield Array':'rule-core-b0197-r3',
                  'Command Aura':'rule-core-b0197-r7','Fabricator Swarm':'rule-core-b0197-r8',
                  'Hardened Carapace':'rule-core-b0197-r11'})
    look={key.casefold():value for key,value in terms.items()}
    regex=re.compile(r'(?<!\w)('+ '|'.join(re.escape(k) for k in sorted(terms,key=len,reverse=True))+r')(?!\w)',re.I)
    def render(text):
        parts=[];cursor=0
        for match in regex.finditer(text):
            parts.append(escape(text[cursor:match.start()]))
            parts.append(f'<a class="keyword-ref" href="../../rules/index.html#{look[match[0].casefold()]}">{escape(match[0])}</a>')
            cursor=match.end()
        parts.append(escape(text[cursor:]))
        return ''.join(parts).replace('\n','<br>')
    return render,terms

def point_label(unit):
    points=unit['points']
    if points.get('calculation'):
        calculation=points['calculation']
        return str(calculation['total'])+' pts' if calculation['total'] is not None else 'Pricing incomplete'
    if points['filter_value'] is None:
        return 'Cost under review' if points['observations'] else 'Not specified'
    return ('~' if points['approximate'] else '')+str(points['filter_value'])+' pts'

def calculation_html(unit):
    calc=unit['points']['calculation'];rows=[]
    for item in calc['components']:
        optional=not item.get('included',True)
        quantity=(str(item.get('groups',1))+' groups × ' if item.get('groups',1)>1 else '')+str(item['quantity'])
        if item.get('linked'):quantity+=' linked'
        if optional:quantity+=' (optional)'
        value='Not priced' if item['total'] is None else str(item['total'])+(' pt' if abs(item['total'])==1 else ' pts')
        if item.get('alternatives'):value=f'{item["alternatives"]["separate"]} separate / {item["alternatives"]["linked"]} linked'
        if optional:value+=' · not included'
        ref=item.get('price_source_ref')
        source='Core v0.0.14' if item.get('price_source_id')=='core' else 'Faction component price'
        if item['basis']=='explicit-grant':source='Included / explicit grant'
        elif not ref:source='No price supplied'
        formula=''
        if item.get('copy_prices'):
            formula='<small class="linked-calculation">'+' + '.join(map(str,item['copy_prices']))+' per group</small>'
        evidence=f' data-price-ref="{escape(ref,quote=True)}"' if ref else ''
        rows.append(f'<tr><th scope="row">{escape(item["name"])}{formula}</th><td>{escape(quantity)}</td><td>{escape(value)}</td><td{evidence}>{source}</td></tr>')
    footer=f'<p class="calculated-total">Recalculated total: <strong>{calc["total"]} pts</strong></p>' if calc['total'] is not None else f'<p class="calculated-total">Known subtotal: <strong>{calc["known_subtotal"]} pts</strong></p><p class="pricing-missing">A complete total needs prices or construction details for: {escape(", ".join(calc["missing_components"]))}. The subtotal is not the unit’s playable point cost.</p>'
    return '<section class="unit-calculation" aria-labelledby="calculation-title"><h2 id="calculation-title">Point calculation</h2><p>Calculated from the latest matching component prices. Optional upgrades are separate. The original stock total is retained below for reference.</p><div class="unit-table" role="region" aria-label="Itemized component prices" tabindex="0"><table><caption>Chassis + weapons + paid systems and traits</caption><thead><tr><th scope="col">Component</th><th scope="col">Quantity</th><th scope="col">Points</th><th scope="col">Price source</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'+footer+'<p class="equipment-intro">Linked weapons use the <a class="keyword-ref" href="../../rules/index.html#rule-core-b0232-r18">core linked-cost formula</a>. A component reused in a transformation mode is counted once. Distinct Prototype/Experimental components use their specific prices.</p></section>'

def card_stats(unit):
    parts=[]
    for name,label in [('movement','M'),('defence','D'),('structure','STR')]:
        values=list(dict.fromkeys(p['fields'][name]['text'] for p in unit['profiles'] if name in p['fields']))
        value=' / '.join(values) if values else '—'
        if unit['alternate_observations'] and unit['source']['id']=='rebellion' and name in ('movement','defence'):value='Varies'
        parts.append(f'<span><small>{label}</small>{escape(value)}</span>')
    return '<div class="unit-card-stats">'+''.join(parts)+'</div>'

def profiles_html(unit,rich):
    if not unit['profiles']:
        return '<p>The source example does not specify a complete movement, Defence, or Structure profile. No values have been inferred from generic chassis tiers.</p>'
    rows=[]
    for profile in unit['profiles']:
        fields=profile['fields']
        values=''.join(f'<td data-value-ref="{fields[key]["source_ref"]}">{escape(fields[key]["text"])}</td>' if key in fields else '<td>Not specified</td>' for key in ['movement','defence','structure'])
        rows.append(f'<tr><th scope="row">{escape(profile["name"])}</th>{values}</tr>')
    details=[]
    for profile in unit['profiles']:
        if profile.get('mode_details') and profile['name']!='Standard':
            details.append('<div class="mode-details"><h3>'+escape(profile['name'])+'</h3>')
            for key,value in profile['mode_details'].items():
                details.append(f'<p data-value-ref="{value["source_ref"]}"><strong>{escape(key.title())}:</strong> {rich(value["text"])}</p>')
            details.append('</div>')
    return '<div class="unit-table" role="region" aria-label="Unit profiles and forms" tabindex="0"><table><caption>Source profile'+('s & forms' if len(rows)>1 else '')+'</caption><thead><tr><th scope="col">Form</th><th scope="col">Move</th><th scope="col">Defence</th><th scope="col">Structure</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'+''.join(details)

def display_weapon_text(text):
    # Roster data carries the literal weapon entry. The displayed stat line omits
    # parenthetical keyword explanations, so shared effects use the current core
    # glossary rather than superseded faction paraphrases.
    match=re.search(r'\b(?:FP|ME)\s*\d',text)
    if not match:return text
    prefix=text[:match.start()];stats=text[match.start():]
    stats=re.sub(r'\([^)]*\)','',stats)
    stats=re.sub(r'\s*[—–-]?\s*\d+\s*pts?\b','',stats,flags=re.I).strip()
    return (prefix+stats).strip()

def weapons_html(unit,rich):
    if not unit['weapons']:return '<p>No complete weapon profiles are specified in this entry.</p>'
    parts=[]
    for weapon in unit['weapons']:
        ref=weapon['source_ref']
        if weapon['kind']=='text':
            context=weapon.get('name_context')
            text=display_weapon_text(weapon['text'])
            name=f'<h3>{escape(context)}</h3>' if context else ''
            parts.append(f'<div class="weapon-entry" data-weapon-ref="{ref}">{name}<p>{rich(text)}</p>')
            if weapon.get('mode'):parts.append(f'<p class="equipment-mode">{escape(weapon["mode"])}</p>')
            for access in weapon.get('availability',[]):parts.append(f'<p class="equipment-mode" data-value-ref="{access["source_ref"]}">{rich(access["text"])}</p>')
            for drawback in weapon.get('drawbacks',[]):parts.append(f'<p class="equipment-mode" data-value-ref="{drawback["source_ref"]}">{rich(drawback["text"])}</p>')
            parts.append('</div>')
        else:
            rows=[]
            for header,cell in zip(weapon['columns'],weapon['cells']):
                if 'cost' in header.lower():continue
                value=cell['text']
                if header.lower() in ('traits','stats'):value=re.sub(r'\([^)]*\)','',value).strip()
                rows.append(f'<div><dt>{escape(header)}</dt><dd data-value-ref="{cell["id"]}">{rich(value)}</dd></div>')
            parts.append(f'<dl class="weapon-entry weapon-fields" data-weapon-ref="{ref}">'+''.join(rows)+'</dl>')
    return '<p class="equipment-intro">Weapon profiles are listed as printed. Linked groups retain their printed FP; they are not multiplied again. Shared keyword meanings link to core v0.0.14.</p>'+''.join(parts)

def systems_html(unit,rich,terms):
    if not unit['systems']:return '<p>No additional named systems are specified in this entry.</p>'
    parts=[]
    shared={name.casefold():target for name,target in terms.items()}
    faction_terms={'Iron Will','Scorch Doctrine','Storm Charge','Disruptive Presence','Relic Might','Guardian Protocols','Piercing Judgment','Overdrive Surge','Recursive Logic','Signal Dominion'}
    for system in unit['systems']:
        name=system['name'].strip()
        base_name=re.sub(r'\s*\([^)]*\)','',name).strip()
        if name in ('Sponsor Protocol','Knightly Perfection'):continue
        if base_name.casefold() in shared:
            body=f'<p><a class="text-link" href="../../rules/index.html#{shared[base_name.casefold()]}">Read the current core rule ↗</a></p>'
        elif base_name in faction_terms:
            body=f'<p><a class="text-link" href="../../factions/{unit["faction"]}/index.html#subfactions">Read the current faction rule ↗</a></p>'
        else:body='<p>'+rich(system['description'])+'</p>'
        parts.append(f'<div class="system-entry" data-system-ref="{system["source_ref"]}"><h3>{escape(name)}</h3>{body}</div>')
    return ''.join(parts)

def index_content(data):
    cards=[]
    for unit in sorted(data['units'],key=lambda u:u['name'].lower()):
        tags=unit['role_tags'];sub=unit['subfaction'] or 'Subfaction not specified'
        review='<span class="unit-review-tag">Entry needs review</span>' if unit['review_notes'] else ''
        cards.append(f'''<article class="unit-card" data-unit-id="{unit['id']}"><div class="unit-card-meta"><span>{escape(unit['faction_name'])}</span><strong>{escape(point_label(unit))}</strong></div><h2><a href="{unit['id']}/index.html">{escape(unit['name'])}</a></h2><p class="unit-card-sub">{escape(sub)}</p>{card_stats(unit)}<p class="unit-card-role">{escape(' · '.join(tags) or 'Role not specified')}</p><div class="unit-card-bottom">{review}<a href="{unit['id']}/index.html" aria-label="View {escape(unit['name'],quote=True)} profile">View profile ↗</a></div></article>''')
    factions=''.join(f'<option value="{f["id"]}">{escape(f["name"])}</option>' for f in data['factions'])
    subs=sorted({u['subfaction'] for u in data['units'] if u['subfaction']})
    suboptions=''.join(f'<option value="{escape(name,quote=True)}">{escape(name)}</option>' for name in subs)
    roles=''.join(f'<option>{escape(name)}</option>' for name in sorted({t for u in data['units'] for t in u['role_tags']}))
    inline=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    notes=''.join(f'<div id="{f["id"]}" class="catalog-faction-status"><strong>{escape(f["name"])}</strong><p>'+('Faction in development. Current background and unit example are available on the faction page.' if f['status']=='in-development' else 'Imported-stock faction. The catalog does not assign import eligibility or Compact costs.')+f'</p><a class="text-link" href="../factions/{f["id"]}/index.html">View faction ↗</a></div>' for f in data['factions'] if f['status']!='reference')
    filter_targets=''.join(f'<span id="{f["id"]}" class="catalog-filter-target" aria-hidden="true"></span>' for f in data['factions'] if f['status']=='reference')
    return f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span aria-hidden="true">/</span><span aria-current="page">Units</span></nav><section class="unit-index-intro"><p class="eyebrow">THE FORCE ROSTER / UNIT DATABASE</p><h1 id="title">Know your forces.</h1><p class="lead">Browse {len(data['units'])} source profiles. Find a frame by faction, role, equipment, or recalculated points, then open its loadout and available forms.</p><p class="unit-source-note">Core rules v0.0.14 · Costs recalculated from the latest matching component prices</p></section>
{filter_targets}<form id="unit-filters" class="unit-filters" aria-label="Filter unit profiles"><div class="filter-search"><label for="unit-query">Search units, weapons &amp; systems</label><input id="unit-query" name="query" type="search" placeholder="Try laser, bodyguard, or Interceptor…" disabled></div><div><label for="unit-faction">Faction</label><select id="unit-faction" name="faction" disabled><option value="">All factions</option>{factions}</select></div><div><label for="unit-subfaction">Subfaction</label><select id="unit-subfaction" name="subfaction" disabled><option value="">All subfactions</option><option value="unspecified">Not specified</option>{suboptions}</select></div><div><label for="unit-role">Role</label><select id="unit-role" name="role" disabled><option value="">All roles</option>{roles}</select></div><div><label for="unit-min">Minimum points</label><input id="unit-min" name="min" type="number" min="0" step="1" placeholder="Any" disabled></div><div><label for="unit-max">Maximum points</label><input id="unit-max" name="max" type="number" min="0" step="1" placeholder="Any" disabled></div><div><label for="unit-status">Source review</label><select id="unit-status" name="status" disabled><option value="">All entries</option><option value="review">With review notes</option><option value="clear">Without review notes</option></select></div><div><label for="unit-sort">Sort</label><select id="unit-sort" name="sort" disabled><option value="name">Name A–Z</option><option value="points-asc">Points: low to high</option><option value="points-desc">Points: high to low</option></select></div><button id="reset-unit-filters" type="reset" disabled>Reset filters</button><p class="filter-help">Points use complete component recalculations. Entries lacking a component price show “Pricing incomplete.” A dash means the source does not specify a value. Role filters group the source descriptions; subfactions are assigned only where the source states them.</p></form><noscript><p class="unit-notice">All profiles are shown below. Enable JavaScript for filters, or use your browser’s Find command.</p></noscript>
<p id="unit-count" class="unit-count" role="status" aria-live="polite">{len(data['units'])} unit references · Filters require JavaScript</p><p id="point-filter-note" class="unit-notice" hidden>Point limits exclude incomplete calculations. Original stock totals are retained on each profile for reference.</p><p id="faction-unit-note" class="unit-notice" hidden></p><p id="unit-empty" class="unit-empty" hidden>No units match these filters. Try clearing a filter or widening the point range.</p><div id="unit-catalog" class="unit-catalog">{''.join(cards)}</div><section class="catalog-statuses" aria-label="Factions in development and imported rosters">{notes}</section><script type="application/json" id="unit-data">{inline}</script>'''

def detail_content(unit,rich,terms):
    u=unit
    badges=''.join(f'<span>{escape(value)}</span>' for value in [u['subfaction'],u['configuration']] if value)
    source_version='v'+u['source_version'] if u['source_version'] else 'No release version stated'
    stat=profiles_html(u,rich)
    calculation=calculation_html(u)
    points='<ul class="point-observations">'+''.join(f'<li data-value-ref="{p["source_ref"]}">{escape(p["text"])}</li>' for p in u['points']['observations'])+'</ul>' if u['points']['observations'] else '<p>No point cost is specified.</p>'
    review='<aside class="unit-notice"><h2>Source entry needs review</h2><ul>'+''.join(f'<li>{escape(note)}</li>' for note in u['review_notes'])+'</ul></aside>' if u['review_notes'] else ''
    alternatives=''
    for alt in u['alternate_observations']:
        alternatives+='<details class="unit-alternative"><summary>'+escape(alt['label'])+'</summary>'+''.join(f'<p data-value-ref="{v["source_ref"]}">{rich(v["text"])}</p>' for v in alt['profile_text'])+'</details>'
    special=''.join(f'<p data-value-ref="{v["source_ref"]}">{rich(v["text"])}</p>' for v in u['special_rules'])
    mode_rules=''.join(f'<p data-value-ref="{v["source_ref"]}">{rich(v["text"])}</p>' for v in u['mode_rules'])
    if u['spawned_units']:
        mode_rules+='<details class="unit-alternative"><summary>Spawned unit profiles</summary>'
        for child in u['spawned_units']:
            mode_rules+='<h3>'+escape(child['name'])+'</h3>'
            mode_rules+=''.join(f'<p data-value-ref="{b["id"]}">{rich(b["text"])}</p>' for b in child['source_blocks'] if b.get('text','').strip())
        mode_rules+='</details>'
    role=escape(u['role']['text']) if u['role'] else 'Not specified in this entry.'
    chassis=escape(u['chassis']['text']) if u['chassis'] else 'Not specified in this entry.'
    return f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../index.html">Iron Stars</a><span aria-hidden="true">/</span><a href="../index.html">Units</a><span aria-hidden="true">/</span><span aria-current="page">{escape(u['name'])}</span></nav><section class="unit-detail-intro"><p class="eyebrow">{escape(u['faction_name'])} / UNIT PROFILE</p><h1 id="title">{escape(u['name'])}</h1><div class="unit-badges">{badges}<span>Source reference</span></div><p class="unit-point-heading">{escape(point_label(u))}</p><a class="text-link" href="../../factions/{u['faction']}/index.html">Read faction background &amp; rules ↗</a></section><nav class="unit-section-nav" aria-label="On this unit page"><a href="#profile">Profile</a><a href="#calculation-title">Points</a><a href="#weapons">Weapons</a><a href="#systems">Systems &amp; traits</a><a href="#source">Source</a></nav><div class="unit-detail">{review}<section id="profile"><p class="eyebrow">Frame &amp; configuration</p><h2>Unit profile</h2><dl class="unit-role"><div><dt>Chassis</dt><dd>{chassis}</dd></div><div><dt>Source role</dt><dd>{role}</dd></div></dl>{stat}{mode_rules}{alternatives}{calculation}<details class="unit-alternative"><summary>Original printed totals</summary>{points}<p>These are the original source observations, retained for traceability. The component calculation above determines the current displayed cost.</p></details><div class="unit-artwork-slot"><span aria-hidden="true">✦</span><p>Unit artwork space</p></div></section><section id="weapons"><p class="eyebrow">Loadout</p><h2>Weapons</h2>{weapons_html(u,rich)}</section><section id="systems"><p class="eyebrow">Systems, traits &amp; special rules</p><h2>Systems &amp; traits</h2>{systems_html(u,rich,terms)}{('<div class="unit-core-example">'+special+'</div>') if special else ''}</section><section id="source" class="unit-source"><h2>Source</h2><p>{escape(u['source']['filename'])}<br>{source_version}</p><p>Shared rules and keyword definitions use core v0.0.14. This is a source-reference profile, not an approved army-builder configuration. Missing values remain unspecified.</p><a class="text-link" href="../index.html#{u['faction']}">← Browse this faction’s units</a></section></div>'''

def render_units():
    data=runpy.run_path(str(ROOT/'iron-stars-tools/units_data.py'))['compile_units']()
    rich,terms=keyword_renderer()
    accents={'iron-concord':'#e49a76','unmc':'#8abde0','cybernetic-rebellion':'#7ec8bf','new-avalon':'#b3b2e3'}
    pages=[{'slug':'units','name':'Units','content':index_content(data),'accent':'#f2944a','description':'Search IRON STARS unit references by faction, subfaction, role, equipment, and recalculated points.'}]
    for unit in data['units']:
        pages.append({'slug':'units/'+unit['id'],'name':unit['name'],'content':detail_content(unit,rich,terms),
                      'accent':accents[unit['faction']],'description':unit['name']+' — '+unit['faction_name']+' source profile, weapons, systems, and configurations for IRON STARS.'})
    links={u['source_refs'][0]:u['id'] for u in data['units']}
    return {'pages':pages,'source_unit_links':links,'unit_count':len(data['units'])}
