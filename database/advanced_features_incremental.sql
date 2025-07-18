-- Advanced Features Incremental Database Schema
-- This script safely adds missing tables for advanced features
-- It uses IF NOT EXISTS to avoid overwriting existing data

-- Enable TimescaleDB extension if not already enabled
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================
-- SENTIMENT VOTING SYSTEM TABLES
-- ============================================

-- Sentiment Votes Table (User sentiment votes)
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Will reference users.id when auth is set up
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

-- Create indexes for sentiment tables
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_bullish_count ON sentiment_aggregates(bullish_count DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_bearish_count ON sentiment_aggregates(bearish_count DESC);

-- ============================================
-- NEWSLETTER SYSTEM TABLES
-- ============================================

-- Newsletter Subscribers (if not already exists)
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

-- Newsletter Campaigns (if not already exists)
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

-- Newsletter Logs (if not already exists)
CREATE TABLE IF NOT EXISTS newsletter_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES newsletter_campaigns(id),
    subscriber_id UUID REFERENCES newsletter_subscribers(id),
    status VARCHAR(20) CHECK (status IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- MOBILE WIDGETS CONFIGURATION
-- ============================================

-- Widget Configurations (for mobile widgets)
CREATE TABLE IF NOT EXISTS widget_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Will reference users.id when auth is set up
    widget_type VARCHAR(50) NOT NULL CHECK (widget_type IN ('masi_widget', 'watchlist_widget', 'macro_widget')),
    widget_size VARCHAR(20) DEFAULT 'medium' CHECK (widget_size IN ('small', 'medium', 'large')),
    refresh_interval INTEGER DEFAULT 15, -- minutes
    max_items INTEGER DEFAULT 5,
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, widget_type)
);

-- Widget Usage Analytics
CREATE TABLE IF NOT EXISTS widget_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    widget_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('view', 'refresh', 'tap', 'configure')),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- ============================================
-- MISSING INDEXES FOR PERFORMANCE
-- ============================================

-- Newsletter indexes
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_status ON newsletter_subscribers(status);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_type ON newsletter_campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_newsletter_campaigns_sent_at ON newsletter_campaigns(sent_at);
CREATE INDEX IF NOT EXISTS idx_newsletter_logs_campaign_id ON newsletter_logs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_newsletter_logs_subscriber_id ON newsletter_logs(subscriber_id);

-- Widget indexes
CREATE INDEX IF NOT EXISTS idx_widget_configurations_user_id ON widget_configurations(user_id);
CREATE INDEX IF NOT EXISTS idx_widget_configurations_type ON widget_configurations(widget_type);
CREATE INDEX IF NOT EXISTS idx_widget_analytics_user_id ON widget_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_widget_analytics_timestamp ON widget_analytics(timestamp);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update sentiment aggregates
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Get ticker from the vote
    DECLARE
        vote_ticker VARCHAR(10);
    BEGIN
        -- Handle different trigger operations
        IF TG_OP = 'DELETE' THEN
            vote_ticker := OLD.ticker;
        ELSE
            vote_ticker := NEW.ticker;
        END IF;

        -- Calculate new aggregates
        WITH vote_counts AS (
            SELECT 
                ticker,
                COUNT(*) as total_votes,
                COUNT(*) FILTER (WHERE sentiment = 'bullish') as bullish_count,
                COUNT(*) FILTER (WHERE sentiment = 'neutral') as neutral_count,
                COUNT(*) FILTER (WHERE sentiment = 'bearish') as bearish_count,
                AVG(confidence) as average_confidence
            FROM sentiment_votes 
            WHERE ticker = vote_ticker
            GROUP BY ticker
        )
        INSERT INTO sentiment_aggregates (
            ticker, 
            bullish_count, 
            neutral_count, 
            bearish_count, 
            total_votes,
            bullish_percentage,
            neutral_percentage,
            bearish_percentage,
            average_confidence,
            last_updated
        )
        SELECT 
            vote_ticker,
            COALESCE(bullish_count, 0),
            COALESCE(neutral_count, 0),
            COALESCE(bearish_count, 0),
            COALESCE(total_votes, 0),
            CASE WHEN COALESCE(total_votes, 0) > 0 THEN (COALESCE(bullish_count, 0)::DECIMAL / total_votes) * 100 ELSE 0 END,
            CASE WHEN COALESCE(total_votes, 0) > 0 THEN (COALESCE(neutral_count, 0)::DECIMAL / total_votes) * 100 ELSE 0 END,
            CASE WHEN COALESCE(total_votes, 0) > 0 THEN (COALESCE(bearish_count, 0)::DECIMAL / total_votes) * 100 ELSE 0 END,
            COALESCE(average_confidence, 0),
            NOW()
        FROM vote_counts
        WHERE EXISTS (SELECT 1 FROM vote_counts)
        ON CONFLICT (ticker) DO UPDATE SET
            bullish_count = EXCLUDED.bullish_count,
            neutral_count = EXCLUDED.neutral_count,
            bearish_count = EXCLUDED.bearish_count,
            total_votes = EXCLUDED.total_votes,
            bullish_percentage = EXCLUDED.bullish_percentage,
            neutral_percentage = EXCLUDED.neutral_percentage,
            bearish_percentage = EXCLUDED.bearish_percentage,
            average_confidence = EXCLUDED.average_confidence,
            last_updated = NOW();

        -- If no votes left, delete the aggregate
        IF TG_OP = 'DELETE' AND NOT EXISTS (SELECT 1 FROM sentiment_votes WHERE ticker = vote_ticker) THEN
            DELETE FROM sentiment_aggregates WHERE ticker = vote_ticker;
        END IF;

        RETURN COALESCE(NEW, OLD);
    END;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for sentiment aggregates (drop first to avoid conflicts)
