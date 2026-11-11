from pathlib import Path
import importlib.util, shutil, zipfile, hashlib, urllib.request
root=Path.cwd()
spec=importlib.util.spec_from_file_location('publication',root/'prepare-publication.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
files=module.collect_files()
changed=['celestial-will-a-second-chance.html','celestial-will.css','celestial-will-a-second-chance.pdf','celestial-will/front-cover.jpg']
for name in changed:
    src=root/name; dst=root/'publicering'/name
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    assert module.digest(src)==module.digest(dst)
assert module.digest(root/'celestial-will-a-second-chance.pdf')==module.digest(Path(r'C:\Users\Niklas\Downloads\CelestialWillWebNovellaWithCovers.pdf'))
archive=root/'uppdatering-celestial-will.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for name in changed: z.write(root/name,name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(f'Validated all {len(files)} reachable website files and section links. All 4 changed files match the publication copies. PDF is identical to supplied file. ZIP verified.')

