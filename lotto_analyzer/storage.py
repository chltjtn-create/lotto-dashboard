from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import LottoDraw


CSV_FIELDS = ["draw_no", "date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"]


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        conn = self.connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS draws (
                    draw_no INTEGER PRIMARY KEY,
                    draw_date TEXT,
                    n1 INTEGER NOT NULL,
                    n2 INTEGER NOT NULL,
                    n3 INTEGER NOT NULL,
                    n4 INTEGER NOT NULL,
                    n5 INTEGER NOT NULL,
                    n6 INTEGER NOT NULL,
                    bonus INTEGER,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def upsert_draws(self, draws: Iterable[LottoDraw]) -> int:
        self.init_schema()
        rows = [
            (
                draw.draw_no,
                draw.date,
                *draw.numbers,
                draw.bonus,
            )
            for draw in draws
        ]
        if not rows:
            return 0
        conn = self.connect()
        try:
            conn.executemany(
                """
                INSERT INTO draws (draw_no, draw_date, n1, n2, n3, n4, n5, n6, bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(draw_no) DO UPDATE SET
                    draw_date = excluded.draw_date,
                    n1 = excluded.n1,
                    n2 = excluded.n2,
                    n3 = excluded.n3,
                    n4 = excluded.n4,
                    n5 = excluded.n5,
                    n6 = excluded.n6,
                    bonus = excluded.bonus,
                    updated_at = CURRENT_TIMESTAMP
                """,
                rows,
            )
            conn.commit()
        finally:
            conn.close()
        return len(rows)

    def list_draws(self) -> list[LottoDraw]:
        self.init_schema()
        conn = self.connect()
        try:
            rows = conn.execute(
                """
                SELECT draw_no, draw_date, n1, n2, n3, n4, n5, n6, bonus
                FROM draws
                ORDER BY draw_no ASC
                """
            ).fetchall()
        finally:
            conn.close()
        return [
            LottoDraw(
                draw_no=row["draw_no"],
                date=row["draw_date"],
                numbers=(row["n1"], row["n2"], row["n3"], row["n4"], row["n5"], row["n6"]),
                bonus=row["bonus"],
            )
            for row in rows
        ]


def load_csv(path: str | Path) -> list[LottoDraw]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        return [LottoDraw.from_csv_row(row) for row in reader]


def save_csv(path: str | Path, draws: Iterable[LottoDraw]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(draws)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for draw in rows:
            writer.writerow(draw.to_csv_row())
    return len(rows)
