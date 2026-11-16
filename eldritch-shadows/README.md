# Eldritch Shadows web section

The canonical landing page is `/eldritch-shadows/`, served by `index.html`.
Edit the current web pages and assets in this directory. The rules download is
`rulebook.pdf`. Put updated author-supplied PDFs at
`Eldritch shadows/EldritchShadows.pdf`, then run the packager: it copies the exact
supplied bytes to the clean download path and includes both paths in the ZIP.
Keep the author's PDF unchanged. The legacy `Eldritch shadows/` directory retains
source inputs, shared legacy assets, and redirects for existing bookmarks.

Run `prepare-eldritch-shadows.py --package` with Python to check local links,
redirects, assets, saved-character compatibility, and the rulebook download,
refresh the PDF's cache key, update publication copies, and rebuild
`uppdatering-eldritch-shadows-1.0.zip`. Running without `--package` checks only.
This does not deploy the site.

The existing character generator is still invoked as
`Eldritch shadows/build-pregens.py`; it now reads the template here and writes
character pages and PDFs to `eldritch-shadows/pregens/`. Its source profile data
remains in `Eldritch shadows/pregens-data.json`.

The upload package includes scoped Apache/LiteSpeed 301 redirects in
`Eldritch shadows/.htaccess`. Legacy HTML pages also contain static redirects
with a visible fallback link. Their JavaScript preserves query strings and
section anchors. Keep both mechanisms when uploading; upload hidden files too.
