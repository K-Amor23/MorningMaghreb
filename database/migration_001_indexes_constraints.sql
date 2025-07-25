-- Migration 001: Add indexes and constraints for companies, prices, reports, news tables
-- This migration optimizes query performance and ensures data integrity

-- ============================================
-- ADDITIONAL INDEXES FOR PERFORMANCE
-- ============================================

-- Companies table indexes
CREATE INDEX IF NOT EXISTS idx_companies_company_id ON companies(id);
CREATE INDEX IF NOT EXISTS idx_companies_name_lower ON companies(LOWER(name));
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_exchange ON companies(exchange);
CREATE INDEX IF NOT EXISTS idx_companies_updated_at ON companies(updated_at);
CREATE INDEX IF NOT EXISTS idx_companies_created_at ON companies(created_at);

-- Company Prices table indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_company_id ON company_prices(company_id);
CREATE INDEX IF NOT EXISTS idx_company_prices_close ON company_prices(close);
CREATE INDEX IF NOT EXISTS idx_company_prices_volume ON company_prices(volume);
CREATE INDEX IF NOT EXISTS idx_company_prices_created_at ON company_prices(created_at);
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date_range ON company_prices(ticker, date) WHERE date >= CURRENT_DATE - INTERVAL '1 year';

-- Company Reports table indexes
CREATE INDEX IF NOT EXISTS idx_company_reports_company_id ON company_reports(company_id);
CREATE INDEX IF NOT EXISTS idx_company_reports_title_lower ON company_reports(LOWER(title));
CREATE INDEX IF NOT EXISTS idx_company_reports_created_at ON company_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker_type ON company_reports(ticker, report_type);
CREATE INDEX IF NOT EXISTS idx_company_reports_ticker_year ON company_reports(ticker, report_year);

-- Company News table indexes
CREATE INDEX IF NOT EXISTS idx_company_news_company_id ON company_news(company_id);
CREATE INDEX IF NOT EXISTS idx_company_news_headline_lower ON company_news(LOWER(headline));
CREATE INDEX IF NOT EXISTS idx_company_news_source ON company_news(source);
CREATE INDEX IF NOT EXISTS idx_company_news_created_at ON company_news(created_at);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_sentiment ON company_news(ticker, sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_ticker_date_range ON company_news(ticker, published_at) WHERE published_at >= CURRENT_DATE - INTERVAL '30 days';

-- Analytics Signals table indexes
CREATE INDEX IF NOT EXISTS idx_analytics_signals_company_id ON analytics_signals(company_id);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_confidence ON analytics_signals(confidence);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_created_at ON analytics_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_signals_ticker_type_date ON analytics_signals(ticker, signal_type, signal_date);

-- ============================================
-- ADDITIONAL CONSTRAINTS FOR DATA INTEGRITY
-- ============================================

-- Companies table constraints
ALTER TABLE companies 
ADD CONSTRAINT chk_companies_ticker_format CHECK (ticker ~ '^[A-Z]{1,10}$'),
ADD CONSTRAINT chk_companies_price_positive CHECK (price >= 0),
ADD CONSTRAINT chk_companies_market_cap_positive CHECK (market_cap_billion >= 0),
ADD CONSTRAINT chk_companies_change_percent_range CHECK (change_1d_percent >= -100 AND change_1d_percent <= 1000),
ADD CONSTRAINT chk_companies_change_ytd_range CHECK (change_ytd_percent >= -100 AND change_ytd_percent <= 1000);

-- Company Prices table constraints
ALTER TABLE company_prices 
ADD CONSTRAINT chk_prices_ohlc_positive CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
ADD CONSTRAINT chk_prices_high_low CHECK (high >= low),
ADD CONSTRAINT chk_prices_volume_positive CHECK (volume >= 0),
ADD CONSTRAINT chk_prices_date_not_future CHECK (date <= CURRENT_DATE),
ADD CONSTRAINT chk_prices_ticker_format CHECK (ticker ~ '^[A-Z]{1,10}$');

-- Company Reports table constraints
ALTER TABLE company_reports 
ADD CONSTRAINT chk_reports_ticker_format CHECK (ticker ~ '^[A-Z]{1,10}$'),
ADD CONSTRAINT chk_reports_year_valid CHECK (report_year ~ '^[0-9]{4}$'),
ADD CONSTRAINT chk_reports_url_valid CHECK (url ~ '^https?://'),
ADD CONSTRAINT chk_reports_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);

