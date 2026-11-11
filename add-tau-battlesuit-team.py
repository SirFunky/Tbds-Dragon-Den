from pathlib import Path
import importlib.util
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parent
PHOTOS = [
    ('567035450_817520564506763_6958628259750705836_n.jpg', 'Tre ljusgröna T’au-stridsdräkter tillsammans på målarbordet'),
    ('567536660_798889469635913_7918646667310322413_n.jpg', 'T’au-stridsdräkt framifrån med axelmonterade missiler och sköld'),
    ('568749323_1386144199516578_8533239431904903947_n.jpg', 'T’au-stridsdräkt med missiler och sköld från sidan'),
    ('567074723_3881310915333062_7070175944890819471_n.jpg', 'T’au-stridsdräkt med missiler och sköld bakifrån'),
    ('566621938_812150211533143_496504508971240830_n.jpg', 'T’au-stridsdräkt med missiler och sköld från motsatt sida'),
    ('567128296_2091849838221089_2979482089961047823_n.jpg', 'T’au-stridsdräkt framifrån med två flerpipiga vapen'),
    ('566605722_861772766417129_5864228369080474421_n.jpg', 'T’au-stridsdräkt med två flerpipiga vapen från sidan'),
    ('568230279_1877210079527064_2540573124001606712_n.jpg', 'T’au-stridsdräkt med två flerpipiga vapen bakifrån'),
    ('569211177_25152768514363758_5746616724791314999_n.jpg', 'T’au-stridsdräkt med två flerpipiga vapen från motsatt sida'),
    ('569843672_730027626772570_3037234761979942860_n.jpg', 'Tre T’au-stridsdräkter med den främre modellen vänd åt sidan'),
    ('567122761_1344002890529458_2547246032671917403_n.jpg', 'Närmare sidovy av T’au-stridsdräktens flerpipiga vapen'),
    ('568203675_670494812523131_9040331940086487516_n.jpg', 'Bakre detaljvy av T’au-stridsdräktens ryggaggregat'),
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
before = page.read_text(encoding='utf-8')
assert 'id="tau-battlesuit-team-heading"' not in before
figures = []
assets = []
for number, (filename, caption) in enumerate(PHOTOS, 1):
    source = Path('C:/Users/Niklas/Downloads') / filename
    width, height = jpeg_size(source)
    relative = Path('slay-the-gray') / f'tau-battlesuit-team-{number:02}.jpg'
    assert not (ROOT / relative).exists()
    shutil.copy2(source, ROOT / relative)
    assert source.read_bytes() == (ROOT / relative).read_bytes()
    assets.append(relative)
    figures.append(f'''          <figure>
            <a href="{relative.as_posix()}"><img src="{relative.as_posix()}" width="{width}" height="{height}" alt="{caption}" loading="lazy" /></a>
            <figcaption>{caption}</figcaption>
          </figure>''')

section = '''      <section class="project-card" aria-labelledby="tau-battlesuit-team-heading">
        <h2 id="tau-battlesuit-team-heading" class="project-title">T’au Battlesuit Team</h2>
        <p>Tre ljusgröna stridsdräkter på målarbordet. Samlingsbilder och närbilder visar beväpning, sköld och ryggaggregat från flera vinklar.</p>
        <div class="model-gallery">
''' + '\n'.join(figures) + '''
        </div>
      </section>
'''
assert before.count('    </main>') == 1
after = before.replace('    </main>', section + '    </main>')
assert after.replace(section, '') == before
page.write_text(after, encoding='utf-8')
for relative in [Path('slay-the-gray.html'), *assets]:
    target = ROOT / 'publicering' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, target)
    assert target.read_bytes() == (ROOT / relative).read_bytes()

spec = importlib.util.spec_from_file_location('publication', ROOT / 'prepare-publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)
reachable = publication.collect_files()
assert all(ROOT / asset in reachable for asset in assets)
parser = publication.References()
parser.feed(after)
files = {page}
for link in parser.links:
    target = publication.resolve_local(page, link)
    if target and target.suffix.lower() != '.html':
        files.add(target)
archive_path = ROOT / 'uppdatering-slay-the-gray-photos.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    for path in files:
        assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()

notes = ROOT / 'PUBLICERING.md'
title, rest = notes.read_text(encoding='utf-8').split('\n', 1)
entry = '''
## Slay the Gray — T’au Battlesuit Team

Packa upp senaste `uppdatering-slay-the-gray-photos.zip` och ladda upp innehållet till webbroten hos Inleed. Behåll mappstrukturen. Tolv ytterligare originalbilder finns i ett eget bildspel, T’au Battlesuit Team, med samlingsbilder och flera vinklar av stridsdräkterna. Alla tidigare bilder finns kvar och ingår också i ZIP-filen tillsammans med sidans stilmallar och logotyp. Arbetsfiler och `publicering/` är uppdaterade. Lokala länkar, bildmått, originalkopior, publiceringskopior och ZIP-innehåll är kontrollerade. Layouten är inte visuellt verifierad i webbläsare. Inga filer har laddats upp till Inleed.

'''
notes.write_text(title + '\n' + entry + rest, encoding='utf-8')
print(f'Added {len(assets)} original photos; earlier page content preserved. Validated {len(reachable)} reachable site files.')
print(f'Updated ZIP: {len(files)} files, {archive_path.stat().st_size:,} bytes. All ZIP entries and publication copies verified.')
