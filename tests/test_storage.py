import tempfile
import unittest
from pathlib import Path

from lotto_analyzer.models import LottoDraw
from lotto_analyzer.storage import SQLiteStore, load_csv, save_csv


class StorageTest(unittest.TestCase):
    def test_sqlite_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "lotto.db"
            store = SQLiteStore(db_path)
            draw = LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7)

            self.assertEqual(store.upsert_draws([draw]), 1)
            self.assertEqual(store.list_draws(), [draw])

    def test_csv_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "draws.csv"
            draws = [LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7)]

            self.assertEqual(save_csv(csv_path, draws), 1)
            self.assertEqual(load_csv(csv_path), draws)


if __name__ == "__main__":
    unittest.main()
