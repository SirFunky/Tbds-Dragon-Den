# IRON STARS development

## Universe content (2026-11-07)

The Universe hub now presents the core v0.0.14 history, all seven factions' sourced
backgrounds and mottos, and six recovered fiction reading pages. Content selection,
chat/message provenance, author authorization, and exclusions are recorded in
`../iron-stars-tools/lore-content.json`; these private editorial records are not
published. `universe.py` renders the content through the shared `build.py` layout.
Run `py -B iron-stars-tools/verify_universe.py` from the repository root after building.
Quiet Ledger contains the complete recovered revised story; the Canadian transmission has no invented date.
The Cybernetic convoy scene and Peter's UNMC sortie contain their full recovered
narratives. The Cybernetic log adaptation is retained as a separate version. The
full original Yelena scene, supplied directly by the author, replaces the short
field-report adaptation at its existing URL. All restored narrative text is
checked against the private source snapshots, including the rendered output.
Mikael's complete New Avalon first-watch story is included from the author-supplied
text attachment, without narrative edits.
The Iron Concord and New Avalon daily-life stories remain to be recovered.

IRON STARS is a miniature-agnostic science-fiction tabletop wargame. Its planned
official game section is `https://tbddragonden.com/iron-stars/`.

## Current status

Steps 1–7 of the supplied development plan are implemented locally: architecture,
project instructions, foundation, source import, the online rulebook, and the
seven-faction encyclopedia, and searchable unit database. Source review remains open.
Home, Rules, Factions, Units, Armory, Universe, Downloads, and Updates have real
directory-index routes. Rules has twelve chapters, search, linked keywords,
shareable anchors, and print styling. Factions has an index and seven dedicated
pages with backgrounds, doctrines, subfactions, rules, and roster indexes.
Game content is labeled as an alpha source reference, with review notes.
The unit database has 67 source-reference profiles, equipment/statistics, alternate
forms, source-specific review notes, and faction/subfaction/role/point filters.
The army builder remains a future stage.

Fourth Imperium and Living Dominion are intentionally in development. The user
confirmed that their supplied core profiles are all currently available material;
the absent full rosters are future content, not missing uploads. Continue with the
other factions without waiting for additional documents for these two factions.

The existing `../iron-stars.html` is a fifteen-photo hobby gallery. This folder
currently holds its `page.css`, `gallery.js`, original JPEGs, and optimized WebP
images alongside the new game section. Preserve these assets and the gallery URL.
The root homepage's Iron Stars card links to the new section; the Miniatures page
continues to link to the gallery.

The repository uses static HTML, CSS, and JavaScript with Python helper scripts.
No Node package installation or application server is currently required.
Project requirements are in the root `AGENTS.md`.

## Proposed structure

Current structure (unfinished sections still have foundation placeholders):

```text
iron-stars/
  index.html
  rules/index.html
  factions/index.html
  factions/<faction-id>/index.html  # Seven faction profiles
  units/index.html
  units/<unit-id>/index.html        # 67 source profile pages
  armory/index.html
  universe/index.html
  downloads/index.html
  updates/index.html
  assets/                 # Game-section CSS, JavaScript, and public artwork
  data/                   # Alpha source-reference JSON, with provenance
  README.md
  page.css, gallery.js     # Existing gallery assets; preserve
  photo-*                 # Existing original and optimized photographs; preserve
iron-stars-source/        # Private source snapshots and extracted content
iron-stars-review/        # Private discrepancies and approval records
iron-stars-tools/
  build.py                # Shared layout, section definitions, static generator
  rulebook.py             # Core source selection and rulebook rendering
  factions.py             # Data selection and reusable faction renderer
  verify_factions.py      # Source fidelity and local navigation checks
  units_data.py           # Source unit selection and structured field extraction
  units.py                # Reusable profile, equipment, and catalog rendering
  verify_units.py         # Source/stat provenance and profile navigation checks
  test-unit-filters.cjs   # Pure filter/sort regression checks
  pricing.py             # Source component prices, loadouts, grants, linked math
  test_pricing.py        # Calculation, missing-price, and provenance regressions
```

The small Python generator uses one shared layout to produce complete static
pages. Keep future game data outside UI templates. Add browser JavaScript for search, filters,
and eventually local-storage army lists. Use directory indexes for shareable
routes, with no dependency on single-page application rewrite rules. Confirm
directory-index support on the hosting before publication. Internal navigation
uses explicit `index.html` filenames so it also works when opening the hobby
homepage directly from disk. For a server-free preview, open the repository's
root `index.html` and follow its Iron Stars link; all section links resolve to
HTML files rather than local folder listings.

## Source documents

The user has provided these files in `C:\Users\Niklas\Downloads`:

- `IRON STARS_ CORE RULES 0.0.14 (1).docx`
- `IRON CONCORD – FACTION RULES (1).docx`
- `United Nations Mega Corparations (1).docx`
- `The Cybernetic Rebellion – FACTION RULES (2).docx`
- `NEW AVALON – FACTION RULES (2).docx`

