import concurrent.futures
from django.core.cache import cache
from django.utils import timezone
from products.models import Product, Website, Price
from .scrapers.amazon import scrape_amazon
from .scrapers.flipkart import scrape_flipkart
from .scrapers.croma import scrape_croma
from .scrapers.matcher import _name_similarity, _passes_variant_guards, _fetch_title_from_url


# Maps your Website DB IDs to scraper functions
SCRAPERS = {
    1: ("Amazon",   scrape_amazon),
    2: ("Flipkart", scrape_flipkart),
    3: ("Croma",    scrape_croma),
}

PLACEHOLDER_IMAGE = "https://placehold.co/300x300?text=No+Image"
CACHE_TIMEOUT = 30 * 60  # 30 minutes in seconds
PRODUCT_PAGE_CACHE_TIMEOUT = 15 * 60  # 15 minutes


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


def _should_merge_products(product_a: dict, product_b: dict, query: str) -> bool:
    """
    Determine if two products from different websites are actually the same product.
    Uses similar logic to the matcher but adapted for cross-website comparison.
    """
    name_a = product_a.get("name", "").strip()
    name_b = product_b.get("name", "").strip()
    
    if not name_a or not name_b:
        return False
    
    # Calculate name similarity
    base_similarity = _name_similarity(name_a, name_b)
    
    # If names are very similar, they're likely the same product
    if base_similarity >= 0.85:
        print(f"[Product Matching] High similarity ({base_similarity:.2f}) between '{name_a}' and '{name_b}'")
        return True
    
    # For books and similar items, check if they contain similar core terms
    # Remove common variations like "Book 1", "(Paperback)", etc.
    def normalize_title(title: str) -> str:
        # Remove book numbers, formats, etc.
        title = title.lower()
        title = title.replace("book 1", "").replace("(book 1)", "").replace(": book 1", "")
        title = title.replace("paperback", "").replace("hardcover", "").replace("ebook", "")
        title = title.replace("(paperback)", "").replace("(hardcover)", "").replace("(ebook)", "")
        title = title.replace("vol. 1", "").replace("volume 1", "")
        # Remove extra whitespace and punctuation
        import re
        title = re.sub(r'[^\w\s]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    normalized_a = normalize_title(name_a)
    normalized_b = normalize_title(name_b)
    
    # If normalized titles are very similar, they're the same product
    normalized_similarity = _name_similarity(normalized_a, normalized_b)
    if normalized_similarity >= 0.9:
        print(f"[Product Matching] Normalized similarity ({normalized_similarity:.2f}) between '{normalized_a}' and '{normalized_b}'")
        return True
    
    # For the specific case of Percy Jackson, check for common patterns
    if "percy jackson" in name_a.lower() and "percy jackson" in name_b.lower():
        if ("lightning thief" in name_a.lower() and "lightning thief" in name_b.lower()) or \
           ("book 1" in name_a.lower() and "book 1" in name_b.lower()):
            print(f"[Product Matching] Percy Jackson match: '{name_a}' and '{name_b}'")
            return True
    
    return False


def save_results(scraped_data: dict[int, list[dict]], query: str = "") -> list[dict]:
    """
    Saves scraped results to the DB and returns a unified product list.
    Now uses intelligent product matching across websites.
    """
    # Collect all products from all websites
    all_products = []
    for website_id, results in scraped_data.items():
        website = Website.objects.get(id=website_id)
        for item in results:
            all_products.append({
                "website": website,
                "data": item
            })
    
    # Group products that are actually the same item
    product_groups = []
    
    for product_info in all_products:
        website = product_info["website"]
        item = product_info["data"]
        
        # Try to find an existing group this product belongs to
        matched_group = None
        for group in product_groups:
            # Check if this product matches any product in the existing group
            for existing_product in group["products"]:
                if _should_merge_products(item, existing_product["data"], query):
                    matched_group = group
                    break
            if matched_group:
                break
        
        if matched_group:
            # Add to existing group
            matched_group["products"].append({
                "website": website,
                "data": item
            })
        else:
            # Create new group
            product_groups.append({
                "products": [{
                    "website": website,
                    "data": item
                }]
            })
    
    # Now save each group as a single product with multiple prices
    response = []
    for group in product_groups:
        if not group["products"]:
            continue
            
        # Use the first product in the group as the canonical product
        canonical_product = group["products"][0]["data"]
        canonical_name = canonical_product["name"]
        
        print(f"[Product Grouping] Creating product '{canonical_name}' with {len(group['products'])} variants from:")
        for p in group["products"]:
            print(f"  - {p['website'].name}: {p['data']['name']}")
        
        # Create or get the product
        product, _ = Product.objects.get_or_create(
            name__iexact=canonical_name,
            defaults={"name": canonical_name, "description": ""}
        )
        
        # Set image URL if not already set
        if canonical_product.get("image_url") and not product.image_url:
            product.image_url = canonical_product["image_url"]
            product.save()
        
        # Save prices for all websites in this group
        for product_info in group["products"]:
            website = product_info["website"]
            item = product_info["data"]
            
            Price.objects.update_or_create(
                product=product,
                website=website,
                defaults={
                    "price": item["price"],
                    "product_url": item["url"],
                }
            )
        
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
        
        response.append({
            "id": product.id,
            "name": product.name,
            "image_url": product.image_url if product.image_url else PLACEHOLDER_IMAGE,
            "stores": stores,
        })
    
    print(f"[Search Result] Returning {len(response)} unified products")
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

    return save_results(scraped_data, query)


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
    cache_key = f"product_prices_{product.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        print(f"[ProductCache] HIT for product_id={product.id}")
        return cached

    print(f"[ProductCache] MISS for product_id={product.id} — scraping fresh")

    def run(website_id):
        scraper_fn = PRODUCT_SCRAPERS[website_id]
        result = scraper_fn(product.name)
        return website_id, result

    site_results = {wid: {"item": None, "error": None} for wid in PRODUCT_SCRAPERS}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run, wid): wid for wid in PRODUCT_SCRAPERS}
        for future in concurrent.futures.as_completed(futures):
            website_id = futures[future]
            try:
                _, item = future.result()
                if isinstance(item, dict) and item.get("error"):
                    site_results[website_id] = {"item": None, "error": item["error"]}
                else:
                    site_results[website_id] = {"item": item, "error": None}

                website = Website.objects.get(id=website_id)
                if item and not item.get("error"):
                    Price.objects.update_or_create(
                        product=product,
                        website=website,
                        defaults={
                            "price": item["price"],
                            "product_url": item["url"],
                        }
                    )
                    if item.get("image_url") and not product.image_url:
                        product.image_url = item["image_url"]
                        product.save()
                # Leave stale prices in place when the site cannot be verified.
            except Exception as e:
                site_results[website_id] = {"item": None, "error": str(e)}
                print(f"[ProductScrape] website_id={website_id} failed: {e}")

    # Build response with all websites, including explicit unavailability.
    stores = []
    for website_id, scraper_fn in PRODUCT_SCRAPERS.items():
        _ = scraper_fn  # keep loop explicit/readable
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            continue

        entry = site_results.get(website_id, {})
        item = entry.get("item")
        error = entry.get("error")
        stale_price = Price.objects.filter(product=product, website=website).first()

        if item:
            stores.append({
                "site": website.name,
                "price": float(item["price"]),
                "link": item["url"],
                "available": True,
                "message": "",
                "avg_rating": item.get("avg_rating"),
                "reviews": item.get("reviews", []),
            })
        elif error:
            if stale_price:
                stores.append({
                    "site": website.name,
                    "price": float(stale_price.price),
                    "link": stale_price.product_url,
                    "available": True,
                    "message": "Live scrape failed; showing last known store listing.",
                    "avg_rating": None,
                    "reviews": [],
                })
            else:
                stores.append({
                    "site": website.name,
                    "price": None,
                    "link": "",
                    "available": False,
                    "message": "Scraper failed to verify availability for this store.",
                    "avg_rating": None,
                    "reviews": [],
                })
        elif stale_price:
            stores.append({
                "site": website.name,
                "price": float(stale_price.price),
                "link": stale_price.product_url,
                "available": True,
                "message": "No live match found; showing last known listing.",
                "avg_rating": None,
                "reviews": [],
            })
        else:
            stores.append({
                "site": website.name,
                "price": None,
                "link": "",
                "available": False,
                "message": "This specific product is not available on this website.",
                "avg_rating": None,
                "reviews": [],
            })

    response = {
        "id": product.id,
        "name": product.name,
        "image_url": product.image_url if product.image_url else PLACEHOLDER_IMAGE,
        "stores": stores,
        "last_updated": timezone.now().isoformat(),
    }
    cache.set(cache_key, response, timeout=PRODUCT_PAGE_CACHE_TIMEOUT)
    print(f"[ProductCache] Stored product_id={product.id} ({PRODUCT_PAGE_CACHE_TIMEOUT // 60} min TTL)")
    return response