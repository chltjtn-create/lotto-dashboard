import unittest

from lotto_analyzer.analysis import analyze, top_overdue
from lotto_analyzer.models import LottoDraw


class AnalysisTest(unittest.TestCase):
    def test_frequency_and_overdue(self):
        draws = [
            LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7),
            LottoDraw(2, "2024-01-08", (1, 8, 9, 10, 11, 12), 13),
        ]

        result = analyze(draws)

        self.assertEqual(result.draw_count, 2)
        self.assertEqual(result.number_frequency[1], 2)
        self.assertEqual(result.overdue[1], 0)
        self.assertEqual(result.overdue[2], 1)
        self.assertEqual(top_overdue(result.overdue, 1)[0], (7, 2))


if __name__ == "__main__":
    unittest.main()
