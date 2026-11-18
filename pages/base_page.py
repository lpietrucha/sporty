"""Shared Selenium wrappers with explicit waits. No assertions live here."""

from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout_seconds: float) -> None:
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout_seconds)

    def _open(self, url: str) -> None:
        self._driver.get(url)

    def _find_visible(self, locator: Locator) -> WebElement:
        return self._wait.until(ec.visibility_of_element_located(locator))

    def _click(self, locator: Locator) -> None:
        self._wait.until(ec.element_to_be_clickable(locator)).click()

    def _type(self, locator: Locator, text: str) -> None:
        element = self._find_visible(locator)
        element.clear()
        element.send_keys(text)

    def _text_of(self, locator: Locator) -> str:
        return self._find_visible(locator).text

    def _is_present(self, locator: Locator) -> bool:
        return bool(self._driver.find_elements(*locator))

    def _wait_until_gone(self, locator: Locator) -> None:
        self._wait.until(ec.invisibility_of_element_located(locator))
