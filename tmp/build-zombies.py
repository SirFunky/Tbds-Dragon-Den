from pathlib import Path
import json,html,re,shutil,zipfile,importlib.util
from bs4 import BeautifulSoup
root=Path.cwd()
groups=json.loads(Path('tmp/horror-groups.json').read_text(encoding='utf-8'))
meta=json.loads(Path('tmp/horror-photo-metadata.json').read_text(encoding='utf-8-sig'))
template=Path('expatriated-lilys.html').read_text(encoding='utf-8')
header=template[template.index('    <header'):template.index('    <main')]
css=template[template.index('  <style>'):template.index('  </style>')+len('  </style>')].replace('.lilys','.zombies').replace('.operative-feature { max-width:28rem;', '.operative-feature { max-width:44rem;')
css=css.replace('  </style>','    .zombies .closing-photo { margin-top:2rem; }\n  </style>')
def image(url,alt,lazy=True):
 name=url.rsplit('/',1)[1]; dims=meta[name]; web=name.replace('.jpg','-web.jpg')
 return f'<a href="deadwalker-zombies/{name}" aria-label="{html.escape(alt)} — full-size photo"><img src="deadwalker-zombies/{web}" alt="{html.escape(alt)}" width="{dims["width"]}" height="{dims["height"]}"'+(' loading="lazy"' if lazy else ' fetchpriority="high"')+' decoding="async" /></a>'
body='''      <p><a href="kill-team.html">← Kill Team</a></p>
      <p class="project-tagline">Deadwalker Zombies · Poxwalker proxies · <time datetime="2024-09-13">September 13, 2024</time></p>
      <h1>My Last Horror-Themed Kill Team Joins the Fray!</h1>
      <p class="intro">My idea was to create three Kill Teams inspired by horror creatures I love. First came my Necrons, inspired by <em>Terminator</em>. Then came my Tyranids, inspired by the Xenomorphs. Finally, here are my Deadwalker Zombies, used as Poxwalker proxies — a Kill Team inspired by zombies!</p>
'''
body+='<figure class="team-photo">'+image(groups[0]['images'][0],'The complete painted Deadwalker Zombies Kill Team, used as Poxwalker proxies',False)+'<figcaption>The Deadwalker Zombies, ready to join the fray.</figcaption></figure>\n'
body+='''<section class="project-card" aria-labelledby="painting-heading"><h2 id="painting-heading" class="project-title">The painting challenge</h2><p>I painted the whole gang following Games Workshop’s Poxwalkers colour scheme. For an extra challenge, I used only primer, Contrast paints and Dry paints.</p></section>
<section aria-labelledby="roster-heading"><h2 id="roster-heading">Meet the zombies</h2><p>Explore each group below. Open the extra angles or select any photo for a full-size view.</p><ul class="roster">'''
for group in groups[1:-1]:
 group['id']=re.sub('[^a-z0-9]+','-',group['name'].lower()).strip('-')
 body+=f'<li><a href="#{group["id"]}">{html.escape(group["name"])}</a></li>'
body+='</ul></section><div class="operative-list">\n'
for group in groups[1:-1]:
 name=html.escape(group['name']); gid=group['id']
 body+=f'<section class="project-card operative" id="{gid}" aria-labelledby="{gid}-heading"><h2 class="project-title" id="{gid}-heading">{name}</h2><div class="operative-feature">'+image(group['images'][0],f'{group["name"]}, painted Deadwalker Zombie miniatures — view 1')+'</div><details><summary>More angles ('+str(len(group['images'])-1)+')</summary><div class="operative-photos">'
 for i,u in enumerate(group['images'][1:],2): body+=image(u,f'{group["name"]}, painted Deadwalker Zombie miniatures — view {i}')
 body+='</div></details><p class="back-to-roster"><a href="#roster-heading">↑ Back to the zombies</a></p></section>\n'
body+='</div><section class="closing-photo" aria-labelledby="fishy-heading"><h2 id="fishy-heading">Something Smells Fishy Here!</h2><figure class="team-photo">'+image(groups[-1]['images'][0],'A wider view of the hobby table, with painted miniatures and scenery')+'<figcaption>A final look across the hobby table.</figcaption></figure></section>'
body+='''<p class="source-note">Originally shared on <a href="https://tbdshobbycorner.wordpress.com/2024/09/13/my-last-horror-teamed-kill-team-joins-the-fray/">TBD’s Hobby Corner</a>.</p><p><a href="kill-team.html">← Back to Kill Team</a></p>'''
page='''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="My zombie-inspired Kill Team: Deadwalker Zombies used as Poxwalker proxies, painted with only primer, Contrast and Dry paints. Explore all 38 photos." />
  <title>Deadwalker Zombies — Horror-Themed Kill Team | TBD's Dragon Den</title>
  <link rel="stylesheet" href="style.css" />
  <link rel="stylesheet" href="site-header.css" />
'''+css+'\n</head>\n<body>\n  <div class="page-shell">\n'+header+'    <main class="zombies">\n'+body+'\n    </main>\n  </div>\n</body>\n</html>\n'
Path('deadwalker-zombies.html').write_text(page,encoding='utf-8')
p=Path('kill-team.html');s=p.read_text(encoding='utf-8');anchor='        <a href="hierotek-circle.html"'
if 'href="deadwalker-zombies.html"' not in s:
 pos=s.index(anchor);s=s[:pos]+'        <a href="deadwalker-zombies.html" class="btn-ghost" lang="en">Deadwalker Zombies – Horror-Themed Kill Team <span aria-hidden="true">↗</span></a>\n'+s[pos:];p.write_text(s,encoding='utf-8')
files=[Path('kill-team.html'),Path('deadwalker-zombies.html')]+sorted(Path('deadwalker-zombies').glob('*.jpg'))
for p in files:
 target=Path('publicering')/p;target.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,target)
with zipfile.ZipFile('uppdatering-deadwalker-zombies.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.as_posix())
print(f'Created page with {len(groups)-2} named groups and {sum(len(g["images"]) for g in groups)} photos; packaged {len(files)} files.')
# Check every local page reference, including fragments and filename case.
spec=importlib.util.spec_from_file_location('publication','prepare-publication.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
for path in [Path('deadwalker-zombies.html'),Path('kill-team.html')]:
 parser=mod.References();parser.feed(path.read_text(encoding='utf-8'))
 for url in parser.links:mod.resolve_local(root/path,url)
 for link in BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser').select('a[href^="#"]'):
  assert link['href'][1:] in parser.ids,link
print('All local links, images, filename case and section links passed.')
with zipfile.ZipFile('uppdatering-deadwalker-zombies.zip') as z:
 assert z.testzip() is None
 for p in files:
  assert z.read(p.as_posix())==p.read_bytes()==(Path('publicering')/p).read_bytes()
print('ZIP contents and publication copies match the source files.')
