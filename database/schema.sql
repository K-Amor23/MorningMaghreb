-- Casablanca Insight Database Schema
-- PostgreSQL with TimescaleDB extension for time-series data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'institutional')),
    subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'canceled', 'past_due')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    language_preference VARCHAR(10) DEFAULT 'en' CHECK (language_preference IN ('en', 'fr', 'ar')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys for Premium Access
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions JSONB DEFAULT '{}',
    rate_limit_per_hour INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX idx_api_keys_hash ON api_keys (api_key_hash);

-- Data Exports
CREATE TABLE data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL, -- 'financials', 'macro', 'portfolio', 'custom'
    file_format VARCHAR(10) NOT NULL CHECK (file_format IN ('csv', 'xlsx', 'json')),
    file_path VARCHAR(500),
    file_size_bytes BIGINT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    filters JSONB DEFAULT '{}',
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_data_exports_user_id ON data_exports (user_id);
CREATE INDEX idx_data_exports_status ON data_exports (status);

-- Custom Reports
CREATE TABLE custom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_name VARCHAR(255) NOT NULL,
    company_ticker VARCHAR(10) REFERENCES companies(ticker),
    report_type VARCHAR(50) NOT NULL, -- 'investment_summary', 'financial_analysis', 'risk_profile'
    content JSONB DEFAULT '{}',
    pdf_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_custom_reports_user_id ON custom_reports (user_id);
CREATE INDEX idx_custom_reports_status ON custom_reports (status);

-- Webhook Subscriptions
CREATE TABLE webhook_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    webhook_url VARCHAR(500) NOT NULL,
    events JSONB NOT NULL, -- ['price_alert', 'earnings_release', 'dividend_payment']
    secret_key VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_delivery TIMESTAMPTZ,
    delivery_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_webhook_subscriptions_user_id ON webhook_subscriptions (user_id);

-- Translation Cache
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_text TEXT NOT NULL,
    source_language VARCHAR(10) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    translated_text TEXT NOT NULL,
    translation_provider VARCHAR(50) DEFAULT 'openai',
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_text, source_language, target_language)
);

CREATE INDEX idx_translations_lookup ON translations (source_text, source_language, target_language);

-- Admin Panel - Data Quality Flags
CREATE TABLE data_quality_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_type VARCHAR(50) NOT NULL, -- 'financial_report', 'quote', 'macro_data'
    entity_id VARCHAR(100) NOT NULL, -- ticker, report_id, etc.
    flag_type VARCHAR(50) NOT NULL, -- 'missing_data', 'inconsistent', 'outlier', 'duplicate'
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'ignored')),
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_data_quality_flags_status ON data_quality_flags (status);
CREATE INDEX idx_data_quality_flags_type ON data_quality_flags (data_type, entity_id);

-- Market Data (Time-series)
CREATE TABLE quotes (
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12,4),
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    close DECIMAL(12,4),
    volume BIGINT,
    change_amount DECIMAL(12,4),
    change_percent DECIMAL(8,6),
    PRIMARY KEY (ticker, timestamp)
);

-- Convert quotes to hypertable for time-series optimization
SELECT create_hypertable('quotes', 'timestamp');

-- Create index for efficient queries
CREATE INDEX idx_quotes_ticker_time ON quotes (ticker, timestamp DESC);

-- Company Information
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    website VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Financial Reports
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    period VARCHAR(20) NOT NULL, -- e.g., "2024-Q1", "2024-Annual"
    report_type VARCHAR(20) CHECK (report_type IN ('quarterly', 'annual')),
    filing_date DATE,
    ifrs_data JSONB,
    gaap_data JSONB,
    pdf_url VARCHAR(500),
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_financial_reports_ticker_period ON financial_reports (ticker, period);

-- Financial Ratios
CREATE TABLE financial_ratios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    period VARCHAR(20) NOT NULL,
    ratio_name VARCHAR(50) NOT NULL,
    value DECIMAL(15,6),
    calculation_method TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ratios_ticker_period ON financial_ratios (ticker, period, ratio_name);

-- Macro Economic Data (Time-series)
CREATE TABLE macro_series (
    series_code VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    value DECIMAL(15,6),
    frequency VARCHAR(20), -- daily, weekly, monthly, quarterly, annual
    source VARCHAR(100),
    description TEXT,
    PRIMARY KEY (series_code, date)
);

SELECT create_hypertable('macro_series', 'date');

