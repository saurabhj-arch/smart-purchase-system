import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from typing import Any

from bs4 import BeautifulSoup

from .base import get_driver


STOP_WORDS = {
    "for",
    "with",
    "and",
    "the",
    "from",
    "inch",
    "inches",
    "new",
    "latest",
    "edition",
    "model",
    "buy",
    "online",
    "india",
}

KNOWN_COLORS = {
    "black", "white", "blue", "red", "green", "yellow", "purple", "pink",
    "grey", "gray", "silver", "gold", "midnight", "starlight", "violet",
    "coral", "teal", "orange", "beige",
}

DESCRIPTOR_TOKENS = {
    "soft",
    "light",
    "dark",
    "deep",
    "pale",
    "bright",
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _tokenise(text: str) -> set[str]:
    return {t for t in _normalise(text).split() if t and t not in STOP_WORDS}


def _name_similarity(query: str, candidate: str) -> float:
    query_tokens = _tokenise(query)
    candidate_tokens = _tokenise(candidate)

    if not query_tokens or not candidate_tokens:
        return 0.0

    overlap = len(query_tokens.intersection(candidate_tokens)) / max(len(query_tokens), 1)
    ratio = SequenceMatcher(None, _normalise(query), _normalise(candidate)).ratio()
    return (0.65 * overlap) + (0.35 * ratio)


def _extract_storage_tokens(text: str) -> set[str]:
    norm = _normalise(text)
    matches = re.findall(r"\b(\d{2,4})\s*(gb|tb)\b", norm)
    return {f"{num}{unit}" for num, unit in matches}


def _extract_numeric_tokens(text: str) -> set[str]:
    """
    Extract standalone numeric tokens (e.g. 14, 2026, 1200).
    Storage values are handled separately by _extract_storage_tokens.
    """
    norm = _normalise(text)
    return set(re.findall(r"\b\d{1,4}\b", norm))


def _extract_model_code_tokens(text: str) -> set[str]:
    """
    Extract mixed model/code tokens such as: 17e, m5, a16, s24, x100.
    """
    norm = _normalise(text)
    tokens = {
        t for t in re.findall(r"\b[a-z0-9]*\d+[a-z]+[a-z0-9]*\b", norm)
        if len(t) >= 2
    }
    # Storage-like tokens (e.g., 256gb, 1tb) are not model codes.
    return {t for t in tokens if not re.fullmatch(r"\d{1,4}(gb|tb)", t)}


def _extract_color_tokens(text: str) -> set[str]:
    return {t for t in _tokenise(text) if t in KNOWN_COLORS}


def _core_brand_token(query: str) -> str | None:
    # Important: preserve word order from the original query.
    # Using _tokenise() here is unsafe because it returns a set.
    ordered_tokens = _normalise(query).split()
    for token in ordered_tokens:
        if token in STOP_WORDS or token in KNOWN_COLORS:
            continue
        if token.isdigit():
            continue
        # skip pure storage suffix tokens
        if token in {"gb", "tb"}:
            continue
        return token
    return None


def _required_model_tokens(query: str) -> set[str]:
    """
    Pull essential query tokens (excluding colors/stop words) that should
    appear on the final landing page title.
    """
    tokens = {t for t in _tokenise(query) if len(t) >= 2 and t not in KNOWN_COLORS}
    # Ignore generic commerce tokens that are too noisy
    noisy = {"gb", "tb", "5g", "wifi", "bluetooth"} | DESCRIPTOR_TOKENS
    return {t for t in tokens if t not in noisy}


def _is_low_quality_landing_title(title: str) -> bool:
    if not title:
        return True
    norm = _normalise(title)
    bad_markers = {
        "product summary",
        "keyboard shortcut",
        "captcha",
        "robot check",
        "sorry we just need to make sure",
        "enter the characters you see",
    }
    return any(marker in norm for marker in bad_markers) or len(norm) < 12


def _token_coverage(required_tokens: set[str], text: str) -> float:
    if not required_tokens:
        return 1.0
    text_tokens = _tokenise(text)
    matched = len(required_tokens.intersection(text_tokens))
    return matched / len(required_tokens)


def _passes_variant_guards(query: str, candidate_name: str, landing_title: str) -> bool:
    """
    Strict guardrails for wrong-variant links:
    - if query asks for a storage variant, candidate/landing must include it
    - if query asks for a color, candidate/landing should include it
    - brand token should appear somewhere in candidate or landing title
    """
    query_storage = _extract_storage_tokens(query)
    query_numbers = _extract_numeric_tokens(query)
    query_model_codes = _extract_model_code_tokens(query)
    query_colors = _extract_color_tokens(query)
    query_brand = _core_brand_token(query)

    use_landing = not _is_low_quality_landing_title(landing_title)
    reference_text = landing_title if use_landing else candidate_name

    ref_storage = _extract_storage_tokens(reference_text)
    ref_numbers = _extract_numeric_tokens(reference_text)
    ref_model_codes = _extract_model_code_tokens(reference_text)
    ref_colors = _extract_color_tokens(reference_text)
    ref_tokens = _tokenise(reference_text)
    required_tokens = _required_model_tokens(query)

    if query_storage and not query_storage.intersection(ref_storage):
        return False

    # Keep color as soft check globally by not hard-failing on miss.
    if query_brand and query_brand not in ref_tokens:
        return False

    # Prevent wrong model variants (e.g., iPhone 14 query matching iPhone 11).
    model_numbers = {
        n for n in query_numbers
        if f"{n}gb" not in query_storage and f"{n}tb" not in query_storage
    }
    if model_numbers and not model_numbers.issubset(ref_numbers):
        return False

    # Model code tokens (like 17e, m5) are strong discriminators.
    if query_model_codes and not query_model_codes.issubset(ref_model_codes):
        return False

    # Require most key query tokens to exist on landing title.
    token_coverage = _token_coverage(required_tokens, reference_text)
    min_coverage = 0.5 if (query_storage or model_numbers or query_model_codes) else 0.6
    if token_coverage < min_coverage:
        return False

    # If color exists on landing, reward later in scoring; don't block here.
    _ = query_colors, ref_colors

    return True


def _fetch_title_from_url(url: str) -> str:
    """
    Fetch the destination title/H1 from a product URL.
    Uses Selenium to follow redirects and render JS-heavy pages.
    """
    driver = get_driver()
    try:
        driver.get(url)
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        h1 = soup.select_one("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(" ", strip=True)
        if soup.title and soup.title.get_text(strip=True):
            return soup.title.get_text(" ", strip=True)
        return driver.title or ""
    except Exception:
        return ""
    finally:
        driver.quit()


def _parse_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def _clean_review_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _extract_ld_json_blocks(soup: BeautifulSoup) -> list[Any]:
    blocks = []
    for script in soup.select("script[type='application/ld+json']"):
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
            blocks.append(parsed)
        except Exception:
            continue
    return blocks


def _extract_rating_and_reviews_from_ld_json(soup: BeautifulSoup) -> tuple[float | None, list[str]]:
    rating = None
    reviews: list[str] = []

    def walk(node: Any):
        nonlocal rating, reviews
        if isinstance(node, dict):
            agg = node.get("aggregateRating")
            if isinstance(agg, dict) and rating is None:
                rating = _parse_float(agg.get("ratingValue"))

            rev = node.get("review")
            if isinstance(rev, list):
                for r in rev:
                    if isinstance(r, dict):
                        txt = _clean_review_text(r.get("reviewBody", ""))
                        if txt:
                            reviews.append(txt)
            elif isinstance(rev, dict):
                txt = _clean_review_text(rev.get("reviewBody", ""))
                if txt:
                    reviews.append(txt)

            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for block in _extract_ld_json_blocks(soup):
        walk(block)

    # Deduplicate and keep short sensible list.
    unique_reviews = []
    seen = set()
    for r in reviews:
        key = r.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_reviews.append(r)
        if len(unique_reviews) == 5:
            break

    return rating, unique_reviews


def fetch_product_meta(url: str, site_name: str) -> dict:
    """
    Fetch average rating and a few review snippets from the final product URL.
    Returns {"avg_rating": float|None, "reviews": [str, ...]}.
    """
    driver = get_driver()
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        rating, reviews = _extract_rating_and_reviews_from_ld_json(soup)

        # Site-specific fallbacks when ld+json misses fields.
        if rating is None:
            if site_name.lower() == "amazon":
                tag = soup.select_one("span[data-hook='rating-out-of-text']")
                if tag:
                    m = re.search(r"(\d+(\.\d+)?)", tag.get_text(" ", strip=True))
                    if m:
                        rating = _parse_float(m.group(1))
            elif site_name.lower() == "flipkart":
                tag = soup.select_one("div.XQDdHH")
                if tag:
                    rating = _parse_float(tag.get_text(strip=True))
            elif site_name.lower() == "croma":
                # Croma changes classes/structure often; try multiple patterns.
                croma_rating_selectors = [
                    "span[data-testid='rating-value']",
                    "span.rating-text",
                    "span.ratingValue",
                    "div.rating span",
                    "div.pdp-rating span",
                    "div.review-rating span",
                ]
                for sel in croma_rating_selectors:
                    tag = soup.select_one(sel)
                    if not tag:
                        continue
                    text = tag.get_text(" ", strip=True)
                    m = re.search(
                        r"\b([1-4](?:\.\d+)?|5(?:\.0)?)\b(?:\s*/\s*5|\s*out\s*of\s*5)?",
                        text,
                        flags=re.IGNORECASE,
                    )
                    if m:
                        candidate = _parse_float(m.group(1))
                        if candidate is not None and 0.0 <= candidate <= 5.0:
                            rating = candidate
                            break

                if rating is None:
                    # Text fallback: only trust explicit "x/5" or "x out of 5" patterns.
                    page_text = soup.get_text(" ", strip=True)
                    m = re.search(
                        r"\b([1-4](?:\.\d+)?|5(?:\.0)?)\b\s*(?:/ ?5|out of 5)\b",
                        page_text,
                        flags=re.IGNORECASE,
                    )
                    if m:
                        candidate = _parse_float(m.group(1))
                        if candidate is not None and 0.0 <= candidate <= 5.0:
                            rating = candidate

                if rating is None:
                    # JSON/script fallback: trust only ratingValue (not generic "rating").
                    for script in soup.select("script"):
                        txt = script.string or script.get_text(" ", strip=True)
                        if not txt:
                            continue
                        if "ratingValue" not in txt:
                            continue
                        m = re.search(r'"ratingValue"\s*:\s*"?(?P<r>[0-5](?:\.\d+)?)"?', txt)
                        if m:
                            candidate = _parse_float(m.group("r"))
                            if candidate is not None and 0.0 <= candidate <= 5.0:
                                rating = candidate
                                break

        if not reviews:
            if site_name.lower() == "amazon":
                nodes = soup.select("div[data-hook='review'] span[data-hook='review-body']")[:5]
                reviews = [_clean_review_text(n.get_text(" ", strip=True)) for n in nodes if n.get_text(strip=True)]
            elif site_name.lower() == "flipkart":
                nodes = soup.select("div.ZmyHeo, div.t-ZTKy")[:5]
                reviews = [_clean_review_text(n.get_text(" ", strip=True)) for n in nodes if n.get_text(strip=True)]
            elif site_name.lower() == "croma":
                nodes = soup.select(
                    "p.review-text, div.review-content, div.user-review, "
                    "p[class*='review'], div[class*='reviewText'], div[class*='review-content']"
                )[:8]
                reviews = [_clean_review_text(n.get_text(" ", strip=True)) for n in nodes if n.get_text(strip=True)]

        return {
            "avg_rating": rating if rating is None else round(float(rating), 1),
            "reviews": [r for r in reviews if r][:3],
        }
    except Exception:
        return {"avg_rating": None, "reviews": []}
    finally:
        driver.quit()


def _gemini_match(query: str, candidate_name: str, landing_title: str) -> bool | None:
    """
    Optional LLM verifier. Returns:
    - True / False when API is configured and call succeeds
    - None when API is unavailable/fails (caller should fallback to rules)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )

    prompt = (
        "You are validating e-commerce product matching.\n"
        f"User searched for: {query}\n"
        f"Search card title: {candidate_name}\n"
        f"Landing page title/H1: {landing_title}\n\n"
        "Answer with only YES or NO.\n"
        "YES only if this link is the same product family/variant user intended.\n"
        "NO if it is a different brand, different product family, or obvious mismatch."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                ]
            }
        ]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
            text = (
                parsed.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
                .upper()
            )
            if "YES" in text:
                return True
            if "NO" in text:
                return False
            return None
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None


def choose_best_verified_match(query: str, candidates: list[dict], site_name: str) -> dict | None:
    """
    Pick the most reliable candidate by:
    1) title similarity,
    2) landing-page verification similarity,
    3) optional Gemini YES/NO validation.
    """
    if not candidates:
        return None

    scored_candidates = []
    for item in candidates:
        name = item.get("name", "")
        url = item.get("url", "")
        if not name or not url:
            continue

        base_score = _name_similarity(query, name)
        if base_score < 0.25:
            continue
        scored_candidates.append((base_score, item))

    if not scored_candidates:
        print(f"[{site_name} Matcher] no reliable match found for '{query}'")
        return None

    # Evaluate only the top candidates first to reduce noisy validations.
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    shortlist = scored_candidates[:6]

    best = None
    best_score = -1.0

    for base_score, item in shortlist:
        name = item.get("name", "")
        url = item.get("url", "")

        landing_title = _fetch_title_from_url(url)
        if not _passes_variant_guards(query, name, landing_title):
            print(
                f"[{site_name} Matcher] reject '{name}' -> landing='{landing_title[:90]}'"
            )
            continue

        use_landing = not _is_low_quality_landing_title(landing_title)
        landing_score = _name_similarity(query, landing_title) if use_landing else 0.0
        score = (0.45 * base_score) + (0.55 * landing_score if use_landing else 0.0)
        if not use_landing:
            # Keep score reasonable when anti-bot pages prevent reliable landing validation.
            score += 0.08

        # Soft color bonus/penalty
        query_colors = _extract_color_tokens(query)
        landing_colors = _extract_color_tokens(landing_title)
        if query_colors:
            if query_colors.intersection(landing_colors):
                score += 0.05
            else:
                score -= 0.08

        llm_result = _gemini_match(query, name, landing_title)
        if llm_result is True:
            score += 0.20
        elif llm_result is False:
            score -= 0.25

        if score > best_score:
            best = item
            best_score = score

    if best and best_score >= 0.50:
        print(f"[{site_name} Matcher] verified match score={best_score:.2f} -> {best.get('name')}")
        return best

    print(f"[{site_name} Matcher] no reliable match found for '{query}'")
    return None
