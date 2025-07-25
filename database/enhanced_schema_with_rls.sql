-- Enhanced Casablanca Insights Database Schema
-- PostgreSQL with RLS policies and real-time subscriptions
-- TimescaleDB extension is optional for time-series optimization

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Try to enable TimescaleDB if available (optional)
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
    RAISE NOTICE 'TimescaleDB extension enabled successfully';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB extension not available, using standard PostgreSQL';
END $$;

-- ============================================================================
-- 1. USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'Africa/Casablanca',
    language_preference VARCHAR(10) DEFAULT 'en' CHECK (language_preference IN ('en', 'fr', 'ar')),
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'institutional')),
    subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'canceled', 'past_due')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles for additional data
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
-- 2. NEWSLETTER MANAGEMENT
-- ============================================================================

-- Newsletter subscribers
CREATE TABLE IF NOT EXISTS public.newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced', 'pending')),
    preferences JSONB DEFAULT '{}',
    source VARCHAR(50) DEFAULT 'website', -- website, mobile, api, import
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_email_sent TIMESTAMPTZ,
    email_count INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0
);

-- Newsletter campaigns
CREATE TABLE IF NOT EXISTS public.newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
    created_by UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Newsletter campaign recipients
CREATE TABLE IF NOT EXISTS public.newsletter_campaign_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES public.newsletter_campaigns(id) ON DELETE CASCADE,
    subscriber_id UUID REFERENCES public.newsletter_subscribers(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed')),
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    bounce_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Newsletter templates
CREATE TABLE IF NOT EXISTS public.newsletter_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subject_template VARCHAR(255) NOT NULL,
    content_template TEXT NOT NULL,
    html_template TEXT,
    variables JSONB DEFAULT '[]', -- List of available variables
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. VOLUME DATA & MARKET DATA
-- ============================================================================

-- Enhanced volume data table
CREATE TABLE IF NOT EXISTS public.volume_data (
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    volume BIGINT NOT NULL,
    volume_ma_5 DECIMAL(15,2), -- 5-day moving average
    volume_ma_20 DECIMAL(15,2), -- 20-day moving average
    volume_ratio DECIMAL(8,4), -- Current volume / 20-day average
    volume_alert BOOLEAN DEFAULT FALSE, -- True if volume > 2x average
    source VARCHAR(50) DEFAULT 'wafabourse', -- wafabourse, investing, african_markets
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, timestamp)
);

-- Convert to hypertable for time-series optimization (if TimescaleDB is available)
DO $$
BEGIN
    PERFORM create_hypertable('volume_data', 'timestamp', if_not_exists => TRUE);
    RAISE NOTICE 'Volume data converted to hypertable';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB not available, volume_data remains as regular table';
END $$;

-- Market quotes with volume
CREATE TABLE IF NOT EXISTS public.quotes (
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    change_amount DECIMAL(12,4),
    change_percent DECIMAL(8,6),
    volume_ma_5 DECIMAL(15,2),
    volume_ma_20 DECIMAL(15,2),
    volume_ratio DECIMAL(8,4),
    source VARCHAR(50) DEFAULT 'wafabourse',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, timestamp)
);

-- Convert to hypertable (if TimescaleDB is available)
DO $$
BEGIN
    PERFORM create_hypertable('quotes', 'timestamp', if_not_exists => TRUE);
    RAISE NOTICE 'Quotes converted to hypertable';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB not available, quotes remains as regular table';
END $$;

-- Volume alerts
CREATE TABLE IF NOT EXISTS public.volume_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('high_volume', 'low_volume', 'volume_spike', 'volume_drop')),
    threshold_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    volume_ratio DECIMAL(8,4),
    alert_message TEXT,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. COMPANIES & FINANCIAL DATA
-- ============================================================================

-- Companies table
CREATE TABLE IF NOT EXISTS public.companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    website VARCHAR(255),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    listing_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. WATCHLISTS & ALERTS
-- ============================================================================

-- User watchlists
CREATE TABLE IF NOT EXISTS public.watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist items
CREATE TABLE IF NOT EXISTS public.watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID REFERENCES public.watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    UNIQUE(watchlist_id, ticker)
);

-- Price alerts
CREATE TABLE IF NOT EXISTS public.price_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('above', 'below', 'change_percent', 'volume_spike')),
    target_value DECIMAL(12,4) NOT NULL,
    current_value DECIMAL(12,4),
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMPTZ,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. SENTIMENT & VOTING SYSTEM
-- ============================================================================

