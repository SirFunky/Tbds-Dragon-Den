"""Build the five editable web sheets, matching character files and print PDFs.

Rules transcribed from the supplied EldritchShadowsBeta024_BestiaryVoidCircleFix
DOCX; unresolved beta details are retained as GM notes, not new rules.
Run with the bundled Codex Python runtime (reportlab and pypdf required).
"""
from pathlib import Path
import html
import json
import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from site_navigation import apply_navigation
OUT = ROOT / "pregens"
OUT.mkdir(exist_ok=True)
PROFILES = json.loads((ROOT / "pregens-data.json").read_text(encoding="utf-8"))
TEMPLATE = (ROOT / "character-sheet.html").read_text(encoding="utf-8")

ABILITIES = {
    "Sixth Sense": ("Action; Intelligence + Occult; 20 m", "Sense whether anything supernatural is within 20 m. On a success, identify its kind, such as undead, demon, fae or Eldritch. A matching specialization doubles the pool."),
    "Akimbo": ("Two one-handed weapons", "+1 success on attacks; +1 additional success when shooting two targets in the same round. Apply the rulebook's separate dual-wielding rules as well."),
    "Monsters Hunter": ("Known mortal / folkloric monsters", "Know a monster's weaknesses: +1 damage and -1 initiative for the target. Does not apply to unique Eldritch entities for which no prior knowledge exists."),
    "Memory Manipulation": ("Successful social roll", "Alter or erase up to 10 minutes of one person's memory. Works on humans and humanlike psyches, not Eldritch creatures, undead or mindless beings. Some fanatics may resist, at the GM's discretion."),
    "Forked Tongue": ("Successful social roll", "Make a human accept two contradictory ideas at once. Requires reasoning and comprehension; does not work on animals, undead, Eldritch creatures or fanatics with unshakable faith."),
    "Information Web": ("Established network of contacts", "+2 successes on information gathering. Applies where you already have contacts in society, not foreign dimensions or non-human cultures."),
    "Nanomancy": ("Intelligence + Technology; no Mana cost; CPU capacity 30%", "Activate a program by rolling Intelligence + Technology and taking its listed CPU load. Tizian's base pool is 3 + 1 = 4d6, doubled to 8d6 when his Programming specialization applies. Nanomancy has no Mana cost. His CPU is full at 30% total load: three 10% programs use 100% of his personal capacity. Attempting another program while full requires a Nanomancy roll; failure causes 1 Wisdom damage and Paralyzed for 1 round. Ending a program frees its CPU immediately. A short rest can clear all active programs. Cannot be combined with Magical Ritual."),
    "Swarm Attack": ("Action; Intelligence + Technology; 10% CPU; 30 m; no Mana", "Send nanites at one enemy within 30 m. Deal 2 damage, ignoring armor. Roll Intelligence + Technology to activate. No duration is stated in the program entry."),
    "Healing Protocol": ("Intelligence + Technology; 10% CPU; no Mana", "Roll Intelligence + Technology to activate. When using a discipline to heal someone, also heal 1 additional point in another attribute. This supplements the healing discipline check; it is not a replacement for that check. No duration is stated in the program entry."),
    "Magical Ritual": ("Intelligence + Occult; matching Magic specialization", "Allows rituals from the Magic section. Emilia's normal pool is (5 + 2) x 2 = 14d6 for relevant Magic rolls. Rituals take time and can be interrupted. They cannot directly affect greater Eldritch powers or cosmic horrors, but may affect servants or infested areas. Cannot be combined with Nanomancy."),
    "Water Jet": ("3 Mana with Creator; Magical Ritual roll", "Normal cost 2 Mana, increased by Creator to 3. Fire a high-pressure water jet: 1 Water damage for the first 6; each extra 6 doubles the damage."),
    "Creator": ("Creation specialization; passive modifiers", "Creation Magic costs 1 less Mana (minimum 1). Healing and Combat Spells cost 1 extra Mana. Cannot also select Healer or Destroyer. Once per scene, Genesis can avoid its superficial damage cost, but Emilia has not learned Genesis yet."),
    "Ki": ("Action; 2 Mana; scene / up to 10 min", "Choose one element at activation. Fire: +1 Fire melee damage and +1d6 for strength/endurance. Water: hold breath 10 minutes, move freely in water, +1d6 for agility/balance. Earth: +2 armor; cannot be made Prone or Restrained by physical forces. Air: +5 m movement and +1d6 for stealth/acrobatics/evasion. Electricity: an action may paralyze a target for 1 round (their Strength + Wisdom opposed by your Intelligence + Occult); +1d6 for fast reactions. Only one element at a time. Ends if Paralyzed, Asleep or unconscious. Cannot be active with Chi. GM confirms element eligibility."),
    "Bodyguard": ("Ally within 2 m is being attacked", "Swap places with the ally who is being attacked, putting yourself in the danger. Coordinate with your team and stay close enough to intervene."),
    "Resist": ("Starting type: Slashing; reaction to change: 1 Mana", "Gain Resistance to the chosen damage type: roll an extra d6 and subtract it from damage of that type. Spend 1 Mana as a reaction to change to another damage type."),
}

