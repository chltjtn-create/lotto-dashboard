import unittest

from lotto_analyzer.models import LottoDraw
from lotto_analyzer.recommendation import recommend_numbers


class RecommendationTest(unittest.TestCase):
    def test_recommends_ten_ranked_combinations(self):
        draws = [
            LottoDraw(1, "2024-01-01", (1, 2, 3, 4, 5, 6), 7),
            LottoDraw(2, "2024-01-08", (8, 9, 10, 11, 12, 13), 14),
            LottoDraw(3, "2024-01-15", (15, 16, 17, 18, 19, 20), 21),
        ]

        recommendations = recommend_numbers(draws, count=10, seed=7, candidate_pool=300)

        self.assertEqual(len(recommendations), 10)
        self.assertEqual([item.rank for item in recommendations], list(range(1, 11)))
        self.assertTrue(all(len(item.numbers) == 6 for item in recommendations))
        self.assertTrue(all(item.reasons for item in recommendations))
        self.assertNotIn((1, 2, 3, 4, 5, 6), [item.numbers for item in recommendations])


if __name__ == "__main__":
    unittest.main()
