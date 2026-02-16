import csv
import random
import datetime
import os

# Configuration
SELLERS_COUNT = 20
REVIEWS_COUNT = 800
ORDERS_COUNT = 2500
FAKE_REVIEW_PERCENTAGE = 0.12  # 12% of reviews will be fake

SELLER_NAMES = [f"Seller_{i+1}" for i in range(SELLERS_COUNT)]

def random_date(start_year=2023, end_year=2024):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

def random_date_in_range(start_date, days_range=3):
    """Generate a date within X days of start_date (for burst detection)"""
    return start_date + datetime.timedelta(days=random.randint(0, days_range))

# Generate Sellers with varying quality tiers
sellers = []
sellers_with_fake_reviews = random.sample(range(SELLERS_COUNT), k=6)  # 6 sellers will have fake reviews

for i in range(SELLERS_COUNT):
    seller_id = i + 1
    
    # Create 3 tiers: Good (40%), Average (40%), Poor (20%)
    tier = random.choices(['good', 'average', 'poor'], weights=[40, 40, 20])[0]
    
    if tier == 'good':
        account_age_days = random.randint(800, 2000)
        avg_response_time_hours = round(random.uniform(1, 8), 2)
    elif tier == 'average':
        account_age_days = random.randint(400, 800)
        avg_response_time_hours = round(random.uniform(8, 20), 2)
    else:
        account_age_days = random.randint(100, 400)
        avg_response_time_hours = round(random.uniform(20, 48), 2)
    
    sellers.append({
        "seller_id": seller_id,
        "seller_name": SELLER_NAMES[i],
        "account_age_days": account_age_days,
        "avg_response_time_hours": avg_response_time_hours,
        "tier": tier,
        "has_fake_reviews": i in sellers_with_fake_reviews
    })

