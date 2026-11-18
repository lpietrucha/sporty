"""Domain models shared by the API client, page objects and tests."""

import re
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any

_AMOUNT_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")


class Selection(StrEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"


@dataclass(frozen=True)
class Match:
    match_id: str
    home_team: str
    away_team: str
    kickoff_date: date
    odds: dict[Selection, float]

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "Match":
        """Build a Match from one item of the GET /api/matches response."""
        return cls(
            match_id=payload["id"],
            home_team=payload["homeTeam"],
            away_team=payload["awayTeam"],
            kickoff_date=date.fromisoformat(payload["kickoffDate"]),
            odds={
                selection: payload["odds"][selection.lower()]
                for selection in Selection
            },
        )


def parse_amount(text: str) -> float:
    """Extract the first number from a UI label such as 'Balance: €120.00'.

    Raises:
        ValueError: If the text contains no number.
    """
    found = _AMOUNT_PATTERN.search(text.replace(",", ""))
    if found is None:
        raise ValueError(f"No amount found in {text!r}")
    return float(found.group())
