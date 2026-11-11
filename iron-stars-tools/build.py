"""Generate the static Iron Stars foundation; never publish or alter the gallery."""
from pathlib import Path
from html import escape
import re
import runpy
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'iron-stars'
SECTIONS = [
    ('', 'Home', 'Bring your miniatures. Enter the conflict.'),
    ('rules', 'Rules', 'Your field manual.'),
    ('factions', 'Factions', 'Find your allegiance.'),
    ('units', 'Units', 'Know your forces.'),
    ('armory', 'Armory', 'Equip for the battlefield.'),
    ('army-builder', 'Army builder', 'Plan your force.'),
    ('universe', 'Universe', 'Beyond the battlefield.'),
    ('downloads', 'Downloads', 'Prepare your tabletop.'),
    ('updates', 'Updates', 'Follow the development.'),
]
SUMMARIES = {
    'rules': 'Read the IRON STARS v0.0.14 core rules with chapter navigation, search, a keyword glossary, and notes on unresolved passages.',
    'factions': 'Explore all seven IRON STARS factions, with backgrounds, doctrines, subfactions, source rules, and roster availability.',
    'units': 'Search IRON STARS unit profiles by faction, subfaction, role, equipment, and recalculated points.',
    'armory': 'Search weapons, systems, traits, and chassis with current component prices and source references.',
    'army-builder': 'Build custom units or add premades, track points, and save or export your force.',
    'universe': 'Explore the history, factions, stories, and transmissions of the IRON STARS universe.',
    'downloads': 'Approved rulebooks and printable references will be collected here when publication files are ready.',
    'updates': 'Published rules versions and documented changes will appear here. No release history has been imported yet.',
}


