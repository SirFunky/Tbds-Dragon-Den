from html import escape
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, NextPageTemplate, PageBreak, PageTemplate, Paragraph


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'Bells for the Forgotten - Web Novella.docx'
OUTPUT = ROOT / 'output/pdf/Bells for the Forgotten.pdf'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

for name, file in [('Georgia', 'georgia.ttf'), ('Georgia-Bold', 'georgiab.ttf'), ('Georgia-Italic', 'georgiai.ttf'), ('Georgia-BoldItalic', 'georgiaz.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / file)))
pdfmetrics.registerFontFamily('Georgia', normal='Georgia', bold='Georgia-Bold', italic='Georgia-Italic', boldItalic='Georgia-BoldItalic')

body_style = ParagraphStyle('Body', fontName='Georgia', fontSize=11, leading=13.2, spaceAfter=6, textColor=colors.black, allowWidows=0, allowOrphans=0)
title_style = ParagraphStyle('Title', parent=body_style, fontSize=28, leading=33.6, spaceAfter=10, keepWithNext=True)
subtitle_style = ParagraphStyle('Subtitle', parent=body_style, fontSize=12, leading=14.4, spaceAfter=10, keepWithNext=True)
chapter_style = ParagraphStyle('Chapter', parent=body_style, fontName='Georgia-Bold', fontSize=16, leading=19.2, spaceBefore=18, spaceAfter=10, keepWithNext=True)


def draw_cover(name):
    def draw(canvas, document):
        canvas.drawImage(str(ROOT / 'bells-for-the-forgotten-covers' / name), 0, 0, width=6*inch, height=9*inch)
    return draw


def number_page(canvas, document):
    canvas.saveState()
    canvas.setFont('Georgia', 9)
    canvas.drawCentredString(4.25*inch, .4*inch, str(document.page - 1))
    canvas.restoreState()


class CoverPage(Flowable):
    def __init__(self):
        super().__init__()
        self.width = self.height = 1

    def draw(self):
        pass


class NovellaPDF(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'Chapter':
            title = flowable.getPlainText()
            key = 'chapter-' + str(self.chapter_count)
            self.chapter_count += 1
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=0)


pdf = NovellaPDF(str(OUTPUT), pagesize=(8.5*inch, 11*inch), title='Bells for the Forgotten', author='', subject='Whispers of the Dead — Novella One', pageCompression=1)
pdf.chapter_count = 0
pdf.addPageTemplates([
    PageTemplate(id='front', pagesize=(6*inch, 9*inch), frames=[Frame(0, 0, 6*inch, 9*inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=draw_cover('front-cover.png')),
    PageTemplate(id='body', pagesize=(8.5*inch, 11*inch), frames=[Frame(.9*inch, .8*inch, 6.7*inch, 9.4*inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=number_page),
    PageTemplate(id='back', pagesize=(6*inch, 9*inch), frames=[Frame(0, 0, 6*inch, 9*inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=draw_cover('back-cover.png')),
])

source = Document(SOURCE)
story = [CoverPage(), NextPageTemplate('body'), PageBreak()]
for paragraph in source.paragraphs:
    if not paragraph.text:
        continue
    markup = []
    for run in paragraph.runs:
        text = escape(run.text).replace('\n', '<br/>')
        if run.italic:
            text = '<i>' + text + '</i>'
        if run.bold:
            text = '<b>' + text + '</b>'
        markup.append(text)
    style = {'Title': title_style, 'Subtitle': subtitle_style, 'Heading 1': chapter_style}.get(paragraph.style.name, body_style)
    story.append(Paragraph(''.join(markup), style))
story.extend([NextPageTemplate('back'), PageBreak(), CoverPage()])
pdf.build(story)

reader = PdfReader(OUTPUT)
assert len(reader.outline) == 32
assert tuple(reader.pages[0].mediabox[2:]) == (432, 648)
assert tuple(reader.pages[-1].mediabox[2:]) == (432, 648)
assert len(reader.pages[0].images) == 1
assert len(reader.pages[-1].images) == 1

expected = ''.join(p.text for p in source.paragraphs)
actual = ''.join(page.extract_text(extraction_mode='plain') for page in reader.pages[1:-1])
# Body page numbers are excluded when checking the PDF's text against the DOCX.
actual = ''.join(re.sub(r'^\d+\s*\n', '', page.extract_text(extraction_mode='plain'), count=1) for page in reader.pages[1:-1])
normalize = lambda value: re.sub(r'\s+', '', value)
assert normalize(actual) == normalize(expected), 'PDF manuscript differs from source text.'
print(f'Created {OUTPUT}. {len(reader.pages)} pages, both covers, 32 chapter bookmarks, verified complete text.')
