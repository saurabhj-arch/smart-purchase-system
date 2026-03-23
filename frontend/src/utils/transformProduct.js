const websiteMap = {
  1: "Amazon",
  2: "Flipkart",
  3: "Croma",
  4: "Reliance Digital",
  5: "TATA CliQ"
};

export const transformProduct = (product) => {
  // New search API format: stores already have { site, price, link }
  if (product.stores) {
    return {
      id: product.id,
      name: product.name,
      image_url: product.image_url || "",
      stores: product.stores,
    };
  }

  // Old products API format: prices have { website (id), price, product_url }
  const prices = product.prices || [];
  return {
    id: product.id,
    name: product.name,
    image_url: product.image_url || "",
    stores: prices.map(p => ({
      site: websiteMap[p.website?.id || p.website] || "Unknown",
      price: parseFloat(p.price),
      link: p.product_url,
    }))
  };
};