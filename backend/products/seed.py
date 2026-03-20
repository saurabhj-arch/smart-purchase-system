from products.models import Product, Website, Price

# Create websites
amazon, _ = Website.objects.get_or_create(name="Amazon", base_url="https://amazon.in")
flipkart, _ = Website.objects.get_or_create(name="Flipkart", base_url="https://flipkart.com")
croma, _ = Website.objects.get_or_create(name="Croma", base_url="https://croma.com")
reliance, _ = Website.objects.get_or_create(name="Reliance Digital", base_url="https://reliancedigital.in")
tatacliq, _ = Website.objects.get_or_create(name="Tata CLiQ", base_url="https://tatacliq.com")

# Helper
def add_product(name, desc, prices):
    product, _ = Product.objects.get_or_create(
        name=name,
        defaults={"description": desc}
    )

    for site, price, url in prices:
        Price.objects.update_or_create(
            product=product,
            website=site,
            defaults={
                "price": str(price),
                "product_url": url
            }
        )

# ---------------- PRODUCTS ----------------

products_data = [

    ("iPhone 15", "Apple smartphone", [
        (amazon, "79900.00", "https://www.amazon.in/dp/B0CHX2F5QT"),
        (flipkart, "78499.00", "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"),
        (croma, "78900.00", "https://www.croma.com/apple-iphone-15-128gb-black-/p/300684"),
        (reliance, "79200.00", "https://www.reliancedigital.in/apple-iphone-15-128-gb-black-/p/493839204"),
        (tatacliq, "78850.00", "https://www.tatacliq.com/apple-iphone-15-128-gb/p-mp000000021077")
    ]),

    ("Samsung Galaxy S23", "Samsung flagship phone", [
        (amazon, "69900.00", "https://www.amazon.in/dp/B0BSX6ZQYV"),
        (flipkart, "70999.00", "https://www.flipkart.com/samsung-galaxy-s23-5g-phantom-black-128-gb/p/itmcb8f0c5c3a4d3"),
        (croma, "68999.00", "https://www.croma.com/samsung-galaxy-s23-5g-128gb/p/273733"),
        (reliance, "69200.00", "https://www.reliancedigital.in/samsung-galaxy-s23-5g-128-gb/p/493666090"),
        (tatacliq, "69500.00", "https://www.tatacliq.com/samsung-galaxy-s23-5g/p-mp000000020999")
    ]),

    ("MacBook Air M2", "Apple laptop", [
        (amazon, "109900.00", "https://www.amazon.in/dp/B0B3C2R9G2"),
        (flipkart, "108999.00", "https://www.flipkart.com/apple-macbook-air-m2-8-gb-256-gb-ssd-macos-monterey-mlxy3hn-a/p/itm5b7c5e7c8c7e3"),
        (croma, "110500.00", "https://www.croma.com/apple-macbook-air-m2-chip-13-inch/p/261964"),
        (reliance, "107999.00", "https://www.reliancedigital.in/apple-macbook-air-m2-8gb-256gb/p/492850583"),
        (tatacliq, "108500.00", "https://www.tatacliq.com/apple-macbook-air-m2/p-mp000000020888")
    ]),

    ("Sony WH-1000XM5 Headphones", "Noise cancelling headphones", [
        (amazon, "26990.00", "https://www.amazon.in/dp/B09XS7JWHH"),
        (flipkart, "27999.00", "https://www.flipkart.com/sony-wh-1000xm5-noise-cancellation-headphones/p/itm123abc"),
        (croma, "26499.00", "https://www.croma.com/sony-wh-1000xm5/p/273111"),
        (reliance, "26800.00", "https://www.reliancedigital.in/sony-headphones/p/493666222"),
        (tatacliq, "27200.00", "https://www.tatacliq.com/sony-headphones/p-mp000000021222")
    ]),

    ("iPad Air", "Apple tablet", [
        (amazon, "55900.00", "https://www.amazon.in/dp/B0BJ7VZC9R"),
        (flipkart, "54999.00", "https://www.flipkart.com/apple-ipad-air-5th-gen/p/itm456def"),
        (croma, "55200.00", "https://www.croma.com/apple-ipad-air/p/272333"),
        (reliance, "54500.00", "https://www.reliancedigital.in/apple-ipad-air/p/493777111"),
        (tatacliq, "55300.00", "https://www.tatacliq.com/apple-ipad-air/p-mp000000021333")
    ]),

    ("Nike Running Shoes", "Running shoes", [
        (amazon, "3999.00", "https://www.amazon.in/dp/B09NQSHOE"),
        (flipkart, "3899.00", "https://www.flipkart.com/nike-running-shoes/p/itmshoe123"),
        (croma, "3950.00", "https://www.croma.com/shoes/p/272111"),
        (reliance, "3799.00", "https://www.reliancedigital.in/shoes/p/493111111"),
        (tatacliq, "3849.00", "https://www.tatacliq.com/nike-shoes/p-mp000000021444")
    ]),

    ("Office Chair", "Ergonomic chair", [
        (amazon, "6999.00", "https://www.amazon.in/dp/B09CHAIR123"),
        (flipkart, "6799.00", "https://www.flipkart.com/office-chair/p/itmchair123"),
        (croma, "6899.00", "https://www.croma.com/chair/p/272222"),
        (reliance, "6599.00", "https://www.reliancedigital.in/chair/p/493222222"),
        (tatacliq, "6700.00", "https://www.tatacliq.com/chair/p-mp000000021555")
    ]),

    ("Wooden Study Table", "Study desk", [
        (amazon, "8999.00", "https://www.amazon.in/dp/B09TABLE123"),
        (flipkart, "8799.00", "https://www.flipkart.com/study-table/p/itmtable123"),
        (croma, "8899.00", "https://www.croma.com/table/p/272333"),
        (reliance, "8499.00", "https://www.reliancedigital.in/table/p/493333333"),
        (tatacliq, "8600.00", "https://www.tatacliq.com/table/p-mp000000021666")
    ]),

    ("Mixer Grinder", "Kitchen appliance", [
        (amazon, "4999.00", "https://www.amazon.in/dp/B09MIXER123"),
        (flipkart, "4899.00", "https://www.flipkart.com/mixer-grinder/p/itmmixer123"),
        (croma, "4799.00", "https://www.croma.com/mixer/p/272444"),
        (reliance, "4699.00", "https://www.reliancedigital.in/mixer/p/493444444"),
        (tatacliq, "4850.00", "https://www.tatacliq.com/mixer/p-mp000000021777")
    ]),
]

# Insert all
for name, desc, prices in products_data:
    add_product(name, desc, prices)

print("All demo data added successfully!")