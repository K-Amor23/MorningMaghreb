-- Complete Supabase Database Schema for Casablanca Insights
-- Run this in your Supabase SQL Editor to create all required tables

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
-- 2. USER FEATURES TABLES
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
    language_preference VARCHAR(10) DEFAULT 'en' CHECK (language_preference IN ('en', 'fr', 'ar')),
    newsletter_frequency VARCHAR(20) DEFAULT 'weekly' CHECK (newsletter_frequency IN ('daily', 'weekly', 'monthly')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enhanced watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist items table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(watchlist_id, ticker)
);

-- Enhanced price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('above', 'below', 'change_percent', 'volume_spike')),
    price_threshold DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    triggered_at TIMESTAMPTZ,
    notification_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. SENTIMENT VOTING SYSTEM TABLES
-- ============================================================================

-- Sentiment Votes Table (User sentiment votes)
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Will reference auth.users(id) in Supabase
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
    confidence INTEGER NOT NULL DEFAULT 3 CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Sentiment Aggregates Table (Computed sentiment statistics)
CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL UNIQUE,
    bullish_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    bearish_count INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    bullish_percentage DECIMAL(5,2) DEFAULT 0.0,
    neutral_percentage DECIMAL(5,2) DEFAULT 0.0,
    bearish_percentage DECIMAL(5,2) DEFAULT 0.0,
    average_confidence DECIMAL(3,2) DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. NEWSLETTER SYSTEM TABLES
-- ============================================================================

-- Newsletter Subscribers
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

-- Newsletter Campaigns
CREATE TABLE IF NOT EXISTS newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en' CHECK (language IN ('en', 'fr', 'ar')),
    campaign_type VARCHAR(50) DEFAULT 'weekly_recap' CHECK (campaign_type IN ('weekly_recap', 'market_alert', 'custom')),
    sent_at TIMESTAMPTZ,
    recipient_count INTEGER,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. CONTEST SYSTEM TABLES
-- ============================================================================

-- Contests table
CREATE TABLE IF NOT EXISTS contests (
    contest_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    prize_pool DECIMAL(15,2) NOT NULL,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    rules JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest entries table
CREATE TABLE IF NOT EXISTS contest_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES paper_trading_accounts(id),
    rank INTEGER,
    final_balance DECIMAL(15,2),
    total_return DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    trades_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest prizes table
CREATE TABLE IF NOT EXISTS contest_prizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    rank_position INTEGER NOT NULL,
    prize_amount DECIMAL(15,2) NOT NULL,
    winner_id UUID REFERENCES auth.users(id),
    claimed BOOLEAN DEFAULT FALSE,
    claimed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest notifications table
CREATE TABLE IF NOT EXISTS contest_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    notification_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. PAPER TRADING SYSTEM TABLES
-- ============================================================================

-- Paper trading accounts table
CREATE TABLE IF NOT EXISTS paper_trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    initial_balance DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    available_cash DECIMAL(15,2) NOT NULL,
    total_pnl DECIMAL(15,2) DEFAULT 0,
    total_return_percent DECIMAL(10,4) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper trading orders table
CREATE TABLE IF NOT EXISTS paper_trading_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('buy', 'sell')),
    order_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (order_status IN ('pending', 'filled', 'cancelled', 'rejected')),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    filled_quantity INTEGER DEFAULT 0,
    filled_price DECIMAL(10,2),
    commission DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    filled_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
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
    unrealized_pnl_percent DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, ticker)
);

-- ============================================================================
-- 7. PORTFOLIO SYSTEM TABLES
-- ============================================================================

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, ticker)
);

-- ============================================================================
-- 8. AI AND ANALYTICS TABLES
-- ============================================================================

-- AI Summaries table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    summary TEXT NOT NULL,
    company_data JSONB,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, language)
);

-- Chat queries table
CREATE TABLE IF NOT EXISTS chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles for chat
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 9. FINANCIAL DATA TABLES
-- ============================================================================

