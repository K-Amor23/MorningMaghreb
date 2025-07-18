-- Casablanca Stock Exchange Companies Database Schema
-- This schema defines the structure for storing CSE company information

-- Create the cse_companies table
CREATE TABLE IF NOT EXISTS cse_companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    isin VARCHAR(12),
    sector VARCHAR(100),
    listing_date DATE,
    source_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cse_companies_ticker ON cse_companies(ticker);
CREATE INDEX IF NOT EXISTS idx_cse_companies_isin ON cse_companies(isin);
CREATE INDEX IF NOT EXISTS idx_cse_companies_sector ON cse_companies(sector);
CREATE INDEX IF NOT EXISTS idx_cse_companies_listing_date ON cse_companies(listing_date);
CREATE INDEX IF NOT EXISTS idx_cse_companies_scraped_at ON cse_companies(scraped_at);

-- Create audit log table for tracking changes
CREATE TABLE IF NOT EXISTS cse_companies_audit (
    audit_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES cse_companies(company_id),
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT 'system'
);

-- Create index on audit table
CREATE INDEX IF NOT EXISTS idx_cse_companies_audit_company_id ON cse_companies_audit(company_id);
CREATE INDEX IF NOT EXISTS idx_cse_companies_audit_changed_at ON cse_companies_audit(changed_at);

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_cse_companies_updated_at 
    BEFORE UPDATE ON cse_companies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to log audit changes
CREATE OR REPLACE FUNCTION log_cse_company_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO cse_companies_audit (company_id, action, field_name, new_value)
        VALUES (NEW.company_id, 'INSERT', 'ALL', 'New company created');
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Log changes for each field
        IF OLD.name != NEW.name THEN
            INSERT INTO cse_companies_audit (company_id, action, field_name, old_value, new_value)
            VALUES (NEW.company_id, 'UPDATE', 'name', OLD.name, NEW.name);
        END IF;
        
        IF OLD.ticker != NEW.ticker THEN
            INSERT INTO cse_companies_audit (company_id, action, field_name, old_value, new_value)
            VALUES (NEW.company_id, 'UPDATE', 'ticker', OLD.ticker, NEW.ticker);
        END IF;
        
        IF OLD.isin IS DISTINCT FROM NEW.isin THEN
            INSERT INTO cse_companies_audit (company_id, action, field_name, old_value, new_value)
            VALUES (NEW.company_id, 'UPDATE', 'isin', OLD.isin, NEW.isin);
        END IF;
        
        IF OLD.sector IS DISTINCT FROM NEW.sector THEN
            INSERT INTO cse_companies_audit (company_id, action, field_name, old_value, new_value)
            VALUES (NEW.company_id, 'UPDATE', 'sector', OLD.sector, NEW.sector);
        END IF;
        
        IF OLD.listing_date IS DISTINCT FROM NEW.listing_date THEN
            INSERT INTO cse_companies_audit (company_id, action, field_name, old_value, new_value)
            VALUES (NEW.company_id, 'UPDATE', 'listing_date', OLD.listing_date::text, NEW.listing_date::text);
        END IF;
        
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO cse_companies_audit (company_id, action, field_name, old_value)
        VALUES (OLD.company_id, 'DELETE', 'ALL', 'Company deleted');
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create trigger for audit logging
CREATE TRIGGER cse_companies_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON cse_companies
    FOR EACH ROW
    EXECUTE FUNCTION log_cse_company_changes();

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

-- Insert some sample data for testing
INSERT INTO cse_companies (name, ticker, isin, sector, listing_date, source_url) VALUES
('Attijariwafa Bank', 'ATW', 'MA0000011885', 'Banking', '2004-01-01', 'https://www.casablanca-bourse.com'),
('Maroc Telecom', 'IAM', 'MA0000011886', 'Telecommunications', '2001-12-01', 'https://www.casablanca-bourse.com'),
('Banque Centrale Populaire', 'BCP', 'MA0000011887', 'Banking', '2004-01-01', 'https://www.casablanca-bourse.com'),
('BMCE Bank', 'BMCE', 'MA0000011888', 'Banking', '1995-01-01', 'https://www.casablanca-bourse.com')
ON CONFLICT (ticker) DO NOTHING;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON cse_companies TO your_user;
-- GRANT SELECT ON cse_companies_audit TO your_user;
-- GRANT SELECT ON cse_companies_view TO your_user;
-- GRANT EXECUTE ON FUNCTION get_cse_company_stats() TO your_user;
-- GRANT EXECUTE ON FUNCTION search_cse_companies(TEXT) TO your_user; 