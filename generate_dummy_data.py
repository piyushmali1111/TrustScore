import csv
import random
import datetime
import os
import shutil

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

SELLERS_COUNT = 20
REVIEWS_COUNT = 800
ORDERS_COUNT = 2500

SELLER_NAMES = [
    f"Seller_Alpha_{i}" for i in range(SELLERS_COUNT)
]

def random_date(start_year=2024, end_year=2025):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

# Generate Sellers
sellers = []
for i in range(SELLERS_COUNT):
    seller_id = f"S{i+1:03d}"
    sellers.append({
        "seller_id": seller_id,
        "name": SELLER_NAMES[i],
        "join_date": random_date(2022, 2024).isoformat()
    })

with open("data/sellers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["seller_id", "name", "join_date"])
    writer.writeheader()
    writer.writerows(sellers)

# Generate Orders
orders = []
statuses = ["Delivered", "Returned", "Cancelled", "In Transit"]
for i in range(ORDERS_COUNT):
    seller_id = random.choice(sellers)["seller_id"]
    status = random.choices(statuses, weights=[70, 15, 10, 5])[0]
    delivery_days = random.randint(2, 10) if status == "Delivered" else 0
    
    orders.append({
        "order_id": f"O{i+1:05d}",
        "seller_id": seller_id,
        "order_date": random_date(2024, 2024).isoformat(),
        "status": status,
        "delivery_days": delivery_days
    })

with open("data/orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "seller_id", "order_date", "status", "delivery_days"])
    writer.writeheader()
    writer.writerows(orders)

# Generate Reviews
reviews = []
review_texts = [
    "Great product!", "Fast shipping.", "Terrible quality.", "Not as described.",
    "Okay product.", "Will buy again.", "Awful seller.", "Perfect!",
    "Item arrived broken.", "Highly recommended.", "Fake product!", "Authentic quality.",
    "Slow response.", "Quick delivery.", "Scam alert.", "Trustworthy seller."
]

for i in range(REVIEWS_COUNT):
    seller_id = random.choice(sellers)["seller_id"]
    rating = random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 30, 45])[0]
    is_verified = random.choice([True, False])
    
    # Introduce fake/suspicious patterns
    is_fake = False
    if random.random() < 0.1: # 10% chance of fake review burst
        is_fake = True
        review_text = "Best seller ever!!!!" # Repetitive text
        rating = 5
    else:
        review_text = random.choice(review_texts)

    reviews.append({
        "review_id": f"R{i+1:05d}",
        "seller_id": seller_id,
        "rating": rating,
        "review_text": review_text,
        "date": random_date(2024, 2024).isoformat(),
        "is_verified": is_verified,
        "user_id": f"U{random.randint(1, 500):03d}"
    })

with open("data/reviews.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["review_id", "seller_id", "rating", "review_text", "date", "is_verified", "user_id"])
    writer.writeheader()
    writer.writerows(reviews)

print("Data generation complete.")
