-- IR Scraping Database Schema
-- This schema supports smart IR report scraping with business logic

-- Add columns to existing companies table for IR scraping tracking
ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMP;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS ir_expected_release_date DATE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS actual_release_date DATE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS scraping_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_scraping_error TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_scraping_attempt TIMESTAMP;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS fiscal_year_end_month INTEGER DEFAULT 12;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS fiscal_year_end_day INTEGER DEFAULT 31;

-- Create IR scraping history table
CREATE TABLE IF NOT EXISTS ir_scraping_history (
    id SERIAL PRIMARY KEY,
    company_ticker VARCHAR(10) NOT NULL,
    scraping_date DATE NOT NULL,
    report_url TEXT,
    file_path TEXT,
    file_size BIGINT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'skipped')),
    error_message TEXT,
    user_agent TEXT,
    proxy_used BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_ir_scraping_company_date (company_ticker, scraping_date),
    INDEX idx_ir_scraping_status (status),
    INDEX idx_ir_scraping_created_at (created_at)
);

-- Create IR report metadata table
CREATE TABLE IF NOT EXISTS ir_reports (
    id SERIAL PRIMARY KEY,
    company_ticker VARCHAR(10) NOT NULL,
    report_type VARCHAR(20) NOT NULL CHECK (report_type IN ('annual', 'quarterly', 'interim', 'other')),
    report_year INTEGER NOT NULL,
    report_quarter INTEGER,
    report_period VARCHAR(50),
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    source_url TEXT,
    download_date TIMESTAMP NOT NULL,
    extraction_status VARCHAR(20) DEFAULT 'pending' CHECK (extraction_status IN ('pending', 'success', 'failed')),
    extraction_error TEXT,
    extracted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_ir_reports_company_year (company_ticker, report_year),
    INDEX idx_ir_reports_type_year (report_type, report_year),
    INDEX idx_ir_reports_extraction_status (extraction_status),
    INDEX idx_ir_reports_download_date (download_date)
);

-- Create scraping configuration table
CREATE TABLE IF NOT EXISTS scraping_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Insert default scraping configuration
INSERT INTO scraping_config (config_key, config_value, description) VALUES
('default_user_agents', '["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"]', 'Default User-Agent strings for rotation'),
('default_ir_paths', '["/investors/","/investor-relations/","/financial-reports/","/documents/"]', 'Default IR report URL paths to try'),
('retry_delay_min', '3', 'Minimum delay between requests in seconds'),
('retry_delay_max', '10', 'Maximum delay between requests in seconds'),
('max_retries', '3', 'Maximum number of retry attempts per company'),
('rate_limit_delay', '5', 'Delay when rate limited in seconds'),
('test_mode_limit', '5', 'Number of companies to process in test mode')
ON CONFLICT (config_key) DO NOTHING;

-- Create view for scraping dashboard
CREATE OR REPLACE VIEW ir_scraping_dashboard AS
SELECT 
    c.ticker,
    c.name,
    c.website_url,
    c.investor_relations_url,
    c.last_scraped_at,
    c.ir_expected_release_date,
    c.actual_release_date,
    c.scraping_status,
    c.last_scraping_error,
    c.last_scraping_attempt,
    c.fiscal_year_end_month,
    c.fiscal_year_end_day,
    
    -- Calculate next expected release date
    CASE 
        WHEN c.fiscal_year_end_month = 12 THEN 
            CASE 
                WHEN EXTRACT(MONTH FROM CURRENT_DATE) >= 12 THEN 
                    DATE(CURRENT_DATE + INTERVAL '1 year') + INTERVAL '3 months'
                ELSE 
                    DATE(CURRENT_DATE) + INTERVAL '3 months'
            END
        ELSE 
            DATE(CURRENT_DATE) + INTERVAL '3 months'
    END::DATE AS next_expected_release_date,
    
    -- Count recent scraping attempts
    (SELECT COUNT(*) FROM ir_scraping_history h 
     WHERE h.company_ticker = c.ticker 
     AND h.scraping_date >= CURRENT_DATE - INTERVAL '30 days') AS recent_attempts,
    
    -- Count successful scrapes in last 30 days
    (SELECT COUNT(*) FROM ir_scraping_history h 
     WHERE h.company_ticker = c.ticker 
     AND h.status = 'success'
     AND h.scraping_date >= CURRENT_DATE - INTERVAL '30 days') AS recent_successes,
    
    -- Count failed scrapes in last 30 days
    (SELECT COUNT(*) FROM ir_scraping_history h 
     WHERE h.company_ticker = c.ticker 
     AND h.status = 'failed'
     AND h.scraping_date >= CURRENT_DATE - INTERVAL '30 days') AS recent_failures,
    
    -- Latest error message
    (SELECT h.error_message FROM ir_scraping_history h 
     WHERE h.company_ticker = c.ticker 
     AND h.status = 'failed'
     ORDER BY h.created_at DESC 
     LIMIT 1) AS latest_error,
    
    -- Total reports downloaded
    (SELECT COUNT(*) FROM ir_reports r WHERE r.company_ticker = c.ticker) AS total_reports,
    
    -- Latest report date
    (SELECT MAX(r.download_date) FROM ir_reports r WHERE r.company_ticker = c.ticker) AS latest_report_date
    
FROM companies c
WHERE c.is_active = 'Y'
ORDER BY c.ticker;

