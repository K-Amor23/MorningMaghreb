-- Contest and AI Features Database Schema
-- Add these tables to your existing Supabase project

-- 1. Contest Tables
CREATE TABLE IF NOT EXISTS contests (
    contest_id VARCHAR(50) PRIMARY KEY,
    contest_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    prize_pool DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    winner_id UUID REFERENCES auth.users(id),
    total_participants INTEGER DEFAULT 0,
    rules JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_contests_status ON contests(status);
CREATE INDEX IF NOT EXISTS idx_contests_dates ON contests(start_date, end_date);

-- 2. Contest Entries Table
CREATE TABLE IF NOT EXISTS contest_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES paper_trading_accounts(id),
    username VARCHAR(255),
    initial_balance DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    total_return DECIMAL(15,2) DEFAULT 0.00,
    total_return_percent DECIMAL(8,6) DEFAULT 0.00,
    position_count INTEGER DEFAULT 0,
    rank INTEGER,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'withdrawn', 'disqualified')),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(contest_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_contest_entries_contest_id ON contest_entries(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_entries_user_id ON contest_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_contest_entries_rank ON contest_entries(rank);

-- 3. Contest Prizes Table
CREATE TABLE IF NOT EXISTS contest_prizes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    winner_id UUID REFERENCES auth.users(id),
    prize_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'distributed', 'failed')),
    distributed_at TIMESTAMPTZ,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contest_prizes_contest_id ON contest_prizes(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_prizes_winner_id ON contest_prizes(winner_id);

-- 4. Contest Notifications Table
CREATE TABLE IF NOT EXISTS contest_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    contest_id VARCHAR(50) REFERENCES contests(contest_id),
    notification_type VARCHAR(50) NOT NULL, -- 'rank_change', 'prize_won', 'contest_ending', etc.
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contest_notifications_user_id ON contest_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_contest_notifications_contest_id ON contest_notifications(contest_id);
CREATE INDEX IF NOT EXISTS idx_contest_notifications_read ON contest_notifications(is_read);

-- 5. AI Summaries Table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    summary TEXT NOT NULL,
    company_data JSONB,
    tokens_used INTEGER DEFAULT 0,
    model_used VARCHAR(50) DEFAULT 'gpt-4o-mini',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, language)
);

CREATE INDEX IF NOT EXISTS idx_ai_summaries_ticker ON ai_summaries(ticker);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_language ON ai_summaries(language);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_created_at ON ai_summaries(created_at);

-- 6. AI Chat Queries Table (Enhanced)
CREATE TABLE IF NOT EXISTS ai_chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    context JSONB,
    tokens_used INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    model_used VARCHAR(50) DEFAULT 'gpt-4o-mini',
    cost_usd DECIMAL(10,6) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_chat_queries_user_id ON ai_chat_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_chat_queries_created_at ON ai_chat_queries(created_at);

-- 7. AI Usage Tracking Table
CREATE TABLE IF NOT EXISTS ai_usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,6) DEFAULT 0.00,
    query_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_tracking_user_id ON ai_usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_tracking_date ON ai_usage_tracking(date);

