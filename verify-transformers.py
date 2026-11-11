"""Verify the gallery, source photographs and upload package."""
import ast
from pathlib import Path
import runpy
import zipfile
from PIL import Image

root = Path(__file__).resolve().parent
helpers = runpy.run_path(str(root / 'prepare-publication.py'))
reachable = helpers['collect_files']()
assert root / 'transformers.html' in reachable
content = (root / 'transformers.html').read_text(encoding='utf-8')
assert content.count('class="photo"') == 12
assert content.count('<dialog ') == content.count('</dialog>') == 1
assert 'Iron Stars' not in content
tree = ast.parse((root / 'build-transformers.py').read_text(encoding='utf-8'))
sources = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'sources' for t in node.targets))
for i, name in enumerate(sources, 1):
    assert (root / 'transformers' / f'photo-{i:02}.jpg').read_bytes() == (Path('C:/Users/Niklas/Downloads') / name).read_bytes()
    with Image.open(root / 'transformers' / f'photo-{i:02}.webp') as image:
        image.verify()
with zipfile.ZipFile(root / 'uppdatering-transformers.zip') as archive:
    assert len(archive.namelist()) == 31
    assert archive.testzip() is None
    for name in archive.namelist():
        assert archive.read(name) == (root / name).read_bytes() == (root / 'publicering' / name).read_bytes()
print(f'Validated links and filename casing for {len(reachable)} reachable files; 12 preserved originals, 12 optimized images and 31 matching upload files.')