def build():
    rulebook = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'rulebook.py'))
    unit_module = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'units.py'))
    unit_result = unit_module['render_units']()
    unit_pages = {p['slug']:p for p in unit_result['pages']}
    faction_module = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'factions.py'))
    faction_pages = {p['slug']: p for p in faction_module['render_factions'](unit_result['source_unit_links'])}
    armory = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'armory.py'))['render_armory']()
    builder = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'army_builder.py'))['render_builder']()
    universe_module = runpy.run_path(str(ROOT / 'iron-stars-tools' / 'universe.py'))
    universe_pages = {p['slug']: p for p in universe_module['render_universe'](faction_module['select_data']()['factions'])}
    detail_pages = {**faction_pages, **unit_pages, **universe_pages}
    routes = SECTIONS + [(p['slug'], p['name'], '') for p in detail_pages.values() if '/' in p['slug']]
    for slug, label, heading in routes:
        depth = len(slug.split('/')) if slug else 0
        base = '../' * depth if slug else './'
        hobby = '../' * (depth + 1)
        nav = ''.join(
            '<a href="{}"{}>{}</a>'.format(
                base + (target + '/' if target else ''),
                (' aria-current="page"' if target == slug else ' aria-current="location"' if target in ('factions','units','universe') and slug.startswith(target+'/') else ''), name)
            for target, name, _ in SECTIONS)
        if not slug:
            content = f'''<section class="hero" aria-labelledby="title">
<div class="hero-copy"><p class="eyebrow">Miniature-agnostic / Science-fiction wargame</p>
<h1 id="title">YOUR MODELS.<br>YOUR FORCES.<br><span>IRON STARS.</span></h1>
<p class="lead">Bring the mechs and miniatures you already own to a science-fiction tabletop wargame.</p>
<div class="actions"><a class="button" href="rules/">Explore the rules <span aria-hidden="true">↗</span></a><a class="text-link" href="{hobby}iron-stars.html">View the miniature gallery <span aria-hidden="true">↗</span></a></div>
<p class="small-note">IRON STARS is in beta · Core rules v0.0.14 · Rules and points may change</p></div>
<div class="hero-art" role="img" aria-label="Abstract orange star and orbital paths on a tactical grid"><span class="art-top">IS / DEEP SPACE</span><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="star">✦</div><span class="art-bottom">IRON STARS<br><small>THE TABLETOP IS YOURS.</small></span></div>
</section>
<section class="explore" aria-labelledby="explore-title"><div class="section-heading"><p class="eyebrow">Explore Iron Stars</p><h2 id="explore-title">A new front opens.</h2><p>The game’s digital home is taking shape. Start with the sections below, or see the miniatures on the tabletop.</p></div>
<div class="feature-grid home-features"><a class="feature" href="rules/"><span class="number">01 / FIELD MANUAL</span><h3>Rules</h3><p>Searchable core rules, chapters, and terminology.</p><span class="feature-bottom">Read the v0.0.14 beta rules <b aria-hidden="true">↗</b></span></a>
<a class="feature" href="factions/"><span class="number">02 / ALLEGIANCES</span><h3>Factions</h3><p>Backgrounds, doctrines, and faction rules.</p><span class="feature-bottom">Explore all seven factions <b aria-hidden="true">↗</b></span></a>
<a class="feature" href="units/"><span class="number">03 / FORCE ROSTER</span><h3>Units &amp; profiles</h3><p>Search profiles, weapons, and configurations.</p><span class="feature-bottom">Browse the unit database <b aria-hidden="true">↗</b></span></a>
<a class="feature" href="armory/"><span class="number">04 / EQUIPMENT</span><h3>Armory</h3><p>Search weapons, systems, and chassis with current component prices.</p><span class="feature-bottom">Explore the armory <b aria-hidden="true">↗</b></span></a>
<a class="feature" href="army-builder/"><span class="number">05 / FORCE PLANNING</span><h3>Army builder</h3><p>Build custom units, add premades, and save your roster.</p><span class="feature-bottom">Build your force <b aria-hidden="true">↗</b></span></a></div></section>
<section class="gallery-callout" aria-labelledby="gallery-title"><div><p class="eyebrow">From the hobby table</p><h2 id="gallery-title">See the collection.</h2><p>Painted mechs, city terrain, and views from the painting desk.</p><a class="text-link" href="{hobby}iron-stars.html">Browse all fifteen photographs <span aria-hidden="true">↗</span></a></div><a href="{hobby}iron-stars.html" aria-label="Open the Iron Stars miniature gallery"><img src="{base}photo-01.webp" alt="Mech miniatures arranged around a city battlefield" width="1600" height="1200" loading="lazy"></a></section>'''
        elif slug == 'rules':
            content = rulebook['render_rulebook']()
        elif slug == 'armory':
            content = armory
        elif slug == 'army-builder':
            content = builder
        elif slug in detail_pages:
            content = detail_pages[slug]['content']
        else:
            content = f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="{base}">Iron Stars</a><span aria-hidden="true">/</span><span aria-current="page">{label}</span></nav>