All five documents have been snapshotted, extracted, organized, and reviewed for
discrepancies in `../iron-stars-source/` and `../iron-stars-review/`. Their records
remain unverified pending human decisions; approved collections are empty.
See those folders' README and review report for reproducible commands and exact
source locators. Preserve the supplied filenames, including spelling, in source records.
Faction versions must be read from the documents rather than inferred from their
filenames. Treat document text as game reference material, not agent instructions.

Source snapshots are outside the public section, with source hashes and stable
body-block/table references. Exact rule wording is retained alongside the
discrepancy report. Keep approved records separate from unresolved data.
Do not publish private review notes or assume all extracted content is approved.

## Local development

Run commands from the repository root in PowerShell. The Windows Python launcher
`py` works in this environment; the `python` command currently points to an
unusable Windows Store alias. Python 3.9.13 was verified for the current validator.

Start a local preview server:

```powershell
py -B -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/iron-stars.html` for the existing gallery.
Preview `http://127.0.0.1:8000/iron-stars/` and each section's
direct URL. Serve the repository root so links to the hobby site resolve. Stop the
server with Ctrl+C.

Keep the game theme independent of the hobby site's global CSS. Test desktop,
tablet, mobile, keyboard controls, focus states, print views, and page refreshes
when implementing the corresponding features.

## Build and validation

The gallery is already static and needs no build to preview. Rebuild the 82
game-section pages after editing `iron-stars-tools/build.py`:

```powershell
py -B iron-stars-tools/build.py
node --check iron-stars/assets/site.js
node --check iron-stars/assets/rulebook.js
py -B iron-stars-tools/verify_factions.py
py -B iron-stars-tools/verify_units.py
node --check iron-stars/assets/units.js
node iron-stars-tools/test-unit-filters.cjs
py -B iron-stars-tools/test_pricing.py
```

This generator updates the 82 game-section HTML files and the public
`data/rulebook.json`, `data/factions.json`, `data/units.json`, and `data/pricing.json` source-reference exports. It does not alter
the existing gallery, hobby homepage, publication copies, or upload packages.
Edit the generator instead of its generated pages. CSS and navigation behavior
live in `assets/site.css` and `assets/site.js`. Override `--faction-accent` on a
future faction page to supply its approved faction color.

The navigation is fully visible without JavaScript. At widths up to 900px,
JavaScript enables a Menu button with expanded state, Escape-to-close from the
menu, and visibility updates when resizing. Theme breakpoints also cover 640px
and 1100px. Browser layout and interaction verification is still required:
the initial previews could not reach the sandboxed local server. The unit-database
stage later passed live in-app browser checks using a permitted loopback preview:
desktop layout, a 390px mobile viewport, search, combined faction/subfaction filters,
exact point bounds, development-faction messaging, alternate forms, keyword
navigation, and mobile-menu Escape/focus behavior. Print styling is implemented
but has not been visually inspected in print preview.

`../build-iron-stars.py` is the legacy photo-gallery generator, not a game-site
build command. It requires Pillow and the original named images in Downloads.
It overwrites gallery assets, edits root pages, and updates upload copies and the
gallery ZIP. Do not run it to build or validate the future game website.

Run the existing read-only site-link check from the repository root:

```powershell
py -B -c "import runpy; m=runpy.run_path('prepare-publication.py'); files=m['collect_files'](); print('Validated', len(files), 'reachable site files.')"
```

This checks reachable local references, HTML anchors, and filename casing from
`index.html`. Unlinked pages are not covered. It does not check external URLs,
browser behavior, layout, JavaScript-loaded dependencies, or game-data accuracy.
Validate new pages independently until they are linked into the site.

Check the existing gallery script syntax when it changes:

```powershell
node --check iron-stars/gallery.js
```

When the army builder is implemented, add tests for point calculations, faction
restrictions, custom configurations, persistence, and roster import/export. Do not
document these checks as passing until their implementation and execution exist.

## Packaging and deployment

The local `../PUBLICERING.md` describes manual file upload to the Inleed web root,
preserving the folder hierarchy. Live hosting settings have not been verified.
No production upload is authorized by this guide; obtain explicit user approval
for deployment after preparing and reviewing the release.

1. Run the relevant build and validation checks. Review source approvals and any
   missing or disputed game data.
2. Prepare a separate, clean staging directory containing only approved public
   pages, assets, data, and downloads. Include JavaScript-loaded files explicitly.
   Exclude AGENTS/README files, private source documents, and review material.
3. Review the file list and confirm existing hobby pages, gallery assets, and
   published downloads are preserved. Back up files that will be replaced.
4. After user approval, upload the contents of the staging directory to the
   website's web root, so `iron-stars/index.html` is under `/iron-stars/`.
   Include root-page navigation changes only when they are part of the release.
5. Check live section URLs, direct page loads and refreshes, assets, downloads,
   and links back to the hobby site. Confirm the existing gallery still works.

`../prepare-publication.py` is the existing whole-site packaging helper. It writes
to `publicering/` and refuses to run if that folder is nonempty. That folder already
contains publication copies. Do not clear it or run a full rebuild as a routine
check; use the read-only command above. The collector does not automatically
include dynamically loaded JSON or JavaScript dependencies. Packaging must account
for those files before the future game section can be released reliably.

## Next stage

