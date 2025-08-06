-- Migration: 004_performance_indexes
-- Description: Add performance indexes for better query performance
-- Created: 2025-08-06T16:16:17.157373

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date_price ON market_data(ticker, date, price);
CREATE INDEX IF NOT EXISTS idx_companies_sector_market_cap ON companies(sector, market_cap);
CREATE INDEX IF NOT EXISTS idx_financial_reports_type_period ON financial_reports(report_type, period);
CREATE INDEX IF NOT EXISTS idx_news_articles_tickers ON news_articles USING GIN(tickers);

-- Partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_alerts_active_ticker ON alerts(ticker) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_portfolios_public ON portfolios(id) WHERE is_public = TRUE;

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_title_search ON news_articles USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_companies_name_search ON companies USING GIN(to_tsvector('english', name));

-- Statistics for query planner
ANALYZE companies;
ANALYZE market_data;
ANALYZE financial_reports;
ANALYZE news_articles;
