from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.data_loader import load_data
from backend.trust_engine import TrustScoreEngine
from backend.supabase_client import get_supabase
import os
import bcrypt
from typing import Optional

app = FastAPI(title="TrustScore – Digital Trust Assurance System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_scores_data():
    """Load data and compute scores"""
    data = load_data()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to load data from database")
    
    engine = TrustScoreEngine(data)
    seller_scores = engine.calculate_scores()
    return seller_scores, data

@app.post("/api/signup")
def signup(payload: dict = Body(...)):
    supabase = get_supabase()
    username = payload.get("username")
    email = payload.get("email")
    password = payload.get("password")
    role = payload.get("role", "seller")
    seller_id = payload.get("seller_id")

    # Handle empty seller_id (prevent FK violation)
    if not seller_id:
        seller_id = None

    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        res = supabase.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "seller_id": seller_id
        }).execute()
        return {"message": "User created successfully", "user": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login")
def login(payload: dict = Body(...)):
    supabase = get_supabase()
    username = payload.get("username")
    password = payload.get("password")

    res = supabase.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = res.data[0]
    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return {
            "message": "Login successful",
            "user": {
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "seller_id": user.get('seller_id')
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/admin/dashboard")
def get_admin_dashboard():
    seller_scores, _ = get_scores_data()
    total_sellers = len(seller_scores)
    avg_score = sum(s['trust_score'] for s in seller_scores) / total_sellers if total_sellers else 0
    high_risk = sum(1 for s in seller_scores if s['risk_level'] == 'High')
    low_risk = sum(1 for s in seller_scores if s['risk_level'] == 'Low')
    medium_risk = total_sellers - high_risk - low_risk
    
    return {
        "stats": {
            "total_sellers": total_sellers,
            "avg_trust_score": round(avg_score, 1),
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk
        },
        "sellers": seller_scores
    }

@app.get("/api/seller/dashboard")
def get_seller_dashboard(seller_id: str):
    import traceback
    try:
        seller_scores, data = get_scores_data()
        scores_map = {str(s['seller_id']): s for s in seller_scores}
        
        if seller_id not in scores_map:
            raise HTTPException(status_code=404, detail=f"Seller {seller_id} not found in scores map. Keys: {list(scores_map.keys())[:5]}")
        
        seller_data = scores_map[seller_id]
        
        # Fetch original reviews for table
        reviews_df = data['reviews'][data['reviews']['seller_id'].astype(str) == seller_id].copy()
        if 'review_date' in reviews_df.columns:
            reviews_df['review_date'] = reviews_df['review_date'].astype(str)
        
        reviews = reviews_df.to_dict(orient="records")
        
        # Add stats
        total_reviews = len(reviews)
        avg_rating = sum(r['rating'] for r in reviews) / total_reviews if total_reviews else 0
        
        # 1. Trend History (Simulated based on current score)
        import random
        # Ensure current_score is float
        current_score = float(seller_data['trust_score'])
        trend_history = [
            round(max(0, min(100, current_score - random.uniform(5, 15))), 1),
            round(max(0, min(100, current_score - random.uniform(2, 8))), 1),
            round(max(0, min(100, current_score - random.uniform(-2, 5))), 1),
            round(max(0, min(100, current_score - random.uniform(-1, 3))), 1),
            round(max(0, min(100, current_score - random.uniform(0, 2))), 1),
            current_score
        ]
        
        # 2. Sentiment Analysis (Based on Rating)
        sentiment = {"positive": 0, "neutral": 0, "negative": 0}
        for r in reviews:
            # Handle potential nan
            try:
                rating = float(r['rating'])
                if rating >= 4:
                    sentiment['positive'] += 1
                elif rating == 3:
                    sentiment['neutral'] += 1
                else:
                    sentiment['negative'] += 1
            except:
                continue

        # 3. Benchmarks (Platform Averages)
        def safe_avg(key, nested=False):
            values = []
            for s in seller_scores:
                val = s['metrics'][key] if nested else s[key]
                values.append(float(val)) # Explicit cast
            return round(sum(values) / len(values), 1) if values else 0.0

        benchmarks = {
            "avg_trust_score": safe_avg('trust_score'),
            "avg_delivery": safe_avg('delivery', nested=True),
            "avg_return": safe_avg('return_rate_score', nested=True),
            "avg_response": safe_avg('response', nested=True),
            "avg_authenticity": safe_avg('authenticity', nested=True)
        }

        # 4. AI Insights
        insights = []
        metrics = seller_data['metrics']
        
        if float(metrics['delivery']) < benchmarks['avg_delivery']:
            insights.append({"type": "warning", "icon": "fa-truck", "msg": f"Your Delivery Score ({metrics['delivery']}) is below average ({benchmarks['avg_delivery']}). Consider faster shipping options."})
        else:
            insights.append({"type": "success", "icon": "fa-check-circle", "msg": "Great work! Your delivery times are faster than the platform average."})

        if float(metrics['return_rate_score']) < benchmarks['avg_return']:
            insights.append({"type": "warning", "icon": "fa-rotate-left", "msg": f"Return Rate is high. Improve product descriptions to match customer expectations."})
        
        # Avoid division by zero
        pos = sentiment['positive'] if sentiment['positive'] > 0 else 1
        if sentiment['negative'] > pos * 0.2:
            insights.append({"type": "danger", "icon": "fa-comments", "msg": "Negative sentiment is rising. Review recent low-rated feedback immediately."})
            
        if float(seller_data['confidence_score']) < 60:
            insights.append({"type": "info", "icon": "fa-chart-line", "msg": "Complete more orders to increase your Confidence Score and unlock premium badges."})

        return {
            "score_card": seller_data,
            "reviews": reviews,
            "summary": {
                "avg_rating": round(avg_rating, 1),
                "total_reviews": total_reviews,
                "total_orders": len(data['orders'][data['orders']['seller_id'].astype(str) == seller_id])
            },
            "trend_data": trend_history,
            "sentiment_analysis": sentiment,
            "benchmarks": benchmarks,
            "insights": insights
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/buyer/{seller_id}")
def get_buyer_view(seller_id: str):
    seller_scores, _ = get_scores_data()
    scores_map = {str(s['seller_id']): s for s in seller_scores}
    
    if seller_id not in scores_map:
        raise HTTPException(status_code=404, detail="Seller not found")
        
    seller = scores_map[seller_id]
    return {
        "seller_name": seller['name'],
        "trust_score": seller['trust_score'],
        "risk_level": seller['risk_level'],
        "confidence_score": seller['confidence_score'],
        "metrics": seller['metrics'],
        "stats": seller['stats']
    }

# Original endpoints for backward compatibility if needed
@app.get("/api/dashboard-stats")
def get_dashboard_stats():
    seller_scores, _ = get_scores_data()
    total_sellers = len(seller_scores)
    avg_score = sum(s['trust_score'] for s in seller_scores) / total_sellers if total_sellers else 0
    high_risk = sum(1 for s in seller_scores if s['risk_level'] == 'High')
    low_risk = sum(1 for s in seller_scores if s['risk_level'] == 'Low')
    medium_risk = total_sellers - high_risk - low_risk
    
    return {
        "total_sellers": total_sellers,
        "avg_trust_score": round(avg_score, 1),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk
    }

@app.get("/api/sellers")
def get_sellers():
    scores, _ = get_scores_data()
    return scores

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