-- Sentiment votes
CREATE TABLE IF NOT EXISTS public.sentiment_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(10) NOT NULL CHECK (sentiment IN ('bullish', 'bearish', 'neutral')),
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),
    reasoning TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_date DATE DEFAULT CURRENT_DATE
);

-- Add unique index for one vote per user per ticker per day
-- First ensure the created_date column exists
DO $$
BEGIN
    -- Add created_date column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'created_date' 
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.sentiment_votes ADD COLUMN created_date DATE DEFAULT CURRENT_DATE;
        
        -- Update existing rows to set created_date from created_at
        UPDATE public.sentiment_votes 
        SET created_date = created_at::date 
        WHERE created_date IS NULL;
    END IF;
    
    -- Add confidence_level column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'confidence_level' 
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.sentiment_votes ADD COLUMN confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5);
    END IF;
END $$;

-- Now create the unique index
CREATE UNIQUE INDEX IF NOT EXISTS unique_user_ticker_daily_vote 
ON public.sentiment_votes (user_id, ticker, created_date);

-- ============================================================================
-- 7. PAPER TRADING SYSTEM
-- ============================================================================

-- Paper trading accounts
CREATE TABLE IF NOT EXISTS public.paper_trading_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL DEFAULT 'Paper Trading Account',
    initial_balance DECIMAL(15,2) NOT NULL DEFAULT 100000.00,
    current_balance DECIMAL(15,2) NOT NULL DEFAULT 100000.00,
    total_pnl DECIMAL(15,2) DEFAULT 0.00,
    total_pnl_percent DECIMAL(8,6) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, account_name)
);

-- Paper trading positions
CREATE TABLE IF NOT EXISTS public.paper_trading_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID REFERENCES public.paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,6) NOT NULL DEFAULT 0.00,
    avg_cost DECIMAL(12,4) NOT NULL DEFAULT 0.00,
    total_cost DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    current_value DECIMAL(15,2) DEFAULT 0.00,
    unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
    unrealized_pnl_percent DECIMAL(8,6) DEFAULT 0.00,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, ticker)
);

