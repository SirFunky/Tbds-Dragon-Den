"""Build Gundam Assemble gallery and the site's incremental upload package."""
from pathlib import Path
from html import escape
import hashlib
import shutil
import zipfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
assets = ROOT / 'gundam-assemble'
assets.mkdir(exist_ok=True)
sources = [
    '540478417_24204954835871640_3202803712329535131_n.jpg',
    '540079892_1071791468270338_8776294769761360502_n.jpg',
    '541958613_1348365550140298_3133361471204103972_n.jpg',
    '541063857_748411121346407_2522934825211807763_n.jpg',
    '539425499_779815961160020_6676527599809978566_n.jpg',
    '540446418_1126479056089061_8153651225163473831_n.jpg',
    '541164369_1315129166667815_6126990630503252455_n.jpg',
    '540042412_1108135331409203_5535436333309089783_n.jpg',
    '539454566_1465940438063424_8776216359439042088_n.jpg',
    '539976286_799645502726736_6660869120520816640_n.jpg',
    '539845959_1525661441940172_7747395770473743771_n.jpg',
    '539774724_1686089792076685_4401065675717511951_n.jpg',
    '539888877_1446008543371606_3458609201250698565_n.jpg',
    '539419357_2164878100706584_1574056195464531279_n.jpg',
    '539890793_24808506415422904_4526140840184701294_n.jpg',
    '540624601_1100968218253178_8292215387159310914_n.jpg',
]
angles = [
    'Rear view, showing the backpack and extended rifle',
    'Shield-side view, showing the white panel and gold trim',
    'Front view, showing the blue armour and gold chest details',
    'View along the rifle, with the shield held behind the shoulder',
]
figures = []
for i, name in enumerate(sources, 1):
    source = Path('C:/Users/Niklas/Downloads') / name
    original = assets / f'photo-{i:02}.jpg'
    shutil.copy2(source, original)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest()
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1200, 1600))
        width, height = image.size
        image.save(assets / f'photo-{i:02}.webp', quality=86)
    stage = 'Finished grassy base' if i <= 4 else f'Painting progress · view {i - 4:02}'
    caption = f'{stage}. {angles[(i - 1) % 4]}.'
    text = escape(caption, quote=True)
    loading = 'fetchpriority="high"' if i == 1 else 'loading="lazy"'
    figures.append(f'<figure><a class="photo" href="gundam-assemble/photo-{i:02}.jpg" data-caption="{text}" aria-label="Enlarge photograph {i}"><img src="gundam-assemble/photo-{i:02}.webp" alt="{text}" width="{width}" height="{height}" {loading} decoding="async"><span class="enlarge" aria-hidden="true">↗</span></a><figcaption>{text}</figcaption></figure>')

template = (ROOT / 'battletech.html').read_text(encoding='utf-8')
header = template.split('<header class="site-header screen-only">', 1)[1].split('</header>', 1)[0]
page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gundam Assemble | TBD's Dragon Den</title>
<meta name="description" content="A blue, white and gold Gundam Assemble miniature: 16 photographs from the painting desk to the finished grassy base.">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="site-header.css">
<link rel="stylesheet" href="gundam-assemble/page.css">
<script src="gundam-assemble/gallery.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="page-shell">
<header class="site-header screen-only">''' + header + '''</header>
<main id="main" class="battle-page">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="miniatures.html">Miniatures</a><span aria-hidden="true">/</span><span aria-current="page">Gundam Assemble</span></nav>
<section class="intro" aria-labelledby="page-title">
<p class="eyebrow">Miniature projects / Gundam Assemble</p>
<h1 id="page-title">Gundam Assemble</h1>
<p>Deep blue armour, white panels and gold details. A look around my Gundam Assemble miniature, from the painting desk to its finished grass-covered base.</p>
<nav class="chapter-links" aria-label="Gallery sections"><a href="#finished">Finished miniature · 4 photos</a><a href="#painting">Painting progress · 12 photos</a></nav>
</section>
<section id="finished" aria-labelledby="finished-title">
<div class="gallery-heading"><p class="eyebrow">Ready for the tabletop</p><h2 id="finished-title">The finished miniature</h2><p>Four angles of the painted miniature on its grassy base. Select a photograph to enlarge it; use the arrow keys or buttons to browse all 16 photos.</p></div>
<div class="battle-gallery">''' + '\n'.join(figures[:4]) + '''</div>
</section>
<section id="painting" aria-labelledby="painting-title">
<div class="gallery-heading"><p class="eyebrow">From the workbench</p><h2 id="painting-title">Painting progress</h2><p>Twelve views of the blue, white and gold paintwork before the grass was added to the base.</p></div>
<div class="battle-gallery">''' + '\n'.join(figures[4:]) + '''</div>
</section>
<dialog class="lightbox" aria-label="Photo viewer"><button class="close" aria-label="Close photo viewer">×</button><img alt=""><div class="viewer-bar"><button class="previous" aria-label="Previous photograph">←</button><p aria-live="polite"></p><button class="next" aria-label="Next photograph">→</button><a class="original" href="gundam-assemble/photo-01.jpg">Original ↗</a></div></dialog>
</main>
<footer><a href="miniatures.html">← Back to Miniature Projects</a></footer>
</div>
</body>
</html>
'''
(ROOT / 'gundam-assemble.html').write_text(page, encoding='utf-8')
shutil.copy2(ROOT / 'battletech/page.css', assets / 'page.css')
shutil.copy2(ROOT / 'battletech/gallery.js', assets / 'gallery.js')

miniatures = ROOT / 'miniatures.html'
text = miniatures.read_text(encoding='utf-8')
text = text.replace('<h3 class="project-title">Gundam Assemble</h3>\n            <p class="project-desc">Projekt kommer här.</p>', '<h3 class="project-title">Gundam Assemble</h3>\n            <p class="project-desc">Blå rustning, vita paneler och gulddetaljer — 16 bilder från målning till färdig gräsbas.</p>\n            <a href="gundam-assemble.html" class="btn-ghost">Gundam Assemble gallery <span aria-hidden="true">↗</span></a>')
assert 'href="gundam-assemble.html"' in text
miniatures.write_text(text, encoding='utf-8')

files = [ROOT / name for name in ('gundam-assemble.html', 'miniatures.html', 'style.css', 'site-header.css', 'Eldritch shadows/IconDragonDenSketchEmbedded.svg')]
files += sorted(assets.iterdir())
for source in files:
    target = ROOT / 'publicering' / source.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(ROOT / 'uppdatering-gundam-assemble.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(ROOT).as_posix())
print(f'Built Gundam Assemble page, 16 original photos, 16 optimized images and {len(files)} upload files.')
