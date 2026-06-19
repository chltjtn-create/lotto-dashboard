# lotto-analyzer

Standard-library Python system for 6/45 lotto draw storage, analysis, weekly recommendations, and a static dashboard.

This project does not predict random lottery outcomes. It summarizes historical draws and creates rule-filtered combinations for review.

## Quick Start

```powershell
python -m unittest discover -s tests
python -m lotto_analyzer import-csv examples/synthetic_draws.csv --db data/lotto.db
python -m lotto_analyzer stats --db data/lotto.db
python -m lotto_analyzer generate --db data/lotto.db --count 5 --seed 42
python -m lotto_analyzer update-site --db data/lotto.db --site-dir docs --count 10 --no-sync
```

## Commands

- `import-csv <path>`: import draw data into SQLite.
- `fetch --start N --end M`: fetch draw data from a configurable JSON endpoint into SQLite.
- `stats`: print frequency, overdue numbers, and common pairs.
- `generate`: generate balanced 6-number combinations using historical frequency and overdue scores.
- `export-csv <path>`: export stored draws.
- `update-site`: sync latest draws, recommend 10 combinations, and write the static dashboard under `docs/`.

## Weekly Dashboard Goal

The repository is set up for the following free sharing flow:

1. GitHub Actions runs every Monday 00:10 KST.
2. The workflow fetches missing Lotto 6/45 draw data from the configured endpoint.
3. It builds `docs/data/latest.json`, `docs/data/draws.csv`, and `docs/index.html`.
4. GitHub Pages can serve the `docs/` folder as a free static dashboard.

Enable GitHub Pages in the repository settings and choose the `docs/` folder as the source after pushing this repo to GitHub.

Detailed deployment steps are in `DEPLOYMENT.md`.

After creating a GitHub repository, publish with:

```powershell
.\scripts\publish-github.ps1 -RepoUrl "https://github.com/<owner>/<repo>.git"
```

## CSV Format

Required headers:

```csv
draw_no,date,n1,n2,n3,n4,n5,n6,bonus
1,2024-01-01,1,2,3,4,5,6,7
```

The example file under `examples/` is synthetic test/demo data, not official draw history.

## Data Notes

The default fetch URL template is configurable:

```powershell
python -m lotto_analyzer fetch --start 1 --end 10 --db data/lotto.db --url-template "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
```

If the remote response format changes or the network is unavailable, use CSV import instead.

Current local verification note: in this Codex environment on 2026-06-19, the default endpoint returned HTML rather than JSON after network access was allowed. The fetcher now detects that and fails clearly. Re-test after pushing to GitHub because the production network path can differ.

## Research Notes

See `docs/RESEARCH.md`.

The current method is intentionally conservative: it uses frequency, overdue counts, repeated pairs, odd/even balance, low/high balance, sum range, and bucket diversity. These are transparent analysis features, not proof of future outcomes.

## Development

```powershell
python -m unittest discover -s tests
python -m lotto_analyzer --help
```
