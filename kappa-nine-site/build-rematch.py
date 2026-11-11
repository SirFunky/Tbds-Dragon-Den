from pathlib import Path
import re,shutil,zipfile
from html import escape
from html.parser import HTMLParser

root=Path(__file__).resolve().parent
base=root.parent
dist=root/'dist'
assets=dist/'rematch-assets'
assets.mkdir(exist_ok=True)
files=[
'450039288_7819872078100680_9017080509737699690_n.jpg',
'450047867_363516056850635_8649880980662279466_n.jpg',
'448567084_500939512386221_6638425260134536287_n.jpg',
'450495093_1147674079793515_8589674879275797005_n.jpg',
'450647042_1700210000737422_4038981833563970956_n.jpg',
'450964302_1589238358289848_2583684149724452266_n.jpg',
'450188437_1675768302827719_7896540263109668129_n.jpg',
'450141361_1833656003711860_4377725406734734089_n.jpg',
'450989982_1244342280271393_9157070627959967201_n.jpg',
'450595694_1293857051590834_3375264235400355942_n.jpg',
'450305949_1666681034083818_977250212935594045_n.jpg',
'450948553_1003057704846388_9024235306966206369_n.jpg',
'450595694_1003328157998686_2061511011693588770_n.jpg',
'450303319_1171481647398995_7719066551989834986_n.jpg',
'450948551_874850294537234_7167910892270987462_n.jpg',
'448684251_1084219786647919_8391762667924716097_n.jpg',
'450168690_448016768102683_1997475246796071201_n.jpg',
'451439503_915789373610733_1183768692985569372_n.jpg']
for i,f in enumerate(files,1):shutil.copy2(Path('C:/Users/Niklas/Downloads')/f,assets/f'photo-{i:02}.jpg')

def photo(n,caption):
    c=escape(caption,quote=True)
    w,h=(1512,2016) if n in (2,3,4,5,6,9,15,16,19) else (2016,1512)
    return f'<figure><a class="zoom" href="rematch-assets/photo-{n:02}.jpg" aria-label="Enlarge rematch photograph {n}: {c}"><img src="rematch-assets/photo-{n:02}.jpg" width="{w}" height="{h}" style="height:auto" alt="{c}" loading="lazy"></a><figcaption><span>REMATCH / FIELD IMAGE {n:02}</span>{c}</figcaption></figure>'

