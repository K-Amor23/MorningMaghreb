-- Data Quality Migration for Casablanca Insights
-- Adds data quality indicators to companies table and related functionality

-- ============================================
-- ADD DATA QUALITY COLUMN TO COMPANIES TABLE
-- ============================================

-- Add data_quality column to companies table
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS data_quality VARCHAR(20) DEFAULT 'missing' 
CHECK (data_quality IN ('complete', 'partial', 'missing'));

-- Add data quality details columns
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS ohlcv_coverage_days INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS reports_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS news_count_7d INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_ohlcv_date DATE,
ADD COLUMN IF NOT EXISTS last_report_date DATE,
ADD COLUMN IF NOT EXISTS last_news_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS data_quality_updated_at TIMESTAMPTZ DEFAULT NOW();

-- Create index on data_quality for efficient queries
CREATE INDEX IF NOT EXISTS idx_companies_data_quality ON companies(data_quality);
CREATE INDEX IF NOT EXISTS idx_companies_ohlcv_coverage ON companies(ohlcv_coverage_days);
CREATE INDEX IF NOT EXISTS idx_companies_reports_count ON companies(reports_count);

-- ============================================
-- DATA QUALITY CALCULATION FUNCTION
-- ============================================

CREATE OR REPLACE FUNCTION calculate_company_data_quality()
RETURNS TRIGGER AS $$
DECLARE
    ohlcv_count INTEGER;
    reports_count INTEGER;
    news_count INTEGER;
    last_ohlcv DATE;
    last_report DATE;
    last_news TIMESTAMPTZ;
    quality VARCHAR(20);
BEGIN
    -- Calculate OHLCV coverage
    SELECT COUNT(*), MAX(date)
    INTO ohlcv_count, last_ohlcv
    FROM company_prices 
    WHERE ticker = NEW.ticker;
    
    -- Calculate reports count
    SELECT COUNT(*), MAX(report_date::DATE)
    INTO reports_count, last_report
    FROM company_reports 
    WHERE ticker = NEW.ticker;
    
    -- Calculate recent news count (last 7 days)
    SELECT COUNT(*), MAX(published_at)
    INTO news_count, last_news
    FROM company_news 
    WHERE ticker = NEW.ticker 
    AND published_at >= NOW() - INTERVAL '7 days';
    
    -- Determine data quality
    IF ohlcv_count >= 30 AND reports_count >= 1 AND news_count >= 1 THEN
        quality := 'complete';
    ELSIF ohlcv_count >= 7 OR reports_count >= 1 OR news_count >= 1 THEN
        quality := 'partial';
    ELSE
        quality := 'missing';
    END IF;
    
    -- Update the company record
    UPDATE companies 
    SET 
        data_quality = quality,
        ohlcv_coverage_days = COALESCE(ohlcv_count, 0),
        reports_count = COALESCE(reports_count, 0),
        news_count_7d = COALESCE(news_count, 0),
        last_ohlcv_date = last_ohlcv,
        last_report_date = last_report,
        last_news_date = last_news,
        data_quality_updated_at = NOW()
    WHERE ticker = NEW.ticker;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS FOR AUTOMATIC DATA QUALITY UPDATES
-- ============================================

-- Trigger for company_prices updates
CREATE OR REPLACE FUNCTION trigger_ohlcv_data_quality()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM calculate_company_data_quality() FROM companies WHERE ticker = COALESCE(NEW.ticker, OLD.ticker);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ohlcv_data_quality_trigger
    AFTER INSERT OR UPDATE OR DELETE ON company_prices
    FOR EACH ROW
    EXECUTE FUNCTION trigger_ohlcv_data_quality();

-- Trigger for company_reports updates
CREATE OR REPLACE FUNCTION trigger_reports_data_quality()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM calculate_company_data_quality() FROM companies WHERE ticker = COALESCE(NEW.ticker, OLD.ticker);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reports_data_quality_trigger
    AFTER INSERT OR UPDATE OR DELETE ON company_reports
    FOR EACH ROW
    EXECUTE FUNCTION trigger_reports_data_quality();

-- Trigger for company_news updates
CREATE OR REPLACE FUNCTION trigger_news_data_quality()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM calculate_company_data_quality() FROM companies WHERE ticker = COALESCE(NEW.ticker, OLD.ticker);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER news_data_quality_trigger
    AFTER INSERT OR UPDATE OR DELETE ON company_news
    FOR EACH ROW
    EXECUTE FUNCTION trigger_news_data_quality();

-- ============================================
-- DATA QUALITY VIEWS
-- ============================================

-- View for companies with complete data
CREATE OR REPLACE VIEW companies_complete_data AS
SELECT 
    c.*,
    cp.ohlcv_coverage_days,
    cp.reports_count,
    cp.news_count_7d,
    cp.last_ohlcv_date,
    cp.last_report_date,
    cp.last_news_date
FROM companies c
LEFT JOIN (
    SELECT 
        ticker,
        ohlcv_coverage_days,
        reports_count,
        news_count_7d,
        last_ohlcv_date,
        last_report_date,
        last_news_date
    FROM companies
) cp ON c.ticker = cp.ticker
WHERE c.data_quality = 'complete'
ORDER BY c.market_cap_billion DESC NULLS LAST;