DROP TRIGGER IF EXISTS sentiment_votes_insert_trigger ON sentiment_votes;
DROP TRIGGER IF EXISTS sentiment_votes_update_trigger ON sentiment_votes;
DROP TRIGGER IF EXISTS sentiment_votes_delete_trigger ON sentiment_votes;

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

-- ============================================
-- VIEWS FOR EASY QUERYING
-- ============================================

-- Top sentiment stocks views
CREATE OR REPLACE VIEW top_bullish_stocks AS
SELECT 
    ticker,
    bullish_count,
    total_votes,
    bullish_percentage,
    average_confidence
FROM sentiment_aggregates
WHERE total_votes >= 5
ORDER BY bullish_percentage DESC, total_votes DESC;

CREATE OR REPLACE VIEW top_bearish_stocks AS
SELECT 
    ticker,
    bearish_count,
    total_votes,
    bearish_percentage,
    average_confidence
FROM sentiment_aggregates
WHERE total_votes >= 5
ORDER BY bearish_percentage DESC, total_votes DESC;

-- Newsletter campaign performance view
CREATE OR REPLACE VIEW newsletter_campaign_performance AS
SELECT 
    c.id,
    c.subject,
    c.campaign_type,
    c.language,
    c.sent_at,
    c.recipient_count,
    c.open_count,
    c.click_count,
    CASE 
        WHEN c.recipient_count > 0 
        THEN (c.open_count::DECIMAL / c.recipient_count) * 100 
        ELSE 0 
    END as open_rate,
    CASE 
        WHEN c.open_count > 0 
        THEN (c.click_count::DECIMAL / c.open_count) * 100 
        ELSE 0 
    END as click_through_rate
FROM newsletter_campaigns c
WHERE c.sent_at IS NOT NULL
ORDER BY c.sent_at DESC;

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Insert sample newsletter subscribers
INSERT INTO newsletter_subscribers (email, name, status, preferences) VALUES
('test@example.com', 'Test User', 'active', '{"frequency": "weekly", "language": "en"}'),
('demo@casablanca-insight.com', 'Demo User', 'active', '{"frequency": "weekly", "language": "fr"}')
ON CONFLICT (email) DO NOTHING;

-- Insert sample sentiment votes (only if no existing votes)
INSERT INTO sentiment_votes (user_id, ticker, sentiment, confidence) VALUES
('00000000-0000-0000-0000-000000000001', 'ATW', 'bullish', 4),
('00000000-0000-0000-0000-000000000002', 'ATW', 'bullish', 3),
('00000000-0000-0000-0000-000000000003', 'ATW', 'neutral', 2),
('00000000-0000-0000-0000-000000000001', 'BMCE', 'bearish', 5),
('00000000-0000-0000-0000-000000000002', 'BMCE', 'bearish', 4),
('00000000-0000-0000-0000-000000000003', 'BMCE', 'neutral', 3)
ON CONFLICT (user_id, ticker) DO NOTHING;

-- Create update trigger function for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers for tables with updated_at columns
CREATE TRIGGER update_sentiment_votes_updated_at 
    BEFORE UPDATE ON sentiment_votes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_widget_configurations_updated_at 
    BEFORE UPDATE ON widget_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PERMISSIONS AND SECURITY
-- ============================================

-- Note: Add proper user permissions when you set up your authentication system
-- Example:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sentiment_votes TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sentiment_aggregates TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON newsletter_subscribers TO your_app_user;
-- etc.

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Uncomment these to verify the tables were created successfully:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%sentiment%';
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%newsletter%';
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%widget%'; 