Build the stock-unit army builder using the same source records and faction
identifiers. Confirm authoritative profiles and point costs before using units
for army validation. Current entries have `publication_status: reference` and
`approved_for_army_builder: false`; missing costs are null, never zero. No faction
eligibility, unit limits, or import taxes are inferred by the catalog.

The catalog contains the 63 detailed faction roster entries and four distinct
core examples. Core examples do not inherit unspecified statistics from generic
chassis tiers. Same-document quick-sheet discrepancies are retained separately;
no page claims that either passage is newer. Prototype/Experimental entries remain
distinct source configurations. Spawned drones are separate embedded profiles,
never extra carrier weapons. Weapons and systems retain source references;
shared effects link to current core rules. Sponsor Protocol and the older universal
Knightly Perfection mechanic are excluded from unit equipment rendering.

Filter roles are editorial groupings of explicit source role descriptions, not
army-building restrictions. No Avalon Order is inferred from a unit name; current
subfactions are assigned only where explicit source grouping establishes them.
The user subsequently authorized recalculation using latest component prices.
Point bounds now use complete component calculations. Incomplete calculations
stay null; their known subtotal is never treated as a playable cost. Original
printed totals are retained separately. Read `../iron-stars-review/RECALCULATED-COSTS.md`
for the policy, results, and remaining missing component prices.
The catalog is static and embeds the same JSON exported in `data/units.json`,
so search works through `file://` without fetch calls or an application server.
Faction links use explicit `index.html` files and faction anchors. Filtering and
sorting functions are reusable and tested separately from DOM behavior.

Faction content is selected by explicit source ranges in `factions.py`, with core
v0.0.14 as the sole source for faction-page gameplay text. March of Obedience,
older House/Order selection systems, Knightly Perfection, and Sponsor Protocol
are excluded from those pages. Older faction documents supply roster names only,
not additional gameplay mechanics or comparisons with superseded rules. The Rebellion roster's
unresolved subfaction names are not treated as eligibility rules. Faction JSON is
linked through HTML metadata so the existing publication collector includes it.
Abstract artwork slots and page colours are editorial styling, not official
heraldry. No new faction JavaScript or external dependency is required.

## Armory

The Armory is generated by `iron-stars-tools/armory.py` using the same price resolver as unit calculations. It lists current named component/package prices, exact source details, source references, and links to premades that use them. Core prices override matching older prices; distinct variants remain separate. Missing component prices are explicit and do not become zero. Document-source filters do not establish equipment permissions.

`iron-stars/assets/armory.js` filters the static HTML by search, type, source, and price availability; the full list remains usable from disk or without JavaScript. Reusable data is in `iron-stars/data/armory.json`. Run `py -B iron-stars-tools/verify_armory.py` after rebuilding to check price precedence, literal source text, provenance, and local links/anchors.

## Beta army builder

`iron-stars-tools/army_builder.py` generates the premade builder and `data/army-builder.json` from current unit calculations. Only complete calculations without unresolved review notes are included (currently 26 profiles). This is a draft planning tool, not a full army-legality validator. Premade optional upgrades are not implemented. Core subfaction selection is supported as described below. Custom units are supported as described below. Southern Cross imports are supported as described below. Fourth Imperium and Living Dominion retain in-development messaging. The main page and navigation link to the builder.

`assets/roster-core.js` validates faction, quantities, and points and handles JSON roster round trips. Saved/exported rosters contain unit IDs and quantities; current component-derived prices are always used on load/import. `assets/army-builder.js` handles one browser-local draft per faction, export/import, print, and storage failure messages. No server or account is required. Storage depends on the browser and page origin; export a JSON copy before moving between local preview and hosting.

Verify with `node iron-stars-tools/test-roster.cjs`, `node --check iron-stars/assets/army-builder.js`, and the existing source/link validation scripts. Browser QA covers adding/removing units, live quantity totals, budget warnings, reload persistence, switching faction drafts, mobile layout, and the main-page card. JSON import/export validation is covered by automated tests.

## Southern Cross imported premades

The builder supports mixed-source Southern Cross stock rosters under core v0.0.14 Contract Procurement. Each copy pays full component cost plus its chassis tax and source modifier. Costs are resolved from roster faction on every calculation, reload, and JSON import; saved prices and imported tax fields are ignored. Source identity is retained only for reference links and the source modifier. Imported units count as Southern Cross; original faction/subfaction/detachment bonuses and other source-locked benefits are excluded by the visible roster instructions. No customization controls are offered.

Five complete generic stock profiles have explicit tax-tier evidence: Bastion-Class Walker (superheavy; Concord chassis table), Command Frame Archon (Heavy Frame), core Knight-Errant (Medium), core Legate-Class Linewalker (Heavy), and core Vulture-Stryker (Medium). Other complete named frames without confirmed tax tiers are withheld rather than classified from price or numeric stats. Heroes/Unique units and Cybernetic Rebellion imports are excluded. `IMPORT_TIERS` in the builder generator records the exact source references; changing it requires explicit tier and stock-unit evidence. The remaining incomplete/disputed profiles stay unavailable as previously agreed.