-- Create function to calculate expected release date
CREATE OR REPLACE FUNCTION calculate_expected_release_date(
    p_ticker VARCHAR(10),
    p_report_type VARCHAR(20) DEFAULT 'annual'
) RETURNS DATE AS $$
DECLARE
    v_fiscal_month INTEGER;
    v_fiscal_day INTEGER;
    v_expected_date DATE;
BEGIN
    -- Get company fiscal year end
    SELECT fiscal_year_end_month, fiscal_year_end_day 
    INTO v_fiscal_month, v_fiscal_day
    FROM companies 
    WHERE ticker = p_ticker;
    
    -- Default to December 31 if not set
    IF v_fiscal_month IS NULL THEN
        v_fiscal_month := 12;
        v_fiscal_day := 31;
    END IF;
    
    -- Calculate expected release date based on report type
    CASE p_report_type
        WHEN 'annual' THEN
            -- Annual reports typically released 2-3 months after fiscal year end
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '3 months';
        WHEN 'q1' THEN
            -- Q1 reports typically released mid-April
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '3 months';
        WHEN 'q2' THEN
            -- Q2 reports typically released mid-July
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '6 months';
        WHEN 'q3' THEN
            -- Q3 reports typically released mid-October
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '9 months';
        WHEN 'q4' THEN
            -- Q4 reports typically released mid-January
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '12 months';
        ELSE
            v_expected_date := DATE(CURRENT_DATE) + INTERVAL '3 months';
    END CASE;
    
    RETURN v_expected_date;
END;
$$ LANGUAGE plpgsql;

-- Create function to get companies due for scraping
CREATE OR REPLACE FUNCTION get_companies_due_for_scraping() 
RETURNS TABLE(
    ticker VARCHAR(10),
    name VARCHAR(255),
    website_url TEXT,
    investor_relations_url TEXT,
    last_scraped_at TIMESTAMP,
    ir_expected_release_date DATE,
    reason TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.ticker,
        c.name,
        c.website_url,
        c.investor_relations_url,
        c.last_scraped_at,
        c.ir_expected_release_date,
        CASE 
            WHEN c.last_scraped_at IS NULL THEN 'Never scraped before'
            WHEN c.ir_expected_release_date IS NOT NULL AND c.ir_expected_release_date <= CURRENT_DATE THEN 
                'Expected release date has passed'
            WHEN c.last_scraped_at < CURRENT_DATE - INTERVAL '90 days' THEN 
                'Last scraped more than 90 days ago'
            ELSE 'Manual trigger or other reason'
        END AS reason
    FROM companies c
    WHERE c.is_active = 'Y'
    AND (c.website_url IS NOT NULL OR c.investor_relations_url IS NOT NULL)
    AND (
        c.last_scraped_at IS NULL
        OR (c.ir_expected_release_date IS NOT NULL AND c.ir_expected_release_date <= CURRENT_DATE AND c.last_scraped_at < c.ir_expected_release_date)
        OR c.last_scraped_at < CURRENT_DATE - INTERVAL '90 days'
    )
    ORDER BY c.ticker;
END;
$$ LANGUAGE plpgsql;

-- Create function to update scraping status
CREATE OR REPLACE FUNCTION update_scraping_status(
    p_ticker VARCHAR(10),
    p_status VARCHAR(20),
    p_error_message TEXT DEFAULT NULL,
    p_report_url TEXT DEFAULT NULL,
    p_file_path TEXT DEFAULT NULL,
    p_file_size BIGINT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Update company table
    UPDATE companies 
    SET 
        last_scraped_at = CASE WHEN p_status = 'success' THEN CURRENT_TIMESTAMP ELSE last_scraped_at END,
        actual_release_date = CASE WHEN p_status = 'success' THEN CURRENT_DATE ELSE actual_release_date END,
        scraping_status = p_status,
        last_scraping_error = p_error_message,
        last_scraping_attempt = CURRENT_TIMESTAMP
    WHERE ticker = p_ticker;
    
    -- Insert into scraping history
    INSERT INTO ir_scraping_history (
        company_ticker,
        scraping_date,
        report_url,
        file_path,
        file_size,
        status,
        error_message,
        created_at
    ) VALUES (
        p_ticker,
        CURRENT_DATE,
        p_report_url,
        p_file_path,
        p_file_size,
        p_status,
        p_error_message,
        CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_companies_scraping_status ON companies(scraping_status);
CREATE INDEX IF NOT EXISTS idx_companies_last_scraped_at ON companies(last_scraped_at);
CREATE INDEX IF NOT EXISTS idx_companies_expected_release_date ON companies(ir_expected_release_date);

-- Add comments for documentation
COMMENT ON TABLE ir_scraping_history IS 'Tracks all IR scraping attempts and results';
COMMENT ON TABLE ir_reports IS 'Stores metadata about downloaded IR reports';
COMMENT ON TABLE scraping_config IS 'Configuration settings for IR scraping';
COMMENT ON VIEW ir_scraping_dashboard IS 'Dashboard view for monitoring IR scraping status';
COMMENT ON FUNCTION calculate_expected_release_date IS 'Calculates expected release date based on company fiscal calendar';
COMMENT ON FUNCTION get_companies_due_for_scraping IS 'Returns companies that are due for IR scraping based on business logic';
COMMENT ON FUNCTION update_scraping_status IS 'Updates scraping status and logs to history table'; 