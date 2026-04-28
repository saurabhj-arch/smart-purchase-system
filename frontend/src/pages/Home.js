import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import { transformProduct } from "../utils/transformProduct";
import { searchProducts, getAllProducts } from "../utils/api";

function Home() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Product categories for better organization
  const categories = [
    { id: "all", name: "All Products", icon: "🛍️" },
    { id: "electronics", name: "Electronics", icon: "📱" },
    { id: "books", name: "Books", icon: "📚" },
    { id: "clothing", name: "Clothing", icon: "👕" },
    { id: "home", name: "Home & Kitchen", icon: "🏠" },
    { id: "sports", name: "Sports", icon: "⚽" },
  ];

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
    getAllProducts()
      .then(data => {
        const transformed = data.map(transformProduct);
        setProducts(transformed);
      })
      .catch(err => setError(err.message || "Failed to load products."))
      .finally(() => setLoading(false));
  };

  const handleSearch = async (q) => {
    setLoading(true);
    setError("");
    setProducts([]);

    try {
      const data = await searchProducts(q);
      // Search API already returns { id, name, image_url, stores: [{site, price, link}] }
      // No transformation needed — just pass directly to ProductCard
      setProducts(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Filter products based on selected category
  const filteredProducts = products.filter(product => {
    if (selectedCategory === "all") return true;

    // Simple category detection based on product name
    const name = product.name.toLowerCase();
    switch (selectedCategory) {
      case "electronics":
        return name.includes("phone") || name.includes("laptop") || name.includes("tv") ||
               name.includes("headphone") || name.includes("charger") || name.includes("camera");
      case "books":
        return name.includes("book") || name.includes("novel") || name.includes("textbook");
      case "clothing":
        return name.includes("shirt") || name.includes("jeans") || name.includes("dress") ||
               name.includes("shoes") || name.includes("jacket");
      case "home":
        return name.includes("kitchen") || name.includes("home") || name.includes("appliance") ||
               name.includes("furniture") || name.includes("decor");
      case "sports":
        return name.includes("ball") || name.includes("equipment") || name.includes("fitness") ||
               name.includes("sport") || name.includes("gym");
      default:
        return true;
    }
  });

  return (
    <div className="homeLayout">
      <div className="homeContent">

        <div className="heroSection">
          {query ? (
            <>
              <h1>Search Results</h1>
              <p>Found {filteredProducts.length} products for "<strong>{query}</strong>"</p>
            </>
          ) : (
            <>
              <h1>Smart Shopping Made Easy</h1>
              <p>Compare prices across Amazon, Flipkart & Croma to find the best deals instantly</p>
            </>
          )}
        </div>

        {/* Category Filter - Only show when not searching */}
        {!query && !loading && (
          <div className="categoryFilter">
            <div className="categoryGrid">
              {categories.map(category => (
                <button
                  key={category.id}
                  className={`categoryBtn ${selectedCategory === category.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <span className="categoryIcon">{category.icon}</span>
                  <span className="categoryName">{category.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

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
              <h2>
                {query
                  ? `Results for "${query}"`
                  : selectedCategory === "all"
                    ? "All Products"
                    : categories.find(c => c.id === selectedCategory)?.name || "Products"
                }
              </h2>
              <span>{filteredProducts.length} products</span>
            </div>

            <div className="grid">
              {filteredProducts.length > 0 ? (
                filteredProducts.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))
              ) : (
                <div className="emptyState">
                  <h3>No products found</h3>
                  <p>Try adjusting your search or category filter.</p>
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