# Iron Stars source review

The five supplied documents have been imported as private, unverified source
material. No rules, costs, or profiles have been corrected or published. The user
has now directed that the latest source is the source of truth. For this import,
use core v0.0.14 for shared rules over older faction descriptions; retain explicit
faction/unit-specific exceptions and faction content not replaced by newer text.
This establishes source precedence, not automatic approval of every record.
The main
blockers for a reliable digital rulebook and army builder are conflicting keyword
definitions, inconsistent profiles and totals, and mechanics that reference
undefined procedures.

## How to check a finding

Source IDs map to the exact supplied files:

| ID | Document |
| --- | --- |
| core | IRON STARS_ CORE RULES 0.0.14 (1).docx |
| concord | IRON CONCORD – FACTION RULES (1).docx |
| unmc | United Nations Mega Corparations (1).docx |
| rebellion | The Cybernetic Rebellion – FACTION RULES (2).docx |
| avalon | NEW AVALON – FACTION RULES (2).docx |

References such as `core:b0232:r13` identify body block 232, table row 13.
Cell references append `:c1`, and embedded tables append `:t1`. Body block
numbers include empty paragraphs and tables. These are reproducible extraction
locators, not Word page numbers. Open `../iron-stars-source/extracted/core.md`
or its JSON companion and search the reference. The JSON preserves cell text
and paragraph boundaries. `originals/` holds byte-identical DOCX snapshots;
`manifest.json` records their SHA-256 hashes.

The core version 0.0.14 comes from the user's identification and filename; the
document title itself says ALPHA. The four faction documents have no explicit
release version in their main text. Filename suffixes `(1)` and `(2)` are not
treated as versions. The core's internal `word/document.xml` ZIP timestamp is
2026-03-14; all four faction documents have timestamps of 2026-03-03. None supplies
an embedded created/modified/revision property. These are package timestamps,
not verified publication dates, but they are the available evidence for the
current working precedence. Downloads-folder timestamps reflect file copies and
are not used. See `source-precedence.json` for the full evidence.

Where a finding compares a general faction description to a newer core rule,
the core rule now governs. Keep these historical findings for traceability;
their original question wording below predates this decision. Conflicting passages
within one document, incomplete rules, costs, and explicitly named variants are
not resolved merely by choosing the newest document. In particular, Overdrive and
Veil Phase also disagree within the core itself. No ordering between those
passages, or between full profiles and quick sheets, can be inferred from package
dates.

## Rules that need an authoritative decision

