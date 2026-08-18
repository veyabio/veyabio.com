# VeyaBio website

A Jekyll website for `veyabio.com`, built around the official VeyaBio brand system.

For collaborators using Claude or GitHub Copilot, see the [website editing guide](.github/EDITING_GUIDE.md).

## Fast local preview (no downloads)

From the repository folder:

```powershell
python scripts/build_local_preview.py
python -m http.server 4000 --directory _site
```

Open `http://localhost:4000`. The local builder uses only Python's standard library and does not install Ruby packages or access the network.

## GitHub Pages deployment

The repository includes a GitHub Actions workflow at `.github/workflows/jekyll.yml`. Upload the contents of this package to the root of `veyabio/veyabio.com`, push to `main`, then set **Settings > Pages > Source** to **GitHub Actions**.

The included `CNAME` file configures the site for `veyabio.com`. After GitHub Pages has deployed successfully, configure the domain's DNS records using the values shown by GitHub Pages.

## Before launch

1. Confirm that `hello@veyabio.com` is the correct public contact address.
2. Confirm permission to name DITEC and Dikoda Ltd publicly.
3. Add verified project outcomes and client quotes when available.
4. Enable **Enforce HTTPS** in the repository's Pages settings after the custom domain resolves.

## Brand system

- Merriweather: primary editorial typeface
- Darker Grotesque: supporting and interface typeface
- Obsidian Black: `#0D1B2A`
- Dark Denim: `#415A77`
- Aqua Teal: `#40B5AD`
- Bone White: `#F5F5DC`

The original brand, logo, and content reference PDFs are intentionally excluded from the deployable website package.