-- ============================================================================
-- 8. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Volume data indexes
CREATE INDEX IF NOT EXISTS idx_volume_data_ticker_time ON public.volume_data (ticker, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_volume_data_alert ON public.volume_data (volume_alert) WHERE volume_alert = TRUE;
CREATE INDEX IF NOT EXISTS idx_volume_data_ratio ON public.volume_data (volume_ratio) WHERE volume_ratio > 2.0;

-- Quotes indexes
CREATE INDEX IF NOT EXISTS idx_quotes_ticker_time ON public.quotes (ticker, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_quotes_latest ON public.quotes (ticker, timestamp DESC);

-- Newsletter indexes
DO $$
BEGIN
    -- Check if newsletter_subscribers table and email column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'email' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON public.newsletter_subscribers (email);
    END IF;

    -- Check if newsletter_subscribers table and status column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'status' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_status ON public.newsletter_subscribers (status);
    END IF;

    -- Check if newsletter_campaigns table and status column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_campaigns' 
        AND column_name = 'status' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_status ON public.newsletter_campaigns (status);
    END IF;

    -- Check if newsletter_campaign_recipients table and status column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_campaign_recipients' 
        AND column_name = 'status' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_newsletter_campaign_recipients_status ON public.newsletter_campaign_recipients (status);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some newsletter indexes could not be created: %', SQLERRM;
END $$;

-- Watchlist indexes
DO $$
BEGIN
    -- Check if watchlist_items table and ticker column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'watchlist_items' 
        AND column_name = 'ticker' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON public.watchlist_items (ticker);
    END IF;

    -- Check if watchlists table and user_id column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'watchlists' 
        AND column_name = 'user_id' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON public.watchlists (user_id);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some watchlist indexes could not be created: %', SQLERRM;
END $$;

-- Alert indexes
DO $$
BEGIN
    -- Check if price_alerts table and required columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'price_alerts' 
        AND column_name = 'user_id' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'price_alerts' 
        AND column_name = 'is_active' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_price_alerts_user_active ON public.price_alerts (user_id, is_active) WHERE is_active = TRUE;
    END IF;

    -- Check if volume_alerts table and is_triggered column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'volume_alerts' 
        AND column_name = 'is_triggered' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_volume_alerts_triggered ON public.volume_alerts (is_triggered) WHERE is_triggered = TRUE;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some alert indexes could not be created: %', SQLERRM;
END $$;

-- Sentiment indexes
DO $$
BEGIN
    -- Check if sentiment_votes table and ticker column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'ticker' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON public.sentiment_votes (ticker);
    END IF;

    -- Check if sentiment_votes table and user_id, created_at columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'user_id' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'created_at' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_date ON public.sentiment_votes (user_id, created_at DESC);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some sentiment indexes could not be created: %', SQLERRM;
END $$;

-- Paper trading indexes
DO $$
BEGIN
    -- Check if paper_trading_accounts table and user_id column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'paper_trading_accounts' 
        AND column_name = 'user_id' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_paper_trading_accounts_user ON public.paper_trading_accounts (user_id);
    END IF;

    -- Check if paper_trading_positions table and account_id column exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'paper_trading_positions' 
        AND column_name = 'account_id' 
        AND table_schema = 'public'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_paper_trading_positions_account ON public.paper_trading_positions (account_id);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some paper trading indexes could not be created: %', SQLERRM;
END $$;

-- ============================================================================
-- 9. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
DO $$
BEGIN
    ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.newsletter_subscribers ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.newsletter_campaigns ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.newsletter_campaign_recipients ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.newsletter_templates ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.watchlists ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.watchlist_items ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.price_alerts ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.sentiment_votes ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.paper_trading_accounts ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.paper_trading_positions ENABLE ROW LEVEL SECURITY;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some tables may not exist, RLS setup may be incomplete';
END $$;

-- Users policies
DO $$
BEGIN
    DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
    CREATE POLICY "Users can view own profile" ON public.users
        FOR SELECT USING (auth.uid() = id);

    DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
    CREATE POLICY "Users can update own profile" ON public.users
        FOR UPDATE USING (auth.uid() = id);
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Users table RLS policies setup failed';
END $$;

-- All RLS policies
DO $$
BEGIN
    -- User profiles policies
    DROP POLICY IF EXISTS "Users can view own profile details" ON public.user_profiles;
    CREATE POLICY "Users can view own profile details" ON public.user_profiles
        FOR SELECT USING (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Users can update own profile details" ON public.user_profiles;
    CREATE POLICY "Users can update own profile details" ON public.user_profiles
        FOR UPDATE USING (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Users can insert own profile details" ON public.user_profiles;
    CREATE POLICY "Users can insert own profile details" ON public.user_profiles
        FOR INSERT WITH CHECK (auth.uid() = user_id);

    -- Newsletter subscribers policies (public read, authenticated insert/update)
    DROP POLICY IF EXISTS "Anyone can view newsletter subscribers" ON public.newsletter_subscribers;
    CREATE POLICY "Anyone can view newsletter subscribers" ON public.newsletter_subscribers
        FOR SELECT USING (true);

    DROP POLICY IF EXISTS "Anyone can subscribe to newsletter" ON public.newsletter_subscribers;
    CREATE POLICY "Anyone can subscribe to newsletter" ON public.newsletter_subscribers
        FOR INSERT WITH CHECK (true);

    DROP POLICY IF EXISTS "Subscribers can update own preferences" ON public.newsletter_subscribers;
    CREATE POLICY "Subscribers can update own preferences" ON public.newsletter_subscribers
        FOR UPDATE USING (email = (SELECT email FROM auth.users WHERE id = auth.uid()));

    -- Newsletter campaigns policies (admin only)
    DROP POLICY IF EXISTS "Only admins can manage campaigns" ON public.newsletter_campaigns;
    CREATE POLICY "Only admins can manage campaigns" ON public.newsletter_campaigns
        FOR ALL USING (
            EXISTS (
                SELECT 1 FROM public.users 
                WHERE id = auth.uid() 
                AND subscription_tier = 'institutional'
            )
        );

    -- Watchlists policies
    DROP POLICY IF EXISTS "Users can manage own watchlists" ON public.watchlists;
    CREATE POLICY "Users can manage own watchlists" ON public.watchlists
        FOR ALL USING (auth.uid() = user_id);

    -- Watchlist items policies
    DROP POLICY IF EXISTS "Users can manage own watchlist items" ON public.watchlist_items;
    CREATE POLICY "Users can manage own watchlist items" ON public.watchlist_items
        FOR ALL USING (
            EXISTS (
                SELECT 1 FROM public.watchlists 
                WHERE id = watchlist_id 
                AND user_id = auth.uid()
            )
        );

    -- Price alerts policies
    DROP POLICY IF EXISTS "Users can manage own price alerts" ON public.price_alerts;
    CREATE POLICY "Users can manage own price alerts" ON public.price_alerts
        FOR ALL USING (auth.uid() = user_id);

    -- Sentiment votes policies
    DROP POLICY IF EXISTS "Users can manage own sentiment votes" ON public.sentiment_votes;
    CREATE POLICY "Users can manage own sentiment votes" ON public.sentiment_votes
        FOR ALL USING (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Anyone can view sentiment votes" ON public.sentiment_votes;
    CREATE POLICY "Anyone can view sentiment votes" ON public.sentiment_votes
        FOR SELECT USING (true);

    -- Paper trading policies
    DROP POLICY IF EXISTS "Users can manage own paper trading accounts" ON public.paper_trading_accounts;
    CREATE POLICY "Users can manage own paper trading accounts" ON public.paper_trading_accounts
        FOR ALL USING (auth.uid() = user_id);

    DROP POLICY IF EXISTS "Users can manage own paper trading positions" ON public.paper_trading_positions;
    CREATE POLICY "Users can manage own paper trading positions" ON public.paper_trading_positions
        FOR ALL USING (
            EXISTS (
                SELECT 1 FROM public.paper_trading_accounts 
                WHERE id = account_id 
                AND user_id = auth.uid()
            )
        );
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Some RLS policies setup failed: %', SQLERRM;
END $$;

-- ============================================================================
-- 10. REAL-TIME SUBSCRIPTIONS
-- ============================================================================

-- Enable real-time for specific tables
DO $$
BEGIN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.quotes;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.volume_data;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.volume_alerts;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.sentiment_votes;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.price_alerts;
    RAISE NOTICE 'Real-time subscriptions enabled';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Real-time setup failed: %', SQLERRM;
END $$;

-- ============================================================================
-- 11. FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update user's updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
DO $$
BEGIN
    DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
    CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
    CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_newsletter_campaigns_updated_at ON public.newsletter_campaigns;
    CREATE TRIGGER update_newsletter_campaigns_updated_at BEFORE UPDATE ON public.newsletter_campaigns
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_watchlists_updated_at ON public.watchlists;
    CREATE TRIGGER update_watchlists_updated_at BEFORE UPDATE ON public.watchlists
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_price_alerts_updated_at ON public.price_alerts;
    CREATE TRIGGER update_price_alerts_updated_at BEFORE UPDATE ON public.price_alerts
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_sentiment_votes_updated_at ON public.sentiment_votes;
    CREATE TRIGGER update_sentiment_votes_updated_at BEFORE UPDATE ON public.sentiment_votes
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_paper_trading_accounts_updated_at ON public.paper_trading_accounts;
    CREATE TRIGGER update_paper_trading_accounts_updated_at BEFORE UPDATE ON public.paper_trading_accounts
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

    DROP TRIGGER IF EXISTS update_paper_trading_positions_updated_at ON public.paper_trading_positions;
    CREATE TRIGGER update_paper_trading_positions_updated_at BEFORE UPDATE ON public.paper_trading_positions
        FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
END $$;

-- Function to create default watchlist for new users
CREATE OR REPLACE FUNCTION public.create_default_watchlist()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.watchlists (user_id, name, is_default)
    VALUES (NEW.id, 'My Watchlist', TRUE);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to create default watchlist
DO $$
BEGIN
    DROP TRIGGER IF EXISTS create_default_watchlist_trigger ON public.users;
    CREATE TRIGGER create_default_watchlist_trigger
        AFTER INSERT ON public.users
        FOR EACH ROW EXECUTE FUNCTION public.create_default_watchlist();
END $$;

-- Function to create default paper trading account
CREATE OR REPLACE FUNCTION public.create_default_paper_account()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.paper_trading_accounts (user_id, account_name)
    VALUES (NEW.id, 'Paper Trading Account');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to set created_date from created_at
CREATE OR REPLACE FUNCTION public.set_created_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_date := NEW.created_at::date;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to create default paper trading account
DO $$
BEGIN
    DROP TRIGGER IF EXISTS create_default_paper_account_trigger ON public.users;
    CREATE TRIGGER create_default_paper_account_trigger
        AFTER INSERT ON public.users
        FOR EACH ROW EXECUTE FUNCTION public.create_default_paper_account();
END $$;

-- Trigger to set created_date for sentiment votes
DO $$
BEGIN
    DROP TRIGGER IF EXISTS set_sentiment_votes_created_date ON public.sentiment_votes;
    CREATE TRIGGER set_sentiment_votes_created_date
        BEFORE INSERT ON public.sentiment_votes
        FOR EACH ROW EXECUTE FUNCTION public.set_created_date();
END $$;

-- ============================================================================
-- 12. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Latest quotes view
DO $$
BEGIN
    -- Check if quotes table and required columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quotes' 
        AND column_name = 'ticker' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quotes' 
        AND column_name = 'timestamp' 
        AND table_schema = 'public'
    ) THEN
        CREATE OR REPLACE VIEW public.latest_quotes AS
        SELECT DISTINCT ON (ticker)
            ticker,
            timestamp,
            close AS price,
            change_amount,
            change_percent,
            volume,
            volume_ma_5,
            volume_ma_20,
            volume_ratio
        FROM public.quotes
        ORDER BY ticker, timestamp DESC;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Latest quotes view could not be created: %', SQLERRM;
END $$;

-- Volume alerts summary view
DO $$
BEGIN
    -- Check if volume_alerts table and required columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'volume_alerts' 
        AND column_name = 'ticker' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'volume_alerts' 
        AND column_name = 'is_triggered' 
        AND table_schema = 'public'
    ) THEN
        CREATE OR REPLACE VIEW public.volume_alerts_summary AS
        SELECT 
            ticker,
            COUNT(*) as alert_count,
            MAX(triggered_at) as last_alert,
            STRING_AGG(DISTINCT alert_type, ', ') as alert_types
        FROM public.volume_alerts
        WHERE is_triggered = TRUE
        GROUP BY ticker;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Volume alerts summary view could not be created: %', SQLERRM;
END $$;

-- Sentiment summary view
DO $$
BEGIN
    -- Check if sentiment_votes table and required columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'ticker' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'sentiment' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'confidence_level' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sentiment_votes' 
        AND column_name = 'created_at' 
        AND table_schema = 'public'
    ) THEN
        CREATE OR REPLACE VIEW public.sentiment_summary AS
        SELECT 
            ticker,
            sentiment,
            COUNT(*) as vote_count,
            AVG(confidence_level) as avg_confidence,
            MAX(created_at) as last_vote
        FROM public.sentiment_votes
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY ticker, sentiment;
    ELSE
        -- Create a simplified view without confidence_level if the column doesn't exist
        CREATE OR REPLACE VIEW public.sentiment_summary AS
        SELECT 
            ticker,
            sentiment,
            COUNT(*) as vote_count,
            NULL as avg_confidence,
            MAX(created_at) as last_vote
        FROM public.sentiment_votes
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY ticker, sentiment;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Sentiment summary view could not be created: %', SQLERRM;
END $$;

-- Newsletter subscriber stats view
DO $$
BEGIN
    -- Check if newsletter_subscribers table and required columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'status' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'open_count' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'email_count' 
        AND table_schema = 'public'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'newsletter_subscribers' 
        AND column_name = 'click_count' 
        AND table_schema = 'public'
    ) THEN
        CREATE OR REPLACE VIEW public.newsletter_stats AS
        SELECT 
            status,
            COUNT(*) as subscriber_count,
            AVG(open_count::DECIMAL / NULLIF(email_count, 0)) as avg_open_rate,
            AVG(click_count::DECIMAL / NULLIF(email_count, 0)) as avg_click_rate
        FROM public.newsletter_subscribers
        GROUP BY status;
    ELSE
        -- Create a simplified view without rate calculations if columns don't exist
        CREATE OR REPLACE VIEW public.newsletter_stats AS
        SELECT 
            status,
            COUNT(*) as subscriber_count,
            NULL as avg_open_rate,
            NULL as avg_click_rate
        FROM public.newsletter_subscribers
        GROUP BY status;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Newsletter stats view could not be created: %', SQLERRM;
END $$;

-- ============================================================================
-- 13. SAMPLE DATA
-- ============================================================================

-- Insert sample companies
INSERT INTO public.companies (ticker, name, sector, industry) VALUES
('MASI', 'MASI Index', 'Index', 'Market Index'),
('MADEX', 'MADEX Index', 'Index', 'Market Index'),
('ATW', 'Attijariwafa Bank', 'Financial Services', 'Banks'),
('IAM', 'Maroc Telecom', 'Communication Services', 'Telecoms'),
('BCP', 'Banque Centrale Populaire', 'Financial Services', 'Banks'),
('BMCE', 'BMCE Bank', 'Financial Services', 'Banks'),
('ONA', 'Omnium Nord Africain', 'Conglomerates', 'Diversified Holdings'),
('CMT', 'Ciments du Maroc', 'Materials', 'Building Materials'),
('LAFA', 'Lafarge Ciments', 'Materials', 'Building Materials'),
('CIH', 'CIH Bank', 'Financial Services', 'Banks')
ON CONFLICT (ticker) DO NOTHING;

-- Insert sample newsletter template
INSERT INTO public.newsletter_templates (name, subject_template, content_template, variables) VALUES
('Weekly Market Recap', 'Weekly Market Recap - {date}', 
'Here is your weekly market recap for {date}:

Top Performers:
{top_performers}

Volume Leaders:
{volume_leaders}

Market Summary:
{market_summary}

Stay tuned for more insights!',
'["date", "top_performers", "volume_leaders", "market_summary"]')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 14. COMPRESSION & RETENTION POLICIES
-- ============================================================================

-- Enable compression for older data (if TimescaleDB is available)
DO $$
BEGIN
    PERFORM add_compression_policy('quotes', INTERVAL '7 days');
    PERFORM add_compression_policy('volume_data', INTERVAL '7 days');
    RAISE NOTICE 'Compression policies added';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB not available, compression policies skipped';
END $$;

-- Data retention policies (if TimescaleDB is available)
DO $$
BEGIN
    PERFORM add_retention_policy('quotes', INTERVAL '5 years');
    PERFORM add_retention_policy('volume_data', INTERVAL '5 years');
    RAISE NOTICE 'Retention policies added';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'TimescaleDB not available, retention policies skipped';
END $$;

-- ============================================================================
-- 15. GRANTS & PERMISSIONS
-- ============================================================================

-- Grant permissions to authenticated users
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.users TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.user_profiles TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.watchlists TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.watchlist_items TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.price_alerts TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.sentiment_votes TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.paper_trading_accounts TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.paper_trading_positions TO authenticated;

-- Grant permissions to anon users (for newsletter signup)
GRANT SELECT ON public.newsletter_subscribers TO anon;
GRANT INSERT ON public.newsletter_subscribers TO anon;
GRANT SELECT ON public.companies TO anon;
GRANT SELECT ON public.latest_quotes TO anon;
GRANT SELECT ON public.sentiment_summary TO anon;

-- Grant permissions to service role (for admin operations)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- ============================================================================
-- 16. COMMENTS & DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE public.users IS 'User profiles extending Supabase auth.users';
COMMENT ON TABLE public.newsletter_subscribers IS 'Newsletter subscription management';
COMMENT ON TABLE public.volume_data IS 'Volume data with moving averages and alerts';
COMMENT ON TABLE public.quotes IS 'Market quotes with volume analysis';
COMMENT ON TABLE public.watchlists IS 'User watchlists for tracking stocks';
COMMENT ON TABLE public.sentiment_votes IS 'User sentiment voting system';
COMMENT ON TABLE public.paper_trading_accounts IS 'Paper trading simulation accounts';

COMMENT ON COLUMN public.volume_data.volume_ratio IS 'Current volume / 20-day average volume';
COMMENT ON COLUMN public.volume_data.volume_alert IS 'True when volume > 2x 20-day average';
COMMENT ON COLUMN public.sentiment_votes.confidence_level IS '1-5 scale indicating confidence in sentiment';

-- ============================================================================
-- SCHEMA COMPLETE
-- ============================================================================

-- Log successful schema creation (if etl_jobs table exists)
DO $$
BEGIN
    INSERT INTO public.etl_jobs (job_type, status, records_processed, metadata)
    VALUES ('schema_setup', 'completed', 0, '{"version": "2.0", "features": ["rls", "realtime", "volume_data", "newsletter"]}');
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Schema setup completed (etl_jobs table may not exist)';
END $$; 