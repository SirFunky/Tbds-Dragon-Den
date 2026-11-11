"""Build the beta premade roster tool from current calculated unit data."""
import json
from pathlib import Path
from html import escape
from custom_data import custom_catalog
from roster_reference import references
from subfactions import affiliations

ROOT=Path(__file__).resolve().parents[1]

BUILDER_GUIDE='''<details id="builder-guide" class="builder-guide"><summary>New here? Quick-start guide</summary><p class="guide-intro">Build a force, keep your designs, then take them to the table. Use the shortcuts below to find the controls.</p><ol class="builder-guide-steps">
<li><h2>Choose your force</h2><p>Select a faction, optional affiliation and points limit. Each faction keeps its own saved rosters.</p><button type="button" data-guide-target="army-faction" hidden>Go to faction settings</button></li>
<li><h2>Add units</h2><p>Add a premade for a ready-made loadout, or build a custom unit from a chassis, weapon groups and systems. Hover, focus or tap ⓘ for component rules. Southern Cross uses stock imports only.</p><div class="guide-links"><button type="button" data-guide-target="available-title" hidden>Find premades</button><button type="button" data-guide-target="custom-editor" hidden>Open custom builder</button></div></li>
<li><h2>Save and organize</h2><p>Edits save in this browser. Use New roster or Duplicate roster for another force; add tags to find it later. Save custom designs to your library for reuse.</p><div class="guide-links"><button type="button" data-guide-target="roster-manager" hidden>Go to saved rosters</button><button type="button" data-guide-target="unit-library" hidden>Open unit library</button></div></li>
<li><h2>Keep a backup</h2><p>Export roster saves a JSON file you can keep or move to another device. Import roster adds a new saved force. Saved roster backups and the unit library have their own export/import controls.</p><button type="button" data-guide-target="army-export" hidden>Find roster export</button></li>
<li><h2>Print your references</h2><p>Print roster includes premade and custom profiles. Custom unit cards gives each custom form its own card. Army quick reference gathers the rules used by the selected force.</p><button type="button" data-guide-target="army-print" hidden>Go to print controls</button></li>
<li><h2>Track a battle</h2><p>Battle tracker starts or resumes a separate snapshot of the selected force. Record Structure, forms, statuses, limited uses and notes. Roster edits do not change an ongoing battle; start a new battle to use the updated force.</p><button type="button" data-guide-target="army-battle" hidden>Find battle tracker</button></li>
</ol><p>Need the game rules? <a href="../rules/index.html">Open the rulebook</a> or <a href="../armory/index.html">browse the Armory</a>.</p><p id="builder-guide-status" role="status"></p><button type="button" id="builder-guide-dismiss" hidden>Hide guide</button></details>'''

TRANSFORM_FORM='''<section id="custom-transform" hidden aria-labelledby="custom-transform-title"><h3 id="custom-transform-title">Transform forms</h3><p id="custom-transform-rules" class="transform-source-rule"></p><p class="small-note">The main profile defines Mech form. Other profiles are derived automatically from it. Choose weapon availability below; installed systems stay shared. Each component is charged once and linked copy counts stay fixed across forms.</p><div id="custom-forms"></div></section>'''

CUSTOM_FORM='''<section class="custom-section" aria-labelledby="custom-title"><h2 id="custom-title">Custom units</h2><p id="custom-locked" hidden>Southern Cross uses stock imports only. Custom units cannot be added to this faction.</p><details id="custom-editor"><summary>Build a custom unit</summary><form id="custom-form"><p class="small-note">Hover a component name or ⓘ for its rules. You can also focus or tap ⓘ.</p><div class="custom-settings"><label>Unit name<input id="custom-name" maxlength="100" required></label><div><label for="custom-chassis">Chassis</label><div id="custom-chassis-help" class="part-help"><select id="custom-chassis"></select></div></div><label>Movement (cm)<select id="custom-movement"></select></label><label>Structure<select id="custom-structure"></select></label><p id="custom-defence"></p></div><p class="small-note">Chassis values use the source ranges. Components with missing prices and chassis without complete base stats are unavailable. Faction locks apply. Selected subfaction traits are listed with your force; component prices stay unchanged.</p><h3>Weapon groups</h3><p class="small-note">Each row is an independent group. Linked groups combine identical ranged weapons: first three copies at base cost, fourth at twice base, fifth at three times base, and so on.</p><div id="custom-weapons"></div><button type="button" id="custom-add-weapon">Add weapon group</button><fieldset><legend>Systems &amp; traits</legend><div id="custom-systems"></div></fieldset><label id="custom-ammo-label" hidden>Ammo Bin weapon<select id="custom-ammo-target"></select></label><details class="custom-source"><summary>Selected component details</summary><div id="custom-part-details"></div></details><section class="custom-calculation" aria-labelledby="custom-cost-title"><h3 id="custom-cost-title">Component costs</h3><ul id="custom-breakdown"></ul><strong id="custom-total" role="status"></strong><p id="custom-error" role="status"></p></section><div class="builder-actions"><button type="submit" class="button" id="custom-save">Add custom unit to roster</button><button type="button" id="custom-cancel">Cancel</button></div></form></details></section>'''

