-- Morning Maghreb Database Schema Setup
-- Copy and paste this entire file into your Supabase SQL Editor
-- Then click "Run" to create all tables and functions

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
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'pro', 'admin')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist items table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(watchlist_id, ticker)
);

-- Price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) CHECK (alert_type IN ('above', 'below', 'percent_change')),
    target_price DECIMAL(10,2),
    percent_change DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    triggered_at TIMESTAMPTZ,
    message TEXT
);

-- ============================================================================
-- 3. SENTIMENT & NEWS TABLES
-- ============================================================================

-- Sentiment votes table
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Sentiment aggregates table
CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    positive_votes INTEGER DEFAULT 0,
    negative_votes INTEGER DEFAULT 0,
    neutral_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3,2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker)
);

-- ============================================================================
-- 4. NEWSLETTER TABLES
-- ============================================================================

-- Newsletter subscribers table
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

-- Newsletter campaigns table
CREATE TABLE IF NOT EXISTS newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_type VARCHAR(50) CHECK (campaign_type IN ('daily', 'weekly', 'monthly', 'special')),
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMPTZ,
    recipient_count INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. CONTEST TABLES
-- ============================================================================

-- Contests table
CREATE TABLE IF NOT EXISTS contests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'ended')),
    prize_amount DECIMAL(10,2) DEFAULT 0,
    min_positions INTEGER DEFAULT 1,
    max_participants INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest entries table
CREATE TABLE IF NOT EXISTS contest_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    portfolio_value DECIMAL(15,2) DEFAULT 0,
    return_percentage DECIMAL(10,4) DEFAULT 0,
    rank INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(contest_id, user_id)
);

-- Contest prizes table
CREATE TABLE IF NOT EXISTS contest_prizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    winner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    prize_amount DECIMAL(10,2) NOT NULL,
    rank INTEGER NOT NULL,
    awarded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contest notifications table
CREATE TABLE IF NOT EXISTS contest_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    contest_id UUID REFERENCES contests(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. PAPER TRADING TABLES
-- ============================================================================

-- Paper trading accounts table
CREATE TABLE IF NOT EXISTS paper_trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    initial_balance DECIMAL(15,2) DEFAULT 100000,
    current_balance DECIMAL(15,2) DEFAULT 100000,
    total_pnl DECIMAL(15,2) DEFAULT 0,
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
    price DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'filled', 'cancelled')),
    filled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper trading positions table
CREATE TABLE IF NOT EXISTS paper_trading_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    unrealized_pnl DECIMAL(15,2) DEFAULT 0,
    realized_pnl DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, ticker)
);

-- ============================================================================
-- 7. PORTFOLIO TABLES
-- ============================================================================

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    unrealized_pnl DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, ticker)
);

-- ============================================================================
-- 8. AI & ANALYTICS TABLES
-- ============================================================================

-- AI summaries table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    summary_type VARCHAR(50) CHECK (summary_type IN ('company_overview', 'financial_analysis', 'market_outlook')),
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat queries table
CREATE TABLE IF NOT EXISTS chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 9. ADDITIONAL DATA TABLES
-- ============================================================================

-- User profiles (extended)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    bio TEXT,
    location VARCHAR(255),
    website VARCHAR(255),
    social_links JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CSE companies (legacy)
CREATE TABLE IF NOT EXISTS cse_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    isin VARCHAR(12),
    sector VARCHAR(100),
    market_cap DECIMAL(20,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    change_percent DECIMAL(5,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    open DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, timestamp)
);

-- ============================================================================
-- 10. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_size_category ON companies(size_category);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Company prices indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

-- Company reports indexes
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker ON company_reports(ticker);
CREATE INDEX IF NOT EXISTS idx_company_reports_type ON company_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_company_reports_year ON company_reports(report_year);
CREATE INDEX IF NOT EXISTS idx_company_reports_scraped_at ON company_reports(scraped_at);

