from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
import hashlib

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


root = Path(__file__).resolve().parent.parent
path = root / 'Bells for the Forgotten - Web Novella.docx'
document = Document(path)
original_text = [p.text for p in document.paragraphs]
assert not document.inline_shapes, 'The manuscript already contains images. Inspect before adding covers.'
body = document._element.body
original_section = deepcopy(body.sectPr)
first_body_paragraph = body[0]

# The artwork has a 2:3 ratio. Separate cover sections preserve its proportions
# while retaining the manuscript's existing page size and margins.
front = document.add_paragraph()
front.alignment = WD_ALIGN_PARAGRAPH.CENTER
front.paragraph_format.space_before = Pt(0)
front.paragraph_format.space_after = Pt(0)
front.paragraph_format.line_spacing = 1
front.paragraph_format.keep_with_next = False
front.paragraph_format.widow_control = False
shape = front.add_run().add_picture(str(root / 'bells-for-the-forgotten-covers/front-cover.png'), width=Inches(6), height=Inches(9))
shape._inline.docPr.set('descr', 'Front cover of Bells for the Forgotten')
first_body_paragraph.addprevious(front._p)


def configure_cover(section_properties):
    for node in list(section_properties):
        if node.tag in {qn('w:headerReference'), qn('w:footerReference'), qn('w:pgNumType')}:
            section_properties.remove(node)
    page_size = section_properties.find(qn('w:pgSz'))
    page_size.set(qn('w:w'), '8640')
    page_size.set(qn('w:h'), '12960')
    margins = section_properties.find(qn('w:pgMar'))
    for side in ('top', 'bottom', 'left', 'right', 'header', 'footer', 'gutter'):
        margins.set(qn('w:' + side), '0')
    kind = section_properties.find(qn('w:type'))
    if kind is None:
        kind = OxmlElement('w:type')
        section_properties.insert(0, kind)
    kind.set(qn('w:val'), 'nextPage')


# Anchor each picture to the physical page, so its paragraph cannot spill over
# to an extra page because of the inline picture's baseline.
def anchor_to_page(inline):
    anchor = OxmlElement('wp:anchor')
    for name, value in {'distT': '0', 'distB': '0', 'distL': '0', 'distR': '0', 'simplePos': '0', 'relativeHeight': '0', 'behindDoc': '1', 'locked': '0', 'layoutInCell': '1', 'allowOverlap': '1'}.items():
        anchor.set(name, value)
    simple = OxmlElement('wp:simplePos')
    simple.set('x', '0')
    simple.set('y', '0')
    anchor.append(simple)
    for axis in ('H', 'V'):
        position = OxmlElement('wp:position' + axis)
        position.set('relativeFrom', 'page')
        offset = OxmlElement('wp:posOffset')
        offset.text = '0'
        position.append(offset)
        anchor.append(position)
    for tag in ('extent', 'effectExtent'):
        element = inline.find(qn('wp:' + tag))
        if element is not None:
            anchor.append(deepcopy(element))
    anchor.append(OxmlElement('wp:wrapNone'))
    for tag in ('docPr', 'cNvGraphicFramePr'):
        element = inline.find(qn('wp:' + tag))
        if element is not None:
            anchor.append(deepcopy(element))
    anchor.append(deepcopy(inline.find(qn('a:graphic'))))
    inline.getparent().replace(inline, anchor)


anchor_to_page(shape._inline)
front_section = deepcopy(original_section)
configure_cover(front_section)
front._p.get_or_add_pPr().append(front_section)

# End the existing body section, then add the back cover in its own section.
back_section = document.add_section(WD_SECTION_START.NEW_PAGE)
configure_cover(back_section._sectPr)
back = document.add_paragraph()
back.alignment = WD_ALIGN_PARAGRAPH.CENTER
back.paragraph_format.space_before = Pt(0)
back.paragraph_format.space_after = Pt(0)
back.paragraph_format.keep_with_next = False
back.paragraph_format.widow_control = False
shape = back.add_run().add_picture(str(root / 'bells-for-the-forgotten-covers/back-cover.png'), width=Inches(6), height=Inches(9))
shape._inline.docPr.set('descr', 'Back cover of Bells for the Forgotten')
anchor_to_page(shape._inline)

# Unlink the cover footer to stop the manuscript's page number appearing on it.
back_section.footer.is_linked_to_previous = False
back_section.header.is_linked_to_previous = False
front_section_object = document.sections[0]
front_section_object.footer.is_linked_to_previous = False
front_section_object.header.is_linked_to_previous = False
body_section = document.sections[1]
body_section.footer.is_linked_to_previous = False
numbering = body_section._sectPr.find(qn('w:pgNumType'))
if numbering is None:
    numbering = OxmlElement('w:pgNumType')
    body_section._sectPr.append(numbering)
numbering.set(qn('w:start'), '1')

document.save(path)

checked = Document(path)
assert [p.text for p in checked.paragraphs if p.text] == [text for text in original_text if text]
assert len(checked.sections) == 3
assert checked.sections[1].page_width == Inches(8.5)
assert checked.sections[1].page_height == Inches(11)
assert len(checked._element.xpath('.//wp:anchor')) == 2
with ZipFile(path) as archive:
    images = {hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist() if name.startswith('word/media/')}
for name in ['front-cover.png', 'back-cover.png']:
    assert hashlib.sha256((root / 'bells-for-the-forgotten-covers' / name).read_bytes()).hexdigest() in images
print('Added both full-page covers. Verified embedded images, section sizes, and complete manuscript text.')
