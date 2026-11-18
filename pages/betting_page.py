"""Page object for the single-page betting app: match list, bet slip, receipt."""

from dataclasses import dataclass
from urllib.parse import urlencode

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from utils.models import Selection, parse_amount


@dataclass(frozen=True)
class Receipt:
    """What the success receipt modal shows. full_text holds the whole modal."""

    bet_id: str
    match: str
    stake: float
    odds: float
    payout: float
    placed_at: str
    full_text: str


class BettingPage(BasePage):
    _HEADER_BALANCE: Locator = (By.ID, "header-balance")
    _MATCH_LIST: Locator = (By.ID, "match-list")
    _SLIP_SELECTION_CARD: Locator = (By.CLASS_NAME, "betSelectionCard")
    _SLIP_SELECTION_MARKET: Locator = (By.CLASS_NAME, "betSelectionMarket")
    _SLIP_STAKE_INPUT: Locator = (By.ID, "bet-slip-stake-input")
    _SLIP_POTENTIAL_PAYOUT: Locator = (By.ID, "bet-slip-potential-payout")
    _PLACE_BET_BUTTON: Locator = (By.ID, "bet-slip-place-bet")
    _RECEIPT: Locator = (By.ID, "modal-success")
    _RECEIPT_BET_ID: Locator = (By.ID, "modal-success-bet-id")
    _RECEIPT_MATCH: Locator = (By.ID, "modal-success-match")
    _RECEIPT_STAKE: Locator = (By.ID, "modal-success-stake")
    _RECEIPT_ODDS: Locator = (By.ID, "modal-success-odds")
    _RECEIPT_PAYOUT: Locator = (By.ID, "modal-success-payout")
    _RECEIPT_PLACED_AT: Locator = (By.ID, "modal-success-placed-at")
    _RECEIPT_CLOSE: Locator = (By.ID, "modal-success-close")

    def open(self, base_url: str, user_id: str) -> "BettingPage":
        """Open the app for a user and wait until matches and balance are loaded."""
        self._open(f"{base_url}/?{urlencode({'user-id': user_id})}")
        self._find_visible(self._MATCH_LIST)
        return self

    def read_header_balance(self) -> float:
        return parse_amount(self._text_of(self._HEADER_BALANCE))

    def select_outcome(self, match_id: str, selection: Selection) -> None:
        self._click((By.ID, f"odds-{match_id}-{selection.lower()}"))

    def read_slip_selection(self) -> str:
        """Return the selection label from the bet slip, e.g. 'Home'."""
        market_text = self._text_of(self._SLIP_SELECTION_MARKET)
        return market_text.split(":", maxsplit=1)[-1].strip()

    def enter_stake(self, stake: str) -> None:
        self._type(self._SLIP_STAKE_INPUT, stake)

    def read_slip_payout(self) -> float:
        return parse_amount(self._text_of(self._SLIP_POTENTIAL_PAYOUT))

    def click_place_bet(self) -> None:
        self._click(self._PLACE_BET_BUTTON)

    def read_place_bet_button_text(self) -> str:
        return self._text_of(self._PLACE_BET_BUTTON)

    def wait_for_receipt(self) -> Receipt:
        """Wait for the success modal and return its content."""
        receipt_element = self._find_visible(self._RECEIPT)
        return Receipt(
            bet_id=self._text_of(self._RECEIPT_BET_ID),
            match=self._text_of(self._RECEIPT_MATCH),
            stake=parse_amount(self._text_of(self._RECEIPT_STAKE)),
            odds=parse_amount(self._text_of(self._RECEIPT_ODDS)),
            payout=parse_amount(self._text_of(self._RECEIPT_PAYOUT)),
            placed_at=self._text_of(self._RECEIPT_PLACED_AT),
            full_text=receipt_element.text,
        )

    def close_receipt(self) -> None:
        self._click(self._RECEIPT_CLOSE)
        self._wait_until_gone(self._RECEIPT)

    def has_active_selection(self) -> bool:
        return self._is_present(self._SLIP_SELECTION_CARD)
