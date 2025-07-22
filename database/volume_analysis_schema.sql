-- Volume Analysis Schema for Casablanca Stock Exchange
-- This schema provides comprehensive volume data storage and analysis

-- 1. Volume Analysis Table (Main table for volume data)
CREATE TABLE IF NOT EXISTS volume_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    volume BIGINT NOT NULL,
    average_volume BIGINT,
    volume_ratio DECIMAL(8,4), -- Current volume / average volume
    volume_ma_5 BIGINT, -- 5-day moving average
    volume_ma_20 BIGINT, -- 20-day moving average
    volume_change_percent DECIMAL(8,4), -- Day-over-day change
    high_volume_alert BOOLEAN DEFAULT FALSE, -- Volume > 2x average
    low_volume_alert BOOLEAN DEFAULT FALSE, -- Volume < 0.5x average
    source VARCHAR(50), -- Data source (African Markets, Wafabourse, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, date)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_volume_analysis_ticker_date 
ON volume_analysis (ticker, date DESC);

CREATE INDEX IF NOT EXISTS idx_volume_analysis_alerts 
ON volume_analysis (high_volume_alert, low_volume_alert);

CREATE INDEX IF NOT EXISTS idx_volume_analysis_volume_ratio 
ON volume_analysis (volume_ratio DESC);

CREATE INDEX IF NOT EXISTS idx_volume_analysis_date 
ON volume_analysis (date DESC);

-- 2. Volume Trends Table (Aggregated volume trends)
CREATE TABLE IF NOT EXISTS volume_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_volume BIGINT NOT NULL,
    average_volume BIGINT NOT NULL,
    max_volume BIGINT NOT NULL,
    min_volume BIGINT NOT NULL,
    volume_volatility DECIMAL(8,4), -- Standard deviation of volume
    volume_trend_direction VARCHAR(10), -- 'increasing', 'decreasing', 'stable'
    trend_strength DECIMAL(8,4), -- Correlation coefficient
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, period, start_date)
);

-- Create indexes for volume trends
CREATE INDEX IF NOT EXISTS idx_volume_trends_ticker_period 
ON volume_trends (ticker, period, start_date DESC);

CREATE INDEX IF NOT EXISTS idx_volume_trends_trend_direction 
ON volume_trends (volume_trend_direction, trend_strength DESC);

-- 3. Volume Alerts Table (Volume-based alerts and notifications)
CREATE TABLE IF NOT EXISTS volume_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL, -- 'high_volume', 'low_volume', 'volume_spike', 'volume_drop'
    alert_date DATE NOT NULL,
    volume BIGINT NOT NULL,
    threshold_value BIGINT NOT NULL, -- Volume that triggered the alert
    alert_ratio DECIMAL(8,4), -- Volume / threshold ratio
    alert_message TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID, -- User who acknowledged the alert
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for volume alerts
CREATE INDEX IF NOT EXISTS idx_volume_alerts_ticker_date 
ON volume_alerts (ticker, alert_date DESC);

CREATE INDEX IF NOT EXISTS idx_volume_alerts_type_active 
ON volume_alerts (alert_type, is_active);

CREATE INDEX IF NOT EXISTS idx_volume_alerts_ratio 
ON volume_alerts (alert_ratio DESC);

-- 4. Sector Volume Analysis Table (Aggregated by sector)
CREATE TABLE IF NOT EXISTS sector_volume_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    total_volume BIGINT NOT NULL,
    average_volume_per_stock BIGINT NOT NULL,
    volume_weighted_average_price DECIMAL(12,4),
    sector_volume_ratio DECIMAL(8,4), -- Sector volume / total market volume
    high_volume_stocks_count INTEGER DEFAULT 0,
    low_volume_stocks_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(sector, date)
);

-- Create indexes for sector volume analysis
CREATE INDEX IF NOT EXISTS idx_sector_volume_analysis_sector_date 
ON sector_volume_analysis (sector, date DESC);

CREATE INDEX IF NOT EXISTS idx_sector_volume_analysis_total_volume 
ON sector_volume_analysis (total_volume DESC);

