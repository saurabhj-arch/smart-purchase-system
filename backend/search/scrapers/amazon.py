import time
from bs4 import BeautifulSoup
from .base import get_driver, get_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_amazon(query: str) -> list[dict]:
    """General search — returns top 5 results for a query."""
    return _scrape(query, max_results=5)


def scrape_amazon_for_product(product_name: str) -> dict | None:
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
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        driver.get(search_url)

        try:
            get_wait(driver, timeout=12).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "div[data-component-type='s-search-result'], "
                     "div.s-result-item[data-asin]")
                )
            )
        except Exception:
            print("[Amazon Scraper] Timed out waiting for results")
            return []

        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = (
            soup.select("div[data-component-type='s-search-result']") or
            soup.select("div.s-result-item[data-asin]")
        )
        cards = [c for c in cards if c.get("data-asin")]

        print(f"[Amazon Scraper] Found {len(cards)} cards")

        for card in cards[:max_results + 3]:
            try:
                h2 = card.select_one("h2")
                name = h2.get_text(strip=True) if h2 else None
                if not name or len(name) < 10:
                    continue

                whole = card.select_one("span.a-price-whole")
                fraction = card.select_one("span.a-price-fraction")
                if whole:
                    whole_text = whole.get_text(strip=True).replace(",", "").replace(".", "")
                    fraction_text = fraction.get_text(strip=True) if fraction else "00"
                    try:
                        price = float(f"{whole_text}.{fraction_text}")
                    except ValueError:
                        price = None
                else:
                    price_tag = card.select_one("span.a-offscreen")
                    price_text = (
                        price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
                        if price_tag else None
                    )
                    try:
                        price = float(price_text) if price_text else None
                    except ValueError:
                        price = None

                asin = card.get("data-asin")
                url = f"https://www.amazon.in/dp/{asin}" if asin else None

                img_tag = (
                    card.select_one("img.s-image") or
                    card.select_one("img[data-image-index]")
                )
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

                if len(results) == max_results:
                    break

            except Exception as e:
                print(f"[Amazon Scraper] Card parse error: {e}")
                continue

    except Exception as e:
        print(f"[Amazon Scraper] Error: {e}")

    finally:
        driver.quit()

    return results