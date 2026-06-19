import unittest

from lotto_analyzer.generator import generate_combinations
from lotto_analyzer.models import LottoDraw


class GeneratorTest(unittest.TestCase):
    def test_generates_valid_deterministic_combinations(self):
        draws = [
            LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7),
            LottoDraw(2, "2024-01-08", (8, 9, 10, 11, 12, 13), 14),
        ]

        first = generate_combinations(draws, count=3, seed=123)
        second = generate_combinations(draws, count=3, seed=123)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 3)
        self.assertTrue(all(len(combo) == 6 for combo in first))
        self.assertTrue(all(len(set(combo)) == 6 for combo in first))
        self.assertNotIn((1, 2, 3, 4, 5, 6), first)


if __name__ == "__main__":
    unittest.main()
