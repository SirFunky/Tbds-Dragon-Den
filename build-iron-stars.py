"""Build the Iron Stars gallery and its Inleed upload package."""
from pathlib import Path
from html import escape
import hashlib
import shutil
import zipfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
assets = ROOT / 'iron-stars'
assets.mkdir(exist_ok=True)
sources = [
    '539304855_1722389271753975_1370274980362936359_n.jpg',
    '538795628_1147464077439632_8192838944478267330_n.jpg',
    '539421787_1977962932742554_3065334844455515603_n.jpg',
    '541235569_823894693301816_8038701982090708505_n.jpg',
    '540984825_1220220812967680_7279424219753669505_n.jpg',
    '539452147_1827367744803946_918386588209174577_n.jpg',
    '541229874_1786164312023469_5857857544768703510_n.jpg',
    '542399445_632094606327985_3653975128927809445_n.jpg',
    '546456393_785608380683764_2758696123514258914_n.jpg',
    '552054427_1362763578751636_8699919362569790262_n.jpg',
    '553335678_1914162225861631_843756406626907689_n.jpg',
    '649722211_899011812951981_4194690949841746061_n.jpg',
    '649634781_925494290397742_1415150098919770599_n.jpg',
    '653553150_1409128420961553_1122459524431990313_n.jpg',
    '617328889_1239211811419364_8500582424405769974_n.jpg',
]
captions = [
    'The tabletop setup: a city battlefield surrounded by groups of mech miniatures.',
    'The Iron Stars collection, with deep red armour, gold details and grass-covered bases.',
    'Another view of the collection, with the tall red mech against the city terrain.',
    'A blue-and-gold mech faces a tall red-and-gold mech in front of the city terrain.',
    'A wider tabletop view, with the blue mech in front of the red-and-gold collection.',
    'Front view of the blue-and-gold mech with its rifle and shield, alongside the red mechs.',
    'Rear view of the tall red-and-gold mech, showing its twin gold engine details.',
    'A wide view of the city battlefield, with mech miniatures arranged around all sides of the table.',
    'Four miniatures on the painting desk, with paint pots, brushes and basing materials behind them.',
    'An expanded city battlefield with buildings, a runway, roads, trees and ponds.',
    'The bare textured battlefield mat laid out on the table before adding terrain.',
    'The mech collection lined up in front of a battlefield with buildings, trees and orange rock formations.',
    'Grey mech miniatures beside the winding river and road, with a bridge and buildings behind them.',
    'A closer view of the river crossing, ponds, trees and rocky terrain, with mechs positioned around the battlefield.',
    'The full battlefield layout, with a winding river, bridge, city buildings, runway and rocky hills.',
]
figures = []
for i, (name, caption) in enumerate(zip(sources, captions), 1):
    source = Path('C:/Users/Niklas/Downloads') / name
    original = assets / f'photo-{i:02}.jpg'
    shutil.copy2(source, original)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest()
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1600, 1200))
        width, height = image.size
        image.save(assets / f'photo-{i:02}.webp', quality=86)
    text = escape(caption, quote=True)
    loading = 'fetchpriority="high"' if i == 1 else 'loading="lazy"'
    figures.append(f'''<figure><a class="photo" href="iron-stars/photo-{i:02}.jpg" data-caption="{text}" aria-label="Enlarge photograph {i}"><img src="iron-stars/photo-{i:02}.webp" alt="{text}" width="{width}" height="{height}" {loading} decoding="async"><span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{text}</figcaption></figure>''')

