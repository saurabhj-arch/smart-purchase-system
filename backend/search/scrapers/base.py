import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


# Candidate binary names to search for in PATH, in order of preference
CHROME_BINARIES = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",                        # Windows via PATH
]

# Candidate chromedriver names
CHROMEDRIVER_BINARIES = [
    "chromedriver",
]

# Windows fallback paths (when not in PATH)
WINDOWS_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Chromium\Application\chrome.exe",
]

WINDOWS_CHROMEDRIVER_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
    r"C:\chromedriver\chromedriver.exe",
    r"C:\Windows\chromedriver.exe",
]


def _find_binary(candidates, windows_fallbacks=None):
    """Returns the first found binary path, or None."""
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path

    if windows_fallbacks:
        import os
        for path in windows_fallbacks:
            if os.path.isfile(path):
                return path

    return None


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    chrome_path = _find_binary(CHROME_BINARIES, WINDOWS_CHROME_PATHS)
    chromedriver_path = _find_binary(CHROMEDRIVER_BINARIES, WINDOWS_CHROMEDRIVER_PATHS)

    if not chrome_path:
        raise RuntimeError(
            "No Chrome/Chromium binary found. "
            "Install via: sudo pacman -S chromium  (Arch) | "
            "sudo apt install chromium-browser  (Ubuntu) | "
            "https://www.google.com/chrome  (Windows)"
        )

    if not chromedriver_path:
        raise RuntimeError(
            "chromedriver not found. "
            "Install via: sudo pacman -S chromium  (Arch, bundled) | "
            "sudo apt install chromium-driver  (Ubuntu) | "
            "https://chromedriver.chromium.org  (Windows)"
        )

    options.binary_location = chrome_path

    driver = webdriver.Chrome(
        service=Service(chromedriver_path),
        options=options
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def get_wait(driver, timeout=10):
    return WebDriverWait(driver, timeout)