-- 5. Market Volume Summary Table (Daily market-wide volume metrics)
CREATE TABLE IF NOT EXISTS market_volume_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    total_market_volume BIGINT NOT NULL,
    average_stock_volume BIGINT NOT NULL,
    median_stock_volume BIGINT NOT NULL,
    volume_90th_percentile BIGINT NOT NULL,
    volume_10th_percentile BIGINT NOT NULL,
    high_volume_stocks_count INTEGER DEFAULT 0,
    low_volume_stocks_count INTEGER DEFAULT 0,
    volume_spikes_count INTEGER DEFAULT 0, -- Stocks with >3x average volume
    most_active_stock VARCHAR(10),
    most_active_stock_volume BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for market volume summary
CREATE INDEX IF NOT EXISTS idx_market_volume_summary_date 
ON market_volume_summary (date DESC);

CREATE INDEX IF NOT EXISTS idx_market_volume_summary_total_volume 
ON market_volume_summary (total_market_volume DESC);

-- 6. Volume Data Quality Table (Track data quality and completeness)
CREATE TABLE IF NOT EXISTS volume_data_quality (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    source VARCHAR(50) NOT NULL,
    total_stocks_expected INTEGER NOT NULL,
    total_stocks_with_volume INTEGER NOT NULL,
    data_completeness_ratio DECIMAL(5,4), -- stocks_with_volume / total_stocks
    average_volume_confidence DECIMAL(5,4), -- Confidence in volume data quality
    data_freshness_hours INTEGER, -- Hours since last update
    quality_score DECIMAL(5,4), -- Overall quality score (0-1)
    issues_found TEXT[], -- Array of data quality issues
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, source)
);

-- Create indexes for volume data quality
CREATE INDEX IF NOT EXISTS idx_volume_data_quality_date_source 
ON volume_data_quality (date DESC, source);

CREATE INDEX IF NOT EXISTS idx_volume_data_quality_score 
ON volume_data_quality (quality_score DESC);

-- Views for easy querying

-- 1. Latest Volume Analysis View
CREATE OR REPLACE VIEW latest_volume_analysis AS
SELECT DISTINCT ON (ticker)
    ticker,
    date,
    volume,
    average_volume,
    volume_ratio,
    volume_ma_5,
    volume_ma_20,
    volume_change_percent,
    high_volume_alert,
    low_volume_alert,
    source,
    created_at
FROM volume_analysis
ORDER BY ticker, date DESC;

-- 2. High Volume Alerts View
CREATE OR REPLACE VIEW high_volume_alerts AS
SELECT 
    ticker,
    date,
    volume,
    average_volume,
    volume_ratio,
    source,
    created_at
FROM volume_analysis
WHERE high_volume_alert = TRUE
ORDER BY volume_ratio DESC, date DESC;

-- 3. Volume Trends Summary View
CREATE OR REPLACE VIEW volume_trends_summary AS
SELECT 
    ticker,
    period,
    start_date,
    end_date,
    total_volume,
    average_volume,
    volume_trend_direction,
    trend_strength,
    created_at
FROM volume_trends
ORDER BY ticker, period, start_date DESC;

-- 4. Active Volume Alerts View
CREATE OR REPLACE VIEW active_volume_alerts AS
SELECT 
    ticker,
    alert_type,
    alert_date,
    volume,
    threshold_value,
    alert_ratio,
    alert_message,
    created_at
FROM volume_alerts
WHERE is_active = TRUE
ORDER BY alert_date DESC, alert_ratio DESC;

-- 5. Market Volume Dashboard View
CREATE OR REPLACE VIEW market_volume_dashboard AS
SELECT 
    mvs.date,
    mvs.total_market_volume,
    mvs.average_stock_volume,
    mvs.high_volume_stocks_count,
    mvs.low_volume_stocks_count,
    mvs.volume_spikes_count,
    mvs.most_active_stock,
    mvs.most_active_stock_volume,
    sva.sector,
    sva.total_volume as sector_volume,
    sva.volume_weighted_average_price as sector_vwap
FROM market_volume_summary mvs
LEFT JOIN sector_volume_analysis sva ON mvs.date = sva.date
ORDER BY mvs.date DESC, sva.total_volume DESC;

-- Functions for volume analysis

