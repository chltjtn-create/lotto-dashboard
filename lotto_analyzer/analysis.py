from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from .models import MAX_NUMBER, MIN_NUMBER, LottoDraw


@dataclass(frozen=True)
class AnalysisResult:
    draw_count: int
    first_draw: int | None
    last_draw: int | None
    number_frequency: Counter[int]
    bonus_frequency: Counter[int]
    pair_frequency: Counter[tuple[int, int]]
    overdue: dict[int, int]
    odd_even: Counter[tuple[int, int]]


def analyze(draws: list[LottoDraw]) -> AnalysisResult:
    ordered = sorted(draws, key=lambda draw: draw.draw_no)
    number_frequency: Counter[int] = Counter()
    bonus_frequency: Counter[int] = Counter()
    pair_frequency: Counter[tuple[int, int]] = Counter()
    odd_even: Counter[tuple[int, int]] = Counter()

    for draw in ordered:
        number_frequency.update(draw.numbers)
        if draw.bonus is not None:
            bonus_frequency.update([draw.bonus])
        pair_frequency.update(tuple(pair) for pair in combinations(draw.numbers, 2))
        odd_count = sum(1 for number in draw.numbers if number % 2)
        odd_even.update([(odd_count, len(draw.numbers) - odd_count)])

    return AnalysisResult(
        draw_count=len(ordered),
        first_draw=ordered[0].draw_no if ordered else None,
        last_draw=ordered[-1].draw_no if ordered else None,
        number_frequency=number_frequency,
        bonus_frequency=bonus_frequency,
        pair_frequency=pair_frequency,
        overdue=_overdue_by_draw_count(ordered),
        odd_even=odd_even,
    )


def _overdue_by_draw_count(ordered: list[LottoDraw]) -> dict[int, int]:
    last_seen_index: dict[int, int] = {}
    for index, draw in enumerate(ordered):
        for number in draw.numbers:
            last_seen_index[number] = index

    total = len(ordered)
    overdue: dict[int, int] = {}
    for number in range(MIN_NUMBER, MAX_NUMBER + 1):
        if number not in last_seen_index:
            overdue[number] = total
        else:
            overdue[number] = total - last_seen_index[number] - 1
    return overdue


def top_items(counter: Counter, limit: int) -> list[tuple[object, int]]:
    return counter.most_common(limit)


def top_overdue(overdue: dict[int, int], limit: int) -> list[tuple[int, int]]:
    return sorted(overdue.items(), key=lambda item: (-item[1], item[0]))[:limit]