first=(dist/'index.html').read_text(encoding='utf-8')
head=first.split('<main>')[0]
head=re.sub(r'<title>.*?</title>','<title>Return to Kappa-9 · The Rematch</title>',head)
head=re.sub(r'<meta name="description"[^>]*>','<meta name="description" content="Ghost Talon and the Necrons meet again. A photographic rematch report: Necron victory, reconstructed from the surviving battlefield photographs.">',head)
head=head.replace('<span class="archive">FIELD ARCHIVE / KILL TEAM</span>','<span class="archive">FIELD ARCHIVE / REMATCH</span>')
head=head.replace('href="#top"><span class="sigil"','href="index.html"><span class="sigil"')
body='''<main><section class="hero"><img src="rematch-assets/photo-07.jpg" alt="Necron infantry advance around a central communications platform divided by a long defensive wall" fetchpriority="high"><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow">WARHAMMER 40,000: KILL TEAM / BATTLE REPORT 02</p><p class="series">THE NACHMUND INCIDENT</p><h1>Return to<br><em>Kappa-9</em></h1><p class="dek">The first encounter ended in a draw.<br>This time, the Necrons take the victory.</p><a class="read" href="#briefing">Enter the rematch <span aria-hidden="true">↓</span></a></div><span class="hero-code">NACHMUND GAUNTLET / THE REMATCH</span></section>
<div class="intel-strip"><span><small>ENGAGEMENT</small>T’au versus Necrons</span><span><small>BATTLEFIELD</small>Central platform &amp; diagonal wall</span><span><small>RESULT</small>Necron victory</span><span><small>FINAL SCORE</small>Not recorded</span></div>
<article id="report"><section class="briefing" id="briefing"><div><p class="eyebrow">01 / THE RETURN</p><h2>The station is<br>still worth fighting for.</h2><a href="index.html">← Read the first battle · 10–10 draw</a></div><div class="prose"><p class="lead">Ghost Talon and T-601’s Necrons face one another again, this time across a battlefield built around a single raised communications platform.</p><p>For the campaign, the fight returns to Kappa-9: the listening post whose records drew both forces into the first encounter. Ghost Talon still needs answers. The Necrons still stand between the T’au and the installation.</p><p>The tabletop has changed. The two bunkers are gone. A long defensive wall runs diagonally through the board, meeting the central platform. Rocky positions at opposite corners offer further elevation, while the Vox tower stands beside the main structure.</p><p class="editor-note">A photographic reconstruction. The original written report has not been recovered. The Necron victory is confirmed by the player’s recollection; the final score, mission name, exact turning points and individual attack results are not recorded. The sections below describe visible stages of the fighting, with campaign prose connecting them.</p></div></section>
<section id="engagement"><div class="section-heading"><p class="eyebrow">02 / THE ENGAGEMENT</p><h2>A wall through the battlefield.<br>A fight for the centre.</h2><p>Six dark-armoured stealth suits face silver Necron infantry across the installation. The photographs move from deployment lines to a crowded platform, then to models fallen around the communications array.</p></div>
<div class="opening">'''+photo(2,'Deployment from the T’au side: stealth suits gather along the near edge, with Necrons beyond the central platform.')+'''<div class="prose"><span class="chapter-no">I</span><h3>Opposite sides of the wall</h3><p>The initial overhead views show two distinct lines. Ghost Talon gathers on one side of the listening post; the Necrons spread across the other. Objective markers sit on the platform and behind low barricades around it.</p><p>The diagonal wall breaks up the open ground, but the platform rises above it. Reaching the roof means gaining a commanding position and stepping into a space the enemy also needs.</p><p>Unlike the first game’s exchanges between separate bunkers, this layout draws the opponents toward the same structure.</p></div></div>
<div class="photo-pair landscape">'''+photo(3,'The deployment viewed from the opposite end, showing both forces and the wall running into the central platform.')+photo(7,'Necrons advance at ground level and onto the roof while T’au stealth suits approach from beyond the array.')+'''</div>
<div class="chapter reverse"><div class="prose"><span class="chapter-no">II</span><h3>Onto the platform</h3><p>The next group of views shows Ghost Talon reaching the raised installation. Two stealth suits occupy the near part of the roof, while other suits work along the flanks and around the barricades.</p><p>The Necrons occupy the opposite side of the same roof. Silver infantry also hold positions at ground level, beside the tower and the rocky terrain. The fighting is spreading around the structure even as the two forces close on its upper level.</p><p>In the campaign narrative, Ghost Talon has reached the station’s outer systems. Getting this close is only the beginning: the Necrons have not yielded the roof.</p></div>'''+photo(6,'An overhead view of both forces closing on the installation, with T’au and Necrons on opposite parts of the roof.')+'''</div><div class="photo-pair landscape">'''+photo(8,'T’au stealth suits on the roof and approaches; Necron infantry occupy the far side of the platform.')+photo(11,'Necrons gather around the communications array as T’au suits hold positions close by.')+'''</div>
<div class="chapter"><div class="prose"><span class="chapter-no">III</span><h3>Above the firing lines</h3><p>The tower and rocky positions give the T’au alternatives to the crowded central roof. A stealth suit is photographed on the Vox tower’s narrow platform; another occupies a rocky rise with a view back toward the fighting.</p><p>Below them, the Necron presence remains spread across the central installation and surrounding ground. The upper platform becomes a meeting point for both sides rather than a secure refuge for either.</p><p>The photographs show the positions, but not the exchanges that put each model there. They preserve the shape of the contest: a scattered T’au force trying to operate around a strong Necron concentration.</p></div>'''+photo(10,'A stealth suit occupies the rocky rise, another stands on the tower, and both forces contest the central platform.')+'''</div><div class="photo-pair landscape">'''+photo(9,'Overhead view of the tower position, rocky flank and models gathered around the central array.')+photo(18,'Necrons occupy the platform and ground beside the wall; a fallen T’au model lies in the foreground.')+'''</div>
<div class="chapter reverse"><div class="prose"><span class="chapter-no">IV</span><h3>The cost of the centre</h3><p>Later-looking photographs show models laid on their sides on the roof and beside the stairs. Dark T’au armour and silver Necron frames both appear among the fallen.</p><p>The Necrons remain visibly present across the raised installation. T’au suits persist on the outer approaches and tower, but the images no longer show the intact deployment line from the opening views.</p><p>The exact decisive shot is lost with the missing report. What survives is the outcome: this rematch belongs to the Necrons. Ghost Talon’s first encounter had ended level; its return does not.</p></div>'''+photo(16,'Models lie on their sides around the central platform while a T’au suit remains on the Vox tower.')+'''</div><div class="photo-pair landscape">'''+photo(17,'Fallen T’au suits on the roof and a fallen Necron beside the steps, with Necron infantry still standing around the array.')+photo(15,'An overhead view of the dispersed fighting and fallen models around the central platform.')+'''</div></section>
<section id="results"><div class="section-heading"><p class="eyebrow">03 / THE RESULT</p><h2>The dead claim the field.</h2><p>The rematch ends in a <strong>Necron victory</strong>, as remembered by the player. No numerical score survives in the available record.</p></div><div class="record victory-record"><span class="status-dot"></span><div><p class="eyebrow">CONFIRMED OUTCOME</p><h3>Necron victory</h3><p>T’au / Ghost Talon defeated · Final score unknown</p></div></div><div class="prose result-prose"><p>For the Kappa-9 campaign, the result leaves Ghost Talon’s return checked by T-601’s force. It does not establish whether any archive was destroyed, what intelligence escaped, or which named operatives survived. Those consequences remain open.</p><p>The battlefield photographs support a struggle for the central installation, with losses on both sides. They cannot supply a turn-by-turn score, an MVP or a complete casualty tally.</p></div><a class="read" href="index.html">Revisit the first engagement <span aria-hidden="true">↗</span></a></section>
<section id="tac-ops"><div class="section-heading"><p class="eyebrow">04 / SECONDARY OBJECTIVES</p><h2>The objectives beside the board.</h2><p>Two sets of Tac Op cards appear in the photographs. They preserve the secondary objectives laid out for the game; the photographs do not establish which were achieved or how many points each scored.</p></div><div class="photo-pair">'''+photo(4,'Photographed Tac Ops: Vantage, Behind Enemy Lines and Triangulate.')+photo(5,'Photographed Tac Ops: Central Control, Seize Ground and Hold the Line.')+'''</div></section>
<section id="gallery"><div class="section-heading"><p class="eyebrow">05 / FURTHER FIELD IMAGES</p><h2>The remaining views.</h2><p>Additional angles and close-ups from the supplied photographic record. Select a photograph to enlarge it.</p></div><div class="gallery">'''+photo(1,'Close-up of a T’au stealth suit on the Vox tower platform.')+photo(12,'Necron infantry on and around the platform, with a model fallen beside a barricade.')+photo(13,'A wider angle of the Necron positions and the fallen model beside the central steps.')+photo(14,'A T’au stealth suit beside the rocky terrain, with the central fight in the background.')+'''</div></section>
<footer><p class="eyebrow">TBD’S DRAGON DEN / KILL TEAM FIELD ARCHIVE</p><p>The Nachmund Incident · Return to Kappa-9</p><p class="source-credit">Based on the player’s rematch photographs and recollection of a Necron victory. Campaign framing continues Shadows over Kappa-9.</p><a href="index.html">← Shadows over Kappa-9</a> · <a href="#top">Return to the top ↑</a><small>Unofficial fan-made battle report. Warhammer 40,000 and Kill Team belong to their respective rights holders.</small></footer></article></main>'''
modal=first[first.index('<dialog'):]
page=head+body+modal
from revise_rematch import revise
page=revise(page,photo,assets,base)
(dist/'rematch.html').write_text(page,encoding='utf-8')
# Keep the previous report intact and add a route to its sequel.
link='<p class="sequel-link"><a class="read" href="rematch.html">Next battle: Return to Kappa-9 <span aria-hidden="true">→</span></a></p>'
if 'href="rematch.html"' not in first:
    first=first.replace('<footer>', '<footer>'+link)
    (dist/'index.html').write_text(first,encoding='utf-8')