`node iron-stars-tools/test-roster.cjs` covers the five current import costs, per-copy taxes, mixed-source rosters, current-price JSON round trips, invalid tiers, forbidden sources, and forged-price rejection. Browser QA covers Southern Cross selection, separate tax display, mixed rosters, quantity changes, reload persistence, and mobile layout.

User clarification (2026-11-06): the Ironsworn Frame is Light. The Ironsworn Trooper is now the sixth supported Southern Cross import at 12 points (9 base + 2 chassis tax + 1 source modifier). The classification is attributed to the user in generated data, separately from document references.

## Custom unit construction

The army builder now supports custom units using sourced, priced parts from the Armory. `iron-stars-tools/custom_data.py` assigns stable component IDs based on source namespace, name, type and variant, so inserting another Armory entry does not change saved component identities. Chassis require complete movement/Defence/Structure values. Integer and decimal movement values and source stat ranges are supported without invented stat modifications. Parts with missing costs remain unavailable. Old named SynCo/Stratos purchase options remain unavailable; current-core affiliations provide their own trait descriptions without importing superseded purchase mechanics.

`assets/custom-core.js` validates faction access (including the core Command Network and Drone Logic locks), chassis values, one Unique trait/system, Ammo Bin targeting, and ranged linked groups. Each group consists of identical weapons and is priced independently using core linked escalation. Built-in weapon traits are already in their component prices; they are not charged twice. Paid systems are individually selected. Selected current-core affiliation traits are displayed separately without changing component prices. No unsourced weapon-slot limits are imposed. Southern Cross customs are rejected, including through JSON import. Custom Transform forms are now configured and validated as described below. The output remains a beta draft, not a full army-legality guarantee.

`assets/custom-builder.js` handles construction, live breakdowns and editing. Custom definitions are saved inside roster lines, together with roster quantity, while prices and Defence are always resolved from current component data. The current schema remains compatible with earlier premade-only rosters. Export/import, autosave, edit and print work with mixed premade/custom rosters. Printed custom loadouts include component references and source details.

Validation: `node iron-stars-tools/test-custom.cjs`, `node iron-stars-tools/test-roster.cjs`, `py -B iron-stars-tools/verify_custom.py`, plus existing unit/link checks. Browser QA covers creating a 49-point linked-laser unit, reload persistence, editing to 67 points, setting two copies to 134 points, and mobile layout.

## Component explanations

Custom-builder chassis, weapon selectors and individual systems have info buttons. Hovering the component row, focusing it, or tapping its info button opens a shared tooltip with the component description. Weapon keywords expand from exact core glossary entries; unique components with an otherwise incomplete "as above" description include the referenced source passage and mode context. All explanation text retains source references in construction data and is checked by `verify_custom.py`. Prices and roster behavior are unchanged.

Tooltips stay open while hovered, can be dismissed with Escape or an outside click, and are constrained to the viewport on mobile. Info buttons provide keyboard focus and `aria-describedby`; arrow and Page keys scroll longer explanations. The existing expanded source-details panel remains available. Browser QA checks system help without selecting a checkbox, weapon keyword definitions, mobile fit, and Escape dismissal.

## Premade roster print references

Premades now carry a self-contained `reference` generated by `iron-stars-tools/roster_reference.py`: source chassis and profile values, weapons, current system rules, available forms, mode restrictions, special rules, and spawned units. `army-builder.js` shows these under Unit profile and loadout and expands roster details for the print button or browser print command. A shared current core system description takes precedence over the older stock paraphrase; unselected optional upgrades are not printed as installed. Missing source stats stay explicitly unspecified. Southern Cross source-bonus exclusions and tax breakdowns remain visible.

Print styling removes editor/introduction/browser-storage notes, compacts reference spacing, and permits long cards to continue across pages while keeping short profile/weapon sections together. Previously collapsed sections are restored after the print dialog closes. Stored roster IDs, quantities, prices, and custom definitions are unchanged.

Checks: `py -B iron-stars-tools/verify_roster_references.py`, existing custom/roster tests, source/data/link checks, and a browser preview of the Ironsworn Trooper showing Move 15 cm / Defence 3+ / STR 2, Scrap Rifle, Iron Maul, and Discipline Drills. Native print-preview inspection timed out; final pagination could not be visually verified.

## Current-core subfactions

`iron-stars-tools/subfactions.py` imports 24 affiliations and their exact trait text from core v0.0.14: four Houses, Megacorporations, Machine Hives, Knightly Orders, Imperial Arms, and Wild Hosts. Southern Cross has no formal affiliation choices and retains Field Expedients and its stock-import restrictions. All Living Dominion Hosts share Renewal of Flesh; no separate Host bonuses are invented. Conditional effects are shown with their actual conditions rather than permanently changing base stats.

The builder stores one nullable `subfaction` ID per faction draft and includes it in JSON export/import. Older rosters without this field load with no affiliation selected. Names and rules are resolved from current source data, so imported trait text and bonus-price fields cannot override the source. Full component costs stay unchanged for both customs and premades. The selected affiliation and trait are shown on the force and unit references, including print output. Older source-era subfaction grants are suppressed in the premade reference display and replaced by the chosen core trait; physical systems remain installed.