DISCIPLINES = {
    "Athletics": "rorelse", "Observe": "iaktta", "Combat": "strida", "Technology": "teknologi",
    "Academia": "akademia", "Occult": "ockult", "Social Interaction": "social", "Medicine": "medicin",
}
ATTRS = ["Strength", "Agility", "Intelligence", "Wisdom", "Empathy"]
ATTR_FIELDS = ["styrka", "smidighet", "mental_intelligens", "vishet", "empati"]

def power_rows(p):
    if p["class"] == "Mage":
        return [
            ("Bless Weapon (laptop ritual)", "1 Mana; 20 min; +2 difficulty steps", "Weapon gains an extra damage type for one scene: Bludgeoning, Slashing, Piercing, Fire, Water, Air, Electricity or Earth."),
            ("Protect Object (laptop ritual)", "1 Mana; 20 min; +2 difficulty steps", "Object gains +1 armor against a chosen damage type, excluding Void. The entry does not specify duration; agree with the GM."),
            ("Inspiration Hymn (laptop ritual)", "1 Mana; 20 min; +2 difficulty steps", "Allies gain +2 Social Interaction and +1 Athletics for one scene."),
        ]
    if p["class"] == "Nanomancer":
        return [(a, ABILITIES[a][0], ABILITIES[a][1]) for a in ["Swarm Attack", "Healing Protocol"]]
    return []

def values_for(p):
    values = {}
    for name, val in zip(ATTR_FIELDS, p["attributes"]):
        values["attr_" + name] = str(val)
        values["attr_" + name + "2"] = str(val)
    values.update(character_name=p["name"], character_role=f'{p["class"]} - {p["concept"]}', campaign="", player_name="",
                  mana_max="6", mana_current="6", soul_burned="0", xp_earned="0", xp_spent="0",
                  slots_max=str(p["attributes"][0] * 2), equipment_points="0")
    for n in range(1, 21): values[f"attr_extra_mana{n}"] = n <= 6
    for discipline, field in DISCIPLINES.items():
        rank, specialization = p["disciplines"].get(discipline, [0, ""])
        values[f"attr_{field}_poang"] = str(rank)
        values[f"attr_{field}_specialisering"] = specialization
    for n, (name, hit, damage, rules) in enumerate(p["weapons"], 1):
        values[f"weapon{n}_name_type"] = name
        values[f"attr_vapen{n}_traffa"] = hit
        values[f"attr_vapen{n}_skada"] = damage
        values[f"attr_vapen{n}_specialregler"] = rules
    for n, (name, armor, rules) in enumerate(p["armor"], 1):
        values[f"attr_rustning{n}_namn"] = name
        values[f"armor{n}_max"] = str(armor)
        values[f"attr_rustning{n}_varde"] = str(armor)
        values[f"armor{n}_details"] = rules
    for n, (name, effect) in enumerate(p["equipment"][:4], 1): values[f"equipment{n}"] = name + ": " + effect
    for n, name in enumerate(p["abilities"], 1):
        values[f"ability{n}_name"] = name
        values[f"ability{n}_cost"], values[f"ability{n}_effect"] = ABILITIES[name]
    for n, (name, cost, effect) in enumerate(power_rows(p), 1):
        values[f"power{n}_name"], values[f"power{n}_cost"], values[f"power{n}_effect"] = name, cost, effect
    if p["class"] == "Nanomancer":
        values.update(cpu_max="30", cpu_current="0", power_focus="Implanted Nano Module",
                      upgrades="Exoskeleton Implant: connects to powered armor. Exoskeleton Power Armor: armor 7 and Strength 5 while worn. Start in the leather coat; switch armor and update current Strength / carrying capacity manually. Techno Knight is not learned.")
    values["background"] = p["background"] + "\n\nGOAL: " + p["goal"] + "\n\nWEAKNESS: " + p["weakness"]
    values["campaign_notes"] = "PLAYING ADVICE\n" + "\n\n".join(title + ": " + text for title, text in p["advice"])
    values["campaign_notes"] += "\n\nNEXT STEPS\n" + p["next_steps"] + "\n\nBETA / GM NOTES\n" + p["rules_note"]
    if len(p["equipment"]) > 4:
        values["campaign_notes"] += "\n\nADDITIONAL EQUIPMENT\n" + "\n".join(name + ": " + effect for name, effect in p["equipment"][4:])
    values["campaign_notes"] += "\n\nThe complete prebuilt class equipment is retained. Carrying-slot accounting and any beta exceptions should be agreed with the GM. No spare equipment points or bonus XP have been added."
    return values

