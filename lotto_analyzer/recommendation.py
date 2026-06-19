from __future__ import annotations

import random
from dataclasses import dataclass

from .analysis import analyze
from .models import MAX_NUMBER, MIN_NUMBER, LottoDraw


@dataclass(frozen=True)
class Recommendation:
    rank: int
    numbers: tuple[int, ...]
    score: float
    reasons: tuple[str, ...]


def recommend_numbers(
    draws: list[LottoDraw],
    count: int = 10,
    seed: int | None = None,
    candidate_pool: int = 3500,
) -> list[Recommendation]:
    if count <= 0:
        raise ValueError("count must be positive")
    if not draws:
        return _random_recommendations(count=count, seed=seed)

    rng = random.Random(seed)
    result = analyze(draws)
    previous = {draw.numbers for draw in draws}
    candidates: dict[tuple[int, ...], float] = {}

    attempts = 0
    max_attempts = candidate_pool * 4
    while len(candidates) < candidate_pool and attempts < max_attempts:
        attempts += 1
        combo = tuple(sorted(rng.sample(range(MIN_NUMBER, MAX_NUMBER + 1), 6)))
        if combo in previous:
            continue
        score = _score_combo(combo, result.number_frequency, result.overdue, result.draw_count)
        if score <= 0:
            continue
        candidates[combo] = max(score, candidates.get(combo, 0))

    ranked = sorted(candidates.items(), key=lambda item: (-item[1], item[0]))[:count]
    return [
        Recommendation(
            rank=index + 1,
            numbers=combo,
            score=round(score, 4),
            reasons=_reasons(combo, result.number_frequency, result.overdue),
        )
        for index, (combo, score) in enumerate(ranked)
    ]


def _random_recommendations(count: int, seed: int | None) -> list[Recommendation]:
    rng = random.Random(seed)
    seen: set[tuple[int, ...]] = set()
    recommendations: list[Recommendation] = []
    while len(recommendations) < count:
        combo = tuple(sorted(rng.sample(range(MIN_NUMBER, MAX_NUMBER + 1), 6)))
        if combo in seen:
            continue
        seen.add(combo)
        recommendations.append(
            Recommendation(
                rank=len(recommendations) + 1,
                numbers=combo,
                score=0.0,
                reasons=("No history loaded; random balanced fallback.",),
            )
        )
    return recommendations


def _score_combo(combo: tuple[int, ...], frequency, overdue: dict[int, int], draw_count: int) -> float:
    odd_count = sum(1 for number in combo if number % 2)
    total = sum(combo)
    low_count = sum(1 for number in combo if number <= 22)
    consecutive_pairs = sum(1 for left, right in zip(combo, combo[1:]) if right - left == 1)
    buckets = len({(number - 1) // 10 for number in combo})

    if odd_count not in {2, 3, 4}:
        return 0
    if not 95 <= total <= 185:
        return 0
    if low_count not in {2, 3, 4}:
        return 0
    if consecutive_pairs > 1:
        return 0
    if buckets < 3:
        return 0

    max_freq = max(frequency.values(), default=1) or 1
    max_overdue = max(overdue.values(), default=max(1, draw_count)) or 1
    freq_score = sum(frequency.get(number, 0) / max_freq for number in combo) / 6
    overdue_score = sum(overdue.get(number, draw_count) / max_overdue for number in combo) / 6
    shape_score = 1.0
    shape_score += 0.12 if odd_count == 3 else 0.06
    shape_score += 0.08 if low_count == 3 else 0.04
    shape_score += 0.05 if consecutive_pairs == 1 else 0.03
    shape_score += min(0.1, buckets * 0.02)
    return (0.42 * freq_score) + (0.33 * overdue_score) + (0.25 * shape_score)


def _reasons(combo: tuple[int, ...], frequency, overdue: dict[int, int]) -> tuple[str, ...]:
    hot = sorted(combo, key=lambda number: (-frequency.get(number, 0), number))[:2]
    due = sorted(combo, key=lambda number: (-overdue.get(number, 0), number))[:2]
    odd_count = sum(1 for number in combo if number % 2)
    return (
        f"Hot numbers in combo: {', '.join(str(number) for number in hot)}",
        f"Overdue numbers in combo: {', '.join(str(number) for number in due)}",
        f"Balance: odd {odd_count}, even {6 - odd_count}, sum {sum(combo)}",
    )
