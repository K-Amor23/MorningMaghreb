-- ETL Pipeline Database Schema
-- Casablanca Insight Financial Data Processing

-- Raw financial data extracted from PDFs
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Clean GAAP version with translated labels
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- French to GAAP label mapping dictionary
CREATE TABLE IF NOT EXISTS label_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    french_label TEXT NOT NULL,
    gaap_label TEXT NOT NULL,
    category TEXT NOT NULL, -- 'revenue', 'expense', 'asset', 'liability', etc.
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(french_label, gaap_label)
);

-- ETL job tracking
CREATE TABLE IF NOT EXISTS etl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL, -- 'fetch', 'extract', 'clean', 'translate', 'live_update'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    company TEXT,
    year INTEGER,
    quarter INTEGER,
    metadata JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_financials_raw_company_year ON financials_raw(company, year);
CREATE INDEX IF NOT EXISTS idx_financials_raw_report_type ON financials_raw(report_type);
CREATE INDEX IF NOT EXISTS idx_financials_gaap_company_year ON financials_gaap(company, year);
CREATE INDEX IF NOT EXISTS idx_financials_gaap_report_type ON financials_gaap(report_type);
CREATE INDEX IF NOT EXISTS idx_label_mappings_french ON label_mappings(french_label);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_etl_jobs_company_year ON etl_jobs(company, year);

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