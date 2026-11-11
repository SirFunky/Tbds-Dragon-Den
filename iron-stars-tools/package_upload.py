"""Prepare a fresh, scoped Iron Stars upload bundle. Never deploy or replace outputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
INTEGRATION={'index.html','iron-stars.html','style.css','site-header.css','Eldritch shadows/IconDragonDenSketchEmbedded.svg'}
PRIVATE={'iron-stars-source','iron-stars-review','iron-stars-tools','.git','.codex','.agents','__pycache__','upload-packages','publicering'}
RUNTIME_JSON={'army-builder','armory','units','pricing','factions','rulebook'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(label):
    collector=runpy.run_path(str(ROOT/'prepare-publication.py'))
    reachable=collector['collect_files']()
    selected={p for p in reachable if p.is_relative_to(ROOT/'iron-stars')}
    selected.update(ROOT/name for name in INTEGRATION)
    assert selected<=reachable,'An integration file is not reachable from the site.'
    for path in selected:
        relative=path.relative_to(ROOT)
        assert not PRIVATE.intersection(relative.parts),relative
        assert path.suffix.lower() not in {'.docx','.py','.pyc','.md','.ps1','.zip','.gz','.env'},relative
        if path.suffix=='.json':assert relative.parent==Path('iron-stars/data') and path.stem in RUNTIME_JSON,relative
    required={'iron-stars/assets/battle-core.js','iron-stars/assets/battle-tracker.js',
              'iron-stars/assets/army-builder.js','iron-stars/assets/roster-core.js',
              'iron-stars/assets/custom-core.js','iron-stars/assets/custom-builder.js',
              'iron-stars/army-builder/index.html','iron-stars/index.html'}
    relative_names={p.relative_to(ROOT).as_posix() for p in selected}
    assert required<=relative_names,'A runtime file is missing from the upload.'

    base=ROOT/'upload-packages';base.mkdir(exist_ok=True)
    bundle=base/label;number=2
    while bundle.exists():bundle=base/(label+'-'+str(number));number+=1
    bundle.mkdir();website=bundle/'website';website.mkdir()
    records=[]
    for source in sorted(selected):
        relative=source.relative_to(ROOT);target=website/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        digest=sha(source);assert sha(target)==digest,target
        records.append({'path':relative.as_posix(),'bytes':source.stat().st_size,'sha256':digest})

    archive=bundle/(bundle.name+'.zip')
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for record in records:output.write(website/record['path'],record['path'])
    with zipfile.ZipFile(archive) as output:
        assert output.testzip() is None,'ZIP integrity check failed.'
        assert set(output.namelist())==relative_names,'ZIP file list differs from staging.'
        for record in records:assert hashlib.sha256(output.read(record['path'])).hexdigest()==record['sha256'],record['path']

    dependencies=set()
    for source in selected:
        if source.suffix not in {'.html','.css','.svg'}:continue
        content=source.read_text(encoding='utf-8');refs=[]
        if source.suffix in {'.html','.svg'}:
            parser=collector['References']();parser.feed(content);refs.extend(parser.links)
        refs.extend(match[1] for match in collector['URLS'].findall(content))
        for ref in refs:
            target=collector['resolve_local'](source,ref)
            if target and target not in selected:dependencies.add(target.relative_to(ROOT).as_posix())

    report={'package':archive.name,'files':len(records),'uncompressed_bytes':sum(r['bytes'] for r in records),
            'zip_bytes':archive.stat().st_size,'zip_sha256':sha(archive),
            'extensions':dict(sorted(Counter(Path(r['path']).suffix for r in records).items())),
            'scope':'Iron Stars section, existing gallery, homepage integration and shared header assets',
            'existing_site_navigation_targets':sorted(dependencies),
            'checks':['Reachable local links, anchors and exact filename casing checked',
                      'Every staged and archived file matches its current source SHA-256',
                      'ZIP integrity/CRC and exact file list verified',
                      'Both battle modules and every required builder module included',
                      'Only public runtime JSON included; private sources, QA and tools excluded',
                      'Existing publication output and older archives preserved'],
            'deployed':False}
    (bundle/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (bundle/'manifest.sha256').write_text(''.join(r['sha256']+'  '+r['path']+'\n' for r in records),encoding='utf-8')
    (bundle/'UPLOAD-INSTRUCTIONS.txt').write_text('''IRON STARS — upload to the existing TBD's Dragon Den website

1. Unzip the ZIP file on your computer. Its contents start with index.html,
   iron-stars.html and the iron-stars folder; there is no extra wrapper folder.
2. Upload those extracted contents into the website folder that already contains
   your current index.html. Merge folders and replace the included files.
   Keep the existing website's other files and project folders.
3. Open https://tbddragonden.com/iron-stars/index.html and then the Army builder.
   Refresh with Ctrl+F5 if an older page is shown.

The ZIP includes the homepage's Iron Stars link, existing gallery, shared header
assets and current game pages/scripts/data. Links to other hobby projects use
the files already on your existing website. This is an update, not a complete
backup of all other projects.

The website/ folder beside the ZIP contains the same upload-ready files.
Do not upload the surrounding bundle folder, manifest or verification report.

Saved rosters, the unit library and battles belong to your browser and website
address. They are not part of this upload. To move data from the local builder
to the hosted site, export the relevant JSON files locally and import them on
the hosted builder. Keep those backups.

This package was prepared locally. Nothing has been deployed automatically.
''',encoding='utf-8')
    print(json.dumps({'zip':str(archive),'upload_folder':str(website),'instructions':str(bundle/'UPLOAD-INSTRUCTIONS.txt'),
                      'files':len(records),'zip_mb':round(archive.stat().st_size/1024**2,2),'sha256':report['zip_sha256']},indent=2))
    return bundle

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--label',default='iron-stars-upload-2026-11-07');args=parser.parse_args()
    if not args.label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.label):parser.error('Use a simple package label without paths.')
    prepare(args.label)
