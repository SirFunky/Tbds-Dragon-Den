from html import escape
from pathlib import Path
import re
import shutil

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / 'tmp/novella-edited.md').read_text(encoding='utf-8')
blocks = source.strip().split('\n\n')
document = Document()
section = document.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = section.bottom_margin = Inches(.8)
section.left_margin = section.right_margin = Inches(.9)

normal = document.styles['Normal']
normal.font.name = 'Georgia'
normal.font.size = Pt(11)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.line_spacing = 1.2
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.widow_control = True

for name, size in [('Title', 28), ('Subtitle', 12), ('Heading 1', 16)]:
    style = document.styles[name]
    style.font.name = 'Georgia'
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_after = Pt(10)
    style.paragraph_format.keep_with_next = True
    if name == 'Heading 1':
        style.paragraph_format.space_before = Pt(18)


def add_text(paragraph, text):
    for index, part in enumerate(re.split(r'\*(.*?)\*', text)):
        run = paragraph.add_run(part)
        run.italic = bool(index % 2)


for index, block in enumerate(blocks):
    if block.startswith('# '):
        paragraph = document.add_paragraph(style='Title')
        add_text(paragraph, block[2:])
    elif block.startswith('## '):
        paragraph = document.add_paragraph(style='Heading 1')
        add_text(paragraph, block[3:])
    elif index in (1, 2):
        paragraph = document.add_paragraph(style='Subtitle')
        add_text(paragraph, block)
    else:
        paragraph = document.add_paragraph()
        add_text(paragraph, block)

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer.add_run()
run.font.size = Pt(9)
field = OxmlElement('w:fldSimple')
field.set(qn('w:instr'), 'PAGE')
run._r.addnext(field)
document.core_properties.title = 'Bells for the Forgotten'
document.core_properties.subject = 'Whispers of the Dead — Novella One'
document.core_properties.author = ''
document.core_properties.last_modified_by = ''
document.save(ROOT / 'Bells for the Forgotten - Web Novella.docx')


def inline_html(text):
    return re.sub(r'\*(.*?)\*', r'<em>\1</em>', escape(text))


chapters = [block[3:] for block in blocks if block.startswith('## ')]
contents = ['      <details class="fiction-contents">',
            '        <summary>Chapters</summary>',
            '        <nav aria-label="Novella chapters">',
            '          <ol>']
for index, title in enumerate(chapters, 1):
    label = re.sub(r'^\d+\. ', '', title)
    contents.append(f'            <li><a href="#chapter-{index}">{escape(label)}</a></li>')
contents.extend(['          </ol>', '        </nav>', '      </details>'])

body = []
chapter = 0
for block in blocks[3:]:
    if block.startswith('## '):
        chapter += 1
        body.append(f'          <h2 id="chapter-{chapter}">{escape(block[3:])}</h2>')
    else:
        body.append(f'          <p>{inline_html(block)}</p>')

existing = (ROOT / 'bells-for-the-forgotten.html').read_text(encoding='utf-8')
prefix = existing.split('      <article aria-labelledby="story-title">', 1)[0]
suffix = existing.split('      </article>', 1)[1]
article = '\n'.join(contents) + '''
      <article aria-labelledby="story-title">
        <div class="fiction-title">
          <p class="fiction-label">Whispers of the Dead · Novella One</p>
          <h1 id="story-title">Bells for the Forgotten</h1>
          <p>A story set in the Eldritch Shadows universe</p>
        </div>
        <div class="fiction-prose">
''' + '\n'.join(body) + '''
        </div>
      </article>'''
page = prefix + article + suffix
(ROOT / 'bells-for-the-forgotten.html').write_text(page, encoding='utf-8')
shutil.copyfile(ROOT / 'bells-for-the-forgotten.html', ROOT / 'publicering/bells-for-the-forgotten.html')

print(f'Created edited DOCX and updated both webpage copies. {len(chapters)} chapters including the epilogue.')
