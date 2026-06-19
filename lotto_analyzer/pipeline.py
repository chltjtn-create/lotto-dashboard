from __future__ import annotations

from pathlib import Path

from .dashboard import build_dashboard_payload, write_dashboard
from .fetcher import DEFAULT_URL_TEMPLATE, FetchError, discover_latest_draw_no, fetch_range
from .recommendation import recommend_numbers
from .storage import SQLiteStore, load_csv


def run_weekly_update(
    db_path: str | Path,
    site_dir: str | Path,
    recommendation_count: int = 10,
    seed: int | None = None,
    sync: bool = True,
    bootstrap_start: int = 1,
    url_template: str = DEFAULT_URL_TEMPLATE,
    timeout: float = 10,
    delay: float = 0.0,
    strict_fetch: bool = False,
) -> dict:
    store = SQLiteStore(db_path)
    _load_existing_site_csv(store, Path(site_dir))
    fetch_status = {"ok": None, "message": "Sync skipped."}

    if sync:
        try:
            draws = store.list_draws()
            start = (draws[-1].draw_no + 1) if draws else bootstrap_start
            latest = discover_latest_draw_no(url_template=url_template, timeout=timeout)
            imported = 0
            if start <= latest:
                fetched = fetch_range(start, latest, url_template=url_template, timeout=timeout, delay=delay)
                imported = store.upsert_draws(fetched)
            fetch_status = {
                "ok": True,
                "message": f"Synced successfully. latest={latest}, imported={imported}.",
            }
        except (FetchError, RuntimeError, ValueError, KeyError) as exc:
            if strict_fetch:
                raise
            fetch_status = {"ok": False, "message": f"Sync failed; using existing data. {exc}"}

    draws = store.list_draws()
    recommendations = recommend_numbers(draws, count=recommendation_count, seed=seed)
    payload = build_dashboard_payload(draws, recommendations, fetch_status=fetch_status)
    write_dashboard(site_dir, payload, draws)
    return payload


def _load_existing_site_csv(store: SQLiteStore, site_dir: Path) -> None:
    csv_path = site_dir / "data" / "draws.csv"
    if csv_path.exists():
        store.upsert_draws(load_csv(csv_path))
