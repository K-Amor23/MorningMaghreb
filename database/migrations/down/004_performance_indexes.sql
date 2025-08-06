-- Down Migration: 004_performance_indexes
-- Description: Remove performance indexes

DROP INDEX IF EXISTS idx_news_articles_title_search;
DROP INDEX IF EXISTS idx_companies_name_search;
DROP INDEX IF EXISTS idx_portfolios_public;
DROP INDEX IF EXISTS idx_alerts_active_ticker;
DROP INDEX IF EXISTS idx_news_articles_tickers;
DROP INDEX IF EXISTS idx_financial_reports_type_period;
DROP INDEX IF EXISTS idx_companies_sector_market_cap;
DROP INDEX IF EXISTS idx_market_data_ticker_date_price;