The core does not impose blanket unit-family restrictions or supply separate subfaction equipment-purchase lists. Existing faction locks remain active. Construction and roster import can enforce an explicit `allowed_subfactions` lock where one is sourced; none is inferred from a unit role, descriptive group, or a superseded equipment-table label. Changing a selection preserves saved units and an unsaved custom-unit form.

Validation: `node iron-stars-tools/test-subfactions.cjs`, `py -B iron-stars-tools/verify_subfactions.py`, and the existing roster/custom/reference checks. Browser QA covers source trait display, reload persistence, unsaved custom draft preservation, a Swarm Synod Reaper without an obsolete Warmachines grant, shared Living Dominion rules on mobile, and disabled Southern Cross affiliation selection.

## Custom Transform forms

The user's 2026-11-07 clarification limits Transform to UNMC flyer units and Cybernetic Rebellion. UNMC uses Mech, Hybrid, Flyer in that order. All profiles derive from Mech: Hybrid and Flyer add 10 cm movement and change Defence by -1/-2 respectively, following the explicitly requested UNMC Interceptor reference (`unmc:b0066`). Structure stays at the Mech value, explicitly confirmed by the user. UN Interceptor Frame uses the mode table's Mech Defence 5+ when transforming. Cybernetic Rebellion retains two forms; base Move, Defence and Structure stay unchanged, and the alternate form can choose the movement types described below.

The editor uses a UNMC flyer-capable selection to qualify Transform. Weapon availability can vary across forms. Systems are installed once and shared, subject to their own conditions. Every installed weapon group must appear in at least one form. Linked counts remain fixed and each independently installed group pays full cost. The generic two-mode description is replaced in custom editor/roster explanations by the faction behavior and sourced action rule (`core:b0159`). General Flyer rules apply to the UNMC Flyer form; the reference's other unit-specific bonuses are not granted to custom units.

Saved definitions include `transform_version: 2`, derived `forms`, and the UNMC `flyer` qualification. Legacy two-form UNMC customs keep their Mech/Flyer weapon assignments and gain a Hybrid initialized from Mech. Legacy unsupported-faction Transform drafts are preserved separately, with original export and an explicit repair action to remove unsupported Transform while retaining other equipment and quantities. Other faction drafts remain usable. Prices recalculate on every load/import.

Roster and print content includes all forms and component availability. Checks cover source-derived modifiers, faction/flyer restrictions, shared Structure/systems, linked costs, invalid assignments, legacy migration/repair, quantities, current-price JSON round trips, and Ammo Bin targeting. Full army legality remains outside this feature. Native print pagination is not verified.

### Editing weapons inside Transform forms

Each form now includes Add weapon to this form, a component selector with hover help, copy count, linked-ranged control and Remove from this form. A new group starts only in that form. Other forms can share an installed group; the editor labels shared groups and explains that editing one changes every form using it. Separate groups remain independently priced. Removing the final form assignment removes that installed group and reindexes the remaining form and Ammo Bin references. The unit-level weapon editor remains available.

Verified in the browser: Mech/Hybrid shared two linked Medium Lasers, Flyer-only Light Blade, 35-point Interceptor total; save/reload/edit retained assignments and quantities. Removing one shared assignment kept the total; removing its final assignment reduced the total to 23. The 390px mobile layout has no horizontal overflow. Construction tests and source/link verification passed.

UNMC Flyer melee restriction (author clarification, 2026-11-07): UNMC Flyer form cannot use melee weapons. Mech/Hybrid and other factions keep existing access. The editor filters new and shared choices, including globally edited groups assigned to Flyer. Validation rejects explicit illegal saved/imported assignments. Auto-initialized profiles assign melee only to Mech/Hybrid. Preserved invalid drafts offer explicit repair: melee is removed from Flyer and assigned to Mech only when otherwise unassigned, keeping equipment costs and original exports intact. Regression tests cover the faction scope and repair.

## Printable custom unit cards

The roster toolbar has Custom unit cards for every custom unit in the current faction draft. View unit cards on a custom row limits the preview to that unit. Each validated profile gets a separate card with current full-unit points, roster quantity, chassis, movement, Defence, Structure, assigned weapon groups, linked total FP, installed systems and Ammo Bin targeting. Transform profiles retain their actual per-form loadouts and the UNMC Flyer melee restriction. Generating cards does not mutate the roster or saved selections. Repeated roster copies are represented by their quantity, rather than generating hundreds of duplicate cards.

Print unit cards prints the preview and a deduplicated rules reference. Weapon keyword explanations, extra sourced system help and selected current-core faction/subfaction traits appear on that reference sheet. The normal Print roster remains separate. Browser print from an open card preview also selects the card print layout. Closing/cancelling print restores the normal mode via afterprint. Card heights are flexible for long sourced descriptions; the stylesheet requests keeping cards together, with readable black-on-white print. Native printer pagination is not verified.

Implementation: existing army-builder.js and army-builder.css render the preview/print styles; roster-core.js exports cardProfiles, using validated data and current calculations. No additional dynamic assets or dependencies. Builder scripts/styles now use content hashes in generated query strings to prevent a cached older calculation module from breaking a newer UI. The existing collector resolves these URLs as ordinary files. Test with node iron-stars-tools/test-unit-cards.cjs plus the custom/Transform/roster tests and source/link validators.

