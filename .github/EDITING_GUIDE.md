# Editing the VeyaBio website with Claude or GitHub Copilot

This repository contains the public website at **[veyabio.com](https://veyabio.com)**. It is a Jekyll site: changes merged into `main` are built and published automatically by GitHub Actions. Editors should work on a branch and use a pull request so another person can review the result before it goes live.

## Access and the normal workflow

An editor needs a GitHub account with **write access** to `veyabio/veyabio.com`. Never share GitHub, Claude, or Copilot passwords or authentication codes.

1. Describe the requested change in a GitHub issue or a short written brief.
2. Ask Claude or Copilot to make the change on a new branch—not directly on `main`.
3. Preview the site and review the changed files.
4. Open a pull request and have another person approve it.
5. Merge the pull request. GitHub Actions will publish the new version automatically.

## Option A: Claude

The standard Claude.ai GitHub connection gives Claude repository context, but it does not by itself provide a complete write-and-publish workflow. To make changes, use either Claude Code locally or the Claude Code GitHub app/action.

### Claude Code on a computer

Clone the repository, create a branch, and start Claude Code from the repository folder:

```powershell
git clone https://github.com/veyabio/veyabio.com.git
cd veyabio.com
git switch -c edit/short-description
claude
```

Give Claude a precise request, ask it to preserve the brand system, preview the result, and then ask it to commit and push the branch. Open the pull-request link it provides and review before merging.

### Claude through GitHub

A repository administrator can install the official Claude GitHub app and Claude Code action. Once configured, an authorised contributor can write `@claude` in an issue or pull-request comment. Claude works on a branch and proposes changes for human review. This setup requires separate Claude authentication and repository administration; simply adding the repository to a Claude chat is not enough.

## Option B: GitHub Copilot cloud agent

If someone refers to Copilot Workspace, the current GitHub workflow to use here is the **Copilot cloud agent**.

1. Open the repository on GitHub and create an issue describing the change and acceptance criteria.
2. Assign the issue to **Copilot**, or start the task from the repository's **Agents** tab.
3. Copilot creates a draft pull request and updates it as it works.
4. Review **Files changed**, request corrections in PR comments if needed, and merge only when satisfied.

Copilot can also be used from VS Code after cloning the repository. In Agent mode, ask it to create a branch, make the edit, run the preview, and prepare a pull request.

## Where website content lives

| Change | File or folder |
|---|---|
| Homepage | `index.html` |
| Services page and service list | `services/index.html`, `_data/services.yml` |
| Work/case studies | `work/index.html` |
| Contact page | `contact/index.html` |
| Blog listing and articles | `blog/index.html`, `_posts/` |
| Navigation | `_data/navigation.yml` |
| Shared header, footer and CTA | `_includes/` |
| Brand styling | `assets/css/style.css` |
| Images, logo and fonts | `assets/images/`, `assets/fonts/` |

Do not edit `CNAME`, the domain settings in `_config.yml`, or `.github/workflows/jekyll.yml` unless the task specifically concerns hosting. Do not upload secrets, customer-confidential information, or source brand/reference files.

## Preview and review

From the repository folder, build the local preview:

```powershell
python scripts/build_local_preview.py
python -m http.server 4000 --directory _site
```

Open `http://localhost:4000` and check desktop and mobile layouts, navigation, spelling, links, logo, colours, Merriweather headings, and Darker Grotesque supporting text. Stop the server with `Ctrl+C`.

Suggested agent prompt:

> Update the VeyaBio website on a new branch. Change [describe the content]. Preserve the existing brand colours, Merriweather and Darker Grotesque fonts, page structure, responsive behaviour, and scientific tone. Do not modify hosting, domain, workflow, or reference files. Build the local preview, report what you changed, and prepare a pull request for human review.

After the pull request is merged, confirm that **Build and deploy Jekyll site** is green under GitHub Actions and then check the live page at `https://veyabio.com`.