def build_web(p, values):
    content = TEMPLATE
    replacements = {
        'href="character-sheet.css"': 'href="../character-sheet.css"',
        'src="character-sheet.js"': 'src="../character-sheet.js"',
        '<title>Character Sheet | Eldritch Shadows</title>': f'<title>{html.escape(p["name"])} | Eldritch Shadows</title>',
        '<h1>Character Sheet</h1>': f'<h1>{html.escape(p["name"])}</h1>',
        'Ready for your next session': f'Prebuilt {p["class"]}',
        'Fill it in here, or print a blank copy. Use your browser\'s print dialog to save a PDF.': html.escape(p["tagline"]) + f' <a href="{p["id"]}.pdf">Download the print PDF</a> or <a href="index.html">choose another character</a>.',
        '<form id="character-sheet" autocomplete="off">': f'<form id="character-sheet" data-character-id="{p["id"]}" autocomplete="off">',
        'One current character is saved in this browser when storage is available.': 'This character has its own browser save, separate from the blank sheet and the other prebuilt characters.',
        'At creation: distribute 3 discipline points.': 'Ranks follow the prebuilt class in the beta rulebook.',
    }
    for old, new in replacements.items():
        assert old in content, old
        content = content.replace(old, new)
    def input_value(match):
        tag = match.group(0)
        name = re.search(r'\bname="([^"]+)"', tag)
        if not name or name[1] not in values: return tag
        value = values[name[1]]
        if isinstance(value, bool): return tag.replace(" />", " checked />") if value else tag
        return tag.replace(" />", ' value="' + html.escape(value, quote=True) + '" />')
    content = re.sub(r'<input\b[^>]*>', input_value, content)
    def textarea_value(match):
        tag = match[1]
        name = re.search(r'\bname="([^"]+)"', tag)[1]
        return tag + html.escape(values.get(name, "")) + '</textarea>'
    content = re.sub(r'(<textarea\b[^>]*>).*?</textarea>', textarea_value, content, flags=re.S)
    # Replace every field in the downloadable file, including blank defaults.
    names = re.findall(r'<(?:input|textarea)\b[^>]*\bname="([^"]+)"', content)
    field_values = {name: values.get(name, "") for name in names}
    (OUT / f'{p["id"]}.html').write_text(apply_navigation(content, 2), encoding="utf-8")
    (OUT / f'{p["id"]}.json').write_text(json.dumps({"schema": "eldritch-shadows-character", "version": 1, "fields": field_values}, ensure_ascii=False, indent=2), encoding="utf-8")

