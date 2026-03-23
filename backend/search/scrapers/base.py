from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


def get_driver():
    """
    Returns a headless Chrome WebDriver instance.
    Make sure chromedriver is installed and in PATH.
    Install via: pip install selenium webdriver-manager
    """
    options = Options()
    options.add_argument("--headless")               # Run without opening a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hides bot fingerprint
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Mimics a real browser user-agent so sites don't block us
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # webdriver-manager auto-downloads the right chromedriver version
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Extra stealth: remove the 'webdriver' property JS sees
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def get_wait(driver, timeout=10):
    """Returns a WebDriverWait instance. Use for waiting until elements load."""
    return WebDriverWait(driver, timeout)