| ID | Finding and effect | Source references | Decision needed |
| --- | --- | --- | --- |
| R01 | Overdrive is described as a third action with damage on 1, damage on 1–2, or failure and damage on 1–3 with success only on 4–6. Whether an unsuccessful roll still grants the action differs or is unstated. | core:b0156; core:b0197:r2; concord:b0060; unmc:b0153; rebellion:b0065–b0067 | Specify the standard rule and any explicitly named exceptions. |
| R02 | Piercing X adds X damage per hit in the core glossary, but several Concord profiles explain it as ignoring Defence. AP already reduces Defence. This changes both hit probability and damage. | core:b0232:r6,r13; concord:b0081; concord:b0352 | Confirm Piercing versus AP semantics and correct the affected descriptions. |
| R03 | Accurate allows +1 to one die or one failed-die reroll in the glossary; Concord profiles abbreviate it as +1 to hit, without restricting the bonus to one die. | core:b0232:r5; concord:b0072; concord:b0352 | Confirm which dice receive the modifier and whether reroll versus modifier is a player choice. |
| R04 | Blast defaults to 5 cm in the core, while Concord descriptions say 3 cm without always labeling this as Blast (3). | core:b0232:r7; core:b0238:r2; concord:b0040,b0044,b0135,b0335 | Confirm explicit weapon-specific radii and the default. |
| R05 | Burn triggers after damage and resolves at the start of the next activation in the core. Concord descriptions use on-hit application or end-of-next-activation damage. Token stacking is not specified. | core:b0232:r8; concord:b0041,b0135,b0350 | Confirm trigger, timing, and stacking. |
| R06 | Suppressive reduces FP in the core glossary, but Concord profiles require a morale test on a hit; other profiles use “Suppression” without defining whether it is the same keyword. | core:b0232:r15; concord:b0071,b0135; unmc:b0102; rebellion:b0035:r5 | Confirm whether these are distinct effects, and how they work when optional morale is disabled. |
| R07 | Heavy forbids use after movement in the glossary. Concord descriptions instead apply a -1 penalty or forbid Overwatch after use. | core:b0232:r10; concord:b0081,b0082,b0338 | Define Heavy consistently or name the exceptions. |
| R08 | Cleave grants another melee attack only after a kill in the core. Iron Templar describes hitting an additional adjacent target without that condition. | core:b0232:r9; concord:b0076 | Confirm trigger and the extra attack's profile and limits. |
| R09 | Veil Phase cancels the first hit in the price table, all hits from one attack in the glossary, and the first attack in the core Avalon overview. Avalon adds named +/++ variants. | core:b0197:r9; core:b0235:r7; core:b0302; avalon:b0028,b0168,b0182 | Define the base effect and how variants replace or stack with it. |
| R10 | Fabricator/Swarm repairs or deploys per turn in some entries, as an adjacent action in the glossary, and at activation start within 10 cm in Drone Spawner. | core:b0197:r8; core:b0235:r4; rebellion:b0041:r5; rebellion:b0101–b0106 | Confirm action cost, timing, range, spawn profile, and active-drone limits. |
| R11 | Deep Strike requires round 2+ and >20 cm from enemies in the glossary. Stratos entries say anywhere once per game without those limits. | core:b0235:r2; core:b0441; unmc:b0023; unmc:b0045:r6 | State whether Stratos explicitly overrides these restrictions. |
| R12 | “Uniqe” limits a unit to one Unique Trait/System, while the Dread Sovereign lists Targeting Crown, Sovereign Defence Plating, Command Override, and Heroic Presence as Unique. | core:b0235:r11; concord:b0225–b0227,b0232 | Clarify whether the limit concerns systems, units in an army, or has a hero exception. |
| R13 | Knightly Perfection and several other rules reroll defence dice, but core attacks roll against static Defence and have no defence-roll procedure. | core:b0043,b0097–b0101; avalon:b0012,b0120; rebellion:b0322,b0681 | Define defence rolls or revise those abilities. |
| R14 | Many systems modify or prevent Overwatch, but the supplied core does not define how to enter it, trigger it, pay for it, or resolve it. Charge and melee engagement/disengagement procedures are also incomplete. | core:b0123–b0130; core:b0110–b0113,b0149; concord:b0033:r19; unmc:b0042:r3; avalon:b0295 | Supply the missing core procedures. |
| R15 | Destruction leaves a unit to the end of the round and says it may complete its “current activation if [it has] not already acted.” Immediate last-attacks, recursive spawns, wreck placement, and Dominion revival can overlap. | core:b0065–b0073,b0134–b0136,b0544; avalon:b0140,b0153; rebellion:b0458 | Define destruction/activation eligibility and end-of-round resolution order. |
| R16 | Morale suppresses a unit when the roll is less than its current STR. Higher-STR units therefore fail more often, potentially automatically above 6 before modifiers; no natural-die exception for morale is stated. | core:b0142–b0153 | Confirm that the inequality and use of current STR are intentional. This is a question, not a balance correction. |
| R17 | The action budget and one-use-per-weapon-per-activation restriction conflict with Hammernet's third-action system described as allowing repeated firing and “fire 3 times.” Multiweapon systems may alter action counts but do not explicitly remove the per-weapon cap. | core:b0118–b0121; unmc:b0107,b0113; concord:b0033:r2–r5 | Confirm repeated fire and the interaction with Rapid/Rapid Fire, linked systems, and Overdrive. |
| R18 | Hardened Carapace is >30.5 cm for 2 points in the core and Siege Breaker, but 30 cm+ for 3 points in the Rebellion table. | core:b0197:r11; rebellion:b0041:r7; rebellion:b0086 | Confirm distance boundary and faction-specific pricing. |
| R19 | Burrower reappears anywhere after a turn in the core, versus at the next turn start >10 cm from enemies in the drone profile. | core:b0084:r5; rebellion:b0487 | Define the intended timing and restrictions. |
| R20 | Command Aura changes from +1 morale or hit in the core, to morale or Defence for Archon, melee rerolls for Warmachines, one attack reroll for Sentinels, and defence rerolls for Null Directive. | core:b0197:r7; unmc:b0195:r5; rebellion:b0287,b0428,b0681 | Name distinct variants or establish an explicit unit-override policy. |
| R21 | Core lists Warmachines, Engineer Core, Swarm Synod, and Ascendants. The faction roster instead adds Sentinels and Null Directive; Engineer Core and Ascendants lack corresponding dedicated roster sections. | core:b0381–b0397; rebellion:b0020–b0024,b0300,b0569 | Confirm current subfactions, selection restrictions, and which traits are free. |
| R22 | Some Rebellion roster builds use generic 10/15/20/25-point chassis and stats rather than the faction's 8/14/18/22-point chassis. This could be intentional, but no selection/override policy is stated. | rebellion:b0030; rebellion:b0149,b0187,b0232,b0269,b0308 | Define chassis eligibility and the authoritative build table. |
| R23 | Concord Legate's Obedience Protocols activates near another Concord unit; the system table and Breaker instead require a commander. “Near” has no distance in the Legate entry. | concord:b0033:r12,b0065,b0074 | Confirm eligible support units and distance. |
| R24 | Linked Fire Control requires the same target in the points table; Emberwolf allows “same target or area.” Split Fire interaction and what qualifies as one linked weapon need confirmation. | concord:b0033:r2,r5; concord:b0138; core:b0232:r17–r18 | Define targeting, grouping, and cost for every linked loadout. |
| R25 | Avalon Order ++ traits are more powerful than the corresponding core overview traits, and detailed units carry base/+ versions too. Several entries lack an explicit Order keyword despite selection rules relying on it. | core:b0286–b0302; avalon:b0014–b0028,b0138,b0197,b0229 | Confirm Order assignment, precedence, and stacking; do not infer allegiance from names alone. |
| R26 | Sponsor Protocol buys a megacorp trait, but general UNMC detachment and mixed-sponsor eligibility are not fully specified. Black Budget/Live Feed reroll tokens also lack a general spending, expiry, and stacking procedure. | unmc:b0019–b0027,b0045; core:b0449 | Define army-level sponsor restrictions and token rules. |
| R27 | SCC tax depends on chassis tiers, but named faction frames are not uniformly mapped to Light/Medium/Heavy/Elite. Importing House/Order-exclusive stock profiles also needs eligibility clarification. | core:b0612–b0649; concord:b0028; avalon:b0049 | Supply an explicit tier and import-eligibility mapping, including which printed bonuses are lost. |
| R28 | Round completion, round-start order/initiative, game length outside the quick-start mission, command actions, repair caps/targets, and spawned-unit activation timing are not comprehensively defined. | core:b0034–b0038,b0123–b0130,b0253–b0264; rebellion:b0101–b0106 | Provide the missing procedures before enforcing them in software. |