# Write sellers.csv
with open("data/sellers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["seller_id", "seller_name", "account_age_days", "avg_response_time_hours"])
    writer.writeheader()
    for seller in sellers:
        writer.writerow({
            "seller_id": seller["seller_id"],
            "seller_name": seller["seller_name"],
            "account_age_days": seller["account_age_days"],
            "avg_response_time_hours": seller["avg_response_time_hours"]
        })

# Generate Orders
orders = []
for i in range(ORDERS_COUNT):
    seller = random.choice(sellers)
    seller_tier = seller["tier"]
    
    order_date = random_date(2023, 2024)
    
    if seller_tier == 'good':
        on_time = 1 if random.random() < 0.90 else 0
        returned = 1 if random.random() < 0.05 else 0
    elif seller_tier == 'average':
        on_time = 1 if random.random() < 0.70 else 0
        returned = 1 if random.random() < 0.15 else 0
    else:
        on_time = 1 if random.random() < 0.40 else 0
        returned = 1 if random.random() < 0.30 else 0
    
    if on_time:
        delivery_days = random.randint(2, 5)
    else:
        delivery_days = random.randint(6, 15)
    
    delivered_date = order_date + datetime.timedelta(days=delivery_days)
    
    orders.append({
        "order_id": i + 1,
        "seller_id": seller["seller_id"],
        "order_date": order_date.isoformat(),
        "delivered_date": delivered_date.isoformat(),
        "delivery_days": delivery_days,
        "on_time_delivery": on_time,
        "returned": returned
    })

# Write orders.csv
with open("data/orders.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "seller_id", "order_date", "delivered_date", "delivery_days", "on_time_delivery", "returned"])
    writer.writeheader()
    writer.writerows(orders)

# Generate Reviews with FAKE patterns
review_texts = {
    'good': [
        "Excellent product and fast delivery.",
        "Very good quality, satisfied.",
        "Highly recommend this seller.",
        "Great experience overall.",
        "Fast shipping and good packaging.",
        "Product exactly as described.",
        "Will definitely buy again.",
        "Outstanding service and quality."
    ],
    'average': [
        "Average experience, could be better.",
        "Product is okay, delivery was slow.",
        "Decent quality for the price.",
        "Acceptable service.",
        "Nothing special but not bad.",
        "Met my expectations.",
        "Fair product, average shipping."
    ],
    'poor': [
        "Poor packaging and slow response.",
        "Not satisfied with the quality.",
        "Delivery was very late.",
        "Would not recommend.",
        "Disappointing experience.",
        "Product quality below expectations.",
        "Slow customer service."
    ]
}

# Fake review patterns
fake_review_patterns = [
    # Pattern 1: Generic 5-star spam
    "Amazing product! Best seller!",
    "Excellent! Highly recommended!",
    "Perfect! Will buy again!",
    "Great seller! Fast shipping!",
    
    # Pattern 2: Very short suspicious
    "Good",
    "Nice",
    "Best",
    "Perfect",
    
    # Pattern 3: Overly enthusiastic
    "BEST PRODUCT EVER!!! AMAZING!!!",
    "SUPER GREAT SELLER!!! BUY NOW!!!",
    
    # Pattern 4: Copy-paste duplicates
    "This is the best product I have ever purchased and I highly recommend it to everyone.",
    "Outstanding quality and amazing service from this seller.",
]

reviews = []
fake_reviews_count = 0
target_fake_count = int(REVIEWS_COUNT * FAKE_REVIEW_PERCENTAGE)

for i in range(REVIEWS_COUNT):
    seller = random.choice(sellers)
    seller_tier = seller["tier"]
    
    # Decide if this should be a fake review
    is_fake = False
    if seller["has_fake_reviews"] and fake_reviews_count < target_fake_count:
        # 30% chance of making it fake if seller is flagged for fakes
        if random.random() < 0.3:
            is_fake = True
            fake_reviews_count += 1
    
    review_date = random_date(2023, 2024)
    
    if is_fake:
        # FAKE REVIEW PATTERNS
        pattern = random.choice(['duplicate', 'generic', 'burst', 'suspicious_rating'])
        
        if pattern == 'duplicate':
            # Use same review text multiple times
            review_text = random.choice(fake_review_patterns[8:10])
            rating = 5  # Always 5 stars
            
        elif pattern == 'generic':
            # Very short, generic text
            review_text = random.choice(fake_review_patterns[4:8])
            rating = 5
            
        elif pattern == 'burst':
            # Part of a review burst (multiple reviews same day)
            review_text = random.choice(fake_review_patterns[0:4])
            rating = 5
            # Set date to be clustered (handled in burst generation)
            
        else:  # suspicious_rating
            # Overly enthusiastic
            review_text = random.choice(fake_review_patterns[6:8])
            rating = 5
    else:
        # GENUINE REVIEW
        if seller_tier == 'good':
            rating = random.choices([3, 4, 5], weights=[10, 30, 60])[0]
            review_text = random.choice(review_texts['good'])
        elif seller_tier == 'average':
            rating = random.choices([2, 3, 4], weights=[20, 50, 30])[0]
            review_text = random.choice(review_texts['average'])
        else:
            rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
            review_text = random.choice(review_texts['poor'])
    
    reviews.append({
        "review_id": i + 1,
        "seller_id": seller["seller_id"],
        "rating": rating,
        "review_text": review_text,
        "review_date": review_date.isoformat(),
        "is_fake_label": is_fake  # Ground truth label (not in CSV, just for tracking)
    })

# Add review BURSTS for some sellers with fake reviews
burst_reviews_added = 0
for seller in sellers:
    if seller["has_fake_reviews"] and burst_reviews_added < 20:
        # Add a burst of 5-8 reviews on same day
        burst_size = random.randint(5, 8)
        burst_date = random_date(2023, 2024)
        burst_text = random.choice(fake_review_patterns[0:4])
        
        for j in range(burst_size):
            reviews.append({
                "review_id": len(reviews) + 1,
                "seller_id": seller["seller_id"],
                "rating": 5,
                "review_text": burst_text,
                "review_date": burst_date.isoformat(),
                "is_fake_label": True
            })
            burst_reviews_added += 1
            fake_reviews_count += 1

# Write reviews.csv
with open("data/reviews.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["review_id", "seller_id", "rating", "review_text", "review_date"])
    writer.writeheader()
    for review in reviews:
        writer.writerow({
            "review_id": review["review_id"],
            "seller_id": review["seller_id"],
            "rating": review["rating"],
            "review_text": review["review_text"],
            "review_date": review["review_date"]
        })

print(f"✅ Generated dataset with FAKE REVIEWS:")
print(f"   - {SELLERS_COUNT} sellers")
print(f"   - {ORDERS_COUNT} orders")
print(f"   - {len(reviews)} reviews ({fake_reviews_count} fake, {len(reviews) - fake_reviews_count} genuine)")
print(f"   - Fake review percentage: {fake_reviews_count/len(reviews)*100:.1f}%")
print(f"\nFake review patterns included:")
print(f"   - Review bursts (same day, same text)")
print(f"   - Duplicate generic reviews")
print(f"   - Very short suspicious text")
print(f"   - Overly enthusiastic spam")
