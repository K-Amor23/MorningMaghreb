-- Sentiment Voting System Schema
-- Add these tables to your existing database

-- Sentiment Votes Table
CREATE TABLE IF NOT EXISTS sentiment_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
    confidence INTEGER NOT NULL DEFAULT 3 CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);

-- Sentiment Aggregates Table
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

-- Create indexes for sentiment aggregates
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_bullish_count ON sentiment_aggregates(bullish_count DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_bearish_count ON sentiment_aggregates(bearish_count DESC);

-- Row Level Security Policies for Sentiment Votes
ALTER TABLE sentiment_votes ENABLE ROW LEVEL SECURITY;

-- Users can only see their own votes
CREATE POLICY "Users can view own sentiment votes" ON sentiment_votes
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own votes
CREATE POLICY "Users can insert own sentiment votes" ON sentiment_votes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own votes
CREATE POLICY "Users can update own sentiment votes" ON sentiment_votes
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own votes
CREATE POLICY "Users can delete own sentiment votes" ON sentiment_votes
    FOR DELETE USING (auth.uid() = user_id);

-- Row Level Security Policies for Sentiment Aggregates
ALTER TABLE sentiment_aggregates ENABLE ROW LEVEL SECURITY;

-- Everyone can view sentiment aggregates (public data)
CREATE POLICY "Everyone can view sentiment aggregates" ON sentiment_aggregates
    FOR SELECT USING (true);

-- Only authenticated users can update aggregates (via triggers)
CREATE POLICY "Authenticated users can update sentiment aggregates" ON sentiment_aggregates
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Function to update sentiment aggregate when votes change
CREATE OR REPLACE FUNCTION update_sentiment_aggregate()
RETURNS TRIGGER AS $$
BEGIN
    -- Delete old aggregate if no votes exist
    IF TG_OP = 'DELETE' THEN
        DELETE FROM sentiment_aggregates WHERE ticker = OLD.ticker;
        RETURN OLD;
    END IF;

    -- Get ticker from the vote
    DECLARE
        vote_ticker VARCHAR(10);
    BEGIN
        IF TG_OP = 'INSERT' THEN
            vote_ticker := NEW.ticker;
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
            ticker,
            bullish_count,
            neutral_count,
            bearish_count,
            total_votes,
            CASE WHEN total_votes > 0 THEN (bullish_count::DECIMAL / total_votes) * 100 ELSE 0 END,
            CASE WHEN total_votes > 0 THEN (neutral_count::DECIMAL / total_votes) * 100 ELSE 0 END,
            CASE WHEN total_votes > 0 THEN (bearish_count::DECIMAL / total_votes) * 100 ELSE 0 END,
            average_confidence,
            NOW()
        FROM vote_counts
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

        RETURN COALESCE(NEW, OLD);
    END;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update aggregates
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

-- Views for easy querying
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

-- Sample data for testing
INSERT INTO sentiment_votes (user_id, ticker, sentiment, confidence) VALUES
    ('00000000-0000-0000-0000-000000000001', 'ATW', 'bullish', 4),
    ('00000000-0000-0000-0000-000000000002', 'ATW', 'bullish', 3),
    ('00000000-0000-0000-0000-000000000003', 'ATW', 'neutral', 2),
    ('00000000-0000-0000-0000-000000000001', 'BMCE', 'bearish', 5),
    ('00000000-0000-0000-0000-000000000002', 'BMCE', 'bearish', 4),
    ('00000000-0000-0000-0000-000000000003', 'BMCE', 'neutral', 3)
ON CONFLICT (user_id, ticker) DO NOTHING; 