pdfmetrics.registerFont(TTFont("Sheet", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("SheetBold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFontFamily("Sheet", normal="Sheet", bold="SheetBold", italic="Sheet", boldItalic="SheetBold")
INK = colors.HexColor("#17251f")
GREEN = colors.HexColor("#194c39")
GRAY = colors.HexColor("#e9eeeb")
LINE = colors.HexColor("#b7c2bb")
BODY = ParagraphStyle("Body", fontName="Sheet", fontSize=9, leading=12, textColor=INK, spaceAfter=6)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=7.7, leading=10, spaceAfter=3)
TITLE = ParagraphStyle("Title", parent=BODY, fontName="SheetBold", fontSize=22, leading=25, spaceAfter=5)
H2 = ParagraphStyle("Section", parent=BODY, fontName="SheetBold", fontSize=11, leading=14, spaceBefore=10, spaceAfter=5, textColor=GREEN)
H3 = ParagraphStyle("Subsection", parent=BODY, fontName="SheetBold", fontSize=9.5, leading=12, spaceAfter=3)
WIDTH = A4[0] - 28 * mm

def P(text, style=BODY):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)

def table(headers, rows, widths, style=SMALL):
    data = [[P(h, ParagraphStyle("TH", parent=style, fontName="SheetBold")) for h in headers]]
    data += [[P(c, style) for c in row] for row in rows]
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRAY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), .5, LINE), ("INNERGRID", (0, 0), (-1, -1), .35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return result

def build_pdf(p):
    story = [P(p["name"], TITLE), P(p["class"] + " | " + p["concept"]), P("Player: ____________________    Campaign: ____________________", SMALL), P("Attributes and disciplines", H2)]
    attrs = table(["Attribute", "Max", "Current"], [[a, v, v] for a, v in zip(ATTRS, p["attributes"])], [30*mm, 11*mm, 14*mm])
    disciplines = table(["Discipline", "Rank", "Specialization"], [[name, p["disciplines"].get(name, [0, ""])[0], p["disciplines"].get(name, [0, ""])[1]] for name in DISCIPLINES], [39*mm, 11*mm, 35*mm])
    side = Table([[attrs, disciplines]], colWidths=[68*mm, WIDTH-68*mm]); side.setStyle(TableStyle([("VALIGN", (0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])); story.append(side)
    story += [Spacer(1, 8), P("Mana 6 / 6     Soul burned: 0     XP earned: 0     XP spent: 0", H3)]
    circles = Table([["o" for _ in range(20)]], colWidths=[WIDTH/20]*20); circles.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Sheet"),("FONTSIZE",(0,0),(-1,-1),14),("ALIGN",(0,0),(-1,-1),"CENTER")])); story.append(circles)
    story.append(P("20 tracking circles; start with 6 Mana. Mark or cross out spent points. No current injuries or conditions.", SMALL))
    story += [P("Weapons", H2), table(["Name / type", "Hit", "Damage", "Special rules"], p["weapons"], [48*mm, 11*mm, 35*mm, WIDTH-94*mm])]
    story += [P("Armor", H2), table(["Armor", "Max / current", "Notes"], [[n, f"{a} / {a}", r] for n,a,r in p["armor"]], [52*mm, 22*mm, WIDTH-74*mm])]
    story += [P("Equipment", H2), table(["Item", "Uses / effect"], p["equipment"], [59*mm, WIDTH-59*mm])]
    story += [P("Class equipment is included at no cost. Spare equipment points: 0. Agree carrying-slot accounting with the GM; this sheet does not silently remove class gear.", SMALL), PageBreak()]
    story += [P("Abilities & powers", TITLE), P(p["name"] + " | " + p["class"])]
    for name in p["abilities"]:
        cost, effect = ABILITIES[name]
        story.append(KeepTogether([P(name, H2), P(cost, H3), P(effect)]))
    if p["class"] == "Nanomancer":
        story += [P("Equipment and CPU", H2), P("CPU capacity: 30%   |   CPU in use: 0%. Start in the leather coat. Exoskeleton Power Armor is an alternative suit: armor 7 and Strength 5 while worn. Change current Strength and carrying capacity manually. Do not add both suits' armor values. Techno Knight is not selected.")]
    if p["class"] == "Mage":
        story.append(P("Black Tower Laptop: loaded rituals", H2))
        for name, cost, effect in power_rows(p):
            story += [P(name, H3), P(cost + ". " + effect)]
        story.append(P("The laptop imposes +2 difficulty steps and doubles casting time (already shown above). An hour connected to its database lets you replace its three rituals.", SMALL))
    story += [P("Using your character", H2), P(p["next_steps"]), P("Beta notes for the GM", H2), P(p["rules_note"], SMALL)]
    story += [P("Quick reference", H2), P("Build a pool from an attribute plus a discipline; double it for a matching specialization. Each 6 is a success. Opposing successes cancel. Spend 1 Mana to reroll up to two dice. Damage reduces attributes. At 0 in an attribute, you go down and need treatment. Use the full rulebook for armor, damage types and ability timing.", SMALL), PageBreak()]
    story += [P("Background & playing advice", TITLE), P(p["name"] + " | " + p["class"]), P(p["tagline"], H3), P("Background", H2)]
    for para in p["background"].split("\n\n"): story.append(P(para))
    story += [P("Goal", H2), P(p["goal"]), P("Weakness", H2), P(p["weakness"]), P("Playing advice", H2)]
    for title, text in p["advice"]:
        story.append(Paragraph("<b>"+escape(title)+".</b> "+escape(text), BODY))
    story += [P("Session notes", H2), P("________________________________________________________________________________\n\n________________________________________________________________________________\n\n________________________________________________________________________________", SMALL)]
    def footer(canvas, doc):
        canvas.saveState(); canvas.setStrokeColor(LINE); canvas.line(14*mm, 13*mm, A4[0]-14*mm, 13*mm)
        canvas.setFont("Sheet", 7); canvas.setFillColor(INK); canvas.drawString(14*mm, 9*mm, "ELDRITCH SHADOWS | TBD's Dragon Den | Prebuilt class / beta rules")
        canvas.drawRightString(A4[0]-14*mm, 9*mm, f'{p["name"]} - {doc.page}'); canvas.restoreState()
    path = OUT / f'{p["id"]}.pdf'
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=13*mm, bottomMargin=18*mm, title=p["name"]+" - "+p["class"], author="TBD's Dragon Den")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    assert len(PdfReader(path).pages) == 3, f'{p["name"]}: expected 3 pages'

def build_hub():
    cards = []
    for p in PROFILES:
        cards.append(f'''<article class="pregen-card"><span class="eyebrow">{html.escape(p['class'])}</span><h2>{html.escape(p['name'])}</h2><p>{html.escape(p['tagline'])}</p><p>{html.escape(p['concept'])}</p><div class="toolbar-actions"><a class="action-link" href="{p['id']}.html">Open character sheet</a><a href="{p['id']}.pdf" download>PDF</a><a href="{p['id']}.json" download>Character file</a></div></article>''')
    page = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Ready-to-play characters | Eldritch Shadows</title><link rel="stylesheet" href="../character-sheet.css"><style>.pregen-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px}.pregen-card{padding:24px;background:#0f172a;border:1px solid #475569;border-radius:14px}.pregen-card h2{margin:8px 0;font-size:23px}.pregen-card p{color:#aeb8c8}.action-link{padding:9px 13px;border-radius:6px;background:#4ade80;color:#052e16;text-decoration:none;font-weight:600}.toolbar-actions{align-items:center}.beta-note{margin:24px 0;color:#aeb8c8;line-height:1.7}</style></head><body><header class="site-header"><a class="brand" href="../../index.html">TBD's Dragon Den</a><nav><a href="../EldritchShadowsPublicEnglishPdfUpdated.html#start-playing">Start playing</a><a href="../character-sheet.html">Blank character sheet</a></nav></header><main><div class="sheet-toolbar"><span class="eyebrow">Materials for your first session</span><h1>Meet your next character</h1><p>Five characters based on the rulebook's prebuilt classes, with complete backgrounds, goals, weaknesses and playing advice. Pick a character, change any personal details you like, and bring them to your first game.</p><div class="toolbar-actions"><a class="action-link" href="eldritch-shadows-five-characters.pdf" download>Download all five (PDF)</a></div></div><div class="pregen-grid">'''+"\n".join(cards)+'''</div><p class="beta-note">These characters use the standard class loadouts, rather than the special characters from Into the Fog. Optional class abilities have been chosen in advance. The beta's unresolved rules and equipment exceptions are recorded on the sheets; <a href="beta-notes.html">the GM can review them here</a>. Each editable web sheet saves separately in this browser. Character JSON files can also be loaded into the blank sheet.</p></main></body></html>'''
    (OUT / "index.html").write_text(apply_navigation(page, 2), encoding="utf-8")
    notes = "\n".join(f'<section class="pregen-card"><h2>{html.escape(p["name"])} - {p["class"]}</h2><p>{html.escape(p["rules_note"])}</p></section>' for p in PROFILES)
    (OUT / "beta-notes.html").write_text('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Prebuilt character beta notes</title><link rel="stylesheet" href="../character-sheet.css"></head><body><main><div class="sheet-toolbar"><a href="index.html">Back to characters</a><h1>Beta notes for the GM</h1><p>The printed class presets are preserved. These notes identify places where the beta needs a ruling; they do not add new abilities or campaign equipment.</p></div>'''+notes+'''<p>All five characters begin with 12 attribute points, 6 Mana, no injuries and zero earned XP. All five characters have 3 discipline points, including the author-corrected Mage. Equipment is provided by the class, rather than bought with an additional 60-point allowance.</p></main></body></html>''', encoding="utf-8")

    notes_path = OUT / "beta-notes.html"
    notes_path.write_text(apply_navigation(notes_path.read_text(encoding="utf-8"), 2), encoding="utf-8")

if __name__ == "__main__":
    for p in PROFILES:
        assert sum(p["attributes"]) == 12
        vals = values_for(p)
        build_web(p, vals)
        build_pdf(p)
    writer = PdfWriter()
    for p in PROFILES: writer.append(OUT / f'{p["id"]}.pdf')
    writer.write(OUT / "eldritch-shadows-five-characters.pdf")
    build_hub()
    print("Built 5 web sheets, 5 character files, 5 three-page PDFs, a 15-page combined PDF and the character hub.")
