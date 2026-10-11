# Joseph Imperial — website design studies

Three complete, responsive design directions for Joseph Imperial's academic website.

- **Editorial** — warm paper, forest green, serif typography.
- **Precision** — graphite, cool blue, structured research presentation.
- **Studio** — white, cobalt, bold typography, prominent portrait.

## Preview

```powershell
python build.py
python -m http.server 8765 --directory dist
```

Open `http://localhost:8765`. All three designs include topic filters, research areas, publications, biography, media, and contact links. No installation or backend is required.

## Editing

`build.py` is the Python content and page generator. `dist/styles.css` and `dist/site.js` contain browser presentation and progressive interactions. Run the generator after editing page content. It preserves the stylesheet, JavaScript, and assets.

## Content and assets

The biography, roles, publication information, announcements, portrait, and destination links were taken from https://www.josephimperial.com/ on 11 October 2026. Publication acceptance announcements are reproduced from the owner's site. ScrapeBench has no preprint link there and is explicitly marked forthcoming. Long author lists are abbreviated; source project links carry the full author lists.

Portrait copyright remains with its owner. Instrument Serif and DM Sans are locally served Google Fonts, distributed under the SIL Open Font License. The preview does not load analytics or external scripts.

These are design previews. Search indexing is disabled. A production release should use the selected design as `index.html`, remove the concept selector and noindex metadata, and configure production metadata and the custom domain.

The existing website and domain have not been changed.
