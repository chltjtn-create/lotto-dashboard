# Deployment

Goal: publish the generated dashboard for free with GitHub Actions and GitHub Pages.

## 1. Push This Repository

Create a GitHub repository and push this folder.

```powershell
.\scripts\publish-github.ps1 -RepoUrl "https://github.com/<owner>/<repo>.git"
```

## 2. GitHub Pages

The workflow deploys the `docs/` folder to the `gh-pages` branch.

If GitHub asks for a Pages source, use:

1. Open the repository settings.
2. Go to Pages.
3. Set source to "Deploy from a branch".
4. Select branch `gh-pages`.
5. Select folder `/`.
6. Save.

GitHub will show the public dashboard URL after the first Pages deployment.

## 3. Weekly Update

The workflow in `.github/workflows/weekly-update.yml` runs on push, manual dispatch, and every Monday 00:10 KST.

It does this:

1. Runs tests.
2. Fetches missing draw numbers on schedule/manual runs.
3. Generates 10 recommended combinations.
4. Rebuilds `docs/index.html` and `docs/data/latest.json`.
5. Commits dashboard changes back to the repository on schedule/manual runs.
6. Deploys `docs/` to GitHub Pages.

## 4. Manual Run

In GitHub Actions, run "Weekly Lotto Dashboard" manually with `workflow_dispatch`.

Local equivalent:

```powershell
python -m lotto_analyzer update-site --db data/lotto.db --site-dir docs --count 10
```

If the official endpoint is blocked, the command still rebuilds the dashboard with existing data and writes the fetch error into `docs/data/latest.json`.

## 5. Local Preflight

If `python` is available on PATH:

```powershell
.\scripts\preflight.ps1
```

If Python is not on PATH, pass the full Python executable:

```powershell
.\scripts\preflight.ps1 -Python "C:\Path\To\python.exe"
```

## 6. Current Risk

The official dhlottery endpoint may block some environments or return HTML instead of JSON. The code includes a JSON fetcher and official-page HTML fallback parser, but the final production proof is the first successful GitHub Actions run.
