from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, zipfile

root=Path(__file__).resolve().parent
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.add(a['id'])
        self.links += [a[k] for k in ('href','src') if a.get(k)]

def check(base, filenames):
    for name in filenames:
        file=base/name
        parser=Links(); parser.feed(file.read_text(encoding='utf-8'))
        for link in parser.links:
            u=urlsplit(link)
            if u.scheme or u.netloc: continue
            target=(file.parent/unquote(u.path)) if u.path else file
            assert target.is_file(), (file,link)
            if u.fragment and target.suffix=='.html':
                other=Links(); other.feed(target.read_text(encoding='utf-8'))
                assert unquote(u.fragment) in other.ids, (file,link)
    print(f'All links and anchors pass: {base}')
check(root,['age-of-sigmar.html','stormcast-eternals.html','miniatures.html'])
check(root/'sigmar-warbands-site/dist',['index.html','age-of-sigmar.html','stormcast-eternals.html'])
originals=list((root/'stormcast-eternals').glob('photo-*.jpg'))
assert len(originals)==19
digest=lambda p:hashlib.sha256(p.read_bytes()).digest()
download_hashes={digest(p) for p in Path('C:/Users/Niklas/Downloads').glob('462*.jpg')}
for p in originals:
    assert digest(p) in download_hashes
    assert digest(p)==digest(root/'publicering/stormcast-eternals'/p.name)
    assert digest(p)==digest(root/'sigmar-warbands-site/dist/stormcast-eternals'/p.name)
with zipfile.ZipFile(root/'uppdatering-age-of-sigmar.zip') as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.jpg')])==19
    for n in z.namelist(): assert z.read(n)==(root/n).read_bytes()
print('All 19 supplied originals preserved; staging and hosted copies match; upload ZIP verified.')