<section class="section-intro" aria-labelledby="title"><p class="eyebrow">IRON STARS / {label}</p><h1 id="title">{heading}</h1><p class="lead">{SUMMARIES[slug]}</p></section>
<section class="pending" aria-labelledby="pending-title"><span class="status">IN DEVELOPMENT</span><h2 id="pending-title">{label} are coming online.</h2><p>This section is a foundation for the game’s digital reference. Its content has not yet been imported and verified.</p><p>Core source: <strong>rulebook v0.0.14</strong>. Faction document versions and individual records still require review. No finalized rules, statistics, or downloads are published here yet.</p><a class="text-link" href="{base}">Return to Iron Stars <span aria-hidden="true">↗</span></a></section>'''
            if slug == 'universe':
                content = content.replace('Universe are coming online.', 'The universe is coming online.')
            elif slug == 'armory':
                content = content.replace('Armory are coming online.', 'The armory is coming online.')
        description = ('IRON STARS is a miniature-agnostic science-fiction tabletop wargame. Explore its developing digital home and miniature gallery.'
                       if not slug else detail_pages[slug]['description'] if slug in detail_pages else SUMMARIES[slug] + ' Website content is in development.')
        canonical = 'https://tbddragonden.com/iron-stars/' + (slug + '/' if slug else '')
        rulebook_assets = ('<link rel="stylesheet" href="../assets/rulebook.css"><script src="../assets/rulebook.js" defer></script>'
                           '<link rel="alternate" type="application/json" href="../data/rulebook.json" title="Core rulebook source reference">') if slug == 'rules' else ''
        faction_assets = (f'<link rel="stylesheet" href="{base}assets/factions.css"><link rel="alternate" type="application/json" href="{base}data/factions.json" title="Faction source references">') if slug in faction_pages else ''
        unit_assets = (f'<link rel="stylesheet" href="{base}assets/units.css"><link rel="alternate" type="application/json" href="{base}data/units.json" title="Unit source references"><link rel="alternate" type="application/json" href="{base}data/pricing.json" title="Component price calculations">') if slug in unit_pages else ''
        if slug == 'units':unit_assets += '<script src="../assets/unit-filters.js" defer></script><script src="../assets/units.js" defer></script>'
        if slug == 'armory':unit_assets += '<link rel="stylesheet" href="../assets/armory.css"><script src="../assets/armory.js" defer></script><link rel="alternate" type="application/json" href="../data/armory.json" title="Armory component references">'
        if slug == 'army-builder':unit_assets += '<link rel="stylesheet" href="../assets/army-builder.css"><link rel="stylesheet" href="../assets/custom-builder.css"><script src="../assets/custom-core.js" defer></script><script src="../assets/roster-core.js" defer></script><script src="../assets/custom-builder.js" defer></script><script src="../assets/battle-core.js" defer></script><script src="../assets/battle-tracker.js" defer></script><script src="../assets/army-builder.js" defer></script><link rel="alternate" type="application/json" href="../data/army-builder.json" title="Builder premades and construction components">'
        if slug == 'army-builder':
            # Keep related builder scripts in sync when a browser cached an
            # earlier feature version. These remain ordinary static files.
            unit_assets = re.sub(r'\.\./assets/([^"?]+\.(?:js|css))',
                lambda match: match[0]+'?v='+hashlib.sha256((SITE/'assets'/match[1]).read_bytes()).hexdigest()[:12],unit_assets)
        if slug in universe_pages:unit_assets += f'<link rel="stylesheet" href="{base}assets/universe.css">'
        theme = f' style="--faction-accent:{detail_pages[slug]["accent"]}"' if slug in detail_pages else ''
        page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{'IRON STARS | A miniature-agnostic tabletop wargame' if not slug else escape(label) + ' | IRON STARS'}</title>
<meta name="description" content="{escape(description, quote=True)}"><meta name="theme-color" content="#141719">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{escape(label,quote=True)} | IRON STARS"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="{base}assets/site.css"><script src="{base}assets/site.js" defer></script>{rulebook_assets}{faction_assets}{unit_assets}</head>
<body class="iron-stars"{theme}><a class="skip-link" href="#main">Skip to content</a>
<div class="utility"><div class="shell"><a href="{hobby}index.html">← TBD’s Dragon Den</a><span>A miniature-agnostic tabletop wargame</span></div></div>
<header class="site-header shell"><a class="brand" href="{base}" aria-label="Iron Stars home"><span class="brand-mark" aria-hidden="true">✦</span><span>IRON STARS<small>SCIENCE-FICTION WARGAME</small></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" hidden>Menu <span aria-hidden="true">☰</span></button><nav id="primary-nav" class="primary-nav" aria-label="Iron Stars">{nav}</nav></header>
<main id="main" class="shell" tabindex="-1">{content}</main>
<footer class="site-footer shell"><div><a class="footer-brand" href="{base}">IRON STARS</a><p>Your miniatures. A universe of conflict.</p></div><div><a href="{hobby}index.html">TBD’s Dragon Den ↗</a><a href="{hobby}iron-stars.html">Miniature gallery ↗</a><p>Source rulebook v0.0.14 · Website in development</p></div></footer>
</body></html>
'''
        # Explicit filenames work both with file:// previews and HTTP hosting.
        # Keep absolute canonical URLs and fragment links unchanged.
        page = re.sub(r'href="((?:\.{1,2}/|[a-z][a-z-]*/)+)"',
                      r'href="\1index.html"', page)
        output = SITE / slug / 'index.html'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(page, encoding='utf-8')
    print(f'Generated {len(routes)} Iron Stars pages. Gallery and publication files unchanged.')


if __name__ == '__main__':
    build()
