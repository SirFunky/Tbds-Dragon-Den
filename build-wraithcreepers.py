from pathlib import Path
from html import escape
import re, json, shutil, zipfile

R=Path(__file__).resolve().parent
A='drepurs-wraithcreepers'
urls=json.loads((R/'tmp/underworlds-images.json').read_text())
names=[u.rsplit('/',1)[1] for u in urls]
source='https://tbdshobbycorner.wordpress.com/2024/09/29/my-first-warhammer-underworlds-warband/'
template=(R/'stormcast-eternals.html').read_text(encoding='utf-8')
header=template.split('<body>')[1].split('<main id="main">')[0]

def img(i,alt,eager=False):
    return f'<img src="{A}/web/{names[i]}" alt="{escape(alt)}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'
def photo(i,caption):
    return f'<figure><a class="photo" href="{A}/{names[i]}" data-caption="{escape(caption)}" aria-label="Enlarge: {escape(caption)}">{img(i,caption)}<span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{escape(caption)}</figcaption></figure>'

content='''<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span>/</span><a href="age-of-sigmar.html">Age of Sigmar</a><span>/</span><span aria-current="page">Drepur’s Wraithcreepers</span></nav>
<section class="warband-hero"><div><p class="eyebrow">Warhammer Underworlds / My first warband</p><h1>Drepur’s<br><em>Wraithcreepers.</em></h1><p class="lead">Four restless spirits.<br>One painted warband.</p><p>My first Warhammer Underworlds warband, collected here with a closer look at each of its four fighters.</p><a class="button" href="#fighters">Meet the warband <span aria-hidden="true">↓</span></a></div><figure class="hero-photo"><a class="photo" href="drepurs-wraithcreepers/20240929_124806.jpg" data-caption="Drepur’s Wraithcreepers — the complete painted warband" aria-label="Enlarge the complete painted warband">'''+img(17,'The four painted Wraithcreepers, with dark cloaks, turquoise spirits and textured bases',True)+'''<span class="enlarge" aria-hidden="true">↗</span></a><figcaption>The complete warband, at the painting desk.</figcaption></figure></section>
<nav class="chapter-nav" aria-label="On this page"><a href="#painting">01 / The colours</a><a href="#fighters">02 / The fighters</a><a href="#warband">03 / Together</a></nav>
<section class="inspiration" id="painting"><p class="eyebrow">01 / The colours</p><h2>Dark cloth.<br><em>Ghostly green.</em></h2><div><p>Black and blue-grey cloaks frame bright turquoise spirits. Pale bone and metallic weapons stand out against the dark fabric, while textured grey bases and small patches of greenery tie the four miniatures together.</p><div class="palette"><span><i style="--swatch:#262e38"></i>Dark cloaks</span><span><i style="--swatch:#37bda8"></i>Spectral turquoise</span><span><i style="--swatch:#d9d1ad"></i>Pale bone</span><span><i style="--swatch:#81888c"></i>Weathered metal</span></div></div></section>
<section id="fighters"><div class="section-heading"><div><p class="eyebrow">02 / The fighters</p><h2>Faces of the haunting.</h2></div><span>4 fighters · 16 photographs</span></div><p>Select a photograph to inspect the original. Explore each fighter from four angles.</p><nav class="fighter-nav" aria-label="Fighters">'''
groups=[('viceroy-drepur','Viceroy Drepur',1),('the-patrician','The Patrician',5),('sir-haqfel','Sir Haqfel',9),('grodrig-the-lance','Grodrig the Lance',13)]
content+=''.join(f'<a href="#{id}">{name} <span aria-hidden="true">↘</span></a>' for id,name,_ in groups)+'</nav>'
for n,(id,name,start) in enumerate(groups,1):
    content+=f'<article class="model" id="{id}"><div class="section-heading"><h3>{name}</h3><span>0{n} / Fighter study</span></div><div class="fighter-study">{photo(start,name+" — painted miniature")}'
    content+='<div class="alternate-views"><p class="eyebrow">Around the miniature</p>'+''.join(photo(i,f'{name} — alternate view {i-start}') for i in range(start+1,start+4))+'</div></div></article>'
