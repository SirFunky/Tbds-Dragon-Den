from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
import json

p=Path('expatriated-lilys');p.mkdir(exist_ok=True)
urls=[u for g in json.loads(Path('tmp/expatriated-lilys-groups.json').read_text(encoding='utf-8')) for u in g['images']]
def download(u):
 target=p/u.rsplit('/',1)[1]
 if not target.exists(): target.write_bytes(urlopen(u,timeout=60).read())
 assert target.read_bytes().startswith(bytes([255,216,255])), target
 return target.stat().st_size
with ThreadPoolExecutor(max_workers=6) as pool: sizes=list(pool.map(download,urls))
print(f'Downloaded and verified {len(sizes)} photos, {sum(sizes)/1024**2:.1f} MB')

