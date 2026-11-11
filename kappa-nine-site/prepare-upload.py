from pathlib import Path
from html.parser import HTMLParser
import shutil,re,zipfile
base=Path(__file__).resolve().parent.parent
dist=base/'kappa-nine-site/dist'
class Audit(HTMLParser):
    def __init__(self): super().__init__();self.ids=set();self.links=[];self.images=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
        for name in ('href','src'):
            if name in a:self.links.append(a[name])
        if tag=='img' and a.get('src'):assert a.get('alt');self.images+=1
audit=Audit();text=(dist/'index.html').read_text(encoding='utf-8');audit.feed(text)
for link in audit.links:
    if link.startswith('#'):assert link[1:] in audit.ids,link
    elif not link.startswith(('http','mailto:')):assert (dist/link).is_file(),link
assert not re.search(r'seraphim|thirteen|men of gold',text,re.I)
assert len(list((dist/'assets').glob('*.jpg')))==15
assert all(text.count(f'id="turn-{i}"')==1 for i in range(1,5))
assert 'Hunter Cadre 10, Tomb World 10, draw' in text
assert 'Implacable March' in text
assert not re.search(r'Outcome: unconfirmed|No final score|Later-looking|Sections follow areas',text)
assets=base/'shadows-over-kappa-9';assets.mkdir(exist_ok=True)
for f in (dist/'assets').glob('*.jpg'):shutil.copy2(f,assets/f.name)
for f in ('report.css','report.js'):shutil.copy2(dist/f,assets/f)
local=text.replace('href="assets/','href="shadows-over-kappa-9/').replace('src="assets/','src="shadows-over-kappa-9/').replace('href="report.css"','href="shadows-over-kappa-9/report.css"').replace('src="report.js"','src="shadows-over-kappa-9/report.js"')
local=local.replace('<a class="brand" href="#top">','<a class="brand" href="kill-team.html">')
(base/'shadows-over-kappa-9.html').write_text(local,encoding='utf-8')
kill=base/'kill-team.html';k=kill.read_text(encoding='utf-8')
if 'shadows-over-kappa-9.html' not in k:
    anchor='<a href="shadows-over-nachmund.html"'
    k=k.replace(anchor,'<a href="shadows-over-kappa-9.html" class="btn-ghost" lang="en">The Nachmund Incident — Shadows over Kappa-9 <span aria-hidden="true">↗</span></a>\n        '+anchor)
    kill.write_text(k,encoding='utf-8')
pub=base/'publicering';shutil.copy2(kill,pub/kill.name);shutil.copy2(base/'shadows-over-kappa-9.html',pub/'shadows-over-kappa-9.html');shutil.copytree(assets,pub/assets.name,dirs_exist_ok=True)
with zipfile.ZipFile(base/'uppdatering-shadows-over-kappa-9.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in [kill,base/'shadows-over-kappa-9.html',*assets.iterdir()]:z.write(f,f.relative_to(base))
print(f'PASS: {audit.images} image placements, 15 image assets, local files and anchors resolve, restricted lore absent. Upload ZIP created.')
