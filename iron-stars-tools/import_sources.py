"""Lossless source snapshots and traceable OOXML text extraction (no publication)."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'iron-stars-source'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SOURCES = {
    'core': 'IRON STARS_ CORE RULES 0.0.14 (1).docx',
    'concord': 'IRON CONCORD – FACTION RULES (1).docx',
    'unmc': 'United Nations Mega Corparations (1).docx',
    'rebellion': 'The Cybernetic Rebellion – FACTION RULES (2).docx',
    'avalon': 'NEW AVALON – FACTION RULES (2).docx',
}


def text_of(element):
    parts = []
    def walk(node):
        # Deleted text stays in the source snapshot; track its presence separately.
        if node.tag in (W + 'del', W + 'moveFrom'):
            return
        if node.tag == W + 't':
            parts.append(node.text or '')
        elif node.tag == W + 'tab':
            parts.append('\t')
        elif node.tag in (W + 'br', W + 'cr'):
            parts.append('\n')
        else:
            for child in node:
                walk(child)
    walk(element)
    return ''.join(parts)


def extract(path, key):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
        style_names = {}
        if 'word/styles.xml' in archive.namelist():
            for style in ET.fromstring(archive.read('word/styles.xml')).findall(W + 'style'):
                name = style.find(W + 'name')
                style_names[style.get(W + 'styleId')] = name.get(W + 'val') if name is not None else ''
        body = root.find(W + 'body')
        blocks = []
        heading = []
        for i, item in enumerate(body, 1):
            ref = f'{key}:b{i:04}'
            if item.tag == W + 'p':
                style = item.find(W + 'pPr/' + W + 'pStyle')
                style_id = style.get(W + 'val') if style is not None else ''
                style_name = style_names.get(style_id, style_id)
                value = text_of(item)
                if style_name.lower().startswith('heading') and value.strip():
                    heading = [value]
                blocks.append({'id': ref, 'kind': 'paragraph', 'style': style_name,
                               'heading': heading[:], 'text': value,
                               'numbering': item.find(W+'pPr/'+W+'numPr') is not None})
            elif item.tag == W + 'tbl':
                rows = []
                for ri, row in enumerate(item.findall(W + 'tr'), 1):
                    cells = []
                    for ci, cell in enumerate(row.findall(W + 'tc'), 1):
                        paras = [text_of(p) for p in cell.findall('.//' + W + 'p')]
                        span = cell.find(W + 'tcPr/' + W + 'gridSpan')
                        merge = cell.find(W + 'tcPr/' + W + 'vMerge')
                        cells.append({'id': f'{ref}:r{ri}:c{ci}', 'paragraphs': paras,
                                      'text': '\n'.join(paras),
                                      'column_span': int(span.get(W+'val')) if span is not None else 1,
                                      'vertical_merge': merge.get(W+'val', 'continue') if merge is not None else None})
                    rows.append({'id': f'{ref}:r{ri}', 'cells': cells})
                blocks.append({'id': ref, 'kind': 'table', 'heading': heading[:], 'rows': rows})
            elif item.tag != W + 'sectPr':
                # Content controls can wrap real tables. Retain their cell structure
                # without changing the stable top-level body-block references.
                embedded = []
                for ti, table in enumerate(item.findall('.//' + W + 'tbl'), 1):
                    table_ref = f'{ref}:t{ti}'
                    rows = []
                    for ri, row in enumerate(table.findall(W+'tr'), 1):
                        cells = []
                        for ci, cell in enumerate(row.findall(W+'tc'), 1):
                            paras = [text_of(p) for p in cell.findall('.//'+W+'p')]
                            cells.append({'id': f'{table_ref}:r{ri}:c{ci}', 'paragraphs': paras, 'text': '\n'.join(paras)})
                        rows.append({'id': f'{table_ref}:r{ri}', 'cells': cells})
                    embedded.append({'id': table_ref, 'kind': 'table', 'rows': rows})
                blocks.append({'id': ref, 'kind': 'other', 'text': text_of(item), 'embedded_tables': embedded})
        ancillary = {}
        for name in archive.namelist():
            if name.startswith(('word/footnotes', 'word/endnotes', 'word/comments', 'word/header', 'word/footer')) and name.endswith('.xml'):
                ancillary[name] = text_of(ET.fromstring(archive.read(name)))
        audit = {tag: len(root.findall('.//' + W + tag)) for tag in
                 ('ins', 'del', 'moveFrom', 'moveTo', 'drawing', 'pict', 'txbxContent', 'altChunk', 'sdt', 'sym')}
        audit['nested_tables'] = sum(len(t.findall('.//' + W + 'tbl')) for t in body.findall(W + 'tbl'))
    return {'source_id': key, 'filename': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'status': 'unverified', 'publication_status': 'private',
            'blocks': blocks, 'ancillary_text': ancillary, 'audit': audit}


def main():
    manifest = []
    for key, name in SOURCES.items():
        source = Path.home() / 'Downloads' / name
        snapshot = PRIVATE / 'originals' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists() and snapshot.read_bytes() != source.read_bytes():
            raise RuntimeError(f'Source changed; preserve previous snapshot before reimport: {name}')
        shutil.copy2(source, snapshot)
        data = extract(snapshot, key)
        out = PRIVATE / 'extracted'
        out.mkdir(exist_ok=True)
        (out / f'{key}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        lines = [f'# {name}', '', 'Private extraction; unverified. References use body block order, not page numbers.', '']
        for block in data['blocks']:
            lines.append(f"[{block['id']}]" + (' ' + block.get('style', '') if block['kind'] == 'paragraph' else ' TABLE'))
            if block['kind'] == 'table':
                for row in block['rows']:
                    lines.append(row['id'] + ' | ' + ' | '.join(c['text'].replace('\n', ' / ') for c in row['cells']))
            else:
                lines.append(block.get('text', ''))
            lines.append('')
        (out / f'{key}.md').write_text('\n'.join(lines), encoding='utf-8')
        manifest.append({k: v for k, v in data.items() if k not in ('blocks', 'ancillary_text')})
        print(key, 'blocks', len(data['blocks']), 'tables', sum(b['kind']=='table' for b in data['blocks']), 'audit', data['audit'])
    (PRIVATE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
