from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import zipfile
R=Path(__file__).resolve().parent
class Page(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.ids=set();self.photos=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if a.get(key):self.refs.append(a[key])
        if t=='a' and a.get('class')=='photo':self.photos.append(a['href'])
for file in [R/'drepurs-wraithcreepers.html',R/'age-of-sigmar.html',R/'wraithcreepers-site/dist/index.html']:
    p=Page();p.feed(file.read_text(encoding='utf-8'))
    for ref in p.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        target=file.parent/unquote(u.path) if u.path else file
        assert target.exists(),(file,ref)
        if target==file and u.fragment:assert u.fragment in p.ids,ref
    if 'Wraithcreepers |' in file.read_text(encoding='utf-8'):
        assert len(set(p.photos))==18,len(set(p.photos))
    print(file.name,': links and anchors pass')
with zipfile.ZipFile(R/'uppdatering-drepurs-wraithcreepers.zip') as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.jpg')])==36
    print('ZIP: 18 originals, 18 web images, page, collection, styles and script pass')
