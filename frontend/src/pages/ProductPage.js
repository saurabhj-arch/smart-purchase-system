import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getProductPrices } from "../utils/api";
import "../styles/ProductPage.css";

const PLACEHOLDER = "https://placehold.co/300x300?text=No+Image";

function renderStars(rating) {
  if (rating == null) return "No rating";
  const full = Math.round(rating);
  const filled = "★".repeat(Math.max(0, Math.min(5, full)));
  const empty = "☆".repeat(Math.max(0, 5 - filled.length));
  return `${filled}${empty}`;
}

function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    getProductPrices(id)
      .then(data => setProduct(data))
      .catch((err) => {
        console.error("ProductPage fetch error:", err);
        setError(err.message || "Failed to load product prices.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="productPageState">
      <h2>Fetching latest prices...</h2>
      <p>Checking Amazon, Flipkart & Croma for you. This may take a few seconds.</p>
    </div>
  );

  if (error) return (
    <div className="productPageState productPageStateError">
      <h2>{error}</h2>
    </div>
  );

  if (!product) return null;

  const availableStores = product.stores.filter((s) => s.available !== false && s.price != null);
  const prices = availableStores.map((s) => s.price);
  const lowest = prices.length ? Math.min(...prices) : null;
  const highest = prices.length ? Math.max(...prices) : null;
  const ratings = product.stores
    .filter((s) => s.available !== false && s.avg_rating != null)
    .map((s) => Number(s.avg_rating));
  const overallRating = ratings.length
    ? (ratings.reduce((sum, value) => sum + value, 0) / ratings.length).toFixed(1)
    : null;
  const lastUpdated = product.last_updated
    ? new Date(product.last_updated).toLocaleString()
    : null;
  const reviewItems = product.stores.flatMap((s) =>
    (s.reviews || []).map((text, idx) => ({
      id: `${s.site}-${idx}`,
      site: s.site,
      text,
    }))
  );

  return (
    <div className="productPageShell">
      <div className="productHeroCard">
        <img
          src={product.image_url || PLACEHOLDER}
          alt={product.name}
          className="productHeroImage"
          onError={(e) => { e.target.src = PLACEHOLDER; }}
        />
        <div className="productHeroInfo">
          <h1>{product.name}</h1>
          {lowest !== null ? (
            <h2 className="productBestPrice">Best Price: ₹{lowest}</h2>
          ) : (
            <h2 className="productNoPrice">No exact-match price found</h2>
          )}
          {lowest !== null && highest > lowest && (
            <p className="productSavings">You save ₹{highest - lowest} vs highest listed price</p>
          )}
          <p className="productMetaLine">
            Overall Rating: {overallRating ? `${overallRating}/5` : "No overall rating yet"}
          </p>
          <p className="productMetaSubline">
            Last updated: {lastUpdated || "Unknown"}
          </p>
        </div>
      </div>

      <h3 className="productSectionTitle">Price Comparison</h3>

      {product.stores.length === 0 ? (
        <p className="productEmptyText">No prices found across stores right now. Try again later.</p>
      ) : (
        <div className="productSectionList">
          {product.stores.map((s, i) => {
            const isAvailable = s.available !== false && s.price != null;
            const isBest = isAvailable && lowest !== null && s.price === lowest;
            return (
              <div key={i} className={`productStoreCard ${isBest ? "productStoreCardBest" : ""}`}>
                <div className="productStoreInfo">
                  <h4>{s.site}</h4>
                  {isAvailable ? (
                    <>
                      <p className="productStorePrice">₹{s.price}</p>
                      {isBest && <span className="productBadge">Best Deal</span>}
                    </>
                  ) : (
                    <p className="productStoreUnavailable">
                      {s.message || "This specific product is not available on this website."}
                    </p>
                  )}
                </div>
                {isAvailable && s.link ? (
                  <a href={s.link} target="_blank" rel="noreferrer">
                    <button className="productActionBtn">Buy Now</button>
                  </a>
                ) : (
                  <button className="productActionBtn productActionBtnDisabled" disabled>
                    Unavailable
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      <h3 className="productSectionTitle">Average Rating by Platform</h3>
      <div className="productSectionList">
        {product.stores.map((s, i) => (
          <div key={`rating-${i}`} className="productStoreCard">
            <div className="productStoreInfo">
              <h4>{s.site}</h4>
              {s.available !== false ? (
                <>
                  <p className="productStorePrice">
                    {s.avg_rating != null ? `${s.avg_rating}/5` : "No rating"}
                  </p>
                  <p className="productRatingStars">{renderStars(s.avg_rating)}</p>
                </>
              ) : (
                <p className="productStoreUnavailable">No rating</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <h3 className="productSectionTitle">Reviews Across Platforms</h3>
      {reviewItems.length === 0 ? (
        <p className="productEmptyText">
          No review snippets available right now for this exact variant.
        </p>
      ) : (
        <div className="productSectionList">
          {reviewItems.map((r) => (
            <div key={r.id} className="productStoreCard">
              <div className="productStoreInfo">
                <h4>{r.site}</h4>
                <p className="productReviewText">"{r.text}"</p>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

export default ProductPage;