template = (ROOT / 'battletech.html').read_text(encoding='utf-8')
header = template.split('<header class="site-header screen-only">', 1)[1].split('</header>', 1)[0]
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Iron Stars | TBD's Dragon Den</title>
<meta name="description" content="The Iron Stars collection: fifteen photographs of painted mechs, the painting desk and city battlefield terrain at TBD's Dragon Den.">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="site-header.css">
<link rel="stylesheet" href="iron-stars/page.css">
<script src="iron-stars/gallery.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="page-shell">
<header class="site-header screen-only">''' + header + '''</header>
<main id="main" class="battle-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span aria-hidden="true">/</span><span aria-current="page">Iron Stars</span></nav>
<section class="intro" aria-labelledby="page-title">
<p class="eyebrow">Miniature projects / Iron Stars</p>
<h1 id="page-title">Iron Stars</h1>
<p>Mechs, painted miniatures and a city battlefield. A look at my Iron Stars collection, with deep red armour, gold and metallic details, and grassy bases.</p>
</section>
<section aria-labelledby="gallery-title">
<div class="gallery-heading"><p class="eyebrow">From the collection</p><h2 id="gallery-title">On the tabletop &amp; at the painting desk</h2><p>Fifteen views of the miniatures, painting desk and battlefield terrain. Select a photograph to enlarge it; use the arrow keys or buttons to browse.</p></div>
<div class="battle-gallery iron-gallery">''' + '\n'.join(figures) + '''</div>
</section>
<dialog class="lightbox" aria-label="Photo viewer"><button class="close" aria-label="Close photo viewer">×</button><img alt=""><div class="viewer-bar"><button class="previous" aria-label="Previous photograph">←</button><p aria-live="polite"></p><button class="next" aria-label="Next photograph">→</button><a class="original" href="iron-stars/photo-01.jpg">Original ↗</a></div></dialog>
</main>
<footer><a href="miniatures.html">← Back to Miniature Projects</a></footer>
</div>
</body>
</html>
'''
(ROOT / 'iron-stars.html').write_text(page, encoding='utf-8')
css = (ROOT / 'battletech/page.css').read_text(encoding='utf-8')
css += '\n.iron-gallery{grid-template-columns:repeat(2,minmax(0,1fr))}\n.iron-gallery figure:first-child{grid-column:1/-1}\n@media(max-width:540px){.iron-gallery{grid-template-columns:1fr}}\n'
(assets / 'page.css').write_text(css, encoding='utf-8')
shutil.copy2(ROOT / 'battletech/gallery.js', assets / 'gallery.js')

miniatures = ROOT / 'miniatures.html'
text = miniatures.read_text(encoding='utf-8')
text = text.replace('<h3 class="project-title">Iron Stars</h3>\n            <p class="project-desc">Projekt kommer här.</p>', '<h3 class="project-title">Iron Stars</h3>\n            <p class="project-desc">Målade mechs och ett stadslandskap — tre bilder från spelbordet.</p>\n            <a href="iron-stars.html" class="btn-ghost">Iron Stars gallery <span aria-hidden="true">↗</span></a>')
text = text.replace('tre bilder från spelbordet.', 'åtta bilder från spelbordet.').replace('sju bilder från spelbordet.', 'åtta bilder från spelbordet.')
text = text.replace('Målade mechs och ett stadslandskap — åtta bilder från spelbordet.', 'Målade mechs, målarbord och terräng — elva bilder från Iron Stars.')
text = text.replace('elva bilder från Iron Stars.', 'femton bilder från Iron Stars.')
miniatures.write_text(text, encoding='utf-8')
index = ROOT / 'index.html'
text = index.read_text(encoding='utf-8')
start = text.index('<!-- Iron Stars -->')
end = text.index('</article>', start)
card = text[start:end].replace('href="#"', 'href="iron-stars.html"').replace('Coming Soon', 'Iron Stars gallery')
text = text[:start] + card + text[end:]
index.write_text(text, encoding='utf-8')

files = [ROOT / name for name in ('iron-stars.html', 'miniatures.html', 'index.html', 'style.css', 'site-header.css', 'Eldritch shadows/IconDragonDenSketchEmbedded.svg')]
files += sorted(assets.iterdir())
for source in files:
    target = ROOT / 'publicering' / source.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(ROOT / 'uppdatering-iron-stars.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(ROOT).as_posix())
print(f'Built Iron Stars page, {len(sources)} original photos, {len(sources)} optimized images and {len(files)} upload files.')