class Audit(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.refs=[];self.photos=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:assert a['id'] not in self.ids;self.ids.add(a['id'])
        self.refs += [a[k] for k in ('src','href') if a.get(k)]
        if tag=='img' and a.get('src'):assert a.get('alt');self.photos.add(a['src'])
a=Audit();a.feed(page)
for ref in a.refs:
    if ref.startswith('#'):assert ref[1:] in a.ids,ref
    elif not ref.startswith('http'):assert (dist/ref).is_file(),ref
assert len(a.photos)==20
assert 'Final result: T’au 8, Necrons 18, Necron victory' in page
assert all(f'id="round-{i}"' in page for i in range(1,5))
assert not re.search(r'Final score unknown|<small>FINAL SCORE</small>Not recorded|original written report has not|No numerical score|cannot supply a turn-by-turn',page,re.I)
assert not re.search('seraphim|thirteen|men of gold',page,re.I)
print('PASS: rematch page, 20 photographs, four recovered round groups, mission and 18–8 Necron victory.')

# Export both linked pages into the established Inleed layout.
local_assets=base/'return-to-kappa-9';local_assets.mkdir(exist_ok=True)
for f in assets.iterdir():shutil.copy2(f,local_assets/f.name)
for f in ('report.css','report.js'):shutil.copy2(dist/f,local_assets/f)
local=page.replace('rematch-assets/','return-to-kappa-9/').replace('href="report.css"','href="return-to-kappa-9/report.css"').replace('src="report.js"','src="return-to-kappa-9/report.js"').replace('href="index.html"','href="shadows-over-kappa-9.html"')
(base/'return-to-kappa-9.html').write_text(local,encoding='utf-8')
old=first.replace('href="assets/','href="shadows-over-kappa-9/').replace('src="assets/','src="shadows-over-kappa-9/').replace('href="report.css"','href="shadows-over-kappa-9/report.css"').replace('src="report.js"','src="shadows-over-kappa-9/report.js"').replace('href="rematch.html"','href="return-to-kappa-9.html"').replace('<a class="brand" href="#top">','<a class="brand" href="kill-team.html">')
(base/'shadows-over-kappa-9.html').write_text(old,encoding='utf-8')
kill=base/'kill-team.html';k=kill.read_text(encoding='utf-8')
if 'return-to-kappa-9.html' not in k:
    k=k.replace('<a href="shadows-over-nachmund.html"','<a href="return-to-kappa-9.html" class="btn-ghost" lang="en">Return to Kappa-9 — The Rematch <span aria-hidden="true">↗</span></a>\n        <a href="shadows-over-nachmund.html"')
    kill.write_text(k,encoding='utf-8')
pub=base/'publicering'
for f in (kill,base/'shadows-over-kappa-9.html',base/'return-to-kappa-9.html'):shutil.copy2(f,pub/f.name)
shutil.copytree(local_assets,pub/local_assets.name,dirs_exist_ok=True)
with zipfile.ZipFile(base/'uppdatering-return-to-kappa-9.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in [kill,base/'shadows-over-kappa-9.html',base/'return-to-kappa-9.html',*local_assets.iterdir()]:z.write(f,f.relative_to(base))
print('Updated Dragon Den pages, publication folder and rematch upload ZIP.')