content+='</section><section id="warband"><div class="section-heading"><div><p class="eyebrow">03 / Together</p><h2>A haunting at the hobby desk.</h2></div><span>2 photographs</span></div><div class="together">'+photo(17,'Drepur’s Wraithcreepers — the four fighters together')+photo(0,'The hobby desk — the warband and scenery')+'''</div></section><aside class="endnote"><p class="eyebrow">From the hobby journal</p><h2>The first step into Underworlds.</h2><p>Originally shared on TBD’s Hobby Corner on <time datetime="2024-09-29">29 September 2024</time>.</p><a class="text-link" href="'''+source+'''">Read the original post <span aria-hidden="true">↗</span></a></aside>
<dialog class="lightbox" aria-label="Photo viewer"><button class="close" aria-label="Close photo viewer">×</button><img alt=""><div class="viewer-bar"><button class="previous" aria-label="Previous photograph">←</button><p aria-live="polite"></p><button class="next" aria-label="Next photograph">→</button><a class="original" href="">Original ↗</a></div></dialog>'''
page='''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Drepur’s Wraithcreepers | TBD’s Dragon Den</title><meta name="description" content="My first Warhammer Underworlds warband: Drepur’s Wraithcreepers. Explore all four painted fighters and 18 photographs."><link rel="stylesheet" href="site-header.css"><link rel="stylesheet" href="age-of-sigmar.css"><link rel="stylesheet" href="drepurs-wraithcreepers/page.css"><script src="drepurs-wraithcreepers/gallery.js" defer></script></head><body>'''+header+'<main id="main">'+content+'''</main><footer><a href="age-of-sigmar.html">← Age of Sigmar warbands</a><span>TBD’s Dragon Den · The miniature collection</span><small>Unofficial fan project. Warhammer and Warhammer Underworlds belong to Games Workshop.</small></footer></div></body></html>'''
(R/'drepurs-wraithcreepers.html').write_text(page,encoding='utf-8')
shutil.copy2(R/'stormcast-eternals/gallery.js',R/A/'gallery.js')
index=R/'age-of-sigmar.html'
s=index.read_text(encoding='utf-8')
if 'href="drepurs-wraithcreepers.html"' not in s:
    card='''<a class="feature" style="margin-top:28px" href="drepurs-wraithcreepers.html"><div class="feature-image">'''+img(17,'The complete painted Drepur’s Wraithcreepers warband')+'''</div><div class="feature-copy"><p class="eyebrow">Warhammer Underworlds</p><h2>Drepur’s<br><em>Wraithcreepers.</em></h2><p>My first Underworlds warband. Four spectral fighters, dark cloaks and ghostly turquoise details.</p><span class="tags">4 fighters · 18 photographs</span><span class="text-link">Explore the warband <b aria-hidden="true">↗</b></span></div></a>'''
    s=s.replace('</section></main>',card+'</section></main>')
    index.write_text(s,encoding='utf-8')
files=['drepurs-wraithcreepers.html','age-of-sigmar.html']+[str(p.relative_to(R)) for p in (R/A).rglob('*') if p.is_file()]
for f in files:
    dest=R/'publicering'/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,dest)
with zipfile.ZipFile(R/'uppdatering-drepurs-wraithcreepers.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(R/f,f)
# Standalone private Sites presentation; collection links lead to this local gallery.
D=R/'wraithcreepers-site/dist';D.mkdir(parents=True,exist_ok=True)
standalone=page.replace('href="index.html"','href="index.html"').replace('href="index.html#projects"','href="#fighters"').replace('href="about.html"',f'href="{source}"').replace('>About</a>','>Hobby journal</a>').replace('href="contact.html"','href="#warband"').replace('>Contact</a>','>Photographs</a>').replace('href="miniatures.html"','href="index.html"').replace('href="age-of-sigmar.html"','href="index.html"')
(D/'index.html').write_text(standalone,encoding='utf-8')
for f in ['site-header.css','age-of-sigmar.css']:shutil.copy2(R/f,D/f)
shutil.copytree(R/A,D/A,dirs_exist_ok=True)
logo='Eldritch shadows/IconDragonDenSketchEmbedded.svg'
(D/'Eldritch shadows').mkdir(exist_ok=True);shutil.copy2(R/logo,D/logo)
print('Created warband page, collection link, publication files, ZIP and standalone Site.')