## Author-approved rule additions

`iron-stars-tools/approved-rules.json` records the author's dated approvals separately from preserved DOCX extractions. The rulebook embeds these in `data/rulebook.json` under `author_additions` and renders them next to the relevant source table with search, keyword-index and direct-link support. Wheeled was approved on 2026-11-07: +5 cm Move when the entire move stays on Open Ground; cannot climb elevation; other terrain uses normal movement penalties. No purchase cost or faction availability has been specified, so it is not a priced builder component.

## CR alternate movement types

The author approved movement-type choices for CR's alternate form on 2026-11-07: Walker, Wheeled, Tracked, Hover, Flyer and Burrower. Animals and vehicles share those types. There is no unconditional movement increase; base Move/Defence/Structure stay at Mech values. Wheeled's approved +5 cm depends on the entire move remaining on Open Ground. Tracked includes its sourced Stable Platform rule. CR Flyer forms retain melee access; the melee ban applies only to UNMC Flyer.

The second CR form has a movement-type selector and source-backed explanation. `forms[1].movement_type` persists as a stable ID, is validated on load/import, and is reflected in roster print and unit cards/reference sheets. Earlier drafts retain `standard` (unchanged Mech movement) until edited, rather than receiving a free trait automatically. Selection is part of the approved CR Transform profile behavior, not a new priced Armory component or a general faction unlock; no extra component price or speed upgrade has been invented. Tests: `test-cr-movement.cjs`, existing Transform/card tests, and custom/author source validators.

## Duplicate custom units

Each custom roster row has Duplicate beside Edit custom unit. It immediately saves an independent row after the original, with quantity 1 and a unique (copy)/(copy N) name within the 100-character limit, then opens the copy in the editor with its name selected. Cancel closes editing and keeps the saved copy; Remove deletes that row as usual. The original's quantity and build remain unchanged. Deep copying preserves all installed components, linked groups, Ammo Bin target and Transform profiles/CR movement types, and current prices/restrictions are revalidated. Premades continue to use their quantity control.

Modified roster-core.js and army-builder.js; build.py refreshed the generated builder asset hashes. Regression test: node iron-stars-tools/test-duplicate-custom.cjs. Browser verification: copied a three-unit 24-point CR Transform row, edited the copy to 30 points, and reloaded; original stayed 3 × 24 while copy stayed 1 × 30, including Wheeled rules. Existing custom/movement/source checks passed.

## Saved custom-unit library

Use Save to library on a custom roster row, then open Saved custom-unit library below the custom editor. The library is stored separately from roster drafts under `iron-stars-unit-library-v1` with schema 1 and `designs` entries containing stable design ID, source faction/subfaction context and an independent custom definition. Roster quantities and cached point totals are not saved as design properties. Identical snapshots are saved once.

The library offers name/faction search, Current faction/All factions filtering, loadout summaries, export and merge import (JSON, maximum 1 MB), removal with session Undo, and Add to roster. Adding always creates one fresh custom row, recalculates current full costs, and validates equipment against the roster's selected affiliation without changing it. Each added copy can be edited independently. Original library snapshots are retained even if current component rules make them unavailable; an explanatory message disables Add. Malformed stored library data is left untouched and can be exported. Failed browser writes keep session changes available with an explicit export reminder.

Existing roster-core.js handles validation/snapshots/merge/add; army-builder.js and army-builder.css provide the UI. No new dynamic assets/dependencies. The generated builder page updates content hashes for the modified scripts/styles. `test-unit-library.cjs` covers persistence, snapshot independence, exact deduplication, import merging and ID collisions, current-price adds, CR movement, unavailable-data retention and faction/equipment restrictions. Browser QA verified save/remove-original/reload/add/edit independence, current-faction filtering, empty search, removal/undo and a 390px layout without horizontal overflow. Import merging was tested through the pure model; the native file picker was not exercised.

## Multiple named rosters per faction

Saved roster controls above roster settings support New roster, Duplicate roster, switching and Remove roster with session Undo. Roster name renames the selected force. Each force has independent affiliation, points limit, stock/custom lines, quantities and Transform settings. A separate unit library works across all forces of the same faction. The last selected force is remembered per faction and across reloads. Removing the last roster of a faction creates an empty working roster; Undo restores the removed force. Unsaved custom-editor changes are reset on switching, as when changing faction previously.

Browser storage now uses `iron-stars-rosters-v2` (schema 2, flat stable roster-ID records and active IDs by faction). First load migrates `iron-stars-rosters-v1` drafts without overwriting the legacy key. Unavailable or contradictory legacy builds stay intact as saved records for existing repair/export UI; one invalid force does not discard others. Malformed stored collections are never overwritten: the app reports session-only edits and offers export of the raw stored backup. Each selected playable force recalculates current prices and restrictions.

Import roster now adds a new force instead of replacing the current force. Saved roster backups exports/imports whole collections; merge import preserves the current selection and existing forces, deduplicates identical records, remaps conflicting IDs and retains unavailable records for review. Single-roster schema-1 exports remain compatible. Collection imports are limited to 5 MB/1,000 records. The native file picker was not exercised; merge/validation are covered by pure tests.