-- Portfolio Management
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) REFERENCES companies(ticker),
    quantity DECIMAL(15,6) NOT NULL,
    purchase_price DECIMAL(12,4),
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio Performance (Time-series)
CREATE TABLE portfolio_performance (
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_value DECIMAL(15,2),
    daily_return DECIMAL(8,6),
    cumulative_return DECIMAL(8,6),
    PRIMARY KEY (portfolio_id, date)
);

SELECT create_hypertable('portfolio_performance', 'date');

-- Newsletter Management
CREATE TABLE newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);

CREATE TABLE newsletter_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMPTZ,
    recipient_count INTEGER,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE newsletter_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES newsletter_campaigns(id),
    subscriber_id UUID REFERENCES newsletter_subscribers(id),
    status VARCHAR(20) CHECK (status IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- AI Chat System
CREATE TABLE chat_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    context JSONB,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_queries_user_time ON chat_queries (user_id, created_at DESC);

-- Watchlists (Simple version for direct user-ticker mapping)
CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Create index for efficient queries
CREATE INDEX idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX idx_watchlists_ticker ON watchlists (ticker);

-- Alert System
CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) REFERENCES companies(ticker),
    condition_type VARCHAR(20) CHECK (condition_type IN ('above', 'below', 'change_percent')),
    target_value DECIMAL(12,4) NOT NULL,
    current_value DECIMAL(12,4),
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ETL Job Tracking
CREATE TABLE etl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('running', 'completed', 'failed', 'scheduled')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    records_processed INTEGER,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create continuous aggregates for common queries
CREATE MATERIALIZED VIEW daily_market_summary
WITH (timescaledb.continuous) AS
SELECT
    ticker,
    time_bucket('1 day', timestamp) AS day,
    first(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, timestamp) AS close,
    sum(volume) AS volume,
    last(change_percent, timestamp) AS change_percent
FROM quotes
GROUP BY ticker, day;

-- Enable compression for older data
SELECT add_compression_policy('quotes', INTERVAL '7 days');
SELECT add_compression_policy('macro_series', INTERVAL '30 days');

-- Data retention policies
SELECT add_retention_policy('quotes', INTERVAL '5 years');
SELECT add_retention_policy('macro_series', INTERVAL '10 years');

-- Insert sample companies
INSERT INTO companies (ticker, name, sector, industry) VALUES
('MASI', 'MASI Index', 'Index', 'Market Index'),
('MADEX', 'MADEX Index', 'Index', 'Market Index'),
('MASI-ESG', 'MASI ESG Index', 'Index', 'ESG Index'),
('ATW', 'Attijariwafa Bank', 'Financial Services', 'Banks'),
('IAM', 'Maroc Telecom', 'Communication Services', 'Telecoms'),
('BCP', 'Banque Centrale Populaire', 'Financial Services', 'Banks'),
('BMCE', 'BMCE Bank', 'Financial Services', 'Banks'),
('ONA', 'Omnium Nord Africain', 'Conglomerates', 'Diversified Holdings'),
('CMT', 'Ciments du Maroc', 'Materials', 'Building Materials'),
('LAFA', 'Lafarge Ciments', 'Materials', 'Building Materials');

-- Insert sample macro series
INSERT INTO macro_series (series_code, date, value, frequency, source, description) VALUES
('MAR_POLICY_RATE', '2024-01-01', 3.0, 'daily', 'Bank Al-Maghrib', 'Monetary Policy Rate'),
('MAR_CPI', '2024-01-01', 125.4, 'monthly', 'HCP', 'Consumer Price Index'),
('MAR_UNEMPLOYMENT', '2024-01-01', 9.2, 'quarterly', 'HCP', 'Unemployment Rate'),
('MAR_GDP_GROWTH', '2024-01-01', 3.1, 'quarterly', 'HCP', 'GDP Growth Rate');

-- Create views for common queries
CREATE VIEW latest_quotes AS
SELECT DISTINCT ON (ticker)
    ticker,
    timestamp,
    close AS price,
    change_amount,
    change_percent,
    volume
FROM quotes
ORDER BY ticker, timestamp DESC;

CREATE VIEW portfolio_summary AS
SELECT 
    p.id,
    p.name,
    p.user_id,
    COUNT(ph.id) AS holdings_count,
    SUM(ph.quantity * lq.price) AS total_value
FROM portfolios p
LEFT JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
LEFT JOIN latest_quotes lq ON ph.ticker = lq.ticker
GROUP BY p.id, p.name, p.user_id;