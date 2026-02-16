import pandas as pd
import os
from backend.supabase_client import get_supabase_admin
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def seed_sellers():
    print("Seeding sellers...")
    df = pd.read_csv(os.path.join(DATA_DIR, "sellers.csv"))
    # Rename columns to match SQL schema
    df = df.rename(columns={
        "seller_name": "seller_name",
        "avg_response_time_hours": "avg_response_time_hours"
    })
    data = df.to_dict(orient="records")
    supabase = get_supabase_admin()
    for row in data:
        supabase.table("sellers").upsert(row).execute()
    print(f"Seeded {len(data)} sellers.")

def seed_orders():
    print("Seeding orders...")
    df = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    # Handle dates and booleans
    df['order_date'] = pd.to_datetime(df['order_date']).dt.strftime('%Y-%m-%d')
    df['delivered_date'] = pd.to_datetime(df['delivered_date']).dt.strftime('%Y-%m-%d')
    df['on_time_delivery'] = df['on_time_delivery'].astype(bool)
    df['returned'] = df['returned'].astype(bool)
    
    data = df.to_dict(orient="records")
    supabase = get_supabase_admin()
    
    # Supabase might have limits on batch size, but 2500 should be okay or split
    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        supabase.table("orders").upsert(batch).execute()
    print(f"Seeded {len(data)} orders.")

def seed_reviews():
    print("Seeding reviews...")
    df = pd.read_csv(os.path.join(DATA_DIR, "reviews.csv"))
    df['review_date'] = pd.to_datetime(df['review_date']).dt.strftime('%Y-%m-%d')
    
    data = df.to_dict(orient="records")
    supabase = get_supabase_admin()
    
    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        supabase.table("reviews").upsert(batch).execute()
    print(f"Seeded {len(data)} reviews.")

def seed_users():
    print("Seeding demo users...")
    import bcrypt
    
    supabase = get_supabase_admin()
    
    # Admin User
    admin_data = {
        "username": "admin_demo",
        "email": "admin@trustscore.com",
        "password_hash": bcrypt.hashpw("Admin@123".encode(), bcrypt.gensalt()).decode(),
        "role": "admin"
    }
    supabase.table("users").upsert(admin_data).execute()
    
    # Seller User (tied to Seller_1 / id 1)
    seller_data = {
        "username": "seller_alpha",
        "email": "alpha@shop.com",
        "password_hash": bcrypt.hashpw("Seller@123".encode(), bcrypt.gensalt()).decode(),
        "role": "seller",
        "seller_id": "1"
    }
    supabase.table("users").upsert(seller_data).execute()
    print("Seeded demo users.")

if __name__ == "__main__":
    try:
        seed_sellers()
        seed_orders()
        seed_reviews()
        seed_users()
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
