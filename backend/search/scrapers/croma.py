import time
from bs4 import BeautifulSoup
from .base import get_driver, get_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_croma(query: str) -> list[dict]:
    """General search — returns top 5 results for a query."""
    return _scrape(query, max_results=5)


def scrape_croma_for_product(product_name: str) -> dict | None:
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
        search_url = f"https://www.croma.com/searchB?q={query.replace(' ', '%20')}%3Arelevance"
        driver.get(search_url)

        get_wait(driver, timeout=12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-item"))
        )

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("li.product-item")

        for card in cards[:max_results]:
            try:
                name_tag = card.select_one("h3.product-title")
                name = name_tag.get_text(strip=True) if name_tag else None

                price_tag = card.select_one("span.amount")
                price_text = (
                    price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
                    if price_tag else None
                )
                price = float(price_text) if price_text else None

                link_tag = card.select_one("a.product-title-link") or card.select_one("a")
                url = (
                    "https://www.croma.com" + link_tag["href"]
                    if link_tag and link_tag.get("href", "").startswith("/")
                    else link_tag["href"] if link_tag else None
                )

                img_tag = card.select_one("img.product-img") or card.select_one("img")
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

            except Exception:
                continue

    except Exception as e:
        print(f"[Croma Scraper] Error: {e}")

    finally:
        driver.quit()

    return results