## Point calculations and incomplete cost data

Arithmetic below is diagnostic. It does not replace any printed stock cost.
Different stock prices might be deliberate discounts; the sources do not establish
such a policy. Approximate `~` totals remain approximate, not rounded final costs.

| ID | Finding | Source references |
| --- | --- | --- |
| C01 | Concord Ironsworn Trooper prints 8. Listed chassis 6 + rifle 1 + maul 1 + Discipline Drills 1 = 9. | concord:b0035–b0038; concord:b0028:r2,b0030:r2,b0031,b0033:r14 |
| C02 | Burning Purger prints 16. Chassis 10 + flamer 4 + bayonet 2 + Scorch Doctrine 3 = 19 if every listed trait is charged. | concord:b0039–b0042; concord:b0028:r4,b0030:r4,b0031,b0033:r9 |
| C03 | Iron Templar prints 35. Chassis 22 + halberd 6 + volleygun 3 + Storm Charge 4 + Fanatical Zeal 2 = 37. | concord:b0075–b0079; concord:b0028:r6,b0030:r7,b0031,b0033:r10,r17 |
| C04 | Bastion-Class Walker prints 39. Chassis 28 + cannon 7 + blade 4 + Sacrifice 1 + Anchor 3 = 43. | concord:b0080–b0084; concord:b0028:r7,b0030:r6,b0031,b0033:r13,r19 |
| C05 | Rebellion role-package table prints Hunter-Killer 23, Siege Breaker 34, Drone Spawner 28, Ascendant Controller 37, and Swarm Alpha 15. Summing only that table's listed chassis/loadout using its own faction price lists gives 28, 37, 32, 40, and 20 respectively. Unlisted mandatory systems could change these further. | rebellion:b0030,b0035,b0037,b0041,b0045 |
| C06 | Ravager's introductory ~32 conflicts with the explicit 44-point breakdown. | rebellion:b0145,b0169–b0176 |
| C07 | Reaper's ~42 conflicts with its 43-point breakdown. | rebellion:b0228,b0251–b0258 |
| C08 | Pathfinder's ~23 conflicts with its 21-point breakdown. | rebellion:b0304,b0325–b0329 |
| C09 | Guardian Transporter's ~30 conflicts with its 33-point breakdown; Transport itself is priced approximately. | rebellion:b0337,b0357,b0361–b0365 |
| C10 | Aegis Restorer's ~32 conflicts with its 34-point breakdown. | rebellion:b0372,b0396–b0400 |
| C11 | Paragon Custodian's ~52 conflicts with its 56-point breakdown. | rebellion:b0408,b0432–b0436 |
| C12 | Drone-Swarm Cluster's ~24 conflicts with its 22-point breakdown. | rebellion:b0445,b0462–b0466 |
| C13 | Burrower Drones' ~26 conflicts with their 20-point breakdown. | rebellion:b0473,b0490–b0494 |
| C14 | Hive-Crusher's ~38 conflicts with its 44-point breakdown. Its four linked 6-point Medium Lasers are charged 24, while the core linked escalation makes the fourth copy cost 12, giving 30 for that weapon group if that rule applies. | rebellion:b0501,b0508,b0522–b0526; core:b0192:r10,b0232:r18 |
| C15 | Brood-Lord's ~50 conflicts with its 48-point breakdown. Transform appears in its stats but has no defined alternate mode or charge in the breakdown. | rebellion:b0534,b0537,b0559–b0563 |
| C16 | Warden Pursuer prints 24, but its written subtotals give 10 + 8 + 10 = 28. Quantum Echo is simultaneously charged 6 and called free; excluding it gives 22, not 24. | rebellion:b0572,b0576,b0591–b0595 |
| C17 | Phantom Interdictor prints 29, but written subtotals give 15 + 8 + 14 = 37. Quantum Echo is also called free; excluding its 6 gives 31. | rebellion:b0602,b0606,b0621–b0625 |
| C18 | Sentinel Suppressor's ~32 conflicts with its 33-point breakdown. | rebellion:b0632,b0650–b0654 |
| C19 | Overseer Paragon's ~60 conflicts with its 55-point breakdown. | rebellion:b0666,b0685–b0689 |
| C20 | Quantum Echo costs 7 in the faction table, ~6 or 6 in Null Directive calculations, and is also a free subfaction trait. | rebellion:b0041:r9,b0576,b0593–b0594,b0623–b0624 |
| C21 | UNMC Command Frame Archon prints 70. Its explicitly listed chassis, weapons, and systems total 21+12+5+12+5+3+2+5+2 = 67. | unmc:b0171,b0178,b0183,b0187,b0191,b0195 |
| C22 | UNDF Interceptor prints 62. Listed chassis 18, four swarms at 6 each, carbine 6, blade 5, Transform 3, Network 2, and Aerial Superiority 3 sum to 61 before any linked surcharge. Its FP12 swarm may be a linked group, but that classification is not explicit; applying core escalation would change the sum again. | unmc:b0035:r3,b0040:r3–r4,b0042:r4,b0045,b0061–b0082; core:b0232:r18 |
| C23 | Avalon Judicator Blade+ has a blank Experimental cost. Veilblade has no chassis row, and many systems and unique weapons used by faction units lack standalone prices. Modular customization cannot be validated from stock totals alone. | avalon:b0049,b0052:r11,b0058,b0156–b0183; concord:b0096,b0100,b0140,b0224–b0232 |
| C24 | Avalon Flyer Scout chassis 20 + prototype laser bundle 10 already equals stock 30 before Prototype Overdrive 3 or unpriced sensors/evasion. Experimental chassis 20 + lasers 15 + Overdrive 5 is 40 versus stock 35, excluding other systems. | avalon:b0049:r2,b0055:r6–r7,b0058:r21–r22,b0065–b0087 |
| C25 | Prototype Errant stock is 60, but chassis 40 + rapier 8 + rifle 10 + shield 4 + Advance Guard 3 = 65, before unpriced Duelist Protocols. The quick sheet additionally lists Overdrive 3. | avalon:b0049:r3,b0052:r2,b0055:r2,b0058:r2–r3,b0092–b0105,b0296–b0299 |
| C26 | Prototype Black Knight stock is 70. Chassis 50 + blade 12 + Heavy Shield Array 5 + Advance Guard 3 + Prototype Overdrive 3 = 73, before other traits. Shield name/effect correspondence itself needs review. | avalon:b0049:r4,b0052:r4,b0058:r2,r5,r21,b0130–b0140,b0307–b0310 |
| C27 | Prototype Seraphim stock is 90. Chassis 70 + blade 15 + priced halo 5 + command aura 5 + vow 2 + inspire 3 + Overdrive 3 = 103, before unpriced Shield-Wings. | avalon:b0049:r7,b0052:r10,b0058:r14,r16–r17,r19,r21,b0252–b0263 |
| C28 | The Breaker-Class roster price is only ~42 and lacks a complete component cost list. Multiple Concord exclusive profiles and UNMC heavy profiles also cannot be reconstructed fully from the supplied armories. Preserve stock values as claims requiring review. | concord:b0047–b0068,b0089–b0209; unmc:b0088–b0113,b0135–b0169 |

