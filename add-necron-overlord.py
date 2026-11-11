from pathlib import Path
import hashlib
import shutil
import zipfile
from html.parser import HTMLParser
import importlib.util

ROOT = Path(__file__).resolve().parent
photos = [
    ('462545900_1079054513381728_3302482519517058375_n.jpg', 'front', 'Necron Overlord framifrån med silverfärgad rustning och blå energidetaljer'),
    ('462541980_1657528591830765_7543056482946927737_n.jpg', 'angle', 'Necron Overlord snett framifrån med blå energikula'),
    ('462550311_968975895271408_3489396070849030221_n.jpg', 'side', 'Necron Overlord från sidan med sitt långa vapen'),
    ('462566376_1090969959701817_4345943960082354252_n.jpg', 'back', 'Necron Overlord bakifrån med metallmantel och blå detaljer'),
]
figures = []
assets = []
for filename, angle, caption in photos:
    source = Path('C:/Users/Niklas/Downloads') / filename
    relative = Path('slay-the-gray') / f'necron-overlord-{angle}.jpg'
    target = ROOT / relative
    shutil.copy2(source, target)
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
    assets.append(relative)
    url = relative.as_posix()
    figures.append(f'''          <figure>
            <a href="{url}">
              <img src="{url}" width="1512" height="2016" alt="{caption}" loading="lazy" />
            </a>
            <figcaption>{caption}</figcaption>
          </figure>''')

page = ROOT / 'slay-the-gray.html'
html = page.read_text(encoding='utf-8')
section = '''      <section class="project-card" aria-labelledby="necron-overlord-heading">
        <h2 id="necron-overlord-heading" class="project-title">Necron Overlord</h2>
        <p>Silverfärgad rustning och klarblå energidetaljer, fotograferad från fyra vinklar.</p>
        <div class="model-gallery">
''' + '\n'.join(figures) + '''
        </div>
      </section>
'''
anchor = '      <section class="project-card" aria-labelledby="fronteris-heading">'
assert html.count(anchor) == 1
assert 'id="necron-overlord-heading"' not in html
page.write_text(html.replace(anchor, section + anchor), encoding='utf-8')

for relative in [Path('slay-the-gray.html'), *assets]:
    target = ROOT / 'publicering' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, target)

spec = importlib.util.spec_from_file_location('publication', ROOT / 'prepare-publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)
reachable = publication.collect_files()
assert all(ROOT / relative in reachable for relative in assets)

archive_path = ROOT / 'uppdatering-necron-overlord.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for relative in [Path('slay-the-gray.html'), *assets]:
        archive.write(ROOT / relative, relative.as_posix())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    for relative in [Path('slay-the-gray.html'), *assets]:
        assert archive.read(relative.as_posix()) == (ROOT / relative).read_bytes()
        assert (ROOT / 'publicering' / relative).read_bytes() == (ROOT / relative).read_bytes()

notes = ROOT / 'PUBLICERING.md'
text = notes.read_text(encoding='utf-8')
entry = '''
## Necron Overlord — Slay the Gray

Packa upp `uppdatering-necron-overlord.zip` och ladda upp innehållet till webbroten hos Inleed. Behåll mappstrukturen. Paketet innehåller uppdaterad `slay-the-gray.html` och fyra bifogade originalbilder i `slay-the-gray/`. Necron Overlord har ett eget bildspel direkt efter Necrons, med bildtexter och länkar till originalbilderna. Samma filer finns i `publicering/`. Lokala länkar, filnamnens stora och små bokstäver, originalkopior och ZIP-innehåll är kontrollerade. Inga filer har laddats upp till Inleed.

'''
title, rest = text.split('\n', 1)
notes.write_text(title + '\n' + entry + rest, encoding='utf-8')
print(f'Added Necron Overlord with four original photos. Validated {len(reachable)} reachable site files; publication copies and ZIP match.')
print(archive_path)
