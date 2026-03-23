import concurrent.futures
from django.core.cache import cache
from products.models import Product, Website, Price
from .scrapers.amazon import scrape_amazon
from .scrapers.flipkart import scrape_flipkart
from .scrapers.croma import scrape_croma


# Maps your Website DB IDs to scraper functions
SCRAPERS = {
    1: ("Amazon",   scrape_amazon),
    2: ("Flipkart", scrape_flipkart),
    3: ("Croma",    scrape_croma),
}

PLACEHOLDER_IMAGE = "https://placehold.co/300x300?text=No+Image"
CACHE_TIMEOUT = 30 * 60  # 30 minutes in seconds


def get_cache_key(user_id: int, query: str) -> str:
    """
    Builds a unique cache key per user per query.
    e.g. "search_user42_iphone15"
    Normalised: lowercase, spaces removed so "iPhone 15" == "iphone 15"
    """
    normalised = query.lower().replace(" ", "")
    return f"search_user{user_id}_{normalised}"


def run_scraper(website_id: int, query: str) -> tuple[int, list[dict]]:
    """Runs a single scraper and returns (website_id, results)."""
    _, scraper_fn = SCRAPERS[website_id]
    results = scraper_fn(query)
    return website_id, results


def save_results(scraped_data: dict[int, list[dict]]) -> list[dict]:
    """
    Saves scraped results to the DB and returns a unified product list.
    """
    name_to_product = {}

    for website_id, results in scraped_data.items():
        website = Website.objects.get(id=website_id)

        for item in results:
            name_lower = item["name"].lower()

            if name_lower not in name_to_product:
                product, _ = Product.objects.get_or_create(
                    name__iexact=item["name"],
                    defaults={"name": item["name"], "description": ""}
                )
                if item.get("image_url") and not product.image_url:
                    product.image_url = item["image_url"]
                    product.save()
                name_to_product[name_lower] = product
            else:
                product = name_to_product[name_lower]
                if item.get("image_url") and not product.image_url:
                    product.image_url = item["image_url"]
                    product.save()

            Price.objects.update_or_create(
                product=product,
                website=website,
                defaults={
                    "price": item["price"],
                    "product_url": item["url"],
                }
            )

    response = []
    for product in name_to_product.values():
        prices = Price.objects.filter(product=product).select_related("website")
        stores = [
            {
                "site": p.website.name,
                "price": float(p.price),
                "link": p.product_url,
            }
            for p in prices
        ]
        response.append({
            "id": product.id,
            "name": product.name,
            "image_url": product.image_url if product.image_url else PLACEHOLDER_IMAGE,
            "stores": stores,
        })

    return response


def scrape_fresh(query: str) -> list[dict]:
    """
    Runs all 3 scrapers in parallel and saves results to DB.
    Always hits the live sites — no cache involved.
    """
    scraped_data = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_scraper, website_id, query): website_id
            for website_id in SCRAPERS
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                website_id, results = future.result()
                scraped_data[website_id] = results
                print(f"[DEBUG] Website {website_id} returned {len(results)} results")
            except Exception as e:
                website_id = futures[future]
                print(f"[SearchService] Scraper for website_id={website_id} failed: {e}")
                scraped_data[website_id] = []

    return save_results(scraped_data)


def search_and_scrape(query: str, user=None) -> list[dict]:
    """
    Main entry point called by the view.

    - If user is logged in: check cache first, return instantly if hit,
      otherwise scrape fresh and cache the results for 30 minutes.
    - If user is a guest: always scrape fresh, never cache.
    """
    if user and user.is_authenticated:
        cache_key = get_cache_key(user.id, query)
        cached = cache.get(cache_key)

        if cached is not None:
            print(f"[Cache] HIT for user={user.id} query='{query}' — returning instantly")
            return cached

        print(f"[Cache] MISS for user={user.id} query='{query}' — scraping fresh")
        results = scrape_fresh(query)

        # Store in cache for 30 minutes
        cache.set(cache_key, results, timeout=CACHE_TIMEOUT)
        print(f"[Cache] Stored results for user={user.id} query='{query}' (30 min TTL)")
        return results

    # Guest user — always scrape live
    print(f"[Cache] Guest search for '{query}' — scraping live, no cache")
    return scrape_fresh(query)


# ── Product Page Scraping ────────────────────────────────────────────────────

from .scrapers.amazon import scrape_amazon_for_product
from .scrapers.flipkart import scrape_flipkart_for_product
from .scrapers.croma import scrape_croma_for_product

PRODUCT_SCRAPERS = {
    1: scrape_amazon_for_product,
    2: scrape_flipkart_for_product,
    3: scrape_croma_for_product,
}


def scrape_product_prices(product) -> dict:
    """
    Given an existing Product instance, scrapes all 3 sites for that
    specific product name and updates its prices in the DB.

    Returns the product as a dict with all available store prices.
    """
    def run(website_id):
        scraper_fn = PRODUCT_SCRAPERS[website_id]
        result = scraper_fn(product.name)
        return website_id, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run, wid): wid for wid in PRODUCT_SCRAPERS}
        for future in concurrent.futures.as_completed(futures):
            try:
                website_id, item = future.result()
                if item:
                    website = Website.objects.get(id=website_id)
                    Price.objects.update_or_create(
                        product=product,
                        website=website,
                        defaults={
                            "price": item["price"],
                            "product_url": item["url"],
                        }
                    )
                    # Update image if product doesn't have one yet
                    if item.get("image_url") and not product.image_url:
                        product.image_url = item["image_url"]
                        product.save()
            except Exception as e:
                print(f"[ProductScrape] website_id={futures[future]} failed: {e}")

    # Build response
    prices = Price.objects.filter(product=product).select_related("website")
    stores = [
        {
            "site": p.website.name,
            "price": float(p.price),
            "link": p.product_url,
        }
        for p in prices
    ]
    return {
        "id": product.id,
        "name": product.name,
        "image_url": product.image_url if product.image_url else PLACEHOLDER_IMAGE,
        "stores": stores,
    }