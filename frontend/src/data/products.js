const baseStores = [
  { site: "Amazon", rating: 4.6, base: "https://www.amazon.in/s?k=" },
  { site: "Flipkart", rating: 4.5, base: "https://www.flipkart.com/search?q=" },
  { site: "Croma", rating: 4.4, base: "https://www.croma.com/search/?text=" },
  { site: "Reliance Digital", rating: 4.3, base: "https://www.reliancedigital.in/search?q=" },
  { site: "Tata CLiQ", rating: 4.2, base: "https://www.tatacliq.com/search/?searchCategory=all&text=" },
  { site: "Vijay Sales", rating: 4.4, base: "https://www.vijaysales.com/search/" },
  { site: "Snapdeal", rating: 4.1, base: "https://www.snapdeal.com/search?keyword=" }
];

const generateStores = (basePrice, productName) => {
  const query = productName.replace(/ /g, "+");

  return baseStores.map((s, i) => ({
    site: s.site,
    rating: s.rating,
    price: basePrice + (i * 500 - 1500),
    link: s.base + query
  }));
};

const products = [

  { name:"iPhone 15", category:"mobiles", image:"https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400", rating:4.7, reviews:2345, stores:generateStores(75000, "iPhone 15") },

  { name:"Samsung S23", category:"mobiles", image:"https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400", rating:4.5, reviews:1820, stores:generateStores(70000, "Samsung S23") },

  { name:"OnePlus 11", category:"mobiles", image:"https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400", rating:4.6, reviews:2100, stores:generateStores(65000, "OnePlus 11") },

  { name:"MacBook Air M2", category:"laptops", image:"https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400", rating:4.8, reviews:1290, stores:generateStores(110000, "MacBook Air M2") },

  { name:"Dell XPS 13", category:"laptops", image:"https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400", rating:4.6, reviews:870, stores:generateStores(100000, "Dell XPS 13") },

  { name:"HP Pavilion Laptop", category:"laptops", image:"https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=400", rating:4.4, reviews:980, stores:generateStores(60000, "HP Pavilion Laptop") },

  { name:"Sony Headphones", category:"audio", image:"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", rating:4.6, reviews:980, stores:generateStores(9000, "Sony Headphones") },

  { name:"Boat Headphones", category:"audio", image:"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", rating:4.3, reviews:1700, stores:generateStores(2500, "Boat Headphones") },

  { name:"Apple Watch", category:"wearables", image:"https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400", rating:4.7, reviews:1540, stores:generateStores(38000, "Apple Watch") },

  { name:"Noise Smartwatch", category:"wearables", image:"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400", rating:4.2, reviews:1500, stores:generateStores(5000, "Noise Smartwatch") },

  { name:"iPad Air", category:"tablets", image:"https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400", rating:4.7, reviews:1120, stores:generateStores(56000, "iPad Air") },

  { name:"Samsung Tablet", category:"tablets", image:"https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400", rating:4.5, reviews:890, stores:generateStores(30000, "Samsung Tablet") },

  { name:"Canon DSLR", category:"accessories", image:"https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400", rating:4.5, reviews:760, stores:generateStores(45000, "Canon DSLR Camera") },

  { name:"Logitech Mouse", category:"accessories", image:"https://images.unsplash.com/photo-1527814050087-3793815479db?w=400", rating:4.4, reviews:2210, stores:generateStores(1500, "Logitech Mouse") },

  { name:"Gaming Keyboard", category:"accessories", image:"https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=400", rating:4.5, reviews:1340, stores:generateStores(4000, "Gaming Keyboard") }

];

export default products;