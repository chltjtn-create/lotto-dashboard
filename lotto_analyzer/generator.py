from __future__ import annotations

import random
from collections import Counter
from typing import Iterable

from .analysis import analyze
from .models import MAX_NUMBER, MIN_NUMBER, LottoDraw


def generate_combinations(
    draws: list[LottoDraw],
    count: int,
    seed: int | None = None,
    exclude_previous: bool = True,
) -> list[tuple[int, ...]]:
    if count <= 0:
        raise ValueError("count must be positive")

    rng = random.Random(seed)
    analysis = analyze(draws)
    weights = _weights(analysis.number_frequency, analysis.overdue, max(1, analysis.draw_count))
    previous = {draw.numbers for draw in draws} if exclude_previous else set()
    generated: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()

    attempts = 0
    max_attempts = max(1000, count * 500)
    while len(generated) < count and attempts < max_attempts:
        attempts += 1
        combo = tuple(sorted(_weighted_sample(range(MIN_NUMBER, MAX_NUMBER + 1), weights, 6, rng)))
        if combo in seen or combo in previous:
            continue
        if not _looks_balanced(combo):
            continue
        seen.add(combo)
        generated.append(combo)

    while len(generated) < count:
        combo = tuple(sorted(rng.sample(range(MIN_NUMBER, MAX_NUMBER + 1), 6)))
        if combo in seen or combo in previous:
            continue
        seen.add(combo)
        generated.append(combo)

    return generated


def _weights(frequency: Counter[int], overdue: dict[int, int], draw_count: int) -> dict[int, float]:
    max_frequency = max(frequency.values(), default=0) or 1
    max_overdue = max(overdue.values(), default=0) or 1
    weights: dict[int, float] = {}
    for number in range(MIN_NUMBER, MAX_NUMBER + 1):
        freq_score = frequency.get(number, 0) / max_frequency
        overdue_score = overdue.get(number, draw_count) / max_overdue
        weights[number] = 1.0 + (0.55 * freq_score) + (0.45 * overdue_score)
    return weights


def _weighted_sample(
    numbers: Iterable[int],
    weights: dict[int, float],
    size: int,
    rng: random.Random,
) -> list[int]:
    pool = list(numbers)
    picked: list[int] = []
    for _ in range(size):
        total = sum(weights[number] for number in pool)
        point = rng.uniform(0, total)
        upto = 0.0
        for index, number in enumerate(pool):
            upto += weights[number]
            if upto >= point:
                picked.append(number)
                del pool[index]
                break
    return picked


def _looks_balanced(combo: tuple[int, ...]) -> bool:
    odd_count = sum(1 for number in combo if number % 2)
    total = sum(combo)
    tens_bucket_count = len({number // 10 for number in combo})
    return 2 <= odd_count <= 4 and 90 <= total <= 200 and tens_bucket_count >= 3
