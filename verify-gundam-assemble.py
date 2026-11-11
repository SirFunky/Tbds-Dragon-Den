"""Check gallery links, originals and publication package."""
from pathlib import Path
import ast
import runpy
import zipfile

root = Path(__file__).resolve().parent
m = runpy.run_path(str(root / 'prepare-publication.py'))
reachable = m['collect_files']()
page = root / 'gundam-assemble.html'
assert page in reachable
content = page.read_text(encoding='utf-8')
assert content.count('class="photo"') == 16
parser = m['References']()
parser.feed(content)
for url in parser.links:
    m['resolve_local'](page, url)
tree = ast.parse((root / 'build-gundam-assemble.py').read_text(encoding='utf-8'))
sources = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'sources' for t in node.targets))
for i, name in enumerate(sources, 1):
    original = root / 'gundam-assemble' / f'photo-{i:02}.jpg'
    assert original.read_bytes() == (Path('C:/Users/Niklas/Downloads') / name).read_bytes()
with zipfile.ZipFile(root / 'uppdatering-gundam-assemble.zip') as archive:
    assert len(archive.namelist()) == 39
    assert archive.testzip() is None
    for name in archive.namelist():
        source = (root / name).read_bytes()
        assert source == archive.read(name)
        assert source == (root / 'publicering' / name).read_bytes()
print(f'Validated {len(reachable)} reachable site files, links/anchors/casing, 16 original photos, and 39 matching publication/ZIP files.')
