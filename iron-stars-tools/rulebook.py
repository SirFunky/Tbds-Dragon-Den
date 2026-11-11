"""Render the selected core source as a traceable alpha reference, not finalized rules."""
import hashlib
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [
    ('basics','The basics',10,46),
    ('terrain','Terrain & movement',48,94),
    ('combat','Combat',95,121),
    ('actions','Actions',123,130),
    ('damage','Damage & destruction',132,139),
    ('morale','Morale & suppression',141,153),
    ('traits','Trait examples',155,159),
    ('getting-started','Getting started',161,172),
    ('construction','Building a unit',173,226),
    ('glossary','Keyword glossary',228,243),
    ('game-sizes','Game sizes & design notes',245,251),
    ('secure-the-relay','Secure the Relay',253,265),
]
# Editorial warnings identify ambiguity; the adjacent source text is unchanged.
NOTES = {
 'core:b0012': ('Objective marker dimensions', 'The source gives 25–40 mm diameter and 2–4 cm radius as alternatives. These are different sizes. Agree on your marker size before play.'),
 'core:b0110': ('Close combat needs clarification', 'The source limits which weapons may be used in melee, but does not fully define charging, engagement distance, or disengaging. No extra procedure has been added here.'),
 'core:b0123': ('Overwatch is not defined', 'Other rules mention Overwatch, but this core document does not give its action cost, trigger, or resolution procedure.'),
 'core:b0135': ('Destruction timing needs clarification', 'The source delays removal until round end, but its wording about completing an activation is unclear. The interaction with last attacks, spawning, and revival also needs a decision.'),
 'core:b0145': ('Morale check needs confirmation', 'As written, a result below current STR causes suppression. Higher-STR units therefore fail more often. The source wording is preserved; no balance change has been made.'),
 'core:b0156': ('Two versions of Overdrive', 'This example grants a third action and causes damage on a 1. The system cost table instead gives failure and damage on 1–3, and an extra action only on 4–6. Neither passage is known to be newer.'),
 'core:b0197:r2': ('Overdrive differs elsewhere', 'The earlier trait example gives a third action with damage only on a 1. This table uses a success test. The source does not establish which version replaces the other.'),
 'core:b0197:r8': ('Fabricator timing differs', 'This table says per turn. The glossary’s Fabricator entry instead uses an action and requires an adjacent target. Whether Fabricator Swarm is a separate exception needs confirmation.'),
 'core:b0197:r9': ('Veil Phase differs elsewhere', 'This table cancels the first hit. The glossary instead cancels all hits from one attack, once per game. These effects have not been combined.'),
 'core:b0197:r10': ('Deep Strike has more detail elsewhere', 'The glossary adds a round-2-or-later limit and requires more than 20 cm from enemy units. Read that entry before using the shorter description here.'),
 'core:b0235:r4': ('Fabricator has another description', 'The earlier Fabricator Swarm cost entry describes deploying or repairing per turn. This glossary describes an adjacent repair or deployment as an action. The relationship needs confirmation.'),
 'core:b0235:r7': ('Veil Phase has another description', 'The cost table cancels the first hit of the game. This glossary cancels a whole attack. There is no confirmed revision order within this document.'),
}


def anchor(ref):
    return 'rule-' + ref.replace(':','-')


def selected_data():
    path=ROOT/'iron-stars-source/extracted/core.json'
    source=json.loads(path.read_text(encoding='utf-8'))
    policy=json.loads((ROOT/'iron-stars-review/source-precedence.json').read_text(encoding='utf-8'))
    evidence=next(e for e in policy['evidence'] if e['source_id']=='core')
    original=ROOT/'iron-stars-source/originals'/source['filename']
    assert hashlib.sha256(original.read_bytes()).hexdigest()==source['sha256']==evidence['sha256'], 'Core source changed; review its precedence before rebuilding.'
    chapters=[]
    for slug,title,start,end in CHAPTERS:
        chapter_blocks=[b for b in source['blocks'] if start<=int(b['id'].split(':b')[1])<=end]
        chapters.append({'id':slug,'title':title,'blocks':chapter_blocks})
    return {'schema_version':1,'title':'IRON STARS core rulebook','version':'0.0.14',
            'status':'alpha-source-reference','finalized':False,
            'source':{'id':'core','filename':source['filename'],'sha256':source['sha256']},
            'scope':'Core gameplay, construction, glossary, and quick-start mission. Faction profiles and setting history are reserved for their own sections.',
            'editorial_notes':{ref:{'title':title,'text':text,'status':'requires-review'} for ref,(title,text) in NOTES.items()},
            'chapters':chapters,
            'author_additions':json.loads((ROOT/'iron-stars-tools/approved-rules.json').read_text(encoding='utf-8'))['rules']}


