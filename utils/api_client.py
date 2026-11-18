"""Thin requests wrapper for the betting API."""

from collections.abc import Mapping
from http import HTTPMethod
from types import TracebackType
from typing import Self

import requests

from utils.models import Match, Selection


class ApiClient:
    """Calls the betting API on behalf of one user (x-user-id header).

    Use it as a context manager so the HTTP session is always closed.
    """

    def __init__(self, base_url: str, user_id: str, timeout_seconds: float) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers["x-user-id"] = user_id

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._session.close()

    def get_matches(self) -> list[Match]:
        response = self._request(HTTPMethod.GET, "/api/matches")
        response.raise_for_status()
        return [Match.from_api(item) for item in response.json()]

    def get_balance(self) -> float:
        response = self._request(HTTPMethod.GET, "/api/balance")
        response.raise_for_status()
        return response.json()["balance"]

    def reset_balance(self) -> requests.Response:
        return self._request(HTTPMethod.POST, "/api/reset-balance")

    def place_bet(
        self,
        match_id: str,
        selection: Selection,
        stake: float,
    ) -> requests.Response:
        """Send POST /api/place-bet and return the raw response for assertions."""
        payload = {"matchId": match_id, "selection": selection.value, "stake": stake}
        return self._request(HTTPMethod.POST, "/api/place-bet", json=payload)

    def _request(
        self,
        method: HTTPMethod,
        path: str,
        json: Mapping[str, object] | None = None,
    ) -> requests.Response:
        return self._session.request(
            method,
            f"{self._base_url}{path}",
            json=json,
            timeout=self._timeout_seconds,
        )