-- CSE Companies Table (Casablanca Stock Exchange)
CREATE TABLE IF NOT EXISTS cse_companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    isin VARCHAR(12),
    sector VARCHAR(100),
    listing_date DATE,
    source_url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market Data Table (for real-time price data)
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    price DECIMAL(10,2),
    volume BIGINT,
    market_cap DECIMAL(20,2),
    change_percent DECIMAL(5,2),
    high_24h DECIMAL(10,2),
    low_24h DECIMAL(10,2),
    open_price DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source TEXT DEFAULT 'cse'
);

-- ============================================================================
-- 10. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_size_category ON companies(size_category);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Company Prices indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

-- Company Reports indexes
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker ON company_reports(ticker);
CREATE INDEX IF NOT EXISTS idx_company_reports_type ON company_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_company_reports_year ON company_reports(report_year);
CREATE INDEX IF NOT EXISTS idx_company_reports_scraped_at ON company_reports(scraped_at);

-- Company News indexes
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

-- User features indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles (email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles (tier);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles (status);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer ON profiles (stripe_customer_id);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_is_default ON watchlists (is_default) WHERE is_default = true;

CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON watchlist_items (watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items (ticker);

CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_price_alerts_alert_type ON price_alerts (alert_type);

-- Sentiment indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);

-- Newsletter indexes
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_status ON newsletter_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_type ON newsletter_campaigns(campaign_type);
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

-- AI and analytics indexes
CREATE INDEX IF NOT EXISTS idx_ai_summaries_ticker ON ai_summaries(ticker);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_language ON ai_summaries(language);
CREATE INDEX IF NOT EXISTS idx_chat_queries_user_id ON chat_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_queries_created_at ON chat_queries(created_at DESC);

-- Financial data indexes
CREATE INDEX IF NOT EXISTS idx_cse_companies_ticker ON cse_companies(ticker);
CREATE INDEX IF NOT EXISTS idx_cse_companies_isin ON cse_companies(isin);
CREATE INDEX IF NOT EXISTS idx_cse_companies_sector ON cse_companies(sector);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

-- ============================================================================
-- 11. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_aggregates ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE contests ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_prizes ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cse_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- Public read access policies
CREATE POLICY "Public read access to companies" ON companies FOR SELECT USING (true);
CREATE POLICY "Public read access to company_prices" ON company_prices FOR SELECT USING (true);
CREATE POLICY "Public read access to company_reports" ON company_reports FOR SELECT USING (true);
CREATE POLICY "Public read access to company_news" ON company_news FOR SELECT USING (true);
CREATE POLICY "Public read access to sentiment_aggregates" ON sentiment_aggregates FOR SELECT USING (true);
CREATE POLICY "Public read access to ai_summaries" ON ai_summaries FOR SELECT USING (true);
CREATE POLICY "Public read access to cse_companies" ON cse_companies FOR SELECT USING (true);
CREATE POLICY "Public read access to market_data" ON market_data FOR SELECT USING (true);
CREATE POLICY "Public read access to newsletter_subscribers" ON newsletter_subscribers FOR SELECT USING (true);

-- User-specific policies
CREATE POLICY "Users can view their own profiles" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profiles" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert their own profiles" ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view their own watchlists" ON watchlists FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own watchlists" ON watchlists FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own watchlists" ON watchlists FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own watchlists" ON watchlists FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own watchlist items" ON watchlist_items FOR SELECT USING (
    EXISTS (SELECT 1 FROM watchlists WHERE watchlists.id = watchlist_items.watchlist_id AND watchlists.user_id = auth.uid())
);
CREATE POLICY "Users can insert their own watchlist items" ON watchlist_items FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM watchlists WHERE watchlists.id = watchlist_items.watchlist_id AND watchlists.user_id = auth.uid())
);
CREATE POLICY "Users can update their own watchlist items" ON watchlist_items FOR UPDATE USING (
    EXISTS (SELECT 1 FROM watchlists WHERE watchlists.id = watchlist_items.watchlist_id AND watchlists.user_id = auth.uid())
);
CREATE POLICY "Users can delete their own watchlist items" ON watchlist_items FOR DELETE USING (
    EXISTS (SELECT 1 FROM watchlists WHERE watchlists.id = watchlist_items.watchlist_id AND watchlists.user_id = auth.uid())
);

