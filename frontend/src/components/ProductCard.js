import { useNavigate } from "react-router-dom";

const PLACEHOLDER = "https://placehold.co/300x300?text=No+Image";

function ProductCard({ product }) {
  const nav = useNavigate();

  if (!product.stores || product.stores.length === 0) {
    return null;
  }

  const lowestPrice = Math.min(...product.stores.map((s) => s.price));
  const bestStore = product.stores.find((s) => s.price === lowestPrice);

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

      <div className="priceBox">From ₹{lowestPrice}</div>

      <p className="bestDealText">
        Best deal on {bestStore.site}
      </p>
    </div>
  );
}

export default ProductCard;