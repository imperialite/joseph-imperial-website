# Joseph Imperial academic website

Three restrained academic website layouts built from the existing website content.

1. Classic academic: centered profile, serif headings, chronological publications.
2. Profile sidebar: persistent identity and navigation beside the main content.
3. Publications first: compact profile followed directly by the publication list.

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

Portrait copyright remains with its owner. DM Sans is locally served under the SIL Open Font License in `dist/assets/licenses/`. Serif headings use the system Georgia font. No analytics or third-party scripts are loaded.

The pages are private design previews with search indexing disabled. A chosen production version should become `index.html`, remove the preview selector and noindex metadata, and add the final domain metadata.
