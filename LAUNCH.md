# Launch guide

Status on 12 October 2026: the selected design and editor are prepared. The GitHub repository is private, GitHub Pages is not active, and the Namecheap records still serve the original Google Sites website.

## 1. Choose repository visibility

GitHub Pages is available for public repositories on GitHub Free, and private repositories on GitHub Pro, Team, and Enterprise. Your account plan could not be verified through the connected API.

The free route is to make only `imperialite/joseph-imperial-website` public. Its content and source history would become readable by anyone. Keep it private if you prefer, and use an eligible GitHub plan or a separate hosting service. Do not change visibility until that choice is approved.

## 2. Activate and verify hosting

In the [repository Pages settings](https://github.com/imperialite/joseph-imperial-website/settings/pages), choose **GitHub Actions** as the publishing source.

In **Settings → Secrets and variables → Actions → Variables**, add repository variable `PAGES_ENABLED` with value `true`. This is a public configuration flag, not a secret. In **Actions → Publish academic website**, run the workflow. Verify the completed deployment at the GitHub-provided URL before changing the domain.

The local editor will then offer **Publish website**. It saves your records to GitHub; the workflow builds and deploys them. Check [Actions](https://github.com/imperialite/joseph-imperial-website/actions) for publication success. A successful GitHub push starts publication; it does not by itself prove deployment succeeded.

## 3. Connect your Namecheap domain

Once the GitHub-hosted website has been checked, add **www.josephimperial.com** in the repository Pages custom-domain setting. In GitHub account **Settings → Pages**, verify domain ownership using the exact TXT record that GitHub provides. Keep that verification record.

In Namecheap, open **Domain List → josephimperial.com → Manage → Advanced DNS → Host records**. Save a copy of the existing records before changing them.

Set the website records to:

| Type | Host | Value | TTL |
| --- | --- | --- | --- |
| A | @ | 185.199.108.153 | Automatic |
| A | @ | 185.199.109.153 | Automatic |
| A | @ | 185.199.110.153 | Automatic |
| A | @ | 185.199.111.153 | Automatic |
| CNAME | www | imperialite.github.io | Automatic |

Replace website records that conflict at `@` and `www`. Leave mail records and unrelated TXT/subdomain records intact. On 12 October 2026, public DNS showed `www` pointing to `ghs.googlehosted.com`, an apex address of `162.255.119.193`, and Namecheap nameservers `dns1.registrar-servers.com` / `dns2.registrar-servers.com`. The apex address may be produced by a Namecheap URL Redirect record; inspect the actual dashboard record before replacing it.

Wait for GitHub's DNS check and certificate to complete, then enable **Enforce HTTPS**. Verify both `https://josephimperial.com` and `https://www.josephimperial.com`, including the portrait, CV, publications, and mobile layout. Keep the original Google Site available until this is complete. DNS propagation timing varies.

## Sources

- [GitHub Pages availability and custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Namecheap instructions for GitHub Pages](https://www.namecheap.com/support/knowledgebase/article.aspx/9645/2208/how-do-i-link-my-domain-to-github-pages/)
- [GitHub custom-domain setup](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