-- Company News table constraints
ALTER TABLE company_news 
ADD CONSTRAINT chk_news_ticker_format CHECK (ticker ~ '^[A-Z]{1,10}$'),
ADD CONSTRAINT chk_news_sentiment_score_range CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
ADD CONSTRAINT chk_news_published_not_future CHECK (published_at <= CURRENT_TIMESTAMP),
ADD CONSTRAINT chk_news_headline_not_empty CHECK (LENGTH(TRIM(headline)) > 0);

-- Analytics Signals table constraints
ALTER TABLE analytics_signals 
ADD CONSTRAINT chk_signals_ticker_format CHECK (ticker ~ '^[A-Z]{1,10}$'),
ADD CONSTRAINT chk_signals_confidence_range CHECK (confidence >= 0 AND confidence <= 1),
ADD CONSTRAINT chk_signals_date_not_future CHECK (signal_date <= CURRENT_DATE),
ADD CONSTRAINT chk_signals_value_positive CHECK (value >= 0);

-- ============================================
-- FOREIGN KEY CONSTRAINTS (if not already present)
-- ============================================

-- Ensure foreign key constraints exist
DO $$
BEGIN
    -- Company Prices foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'company_prices_company_id_fkey'
    ) THEN
        ALTER TABLE company_prices 
        ADD CONSTRAINT company_prices_company_id_fkey 
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
    END IF;

    -- Company Reports foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'company_reports_company_id_fkey'
    ) THEN
        ALTER TABLE company_reports 
        ADD CONSTRAINT company_reports_company_id_fkey 
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
    END IF;

    -- Company News foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'company_news_company_id_fkey'
    ) THEN
        ALTER TABLE company_news 
        ADD CONSTRAINT company_news_company_id_fkey 
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
    END IF;

    -- Analytics Signals foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'analytics_signals_company_id_fkey'
    ) THEN
        ALTER TABLE analytics_signals 
        ADD CONSTRAINT analytics_signals_company_id_fkey 
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================
-- PARTIAL INDEXES FOR COMMON QUERIES
-- ============================================

-- Active companies only
CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(ticker, name, sector) WHERE is_active = TRUE;

-- Recent prices (last 30 days)
CREATE INDEX IF NOT EXISTS idx_company_prices_recent ON company_prices(ticker, date, close) 
WHERE date >= CURRENT_DATE - INTERVAL '30 days';

-- Recent news (last 7 days)
CREATE INDEX IF NOT EXISTS idx_company_news_recent ON company_news(ticker, published_at, sentiment) 
WHERE published_at >= CURRENT_DATE - INTERVAL '7 days';

-- Recent reports (last 2 years)
CREATE INDEX IF NOT EXISTS idx_company_reports_recent ON company_reports(ticker, report_type, report_year) 
WHERE report_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 2;

-- ============================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- ============================================

-- Company overview queries
CREATE INDEX IF NOT EXISTS idx_companies_overview ON companies(ticker, name, sector, market_cap_billion, price, change_1d_percent);

-- Price analysis queries
CREATE INDEX IF NOT EXISTS idx_company_prices_analysis ON company_prices(ticker, date, close, volume, adjusted_close);

-- News sentiment analysis
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment_analysis ON company_news(ticker, published_at, sentiment, sentiment_score);

-- Report type and year queries
CREATE INDEX IF NOT EXISTS idx_company_reports_type_year ON company_reports(ticker, report_type, report_year, report_quarter);

-- ============================================
-- MIGRATION COMPLETION
-- ============================================

-- Log migration completion
INSERT INTO schema_migrations (version, applied_at) 
VALUES ('001_indexes_constraints', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

-- Create schema_migrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
); 