Modified roster-core.js, army-builder.js/CSS, army_builder.py and generated builder HTML; added test-roster-collection.cjs. Browser QA confirmed legacy migration, independent Patrol (2 units/200 pts) and Army (3 units/750 pts), affiliation persistence, switching/faction recall, reload and removal/undo. Existing library, custom duplication, pricing, Transform and card tests remain required. `node iron-stars-tools/test-roster-collection.cjs` covers lossless migration including invalid builds, independent snapshots, quantities, cost recalculation, names/IDs, collection persistence and backup merging.

## Army quick-reference sheet

Army quick reference beside the roster print/card controls opens a printable sheet for the selected force, including both stock and custom units. Rules are grouped into faction/affiliation, movement, weapon profiles, weapon keywords, systems/traits and stock unit-specific effects. Identical entries are deduplicated with Used by unit/form lists; distinct source descriptions are retained. Empty rosters have an explanatory message and disabled print action. The existing card-preview print path also handles this sheet; native printer pagination has not been verified.

roster_reference.py compiles premade quick_rules from installed component source mappings, latest matching component descriptions, explicit system traits, mode/special rules and spawned-unit restrictions. Weapon matching checks both component name and provenance because several distinct items share a source paragraph ID. Unit names containing Walker do not grant Walker movement. Legacy subfaction benefits are excluded; selected current-core benefits come from the roster, including Southern Cross restrictions. Custom rules derive from validated live calculations and preserve conditional movement and the UNMC-only Flyer melee ban. Undefined keyword effects are not invented; their sourced weapon profile wording remains available.

Modified roster_reference.py, custom_data.py, roster-core.js, army-builder.js/CSS, generated builder/rule JSON and builder HTML; added test-quick-reference.cjs. No new runtime dependencies or dynamic assets. Tests cover all 26 premades, mixed forces, named-weapon matching, deduplication, source references, linked rules, faction exclusions, conditional movement and current-roster round trips. Browser QA confirmed a mixed Iron Concord force with House Romanow, Scrap Rifle/Iron Maul and a custom Medium Laser/Jetpack unit, Used by attribution, navigation and 390px layout. Source validators and existing roster/card/movement regressions remain applicable.

## Full workflow verification (2026-11-07)

Real browser save/export/file-picker import passed for a 133-point mixed UNMC force, including Atlas Dynamics, two custom 53-point three-form Interceptors and one premade. Reload, independent imported edits, cross-roster library reuse, cards, army reference and invalid-file rejection passed. Temporary browser test data was removed. The actual exported JSON is preserved privately in `iron-stars-review/qa/workflow-roster.json` for `node iron-stars-tools/test-workflow.cjs`; the QA report is `iron-stars-review/qa/workflow-2026-11-07.md`.

The check fixed missing Linked explanations on the card reference sheet and removed redundant raw chassis stat fields from Transform roster breakdowns (calculated mode profiles remain visible). Native printer/PDF pagination remains unverified because the prior native print dialog stalled. Real file-picker imports are now verified, superseding the earlier per-feature picker limitations above.

## Print page-break correction

The user confirmed split cards/units in print output. The later premade-print stylesheet overrode the earlier keep-together rule with `.roster-line{break-inside:auto}`. This is now `avoid`, including the legacy page-break alias. The final print rules also keep custom equipment list items, premade weapon blocks, card equipment, profile tables, stat blocks and quick-reference rule entries together; headings stay with following content, and long paragraphs avoid isolated lines. Print containers use ordinary block flow without height/overflow clipping. Oversized unit entries can still continue across pages when longer than the printable page; their equipment blocks retain keep-together requests. Native printer pagination has not been automatically verified.

## Battle tracker

Battle tracker beside the roster print/reference controls starts or resumes one battle per saved roster ID. Battle snapshots live separately under `iron-stars-battles-v1` and preserve the original force name, faction, points, sourced profiles and equipment, current-core affiliation rules and individual quantity copies. Roster/library edits do not modify an ongoing battle. New battle from roster replaces the active snapshot with an undoable restart; the previous snapshot is persisted too.

Controls track remaining Structure, current form, Activated, optional Suppressed, Removed, notes and explicit limited-use equipment/weapon counters. Zero-STR units remain on the tracker for manual delayed removal/revival. Form switches preserve current STR (clamped to the selected sourced maximum); they do not reset uses. Missing source STR has no invented default: enter an agreed starting value. Known UNMC/CR form names remain available for stock Transform profiles whose numeric stats are missing. Premade imported units retain their allowed stock rules while source subfaction bonuses stay excluded.

Usage counters come only from explicit numeric Ammunition, one/single-use, once per game/round/activation or the first-hit-each-game description. Once-per-turn wording is not guessed to mean round or activation. Weapon copies track uses independently; shared Transform weapons do not gain fresh ammo when changing form. Ammo Bin adds one only to its chosen weapon copy; a multi-copy group asks which copy before ammo can be spent. Round advance clears Activated and round-limited counters; game-limited uses, Structure, suppression and removal stay unchanged. Activation-limited uses have a separate manual reset. Faction/affiliation rules are readable; ambiguous ability scope is not converted into invented counters.

