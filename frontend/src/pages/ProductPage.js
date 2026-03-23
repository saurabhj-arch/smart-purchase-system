import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

const PLACEHOLDER = "https://placehold.co/300x300?text=No+Image";

function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    // Calls the new endpoint that scrapes all 3 sites for this specific product
    fetch(`http://127.0.0.1:8000/api/search/product/${id}/`)
      .then(res => {
        if (!res.ok) throw new Error("Product not found");
        return res.json();
      })
      .then(data => setProduct(data))
      .catch(() => setError("Failed to load product prices."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>Fetching latest prices...</h2>
      <p>Checking Amazon, Flipkart & Croma for you. This may take a few seconds.</p>
    </div>
  );

  if (error) return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>{error}</h2>
    </div>
  );

  if (!product) return null;

  const prices = product.stores.map(s => s.price);
  const lowest = Math.min(...prices);
  const highest = Math.max(...prices);

  return (
    <div style={{ padding: "20px", maxWidth: "700px", margin: "auto" }}>

      {/* Product image + name */}
      <div style={{ display: "flex", gap: "24px", alignItems: "flex-start", marginBottom: "24px" }}>
        <img
          src={product.image_url || PLACEHOLDER}
          alt={product.name}
          style={{ width: "200px", height: "200px", objectFit: "contain", borderRadius: "8px", border: "1px solid #eee" }}
          onError={(e) => { e.target.src = PLACEHOLDER; }}
        />
        <div>
          <h1 style={{ marginTop: 0 }}>{product.name}</h1>
          <h2>Best Price: ₹{lowest}</h2>
          {highest > lowest && (
            <p>You save ₹{highest - lowest} vs highest listed price</p>
          )}
        </div>
      </div>

      <h3>Price Comparison</h3>

      {product.stores.length === 0 ? (
        <p>No prices found across stores right now. Try again later.</p>
      ) : (
        <div className="priceList">
          {product.stores.map((s, i) => {
            const isBest = s.price === lowest;
            return (
              <div key={i} className={`priceCard ${isBest ? "bestPrice" : ""}`}>
                <div>
                  <h4 style={{ margin: 0 }}>{s.site}</h4>
                  <p className="price">₹{s.price}</p>
                  {isBest && <span className="badge">Best Deal</span>}
                </div>
                <a href={s.link} target="_blank" rel="noreferrer">
                  <button className="buyBtn">Buy</button>
                </a>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}

export default ProductPage;