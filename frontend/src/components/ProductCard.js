import { useNavigate } from "react-router-dom";

const PLACEHOLDER = "https://placehold.co/300x300?text=No+Image";

function ProductCard({ product }) {
  const nav = useNavigate();

  if (!product.stores || product.stores.length === 0) {
    return null;
  }

  const validStores = product.stores.filter(
    (s) => typeof s.price === "number" && Number.isFinite(s.price)
  );
  const lowestPrice = validStores.length
    ? Math.min(...validStores.map((s) => s.price))
    : null;
  const bestStore = validStores.find((s) => s.price === lowestPrice) || product.stores[0];

  return (
    <div
      className="card"
      onClick={() => nav("/product/" + product.id)}
    >
      <img
        src={product.image_url || PLACEHOLDER}
        alt={product.name}
        className="cardImage"
        onError={(e) => { e.target.src = PLACEHOLDER; }} // fallback if image fails to load
      />

      <h3>{product.name}</h3>

      <div className="priceBox">
        {lowestPrice !== null ? `From ₹${lowestPrice}` : "Price unavailable"}
      </div>

      <p className="bestDealText">
        Best deal on {bestStore?.site || "unknown"}
      </p>
    </div>
  );
}

export default ProductCard;