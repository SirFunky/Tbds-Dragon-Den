"""Verify source fidelity, provenance, approval separation, and private packaging."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'iron-stars-source'
REVIEW = ROOT / 'iron-stars-review'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    manifest = json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    refs = set()
    originals_by_ref = {}
    source_hashes = {}
    table_count = 0
    text_count = 0
    for entry in manifest:
        original = SOURCE/'originals'/entry['filename']
        supplied = Path.home()/'Downloads'/entry['filename']
        digest = hashlib.sha256(original.read_bytes()).hexdigest()
        assert digest == entry['sha256'] == hashlib.sha256(supplied.read_bytes()).hexdigest()
        source_hashes[entry['source_id']] = digest
        doc = json.loads((SOURCE/'extracted'/(entry['source_id']+'.json')).read_text(encoding='utf-8'))
        assert doc['sha256'] == digest
        with zipfile.ZipFile(original) as archive:
            xml = ET.fromstring(archive.read('word/document.xml'))
        source_text = ''.join(t.text or '' for t in xml.find(W+'body').iter(W+'t'))
        parts = []
        tables = []
        for block in doc['blocks']:
            refs.add(block['id'])
            originals_by_ref[block['id']] = block
            if block['kind']=='table':
                tables.append(block)
                parts.extend(c['text'] for row in block['rows'] for c in row['cells'])
            else:
                parts.append(block.get('text',''))
                tables.extend(block.get('embedded_tables',[]))
        for table in tables:
            refs.add(table['id'])
            originals_by_ref[table['id']] = table
            for row in table['rows']:
                refs.add(row['id'])
                originals_by_ref[row['id']] = row
                refs.update(c['id'] for c in row['cells'])
                originals_by_ref.update((c['id'],c) for c in row['cells'])
        assert compact(source_text) == compact(''.join(parts)), 'Text mismatch: '+entry['source_id']
        assert len(tables) == len(xml.find(W+'body').findall('.//'+W+'tbl')), 'Table coverage mismatch'
        table_count += len(tables)
        text_count += len(source_text)
    ids=set(); records=[]; row_groups={}
    for path in sorted((SOURCE/'content'/'unverified').glob('*.json')):
        collection=json.loads(path.read_text(encoding='utf-8'))
        for record in collection['records']:
            assert record['id'] not in ids, record['id']
            ids.add(record['id']); records.append(record)
            assert record['review_status']=='unverified'
            assert record['publication_status']=='private'
            assert record['source_sha256']==source_hashes[record['source_id']]
            assert set(record['source_refs']) <= refs, record['id']
            assert record['source_blocks'] == [originals_by_ref[ref] for ref in record['source_refs']], 'Organized text differs from extraction: '+record['id']
            if record.get('record_type')=='table-row':
                name=record['values_as_written'][0].strip().casefold()
                if name:
                    group=row_groups.setdefault((path.stem,name),{})
                    ref=record['source_refs'][0]
                    group[ref]={'source_ref':ref,'source_id':record['source_id'],
                                'columns':record['columns_as_written'], 'values':record['values_as_written']}
    duplicates=[]
    for (category,name),group in sorted(row_groups.items()):
        if len(group)>1:
            variants=list(group.values())
            duplicates.append({'category':category,'name_as_compared':name,'review_status':'candidate',
                'note':'Same name is not proof of identical semantics; includes intentional unit variants and exact repeats.',
                'variants':variants})
    (REVIEW/'duplicate-definitions.json').write_text(json.dumps(duplicates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    decisions=json.loads((REVIEW/'approvals.json').read_text(encoding='utf-8'))
    approved=[]
    for path in (SOURCE/'content'/'approved').glob('*.json'):
        approved.extend(json.loads(path.read_text(encoding='utf-8'))['records'])
    if not decisions['approvals']:
        assert not approved, 'Approved content without a review decision'
    # Check every fully qualified locator in the review; shorthand continuation
    # references remain readable source citations, not synthesized page numbers.
    report=(REVIEW/'REVIEW.md').read_text(encoding='utf-8')
    for match in re.finditer(r'\b(core|concord|unmc|rebellion|avalon):b\d{4}(?::r\d+)?(?::c\d+)?',report):
        assert match.group() in refs, 'Invalid review locator: '+match.group()
    module=runpy.run_path(str(ROOT/'prepare-publication.py'))
    public=module['collect_files']()
    assert not any(p.is_relative_to(SOURCE) or p.is_relative_to(REVIEW) for p in public)
    result={'source_documents':len(manifest),'body_blocks':sum(len(json.loads((SOURCE/'extracted'/(e['source_id']+'.json')).read_text(encoding='utf-8'))['blocks']) for e in manifest),
            'tables_including_embedded':table_count,'source_text_characters':text_count,
            'unverified_observations':len(records),'approved_records':len(approved),
            'duplicate_name_groups_for_review':len(duplicates),'reachable_public_files':len(public),
            'checks':['Original and supplied DOCX hashes match','Main-body text content matches ignoring whitespace used for table serialization',
                      'All source tables represented, including content-control table',
                      'Unique record IDs and valid source references/hashes','Organized source blocks exactly match extracted source blocks','No private source/review files reachable in public collector',
                      'No approved records without approval decisions','Explicit review references resolve']}
    (REVIEW/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
