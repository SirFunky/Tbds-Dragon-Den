from pathlib import Path
from html import escape
import shutil
import zipfile
import re
from PIL import Image, ImageOps

root = Path.cwd()
assets = root / 'warhammer-40k'
assets.mkdir(exist_ok=True)
photos = [
('566586797_806562775597156_7065386038578733021_n.jpg', 'Överblick över spelbordet med miniatyrer, byggnader och blå terräng.'),
('566523957_684610158027604_955205050975590819_n.jpg', 'Hela Warhammer 40K-samlingen och terrängen från sidan.'),
('566555931_1855532975392644_4617747165008533794_n.jpg', 'Spelbordet från motsatt håll med miniatyrer mellan byggnaderna.'),
('566352915_2592134654494277_5346497023145157381_n.jpg', 'Närbild av miniatyrerna på den blå terrängen och det mönstrade spelbrädet.'),
('566500068_1160218445439146_1166518642782164651_n.jpg', 'Miniatyrer och egenbyggd terräng med en stor industribyggnad i mitten.'),
('566352915_3159880864170217_8209127777357871127_n.jpg', 'Närbild av miniatyrsamlingen och röda modeller på svart terräng med blå detaljer.'),
('597867359_4187537598152323_2833569144627388591_n.jpg', 'Överblick längs spelbordet med silverfärgade miniatyrer, gröna stridsdräkter och blå terräng.'),
('597586105_2053977042086624_1881400999924939937_n.jpg', 'Gröna stridsdräkter och drönare bland industribyggnader och svart terräng med blå detaljer.'),
('598140515_1315844240585704_7414727917030348504_n.jpg', 'Spelbordets mitt med silverfärgade miniatyrer, gröna stridsdräkter och en inhägnad industribyggnad.'),
]
figures = []
for i, (name, alt) in enumerate(photos, 1):
    source = Path('C:/Users/Niklas/Downloads') / name
    original = assets / f'photo-{i:02}.jpg'
    shutil.copy2(source, original)
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1200, 1600))
        width, height = image.size
        image.save(assets / f'photo-{i:02}.webp', quality=86)
    figures.append(f'          <a href="warhammer-40k/photo-{i:02}.jpg" aria-label="Visa bild {i} i full storlek"><img src="warhammer-40k/photo-{i:02}.webp" alt="{escape(alt, quote=True)}" width="{width}" height="{height}" loading="lazy" decoding="async" /></a>')
page_path = root / 'warhammer-40k.html'
page = page_path.read_text(encoding='utf-8')
if 'href="warhammer-40k/gallery.css"' not in page:
    page = page.replace('  <link rel="stylesheet" href="site-header.css" />', '  <link rel="stylesheet" href="site-header.css" />\n  <link rel="stylesheet" href="warhammer-40k/gallery.css" />')
gallery = '''      <section class="project-card warhammer-photos" aria-labelledby="photos-heading">
        <h2 id="photos-heading" class="project-title">Bilder från spelbordet</h2>
        <p class="project-desc">Miniatyrer och terräng från min Warhammer 40K-samling. Klicka på en bild för att se den i full storlek.</p>
        <div class="warhammer-gallery">
''' + '\n'.join(figures) + '''
        </div>
      </section>
'''
if 'id="photos-heading"' in page:
    page, count = re.subn(r'      <section class="project-card warhammer-photos".*?</section>\n', lambda _: gallery, page, count=1, flags=re.S)
    assert count == 1
else:
    page = page.replace('    </main>', gallery + '    </main>')
page_path.write_text(page, encoding='utf-8')
(assets / 'gallery.css').write_text('''.warhammer-photos{margin-top:24px}
.warhammer-gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;align-items:start;margin-top:20px}
.warhammer-gallery a{display:block;border-radius:10px;overflow:hidden;border:1px solid rgba(255,255,255,.15)}
.warhammer-gallery img{display:block;width:100%;height:auto}
.warhammer-gallery a:hover{border-color:currentColor}
.warhammer-gallery a:focus-visible{outline:3px solid currentColor;outline-offset:4px}
@media(max-width:800px){.warhammer-gallery{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){.warhammer-gallery{grid-template-columns:1fr}}
''', encoding='utf-8')
files = [page_path, root / 'style.css', root / 'site-header.css', root / 'Eldritch shadows/IconDragonDenSketchEmbedded.svg', *sorted(assets.iterdir())]
for source in files:
    target = root / 'publicering' / source.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
with zipfile.ZipFile(root / 'uppdatering-warhammer-40k.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for source in files:
        archive.write(source, source.relative_to(root).as_posix())
print(f'Added {len(photos)} photos; synchronized publicering; packaged {len(files)} files.')
