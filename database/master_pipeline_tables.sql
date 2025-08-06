-- Master Pipeline Database Tables for Supabase
-- Tables needed for the master Airflow data pipeline

-- ============================================
-- MARKET DATA TABLES
-- ============================================

-- Company Prices Table (if not exists)
CREATE TABLE IF NOT EXISTS company_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    price DECIMAL(10,2),
    change_1d_percent DECIMAL(5,2),
    change_ytd_percent DECIMAL(5,2),
    market_cap_billion DECIMAL(10,2),
    volume BIGINT,
    pe_ratio DECIMAL(5,2),
    dividend_yield DECIMAL(5,2),
    size_category VARCHAR(50),
    sector_group VARCHAR(100),
    date DATE NOT NULL,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);

-- Market Indices Table
CREATE TABLE IF NOT EXISTS market_indices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_name VARCHAR(50) NOT NULL,
    value DECIMAL(10,2),
    change_1d_percent DECIMAL(5,2),
    change_ytd_percent DECIMAL(5,2),
    volume BIGINT,
    market_cap_total DECIMAL(10,2),
    date DATE NOT NULL,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(index_name, date)
);

-- ============================================
-- MACROECONOMIC DATA TABLES
-- ============================================

-- Macro Indicators Table
CREATE TABLE IF NOT EXISTS macro_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator VARCHAR(100) NOT NULL,
    value DECIMAL(10,4),
    unit VARCHAR(50),
    period VARCHAR(20),
    source VARCHAR(100),
    date DATE NOT NULL,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(indicator, date)
);

-- ============================================
-- NEWS AND SENTIMENT TABLES
-- ============================================

-- Company News Table
CREATE TABLE IF NOT EXISTS company_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    headline TEXT NOT NULL,
    summary TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    source VARCHAR(100),
    published_at TIMESTAMPTZ,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PIPELINE MONITORING TABLES
-- ============================================

-- Data Quality Logs Table
CREATE TABLE IF NOT EXISTS data_quality_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    validation_date DATE NOT NULL,
    african_markets_count INTEGER DEFAULT 0,
    bourse_indices_count INTEGER DEFAULT 0,
    macro_indicators_count INTEGER DEFAULT 0,
    news_articles_count INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0,
    validation_passed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(validation_date)
);

-- Pipeline Notifications Table
CREATE TABLE IF NOT EXISTS pipeline_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_type VARCHAR(20) CHECK (notification_type IN ('success', 'failure', 'warning')),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Company Prices indexes
CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
CREATE INDEX IF NOT EXISTS idx_company_prices_sector ON company_prices(sector);
CREATE INDEX IF NOT EXISTS idx_company_prices_price ON company_prices(price);

-- Market Indices indexes
CREATE INDEX IF NOT EXISTS idx_market_indices_name ON market_indices(index_name);
CREATE INDEX IF NOT EXISTS idx_market_indices_date ON market_indices(date);
CREATE INDEX IF NOT EXISTS idx_market_indices_value ON market_indices(value);

-- Macro Indicators indexes
CREATE INDEX IF NOT EXISTS idx_macro_indicators_indicator ON macro_indicators(indicator);
CREATE INDEX IF NOT EXISTS idx_macro_indicators_date ON macro_indicators(date);
CREATE INDEX IF NOT EXISTS idx_macro_indicators_value ON macro_indicators(value);

-- Company News indexes
CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
CREATE INDEX IF NOT EXISTS idx_company_news_source ON company_news(source);

-- Data Quality Logs indexes
CREATE INDEX IF NOT EXISTS idx_data_quality_logs_date ON data_quality_logs(validation_date);
CREATE INDEX IF NOT EXISTS idx_data_quality_logs_passed ON data_quality_logs(validation_passed);

-- Pipeline Notifications indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_notifications_type ON pipeline_notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_notifications_created_at ON pipeline_notifications(created_at);

-- ============================================
-- VIEWS FOR EASY DATA ACCESS
-- ============================================

-- Latest Company Prices View
CREATE OR REPLACE VIEW latest_company_prices AS
SELECT DISTINCT ON (ticker)
    ticker,
    company_name,
    sector,
    price,
    change_1d_percent,
    change_ytd_percent,
    market_cap_billion,
    volume,
    pe_ratio,
    dividend_yield,
    size_category,
    sector_group,
    date,
    scraped_at
FROM company_prices
ORDER BY ticker, date DESC;

-- Latest Market Indices View
CREATE OR REPLACE VIEW latest_market_indices AS
SELECT DISTINCT ON (index_name)
    index_name,
    value,
    change_1d_percent,
    change_ytd_percent,
    volume,
    market_cap_total,
    date,
    scraped_at
