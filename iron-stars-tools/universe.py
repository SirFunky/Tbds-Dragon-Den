"""Render sourced setting history and author-selected recovered fiction."""
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def inline(text):
    text = escape(text)
    for pattern, tag in [(r'\*\*(.+?)\*\*', 'strong'), (r'\*(.+?)\*', 'em'), (r'_(.+?)_', 'em')]:
        text = re.sub(pattern, rf'<{tag}>\1</{tag}>', text)
    # Source blockquotes sometimes wrap several paragraphs in one emphasis pair.
    # Unmatched paragraph-edge markers are formatting, not story text.
    return text.replace('*', '')


def fiction_html(markdown):
    paragraphs = []
    for part in re.split(r'\n\s*\n', markdown):
        lines = [re.sub(r'^>\s?', '', line).strip() for line in part.splitlines()]
        if not lines or all(not line or line == '---' for line in lines):
            continue
        paragraphs.append('<p>' + '<br>'.join(inline(line) for line in lines) + '</p>')
    return ''.join(paragraphs)


def source_paragraph(block):
    return f'<p data-source-ref="{block["id"]}">{escape(block["text"])}</p>'


def render_universe(factions):
    doc = json.loads((ROOT/'iron-stars-source/extracted/core.json').read_text(encoding='utf-8'))
    blocks = {int(b['id'].split(':b')[1]): b for b in doc['blocks']}
    data = json.loads((ROOT/'iron-stars-tools/lore-content.json').read_text(encoding='utf-8'))
    stories = data['stories']
    faction_names = {f['id']: f['name'] for f in factions}
    cards = []
    pages = []
    for story in stories:
        title = escape(story['title'])
        tags = ' / '.join(escape(faction_names[f]) for f in story['factions']) or 'Beyond the front lines'
        count = len(story['markdown'].split())
        reading = max(1, round(count / 200))
        cards.append(f'''<a class="lore-card" href="{story['id']}/index.html"><span class="eyebrow">{escape(story['kind'])} / {reading} min read</span><h3>{title}</h3><p>{escape(story['summary'])}</p><span class="lore-card-end">Read {escape(story['kind'].lower())} <span aria-hidden="true">↗</span></span></a>''')
        related = ''.join(f'<a class="text-link" href="../../factions/{f}/index.html">{escape(faction_names[f])} ↗</a>' for f in story['factions'])
        others = ''.join(f'<a href="../{s["id"]}/index.html">{escape(s["title"])} ↗</a>' for s in stories if s != story)
        appendices = ''.join(f'<section class="lore-version"><h2>{escape(a["title"])}</h2><div class="lore-prose">{fiction_html(a["markdown"])}</div></section>' for a in story.get('appendices', []))
        content = f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../index.html">Iron Stars</a><span aria-hidden="true">/</span><a href="../index.html">Universe</a></nav>
<article class="lore-reading"><header class="section-intro"><p class="eyebrow">{escape(story['kind'])} / {reading} min read</p><h1 id="title">{title}</h1><p class="lead">{escape(story['summary'])}</p><p class="lore-meta">{tags}</p></header><div class="lore-prose">{fiction_html(story['markdown'])}</div>
{appendices}<footer class="lore-source"><p>Source: {escape(story['chat']['title'])} · {escape(story['kind'])}.</p><p>In-universe fiction. Character accounts describe their experiences and viewpoints.</p><div class="lore-related">{related}</div><a class="text-link" href="../index.html#stories">← Stories &amp; transmissions</a></footer></article>
<nav class="lore-more" aria-label="More fiction"><h2>Keep reading</h2>{others}</nav>'''
        pages.append({'slug': 'universe/'+story['id'], 'name': story['title'], 'description': story['summary'], 'content': content, 'accent': '#f2944a'})
    history = []
    for start, end in [(677,680),(681,684),(685,688),(689,692),(693,696),(697,700),(701,704),(705,708),(709,714)]:
        history.append(f'<li><h3 data-source-ref="{blocks[start]["id"]}">{escape(blocks[start]["text"])}</h3>' + ''.join(source_paragraph(blocks[n]) for n in range(start+1,end+1) if blocks[n].get('text','').strip()) + '</li>')
    faction_cards = []
    for faction in factions:
        quote = faction['quote']
        overview = next(b for b in faction['sections']['overview'] if b.get('text','').strip())
        status = '<p class="lore-meta">Faction in development</p>' if faction['development_status']=='in-development' else ''
        faction_cards.append(f'''<article class="lore-faction" style="--faction-accent:{faction['accent']}"><h3><a href="../factions/{faction['id']}/index.html">{escape(faction['name'])} ↗</a></h3><blockquote data-source-ref="{quote['id']}">{escape(quote['text'])}</blockquote>{source_paragraph(overview)}{status}</article>''')
    content = f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span aria-hidden="true">/</span><span aria-current="page">Universe</span></nav>
<section class="section-intro"><p class="eyebrow">IRON STARS / THE UNIVERSE</p><h1 id="title">Beyond the battlefield.</h1><p class="lead">A fractured world. Rival powers. Lives caught between them.</p><p class="lore-opening" data-source-ref="core:b0004">{escape(blocks[4]['text'])}</p></section>
<nav class="lore-sections" aria-label="On this page"><a href="#stories">Stories &amp; transmissions ↓</a><a href="#powers">The factions ↓</a><a href="#history">History ↓</a></nav>
<section id="stories" class="lore-section" aria-labelledby="stories-title"><p class="eyebrow">Voices from the conflict</p><h2 id="stories-title">Stories &amp; transmissions</h2><p class="lore-section-lead">Contracts, field reports, machine memories, and a final call from Canada.</p><div class="lore-grid">{''.join(cards)}</div></section>
<section id="powers" class="lore-section" aria-labelledby="powers-title"><p class="eyebrow">The powers of Iron Stars</p><h2 id="powers-title">Seven factions. Different futures.</h2><div class="lore-factions">{''.join(faction_cards)}</div><p class="lore-meta">Faction background passages and mottos: core rules v0.0.14.</p></section>
<section id="history" class="lore-section" aria-labelledby="history-title"><p class="eyebrow">2030 / THE 2060s</p><h2 id="history-title">How the world fractured</h2><ol class="lore-timeline">{''.join(history)}</ol><p class="lore-source">Source: {escape(doc['filename'])} · “{escape(blocks[676]['text'])}” · Original history wording retained.</p></section>'''
    return [{'slug':'universe', 'name':'Universe', 'description':'Explore the history, factions, stories, and transmissions of the IRON STARS universe.', 'content':content, 'accent':'#f2944a'}] + pages
