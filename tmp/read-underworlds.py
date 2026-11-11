import re, html, json
from pathlib import Path
s=Path('tmp/underworlds-source.html').read_text(encoding='utf-8')
s=s[s.index('<div class="entry-content'):]
s=s[:s.index('<span id="wordads-inline-marker"')]
print('\n'.join(html.unescape(re.sub('<[^>]+>','',p)) for p in re.findall(r'<p[^>]*>.*?</p>|<h[234][^>]*>.*?</h[234]>',s,re.S)))
urls=list(dict.fromkeys(html.unescape(x).split('?')[0] for x in re.findall(r'<img[^>]+src="([^"]+)',s)))
Path('tmp/underworlds-images.json').write_text(json.dumps(urls,indent=2))
print('\nIMAGES',len(urls)); print('\n'.join(urls))
