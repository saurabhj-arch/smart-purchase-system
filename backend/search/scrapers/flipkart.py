import time
from bs4 import BeautifulSoup
from .base import get_driver, get_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_flipkart(query: str) -> list[dict]:
    """General search — returns top 5 results for a query."""
    return _scrape(query, max_results=5)


def scrape_flipkart_for_product(product_name: str) -> dict | None:
    """
    Targeted scrape — searches for a specific product name and returns
    the single best matching result, or None if not found.
    """
    results = _scrape(product_name, max_results=3)
    return results[0] if results else None


def _scrape(query: str, max_results: int) -> list[dict]:
    driver = get_driver()
    results = []

    try:
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        driver.get(search_url)

        # Close login popup safely
        try:
            close_btn = get_wait(driver, timeout=5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'✕') or contains(text(),'✗') or contains(text(),'×')]")
                )
            )
            close_btn.click()
            time.sleep(1)
        except Exception:
            pass

        try:
            get_wait(driver, timeout=12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id]"))
            )
        except Exception:
            print("[Flipkart Scraper] Timed out waiting for page")
            return []

        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("div[data-id]")
        print(f"[Flipkart Scraper] Found {len(cards)} cards")

        for card in cards[:max_results]:
            try:
                # Name — confirmed class from card HTML: div.RG5Slk
                name_tag = card.select_one("div.RG5Slk")
                name = name_tag.get_text(strip=True) if name_tag else None

                # Price — find any element containing ₹ symbol
                # Minimum ₹1000 to filter out cashback/coupon/EMI amounts like ₹201
                price = None
                for tag in card.find_all(["div", "span"]):
                    text = tag.get_text(strip=True)
                    if text.startswith("₹") and len(text) < 15:
                        price_text = text.replace("₹", "").replace(",", "").strip()
                        try:
                            candidate = float(price_text.split()[0])
                            if candidate >= 1000:  # ignore cashback/coupon amounts
                                price = candidate
                                break
                        except (ValueError, TypeError):
                            continue

                # URL — confirmed class from card HTML: a.k7wcnx
                link_tag = card.select_one("a.k7wcnx") or card.select_one("a[href*='/p/']")
                url = None
                if link_tag:
                    href = link_tag.get("href", "")
                    url = (
                        "https://www.flipkart.com" + href
                        if href.startswith("/")
                        else href
                    )

                # Image — confirmed class from card HTML: img.UCc1lI
                img_tag = card.select_one("img.UCc1lI") or card.select_one("img")
                image_url = (
                    img_tag.get("src") or img_tag.get("data-src")
                    if img_tag else None
                )

                if name and price and url:
                    results.append({
                        "name": name,
                        "price": price,
                        "url": url,
                        "image_url": image_url or "",
                    })

            except Exception as e:
                print(f"[Flipkart Scraper] Card error: {e}")
                continue

    except Exception as e:
        print(f"[Flipkart Scraper] Error: {e}")

    finally:
        driver.quit()

    return results