-- 8. Sentiment Analysis Table (Enhanced)
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'news', 'social', 'earnings_call'
    content TEXT NOT NULL,
    sentiment_score DECIMAL(3,2), -- -1.0 to 1.0
    sentiment_label VARCHAR(20), -- 'positive', 'negative', 'neutral'
    confidence_score DECIMAL(3,2),
    keywords TEXT[],
    ai_analysis TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_ticker ON sentiment_analysis(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_sentiment ON sentiment_analysis(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_created_at ON sentiment_analysis(created_at);

-- 9. Portfolio Analysis Cache Table
CREATE TABLE IF NOT EXISTS portfolio_analysis_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL,
    analysis_data JSONB NOT NULL,
    ai_insights TEXT,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 hour')
);

CREATE INDEX IF NOT EXISTS idx_portfolio_analysis_cache_portfolio_id ON portfolio_analysis_cache(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_analysis_cache_expires_at ON portfolio_analysis_cache(expires_at);

-- Row Level Security Policies

-- Contest entries - users can only see their own entries
ALTER TABLE contest_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own contest entries" ON contest_entries
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own contest entries" ON contest_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own contest entries" ON contest_entries
    FOR UPDATE USING (auth.uid() = user_id);

-- Contest notifications - users can only see their own notifications
ALTER TABLE contest_notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own notifications" ON contest_notifications
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own notifications" ON contest_notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- AI summaries - public read, authenticated write
ALTER TABLE ai_summaries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public can read AI summaries" ON ai_summaries
    FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert AI summaries" ON ai_summaries
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- AI chat queries - users can only see their own queries
ALTER TABLE ai_chat_queries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own chat queries" ON ai_chat_queries
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own chat queries" ON ai_chat_queries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- AI usage tracking - users can only see their own usage
ALTER TABLE ai_usage_tracking ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own usage" ON ai_usage_tracking
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own usage" ON ai_usage_tracking
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Portfolio analysis cache - users can only see their own analysis
ALTER TABLE portfolio_analysis_cache ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own portfolio analysis" ON portfolio_analysis_cache
    FOR SELECT USING (auth.uid()::text = portfolio_id::text);
CREATE POLICY "Users can insert their own portfolio analysis" ON portfolio_analysis_cache
    FOR INSERT WITH CHECK (auth.uid()::text = portfolio_id::text);

-- Functions for contest management

-- Function to update contest rankings
CREATE OR REPLACE FUNCTION update_contest_rankings(contest_id_param VARCHAR(50))
RETURNS VOID AS $$
BEGIN
    UPDATE contest_entries 
    SET rank = subquery.new_rank
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (ORDER BY total_return_percent DESC) as new_rank
        FROM contest_entries 
        WHERE contest_id = contest_id_param AND status = 'active'
    ) as subquery
    WHERE contest_entries.id = subquery.id;
END;
$$ LANGUAGE plpgsql;

-- Function to check contest eligibility
CREATE OR REPLACE FUNCTION check_contest_eligibility(user_id_param UUID, contest_id_param VARCHAR(50))
RETURNS BOOLEAN AS $$
DECLARE
    position_count INTEGER;
    min_positions INTEGER;
BEGIN
    -- Get minimum positions requirement
    SELECT (rules->>'min_positions')::INTEGER INTO min_positions
    FROM contests WHERE contest_id = contest_id_param;
    
    -- Get user's position count
    SELECT COUNT(*) INTO position_count
    FROM paper_trading_positions ptp
    JOIN paper_trading_accounts pta ON ptp.account_id = pta.id
    WHERE pta.user_id = user_id_param AND ptp.quantity > 0;
    
    RETURN position_count >= COALESCE(min_positions, 3);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate contest statistics
CREATE OR REPLACE FUNCTION get_contest_stats(contest_id_param VARCHAR(50))
RETURNS JSON AS $$
DECLARE
    stats JSON;
BEGIN
    SELECT json_build_object(
        'total_participants', COUNT(*),
        'total_prize_pool', (SELECT prize_pool FROM contests WHERE contest_id = contest_id_param),
        'avg_return', AVG(total_return_percent),
        'max_return', MAX(total_return_percent),
        'min_return', MIN(total_return_percent),
        'active_entries', COUNT(*) FILTER (WHERE status = 'active')
    ) INTO stats
    FROM contest_entries 
    WHERE contest_id = contest_id_param;
    
    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- Insert sample contest data
INSERT INTO contests (contest_id, contest_name, start_date, end_date, prize_pool, status, rules) 
VALUES (
    'contest_2024_01',
    'Monthly Portfolio Contest',
    '2024-01-01',
    '2024-02-01',
    100.00,
    'active',
    '{"min_positions": 3, "ranking_metric": "percentage_return", "eligibility": "registered_users_with_minimum_positions"}'
) ON CONFLICT (contest_id) DO NOTHING; 