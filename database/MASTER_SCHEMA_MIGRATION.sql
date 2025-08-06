-- ============================================================================
-- MASTER SCHEMA MIGRATION FOR CASABLANCA INSIGHTS
-- ============================================================================
-- This file contains the complete database schema for the Casablanca Insights platform
-- Run this in your Supabase SQL Editor to create all required tables, indexes, and functions
-- 
-- Features included:
-- - Core company data (companies, prices, reports, news)
-- - User management and authentication
-- - Watchlists and price alerts
-- - Paper trading system
-- - Sentiment voting and aggregation
-- - Newsletter management
-- - Contest system
-- - ETFs and Bonds data
-- - AI summaries and chat queries
-- - Portfolio management
-- - Advanced analytics and reporting
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Try to enable TimescaleDB if available (optional for time-series optimization)
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    RAISE NOTICE 'TimescaleDB extension enabled successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB extension not available, using standard PostgreSQL';
END $$;

-- ============================================================================
-- 1. CORE COMPANY DATA TABLES
-- ============================================================================

-- Companies table (master company information)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    current_price DECIMAL(10,2),
    price_change DECIMAL(10,2),
    price_change_percent DECIMAL(5,2),
    pe_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(5,2),
    roe DECIMAL(5,2),
    shares_outstanding BIGINT,
    size_category VARCHAR(20) CHECK (size_category IN ('Micro Cap', 'Small Cap', 'Mid Cap', 'Large Cap')),
    sector_group VARCHAR(100),
    exchange VARCHAR(100) DEFAULT 'Casablanca Stock Exchange (BVC)',
    country VARCHAR(50) DEFAULT 'Morocco',
    company_url TEXT,
    ir_url TEXT,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Company Prices table (OHLCV data)
CREATE TABLE IF NOT EXISTS company_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    adjusted_close DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);

-- Company Reports table (financial reports)
CREATE TABLE IF NOT EXISTS company_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    report_type VARCHAR(50) CHECK (report_type IN ('annual_report', 'quarterly_report', 'financial_statement', 'earnings', 'unknown')),
    report_date VARCHAR(50),
    report_year VARCHAR(4),
    report_quarter VARCHAR(10),
    url TEXT NOT NULL,
    filename VARCHAR(255),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, url)
);

-- Company News table (news and sentiment)
CREATE TABLE IF NOT EXISTS company_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    headline TEXT NOT NULL,
    source VARCHAR(255),
    published_at TIMESTAMPTZ,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    sentiment_score DECIMAL(3,2),
    url TEXT,
    content_preview TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, url, published_at)
);

-- ============================================================================
-- 2. USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Enhanced profiles table (User Metadata)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'admin')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'Africa/Casablanca',
    language_preference VARCHAR(10) DEFAULT 'en' CHECK (language_preference IN ('en', 'fr', 'ar')),
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles for additional data
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    bio TEXT,
    company VARCHAR(255),
    job_title VARCHAR(255),
    investment_experience VARCHAR(50) CHECK (investment_experience IN ('beginner', 'intermediate', 'advanced', 'professional')),
    investment_goals JSONB DEFAULT '[]',
    risk_tolerance VARCHAR(20) DEFAULT 'moderate' CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. WATCHLISTS & ALERTS
-- ============================================================================

-- Watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist items table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    target_price DECIMAL(10,2),
    UNIQUE(watchlist_id, ticker)
);

-- Price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) CHECK (alert_type IN ('above', 'below', 'percent_change')),
    target_price DECIMAL(10,2),
    percent_change DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    notification_method VARCHAR(20) DEFAULT 'email' CHECK (notification_method IN ('email', 'push', 'both')),
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. SENTIMENT & VOTING SYSTEM
-- ============================================================================

-- Sentiment votes table
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    confidence DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sentiment aggregates table
CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    positive_votes INTEGER DEFAULT 0,
    negative_votes INTEGER DEFAULT 0,
    neutral_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3,2),
    confidence_score DECIMAL(3,2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);

-- ============================================================================
-- 5. NEWSLETTER MANAGEMENT
-- ============================================================================

-- Newsletter subscribers
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced', 'pending')),
    preferences JSONB DEFAULT '{}',
    source VARCHAR(50) DEFAULT 'website',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_email_sent TIMESTAMPTZ,
    email_count INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0
);

-- Newsletter campaigns
CREATE TABLE IF NOT EXISTS newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    html_content TEXT,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'sending', 'sent', 'cancelled')),
    scheduled_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    recipient_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    bounce_count INTEGER DEFAULT 0,
    unsubscribe_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. CONTEST SYSTEM
