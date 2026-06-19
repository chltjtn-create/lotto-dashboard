import unittest
from datetime import date
from unittest.mock import patch

from lotto_analyzer import fetcher


class _Response:
    def __init__(self, body):
        self.body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class FetcherTest(unittest.TestCase):
    def test_estimates_latest_draw_from_first_draw_date(self):
        self.assertEqual(fetcher.estimate_latest_draw_no(date(2002, 12, 7)), 1)
        self.assertEqual(fetcher.estimate_latest_draw_no(date(2002, 12, 14)), 2)

    def test_fetch_draw_rejects_non_json_response(self):
        with patch("lotto_analyzer.fetcher.urlopen", return_value=_Response("<html></html>")):
            with self.assertRaises(fetcher.NonJsonResponseError):
                fetcher.fetch_draw_json(1)

    def test_parse_draw_page_from_meta_description(self):
        body = """
        <html>
          <meta name="description" content="동행복권 1회 당첨번호 10, 23, 29, 33, 37, 40+16.">
          <p class="desc">(2002년 12월 7일 추첨)</p>
        </html>
        """

        draw = fetcher.parse_draw_page(body, expected_draw_no=1)

        self.assertEqual(draw.draw_no, 1)
        self.assertEqual(draw.date, "2002-12-07")
        self.assertEqual(draw.numbers, (10, 23, 29, 33, 37, 40))
        self.assertEqual(draw.bonus, 16)


if __name__ == "__main__":
    unittest.main()