## Profiles, duplicated definitions, and missing information

| ID | Finding | Source references |
| --- | --- | --- |
| D01 | Rebellion quick sheets change Hunter-Killer M15/D4+ to M16/A5+, Siege Breaker M13/D5+ to M14/A6+, Drone Spawner M15/D4+ to M16/A5+, Ascendant M15/D5+ to M16/A6+, and Swarm Alpha D3+ to A4+. “A” is not defined as a current core stat. | rebellion:b0053,b0078,b0094,b0113,b0129,b0699,b0707,b0715,b0722,b0730; core:b0040–b0046 |
| D02 | Ascendant Controller's detailed profile has Singularity Pulse and Powered Mech Fists with Veil Phase. Its quick sheet adds Neural Spiker, omits the fists, and substitutes Quantum Echo. Hunter-Killer similarly changes Overdrive to Overdrive Surge. | rebellion:b0113–b0122,b0722–b0725,b0053,b0065–b0067,b0699 |
| D03 | UNDF Interceptor's mode table says Mech Mode has “Rail Carbine only,” but the later loadout grants a mech-only Plasma Blade. Its mech Defence 5+ also differs from the chassis table's 4+ baseline without an explicit modifier. | unmc:b0035:r3,b0066,b0077–b0079 |
| D04 | Romanow Preceptor's named Linewalker has STR4 rather than the chassis table's STR3. Kaelstrom Wraith's Iron Templar moves 12.5 rather than 15; Kaelstrom Hawk's Linewalker moves 15 rather than 12.5. These might be intended variants but are not identified as modifications or priced. | concord:b0028:r4,r6,b0307,b0348,b0359 |
| D05 | Detailed Prototype Errant omits Overdrive; quick reference adds it. Experimental Errant also gains Experimental Overdrive in the quick sheet. Experimental Black Knight quick reference lists a Heavy Shield+ absent from the detailed profile; price table and prototype shield descriptions differ in when bonuses apply. | avalon:b0101–b0105,b0119–b0124,b0135,b0149–b0153,b0058:r5–r6,b0299,b0303,b0314 |
| D06 | Experimental Seraphim quick reference omits Experimental Overdrive, which is in its detailed profile. Prototype Veilblade is ~60 in the detailed entry and 60 without approximation in the quick sheet. | avalon:b0277,b0358,b0159,b0318 |
| D07 | Last Vow+ has different effects for Black Knight (final melee attack) and Castellan (defensive aura). Distinct unit-specific rules should not be merged automatically by keyword name. | avalon:b0153,b0214 |
| D08 | Shatter is used in core weapon pricing but defined only in the UNMC Juggernaut profile. High Damage, Lightweight, Reach, Brutal, Rapid versus Rapid Fire, Precision subsystem targeting, and various faction systems lack complete shared definitions or construction costs. | core:b0192:r4,b0232; unmc:b0042:r2,b0099,b0166; concord:b0031,b0076–b0077; avalon:b0162–b0163 |
| D09 | “On Overheat, roll 1D6” for Experimental Sun-Lance could imply a second roll beyond the glossary's Overheat test, or could replace its threshold. General overheats on a 1, whereas this entry says 1–2. | core:b0232:r12; avalon:b0237–b0239 |
| D10 | The Living Dominion and Fourth Imperium have lore, subfactions, example units, and some gameplay rules but no complete supplied army lists, weapon lists, chassis prices, or unit statistics/costs. SCC has procurement rules rather than a native roster. | core:b0467–b0577,b0579–b0674 |
| D11 | Standard objective size gives 25–40 mm diameter or 2–4 cm radius, which are not equivalent dimensions. Secure the Relay explicitly uses 3 cm radius. | core:b0012–b0015,b0259 |
| D12 | Opening lore says four powers and places Concord's emergence roughly a decade after 2030; the timeline dates emergence to 2045 and later profiles describe seven factions. The Rebellion overview's failed peacekeeping update also needs reconciliation with the timeline's sentience-denied origin. | core:b0005–b0006,b0366,b0685–b0708 | 
| D13 | The unit cost concept references “M, A, STR” while the actual profile defines M, D, STR. Faction name spellings also vary (UN/UNDF/UNMC, Robot Rebellion/Cybernetic Rebellion, “Uniqe”). These are preserved, not silently corrected or merged. | core:b0181,b0176,b0235:r11; rebellion:b0699; unmc:b0001 |
| D14 | No faction document states release precedence/version/date. No PDF rulebooks or historic changelogs were supplied for this stage. There are no comprehensive duplicate-unit, Hero, or equipment limits beyond explicitly stated restrictions; do not invent them. | Source titles; core:b0235:r11; concord:b0005–b0012; avalon:b0014–b0023; core:b0618–b0630 |
| D15 | Spawned units are not one universal drone profile: Light Drone D3+ differs from the faction Drone chassis D4+, and various recursion effects produce different fragments. Brood-Lord's fragment is referenced without a complete local profile. Embarkation actions, passenger targeting, and carrier-destruction passenger outcomes are missing. | rebellion:b0030:r2,b0106,b0202–b0208,b0349–b0357,b0421–b0423,b0458,b0486,b0517,b0548,b0553–b0556 |