-- View for companies with partial data
CREATE OR REPLACE VIEW companies_partial_data AS
SELECT 
    c.*,
    cp.ohlcv_coverage_days,
    cp.reports_count,
    cp.news_count_7d,
    cp.last_ohlcv_date,
    cp.last_report_date,
    cp.last_news_date
FROM companies c
LEFT JOIN (
    SELECT 
        ticker,
        ohlcv_coverage_days,
        reports_count,
        news_count_7d,
        last_ohlcv_date,
        last_report_date,
        last_news_date
    FROM companies
) cp ON c.ticker = cp.ticker
WHERE c.data_quality = 'partial'
ORDER BY c.market_cap_billion DESC NULLS LAST;

-- View for companies with missing data
CREATE OR REPLACE VIEW companies_missing_data AS
SELECT 
    c.*,
    cp.ohlcv_coverage_days,
    cp.reports_count,
    cp.news_count_7d,
    cp.last_ohlcv_date,
    cp.last_report_date,
    cp.last_news_date
FROM companies c
LEFT JOIN (
    SELECT 
        ticker,
        ohlcv_coverage_days,
        reports_count,
        news_count_7d,
        last_ohlcv_date,
        last_report_date,
        last_news_date
    FROM companies
) cp ON c.ticker = cp.ticker
WHERE c.data_quality = 'missing'
ORDER BY c.market_cap_billion DESC NULLS LAST;

-- ============================================
-- DATA QUALITY SUMMARY VIEW
-- ============================================

CREATE OR REPLACE VIEW data_quality_summary AS
SELECT 
    data_quality,
    COUNT(*) as company_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    AVG(ohlcv_coverage_days) as avg_ohlcv_coverage,
    AVG(reports_count) as avg_reports_count,
    AVG(news_count_7d) as avg_news_count_7d,
    MAX(data_quality_updated_at) as last_updated
FROM companies
GROUP BY data_quality
ORDER BY 
    CASE data_quality 
        WHEN 'complete' THEN 1 
        WHEN 'partial' THEN 2 
        WHEN 'missing' THEN 3 
    END;

-- ============================================
-- DATA QUALITY STATISTICS FUNCTION
-- ============================================

CREATE OR REPLACE FUNCTION get_data_quality_stats()
RETURNS TABLE (
    total_companies INTEGER,
    complete_count INTEGER,
    partial_count INTEGER,
    missing_count INTEGER,
    complete_percentage DECIMAL(5,2),
    partial_percentage DECIMAL(5,2),
    missing_percentage DECIMAL(5,2),
    avg_ohlcv_coverage DECIMAL(5,2),
    avg_reports_count DECIMAL(5,2),
    avg_news_count_7d DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_companies,
        COUNT(*) FILTER (WHERE data_quality = 'complete')::INTEGER as complete_count,
        COUNT(*) FILTER (WHERE data_quality = 'partial')::INTEGER as partial_count,
        COUNT(*) FILTER (WHERE data_quality = 'missing')::INTEGER as missing_count,
        ROUND(COUNT(*) FILTER (WHERE data_quality = 'complete') * 100.0 / COUNT(*), 2) as complete_percentage,
        ROUND(COUNT(*) FILTER (WHERE data_quality = 'partial') * 100.0 / COUNT(*), 2) as partial_percentage,
        ROUND(COUNT(*) FILTER (WHERE data_quality = 'missing') * 100.0 / COUNT(*), 2) as missing_percentage,
        ROUND(AVG(ohlcv_coverage_days), 2) as avg_ohlcv_coverage,
        ROUND(AVG(reports_count), 2) as avg_reports_count,
        ROUND(AVG(news_count_7d), 2) as avg_news_count_7d
    FROM companies;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA QUALITY CALCULATION
-- ============================================

-- Calculate initial data quality for all companies
UPDATE companies 
SET 
    data_quality = 'missing',
    ohlcv_coverage_days = 0,
    reports_count = 0,
    news_count_7d = 0;

-- Trigger calculation for all companies
SELECT calculate_company_data_quality() FROM companies;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON COLUMN companies.data_quality IS 'Data quality indicator: complete, partial, or missing';
COMMENT ON COLUMN companies.ohlcv_coverage_days IS 'Number of days with OHLCV data available';
COMMENT ON COLUMN companies.reports_count IS 'Number of financial reports available';
COMMENT ON COLUMN companies.news_count_7d IS 'Number of news articles in last 7 days';
COMMENT ON COLUMN companies.last_ohlcv_date IS 'Date of most recent OHLCV data';
COMMENT ON COLUMN companies.last_report_date IS 'Date of most recent financial report';
COMMENT ON COLUMN companies.last_news_date IS 'Date of most recent news article';

COMMENT ON FUNCTION calculate_company_data_quality() IS 'Calculates and updates data quality for a company based on available data';
COMMENT ON FUNCTION get_data_quality_stats() IS 'Returns comprehensive data quality statistics for all companies'; 