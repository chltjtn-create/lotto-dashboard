import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lotto_analyzer.pipeline import run_weekly_update


class PipelineTest(unittest.TestCase):
    def test_builds_site_without_network_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = run_weekly_update(
                db_path=root / "lotto.db",
                site_dir=root / "site",
                recommendation_count=10,
                seed=1,
                sync=False,
            )

            self.assertEqual(payload["draw_count"], 0)
            self.assertEqual(len(payload["recommendations"]), 10)
            latest = json.loads((root / "site" / "data" / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(latest["recommendations"]), 10)

    def test_builds_site_when_sync_fails_non_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("lotto_analyzer.pipeline.discover_latest_draw_no", side_effect=RuntimeError("blocked")):
                payload = run_weekly_update(
                    db_path=root / "lotto.db",
                    site_dir=root / "site",
                    recommendation_count=3,
                    seed=1,
                    sync=True,
                    strict_fetch=False,
                )

            self.assertFalse(payload["fetch_status"]["ok"])
            self.assertTrue((root / "site" / "index.html").exists())

    def test_sync_failure_raises_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("lotto_analyzer.pipeline.discover_latest_draw_no", side_effect=RuntimeError("blocked")):
                with self.assertRaises(RuntimeError):
                    run_weekly_update(
                        db_path=root / "lotto.db",
                        site_dir=root / "site",
                        sync=True,
                        strict_fetch=True,
                    )


if __name__ == "__main__":
    unittest.main()