CREATE POLICY "Users can view their own price alerts" ON price_alerts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own price alerts" ON price_alerts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own price alerts" ON price_alerts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own price alerts" ON price_alerts FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own sentiment votes" ON sentiment_votes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own sentiment votes" ON sentiment_votes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own sentiment votes" ON sentiment_votes FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own contest entries" ON contest_entries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own contest entries" ON contest_entries FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own contest entries" ON contest_entries FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own contest notifications" ON contest_notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own contest notifications" ON contest_notifications FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own paper trading accounts" ON paper_trading_accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own paper trading accounts" ON paper_trading_accounts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own paper trading accounts" ON paper_trading_accounts FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own paper trading orders" ON paper_trading_orders FOR SELECT USING (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_orders.account_id AND paper_trading_accounts.user_id = auth.uid())
);
CREATE POLICY "Users can insert their own paper trading orders" ON paper_trading_orders FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_orders.account_id AND paper_trading_accounts.user_id = auth.uid())
);
CREATE POLICY "Users can update their own paper trading orders" ON paper_trading_orders FOR UPDATE USING (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_orders.account_id AND paper_trading_accounts.user_id = auth.uid())
);

CREATE POLICY "Users can view their own paper trading positions" ON paper_trading_positions FOR SELECT USING (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_positions.account_id AND paper_trading_accounts.user_id = auth.uid())
);
CREATE POLICY "Users can insert their own paper trading positions" ON paper_trading_positions FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_positions.account_id AND paper_trading_accounts.user_id = auth.uid())
);
CREATE POLICY "Users can update their own paper trading positions" ON paper_trading_positions FOR UPDATE USING (
    EXISTS (SELECT 1 FROM paper_trading_accounts WHERE paper_trading_accounts.id = paper_trading_positions.account_id AND paper_trading_accounts.user_id = auth.uid())
);

CREATE POLICY "Users can view their own portfolios" ON portfolios FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own portfolios" ON portfolios FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own portfolios" ON portfolios FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own portfolios" ON portfolios FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own portfolio holdings" ON portfolio_holdings FOR SELECT USING (
    EXISTS (SELECT 1 FROM portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
);
CREATE POLICY "Users can insert their own portfolio holdings" ON portfolio_holdings FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
);
CREATE POLICY "Users can update their own portfolio holdings" ON portfolio_holdings FOR UPDATE USING (
    EXISTS (SELECT 1 FROM portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
);
CREATE POLICY "Users can delete their own portfolio holdings" ON portfolio_holdings FOR DELETE USING (
    EXISTS (SELECT 1 FROM portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
);

CREATE POLICY "Users can view their own chat queries" ON chat_queries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own chat queries" ON chat_queries FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own user profiles" ON user_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own user profiles" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own user profiles" ON user_profiles FOR UPDATE USING (auth.uid() = user_id);

-- Authenticated user policies
CREATE POLICY "Authenticated users can insert newsletter subscribers" ON newsletter_subscribers FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can insert ai_summaries" ON ai_summaries FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- 12. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update sentiment aggregates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO sentiment_aggregates (ticker, bullish_count, neutral_count, bearish_count, total_votes, 
                                     bullish_percentage, neutral_percentage, bearish_percentage, average_confidence, last_updated)
    SELECT 
        ticker,
        COUNT(CASE WHEN sentiment = 'bullish' THEN 1 END) as bullish_count,
        COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral_count,
        COUNT(CASE WHEN sentiment = 'bearish' THEN 1 END) as bearish_count,
        COUNT(*) as total_votes,
        ROUND(COUNT(CASE WHEN sentiment = 'bullish' THEN 1 END) * 100.0 / COUNT(*), 2) as bullish_percentage,
        ROUND(COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) * 100.0 / COUNT(*), 2) as neutral_percentage,
        ROUND(COUNT(CASE WHEN sentiment = 'bearish' THEN 1 END) * 100.0 / COUNT(*), 2) as bearish_percentage,
        ROUND(AVG(confidence), 2) as average_confidence,
        NOW() as last_updated
    FROM sentiment_votes
    WHERE ticker = COALESCE(NEW.ticker, OLD.ticker)
    GROUP BY ticker
    ON CONFLICT (ticker) DO UPDATE SET
        bullish_count = EXCLUDED.bullish_count,
        neutral_count = EXCLUDED.neutral_count,
        bearish_count = EXCLUDED.bearish_count,
        total_votes = EXCLUDED.total_votes,
        bullish_percentage = EXCLUDED.bullish_percentage,
        neutral_percentage = EXCLUDED.neutral_percentage,
        bearish_percentage = EXCLUDED.bearish_percentage,
        average_confidence = EXCLUDED.average_confidence,
        last_updated = EXCLUDED.last_updated;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to ensure single default watchlist
