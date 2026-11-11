# Private Iron Stars source content

This directory is development material. Do not upload it with the website.

- `originals/`: byte-identical snapshots of the five supplied DOCX files.
- `manifest.json`: filenames, source IDs, SHA-256 hashes, import status, and OOXML audits.
- `extracted/`: exact main-body text/cell observations in JSON and searchable Markdown.
- `content/unverified/`: categorized source observations, not finalized game data.
- `content/approved/`: separate collections reserved for explicitly approved records.
- `content/inventory.json`: counts by category; counts are not canonical entity counts.

See `../iron-stars-review/REVIEW.md` for discrepancies and missing information.
All imported content is currently unverified. `approved/` intentionally contains
zero records. This reflects a pending human review, not a statement that all
source material is incorrect.

The user has selected the latest source as the source of truth. The current
working precedence puts core v0.0.14 above older faction descriptions for shared
rules, using internal package dates as evidence. Explicit special rules remain
exceptions, and faction documents provide content absent from the core. See
`../iron-stars-review/source-precedence.json`. Same-document contradictions and
missing values still require review; newer-document precedence does not resolve
them or authorize invented costs.

## Reproduce the import

From the repository root in PowerShell:

```powershell
py -B iron-stars-tools/import_sources.py
py -B iron-stars-tools/organize_content.py
py -B iron-stars-tools/validate_content.py
```

Only the Python standard library is required. Import reads the five exact
filenames from the user's Downloads folder. It refuses to overwrite a snapshot
if the supplied document changes. Preserve revisions separately before importing
a new version. None of these scripts edits the source DOCX or public website.

`organize_content.py` contains the curated source ranges. Its row-level equipment
and keyword observations retain columns and values as written, including blank
costs and approximation markers. It does not normalize different printed stats
into a canonical profile. Unit records retain complete entry blocks, source cost
observations, and profile observations; `approved_point_cost` and
`approved_profile` remain null. Quick sheets and spawned-unit entries are
separate record types. Some unit-rule classification is explicitly provisional.

An observation includes a stable ID, source filename/hash, source block or table
row references, original text/cells, and review/publication status. `b0232:r13`
means source body block 232, table row 13. References are not Word page numbers.
Whitespace added between table paragraphs is structural serialization; original
paragraph strings are retained in the cell's `paragraphs` array. Formatting,
automatic list labels, and artwork remain in the source snapshot rather than
being recreated in Markdown.

The core version 0.0.14 is recorded from the supplied filename and user context.
Faction versions are null pending confirmation. No rules versions, publication
dates, artwork permissions, or changelog entries have been invented.

## Review and approval

Read the report and compare the exact source blocks before approving records.
Record the reviewer, date, source hashes, record IDs, relevant finding IDs, and
exact approved wording in `../iron-stars-review/approvals.json`. Keep any amended
wording alongside its original source text and explicit decision. Copy only the
reviewed records into the corresponding approved collections with their decision
references. Never treat the importer's unverified observations as finalized rules.

The organizer preserves existing approved collections. No public exporter exists
yet; the website generator currently imports no game data. Any future exporter
must allow only explicitly approved records and exclude these private directories.
The validator's duplicate-name report is a comparison aid, not an automatic merge
or claim that every repeated name is an error.
