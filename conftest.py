"""Global fixtures: settings, API client, test state, browser lifecycle."""

import re
from collections.abc import Generator, Iterator
from datetime import date
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.betting_page import BettingPage
from utils.api_client import ApiClient
from utils.config import Settings, load_settings
from utils.driver_factory import create_chrome_driver
from utils.models import Match

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


@pytest.fixture(scope="session")
def api_client(settings: Settings) -> Iterator[ApiClient]:
    with ApiClient(
        settings.base_url,
        settings.user_id,
        settings.api_timeout_seconds,
    ) as client:
        yield client


@pytest.fixture
def initial_balance(api_client: ApiClient) -> float:
    """Reset the user's balance and return the persisted value.

    The value is read from GET /api/balance, not from the reset response,
    because the reset response does not match the stored balance (ISSUE-009).
    """
    api_client.reset_balance().raise_for_status()
    return api_client.get_balance()


@pytest.fixture
def upcoming_match(api_client: ApiClient) -> Match:
    """Return a match whose kickoff is after today.

    GET /api/matches also returns past events (ISSUE-001), so we filter them out
    to avoid testing bet placement on an event that has already happened.
    """
    today = date.today()
    upcoming_matches = [
        match for match in api_client.get_matches() if match.kickoff_date > today
    ]
    if not upcoming_matches:
        pytest.fail("GET /api/matches returned no match with a future kickoffDate.")
    return upcoming_matches[0]


@pytest.fixture
def driver(settings: Settings) -> Iterator[WebDriver]:
    # WebDriver's context manager calls quit() on exit, even if the test fails.
    with create_chrome_driver(settings.is_headless) as web_driver:
        yield web_driver


@pytest.fixture
def betting_page(
    driver: WebDriver,
    settings: Settings,
    initial_balance: float,
) -> BettingPage:
    """Open the app only after the balance reset, so the page loads fresh state."""
    page = BettingPage(driver, settings.ui_timeout_seconds)
    return page.open(settings.base_url, settings.user_id)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Save a browser screenshot into reports/ when a UI test fails.

    pytest-check's hook runs inside this wrapper, so soft-assertion failures are
    already reflected in report.failed here.
    """
    report = yield
    web_driver = item.funcargs.get("driver") if hasattr(item, "funcargs") else None
    if report.when == "call" and report.failed and web_driver is not None:
        REPORTS_DIR.mkdir(exist_ok=True)
        file_name = re.sub(r"[^\w.-]", "_", item.name)
        web_driver.save_screenshot(str(REPORTS_DIR / f"{file_name}.png"))
    return report