# Only explicit chassis tiers/classifications; never infer a tier from points,
# movement, Defence, Structure, or a similar-looking frame's name.
IMPORT_TIERS={
    'concord:b0035':('light','user:ironsworn-frame-light'),
    'concord:b0080':('superheavy','concord:b0028:r7:c6'),
    'unmc:b0171':('heavy','unmc:b0174'),
    'core:b0205':('medium','core:b0206'),
    'core:b0212':('heavy','core:b0213'),
    'core:b0220':('medium','core:b0221'),
}

def import_policy(unit):
    if unit['faction'] not in ('iron-concord','unmc','new-avalon'):
        return {'eligible':False,'reason':'Source faction cannot be imported.'}
    # The currently complete candidates are generic stock entries. Explicitly
    # refuse Heroes/Unique records if these become priced in future imports.
    import re
    if re.search(r'\b(hero|unique)\b',unit['name'],re.I) or unit['role'] and re.search(r'\b(hero|unique)\b',unit['role']['text'],re.I):
        return {'eligible':False,'reason':'Heroes and Unique units cannot be imported.'}
    tier=IMPORT_TIERS.get(unit['source_refs'][0])
    if tier is None:
        return {'eligible':False,'reason':'Chassis tax tier is not confirmed.'}
    policy={'eligible':True,'tier':tier[0],'tier_source_ref':tier[1]}
    if tier[1]=='user:ironsworn-frame-light':
        policy['tier_confirmation']='User confirmed the Ironsworn Frame is Light, 2026-11-06.'
    return policy

