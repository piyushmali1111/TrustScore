from datetime import datetime
import pandas as pd
import numpy as np
from .model import ReviewAnalyzer

class TrustScoreEngine:
    def __init__(self, data):
        self.sellers = data['sellers']
        self.orders = data['orders']
        self.reviews = data['reviews']
        
        # Precompute
        self.analyzer = ReviewAnalyzer(self.reviews)
        self.suspicious_reviews = self.analyzer.detect_fake_reviews()
        self.seller_stats = {}

    def calculate_scores(self):
        scores = []
        for _, seller in self.sellers.iterrows():
            sid = seller['seller_id']
            # Filter Data
            s_orders = self.orders[self.orders['seller_id'] == sid]
            s_reviews = self.reviews[self.reviews['seller_id'] == sid]
            
            # --- 1. DELIVERY SCORE ---
            if len(s_orders) > 0 and 'on_time_delivery' in s_orders.columns:
                # on_time_delivery is assumed to be 1 for On Time, 0 for Late
                delivery_rate = s_orders['on_time_delivery'].mean()
                delivery_score = delivery_rate * 100
            elif len(s_orders) > 0 and 'delivery_days' in s_orders.columns:
                # Fallback to delivery_days if on_time_delivery missing
                delivered = s_orders[s_orders['delivery_days'] > 0] # assume 0 is cancelled
                on_time = delivered[delivered['delivery_days'] <= 5]
                if len(delivered) > 0:
                    delivery_score = (len(on_time) / len(delivered)) * 100
                else:
                    delivery_score = 50
            else:
                delivery_score = 50

            # --- 2. RETURN SCORE ---
            if len(s_orders) > 0 and 'returned' in s_orders.columns:
                return_rate = s_orders['returned'].mean()
                # Lower return rate is better. Score = 100 - (rate * X)
                # If rate is 0.1 (10%), score = 100 - 20 = 80
                # If rate is 0.5 (50%), score = 0
                return_score = max(0, 100 - (return_rate * 200))
            else:
                return_score = 50

            # --- 3. RESPONSE SCORE ---
            if 'avg_response_time_hours' in seller:
                rt = seller['avg_response_time_hours']
                # Lower is better. 0h -> 100, 24h -> 0
                response_score = max(0, 100 - (rt * 4))
            else:
                response_score = 50 # Default

            # --- 4. ACCOUNT AGE SCORE ---
            if 'account_age_days' in seller:
                age_days = seller['account_age_days']
                # 2 years (730 days) = 100 score
                age_score = min(100, (age_days / 730) * 100)
            else:
                age_score = 50

            # --- 5. AUTHENTICITY SCORE ---
            total_reviews = len(s_reviews)
            valid_reviews = s_reviews[~s_reviews['review_id'].isin(self.suspicious_reviews)]
            valid_count = len(valid_reviews)
            
            if total_reviews > 0:
                authenticity_score = (valid_count / total_reviews) * 100
            else:
                authenticity_score = 50

            # --- 6. CONSISTENCY SCORE ---
            if valid_count > 1:
                std_dev = valid_reviews['rating'].std()
                # Lower std dev is better. 0 -> 100. 2 -> 0.
                consistency_score = max(0, 100 - (std_dev * 50))
            else:
                consistency_score = 50

            # --- 7. FINAL TRUST SCORE ---
            trust_score = (
                0.25 * delivery_score +
                0.20 * return_score +
                0.15 * response_score +
                0.20 * authenticity_score +
                0.10 * consistency_score +
                0.10 * age_score
            )

            # --- 8. CONFIDENCE SCORE ---
            tx_count = len(s_orders)
            confidence_score = min(100, (tx_count / 200) * 100) # 200 tx gives full confidence

            # --- 9. RISK LEVEL ---
            if trust_score > 85:
                risk = "Low"
            elif trust_score >= 70:
                risk = "Medium"
            else:
                risk = "High"

            scores.append({
                "seller_id": str(sid),
                "name": seller['seller_name'],
                "trust_score": round(trust_score, 1),
                "confidence_score": round(confidence_score, 1),
                "risk_level": risk,
                "metrics": {
                    "delivery": round(delivery_score, 1),
                    "return_rate_score": round(return_score, 1), 
                    "response": round(response_score, 1),
                    "authenticity": round(authenticity_score, 1),
                    "consistency": round(consistency_score, 1),
                    "age": round(age_score, 1)
                },
                "stats": {
                    "fake_reviews": total_reviews - valid_count,
                    "real_reviews": valid_count
                }
            })
            
        return scores
