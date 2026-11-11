from pathlib import Path
from html import escape
import shutil, zipfile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'stormcast-eternals'
ASSETS.mkdir(exist_ok=True)
names = '''462574312_3843175852592025_1330826141534558483_n.jpg
462540849_792556612924706_5927551931250302279_n.jpg
462567123_917755573537167_3323569031939789208_n.jpg
462545724_1284889852864033_5635064283600828757_n.jpg
462544097_575591991659783_6536762606203746910_n.jpg
462542030_1266729734643920_197632751199793223_n.jpg
462545958_884088427155467_2460200199765407337_n.jpg
462545971_1729660760910721_1227122597661824322_n.jpg
462545891_3918807908444537_19563385552556260_n.jpg
462540883_1063480735042813_4207382217731735670_n.jpg
462544175_1219560799335839_7576725734138590722_n.jpg
462553399_902819554725152_8212830799171003934_n.jpg
462562422_521663754166713_8456764653751973571_n.jpg
462572070_474262438959146_8766541582183179405_n.jpg
462545640_1214928316227127_522362240535722933_n.jpg
462545869_866906781896724_4328404067453402022_n.jpg
462553896_1085604499669127_4887641583233081041_n.jpg
462547805_531674799665542_7925760056151599520_n.jpg
462550294_1715001409264294_2737506315480528358_n.jpg'''.splitlines()
for i, name in enumerate(names, 1):
    shutil.copy2(Path('C:/Users/Niklas/Downloads') / name, ASSETS / f'photo-{i:02}.jpg')

def img(i, alt, eager=False):
    return f'<img src="stormcast-eternals/photo-{i:02}.jpg" alt="{escape(alt)}" width="2016" height="1512" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'

def photo(i, caption):
    return f'<figure><a class="photo" href="stormcast-eternals/photo-{i:02}.jpg" data-caption="{escape(caption)}" aria-label="{escape(caption)} — enlarge photo">{img(i,caption)}<span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{caption}</figcaption></figure>'

header = '''<a class="skip" href="#main">Skip to content</a><div class="page-shell"><header class="site-header"><a class="logo" href="index.html" aria-label="TBD's Dragon Den – home"><div class="logo-mark"><img src="Eldritch%20shadows/IconDragonDenSketchEmbedded.svg" alt="" class="logo-icon"></div><div class="logo-text">TBD's Dragon Den</div></a><nav class="site-nav" aria-label="Main navigation"><a href="index.html#projects">Projects</a><a href="about.html">About</a><a href="contact.html">Contact</a><span class="site-pill">Indie worlds &amp; games</span></nav></header>'''
def page(title, desc, content, gallery=False):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{escape(desc)}"><title>{escape(title)} | TBD's Dragon Den</title><link rel="stylesheet" href="site-header.css"><link rel="stylesheet" href="age-of-sigmar.css">{('<script src="stormcast-eternals/gallery.js" defer></script>' if gallery else '')}</head><body>{header}<main id="main">{content}</main><footer><a href="miniatures.html">← All miniature projects</a><span>TBD’s Dragon Den · A personal miniature collection</span><small>Unofficial fan project. Warhammer Age of Sigmar and World of Warcraft belong to their respective owners.</small></footer></div></body></html>'''

index = '''<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span>/</span><span aria-current="page">Age of Sigmar</span></nav><section class="intro"><p class="eyebrow">The miniature collection / Warbands</p><h1>Warriors of the<br><em>Mortal Realms.</em></h1><p class="lead">My Age of Sigmar warbands, one painted miniature at a time. Explore the models, the colours, and the ideas behind each collection.</p></section><section aria-labelledby="collection"><div class="section-heading"><h2 id="collection">The warbands</h2><span>01 / Collection</span></div><a class="feature" href="stormcast-eternals.html"><div class="feature-image">'''+img(3,'Three painted Stormcast Eternals and their Gryph-hound on ruined stone bases',True)+'''</div><div class="feature-copy"><p class="eyebrow">Stormcast Eternals</p><h2>Forged in lightning.<br><em>Painted in frost.</em></h2><p>A warband with a darker soul: my Stormcast Eternals, painted to resemble the Death Knights of World of Warcraft.</p><span class="tags">Icy blue · Violet · Silver</span><span class="text-link">Explore the warband <b aria-hidden="true">↗</b></span></div></a></section>'''
(ROOT / 'age-of-sigmar.html').write_text(page('Age of Sigmar Warbands','Explore my painted Age of Sigmar warbands, including Death Knight-inspired Stormcast Eternals.',index),encoding='utf-8')

