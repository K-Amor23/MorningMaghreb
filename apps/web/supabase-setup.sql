-- Supabase Setup for Casablanca Insights
-- Run this in your Supabase SQL editor

-- Create watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_ticker ON watchlists (ticker);

-- Enable Row Level Security (RLS)
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to only see their own watchlist items
CREATE POLICY "Users can view their own watchlist items" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own watchlist items
CREATE POLICY "Users can insert their own watchlist items" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own watchlist items
CREATE POLICY "Users can delete their own watchlist items" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- Create policy to allow users to update their own watchlist items
CREATE POLICY "Users can update their own watchlist items" ON watchlists
    FOR UPDATE USING (auth.uid() = user_id);

-- Insert some sample Moroccan stock tickers for testing
INSERT INTO watchlists (user_id, ticker) VALUES 
    ('00000000-0000-0000-0000-000000000000', 'IAM'),
    ('00000000-0000-0000-0000-000000000000', 'BCP'),
    ('00000000-0000-0000-0000-000000000000', 'ATW')
ON CONFLICT (user_id, ticker) DO NOTHING;

-- Create price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(5) NOT NULL CHECK (alert_type IN ('above', 'below')),
    price_threshold DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    triggered_at TIMESTAMPTZ,
    UNIQUE(user_id, ticker, alert_type, price_threshold)
);

-- Create indexes for price alerts
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (is_active) WHERE is_active = true;

-- Enable Row Level Security for price alerts
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;

-- Create policies for price alerts
CREATE POLICY "Users can view their own price alerts" ON price_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own price alerts" ON price_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own price alerts" ON price_alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own price alerts" ON price_alerts
    FOR DELETE USING (auth.uid() = user_id); 