-- ============================================================================

-- Contests table
CREATE TABLE IF NOT EXISTS contests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'ended', 'cancelled')),
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    prize_pool DECIMAL(10,2),
    rules JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest entries table
CREATE TABLE IF NOT EXISTS contest_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    portfolio_value DECIMAL(15,2) DEFAULT 0,
    total_return DECIMAL(8,4) DEFAULT 0,
    rank INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(contest_id, user_id)
);

-- Contest prizes table
CREATE TABLE IF NOT EXISTS contest_prizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    prize_amount DECIMAL(10,2),
    prize_description TEXT,
    winner_id UUID REFERENCES profiles(id),
    awarded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest notifications table
CREATE TABLE IF NOT EXISTS contest_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 7. PAPER TRADING SYSTEM
-- ============================================================================

-- Paper trading accounts table
CREATE TABLE IF NOT EXISTS paper_trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    initial_balance DECIMAL(15,2) DEFAULT 100000,
    current_balance DECIMAL(15,2) DEFAULT 100000,
    total_pnl DECIMAL(15,2) DEFAULT 0,
    total_return_percent DECIMAL(8,4) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper trading orders table
CREATE TABLE IF NOT EXISTS paper_trading_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) CHECK (order_type IN ('buy', 'sell')),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2),
    order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'filled', 'cancelled', 'rejected')),
    filled_price DECIMAL(10,2),
    filled_quantity INTEGER,
    commission DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    filled_at TIMESTAMPTZ
);

-- Paper trading positions table
CREATE TABLE IF NOT EXISTS paper_trading_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    market_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(15,2),
    unrealized_pnl_percent DECIMAL(8,4),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, ticker)
);

-- ============================================================================
-- 8. PORTFOLIO MANAGEMENT
-- ============================================================================

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(10,2) NOT NULL,
    notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, ticker)
);

-- ============================================================================
-- 9. AI & ANALYTICS
-- ============================================================================

-- AI summaries table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    summary_type VARCHAR(50) DEFAULT 'company_overview',
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat queries table
CREATE TABLE IF NOT EXISTS chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    query_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 10. ETFs & BONDS
-- ============================================================================

-- ETFs table
CREATE TABLE IF NOT EXISTS etfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(25) NOT NULL UNIQUE,
    isin VARCHAR(12) UNIQUE,
    underlying_index VARCHAR(100),
    issuer VARCHAR(100),
    expense_ratio DECIMAL(5,4),
    inception_date DATE,
    listing_date DATE,
    asset_class VARCHAR(50),
    geographic_focus VARCHAR(100),
    sector_focus VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'MAD',
    dividend_frequency VARCHAR(20),
    rebalancing_frequency VARCHAR(20),
    source_url TEXT,
    prospectus_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ETF data table
CREATE TABLE IF NOT EXISTS etf_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etf_id UUID REFERENCES etfs(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    nav DECIMAL(12,4) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    total_assets DECIMAL(20,2),
    shares_outstanding BIGINT,
    premium_discount DECIMAL(5,4),
    change_amount DECIMAL(12,4),
    change_percent DECIMAL(8,6),
    high_24h DECIMAL(12,4),
    low_24h DECIMAL(12,4),
    open_price DECIMAL(12,4),
    previous_close DECIMAL(12,4),
    source VARCHAR(50) DEFAULT 'cse',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(etf_id, date)
);

-- Bonds table
CREATE TABLE IF NOT EXISTS bonds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(25) NOT NULL UNIQUE,
    isin VARCHAR(12) UNIQUE,
    issuer VARCHAR(100) NOT NULL,
    issuer_name VARCHAR(255),
    bond_type VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'MAD',
    face_value DECIMAL(15,2) NOT NULL,
    coupon_rate DECIMAL(5,4),
    coupon_frequency VARCHAR(20),
    issue_date DATE,
    maturity_date DATE NOT NULL,
    issue_size DECIMAL(20,2),
    minimum_investment DECIMAL(15,2),
    credit_rating VARCHAR(10),
    rating_agency VARCHAR(50),
    callable BOOLEAN DEFAULT FALSE,
    puttable BOOLEAN DEFAULT FALSE,
    convertible BOOLEAN DEFAULT FALSE,
    floating_rate BOOLEAN DEFAULT FALSE,
    benchmark_rate VARCHAR(50),
    spread DECIMAL(5,4),
    source_url TEXT,
    prospectus_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bond data table
