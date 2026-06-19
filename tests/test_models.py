import unittest

from lotto_analyzer.models import LottoDraw


class LottoDrawTest(unittest.TestCase):
    def test_sorts_and_validates_numbers(self):
        draw = LottoDraw(draw_no=1, date="2024-01-01", numbers=(6, 1, 5, 2, 4, 3), bonus=7)

        self.assertEqual(draw.numbers, (1, 2, 3, 4, 5, 6))

    def test_rejects_duplicate_main_numbers(self):
        with self.assertRaises(ValueError):
            LottoDraw(draw_no=1, date=None, numbers=(1, 1, 2, 3, 4, 5), bonus=6)

    def test_rejects_bonus_duplicate(self):
        with self.assertRaises(ValueError):
            LottoDraw(draw_no=1, date=None, numbers=(1, 2, 3, 4, 5, 6), bonus=6)


if __name__ == "__main__":
    unittest.main()
