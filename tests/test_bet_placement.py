"""SG-TS-2: successful single bet placement (UI), cross-checked against the API.

Receipt and balance checks are soft (pytest-check), so one failure does not hide
the others. Known bugs this test exposes: ISSUE-003, 004, 005, 006.
"""

import pytest
from pytest_check import check

from pages.betting_page import BettingPage
from utils.api_client import ApiClient
from utils.data_loader import load_test_data
from utils.models import Match, Selection

BET_CASES = load_test_data("bets.json")["single_bet_ui"]


@pytest.mark.parametrize("bet_case", BET_CASES, ids=lambda case: case["id"])
def test_single_bet_placement_shows_receipt_and_deducts_stake(
    betting_page: BettingPage,
    api_client: ApiClient,
    upcoming_match: Match,
    initial_balance: float,
    bet_case: dict[str, str],
) -> None:
    selection = Selection(bet_case["selection"])
    stake = float(bet_case["stake"])
    expected_odds = upcoming_match.odds[selection]
    expected_payout = round(stake * expected_odds, 2)
    expected_balance = round(initial_balance - stake, 2)

    check.equal(
        betting_page.read_header_balance(),
        initial_balance,
        "Screen balance should match the server before betting",
    )

    betting_page.select_outcome(upcoming_match.match_id, selection)
    betting_page.enter_stake(bet_case["stake"])
    slip_selection = betting_page.read_slip_selection()
    check.equal(
        betting_page.read_slip_payout(),
        expected_payout,
        "Bet slip payout should be stake x odds",
    )

    betting_page.click_place_bet()
    check.equal(
        betting_page.read_place_bet_button_text(),
        "Placing...",
        "Place Bet button should show the loading state",
    )

    # Hard stop: without a receipt the remaining checks are meaningless.
    receipt = betting_page.wait_for_receipt()
    check.is_true(receipt.bet_id, "Receipt should show a bet ID")
    check.equal(
        receipt.match,
        f"{upcoming_match.home_team} vs {upcoming_match.away_team}",
        "ISSUE-005: receipt should list the home team first",
    )
    check.is_in(
        slip_selection,
        receipt.full_text,
        "ISSUE-003: receipt should show the selection",
    )
    check.equal(receipt.stake, stake, "Receipt stake")
    check.equal(receipt.odds, expected_odds, "Receipt odds")
    check.equal(
        receipt.payout,
        expected_payout,
        "ISSUE-004: receipt payout should be stake x odds",
    )
    check.is_true(receipt.placed_at, "Receipt should show a placement timestamp")

    betting_page.close_receipt()
    check.is_false(
        betting_page.has_active_selection(),
        "Closing the receipt should leave no active selection",
    )

    check.equal(
        api_client.get_balance(),
        expected_balance,
        "Server balance should drop by exactly the stake",
    )
    check.equal(
        betting_page.read_header_balance(),
        expected_balance,
        "ISSUE-006: screen balance should match the server after betting",
    )