CREATE TABLE IF NOT EXISTS bond_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bond_id UUID REFERENCES bonds(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    dirty_price DECIMAL(12,4),
    yield_to_maturity DECIMAL(8,6),
    yield_to_call DECIMAL(8,6),
    current_yield DECIMAL(8,6),
    modified_duration DECIMAL(8,4),
    convexity DECIMAL(8,4),
    accrued_interest DECIMAL(12,4),
    volume BIGINT,
    bid_price DECIMAL(12,4),
    ask_price DECIMAL(12,4),
    bid_yield DECIMAL(8,6),
    ask_yield DECIMAL(8,6),
    spread_to_benchmark DECIMAL(8,6),
    source VARCHAR(50) DEFAULT 'cse',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(bond_id, date)
);

-- ============================================================================
-- 11. MARKET DATA & ANALYTICS
-- ============================================================================

-- CSE companies table
CREATE TABLE IF NOT EXISTS cse_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    isin VARCHAR(12),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    shares_outstanding BIGINT,
    listing_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price DECIMAL(10,2),
    volume BIGINT,
    change_amount DECIMAL(10,2),
    change_percent DECIMAL(8,6),
    high_24h DECIMAL(10,2),
    low_24h DECIMAL(10,2),
    open_price DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    source VARCHAR(50) DEFAULT 'cse',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 12. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Core company indexes
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_size_category ON companies(size_category);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Price data indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

-- Reports indexes
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker ON company_reports(ticker);
CREATE INDEX IF NOT EXISTS idx_company_reports_type ON company_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_company_reports_year ON company_reports(report_year);
CREATE INDEX IF NOT EXISTS idx_company_reports_scraped_at ON company_reports(scraped_at);

-- News indexes
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

-- User indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(tier);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles(status);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer ON profiles(stripe_customer_id);

