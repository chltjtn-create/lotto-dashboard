from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MIN_NUMBER = 1
MAX_NUMBER = 45
DRAW_SIZE = 6


@dataclass(frozen=True)
class LottoDraw:
    draw_no: int
    date: str | None
    numbers: tuple[int, ...]
    bonus: int | None = None

    def __post_init__(self) -> None:
        draw_no = int(self.draw_no)
        numbers = tuple(sorted(int(number) for number in self.numbers))
        bonus = None if self.bonus in (None, "") else int(self.bonus)

        if draw_no <= 0:
            raise ValueError("draw_no must be positive")
        if len(numbers) != DRAW_SIZE:
            raise ValueError(f"expected {DRAW_SIZE} main numbers")
        if len(set(numbers)) != DRAW_SIZE:
            raise ValueError("main numbers must be unique")
        invalid = [number for number in numbers if number < MIN_NUMBER or number > MAX_NUMBER]
        if invalid:
            raise ValueError(f"numbers out of range {MIN_NUMBER}-{MAX_NUMBER}: {invalid}")
        if bonus is not None:
            if bonus < MIN_NUMBER or bonus > MAX_NUMBER:
                raise ValueError(f"bonus out of range {MIN_NUMBER}-{MAX_NUMBER}: {bonus}")
            if bonus in numbers:
                raise ValueError("bonus must not duplicate a main number")

        object.__setattr__(self, "draw_no", draw_no)
        object.__setattr__(self, "numbers", numbers)
        object.__setattr__(self, "bonus", bonus)

    @classmethod
    def from_csv_row(cls, row: Mapping[str, str]) -> "LottoDraw":
        normalized = {key.strip().lower(): value for key, value in row.items()}
        return cls(
            draw_no=_value(normalized, "draw_no", "drwno", "round"),
            date=_optional_value(normalized, "date", "draw_date", "drwnodate"),
            numbers=tuple(int(_value(normalized, f"n{i}", f"drwtno{i}", f"num{i}")) for i in range(1, 7)),
            bonus=int(_value(normalized, "bonus", "bnusno")),
        )

    @classmethod
    def from_api_payload(cls, payload: Mapping[str, object]) -> "LottoDraw":
        return_value = str(payload.get("returnValue", "")).lower()
        if return_value and return_value != "success":
            raise ValueError(f"remote draw lookup failed: {payload.get('returnValue')}")
        return cls(
            draw_no=int(payload["drwNo"]),
            date=str(payload.get("drwNoDate") or ""),
            numbers=tuple(int(payload[f"drwtNo{i}"]) for i in range(1, 7)),
            bonus=int(payload["bnusNo"]),
        )

    def to_csv_row(self) -> dict[str, object]:
        return {
            "draw_no": self.draw_no,
            "date": self.date or "",
            "n1": self.numbers[0],
            "n2": self.numbers[1],
            "n3": self.numbers[2],
            "n4": self.numbers[3],
            "n5": self.numbers[4],
            "n6": self.numbers[5],
            "bonus": self.bonus or "",
        }


def _value(row: Mapping[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and str(row[key]).strip() != "":
            return str(row[key]).strip()
    raise KeyError(f"missing required column; expected one of: {', '.join(keys)}")


def _optional_value(row: Mapping[str, str], *keys: str) -> str | None:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return None
