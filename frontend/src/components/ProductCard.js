import { useNavigate } from "react-router-dom";

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
      onClick={() => {
  console.log("Clicked product ID:", product.id);
  nav("/product/" + product.id);
}}
    >
      <h3>{product.name}</h3>

      <div className="priceBox">From ₹{lowestPrice}</div>

      <p className="bestDealText">
        Best deal on {bestStore.site}
      </p>
    </div>
  );
}

export default ProductCard;