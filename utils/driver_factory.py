"""Create WebDriver instances. Selenium Manager resolves the driver binary."""

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

# The spec targets desktop only, and the bet slip sits on the right side.
DESKTOP_WINDOW_SIZE = "1440,900"


def create_chrome_driver(is_headless: bool) -> WebDriver:
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={DESKTOP_WINDOW_SIZE}")
    return webdriver.Chrome(options=options)
