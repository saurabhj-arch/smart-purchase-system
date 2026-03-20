import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { transformProduct } from "../utils/transformProduct";

function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/products/${id}/`)
      .then(res => res.json())
      .then(data => {
  console.log("API response:", data);
  setProduct(transformProduct(data));
});
  }, [id]);

  if (!product) return <div>Loading...</div>;

  const prices = product.stores.map(s => s.price);
  const lowest = Math.min(...prices);
  const highest = Math.max(...prices);

  return (
    <div style={{ padding: "20px", maxWidth: "700px", margin: "auto" }}>
    <h1>{product.name}</h1>

    <div style={{ margin: "15px 0" }}>
      <h2>Best Price: ₹{lowest}</h2>
      <p>You save ₹{highest - lowest}</p>
    </div>

    <h3>Price Comparison</h3>

    <div className="priceList">
      {product.stores.map((s, i) => {
        const isBest = s.price === lowest;

        return (
          <div
            key={i}
            className={`priceCard ${isBest ? "bestPrice" : ""}`}
          >
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
  </div>
  );
}

export default ProductPage;