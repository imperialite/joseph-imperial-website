# Joseph Imperial academic website

The approved Research index is the homepage. The site is generated with Python and uses no external Python packages. Website records are separate from the design.

## Update your records

1. Double-click **Edit website.cmd** in this folder. Keep its small window open.
2. Your browser opens the editor. Choose a section, then edit, add, remove, or reorder entries.
3. Click **Save changes**, then **Preview website** to check the result.
4. Click **Save to GitHub** to back up the changes. Once GitHub Pages is activated, this button becomes **Publish website** and starts automatic publication.

The editor runs only on this computer. It is never uploaded as a public administration page. Python 3.11+ is required. Saving to GitHub also requires Git and an authenticated GitHub CLI; both are configured on the current computer.

While public hosting is pending, Save to GitHub does not update the private Sites preview. Ask Codex to publish that preview. The editor states which publishing mode is available.

Links in text use `[link text](https://example.com)`. Publication forms have a separate URL field. Leave that field empty for forthcoming papers. The highlight checkbox controls the dark publication card. Dates in experience, education, and awards are free text, so ranges and multiple years are supported.

The editor preserves complete author lists, existing links, and record order. Saves retain a timestamped copy of the previous records in `.editor-backups`. These local backups are excluded from Git. GitHub also retains the committed change history.

To close the editor, close its command window. Unsaved browser edits are not retained after a reload. Edit on one computer at a time; fetch newer GitHub changes before editing on a second computer.

## Launch at josephimperial.com

The prepared route is GitHub Pages hosting with the existing domain registered at Namecheap. See [LAUNCH.md](LAUNCH.md) for the exact setup and DNS records. GitHub Pages and the domain cutover are not enabled yet. The repository remains private pending the hosting decision.

## Project files

- `content.json` contains your profile, biography, news, experience, education, awards, media entries, and social links.
- `publications.json` contains complete publication records and the featured flag.
- `build.py` generates the website. `python build.py` builds a private preview; `python build.py --public` makes the homepage indexable.
- `edit.py` and `editor/` provide the local editor.
- `dist/` contains the deployable website and its fonts, portrait, and styles.
- `.github/workflows/publish.yml` builds and publishes after a GitHub update once the repository variable `PAGES_ENABLED` is set to `true` and Pages is configured for GitHub Actions.

For a local command-line preview, run `python build.py`, then `python -m http.server 8765 --directory dist`. For validation, run `python -m unittest discover -s tests -v`.

## Content and design

Content, portrait, and original external links were checked against https://www.josephimperial.com/ on 12 October 2026. Publication acceptance announcements reproduce the original site. ScrapeBench currently has no preprint URL. The CV opens the original Google Drive folder.

This website's design and color palette are inspired by the [Institute for Law & AI](https://law-ai.org/) website. The fine-line motif is original vector artwork generated in Python. The reference website's logo, fonts, images, and artwork are not used.

Portrait copyright remains with its owner. DM Sans and Source Serif 4 are locally served under the SIL Open Font License, included in `dist/assets/licenses/`. The site loads no analytics or third-party scripts. Previous design previews remain available at `design-options.html` and retain noindex metadata.
