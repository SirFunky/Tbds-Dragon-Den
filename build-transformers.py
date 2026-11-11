"""Build the Transformers gallery and the site's usual upload package."""
from pathlib import Path
from html import escape
import shutil
import zipfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
assets = ROOT / 'transformers'
assets.mkdir(exist_ok=True)
sources = [
    '541248434_1905152683666855_1221023846303872567_n.jpg',
    '542996131_662996962949848_6058002074005176044_n.jpg',
    '541944311_711501408561918_6642266248899579831_n.jpg',
    '541089303_1414530466296025_7817840118719916066_n.jpg',
    '541047759_775792645150218_7340092148067758731_n.jpg',
    '541604290_796308739569073_5362293698339446756_n.jpg',
    '541624573_634669206185829_1589304750164648789_n.jpg',
    '542371094_785915423897604_1284194707411492904_n.jpg',
    '541747804_1125868802806604_2685618797146652137_n.jpg',
    '541173309_763775763299315_5379401076397592828_n.jpg',
    '540976318_1473581107165767_4105963735150586830_n.jpg',
    '541059027_2256159488145303_859191267588800804_n.jpg',
]
captions = [
    'Side view of the blue and metallic miniature on its gravel-covered base.',
    'Rear view with silver shoulder details and stones around the feet.',
    'The opposite side, showing the painted armour and textured base.',
    'Front view with green eyes, metallic highlights and the gravel base.',
    'Side view at the painting desk, before adding the gravel.',
    'Rear view of the blue-green armour and metallic panels on a plain black base.',
    'The opposite side during painting, with silver shoulder and leg details.',
    'Front view during painting, with blue-green armour and bright metallic legs.',
    'Side view of the blue-painted miniature on its plain black base.',
    'Rear view during painting, showing the back panels and silver details.',
    'Another side view of the miniature before the base was decorated.',
    'Front view of the blue armour, dark chest panels and metallic highlights.',
]
figures = {}
for i, (name, caption) in enumerate(zip(sources, captions), 1):
    source = Path('C:/Users/Niklas/Downloads') / name
    shutil.copy2(source, assets / f'photo-{i:02}.jpg')
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1200, 1600))
        width, height = image.size
        image.save(assets / f'photo-{i:02}.webp', quality=86)
    text = escape(caption, quote=True)
    loading = 'fetchpriority="high"' if i == 9 else 'loading="lazy"'
    figures[i] = f'<figure><a class="photo" href="transformers/photo-{i:02}.jpg" data-caption="{text}" aria-label="Enlarge photograph: {text}"><img src="transformers/photo-{i:02}.webp" alt="{text}" width="{width}" height="{height}" {loading} decoding="async"><span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{text}</figcaption></figure>'

template = (ROOT / 'iron-stars.html').read_text(encoding='utf-8')
head = template.split('<main ', 1)[0].replace('Iron Stars', 'Transformers').replace('iron-stars/', 'transformers/')
head = head.replace('The Transformers miniature collection: seven photographs of painted mechs and a city battlefield at TBD\'s Dragon Den.', 'A Transformers miniature painting gallery: twelve photographs of blue armour, metallic details and a gravel base at TBD\'s Dragon Den.')
sections = ''
for title, subtitle, order in [
    ('At the painting desk', 'Eight views of the blue armour and metallic details before the base was decorated.', [9, 10, 11, 12, 5, 6, 7, 8]),
    ('Adding the gravel base', 'Four views with stones added around the feet, including a front view of the green eyes.', [1, 2, 3, 4]),
]:
    sections += f'<section aria-labelledby="gallery-{order[0]}"><div class="gallery-heading"><h2 id="gallery-{order[0]}">{title}</h2><p>{subtitle}</p></div><div class="battle-gallery transformers-gallery">' + '\n'.join(figures[i] for i in order) + '</div></section>\n'
page = head + '''<main id="main" class="battle-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span aria-hidden="true">/</span><span aria-current="page">Transformers</span></nav>
<section class="intro" aria-labelledby="page-title">
<p class="eyebrow">Miniature projects / Transformers</p>
<h1 id="page-title">Transformers</h1>
<p>From painted armour to a gravel-covered base. Twelve photographs of my Transformers miniature at the painting desk, with blue tones, metallic details and a closer look from every side.</p>
<p class="gallery-help">Select a photograph to enlarge it. Browse with the arrow buttons or arrow keys; press Escape to close.</p>
</section>
''' + sections + '<dialog ' + template.split('<dialog ', 1)[1]
page = page.replace('iron-stars/', 'transformers/')
(ROOT / 'transformers.html').write_text(page, encoding='utf-8')
css = (ROOT / 'battletech/page.css').read_text(encoding='utf-8')
css += '\n.transformers-gallery{grid-template-columns:repeat(3,minmax(0,1fr))}\n.gallery-help{font-size:13px!important;line-height:1.6!important;color:var(--text-muted)}\n@media(max-width:800px){.transformers-gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}\n@media(max-width:540px){.transformers-gallery{grid-template-columns:1fr}}\n'
(assets / 'page.css').write_text(css, encoding='utf-8')
shutil.copy2(ROOT / 'battletech/gallery.js', assets / 'gallery.js')
miniatures = ROOT / 'miniatures.html'
text = miniatures.read_text(encoding='utf-8')
text = text.replace('<h3 class="project-title">Transformers</h3>\n            <p class="project-desc">Projekt kommer här.</p>', '<h3 class="project-title">Transformers</h3>\n            <p class="project-desc">Blå rustning, metalldetaljer och grusbas — tolv bilder från målarbordet.</p>\n            <a href="transformers.html" class="btn-ghost">Transformers gallery <span aria-hidden="true">↗</span></a>')
miniatures.write_text(text, encoding='utf-8')
files = [ROOT / name for name in ('transformers.html', 'miniatures.html', 'style.css', 'site-header.css', 'Eldritch shadows/IconDragonDenSketchEmbedded.svg')]
files += sorted(assets.iterdir())
for source in files:
    target = ROOT / 'publicering' / source.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(ROOT / 'uppdatering-transformers.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(ROOT).as_posix())
print(f'Built Transformers page, {len(sources)} original photos and {len(files)} upload files.')