CREATE OR REPLACE FUNCTION public.ensure_single_default_watchlist()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = true THEN
        UPDATE watchlists 
        SET is_default = false 
        WHERE user_id = NEW.user_id 
        AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update watchlist timestamp
CREATE OR REPLACE FUNCTION public.update_watchlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE watchlists 
    SET updated_at = NOW() 
    WHERE id = NEW.watchlist_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers
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

CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sentiment_votes_updated_at 
    BEFORE UPDATE ON sentiment_votes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE TRIGGER on_watchlist_default_change
    AFTER INSERT OR UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION public.ensure_single_default_watchlist();

CREATE TRIGGER on_watchlist_item_change
    AFTER INSERT OR UPDATE OR DELETE ON watchlist_items
    FOR EACH ROW EXECUTE FUNCTION public.update_watchlist_updated_at();

-- ============================================================================
-- 13. GRANT PERMISSIONS
-- ============================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- ============================================================================
-- 14. COMMENTS
-- ============================================================================

COMMENT ON TABLE companies IS 'Master table for all Moroccan companies listed on the Casablanca Stock Exchange';
COMMENT ON TABLE company_prices IS 'Daily OHLCV price data for all companies';
COMMENT ON TABLE company_reports IS 'Financial reports and documents scraped from company IR pages';
COMMENT ON TABLE company_news IS 'News articles and sentiment analysis for companies';
COMMENT ON TABLE profiles IS 'User profiles and subscription information';
COMMENT ON TABLE watchlists IS 'User watchlists for tracking companies';
COMMENT ON TABLE watchlist_items IS 'Individual companies in user watchlists';
COMMENT ON TABLE price_alerts IS 'User price alerts for companies';
COMMENT ON TABLE sentiment_votes IS 'User sentiment votes for companies';
COMMENT ON TABLE sentiment_aggregates IS 'Aggregated sentiment statistics for companies';
COMMENT ON TABLE newsletter_subscribers IS 'Newsletter subscription management';
COMMENT ON TABLE newsletter_campaigns IS 'Newsletter campaign tracking';
COMMENT ON TABLE contests IS 'Portfolio trading contests';
COMMENT ON TABLE contest_entries IS 'User entries in trading contests';
COMMENT ON TABLE contest_prizes IS 'Prizes for contest winners';
COMMENT ON TABLE contest_notifications IS 'Notifications for contest participants';
COMMENT ON TABLE paper_trading_accounts IS 'Paper trading accounts for users';
COMMENT ON TABLE paper_trading_orders IS 'Paper trading orders';
COMMENT ON TABLE paper_trading_positions IS 'Current positions in paper trading accounts';
COMMENT ON TABLE portfolios IS 'User investment portfolios';
COMMENT ON TABLE portfolio_holdings IS 'Holdings in user portfolios';
COMMENT ON TABLE ai_summaries IS 'AI-generated company summaries';
COMMENT ON TABLE chat_queries IS 'User chat queries and responses';
COMMENT ON TABLE user_profiles IS 'Extended user profile information';
COMMENT ON TABLE cse_companies IS 'Casablanca Stock Exchange companies';
COMMENT ON TABLE market_data IS 'Real-time market data'; 