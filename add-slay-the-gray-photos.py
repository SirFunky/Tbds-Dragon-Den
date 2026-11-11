from pathlib import Path
from html import escape
from html.parser import HTMLParser
import importlib.util
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
DOWNLOADS = Path('C:/Users/Niklas/Downloads')
GROUPS = [
    ('tau-battlesuit-drones', 'T’au Battlesuit &amp; Drones',
     'Ljusgrön stridsdräkt med två drönare, fotograferad från fyra vinklar.', [
        ('551879454_1377479480398844_1789748016251534242_n.jpg', 'T’au-stridsdräkt framifrån med två drönare'),
        ('553138707_1337428884559105_2890619413318650661_n.jpg', 'T’au-stridsdräkt och drönare från sidan'),
        ('553576388_843413061446339_2638514066811038907_n.jpg', 'T’au-stridsdräkt bakifrån med två drönare'),
        ('551705432_656022110908963_4539291129374918031_n.jpg', 'T’au-stridsdräkt och drönare från motsatt sida'),
    ]),
    ('tau-heavy-battlesuit', 'T’au Heavy Battlesuit',
     'Ljusgrön stridsdräkt med tung beväpning och sköld, fotograferad från fyra vinklar.', [
        ('552895472_2189284954909368_8741816438901215483_n.jpg', 'Tung T’au-stridsdräkt framifrån med kanon och sköld'),
        ('553565519_1331845578473493_1265992919407378752_n.jpg', 'Tung T’au-stridsdräkt från sidan med sköld'),
        ('552777729_1859110831308609_3384084131895457692_n.jpg', 'Tung T’au-stridsdräkt bakifrån'),
        ('552783237_693094980480660_1951914762583818801_n.jpg', 'Tung T’au-stridsdräkt från sidan med kanonen i profil'),
    ]),
    ('necron-warriors-purple', 'Necron Warriors — Purple &amp; Blue',
     'Silverfärgade Necron Warriors med lila och blå vapendetaljer. Fyra vinklar av modellen med det lila vapnet.', [
        ('545677660_796103369774911_6949482957350345881_n.jpg', 'Necron Warrior framifrån med lila vapen och fler Necrons i bakgrunden'),
        ('545458695_1422970122116532_3434412964288697175_n.jpg', 'Necron Warrior från sidan med lila vapen'),
        ('546615410_777285278373212_3053022760110017224_n.jpg', 'Necron Warrior bakifrån med blåbeväpnad Necron i bakgrunden'),
        ('546170640_938452475164687_3890928982938335483_n.jpg', 'Necron Warrior från motsatt sida med lila vapen'),
    ]),
]


def jpeg_size(path):
    with path.open('rb') as stream:
        assert stream.read(2) == b'\xff\xd8'
        while True:
            assert stream.read(1) == b'\xff'
            marker = stream.read(1)
            while marker == b'\xff':
                marker = stream.read(1)
            length = struct.unpack('>H', stream.read(2))[0]
            if marker[0] in (0xc0, 0xc1, 0xc2, 0xc3):
                _, height, width = struct.unpack('>BHH', stream.read(5))
                return width, height
            stream.seek(length - 2, 1)


page = ROOT / 'slay-the-gray.html'
html = page.read_text(encoding='utf-8')
sections = []
new_assets = []
for slug, title, description, photos in GROUPS:
    assert f'id="{slug}-heading"' not in html
    figures = []
    for number, (filename, caption) in enumerate(photos, 1):
        source = DOWNLOADS / filename
        width, height = jpeg_size(source)
        relative = Path('slay-the-gray') / f'{slug}-{number}.jpg'
        shutil.copy2(source, ROOT / relative)
        assert source.read_bytes() == (ROOT / relative).read_bytes()
        new_assets.append(relative)
        url = relative.as_posix()
        figures.append(f'''          <figure>
            <a href="{url}"><img src="{url}" width="{width}" height="{height}" alt="{escape(caption)}" loading="lazy" /></a>
            <figcaption>{escape(caption)}</figcaption>
          </figure>''')
    sections.append(f'''      <section class="project-card" aria-labelledby="{slug}-heading">
        <h2 id="{slug}-heading" class="project-title">{title}</h2>
        <p>{description}</p>
        <div class="model-gallery">
''' + '\n'.join(figures) + '''
        </div>
      </section>
''')
assert html.count('    </main>') == 1
page.write_text(html.replace('    </main>', ''.join(sections) + '    </main>'), encoding='utf-8')

for relative in [Path('slay-the-gray.html'), *new_assets]:
    destination = ROOT / 'publicering' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, destination)
    assert destination.read_bytes() == (ROOT / relative).read_bytes()

spec = importlib.util.spec_from_file_location('publication', ROOT / 'prepare-publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)
reachable = publication.collect_files()
assert all(ROOT / asset in reachable for asset in new_assets)
parser = publication.References()
parser.feed(page.read_text(encoding='utf-8'))
files = {page}
for link in parser.links:
    target = publication.resolve_local(page, link)
    if target and (target.suffix.lower() != '.html'):
        files.add(target)

# Include every photo on this page so earlier gallery additions travel with it.
archive_path = ROOT / 'uppdatering-slay-the-gray-photos.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    for path in files:
        assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()

notes = ROOT / 'PUBLICERING.md'
text = notes.read_text(encoding='utf-8')
title, rest = text.split('\n', 1)
entry = '''
## Slay the Gray — T’au och Necron Warriors

Packa upp `uppdatering-slay-the-gray-photos.zip` och ladda upp innehållet till webbroten hos Inleed. Behåll mappstrukturen. Alla tolv nya originalbilder finns i tre separata bildspel: T’au Battlesuit & Drones, T’au Heavy Battlesuit och Necron Warriors — Purple & Blue. Sidan använder befintliga knappar och piltangenter för bläddring; bilderna länkar till originalen. Paketet innehåller hela sidans bildsamling, inklusive tidigare Necron Overlord, samt sidans stilmallar och logotyp. Arbetsfiler och `publicering/` är uppdaterade. Lokala länkar, bildmått, originalkopior, publiceringskopior och ZIP-innehåll är kontrollerade. Layouten är inte visuellt verifierad i webbläsare. Inga filer har laddats upp till Inleed.

'''
notes.write_text(title + '\n' + entry + rest, encoding='utf-8')
print(f'Added {len(new_assets)} original photos in {len(GROUPS)} galleries. Checked {len(reachable)} reachable files.')
print(f'ZIP verified: {len(files)} files, {archive_path.stat().st_size:,} bytes. Publication copies match.')
