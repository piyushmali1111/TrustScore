# TrustScore – Supabase Setup Guide

This project has been updated to use Supabase for data persistence and role-based authentication.

## 1. Supabase Project Setup
1. Create a new project on [Supabase](https://supabase.com/).
2. Go to the **SQL Editor** in your Supabase dashboard.
3. Copy the contents of `db_setup.sql` from this project and run it. This will create the `sellers`, `orders`, `reviews`, and `users` tables.

## 2. Environment Variables
1. Create a `.env` file in the root directory (you can use `.env.template` as a starting point).
2. Fill in the following credentials from your Supabase Project Settings (Settings > API):
   - `SUPABASE_URL`: Your Project URL.
   - `SUPABASE_KEY`: Your `anon` `public` key.
   - `SUPABASE_SERVICE_ROLE_KEY`: Your `service_role` `secret` key (required for initial data seeding).

## 3. Data Migration
1. Ensure your virtual environment is active and dependencies are installed:
   ```bash
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the migration script to upload CSV data to Supabase:
   ```bash
   python seed_supabase.py
   ```
   This script will:
   - Upload all sellers, orders, and reviews from the `data/` directory.
   - Create a demo Admin (`admin_demo` / `Admin@123`) and Seller (`seller_alpha` / `Seller@123`).

## 4. Run the Application
1. Start the FastAPI backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
2. Open your browser to `http://localhost:8000`.

## 5. Dashboards
- **Landing Page**: View the project overview and call-to-actions.
- **Login**: Use the demo credentials to access Admin or Seller dashboards.
- **Admin Dashboard**: See platform-wide metrics, risk distribution, and full seller list.
- **Seller Dashboard**: Access your personal TrustScore, performance radar, and review management.
- **Buyer Page**: A standalone verification page for a specific seller (e.g., `buyer_page.html?id=1`).

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **ML Engine**: Scikit-Learn (Fake Review Detection)
- **Frontend**: Vanilla HTML5, CSS3 (Rich Premium UI), JavaScript (Chart.js)
