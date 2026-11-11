"""Build the Gunpla page and incremental Inleed upload package."""
from pathlib import Path
from html import escape
import shutil
import zipfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
assets = ROOT / 'gunpla'
assets.mkdir(exist_ok=True)
photos = [
    ('554239178_692427277207536_3263813424717069148_n.jpg', 'Front view of the blue, white, red and yellow Gunpla model with its twin-barrel weapon.'),
    ('553679681_690707713808528_6597522869428918558_n.jpg', 'Side view showing the blue weapon, red forearm panel and dark backpack.'),
    ('553199892_1285123659605253_4471255554346488223_n.jpg', 'Rear view showing the backpack, blue wings and two white beam saber handles.'),
    ('552516267_828092696307700_7157807178088117077_n.jpg', 'Opposite side view showing the white leg armour, red feet and long weapon barrels.'),
    ('553541011_1549401199558868_1516569336968767410_n.jpg', 'Closer front view showing the yellow head crest, blue chest and red armour details.'),
]
figures = []
for i, (filename, caption) in enumerate(photos, 1):
    source = Path('C:/Users/Niklas/Downloads') / filename
    original = assets / f'photo-{i:02}.jpg'
    shutil.copy2(source, original)
    assert source.read_bytes() == original.read_bytes()
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1200, 1600))
        width, height = image.size
        image.save(assets / f'photo-{i:02}.webp', quality=86)
    text = escape(caption, quote=True)
    loading = 'fetchpriority="high"' if i == 1 else 'loading="lazy"'
    figures.append(f'<figure><a class="photo" href="gunpla/photo-{i:02}.jpg" data-caption="{text}" aria-label="Enlarge photograph {i}"><img src="gunpla/photo-{i:02}.webp" alt="{text}" width="{width}" height="{height}" {loading} decoding="async"><span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{text}</figcaption></figure>')

template = (ROOT / 'gundam-assemble.html').read_text(encoding='utf-8')
head = template.split('<main id="main"', 1)[0]
head = head.replace('Gundam Assemble', 'Gunpla').replace('gundam-assemble/', 'gunpla/')
head = head.replace('A blue, white and gold Gunpla miniature: 16 photographs from the painting desk to the finished grassy base.', 'Five photographs of my blue, white, red and yellow Gunpla model, with front, side and rear views from the workbench.')
tail = template.split('<dialog class="lightbox"', 1)[1].replace('gundam-assemble/', 'gunpla/')
page = head + '''<main id="main" class="battle-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span aria-hidden="true">/</span><span aria-current="page">Gunpla</span></nav>
<section class="intro" aria-labelledby="page-title">
<p class="eyebrow">Model projects / Gunpla</p>
<h1 id="page-title">Gunpla</h1>
<p>Blue and white armour, red panels and yellow details. Five photographs of my Gunpla model from the workbench, taking a look at the front, sides and backpack.</p>
</section>
<section aria-labelledby="gallery-title">
<div class="gallery-heading"><p class="eyebrow">From the workbench</p><h2 id="gallery-title">Around the model</h2><p>Select a photograph to enlarge it. Browse all five photos with the buttons or arrow keys; press Escape to close.</p></div>
<div class="battle-gallery">''' + '\n'.join(figures) + '</div>\n</section>\n<dialog class="lightbox"' + tail
(ROOT / 'gunpla.html').write_text(page, encoding='utf-8')
for name in ('page.css', 'gallery.js'):
    shutil.copy2(ROOT / 'gundam-assemble' / name, assets / name)
with (assets / 'page.css').open('a', encoding='utf-8') as stream:
    stream.write('\n/* Keep five portrait photographs comfortably sized on wide screens. */\n@media(min-width:801px){.battle-gallery{grid-template-columns:repeat(3,minmax(0,1fr))}}\n')

miniatures = ROOT / 'miniatures.html'
text = miniatures.read_text(encoding='utf-8')
if 'href="gunpla.html"' not in text:
    marker = '          <article class="project-card">\n            <h3 class="project-title">Robotech Minitech</h3>'
    assert marker in text
    card = '''          <article class="project-card">
            <h3 class="project-title">Gunpla</h3>
            <p class="project-desc">Blå och vit rustning med röda och gula detaljer — fem bilder av modellen från olika vinklar.</p>
            <a href="gunpla.html" class="btn-ghost">Gunpla gallery <span aria-hidden="true">↗</span></a>
          </article>
'''
    miniatures.write_text(text.replace(marker, card + marker), encoding='utf-8')

files = [ROOT / name for name in ('gunpla.html', 'miniatures.html', 'style.css', 'site-header.css', 'Eldritch shadows/IconDragonDenSketchEmbedded.svg')]
files += sorted(assets.iterdir())
for source in files:
    target = ROOT / 'publicering' / source.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(ROOT / 'uppdatering-gunpla.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(ROOT).as_posix())
print(f'Built Gunpla page, five originals, five optimized images and {len(files)} upload files.')