-- Company news indexes
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles (email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles (tier);
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles (status);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer ON profiles (stripe_customer_id);

-- Watchlists indexes
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_is_default ON watchlists (is_default) WHERE is_default = true;

-- Watchlist items indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON watchlist_items (watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items (ticker);

-- Price alerts indexes
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

-- Additional data indexes
CREATE INDEX IF NOT EXISTS idx_cse_companies_ticker ON cse_companies(ticker);
CREATE INDEX IF NOT EXISTS idx_cse_companies_isin ON cse_companies(isin);
CREATE INDEX IF NOT EXISTS idx_cse_companies_sector ON cse_companies(sector);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

-- ============================================================================
-- 11. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update sentiment aggregates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Update sentiment aggregates when sentiment votes change
    INSERT INTO sentiment_aggregates (ticker, positive_votes, negative_votes, neutral_votes, total_votes, sentiment_score)
    VALUES (
        NEW.ticker,
        (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker AND sentiment = 'positive'),
        (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker AND sentiment = 'negative'),
        (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker AND sentiment = 'neutral'),
        (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker),
        CASE 
            WHEN (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker) > 0 
            THEN (
                (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker AND sentiment = 'positive')::DECIMAL / 
                (SELECT COUNT(*) FROM sentiment_votes WHERE ticker = NEW.ticker)::DECIMAL
            )
            ELSE 0
        END
    )
    ON CONFLICT (ticker) DO UPDATE SET
        positive_votes = EXCLUDED.positive_votes,
        negative_votes = EXCLUDED.negative_votes,
        neutral_votes = EXCLUDED.neutral_votes,
        total_votes = EXCLUDED.total_votes,
        sentiment_score = EXCLUDED.sentiment_score,
        last_updated = NOW();
    
    RETURN NEW;
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
        WHERE user_id = NEW.user_id AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update watchlist updated_at
CREATE OR REPLACE FUNCTION public.update_watchlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE watchlists 
    SET updated_at = NOW() 
    WHERE id = COALESCE(NEW.watchlist_id, OLD.watchlist_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 12. TRIGGERS
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
-- 13. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE contest_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Watchlists policies
CREATE POLICY "Users can view own watchlists" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own watchlists" ON watchlists
    FOR ALL USING (auth.uid() = user_id);

-- Watchlist items policies
CREATE POLICY "Users can view own watchlist items" ON watchlist_items
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM watchlists WHERE id = watchlist_id
        )
    );

CREATE POLICY "Users can manage own watchlist items" ON watchlist_items
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM watchlists WHERE id = watchlist_id
        )
    );

-- Price alerts policies
CREATE POLICY "Users can view own price alerts" ON price_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own price alerts" ON price_alerts
    FOR ALL USING (auth.uid() = user_id);

-- Sentiment votes policies
CREATE POLICY "Users can view own sentiment votes" ON sentiment_votes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own sentiment votes" ON sentiment_votes
    FOR ALL USING (auth.uid() = user_id);

-- Contest entries policies
CREATE POLICY "Users can view own contest entries" ON contest_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own contest entries" ON contest_entries
    FOR ALL USING (auth.uid() = user_id);

-- Contest notifications policies
CREATE POLICY "Users can view own contest notifications" ON contest_notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own contest notifications" ON contest_notifications
    FOR ALL USING (auth.uid() = user_id);

-- Paper trading policies
CREATE POLICY "Users can view own paper trading accounts" ON paper_trading_accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own paper trading accounts" ON paper_trading_accounts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own paper trading orders" ON paper_trading_orders
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        )
    );

CREATE POLICY "Users can manage own paper trading orders" ON paper_trading_orders
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        )
    );

CREATE POLICY "Users can view own paper trading positions" ON paper_trading_positions
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        )
    );

CREATE POLICY "Users can manage own paper trading positions" ON paper_trading_positions
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        )
    );

-- Portfolio policies
CREATE POLICY "Users can view own portfolios" ON portfolios
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own portfolios" ON portfolios
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own portfolio holdings" ON portfolio_holdings
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM portfolios WHERE id = portfolio_id
        )
    );

CREATE POLICY "Users can manage own portfolio holdings" ON portfolio_holdings
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM portfolios WHERE id = portfolio_id
        )
    );

-- Chat queries policies
CREATE POLICY "Users can view own chat queries" ON chat_queries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own chat queries" ON chat_queries
    FOR ALL USING (auth.uid() = user_id);

-- User profiles policies
CREATE POLICY "Users can view own user profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own user profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Public read policies for market data
CREATE POLICY "Anyone can view companies" ON companies
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view company prices" ON company_prices
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view company reports" ON company_reports
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view company news" ON company_news
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view sentiment aggregates" ON sentiment_aggregates
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view contests" ON contests
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view newsletter campaigns" ON newsletter_campaigns
    FOR SELECT USING (true);

CREATE POLICY "Anyone can view market data" ON market_data
    FOR SELECT USING (true);

-- ============================================================================
-- 14. COMPLETION MESSAGE
-- ============================================================================

-- This will show a success message when the script completes
SELECT 'Morning Maghreb database schema setup completed successfully!' as status; 