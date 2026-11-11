"""Verify source values, navigable profiles, catalog data, and publication boundaries."""
import json
from pathlib import Path
import re
import runpy
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.links=[];self.values=[];self.catalog_ids=[];self.inline=None;self.in_data=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for key in ['href','src']:
            if attrs.get(key):self.links.append(attrs[key])
        if 'data-value-ref' in attrs:self.values.append(attrs['data-value-ref'])
        if 'data-unit-id' in attrs:self.catalog_ids.append(attrs['data-unit-id'])
        if tag=='script' and attrs.get('id')=='unit-data':self.in_data=True;self.inline=''
    def handle_data(self,text):
        if self.in_data:self.inline+=text
    def handle_endtag(self,tag):
        if tag=='script':self.in_data=False

def normalize(value):return re.sub(r'\s+',' ',value).strip()

def main():
    data=json.loads((ROOT/'iron-stars/data/units.json').read_text(encoding='utf-8'))
    sources={}
    for path in (ROOT/'iron-stars-source/extracted').glob('*.json'):
        for block in json.loads(path.read_text(encoding='utf-8'))['blocks']:
            sources[block['id']]=block.get('text','')
            for row in block.get('rows',[]):
                sources[row['id']]=' | '.join(c['text'] for c in row['cells'])
                sources.update((c['id'],c['text']) for c in row['cells'])
    ids=[u['id'] for u in data['units']]
    assert len(ids)==len(set(ids))==67
    index=ROOT/'iron-stars/units/index.html'
    catalog=Page();catalog.feed(index.read_text(encoding='utf-8'))
    assert set(catalog.catalog_ids)==set(ids)
    assert json.loads(catalog.inline)==data, 'Embedded data differs from reusable JSON'
    pages={}
    def parse(path):
        if path not in pages:
            parser=Page();parser.feed(path.read_text(encoding='utf-8'));pages[path]=parser
        return pages[path]
    checks=0
    for unit in data['units']:
        assert unit['publication_status']=='reference' and not unit['approved_for_army_builder']
        assert unit['points']['approved_value'] is None
        assert all(ref in sources for ref in unit['source_refs'])
        assert not any(s['name'] in ['Sponsor Protocol','Knightly Perfection'] for s in unit['systems'])
        assert unit['faction'] not in ('fourth-imperium','living-dominion','southern-cross-compact')
        for field in ['role','chassis']:
            if unit[field]:assert normalize(unit[field]['text']) in normalize(sources[unit[field]['source_ref']])
        for weapon in unit['weapons']:
            assert weapon['source_ref'] in sources
            assert set(weapon['statistics'])=={'fp','me','range_cm'}
        for profile in unit['profiles']:
            for value in profile['fields'].values():
                assert normalize(value['text']) in normalize(sources[value['source_ref']]),(unit['name'],value)
                checks+=1
            for value in profile.get('mode_details',{}).values():
                assert value['text']==sources[value['source_ref']].strip()
        for point in unit['points']['observations']:
            assert str(point['value']) in sources[point['source_ref']]
        assert unit['points']['filter_value']==unit['points']['calculation']['total']
        for child in unit['spawned_units']:
            assert all(b['id'] in sources for b in child['source_blocks'])
        page=ROOT/'iron-stars/units'/unit['id']/'index.html'
        parsed=parse(page)
        assert len(parsed.ids)==len(set(parsed.ids))
        assert {'profile','weapons','systems','source'}<=set(parsed.ids)
        assert all(ref in sources for ref in parsed.values)
    for path in [index]+[ROOT/'iron-stars/units'/u['id']/'index.html' for u in data['units']]:
        for url in parse(path).links:
            split=urlsplit(url)
            if split.scheme or split.netloc:continue
            target=(path.parent/unquote(split.path)).resolve() if split.path else path.resolve()
            assert target.is_file(),(path,url)
            if split.fragment:assert unquote(split.fragment) in parse(target).ids,(path,url)
    public=runpy.run_path(str(ROOT/'prepare-publication.py'))['collect_files']()
    assert ROOT/'iron-stars/data/units.json' in public
    assert not any(p.is_relative_to(ROOT/'iron-stars-source') or p.is_relative_to(ROOT/'iron-stars-review') for p in public)
    by_name={u['name']:u for u in data['units']}
    assert len(by_name['UNDF Interceptor (Exclusive)']['profiles'])==3
    forge=by_name['Bastion-Class Fabricator (Transformable Drone-Forge)']
    assert len(forge['spawned_units'])==3 and len(forge['weapons'])==2, 'Spawned drones must not become carrier weapons'
    assert not by_name['Knight-Errant Frame']['profiles'], 'Do not infer missing stats from generic chassis tiers'
    assert by_name['Ravager-Class Striker (Transformable Fighter)']['points']['filter_value']==44
    print(f'PASS: 67 source profiles, {checks} literal stat values, embedded JSON, source references, mode access, and spawned-unit separation.')
    print(f'PASS: direct file links and anchors across 68 unit pages; {len(public)} reachable files; private imports excluded.')

if __name__=='__main__':main()
