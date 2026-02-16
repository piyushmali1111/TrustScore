import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key) if url and key else None
supabase_admin: Client = create_client(url, service_key) if url and service_key else None

def get_supabase() -> Client:
    if not supabase:
        raise Exception("Supabase credentials not found in environment variables")
    return supabase

def get_supabase_admin() -> Client:
    if not supabase_admin:
        raise Exception("Supabase Service Role Key not found in environment variables")
    return supabase_admin
