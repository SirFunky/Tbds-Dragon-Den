from pathlib import Path
from PIL import Image
from pypdf import PdfReader
import shutil, re, zipfile, importlib.util
root=Path.cwd()
assets=root/'celestial-will'
assets.mkdir(exist_ok=True)
pdf=root/'celestial-will-a-second-chance.pdf'
shutil.copy2(Path(r'C:\Users\Niklas\Downloads\CelestialWillWebNovellaWithCovers.pdf'), pdf)
reader=PdfReader(pdf)
cover=reader.pages[0].images[0]
im=Image.open(__import__('io').BytesIO(cover.data)).convert('RGB')
im.save(assets/'front-cover.jpg', quality=94)
print('Cover:', im.size, 'PDF pages:',len(reader.pages))
path=root/'celestial-will-a-second-chance.html'
html=path.read_text(encoding='utf-8')
original_prose=html.split('<div class="fiction-prose">',1)[1].split('</div>',1)[0]
html=html.replace('<body>', '<body class="celestial-novella">').replace('class="fiction fiction-reader"', 'class="fiction"')
html=html.replace('  <link rel="stylesheet" href="short-stories.css" />','  <link rel="stylesheet" href="short-stories.css" />\n  <link rel="stylesheet" href="celestial-will.css" />\n  <meta name="description" content="Read Celestial Will: A Second Chance by Niklas Karlsson online, or download the complete novella PDF with front and back covers." />')
hero='''        <div class="celestial-hero">
          <figure class="celestial-cover">
            <img src="celestial-will/front-cover.jpg" width="WIDTH" height="HEIGHT" alt="Celestial Will: A Second Chance cover: a luminous Earth beneath a ring of stars, with thirteen figures between a ruined city and a restored future" fetchpriority="high" />
          </figure>
          <div class="celestial-intro">
            <p class="fiction-label">Science fiction · A web novella</p>
            <h1 id="story-title">Celestial Will<span>A Second Chance</span></h1>
            <p class="celestial-author">By Niklas Karlsson</p>
            <div class="celestial-orbit" aria-hidden="true"><span>✦</span></div>
            <p class="celestial-hook">Humanity has been given a second chance.</p>
            <p class="celestial-description">An unseen organization ends humanity’s wars with technology beyond comprehension. But behind the promise of peace, thirteen figures in the dark are preparing for a future the world knows nothing about.</p>
            <div class="celestial-actions">
              <a class="celestial-button" href="celestial-will-a-second-chance.pdf" download="Celestial Will - A Second Chance.pdf">Download the PDF <span aria-hidden="true">↓</span></a>
              <a class="celestial-button celestial-button-secondary" href="#chapter-1">Read online <span aria-hidden="true">→</span></a>
            </div>
            <p class="celestial-file-note">PDF · 15 pages · 746 KB · Includes front and back covers</p>
          </div>
        </div>
        <details class="fiction-contents">
          <summary>Chapters</summary>
          <nav aria-label="Story chapters"><ol>
'''.replace('WIDTH',str(im.width)).replace('HEIGHT',str(im.height))
headings=re.findall(r'<h2>(.*?)</h2>',original_prose)
for i,title in enumerate(headings,1):
    hero+=f'            <li><a href="#chapter-{i}">{title}</a></li>\n'
hero+='          </ol></nav>\n        </details>'
html=re.sub(r'        <div class="fiction-title">.*?</div>',lambda _:hero,html,count=1,flags=re.S)
for i,title in enumerate(headings,1):
    html=html.replace(f'<h2>{title}</h2>',f'<h2 id="chapter-{i}">{title}</h2>',1)
footer='''        <aside class="celestial-download" aria-label="Download the novella">
          <p class="fiction-label">Keep the story</p>
          <h2>A Second Chance, wherever you read.</h2>
          <p>Download the complete novella with its front and back covers.</p>
          <a class="celestial-button" href="celestial-will-a-second-chance.pdf" download="Celestial Will - A Second Chance.pdf">Download the PDF <span aria-hidden="true">↓</span></a>
        </aside>
'''
html=html.replace('      </article>',footer+'      </article>')
updated_prose=html.split('<div class="fiction-prose">',1)[1].split('</div>',1)[0]
assert re.sub(r' id="chapter-\d+"','',updated_prose)==original_prose
path.write_text(html,encoding='utf-8')
print('Updated hero and',len(headings),'chapter links; story text preserved.')
