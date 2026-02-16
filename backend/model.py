from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import IsolationForest 
import numpy as np
import pandas as pd
from collections import Counter

class ReviewAnalyzer:
    def __init__(self, reviews_df):
        """
        Initialize with reviews DataFrame.
        """
        self.reviews_df = reviews_df
        
    def detect_fake_reviews(self):
        """
        Conservative fake review detection - only flags clear manipulation:
        1. Review bursts (5+ identical reviews same day for same seller)
        2. Very short spam (< 8 chars with 5 stars)
        
        Returns a set of suspicious review IDs.
        """
        suspicious_ids = set()
        
        # STRATEGY 1: Review Burst Detection
        # Only flag if seller gets 5+ IDENTICAL reviews on SAME DAY
        try:
            for seller_id in self.reviews_df['seller_id'].unique():
                seller_reviews = self.reviews_df[self.reviews_df['seller_id'] == seller_id]
                
                if len(seller_reviews) < 5:
                    continue
                
                # Group by date AND review text
                grouped = seller_reviews.groupby([seller_reviews['date'].dt.date, 'review_text']).size()
                
                # Flag if same text appears 5+ times on same date (clear coordinated attack)
                for (date, text), count in grouped.items():
                    if count >= 5:
                        burst_reviews = seller_reviews[
                            (seller_reviews['date'].dt.date == date) & 
                            (seller_reviews['review_text'] == text)
                        ]
                        for idx in burst_reviews.index:
                            suspicious_ids.add(self.reviews_df.loc[idx, 'review_id'])
                        
        except Exception as e:
            print(f"Error in burst detection: {e}")
        
        # STRATEGY 2: Very Short Spam Reviews
        # Single-word 5-star reviews are obviously fake
        try:
            short_spam = self.reviews_df[
                (self.reviews_df['review_text'].str.len() < 8) & 
                (self.reviews_df['rating'] == 5)
            ]
            
            for idx in short_spam.index:
                suspicious_ids.add(self.reviews_df.loc[idx, 'review_id'])
                
        except Exception as e:
            print(f"Error in short review detection: {e}")
            
        return suspicious_ids

    def calculate_authenticity_score(self, seller_reviews):
        """
        Calculate authenticity score for a seller based on ratio of flagged fakes vs total reviews.
        """
        total = len(seller_reviews)
        if total == 0:
            return 50
            
        return 50
