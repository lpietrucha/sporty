"""SG-TS-4: negative balance protection in POST /api/place-bet.

Known bug this test exposes: ISSUE-007 (the API accepts bets above the balance).
"""

from typing import Any

import pytest
from pytest_check import check

from utils.api_client import ApiClient
from utils.data_loader import load_test_data
from utils.models import Match, Selection

BET_CASES = load_test_data("bets.json")["insufficient_balance_api"]


def _lower_balance_to(
    api_client: ApiClient,
    match: Match,
    current_balance: float,
    target_balance: float,
) -> float:
    """Place one setup bet so the balance lands exactly on target_balance.

    This replaces "place bets until below 100" with a single deterministic step.
    """
    setup_stake = round(current_balance - target_balance, 2)
    if setup_stake > 0:
        response = api_client.place_bet(match.match_id, Selection.HOME, setup_stake)
        assert response.status_code == 200, f"Setup bet failed: {response.text}"

    balance = api_client.get_balance()
    assert balance == target_balance, f"Setup left balance at {balance}"
    return balance


@pytest.mark.parametrize("bet_case", BET_CASES, ids=lambda case: case["id"])
def test_place_bet_above_balance_is_rejected(
    api_client: ApiClient,
    upcoming_match: Match,
    initial_balance: float,
    bet_case: dict[str, Any],
) -> None:
    stake = bet_case["stake_above_balance"]
    balance_before = _lower_balance_to(
        api_client,
        upcoming_match,
        initial_balance,
        bet_case["balance_before_bet"],
    )
    assert stake > balance_before, "Test data error: stake must exceed the balance"

    response = api_client.place_bet(
        upcoming_match.match_id,
        Selection(bet_case["selection"]),
        stake,
    )
    balance_after = api_client.get_balance()

    # The spec does not document the status code for insufficient balance.
    # 422 (semantic validation failure) is assumed, so any 4xx is accepted here
    # and the error code is the real contract.
    check.between_equal(
        response.status_code,
        400,
        499,
        f"Bet above balance should be rejected with 4xx, got {response.text}",
    )
    check.equal(
        response.json().get("error"),
        "insufficient_balance",
        "Error code should be insufficient_balance",
    )
    check.equal(balance_after, balance_before, "Balance should be unchanged")
    check.greater_equal(balance_after, 0, "Balance should never go negative")
