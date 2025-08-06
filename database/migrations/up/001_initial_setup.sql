-- Migration: 001_initial_setup
-- Description: Initial database setup for Casablanca Insights
-- Created: 2025-08-06T16:16:17.156282

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_tier AS ENUM ('free', 'pro', 'admin');
CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due', 'trialing');
CREATE TYPE notification_type AS ENUM ('price_alert', 'news_alert', 'system_notification');

-- Create base tables
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    tier user_tier DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'active',
    subscription_id TEXT,
    stripe_customer_id TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sector TEXT,
    market_cap NUMERIC,
    current_price NUMERIC,
    price_change_percent NUMERIC,
    volume BIGINT,
    pe_ratio NUMERIC,
    dividend_yield NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL REFERENCES companies(ticker),
    price NUMERIC NOT NULL,
    change_percent NUMERIC,
    volume BIGINT,
    high NUMERIC,
    low NUMERIC,
    open_price NUMERIC,
    close_price NUMERIC,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date ON market_data(ticker, date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
