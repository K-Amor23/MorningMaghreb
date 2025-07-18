-- Financial Data Schema for Supabase
-- Add these tables to your existing Supabase project
-- Run this in your Supabase SQL Editor

-- 1. CSE Companies Table (Casablanca Stock Exchange)
CREATE TABLE IF NOT EXISTS cse_companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    isin VARCHAR(12),
    sector VARCHAR(100),
    listing_date DATE,
    source_url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cse_companies_ticker ON cse_companies(ticker);
CREATE INDEX IF NOT EXISTS idx_cse_companies_isin ON cse_companies(isin);
CREATE INDEX IF NOT EXISTS idx_cse_companies_sector ON cse_companies(sector);
CREATE INDEX IF NOT EXISTS idx_cse_companies_listing_date ON cse_companies(listing_date);
CREATE INDEX IF NOT EXISTS idx_cse_companies_scraped_at ON cse_companies(scraped_at);

-- 2. Financial Raw Data Table
CREATE TABLE IF NOT EXISTS financials_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER, -- NULL for annual reports
    report_type TEXT NOT NULL CHECK (report_type IN ('pnl', 'balance', 'cashflow', 'other')),
    language TEXT NOT NULL DEFAULT 'fr',
    source_url TEXT,
    pdf_filename TEXT,
    json_data JSONB NOT NULL,
    extraction_metadata JSONB, -- Store extraction quality metrics, confidence scores
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Financial GAAP Data Table
CREATE TABLE IF NOT EXISTS financials_gaap (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_id UUID REFERENCES financials_raw(id),
    company TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    report_type TEXT NOT NULL,
    json_data JSONB NOT NULL, -- Clean GAAP data
    ratios JSONB, -- Computed financial ratios
    ai_summary TEXT, -- AI-generated summary
    confidence_score FLOAT DEFAULT 0.0, -- Translation confidence
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Label Mappings Table
CREATE TABLE IF NOT EXISTS label_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    french_label TEXT NOT NULL,
    gaap_label TEXT NOT NULL,
    category TEXT NOT NULL, -- 'revenue', 'expense', 'asset', 'liability', etc.
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(french_label, gaap_label)
);

-- 5. ETL Jobs Tracking Table
CREATE TABLE IF NOT EXISTS etl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL, -- 'fetch', 'extract', 'clean', 'translate', 'live_update'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    company TEXT,
    year INTEGER,
    quarter INTEGER,
    metadata JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Market Data Table (for real-time price data)
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    price DECIMAL(10,2),
    volume BIGINT,
    market_cap DECIMAL(20,2),
    change_percent DECIMAL(5,2),
    high_24h DECIMAL(10,2),
    low_24h DECIMAL(10,2),
    open_price DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source TEXT DEFAULT 'cse'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_financials_raw_company_year ON financials_raw(company, year);
CREATE INDEX IF NOT EXISTS idx_financials_raw_report_type ON financials_raw(report_type);
CREATE INDEX IF NOT EXISTS idx_financials_gaap_company_year ON financials_gaap(company, year);
CREATE INDEX IF NOT EXISTS idx_financials_gaap_report_type ON financials_gaap(report_type);
CREATE INDEX IF NOT EXISTS idx_label_mappings_french ON label_mappings(french_label);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_company_year ON etl_jobs(company, year);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_financials_raw_updated_at 
    BEFORE UPDATE ON financials_raw 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financials_gaap_updated_at 
    BEFORE UPDATE ON financials_gaap 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cse_companies_updated_at 
    BEFORE UPDATE ON cse_companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE cse_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE financials_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE financials_gaap ENABLE ROW LEVEL SECURITY;
ALTER TABLE label_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE etl_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access to market data
CREATE POLICY "Public read access to CSE companies" ON cse_companies
    FOR SELECT USING (true);

CREATE POLICY "Public read access to market data" ON market_data
    FOR SELECT USING (true);

CREATE POLICY "Public read access to financial data" ON financials_gaap
    FOR SELECT USING (true);

-- Create policies for authenticated users to access raw data
CREATE POLICY "Authenticated users can read financial raw data" ON financials_raw
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read label mappings" ON label_mappings
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create policies for admin users to manage ETL jobs
CREATE POLICY "Admin users can manage ETL jobs" ON etl_jobs
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.tier = 'admin'
        )
    );

-- Create function to get company statistics
CREATE OR REPLACE FUNCTION get_cse_company_stats()
RETURNS TABLE (
    total_companies INTEGER,
    companies_with_isin INTEGER,
    companies_with_sector INTEGER,
    companies_with_listing_date INTEGER,
    sectors_count INTEGER,
    oldest_listing_date DATE,
    newest_listing_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_companies,
        COUNT(CASE WHEN isin IS NOT NULL THEN 1 END)::INTEGER as companies_with_isin,
        COUNT(CASE WHEN sector IS NOT NULL THEN 1 END)::INTEGER as companies_with_sector,
        COUNT(CASE WHEN listing_date IS NOT NULL THEN 1 END)::INTEGER as companies_with_listing_date,
        COUNT(DISTINCT sector)::INTEGER as sectors_count,
        MIN(listing_date) as oldest_listing_date,
        MAX(listing_date) as newest_listing_date
    FROM cse_companies;
END;
$$ language 'plpgsql';

-- Create function to search companies
CREATE OR REPLACE FUNCTION search_cse_companies(search_term TEXT)
RETURNS TABLE (
    company_id INTEGER,
    name VARCHAR(255),
    ticker VARCHAR(10),
    isin VARCHAR(12),
    sector VARCHAR(100),
    listing_date DATE,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.company_id,
        c.name,
        c.ticker,
        c.isin,
        c.sector,
        c.listing_date,
        GREATEST(
            similarity(c.name, search_term),
            similarity(c.ticker, search_term),
            COALESCE(similarity(c.isin, search_term), 0)
        ) as similarity
    FROM cse_companies c
    WHERE 
        c.name ILIKE '%' || search_term || '%' OR
        c.ticker ILIKE '%' || search_term || '%' OR
        c.isin ILIKE '%' || search_term || '%'
    ORDER BY similarity DESC;
END;
$$ language 'plpgsql';

-- Create view for easy querying of company information
CREATE OR REPLACE VIEW cse_companies_view AS
SELECT 
    company_id,
    name,
    ticker,
    isin,
    sector,
    listing_date,
    source_url,
    scraped_at,
    created_at,
    updated_at,
    CASE 
        WHEN listing_date IS NOT NULL 
        THEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, listing_date))
        ELSE NULL 
    END as years_listed
FROM cse_companies
ORDER BY name;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL VIEWS IN SCHEMA public TO anon, authenticated;

-- Insert sample data for testing
INSERT INTO cse_companies (name, ticker, isin, sector, listing_date, source_url) VALUES
('Attijariwafa Bank', 'ATW', 'MA0000011885', 'Banking', '2004-01-01', 'https://www.casablanca-bourse.com'),
('Maroc Telecom', 'IAM', 'MA0000011886', 'Telecommunications', '2001-12-01', 'https://www.casablanca-bourse.com'),
('Banque Centrale Populaire', 'BCP', 'MA0000011887', 'Banking', '2004-01-01', 'https://www.casablanca-bourse.com'),
('BMCE Bank', 'BMCE', 'MA0000011888', 'Banking', '1995-01-01', 'https://www.casablanca-bourse.com')
ON CONFLICT (ticker) DO NOTHING;