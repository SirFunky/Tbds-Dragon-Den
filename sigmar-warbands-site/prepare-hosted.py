from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'dist'
for filename in ['age-of-sigmar.html','stormcast-eternals.html']:
    text=(root.parent/filename).read_text(encoding='utf-8')
    text=text.replace('href="index.html#projects"','href="age-of-sigmar.html#collection"').replace('href="index.html"','href="age-of-sigmar.html"')
    text=text.replace('<a href="about.html">About</a>','<a href="stormcast-eternals.html#inspiration">Inspiration</a>')
    text=text.replace('<a href="contact.html">Contact</a>','<a href="stormcast-eternals.html#gallery">Gallery</a>')
    text=text.replace('href="miniatures.html"','href="age-of-sigmar.html"').replace('← All miniature projects','← All warbands')
    (dest/filename).write_text(text,encoding='utf-8')
shutil.copy2(dest/'age-of-sigmar.html',dest/'index.html')
