-- Currency Converter & Remit Rate Advisor Database Schema
-- Casablanca Insight Currency Services

-- Official BAM exchange rates
CREATE TABLE IF NOT EXISTS bam_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    currency_pair TEXT NOT NULL, -- e.g., 'USD/MAD', 'EUR/MAD'
    rate DECIMAL(10,6) NOT NULL,
    rate_date DATE NOT NULL,
    source TEXT NOT NULL DEFAULT 'BAM', -- Bank Al-Maghrib
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(currency_pair, rate_date)
);

-- Remittance service rates
CREATE TABLE IF NOT EXISTS remittance_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL, -- 'Remitly', 'Wise', 'Western Union', etc.
    currency_pair TEXT NOT NULL,
    rate DECIMAL(10,6) NOT NULL,
    fee_amount DECIMAL(10,2),
    fee_currency TEXT DEFAULT 'USD',
    fee_type TEXT DEFAULT 'fixed', -- 'fixed', 'percentage', 'mixed'
    transfer_amount DECIMAL(10,2), -- Amount used for rate calculation
    effective_rate DECIMAL(10,6), -- Rate after fees
    spread_percentage DECIMAL(5,2), -- % difference from BAM rate
    rate_date DATE NOT NULL,
    scraped_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User rate alerts
CREATE TABLE IF NOT EXISTS rate_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    currency_pair TEXT NOT NULL,
    target_rate DECIMAL(10,6) NOT NULL,
    alert_type TEXT NOT NULL DEFAULT 'above', -- 'above', 'below'
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rate comparison history for AI analysis
CREATE TABLE IF NOT EXISTS rate_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    currency_pair TEXT NOT NULL,
    analysis_date DATE NOT NULL,
    bam_rate DECIMAL(10,6) NOT NULL,
    best_service TEXT NOT NULL,
    best_rate DECIMAL(10,6) NOT NULL,
    best_spread DECIMAL(5,2) NOT NULL,
    avg_spread_30d DECIMAL(5,2),
    percentile_30d INTEGER, -- How good is today's rate (1-100)
    ai_advice TEXT, -- AI-generated recommendation
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bam_rates_currency_date ON bam_rates(currency_pair, rate_date);
CREATE INDEX IF NOT EXISTS idx_remittance_rates_service_date ON remittance_rates(service_name, rate_date);
CREATE INDEX IF NOT EXISTS idx_remittance_rates_currency_date ON remittance_rates(currency_pair, rate_date);
CREATE INDEX IF NOT EXISTS idx_rate_alerts_user ON rate_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_alerts_active ON rate_alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_rate_analysis_currency_date ON rate_analysis(currency_pair, analysis_date);

-- Update triggers for updated_at timestamps
CREATE TRIGGER update_rate_alerts_updated_at 
    BEFORE UPDATE ON rate_alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 