FROM market_indices
ORDER BY index_name, date DESC;

-- Latest Macro Indicators View
CREATE OR REPLACE VIEW latest_macro_indicators AS
SELECT DISTINCT ON (indicator)
    indicator,
    value,
    unit,
    period,
    source,
    date,
    scraped_at
FROM macro_indicators
ORDER BY indicator, date DESC;

-- Recent Company News View
CREATE OR REPLACE VIEW recent_company_news AS
SELECT 
    ticker,
    headline,
    summary,
    sentiment,
    source,
    published_at,
    scraped_at
FROM company_news
WHERE published_at >= NOW() - INTERVAL '7 days'
ORDER BY published_at DESC;

-- ============================================
-- FUNCTIONS FOR DATA MANAGEMENT
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_company_prices_updated_at 
    BEFORE UPDATE ON company_prices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_indices_updated_at 
    BEFORE UPDATE ON market_indices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_macro_indicators_updated_at 
    BEFORE UPDATE ON macro_indicators 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_news_updated_at 
    BEFORE UPDATE ON company_news 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE company_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_indices ENABLE ROW LEVEL SECURITY;
ALTER TABLE macro_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_quality_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_notifications ENABLE ROW LEVEL SECURITY;

-- Public read access for market data
CREATE POLICY "Public read access for company_prices" ON company_prices
    FOR SELECT USING (true);

CREATE POLICY "Public read access for market_indices" ON market_indices
    FOR SELECT USING (true);

CREATE POLICY "Public read access for macro_indicators" ON macro_indicators
    FOR SELECT USING (true);

CREATE POLICY "Public read access for company_news" ON company_news
    FOR SELECT USING (true);

-- Service role full access (for Airflow)
CREATE POLICY "Service role full access for company_prices" ON company_prices
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access for market_indices" ON market_indices
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access for macro_indicators" ON macro_indicators
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access for company_news" ON company_news
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access for data_quality_logs" ON data_quality_logs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access for pipeline_notifications" ON pipeline_notifications
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================

-- Insert sample data for testing
INSERT INTO company_prices (ticker, company_name, sector, price, change_1d_percent, change_ytd_percent, market_cap_billion, volume, pe_ratio, dividend_yield, size_category, sector_group, date) VALUES
('ATW', 'Attijariwafa Bank', 'Banking', 410.10, 0.31, 5.25, 24.56, 1250000, 12.5, 4.2, 'Large Cap', 'Financial Services', CURRENT_DATE),
('IAM', 'Maroc Telecom', 'Telecommunications', 156.30, -1.33, -2.15, 15.68, 890000, 15.2, 3.8, 'Large Cap', 'Telecommunications', CURRENT_DATE),
('BCP', 'Banque Centrale Populaire', 'Banking', 245.80, 0.85, 8.45, 18.92, 950000, 11.8, 5.1, 'Large Cap', 'Financial Services', CURRENT_DATE)
ON CONFLICT (ticker, date) DO NOTHING;

INSERT INTO market_indices (index_name, value, change_1d_percent, change_ytd_percent, volume, market_cap_total, date) VALUES
('MASI', 12580.45, 0.45, 12.3, 45000000, 1250.8, CURRENT_DATE),
('MADEX', 10250.30, 0.32, 10.8, 38000000, 980.5, CURRENT_DATE)
ON CONFLICT (index_name, date) DO NOTHING;

INSERT INTO macro_indicators (indicator, value, unit, period, source, date) VALUES
('GDP_Growth', 3.2, 'percent', '2024', 'Bank Al-Maghrib', CURRENT_DATE),
('Inflation_Rate', 2.8, 'percent', '2024', 'Bank Al-Maghrib', CURRENT_DATE),
('Interest_Rate', 2.5, 'percent', '2024', 'Bank Al-Maghrib', CURRENT_DATE),
('Exchange_Rate_USD', 9.85, 'MAD/USD', '2024', 'Bank Al-Maghrib', CURRENT_DATE)
ON CONFLICT (indicator, date) DO NOTHING;

INSERT INTO company_news (ticker, headline, summary, sentiment, source, published_at) VALUES
('ATW', 'Attijariwafa Bank Reports Strong Q4 Results', 'Bank reports 15% increase in net profit', 'positive', 'Financial News Morocco', NOW()),
('IAM', 'Maroc Telecom Expands 5G Network', 'Company announces major 5G infrastructure investment', 'positive', 'Tech News Morocco', NOW())
ON CONFLICT DO NOTHING; 