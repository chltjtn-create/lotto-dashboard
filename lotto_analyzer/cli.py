from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze, top_items, top_overdue
from .fetcher import DEFAULT_URL_TEMPLATE, fetch_range
from .generator import generate_combinations
from .pipeline import run_weekly_update
from .storage import SQLiteStore, load_csv, save_csv


DEFAULT_DB = Path("data/lotto.db")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lotto-analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_csv = subparsers.add_parser("import-csv", help="import draw CSV into SQLite")
    import_csv.add_argument("csv_path")
    import_csv.add_argument("--db", default=DEFAULT_DB)
    import_csv.set_defaults(handler=handle_import_csv)

    fetch = subparsers.add_parser("fetch", help="fetch draw range into SQLite")
    fetch.add_argument("--start", type=int, required=True)
    fetch.add_argument("--end", type=int, required=True)
    fetch.add_argument("--db", default=DEFAULT_DB)
    fetch.add_argument("--url-template", default=DEFAULT_URL_TEMPLATE)
    fetch.add_argument("--timeout", type=float, default=10.0)
    fetch.add_argument("--delay", type=float, default=0.0)
    fetch.set_defaults(handler=handle_fetch)

    stats = subparsers.add_parser("stats", help="print draw statistics")
    stats.add_argument("--db", default=DEFAULT_DB)
    stats.add_argument("--top", type=int, default=10)
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(handler=handle_stats)

    generate = subparsers.add_parser("generate", help="generate number combinations")
    generate.add_argument("--db", default=DEFAULT_DB)
    generate.add_argument("--count", type=int, default=5)
    generate.add_argument("--seed", type=int)
    generate.add_argument("--allow-previous", action="store_true")
    generate.add_argument("--json", action="store_true")
    generate.set_defaults(handler=handle_generate)

    export = subparsers.add_parser("export-csv", help="export SQLite draws to CSV")
    export.add_argument("csv_path")
    export.add_argument("--db", default=DEFAULT_DB)
    export.set_defaults(handler=handle_export_csv)

    update_site = subparsers.add_parser("update-site", help="sync draws and build the static dashboard")
    update_site.add_argument("--db", default=DEFAULT_DB)
    update_site.add_argument("--site-dir", default="docs")
    update_site.add_argument("--count", type=int, default=10)
    update_site.add_argument("--seed", type=int)
    update_site.add_argument("--no-sync", action="store_true")
    update_site.add_argument("--bootstrap-start", type=int, default=1)
    update_site.add_argument("--url-template", default=DEFAULT_URL_TEMPLATE)
    update_site.add_argument("--timeout", type=float, default=10.0)
    update_site.add_argument("--delay", type=float, default=0.0)
    update_site.add_argument("--strict-fetch", action="store_true")
    update_site.set_defaults(handler=handle_update_site)

    return parser


def handle_import_csv(args: argparse.Namespace) -> int:
    draws = load_csv(args.csv_path)
    count = SQLiteStore(args.db).upsert_draws(draws)
    print(f"Imported {count} draws into {args.db}")
    return 0


def handle_fetch(args: argparse.Namespace) -> int:
    draws = list(
        fetch_range(
            args.start,
            args.end,
            url_template=args.url_template,
            timeout=args.timeout,
            delay=args.delay,
        )
    )
    count = SQLiteStore(args.db).upsert_draws(draws)
    print(f"Fetched and saved {count} draws into {args.db}")
    return 0


def handle_stats(args: argparse.Namespace) -> int:
    draws = SQLiteStore(args.db).list_draws()
    result = analyze(draws)
    if args.json:
        print(json.dumps(_analysis_to_json(result, args.top), ensure_ascii=False, indent=2))
        return 0

    print(f"Draws: {result.draw_count}")
    print(f"Range: {result.first_draw or '-'} to {result.last_draw or '-'}")
    print("Top numbers:")
    for number, hits in top_items(result.number_frequency, args.top):
        print(f"  {number:2}: {hits}")
    print("Most overdue:")
    for number, misses in top_overdue(result.overdue, args.top):
        print(f"  {number:2}: {misses} draws")
    print("Top pairs:")
    for pair, hits in top_items(result.pair_frequency, min(args.top, 10)):
        print(f"  {pair[0]:2}-{pair[1]:2}: {hits}")
    return 0


def handle_generate(args: argparse.Namespace) -> int:
    draws = SQLiteStore(args.db).list_draws()
    combos = generate_combinations(
        draws,
        count=args.count,
        seed=args.seed,
        exclude_previous=not args.allow_previous,
    )
    if args.json:
        print(json.dumps({"combinations": combos}, ensure_ascii=False, indent=2))
        return 0
    for combo in combos:
        print(" ".join(f"{number:02}" for number in combo))
    return 0


def handle_export_csv(args: argparse.Namespace) -> int:
    draws = SQLiteStore(args.db).list_draws()
    count = save_csv(args.csv_path, draws)
    print(f"Exported {count} draws to {args.csv_path}")
    return 0


def handle_update_site(args: argparse.Namespace) -> int:
    payload = run_weekly_update(
        db_path=args.db,
        site_dir=args.site_dir,
        recommendation_count=args.count,
        seed=args.seed,
        sync=not args.no_sync,
        bootstrap_start=args.bootstrap_start,
        url_template=args.url_template,
        timeout=args.timeout,
        delay=args.delay,
        strict_fetch=args.strict_fetch,
    )
    print(
        "Updated dashboard: "
        f"{args.site_dir} "
        f"(draws={payload['draw_count']}, latest={payload['last_draw']}, "
        f"recommendations={len(payload['recommendations'])})"
    )
    return 0


def _analysis_to_json(result, top: int) -> dict[str, object]:
    return {
        "draw_count": result.draw_count,
        "first_draw": result.first_draw,
        "last_draw": result.last_draw,
        "top_numbers": top_items(result.number_frequency, top),
        "most_overdue": top_overdue(result.overdue, top),
        "top_pairs": [[list(pair), hits] for pair, hits in top_items(result.pair_frequency, min(top, 10))],
    }