def render_builder():
    units=json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))['units']
    factions=json.loads((ROOT/'iron-stars/data/factions.json').read_text(encoding='utf-8'))['factions']
    eligible=[u for u in units if u['points']['calculation']['total'] is not None and not u['review_notes']]
    custom=custom_catalog()
    reference=references(eligible,custom['parts'])
    affiliation_data=affiliations()
    data={'schema':1,'version':'0.0.14','factions':[{'id':f['id'],'name':f['name'],**affiliation_data[f['id']]} for f in factions],
          'custom':custom,
          'import_rules':{'faction':'southern-cross-compact',
             'chassis_tax':{'light':2,'medium':3,'heavy':4,'superheavy':5,'elite':5},
             'source_modifier':{'iron-concord':1,'unmc':3,'new-avalon':5},
             'chassis_refs':['core:b0635','core:b0636','core:b0637','core:b0638'],
             'source_refs':['core:b0640','core:b0641','core:b0642'],
             'restriction_refs':['core:b0612','core:b0616','core:b0620','core:b0621','core:b0622','core:b0623','core:b0629','core:b0630']},
          'units':[{'id':u['id'],'name':u['name'],'faction':u['faction'],'points':u['points']['calculation']['total'],
                    'role':u['role']['text'] if u['role'] else '', 'subfaction':u['subfaction'],
                    'southern_cross':import_policy(u),
                    'reference':reference[u['id']],
                    'source_ref':u['source_refs'][0]} for u in eligible]}
    (ROOT/'iron-stars/data/army-builder.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    options=''.join(f'<option value="{f["id"]}">{escape(f["name"])}</option>' for f in factions)
    html='''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span>/</span><span aria-current="page">Army builder</span></nav>
<section class="section-intro"><p class="eyebrow">IRON STARS / Force planning</p><h1>Army builder</h1><p class="lead">Choose your faction. Build custom units or add premades. Plan your force.</p><p class="small-note">Beta · Core v0.0.14 · Full component costs, no premade discounts. Custom units check component prices, faction locks, chassis values, Unique systems, and linked-weapon costs. Full army legality and subfaction choices are not yet checked. Only premades with complete costs and no unresolved review notes are available.</p></section>
<noscript><p>This builder needs JavaScript. You can still <a href="../units/index.html">browse the unit reference</a>.</p></noscript>
<div id="builder-app" hidden><section class="builder-settings" aria-label="Roster settings"><label>Faction<select id="army-faction">'''+options+'''</select></label><label>Roster name<input id="army-name" maxlength="100" value="My force"></label><label>Points limit<input id="army-limit" type="number" min="1" max="1000000" step="1" value="500"></label></section>
<p id="save-status" role="status"></p><section id="import-rules" class="pending" hidden aria-labelledby="import-title"><h2 id="import-title">Southern Cross imports</h2><p>Stock units only, from Iron Concord, UNMC, and New Avalon. No Cybernetic Rebellion, Heroes, named characters, or Unique units. No customization.</p><p>Each imported mech pays its full component cost, plus a chassis tax and source modifier. It counts as Southern Cross and keeps its stock weapons, systems, and unit rules. Original faction rules, subfaction and detachment bonuses, faction-wide command benefits, and source-locked benefits do not apply.</p><p>Chassis tax: Light +2 · Medium +3 · Heavy +4 · Superheavy / Elite +5.<br>Source modifier: Iron Concord +1 · UNMC +3 · New Avalon +5.</p><p>Only complete profiles with a confirmed chassis tax tier are selectable. Named frames without a confirmed tier remain unavailable.</p><a href="../factions/southern-cross-compact/index.html">Read Southern Cross rules and import restrictions ↗</a></section><div class="builder-layout"><section aria-labelledby="available-title"><h2 id="available-title">Available premades</h2><label class="builder-search">Search units<input type="search" id="army-search" placeholder="Search by name, role, or subfaction"></label><p id="available-count" class="small-note"></p><div id="army-available"></div></section>
<section class="roster-panel" aria-labelledby="roster-title"><p class="eyebrow">Your force</p><h2 id="roster-title">My force</h2><p id="army-faction-name"></p><div id="army-budget" role="status" class="army-budget"></div><p id="army-validation" role="status"></p><div id="army-lines"></div><div class="builder-actions"><button type="button" class="button" id="army-export">Export roster</button><label class="import-label">Import roster<input type="file" id="army-import" accept=".json,application/json"></label><button type="button" id="army-print">Print roster</button></div><p id="transfer-status" role="status"></p><p class="small-note">Keep multiple named rosters per faction, saved in this browser. Export a roster to keep a copy or move it to another device. Imported rosters use current prices.</p></section></div></div>
<script type="application/json" id="army-data">'''+payload+'</script>'
    html=html.replace('<label>Roster name','<label><span id="army-subfaction-label">Subfaction</span><select id="army-subfaction" aria-label="Subfaction"></select></label><label>Roster name')
    html=html.replace('<p id="army-faction-name"></p>','<p id="army-faction-name"></p><div id="army-traits" class="roster-traits"></div>')
    html=html.replace('Full army legality and subfaction choices are not yet checked.','Subfaction traits use the latest core wording. Conditional effects remain conditional; full army legality is not yet checked.')
    html=html.replace('<p id="save-status"',CUSTOM_FORM+'<p id="save-status"')
    html=html.replace('<div id="builder-app" hidden>','<div id="builder-app" hidden>'+BUILDER_GUIDE)
    html=html.replace('<p id="custom-defence"></p>','<p id="custom-defence"></p><label id="custom-flyer-label" hidden><span>UNMC flyer frame</span><span><input type="checkbox" id="custom-flyer"> Flyer-capable unit (required for Transform)</span></label>')
    return html.replace('<details class="custom-source">',TRANSFORM_FORM+'<details class="custom-source">')