def glossary_terms(data):
    terms={r['name']:anchor(r['id']) for r in data.get('author_additions',[]) if r['status']=='approved'}
    glossary=next(c for c in data['chapters'] if c['id']=='glossary')
    for block in glossary['blocks']:
        if block['kind']!='table': continue
        for row in block['rows'][1:]:
            name=row['cells'][0]['text'].strip()
            if not name: continue
            # Aliases change navigation labels only; source names stay exact.
            aliases={name}
            name_base=re.sub(r'\s*\(.*?\)|:$','',name).strip()
            aliases.add(name_base)
            if name_base.endswith(' X'): aliases.add(name_base[:-2])
            if name_base=='Linked Costing': aliases={'Linked Costing'}
            if name.startswith('FP '): aliases={'FP','Firepower'}
            if name.startswith('ME '): aliases={'ME','Melee'}
            if name=='Uniqe': aliases={'Uniqe','Unique'}
            if name.startswith('Blast ('): aliases={'Blast (X)'}
            for alias in aliases:
                if alias: terms.setdefault(alias,anchor(row['id']))
    return terms


def render_rulebook():
    data=selected_data()
    out=ROOT/'iron-stars/data/rulebook.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    terms=glossary_terms(data)
    lookup={name.casefold():target for name,target in terms.items()}
    pattern=re.compile(r'(?<!\w)('+ '|'.join(re.escape(k) for k in sorted(terms,key=len,reverse=True))+r')(?!\w)',re.I)

    def rich(text, current=None):
        parts=[]; cursor=0
        for match in pattern.finditer(text):
            parts.append(escape(text[cursor:match.start()]))
            target=lookup[match.group().casefold()]
            word=escape(match.group())
            parts.append(word if target==current else f'<a class="keyword-ref" href="#{target}">{word}</a>')
            cursor=match.end()
        parts.append(escape(text[cursor:]))
        return ''.join(parts).replace('\n','<br>')

    def note(ref):
        if ref not in NOTES: return ''
        title,text=NOTES[ref]
        return f'<aside class="rule-note" aria-label="Rule needs review"><strong>Needs review · {escape(title)}</strong><p>{escape(text)}</p></aside>'

    def share(ref,label):
        return f'<a class="permalink" href="#{anchor(ref)}" aria-label="Link to {escape(label,quote=True)}"><span aria-hidden="true">#</span></a>'

    def table_html(table,title):
        ref=table['id']; ident=anchor(ref)
        rows=table['rows']; html=[f'<div id="{ident}" class="table-wrap" role="region" aria-label="{escape(title,quote=True)} table" tabindex="0"><table><caption>{escape(title)} {share(ref,title)}</caption>']
        for ri,row in enumerate(rows):
            row_id=anchor(row['id'])
            attrs='' if ri==0 else f' id="{row_id}" data-search-entry data-search-title="{escape(title,quote=True)}"'
            html.append(('<thead>' if ri==0 else '<tbody>' if ri==1 else '')+f'<tr{attrs}>')
            for ci,cell in enumerate(row['cells']):
                value=cell['text']
                tag='th' if ri==0 or ci==0 else 'td'
                scope=' scope="col"' if ri==0 else ' scope="row"' if ci==0 else ''
                span=f' colspan="{cell["column_span"]}"' if cell.get('column_span',1)>1 else ''
                html.append(f'<{tag}{scope}{span} data-source-cell="{cell["id"]}"><span class="source-text">{rich(value,row_id)}</span>')
                if ri and ci==0 and value.strip(): html.append(share(row['id'],value))
                if ci==len(row['cells'])-1: html.append(note(row['id']))
                html.append(f'</{tag}>')
            html.append('</tr>'+('</thead>' if ri==0 else ''))
        html.append(('</tbody>' if len(rows)>1 else '')+'</table></div>')
        return ''.join(html)

    toc=''.join(f'<li><a href="#{c["id"]}"><span>{i:02}</span>{escape(c["title"])}</a></li>' for i,c in enumerate(data['chapters'],1))
    glossary_nav=''.join(f'<a href="#{target}">{escape(name)}</a>' for name,target in sorted(terms.items(),key=lambda x:x[0].lower()) if name not in ('ME','FP','Uniqe'))
    articles=[]
    for number,chapter in enumerate(data['chapters'],1):
        parts=[f'<section id="{chapter["id"]}" class="rule-chapter" aria-labelledby="chapter-{chapter["id"]}"><p class="eyebrow">Chapter {number:02}</p><h2 id="chapter-{chapter["id"]}">{escape(chapter["title"])} <a class="permalink" href="#{chapter["id"]}" aria-label="Link to chapter {number}">#</a></h2>']
        title=chapter['title']
        if chapter['id']=='morale': parts.append('<p class="module-label">Optional module · As labeled in the source</p>')
        if chapter['id']=='glossary': parts.append(f'<nav class="glossary-jump" aria-label="Keyword index">{glossary_nav}</nav>')
        for block in chapter['blocks']:
            ref=block['id']; ident=anchor(ref)
            if block['kind']=='paragraph':
                text=block['text']
                if not text.strip(): continue
                parts.append(note(ref))
                style=block.get('style','')
                if style.startswith('heading'):
                    level=min(5,int(style.rsplit(' ',1)[1])+1)
                    title=text.strip()
                    parts.append(f'<h{level} id="{ident}" data-search-entry data-search-title="{escape(title,quote=True)}"><span class="source-text" data-source-ref="{ref}">{rich(text,ident)}</span> {share(ref,title)}</h{level}>')
                else:
                    css=' class="source-list-item"' if block.get('numbering') else ''
                    parts.append(f'<p id="{ident}"{css} data-search-entry data-search-title="{escape(title,quote=True)}"><span class="source-text" data-source-ref="{ref}">{rich(text,ident)}</span></p>')
            elif block['kind']=='table': parts.append(table_html(block,title))
            elif block.get('embedded_tables'):
                parts.extend(table_html(t,'Suggested miniature sources') for t in block['embedded_tables'])
            elif block.get('text','').strip():
                parts.append(f'<p id="{ident}" data-search-entry data-search-title="{escape(title,quote=True)}"><span class="source-text" data-source-ref="{ref}">{rich(block["text"],ident)}</span></p>')
            for addition in data['author_additions']:
                if addition['status']!='approved' or addition['after']!=ref:continue
                addition_id=anchor(addition['id'])
                effects=''.join(f'<li class="source-text">{rich(text,addition_id)}</li>' for text in addition['effects'])
                parts.append(f'<section id="{addition_id}" class="author-rule" data-search-entry data-search-title="{escape(addition["name"],quote=True)}" data-author-source="{escape(addition["source_ref"],quote=True)}"><p class="eyebrow">Author-approved addition · {escape(addition["approved_on"])}</p><h3><span class="source-text">{escape(addition["name"])}</span> {share(addition["id"],addition["name"])}</h3><ul>{effects}</ul></section>')
        parts.append(f'<a class="back-to-contents" href="#rulebook-top">↑ Back to contents</a></section>')
        articles.append(''.join(parts))
    return f'''<nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Iron Stars</a><span aria-hidden="true">/</span><span aria-current="page">Rules</span></nav>
<section id="rulebook-top" class="rulebook-intro" aria-labelledby="title"><div><p class="eyebrow">THE FIELD MANUAL / CORE RULES</p><h1 id="title">Know the battlefield.</h1><p class="lead">The core rules in one searchable reference. Read in order, jump to a chapter, or look up a keyword during play.</p></div><span class="version-tag">v0.0.14 <small>ALPHA</small></span></section>
<div class="reference-notice"><strong>Alpha source reference</strong><p>Based on core rulebook v0.0.14, the latest supplied core source. Original document wording is retained. Author-approved additions are labeled separately. Amber notes identify passages that still need clarification; those passages are not finalized rules. Faction profiles and setting history will have their own sections.</p></div>
<div class="rulebook-layout"><aside class="rulebook-sidebar"><nav aria-label="Rulebook chapters"><h2>Contents</h2><ol>{toc}</ol></nav><a class="text-link" href="#glossary">Open keyword glossary ↗</a><p class="sidebar-note">Source: IRON STARS core rules v0.0.14 (Alpha).</p></aside>
<div class="rulebook-body"><section class="search-panel" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Find a rule</h2><button class="print-rules" type="button" hidden>Print rulebook</button></div><label for="rule-search">Search chapters, tables, and keywords</label><div class="search-controls"><input id="rule-search" type="search" placeholder="Try movement, Piercing, or Overdrive…" autocomplete="off" disabled aria-describedby="search-status"><button id="clear-search" type="button" disabled>Clear</button></div><p id="search-status" role="status" aria-live="polite">Search becomes available when JavaScript is enabled.</p><noscript><p>All chapters and keyword links work without JavaScript. Use your browser’s Find command to search and its Print command to print.</p></noscript><ol id="search-results" hidden aria-label="Search results"></ol></section>
{''.join(articles)}<div class="rulebook-source"><h2>About this reference</h2><p>Transcribed from {escape(data['source']['filename'])}. Chapter grouping, navigation, and review notes are editorial additions. Author-approved additions are separately labeled and dated; they are not part of the original DOCX. Version 0.0.14 is taken from the supplied filename; the document title identifies the rules as Alpha.</p></div></div></div>'''
