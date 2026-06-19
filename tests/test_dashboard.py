import json
import tempfile
import unittest
from pathlib import Path

from lotto_analyzer.dashboard import build_dashboard_payload, render_dashboard, write_dashboard
from lotto_analyzer.models import LottoDraw
from lotto_analyzer.recommendation import recommend_numbers


class DashboardTest(unittest.TestCase):
    def test_writes_static_dashboard_files(self):
        draws = [LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7)]
        payload = build_dashboard_payload(draws, recommend_numbers(draws, count=2, seed=1, candidate_pool=100))

        with tempfile.TemporaryDirectory() as tmp:
            write_dashboard(tmp, payload, draws)

            self.assertTrue((Path(tmp) / "index.html").exists())
            latest = json.loads((Path(tmp) / "data" / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest["draw_count"], 1)
            self.assertTrue((Path(tmp) / "data" / "draws.csv").exists())

    def test_embeds_json_without_html_entity_corruption(self):
        html = render_dashboard({"generated_at": "2024-01-01", "recommendations": [], "top_numbers": [], "overdue_numbers": [], "top_pairs": []})

        self.assertIn('"generated_at": "2024-01-01"', html)
        self.assertNotIn("&quot;", html)


if __name__ == "__main__":
    unittest.main()
