-- Create Sellers Table
CREATE TABLE IF NOT EXISTS sellers (
    seller_id TEXT PRIMARY KEY,
    seller_name TEXT NOT NULL,
    account_age_days INTEGER,
    avg_response_time_hours FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    seller_id TEXT REFERENCES sellers(seller_id),
    order_date DATE,
    delivered_date DATE,
    delivery_days INTEGER,
    on_time_delivery BOOLEAN,
    returned BOOLEAN
);

-- Create Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    seller_id TEXT REFERENCES sellers(seller_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE,
    flagged_fake BOOLEAN DEFAULT FALSE,
    user_id TEXT
);

-- Create Users Table for Authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    role TEXT CHECK (role IN ('admin', 'seller')),
    seller_id TEXT REFERENCES sellers(seller_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_orders_seller_id ON orders(seller_id);
CREATE INDEX IF NOT EXISTS idx_reviews_seller_id ON reviews(seller_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
