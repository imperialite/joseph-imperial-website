# Joseph Imperial academic website

Three academic website layouts using a charcoal, ivory, and blue palette informed by the Institute for Law & AI website. The fine-line motif is original vector artwork generated in Python.

1. Academic folio: charcoal masthead, blue linework, ivory reading columns.
2. Research index: charcoal profile column beside a serif academic index.
3. Journal layout: ivory masthead, offset portrait, and prominent chronological publications.

## Build and preview

```powershell
python build.py
python -m http.server 8765 --directory dist
```

Open `http://localhost:8765`. Python uses only the standard library. The site is static and needs no installation or backend.

## Editing

`build.py` generates the pages. `publications.json` contains publication records. `dist/styles.css` and `dist/site.js` contain browser presentation and progressive publication search. All papers remain visible when JavaScript is disabled. Full author lists for large collaborations can be expanded within the publication entry.

The comparison page uses screenshots of the actual layouts in `dist/assets/*-preview.jpg`. Regenerate them after changing the layouts.

## Content and assets

Biography, roles, publications, announcements, portrait, and external links came from https://www.josephimperial.com/ on 11 October 2026. Publication acceptance announcements are reproduced from that site. ScrapeBench has no preprint link in the source and is marked forthcoming. The CV link opens the original Google Drive folder.

Portrait copyright remains with its owner. DM Sans and Source Serif 4 are locally served under the SIL Open Font License in `dist/assets/licenses/`. The reference's logo, font files, images, and artwork are not used. No analytics or third-party scripts are loaded.

The pages are private design previews with search indexing disabled. A chosen production version should become `index.html`, remove the preview selector and noindex metadata, and add the final domain metadata.