content = '''<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span>/</span><a href="age-of-sigmar.html">Age of Sigmar</a><span>/</span><span aria-current="page">Stormcast Eternals</span></nav><section class="warband-hero"><div><p class="eyebrow">Age of Sigmar / Painted warband</p><h1>Stormcast<br><em>Eternals.</em></h1><p class="lead">The might of the storm. The chill of a Death Knight.</p><p>My Stormcast Eternals warband, painted to resemble the Death Knights from World of Warcraft. Cold blues, deep violet and silver armour bring that inspiration to the Mortal Realms.</p><a class="button" href="#gallery">Explore the photographs <span aria-hidden="true">↓</span></a></div><figure class="hero-photo"><a class="photo" href="stormcast-eternals/photo-10.jpg" data-caption="Dark blue armour, silver shoulders and icy blue eyes" aria-label="Enlarge the dark blue Stormcast miniature">'''+img(10,'Dark blue Stormcast Eternals miniature with a silver crossbow and icy blue eyes',True)+'''<span class="enlarge" aria-hidden="true">↗</span></a><figcaption>Death Knight inspiration, Stormcast silhouette.</figcaption></figure></section><nav class="chapter-nav" aria-label="On this page"><a href="#inspiration">01 / The inspiration</a><a href="#gallery">02 / The warband</a><a href="#close-ups">03 / The details</a></nav><section class="inspiration" id="inspiration"><p class="eyebrow">01 / The inspiration</p><h2>A colder kind of<br><em>Stormcast.</em></h2><div><p>The Death Knight influence lives in the colour palette: blue and violet armour, bright silver weapons, and icy blue details. Dark robes tie the three warriors together, while ruined stone bases give the group a shared setting.</p><div class="palette"><span><i style="--swatch:#244ca6"></i>Cold blue</span><span><i style="--swatch:#653b83"></i>Deep violet</span><span><i style="--swatch:#b7c4ce"></i>Silver steel</span><span><i style="--swatch:#47c6ed"></i>Icy details</span></div></div></section><section id="gallery"><div class="section-heading"><div><p class="eyebrow">02 / The warband</p><h2>Together in the ruins.</h2></div><span>6 photographs</span></div><p>Three armoured warriors and their Gryph-hound. Select a photograph to see the full view.</p><div class="gallery group-gallery">'''
captions = ['Warband view with the Gryph-hound in profile','The three warriors and their Gryph-hound, front view','The warband assembled on ruined stone bases','A rear view of the Gryph-hound with the warriors behind','Gryph-hound profile and silver armour details','The Gryph-hound facing forward with the three Stormcast behind']
content += ''.join(photo(i,c) for i,c in enumerate(captions,1))+'</div></section><section id="close-ups"><div class="section-heading"><div><p class="eyebrow">03 / The details</p><h2>Armour, frost &amp; stone.</h2></div><span>13 photographs</span></div><p>A closer look at each warrior, from the weapons and armour to the robes and bases.</p>'
groups = [('The dark blue warrior','Silver shoulders, a dark robe and a pale face with icy blue eyes.',range(7,11),['Side view of the dark blue warrior and crossbow','Rear view of the dark blue warrior’s robe and silver shoulders','Opposite side of the dark blue warrior with blue robe details','Front view of the dark blue warrior with pale face and icy blue eyes']),('The ice blue warrior','Bright blue armour and a silver crossbow carry the coldest colours in the warband.',range(11,15),['Front view of the ice blue warrior and silver crossbow','Side view of the ice blue armour and dark robe','Rear view of the ice blue warrior with blue robe decoration','Opposite side of the ice blue warrior and stone base']),('The violet warrior','Deep violet armour, a sweeping dark robe and bright blue weapon details.',range(15,20),['Violet warrior aiming the crossbow, with Gryph-hound beside it','Rear view of the violet warrior with silver shoulders and robe details','Side view of the violet armour and raised crossbow','Front view of the violet warrior and ruined stone base','Wider view of the violet warrior with the warband behind'])]
for title,desc,indices,caps in groups:
    content += f'<article class="model"><h3>{title}</h3><p>{desc}</p><div class="gallery">'+''.join(photo(i,c) for i,c in zip(indices,caps))+'</div></article>'
content += '''</section><aside class="endnote"><p class="eyebrow">The collection continues</p><h2>Back to the Mortal Realms.</h2><a class="text-link" href="age-of-sigmar.html">Browse Age of Sigmar warbands <span aria-hidden="true">↗</span></a></aside><dialog class="lightbox" aria-label="Photo viewer"><button class="close" aria-label="Close photo viewer">×</button><img alt=""><div class="viewer-bar"><button class="previous" aria-label="Previous photograph">←</button><p aria-live="polite"></p><button class="next" aria-label="Next photograph">→</button><a class="original" href="">Original ↗</a></div></dialog>'''
(ROOT/'stormcast-eternals.html').write_text(page('Stormcast Eternals — Death Knight Inspiration','My Stormcast Eternals warband, painted to resemble World of Warcraft Death Knights. Explore all 19 original photographs.',content,True),encoding='utf-8')

mini = ROOT/'miniatures.html'
text=mini.read_text(encoding='utf-8')
old='<h3 class="project-title">Warhammer Age of Sigmar</h3>\n            <p class="project-desc">Projekt kommer här.</p>'
new='<h3 class="project-title">Warhammer Age of Sigmar</h3>\n            <p class="project-desc">Mina målade warbands från Mortal Realms.</p>\n            <a href="age-of-sigmar.html" class="btn-ghost">Age of Sigmar warbands <span aria-hidden="true">↗</span></a>'
if old in text: mini.write_text(text.replace(old,new,1),encoding='utf-8')

files=['age-of-sigmar.html','stormcast-eternals.html','age-of-sigmar.css','miniatures.html']+ [str(p.relative_to(ROOT)) for p in ASSETS.rglob('*') if p.is_file()]
for filename in files:
    dest=ROOT/'publicering'/filename
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/filename,dest)
with zipfile.ZipFile(ROOT/'uppdatering-age-of-sigmar.zip','w',zipfile.ZIP_DEFLATED) as z:
    for filename in files: z.write(ROOT/filename,filename)
print(f'Created 2 pages, linked the miniatures index, preserved all {len(names)} originals, staged {len(files)} files and ZIP.')