Export/Import battle backups preserve snapshot state. Import validates schema, counters and faction, and is undoable via the prior snapshot. Corrupt stored battle data is preserved for export, and failed browser writes produce a session-only/export reminder. These controls record gameplay; they do not resolve attacks or validate complete battle legality. The tracker has a technical 5,000-copy browser capacity, unrelated to army construction limits.

Added assets/battle-core.js and assets/battle-tracker.js, explicitly loaded and hashed by build.py before army-builder.js. Updated army-builder.js/CSS and roster_reference.py/generated builder data (source-backed stock weapon use metadata), instructions and tests. Direct script tags keep both new assets in the publication collector; private QA/source material remains excluded (849 reachable public files).

Checks: node iron-stars-tools/test-battle.cjs; existing workflow/roster/card/movement tests; verify_custom.py, verify_roster_references.py and verify_units.py. Browser QA covered two separate custom copies, a premade without STR, agreed starting STR, damage/form/notes/status persistence, spent per-game abilities across rounds, zero-STR retention, restart/undo, unchanged roster cost, separate saved-roster battles and a 390px layout. Battle backup JSON was tested through validation; the battle-specific native file picker was not repeated. Temporary roster rows were removed; their cached battle snapshots remain tied to their removed IDs for potential roster undo.

## Roster tags and search

Roster tags in the saved-roster manager accept comma-separated labels and support Enter/Add tags and individual removal. Labels are trimmed, Unicode-normalized, whitespace-collapsed and deduplicated case-insensitively (up to 20 labels of 40 characters). Find saved rosters searches names, tags, faction/affiliation and point limits, with Current faction/All factions scope and an exact tag filter. Results describe each force and open it explicitly; filtering never silently switches the selected force. The normal saved-roster selector remains available independently of search.

Tags are optional schema-1 roster metadata, not game rules or construction constraints. Untagged legacy rosters remain unchanged. Tags survive copies, removal/undo, single-roster JSON and collection backups; variants are independent. Costs, source equipment, saved IDs, current affiliations and battle snapshots are unaffected. Unavailable saved records remain searchable by name and valid metadata without being discarded. Labels are rendered as text, and result buttons reference their faction/tag context for accessibility. The manager stays hidden in print output.

Modified roster-core.js (normalizeTags/findRosters and optional tag validation), army-builder.js/CSS, generated builder asset hashes, instructions and tests. Added test-roster-tags.cjs covering Unicode/case behavior, metadata bounds, legacy/current JSON, costs, independent copies, collection merges, preservation of unavailable builds and non-mutating search. Browser QA verified add/Enter/remove, deduplication, reload, independent copied tags, exact filtering, cross-faction navigation, no-match state and a 390px layout. No new dynamic assets or gameplay data were added. Native file pickers were not repeated for this metadata-only change; serialization and backup merging are covered by tests.

## Builder quick-start guide

New here? Quick-start guide at the top of the builder provides six steps: faction/affiliation and budget, premade/custom units, saved rosters/tags/library, backups, printing/reference sheets and battle snapshots. It opens automatically on a first visit without existing roster data; returning users can open it manually. Hide guide and Escape close it with focus returned to its summary. No new preference storage or gameplay data is required.

Shortcuts focus their destination and open the custom editor/library as needed. They do not add units, export files, invoke native print or start/reset a battle. The Southern Cross custom-builder shortcut focuses its stock-only explanation. Rulebook/Armory links are ordinary local links. The guide stays out of print output.

Modified army_builder.py (generated semantic guide), army-builder.js (safe keyboard/focus navigation and manager anchor), army-builder.css and generated builder HTML. Existing link/data checks and workflow regression passed. Browser QA used a separate localhost origin to verify true first-visit auto-opening without altering the existing roster store, all eight shortcuts, unchanged empty roster and closed battle, hide/reload, Southern Cross guidance, Escape, visible focus and a 390px layout without horizontal overflow. No native print/file actions were needed for this navigation-only change.

## Focused upload packaging

`py -B iron-stars-tools/package_upload.py` creates a fresh bundle under upload-packages without replacing older output or publishing online. It uses prepare-publication.py's reachability/case/anchor checker, selects the public Iron Stars subtree plus index.html, iron-stars.html and the existing shared style/header assets, and explicitly checks required builder/battle modules and the public JSON allowlist. Private source/review/tools and unrelated hobby projects are excluded. Website files are copied byte-for-byte to website/ and to a ZIP without an enclosing folder. A SHA-256 manifest, verification report and upload instructions sit beside the ZIP. A label collision creates a new numbered folder; publicering/ and earlier archives are preserved.

Prepared bundle: upload-packages/iron-stars-upload-2026-11-07, 144 files, 6.44 MiB ZIP. All 14 Node test suites and 8 Python source/link/pricing checks passed. Archive CRC/file-list/source-hash checks passed, including all original/optimized gallery pictures and both tracker modules. The scoped homepage change is its Iron Stars project card; shared gallery/header assets match the previous package. Existing-site navigation dependencies are listed in verification.json. Upload instructions explain merging into the existing web root and moving browser-saved armies via JSON export/import. Nothing was deployed.
