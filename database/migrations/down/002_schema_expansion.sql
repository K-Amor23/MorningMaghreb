-- Down Migration: 002_schema_expansion
-- Description: Rollback schema expansion

DROP TRIGGER IF EXISTS update_portfolio_holdings_updated_at ON portfolio_holdings;
DROP TRIGGER IF EXISTS update_portfolios_updated_at ON portfolios;

DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS portfolio_holdings;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS news_articles;
DROP TABLE IF EXISTS financial_reports;
