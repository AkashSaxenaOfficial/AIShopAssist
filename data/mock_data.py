products = [
    {
        "id": 1,
        "name": "Premium Wireless Headphones",
        "price": 199.99,
        "image": "https://placekitten.com/200/200",  # Placeholder image
        "description": "High-quality wireless headphones with noise cancellation",
        "category": "Electronics"
    },
    {
        "id": 2,
        "name": "Smart Watch Pro",
        "price": 299.99,
        "image": "https://placekitten.com/201/201",
        "description": "Advanced smartwatch with health tracking features",
        "category": "Electronics"
    },
    # Add more products as needed
]

def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)

def get_products_by_category(category=None):
    if category:
        return [p for p in products if p["category"].lower() == category.lower()]
    return products
