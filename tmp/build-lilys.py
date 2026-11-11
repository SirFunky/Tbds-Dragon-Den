from pathlib import Path
import json,html,re
from bs4 import BeautifulSoup
root=Path.cwd()
groups=json.loads(Path('tmp/expatriated-lilys-groups.json').read_text(encoding='utf-8'))
meta=json.loads(Path('tmp/lilys-photo-metadata.json').read_text(encoding='utf-8-sig'))
template=Path('hierotek-circle.html').read_text(encoding='utf-8')
header=template[template.index('    <header'):template.index('    <main')]
def image(url,alt,lazy=True):
 name=url.rsplit('/',1)[1]; dims=meta[name]
 web=name.replace('.jpg','-web.jpg')
 return f'<a href="expatriated-lilys/{name}" aria-label="{html.escape(alt)} — full-size photo"><img src="expatriated-lilys/{web}" alt="{html.escape(alt)}" width="{dims["width"]}" height="{dims["height"]}"'+(' loading="lazy"' if lazy else ' fetchpriority="high"')+' decoding="async" /></a>'
body='''      <p><a href="kill-team.html">← Kill Team</a></p>
      <p class="project-tagline">Adeptus Sororitas · <time datetime="2024-08-14">August 14, 2024</time></p>
      <h1>We Welcome the Expatriated Lily’s</h1>
      <p class="intro">My Adeptus Sororitas Kill Team, the Expatriated Lily’s, is finally finished. This was a challenging project that took several months, but I’m proud to present these fierce ladies!</p>
'''
body+='<figure class="team-photo">'+image(groups[0]['images'][0],'The Expatriated Lily’s — the complete painted Adeptus Sororitas Kill Team',False)+'<figcaption>The Expatriated Lily’s, ready to take the field.</figcaption></figure>\n'
body+='<details class="team-angle"><summary>Another view of the team</summary><div class="team-photo">'+image(groups[0]['images'][1],'The complete Expatriated Lily’s team, alternate view')+'</div></details>\n'
body+='<section aria-labelledby="roster-heading"><h2 id="roster-heading">Meet the team</h2><p>Ten Battle Sisters and their Cherub. Select a name to see the miniature, or open any photo for a closer look.</p><ul class="roster">'
for g in groups[1:]:
 name=g['heading'].split()[-1] if g['heading']!='Battle Sister Superior Johanna D Steiner' else 'Johanna D Steiner'
 g['name']=name;g['id']=re.sub('[^a-z0-9]+','-',name.lower())
 body+=f'<li><a href="#{g["id"]}">{html.escape(name)}</a></li>'
body+='</ul></section><div class="operative-list">\n'
for g in groups[1:]:
 name=g['name']; role=g['heading'][:-len(name)].strip() if name!='Cherub' else 'Cherub'
 body+=f'<section class="project-card operative" id="{g["id"]}" aria-labelledby="{g["id"]}-heading"><p class="project-tagline">{role}</p><h2 class="project-title" id="{g["id"]}-heading">{name}</h2><div class="operative-feature">'+image(g['images'][0],f'{g["heading"]}, painted miniature — view 1')+'</div><details><summary>More angles ('+str(len(g['images'])-1)+')</summary><div class="operative-photos">'
 for i,u in enumerate(g['images'][1:],2): body+=image(u,f'{g["heading"]}, painted miniature — view {i}')
 body+='</div></details><p class="back-to-roster"><a href="#roster-heading">↑ Back to the team</a></p></section>\n'
body+='</div><p class="source-note">Originally shared on <a href="https://tbdshobbycorner.wordpress.com/2024/08/14/we-welcome-the-the-expatriated-lilys/">TBD’s Hobby Corner</a>.</p><p><a href="kill-team.html">← Back to Kill Team</a></p>'
css='''    .lilys { max-width:58rem; margin:0 auto 3rem; }
    .lilys p { line-height:1.65; max-width:70ch; }
    .lilys h1 { max-width:22ch; font-size:clamp(2rem,5vw,3rem); line-height:1.12; }
    .lilys a:focus-visible, .lilys summary:focus-visible { outline:2px solid #86efac; outline-offset:4px; }
    .lilys img { display:block; width:100%; height:auto; border-radius:.6rem; }
    .team-photo { margin:1.5rem 0; }
    .lilys figcaption, .source-note, .back-to-roster { font-size:.875rem; color:var(--text-muted); }
    .lilys figcaption { margin-top:.7rem; }
    .roster { display:flex; flex-wrap:wrap; gap:.6rem; padding:0; list-style:none; margin:1.2rem 0 2rem; }
    .roster a { display:block; padding:.5rem .8rem; border:1px solid var(--border-subtle); border-radius:999px; text-decoration:none; }
    .roster a:hover { border-color:var(--accent); background:var(--accent-soft); }
    .operative-list { display:grid; gap:1.5rem; }
    .operative { scroll-margin-top:1.5rem; }
    .operative-feature { max-width:28rem; margin:1.25rem auto; }
    .operative-photos { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr)); gap:.75rem; padding-top:1rem; }
    .lilys summary { cursor:pointer; padding:.8rem 0; color:var(--text-main); font-weight:600; }
    .lilys details { border-top:1px solid var(--border-subtle); }
    .lilys .project-tagline { margin-bottom:.4rem; }
    .lilys .project-title { font-size:1.6rem; }
    #roster-heading { scroll-margin-top:1.5rem; }
    .source-note { margin-top:2rem; }
'''
page='''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Meet the Expatriated Lily’s, my painted Adeptus Sororitas Kill Team: ten Battle Sisters and a Cherub, with photos of every miniature." />
  <title>The Expatriated Lily’s | TBD's Dragon Den</title>
  <link rel="stylesheet" href="style.css" />
  <link rel="stylesheet" href="site-header.css" />
  <style>
'''+css+'''  </style>
</head>
<body>
  <div class="page-shell">
'''+header+'    <main class="lilys">\n'+body+'\n    </main>\n  </div>\n</body>\n</html>\n'
Path('expatriated-lilys.html').write_text(page,encoding='utf-8')
p=Path('kill-team.html');s=p.read_text(encoding='utf-8');anchor='        <a href="hierotek-circle.html"'
pos=s.index(anchor)
s=s[:pos]+'        <a href="expatriated-lilys.html" class="btn-ghost" lang="en">The Expatriated Lily’s – Adeptus Sororitas <span aria-hidden="true">↗</span></a>\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('Created page with',len(BeautifulSoup(page,'html.parser').find_all('img'))-1,'article photos; updated Kill Team navigation.')
