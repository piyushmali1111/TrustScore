from backend.data_loader import load_data
from backend.model import ReviewAnalyzer
import pandas as pd

print("Loading data...")
data = load_data()
reviews = data['reviews']

print(f"Total reviews: {len(reviews)}")

analyzer = ReviewAnalyzer(reviews)
print("Running detection...")

# Hack to inspect internal steps of detect_fake_reviews if we were debugging interactively,
# but here we'll just run it and see the result.
suspicious = analyzer.detect_fake_reviews()

print(f"Suspicious reviews found: {len(suspicious)}")
print(f"Percentage suspicious: {len(suspicious)/len(reviews)*100:.2f}%")

# Let's verify why.
# Check duplicates
print("\n--- Similarity Check Pre-analysis ---")
print("Top 5 most frequent review texts:")
print(reviews['review_text'].value_counts().head(5))

# Check Isolation Forest inputs
features = pd.DataFrame()
features['rating'] = reviews['rating']
features['length'] = reviews['review_text'].fillna("").apply(len)
print("\n--- Anomaly Features Stats ---")
print(features.describe())
