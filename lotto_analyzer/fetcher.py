from __future__ import annotations

import json
import re
import time
from datetime import date
from json import JSONDecodeError
from typing import Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import LottoDraw


DEFAULT_URL_TEMPLATE = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
DEFAULT_PAGE_URL_TEMPLATE = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={draw_no}"
FIRST_DRAW_DATE = date(2002, 12, 7)


class FetchError(RuntimeError):
    pass


class NonJsonResponseError(FetchError):
    pass


class HtmlParseError(FetchError):
    pass


def fetch_draw(draw_no: int, url_template: str = DEFAULT_URL_TEMPLATE, timeout: float = 10) -> LottoDraw:
    try:
        return fetch_draw_json(draw_no, url_template=url_template, timeout=timeout)
    except NonJsonResponseError:
        if url_template != DEFAULT_URL_TEMPLATE:
            raise
        return fetch_draw_page(draw_no, timeout=timeout)


def fetch_draw_json(draw_no: int, url_template: str = DEFAULT_URL_TEMPLATE, timeout: float = 10) -> LottoDraw:
    url = url_template.format(draw_no=draw_no)
    body = _read_url(url, timeout=timeout, accept="application/json,text/plain,*/*")
    try:
        payload = json.loads(body)
    except JSONDecodeError as exc:
        preview = body[:120].replace("\n", " ").strip()
        raise NonJsonResponseError(f"draw {draw_no} response was not JSON: {preview}") from exc
    return LottoDraw.from_api_payload(payload)


def fetch_draw_page(draw_no: int, url_template: str = DEFAULT_PAGE_URL_TEMPLATE, timeout: float = 10) -> LottoDraw:
    url = url_template.format(draw_no=draw_no)
    body = _read_url(url, timeout=timeout, accept="text/html,*/*")
    return parse_draw_page(body, expected_draw_no=draw_no)


def parse_draw_page(html_body: str, expected_draw_no: int | None = None) -> LottoDraw:
    text = re.sub(r"\s+", " ", html_body)
    content_match = re.search(r'content=["\'][^"\']*?(\d+)회\s*당첨번호\s*([0-9,\s]+)\+([0-9]+)', text)
    if content_match:
        draw_no = int(content_match.group(1))
        numbers = tuple(int(value.strip()) for value in content_match.group(2).split(",") if value.strip())
        bonus = int(content_match.group(3))
    else:
        draw_match = re.search(r"(\d+)회\s*당첨결과", text)
        spans = [int(value) for value in re.findall(r'ball_645[^>]*>\s*([0-9]{1,2})\s*<', text)]
        if not draw_match or len(spans) < 7:
            preview = text[:160].strip()
            raise HtmlParseError(f"could not parse draw page: {preview}")
        draw_no = int(draw_match.group(1))
        numbers = tuple(spans[:6])
        bonus = spans[6]

    if expected_draw_no is not None and draw_no != expected_draw_no:
        raise HtmlParseError(f"expected draw {expected_draw_no}, got {draw_no}")

    date_match = re.search(r"\((\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*추첨\)", text)
    draw_date = None
    if date_match:
        draw_date = f"{int(date_match.group(1)):04d}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"

    return LottoDraw(draw_no=draw_no, date=draw_date, numbers=numbers, bonus=bonus)


def _read_url(url: str, timeout: float, accept: str) -> str:
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 lotto-analyzer/0.1",
                "Accept": accept,
            },
        )
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise FetchError(f"failed to fetch {url}: {exc.__class__.__name__}") from exc


def fetch_range(
    start: int,
    end: int,
    url_template: str = DEFAULT_URL_TEMPLATE,
    timeout: float = 10,
    delay: float = 0.0,
) -> Iterator[LottoDraw]:
    if start <= 0 or end < start:
        raise ValueError("expected 0 < start <= end")
    for draw_no in range(start, end + 1):
        yield fetch_draw(draw_no, url_template=url_template, timeout=timeout)
        if delay > 0 and draw_no < end:
            time.sleep(delay)


def estimate_latest_draw_no(today: date | None = None) -> int:
    today = today or date.today()
    if today < FIRST_DRAW_DATE:
        return 0
    return ((today - FIRST_DRAW_DATE).days // 7) + 1


def discover_latest_draw_no(
    url_template: str = DEFAULT_URL_TEMPLATE,
    timeout: float = 10,
    today: date | None = None,
    probe_window: int = 8,
) -> int:
    estimate = estimate_latest_draw_no(today)
    start = max(1, estimate + probe_window)
    stop = max(1, estimate - probe_window)
    last_error: Exception | None = None
    for draw_no in range(start, stop - 1, -1):
        try:
            fetch_draw(draw_no, url_template=url_template, timeout=timeout)
        except (ValueError, KeyError, FetchError) as exc:
            last_error = exc
            continue
        return draw_no
    detail = f": {last_error}" if last_error else ""
    raise RuntimeError(f"could not discover latest draw number near estimate {estimate}{detail}")