-- 1. Function to calculate volume moving averages
CREATE OR REPLACE FUNCTION calculate_volume_moving_averages(
    p_ticker VARCHAR(10),
    p_days INTEGER DEFAULT 20
) RETURNS TABLE(
    ticker VARCHAR(10),
    date DATE,
    volume BIGINT,
    ma_5 BIGINT,
    ma_20 BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        va.ticker,
        va.date,
        va.volume,
        AVG(va.volume) OVER (
            PARTITION BY va.ticker 
            ORDER BY va.date 
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        )::BIGINT as ma_5,
        AVG(va.volume) OVER (
            PARTITION BY va.ticker 
            ORDER BY va.date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        )::BIGINT as ma_20
    FROM volume_analysis va
    WHERE va.ticker = p_ticker
    ORDER BY va.date DESC
    LIMIT p_days;
END;
$$ LANGUAGE plpgsql;

-- 2. Function to generate volume alerts
CREATE OR REPLACE FUNCTION generate_volume_alerts() RETURNS INTEGER AS $$
DECLARE
    alert_count INTEGER := 0;
    alert_record RECORD;
BEGIN
    -- Generate high volume alerts
    FOR alert_record IN
        SELECT 
            ticker,
            date,
            volume,
            average_volume,
            volume / average_volume as ratio
        FROM volume_analysis
        WHERE volume_ratio > 2.0 
        AND date = CURRENT_DATE
        AND high_volume_alert = FALSE
    LOOP
        INSERT INTO volume_alerts (
            ticker, alert_type, alert_date, volume, 
            threshold_value, alert_ratio, alert_message
        ) VALUES (
            alert_record.ticker,
            'high_volume',
            alert_record.date,
            alert_record.volume,
            alert_record.average_volume * 2,
            alert_record.ratio,
            format('High volume alert: %s volume is %.1fx average', 
                   alert_record.ticker, alert_record.ratio)
        );
        alert_count := alert_count + 1;
    END LOOP;
    
    -- Generate low volume alerts
    FOR alert_record IN
        SELECT 
            ticker,
            date,
            volume,
            average_volume,
            volume / average_volume as ratio
        FROM volume_analysis
        WHERE volume_ratio < 0.5 
        AND date = CURRENT_DATE
        AND low_volume_alert = FALSE
    LOOP
        INSERT INTO volume_alerts (
            ticker, alert_type, alert_date, volume, 
            threshold_value, alert_ratio, alert_message
        ) VALUES (
            alert_record.ticker,
            'low_volume',
            alert_record.date,
            alert_record.volume,
            alert_record.average_volume * 0.5,
            alert_record.ratio,
            format('Low volume alert: %s volume is %.1fx average', 
                   alert_record.ticker, alert_record.ratio)
        );
        alert_count := alert_count + 1;
    END LOOP;
    
    RETURN alert_count;
END;
$$ LANGUAGE plpgsql;

-- 3. Function to update volume analysis metrics
CREATE OR REPLACE FUNCTION update_volume_metrics() RETURNS VOID AS $$
BEGIN
    -- Update volume moving averages
    UPDATE volume_analysis va
    SET 
        volume_ma_5 = (
            SELECT AVG(v2.volume)::BIGINT
            FROM volume_analysis v2
            WHERE v2.ticker = va.ticker
            AND v2.date BETWEEN va.date - INTERVAL '4 days' AND va.date
        ),
        volume_ma_20 = (
            SELECT AVG(v2.volume)::BIGINT
            FROM volume_analysis v2
            WHERE v2.ticker = va.ticker
            AND v2.date BETWEEN va.date - INTERVAL '19 days' AND va.date
        ),
        volume_change_percent = (
            SELECT 
                CASE 
                    WHEN v2.volume > 0 THEN 
                        ((va.volume - v2.volume) / v2.volume * 100)::DECIMAL(8,4)
                    ELSE NULL
                END
            FROM volume_analysis v2
            WHERE v2.ticker = va.ticker
            AND v2.date = va.date - INTERVAL '1 day'
        ),
        updated_at = NOW()
    WHERE va.date >= CURRENT_DATE - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Sample data inserts for testing
INSERT INTO volume_analysis (ticker, date, volume, average_volume, volume_ratio, source) VALUES
('ATW', CURRENT_DATE, 1500000, 800000, 1.875, 'African Markets'),
('BMCE', CURRENT_DATE, 900000, 1200000, 0.750, 'African Markets'),
('CIH', CURRENT_DATE, 2500000, 1000000, 2.500, 'African Markets'),
('WAA', CURRENT_DATE, 600000, 500000, 1.200, 'African Markets'),
('MNG', CURRENT_DATE, 1800000, 1500000, 1.200, 'African Markets')
ON CONFLICT (ticker, date) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user; 