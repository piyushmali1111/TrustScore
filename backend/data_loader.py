import pandas as pd
import os
from .supabase_client import get_supabase

def load_data():
    """
    Load sellers, orders, and reviews from Supabase.
    Returns a dictionary of pandas DataFrames.
    """
    supabase = get_supabase()
    
    try:
        # Fetch Sellers
        sellers_res = supabase.table("sellers").select("*").execute()
        sellers_df = pd.DataFrame(sellers_res.data)
        
        # Fetch Orders
        orders_res = supabase.table("orders").select("*").execute()
        orders_df = pd.DataFrame(orders_res.data)
        
        # Fetch Reviews
        reviews_res = supabase.table("reviews").select("*").execute()
        reviews_df = pd.DataFrame(reviews_res.data)
        
        if sellers_df.empty or orders_df.empty or reviews_df.empty:
            print("Warning: One or more tables are empty in Supabase")
            
        # Ensure correct types
        if not reviews_df.empty:
            reviews_df['date'] = pd.to_datetime(reviews_df['review_date'])
            
        if not orders_df.empty:
            orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
            
        return {
            "sellers": sellers_df,
            "orders": orders_df,
            "reviews": reviews_df
        }
    except Exception as e:
        print(f"Error loading data from Supabase: {e}")
        return None

