import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import { transformProduct } from "../utils/transformProduct";

function Home() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (query) {
      // User has searched — call the scraping endpoint
      handleSearch(query);
    } else {
      // No search query — load all products from DB as before
      loadAllProducts();
    }
  }, [query]); // Re-runs whenever the search query in the URL changes

  const loadAllProducts = () => {
    setLoading(true);
    setError("");
    fetch("http://127.0.0.1:8000/api/products/")
      .then(res => res.json())
      .then(data => {
        const transformed = data.map(transformProduct);
        setProducts(transformed);
      })
      .catch(() => setError("Failed to load products."))
      .finally(() => setLoading(false));
  };

  const handleSearch = async (q) => {
    setLoading(true);
    setError("");
    setProducts([]);

    try {
      const token = localStorage.getItem("access");

      const headers = { "Content-Type": "application/json" };
      // Attach token if logged in — enables caching on the backend
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await fetch("http://127.0.0.1:8000/api/search/", {
        method: "POST",
        headers,
        body: JSON.stringify({ query: q }),
      });

      if (!res.ok) {
        const err = await res.json();
        setError(err.error || "No results found.");
        return;
      }

      const data = await res.json();

      // Search API already returns { id, name, image_url, stores: [{site, price, link}] }
      // No transformation needed — just pass directly to ProductCard
      setProducts(data);

    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="homeLayout">
      <div className="homeContent">

        <div className="heroSection">
          {query ? (
            <>
              <h1>Search Results</h1>
              <p>Showing results for "<strong>{query}</strong>"</p>
            </>
          ) : (
            <>
              <h1>Products</h1>
              <p>Compare prices across the Web</p>
            </>
          )}
        </div>

        {/* Loading state */}
        {loading && (
          <div className="emptyState">
            <h3>
              {query
                ? "Searching across Amazon, Flipkart & Croma..."
                : "Loading products..."}
            </h3>
            <p>This may take a few seconds.</p>
          </div>
        )}

        {/* Error state */}
        {!loading && error && (
          <div className="emptyState">
            <h3>{error}</h3>
          </div>
        )}

        {/* Results */}
        {!loading && !error && (
          <>
            <div className="sectionHeader">
              <h2>{query ? "Results" : "All Products"}</h2>
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
          </>
        )}

      </div>
    </div>
  );
}

export default Home;