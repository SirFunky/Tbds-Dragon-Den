from pathlib import Path
from html import escape
import hashlib
import shutil
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parent
assets = ROOT / 'battletech'
assets.mkdir(exist_ok=True)
sources = [
    '532269950_1058922916231552_3737240148098241739_n.jpg',
    '531398340_1046425610635136_3040306913604302145_n.jpg',
    '531508323_4023530274449385_6946826182870245738_n.jpg',
    '530407722_726311250231708_3228683998601337664_n.jpg',
    '533526606_1393366608395860_4836100069041934822_n.jpg',
    '531801897_23954801264204911_5574913348193723804_n.jpg',
    '532053791_1388613988879683_3363770008717447874_n.jpg',
    '531613146_1758058534811050_1589527819097918421_n.jpg',
]
captions = [
    'Finished miniature, side view: deep red armour, gold details and a green cockpit.',
    'Rear view of the finished miniature on its grass-covered hex base.',
    'The opposite side, showing the metallic weapons and red leg armour.',
    'Front view of the finished miniature, with the green cockpit and grassy base.',
    'Painting in progress: rear view on the painting handle.',
    'Painting in progress: side view with the gold weapon details in place.',
    'Painting in progress: front view before the base was finished.',
    'Painting in progress: an angled view of the red and gold colour scheme.',
]
for i, name in enumerate(sources, 1):
    source = Path('C:/Users/Niklas/Downloads') / name
    original = assets / f'photo-{i:02}.jpg'
    shutil.copy2(source, original)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest()
    with Image.open(source) as image:
        image.thumbnail((900, 1200))
        image.save(assets / f'photo-{i:02}.webp', quality=85)

header = (ROOT / 'self-made-terrain.html').read_text(encoding='utf-8').split('<header class="site-header screen-only">', 1)[1].split('</header>', 1)[0]
def gallery(start, end):
    figures = []
    for i in range(start, end + 1):
        caption = escape(captions[i-1], quote=True)
        with Image.open(assets / f'photo-{i:02}.webp') as image:
            width, height = image.size
        loading = 'fetchpriority="high"' if i == 1 else 'loading="lazy"'
        figures.append(f'<figure><a class="photo" href="battletech/photo-{i:02}.jpg" data-caption="{caption}" aria-label="Enlarge photograph {i}"><img src="battletech/photo-{i:02}.webp" alt="{caption}" width="{width}" height="{height}" {loading} decoding="async"><span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{caption}</figcaption></figure>')
    return '\n'.join(figures)

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BattleTech | TBD's Dragon Den</title>
<meta name="description" content="My BattleTech miniature painting project: red armour, gold details and a green cockpit, from painting handle to finished hex base. Eight photographs.">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="site-header.css">
<link rel="stylesheet" href="battletech/page.css">
<script src="battletech/gallery.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="page-shell">
<header class="site-header screen-only">{header}</header>
<main id="main" class="battle-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span aria-hidden="true">/</span><span aria-current="page">BattleTech</span></nav>
<section class="intro" aria-labelledby="page-title">
<p class="eyebrow">Miniature painting / BattleTech</p>
<h1 id="page-title">BattleTech</h1>
<p>From the painting handle to the tabletop. My BattleTech miniature in deep red armour, with gold details, metallic weapons and a green cockpit — finished with a grassy hex base.</p>
<div class="chapter-links"><a href="#finished">Finished miniature ↓</a><a href="#painting">Painting in progress ↓</a></div>
</section>
<section id="finished" aria-labelledby="finished-title"><div class="gallery-heading"><p class="eyebrow">01 / Ready for the tabletop</p><h2 id="finished-title">The finished miniature</h2><p>Four angles of the completed paintwork. Select a photograph to enlarge it.</p></div><div class="battle-gallery">{gallery(1, 4)}</div></section>
<section id="painting" aria-labelledby="painting-title"><div class="gallery-heading"><p class="eyebrow">02 / At the painting desk</p><h2 id="painting-title">Painting in progress</h2><p>Earlier views on the painting handle, before the grassy base was added.</p></div><div class="battle-gallery">{gallery(5, 8)}</div></section>
<dialog class="lightbox" aria-label="Photo viewer"><button class="close" aria-label="Close photo viewer">×</button><img alt=""><div class="viewer-bar"><button class="previous" aria-label="Previous photograph">←</button><p aria-live="polite"></p><button class="next" aria-label="Next photograph">→</button><a class="original" href="battletech/photo-01.jpg">Original ↗</a></div></dialog>
</main>
<footer><a href="miniatures.html">← Back to Miniature Projects</a></footer>
</div>
</body>
</html>
'''
(ROOT / 'battletech.html').write_text(page, encoding='utf-8')
shutil.copy2(ROOT / 'self-made-terrain/gallery.js', assets / 'gallery.js')
css = (ROOT / 'self-made-terrain/terrain.css').read_text(encoding='utf-8')
for old, new in [('terrain-page', 'battle-page'), ('terrain-breadcrumbs', 'breadcrumbs'), ('terrain-intro', 'intro'), ('terrain-eyebrow', 'eyebrow'), ('terrain-heading', 'gallery-heading'), ('terrain-gallery', 'battle-gallery')]:
    css = css.replace(old, new)
css = css.replace('repeat(3,minmax(0,1fr))', 'repeat(4,minmax(0,1fr))')
css += '''
.chapter-links{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px;font-size:14px}
.chapter-links a{color:var(--accent)}
.battle-page>section+section{margin-top:48px}
.gallery-heading .eyebrow{margin:0 0 12px}
.gallery-heading>p:last-child{line-height:1.6}
.photo:hover .enlarge{background:#166534}
html{scroll-behavior:smooth}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''
(assets / 'page.css').write_text(css, encoding='utf-8')

mini = ROOT / 'miniatures.html'
text = mini.read_text(encoding='utf-8')
if 'href="battletech.html"' not in text:
    marker = '          <article class="project-card">\n            <h3 class="project-title">Gundam Assemble</h3>'
    card = '''          <article class="project-card">
            <h3 class="project-title">BattleTech</h3>
            <p class="project-desc">En röd och guldfärgad BattleTech-miniatyr, från målning till färdig hexbas.</p>
            <a href="battletech.html" class="btn-ghost">BattleTech gallery <span aria-hidden="true">↗</span></a>
          </article>
'''
    assert marker in text
    mini.write_text(text.replace(marker, card + marker), encoding='utf-8')

files = [ROOT / 'miniatures.html', ROOT / 'battletech.html', ROOT / 'style.css', ROOT / 'site-header.css', ROOT / 'Eldritch shadows/IconDragonDenSketchEmbedded.svg', *sorted(assets.iterdir())]
for source in files:
    target = ROOT / 'publicering' / source.relative_to(ROOT)
    target.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(ROOT / 'uppdatering-battletech.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(ROOT))
print(f'Created BattleTech page, eight original photographs, eight optimized previews and upload ZIP ({len(files)} files).')