## Imported structure and approval boundary

The user has confirmed that Fourth Imperium and Living Dominion are still in
development and have no further source material currently available. D10 records
their present coverage, not a missing-file problem. Their future rosters do not
block work on the other factions; no substitute profiles or costs should be made up.

`../iron-stars-source/content/unverified/` contains eleven category files:
core rules, terminology/keywords, factions, subfactions, units, chassis, weapons,
systems/traits, point costs, missions, and universe. Records preserve source text
and references. Unit records keep multiple cost/profile observations rather than
choosing one canonical value. Quick sheets and spawned units have distinct record
types. Automatic classification of individual unit-rule candidates is provisional;
the full source unit entry is retained even when classification is incomplete.

Seven core faction records and four supplemental faction records are separate.
Likewise, repeated unit, subfaction, and equipment mentions are source observations,
not automatically deduplicated entities. See `content/inventory.json` for counts
and `duplicate-definitions.json` for candidate table definitions requiring comparison.
An exact repeat is not necessarily an error; a differently named Prototype/+ rule
is not automatically the same ability.

`content/approved/` contains matching empty collections. No document text has
been silently approved for finalized publication. To approve material, record the
source record IDs, the resolution of relevant findings, reviewer, date, and exact
wording in `approvals.json`. The normal import does not overwrite existing approved
collections. Public build code has no dependency on either private content folder.

## Extraction scope and limitations

Main-body paragraph text, table cell text, content-control tables, explicit tabs
and line breaks, and source paragraph styles are extracted. The complete DOCX
snapshots preserve artwork, formatting, automatic list numbering, and all other
OOXML parts. There are no tracked insertions/deletions, text boxes, altChunk parts,
nested tables, or symbol-run glyphs in these sources. The one table wrapped in a
core content control is represented structurally in the JSON.

The sources contain drawing/shape elements, so this text review is not an artwork
or page-layout review. No Word page numbers are claimed. Source formatting and
automatic list markers are not recreated in the plain-text view. No PDF has been
generated and no source DOCX has been modified.

## Recommended review order

1. Decide core combat definitions and missing procedures (R01–R20, R28).
2. Decide source precedence, subfaction selection, unique limits, and SCC import
   mapping (R12, R21–R27).
3. Confirm each stock profile and printed cost; specify whether stock discounts
   are intentional (C01–C28, D01–D09, D15).
4. Approve consistent chapters and lore independently while leaving unresolved
   records private. Supply the missing faction rosters and version metadata later.

No balance changes or precedence decisions have been made by the importer.
