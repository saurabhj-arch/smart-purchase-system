const websiteMap = {
  1: "Amazon",
  2: "Flipkart",
  3: "Croma",
  4: "Reliance Digtal",
  5: "TATA CliQ"
};

export const transformProduct = (product) => {
  const prices = product.prices || []; // ✅ fix

  return {
    id: product.id,
    name: product.name,
    stores: prices.map(p => ({
      site: websiteMap[p.website] || "Unknown",
      price: parseFloat(p.price),
      link: p.product_url
    }))
  };
};