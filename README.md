# Joseph Imperial academic website

The approved Research index is the homepage. The site is generated with Python and uses no external Python packages. Website records are separate from the design.

## Update your records

1. Double-click **Edit website.cmd** in this folder. Keep its small window open.
2. Your browser opens the editor. Choose a section, then edit, add, remove, or reorder entries.
3. Click **Save changes**, then **Preview website** to check the result.
4. Click **Publish website** to save the changes to GitHub and start automatic publication. Check the completed run in GitHub Actions if the live page has not updated yet.

The editor runs only on this computer. It is never uploaded as a public administration page. Python 3.11+ is required. Saving to GitHub also requires Git and an authenticated GitHub CLI; both are configured on the current computer.

The public website runs on GitHub Pages at https://www.josephimperial.com/. The separate private Sites preview is updated through Codex.

Links in text use `[link text](https://example.com)`. Publication forms have a separate URL field. Leave that field empty for forthcoming papers. The highlight checkbox controls the dark publication card. Dates in experience, education, and awards are free text, so ranges and multiple years are supported.

The editor preserves complete author lists, existing links, and record order. Saves retain a timestamped copy of the previous records in `.editor-backups`. These local backups are excluded from Git. GitHub also retains the committed change history.

To close the editor, close its command window. Unsaved browser edits are not retained after a reload. Edit on one computer at a time; fetch newer GitHub changes before editing on a second computer.

## Launch at josephimperial.com

GitHub Pages is active, HTTPS is enforced, and Namecheap points the domain to GitHub. The repository is public. See [LAUNCH.md](LAUNCH.md) for the setup and DNS records.

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

Portrait copyright remains with its owner. DM Sans and Source Serif 4 are locally served under the SIL Open Font License, included in `dist/assets/licenses/`. Google Analytics is enabled on the public homepage when a Measurement ID is configured. Private builds and archived design previews do not load it. Previous design previews remain available at `design-options.html` and retain noindex metadata.

## Google Analytics

In the editor, open **Profile → Google Analytics Measurement ID**. Enter the G- ID, then **Publish website**. Leave the field blank to turn tracking off. The ID is a public tag identifier and is stored with the website records.

The configured public homepage loads the Google tag in the background. There is no visitor consent control or visual layout change. Google advertising signals and ad personalization signals are disabled in this tag. Page URLs and referrers passed by this loader omit query strings and fragments.

To verify collection, open the live homepage and check the matching property's **Realtime** report in Google Analytics. Browser tracking protection and ad blockers may prevent collection. Local editor previews and private Sites builds remain untracked.

[Find your Measurement ID](https://support.google.com/analytics/answer/9539598?hl=en) · [Google tag setup and verification](https://developers.google.com/tag-platform/gtagjs)
