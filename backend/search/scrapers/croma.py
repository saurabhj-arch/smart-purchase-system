import time
from bs4 import BeautifulSoup
from .base import get_driver, get_wait
from .matcher import choose_best_verified_match, fetch_product_meta, _name_similarity
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_croma(query: str) -> list[dict]:
    """General search — returns top 5 results for a query."""
    return _scrape(query, max_results=10)


def scrape_croma_for_product(product_name: str) -> dict | None:
    """
    Targeted scrape — searches for a specific product name and returns
    the single best matching result, or None if not found.
    """
    # Keep deeper candidate pool for exact-variant verification.
    results = _scrape(product_name, max_results=12)
    best = choose_best_verified_match(product_name, results, site_name="Croma")

    if not best:
        return None
    best.update(fetch_product_meta(best["url"], "Croma"))
    return best


def _scrape(query: str, max_results: int) -> list[dict]:
    driver = get_driver()
    results = []
    scraper_failed = False

    try:
        search_url = f"https://www.croma.com/searchB?q={query.replace(' ', '%20')}%3Arelevance"
        driver.get(search_url)

        try:
            get_wait(driver, timeout=14).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-item, div.product-listing, div.product-tile"))
            )
        except Exception:
            # Some Croma pages render slightly different markup; allow fallback.
            try:
                get_wait(driver, timeout=8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-item, div.product-listing"))
                )
            except Exception:
                print("[Croma Scraper] Timed out waiting for results")
                raise RuntimeError("Croma search results did not load")

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("li.product-item")

        for card in cards[:max_results]:
            try:
                name_tag = card.select_one("h3.product-title")
                if not name_tag:
                    name_tag = card.select_one("a.product-title-link")
                name = name_tag.get_text(strip=True) if name_tag else None

                price_tag = card.select_one("span.amount")
                if not price_tag:
                    # Try alternative price selectors
                    price_tag = card.select_one("span.price") or card.select_one("div.price")
                
                price_text = (
                    price_tag.get_text(strip=True).replace("₹", "").replace(",", "")
                    if price_tag else None
                )
                price = float(price_text) if price_text else None

                link_tag = card.select_one("a.product-title-link") or card.select_one("a")
                if not link_tag:
                    link_tag = card.select_one("a[href*='/product/']")
                url = (
                    "https://www.croma.com" + link_tag["href"]
                    if link_tag and link_tag.get("href", "").startswith("/")
                    else link_tag["href"] if link_tag else None
                )

                img_tag = card.select_one("img.product-img") or card.select_one("img")
                if not img_tag:
                    img_tag = card.select_one("img[data-src]")
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
                print(f"[Croma Scraper] Card error: {e}")
                continue

    except Exception as e:
        print(f"[Croma Scraper] Error: {e}")
        raise

    finally:
        driver.quit()

    return results