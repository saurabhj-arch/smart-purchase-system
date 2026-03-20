import { useEffect, useState } from "react";
import ProductCard from "../components/ProductCard";
import { transformProduct } from "../utils/transformProduct";

function Home() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/products/")
      .then(res => res.json())
      .then(data => {
        const transformed = data.map(transformProduct);
        setProducts(transformed);
      });
  }, []);

  return (
    <div className="homeLayout">

      <div className="homeContent">
        <div className="heroSection">
          <h1>Products</h1>
          <p>Compare prices across the Web</p>
        </div>

        <div className="sectionHeader">
          <h2>All Products</h2>
          <span>{products.length} products</span>
        </div>

        <div className="grid">
          {products.length > 0 ? (
            products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))
          ) : (
            <div className="emptyState">
              <h3>No products found</h3>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}

export default Home;