-- Watchlist indexes
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_is_default ON watchlists(is_default) WHERE is_default = true;
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON watchlist_items(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items(ticker);

-- Alert indexes
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts(ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_price_alerts_alert_type ON price_alerts(alert_type);

-- Sentiment indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);

-- Unique constraint for sentiment votes (one vote per user per ticker per day)
CREATE UNIQUE INDEX IF NOT EXISTS idx_sentiment_votes_unique_daily 
ON sentiment_votes(user_id, ticker, DATE(created_at));

-- Newsletter indexes
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_status ON newsletter_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_type ON newsletter_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_sent_at ON newsletter_campaigns(sent_at);

-- Contest indexes
CREATE INDEX IF NOT EXISTS idx_contests_status ON contests(status);
CREATE INDEX IF NOT EXISTS idx_contests_dates ON contests(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_contest_entries_contest_id ON contest_entries(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_entries_user_id ON contest_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_contest_entries_rank ON contest_entries(rank);
CREATE INDEX IF NOT EXISTS idx_contest_prizes_contest_id ON contest_prizes(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_prizes_winner_id ON contest_prizes(winner_id);
CREATE INDEX IF NOT EXISTS idx_contest_notifications_user_id ON contest_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_contest_notifications_contest_id ON contest_notifications(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_notifications_read ON contest_notifications(is_read);

-- Paper trading indexes
CREATE INDEX IF NOT EXISTS idx_paper_trading_accounts_user_id ON paper_trading_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_account_id ON paper_trading_orders(account_id);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_ticker ON paper_trading_orders(ticker);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_status ON paper_trading_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_paper_trading_positions_account_id ON paper_trading_positions(account_id);
CREATE INDEX IF NOT EXISTS idx_paper_trading_positions_ticker ON paper_trading_positions(ticker);

-- Portfolio indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_ticker ON portfolio_holdings(ticker);

-- AI indexes
CREATE INDEX IF NOT EXISTS idx_ai_summaries_ticker ON ai_summaries(ticker);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_language ON ai_summaries(language);
CREATE INDEX IF NOT EXISTS idx_chat_queries_user_id ON chat_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_queries_created_at ON chat_queries(created_at DESC);

-- CSE and market data indexes
CREATE INDEX IF NOT EXISTS idx_cse_companies_ticker ON cse_companies(ticker);
CREATE INDEX IF NOT EXISTS idx_cse_companies_isin ON cse_companies(isin);
CREATE INDEX IF NOT EXISTS idx_cse_companies_sector ON cse_companies(sector);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

-- ETF and Bond indexes
CREATE INDEX IF NOT EXISTS idx_etfs_ticker ON etfs(ticker);
CREATE INDEX IF NOT EXISTS idx_etfs_isin ON etfs(isin);
CREATE INDEX IF NOT EXISTS idx_etfs_asset_class ON etfs(asset_class);
CREATE INDEX IF NOT EXISTS idx_etf_data_etf_id_date ON etf_data(etf_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_bonds_ticker ON bonds(ticker);
CREATE INDEX IF NOT EXISTS idx_bonds_isin ON bonds(isin);
CREATE INDEX IF NOT EXISTS idx_bonds_issuer ON bonds(issuer);
CREATE INDEX IF NOT EXISTS idx_bond_data_bond_id_date ON bond_data(bond_id, date DESC);

-- ============================================================================
-- 13. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update sentiment aggregates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert sentiment aggregate for the ticker and date
    INSERT INTO sentiment_aggregates (ticker, date, positive_votes, negative_votes, neutral_votes, total_votes, sentiment_score, confidence_score, last_updated)
    SELECT 
        ticker,
        DATE(created_at),
        COUNT(*) FILTER (WHERE sentiment = 'positive'),
        COUNT(*) FILTER (WHERE sentiment = 'negative'),
        COUNT(*) FILTER (WHERE sentiment = 'neutral'),
        COUNT(*),
        CASE 
            WHEN COUNT(*) > 0 THEN 
                (COUNT(*) FILTER (WHERE sentiment = 'positive') - COUNT(*) FILTER (WHERE sentiment = 'negative'))::DECIMAL / COUNT(*)
            ELSE 0 
        END,
        AVG(confidence),
        NOW()
    FROM sentiment_votes 
    WHERE ticker = NEW.ticker AND DATE(created_at) = DATE(NEW.created_at)
    GROUP BY ticker, DATE(created_at)
    ON CONFLICT (ticker, date) DO UPDATE SET
        positive_votes = EXCLUDED.positive_votes,
        negative_votes = EXCLUDED.negative_votes,
        neutral_votes = EXCLUDED.neutral_votes,
        total_votes = EXCLUDED.total_votes,
        sentiment_score = EXCLUDED.sentiment_score,
        confidence_score = EXCLUDED.confidence_score,
        last_updated = NOW();
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Function to ensure single default watchlist
CREATE OR REPLACE FUNCTION public.ensure_single_default_watchlist()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = true THEN
        UPDATE watchlists 
        SET is_default = false 
        WHERE user_id = NEW.user_id AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update watchlist updated_at
CREATE OR REPLACE FUNCTION public.update_watchlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE watchlists 
    SET updated_at = NOW() 
    WHERE id = COALESCE(NEW.watchlist_id, OLD.watchlist_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- ============================================================================
-- 14. TRIGGERS
-- ============================================================================

-- Sentiment votes triggers
CREATE TRIGGER sentiment_votes_insert_trigger
    AFTER INSERT ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

CREATE TRIGGER sentiment_votes_update_trigger
    AFTER UPDATE ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

CREATE TRIGGER sentiment_votes_delete_trigger
    AFTER DELETE ON sentiment_votes
    FOR EACH ROW
    EXECUTE FUNCTION update_sentiment_aggregate();

-- Updated at triggers
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sentiment_votes_updated_at 
    BEFORE UPDATE ON sentiment_votes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlists_updated_at 
    BEFORE UPDATE ON watchlists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_price_alerts_updated_at 
    BEFORE UPDATE ON price_alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paper_trading_accounts_updated_at 
    BEFORE UPDATE ON paper_trading_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paper_trading_positions_updated_at 
    BEFORE UPDATE ON paper_trading_positions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etfs_updated_at 
    BEFORE UPDATE ON etfs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bonds_updated_at 
    BEFORE UPDATE ON bonds 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User creation trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Watchlist triggers
CREATE TRIGGER on_watchlist_default_change
    AFTER INSERT OR UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION public.ensure_single_default_watchlist();

CREATE TRIGGER on_watchlist_item_change
    AFTER INSERT OR UPDATE OR DELETE ON watchlist_items
    FOR EACH ROW EXECUTE FUNCTION public.update_watchlist_updated_at();

-- ============================================================================
-- 15. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all user-related tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_notifications ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- User profiles policies
CREATE POLICY "Users can manage own user profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Watchlists policies
CREATE POLICY "Users can manage own watchlists" ON watchlists
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own watchlist items" ON watchlist_items
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM watchlists WHERE id = watchlist_id
        )
    );

-- Price alerts policies
CREATE POLICY "Users can manage own price alerts" ON price_alerts
    FOR ALL USING (auth.uid() = user_id);

-- Sentiment votes policies
CREATE POLICY "Users can manage own sentiment votes" ON sentiment_votes
    FOR ALL USING (auth.uid() = user_id);

-- Paper trading policies
CREATE POLICY "Users can manage own paper trading accounts" ON paper_trading_accounts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own paper trading orders" ON paper_trading_orders
    FOR ALL USING (auth.uid() IN (
        SELECT user_id FROM paper_trading_accounts WHERE id = account_id
    ));

CREATE POLICY "Users can manage own paper trading positions" ON paper_trading_positions
    FOR ALL USING (auth.uid() IN (
        SELECT user_id FROM paper_trading_accounts WHERE id = account_id
    ));

-- Portfolio policies
CREATE POLICY "Users can manage own portfolios" ON portfolios
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own portfolio holdings" ON portfolio_holdings
    FOR ALL USING (auth.uid() IN (
        SELECT user_id FROM portfolios WHERE id = portfolio_id
    ));

-- Chat queries policies
CREATE POLICY "Users can manage own chat queries" ON chat_queries
    FOR ALL USING (auth.uid() = user_id);

-- Contest policies
CREATE POLICY "Users can manage own contest entries" ON contest_entries
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own contest notifications" ON contest_notifications
    FOR ALL USING (auth.uid() = user_id);

-- ============================================================================
-- 16. GRANTS & PERMISSIONS
-- ============================================================================

-- Grant permissions for public data (read-only)
GRANT SELECT ON companies TO anon, authenticated;
GRANT SELECT ON company_prices TO anon, authenticated;
GRANT SELECT ON company_reports TO anon, authenticated;
GRANT SELECT ON company_news TO anon, authenticated;
GRANT SELECT ON cse_companies TO anon, authenticated;
GRANT SELECT ON market_data TO anon, authenticated;
GRANT SELECT ON etfs TO anon, authenticated;
GRANT SELECT ON etf_data TO anon, authenticated;
GRANT SELECT ON bonds TO anon, authenticated;
GRANT SELECT ON bond_data TO anon, authenticated;
GRANT SELECT ON ai_summaries TO anon, authenticated;
GRANT SELECT ON sentiment_aggregates TO anon, authenticated;
GRANT SELECT ON contests TO anon, authenticated;
GRANT SELECT ON newsletter_campaigns TO anon, authenticated;

-- Grant permissions for user data (full access for authenticated users)
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON watchlists TO authenticated;
GRANT ALL ON watchlist_items TO authenticated;
GRANT ALL ON price_alerts TO authenticated;
GRANT ALL ON sentiment_votes TO authenticated;
GRANT ALL ON paper_trading_accounts TO authenticated;
GRANT ALL ON paper_trading_orders TO authenticated;
GRANT ALL ON paper_trading_positions TO authenticated;
GRANT ALL ON portfolios TO authenticated;
GRANT ALL ON portfolio_holdings TO authenticated;
GRANT ALL ON chat_queries TO authenticated;
GRANT ALL ON contest_entries TO authenticated;
GRANT ALL ON contest_notifications TO authenticated;

-- ============================================================================
-- 17. VIEWS FOR ANALYTICS
-- ============================================================================

-- Latest market data view
CREATE OR REPLACE VIEW latest_market_data AS
SELECT DISTINCT ON (ticker)
    ticker,
    price,
    volume,
    change_amount,
    change_percent,
    high_24h,
    low_24h,
    open_price,
    previous_close,
    timestamp,
    source
FROM market_data
ORDER BY ticker, timestamp DESC;

-- Sentiment summary view
CREATE OR REPLACE VIEW sentiment_summary AS
SELECT 
    ticker,
    date,
    positive_votes,
    negative_votes,
    neutral_votes,
    total_votes,
    sentiment_score,
    confidence_score,
    CASE 
        WHEN sentiment_score > 0.1 THEN 'positive'
        WHEN sentiment_score < -0.1 THEN 'negative'
        ELSE 'neutral'
    END as overall_sentiment
FROM sentiment_aggregates
ORDER BY date DESC, total_votes DESC;

-- Portfolio performance view
CREATE OR REPLACE VIEW portfolio_performance AS
SELECT 
    p.id as portfolio_id,
    p.name as portfolio_name,
    p.user_id,
    ph.ticker,
    ph.quantity,
    ph.average_price,
    md.price as current_price,
    (md.price - ph.average_price) * ph.quantity as unrealized_pnl,
    ((md.price - ph.average_price) / ph.average_price * 100) as return_percent,
    ph.quantity * md.price as market_value
FROM portfolios p
JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
LEFT JOIN latest_market_data md ON ph.ticker = md.ticker;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Master schema migration completed successfully!';
    RAISE NOTICE 'All tables, indexes, functions, triggers, and policies have been created.';
    RAISE NOTICE 'Your Casablanca Insights database is ready for use.';
END $$; 