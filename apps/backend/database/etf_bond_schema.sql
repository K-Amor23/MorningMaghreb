-- ETFs and Bonds Database Schema for Casablanca Insight
-- This schema extends the existing financial data structure

-- 1. ETFs Table
CREATE TABLE IF NOT EXISTS etfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(25) NOT NULL UNIQUE,
    isin VARCHAR(12) UNIQUE,
    underlying_index VARCHAR(100),
    issuer VARCHAR(100),
    expense_ratio DECIMAL(5,4), -- Annual expense ratio as percentage
    inception_date DATE,
    listing_date DATE,
    asset_class VARCHAR(50), -- 'equity', 'bond', 'commodity', 'mixed'
    geographic_focus VARCHAR(100), -- 'Morocco', 'Africa', 'Global', etc.
    sector_focus VARCHAR(100), -- 'Technology', 'Financial', 'Energy', etc.
    currency VARCHAR(3) DEFAULT 'MAD',
    dividend_frequency VARCHAR(20), -- 'monthly', 'quarterly', 'annual', 'none'
    rebalancing_frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly', 'quarterly'
    source_url TEXT,
    prospectus_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. ETF Data Table (Daily NAV and performance)
CREATE TABLE IF NOT EXISTS etf_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etf_id UUID REFERENCES etfs(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    nav DECIMAL(12,4) NOT NULL, -- Net Asset Value
    price DECIMAL(12,4) NOT NULL, -- Market price
    volume BIGINT,
    total_assets DECIMAL(20,2), -- AUM in MAD
    shares_outstanding BIGINT,
    premium_discount DECIMAL(5,4), -- (Price - NAV) / NAV
    change_amount DECIMAL(12,4),
    change_percent DECIMAL(8,6),
    high_24h DECIMAL(12,4),
    low_24h DECIMAL(12,4),
    open_price DECIMAL(12,4),
    previous_close DECIMAL(12,4),
    source VARCHAR(50) DEFAULT 'cse',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(etf_id, date)
);

-- 3. Bonds Table
CREATE TABLE IF NOT EXISTS bonds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(25) NOT NULL UNIQUE,
    isin VARCHAR(12) UNIQUE,
    issuer VARCHAR(100) NOT NULL, -- 'Government', 'Corporate', 'Municipal'
    issuer_name VARCHAR(255), -- Specific issuer name
    bond_type VARCHAR(50), -- 'government', 'corporate', 'municipal', 'sukuk'
    currency VARCHAR(3) DEFAULT 'MAD',
    face_value DECIMAL(15,2) NOT NULL,
    coupon_rate DECIMAL(5,4), -- Annual coupon rate as percentage
    coupon_frequency VARCHAR(20), -- 'annual', 'semi-annual', 'quarterly', 'monthly'
    issue_date DATE,
    maturity_date DATE NOT NULL,
    issue_size DECIMAL(20,2), -- Total issue size in MAD
    minimum_investment DECIMAL(15,2),
    credit_rating VARCHAR(10), -- 'AAA', 'AA+', 'A', 'BBB', etc.
    rating_agency VARCHAR(50), -- 'Moody's', 'S&P', 'Fitch'
    callable BOOLEAN DEFAULT FALSE,
    puttable BOOLEAN DEFAULT FALSE,
    convertible BOOLEAN DEFAULT FALSE,
    floating_rate BOOLEAN DEFAULT FALSE,
    benchmark_rate VARCHAR(50), -- Reference rate for floating bonds
    spread DECIMAL(5,4), -- Spread over benchmark
    source_url TEXT,
    prospectus_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Bond Data Table (Daily prices and yields)
CREATE TABLE IF NOT EXISTS bond_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bond_id UUID REFERENCES bonds(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    price DECIMAL(12,4) NOT NULL, -- Clean price
    dirty_price DECIMAL(12,4), -- Price including accrued interest
    yield_to_maturity DECIMAL(8,6), -- YTM as percentage
    yield_to_call DECIMAL(8,6), -- YTC if callable
    current_yield DECIMAL(8,6), -- Annual coupon / current price
    modified_duration DECIMAL(8,4),
    convexity DECIMAL(8,4),
    accrued_interest DECIMAL(12,4),
    volume BIGINT,
    bid_price DECIMAL(12,4),
    ask_price DECIMAL(12,4),
    bid_yield DECIMAL(8,6),
    ask_yield DECIMAL(8,6),
    spread_to_benchmark DECIMAL(8,6), -- Spread to government bonds
    source VARCHAR(50) DEFAULT 'cse',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(bond_id, date)
);

-- 5. Yield Curve Table (Government bond yields by maturity)
CREATE TABLE IF NOT EXISTS yield_curve (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    maturity_months INTEGER NOT NULL, -- 3, 6, 12, 24, 36, 60, 120, etc.
    yield DECIMAL(8,6) NOT NULL, -- Yield as percentage
    benchmark_bond VARCHAR(25), -- Reference bond ticker
    source VARCHAR(50) DEFAULT 'bam', -- Bank Al-Maghrib
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, maturity_months)
);

-- 6. Bond Issuance Calendar
CREATE TABLE IF NOT EXISTS bond_issuance_calendar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issuer VARCHAR(100) NOT NULL,
    bond_name VARCHAR(255),
    expected_issue_date DATE,
    expected_maturity_date DATE,
    expected_size DECIMAL(20,2),
    expected_coupon_rate DECIMAL(5,4),
    expected_rating VARCHAR(10),
    status VARCHAR(20) DEFAULT 'announced', -- 'announced', 'priced', 'issued', 'cancelled'
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_etfs_ticker ON etfs(ticker);
CREATE INDEX IF NOT EXISTS idx_etfs_isin ON etfs(isin);
CREATE INDEX IF NOT EXISTS idx_etfs_asset_class ON etfs(asset_class);
CREATE INDEX IF NOT EXISTS idx_etfs_geographic_focus ON etfs(geographic_focus);
CREATE INDEX IF NOT EXISTS idx_etfs_sector_focus ON etfs(sector_focus);

CREATE INDEX IF NOT EXISTS idx_etf_data_etf_id_date ON etf_data(etf_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_etf_data_date ON etf_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_etf_data_nav ON etf_data(nav DESC);

CREATE INDEX IF NOT EXISTS idx_bonds_ticker ON bonds(ticker);
CREATE INDEX IF NOT EXISTS idx_bonds_isin ON bonds(isin);
CREATE INDEX IF NOT EXISTS idx_bonds_issuer ON bonds(issuer);
CREATE INDEX IF NOT EXISTS idx_bonds_bond_type ON bonds(bond_type);
CREATE INDEX IF NOT EXISTS idx_bonds_maturity_date ON bonds(maturity_date);
CREATE INDEX IF NOT EXISTS idx_bonds_credit_rating ON bonds(credit_rating);

CREATE INDEX IF NOT EXISTS idx_bond_data_bond_id_date ON bond_data(bond_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_bond_data_date ON bond_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_bond_data_yield ON bond_data(yield_to_maturity DESC);

CREATE INDEX IF NOT EXISTS idx_yield_curve_date ON yield_curve(date DESC);
CREATE INDEX IF NOT EXISTS idx_yield_curve_maturity ON yield_curve(maturity_months);

CREATE INDEX IF NOT EXISTS idx_bond_issuance_calendar_date ON bond_issuance_calendar(expected_issue_date);
CREATE INDEX IF NOT EXISTS idx_bond_issuance_calendar_status ON bond_issuance_calendar(status);

-- Update triggers for updated_at timestamps
CREATE TRIGGER update_etfs_updated_at 
    BEFORE UPDATE ON etfs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bonds_updated_at 
    BEFORE UPDATE ON bonds 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bond_issuance_calendar_updated_at 
    BEFORE UPDATE ON bond_issuance_calendar 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE etfs ENABLE ROW LEVEL SECURITY;
ALTER TABLE etf_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE bonds ENABLE ROW LEVEL SECURITY;
ALTER TABLE bond_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE yield_curve ENABLE ROW LEVEL SECURITY;
ALTER TABLE bond_issuance_calendar ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access
CREATE POLICY "Public read access to ETFs" ON etfs
    FOR SELECT USING (true);

CREATE POLICY "Public read access to ETF data" ON etf_data
    FOR SELECT USING (true);

CREATE POLICY "Public read access to bonds" ON bonds
    FOR SELECT USING (true);

CREATE POLICY "Public read access to bond data" ON bond_data
    FOR SELECT USING (true);

CREATE POLICY "Public read access to yield curve" ON yield_curve
    FOR SELECT USING (true);

CREATE POLICY "Public read access to bond issuance calendar" ON bond_issuance_calendar
    FOR SELECT USING (true);

-- Create views for easy data access
CREATE OR REPLACE VIEW latest_etf_data AS
SELECT 
    e.id as etf_id,
    e.name,
    e.ticker,
    e.isin,
    e.underlying_index,
    e.asset_class,
    e.geographic_focus,
    e.sector_focus,
    ed.date,
    ed.nav,
    ed.price,
    ed.volume,
    ed.total_assets,
    ed.premium_discount,
    ed.change_amount,
    ed.change_percent,
    ed.high_24h,
    ed.low_24h,
    ed.open_price,
    ed.previous_close
FROM etfs e
JOIN LATERAL (
    SELECT * FROM etf_data 
    WHERE etf_id = e.id 
    ORDER BY date DESC 
    LIMIT 1
) ed ON true
WHERE e.is_active = true;

CREATE OR REPLACE VIEW latest_bond_data AS
SELECT 
    b.id as bond_id,
    b.name,
    b.ticker,
    b.isin,
    b.issuer,
    b.issuer_name,
    b.bond_type,
    b.face_value,
    b.coupon_rate,
    b.maturity_date,
    b.credit_rating,
    bd.date,
    bd.price,
    bd.dirty_price,
    bd.yield_to_maturity,
    bd.yield_to_call,
    bd.current_yield,
    bd.modified_duration,
    bd.convexity,
    bd.accrued_interest,
    bd.volume,
    bd.bid_price,
    bd.ask_price,
    bd.bid_yield,
    bd.ask_yield,
    bd.spread_to_benchmark
FROM bonds b
JOIN LATERAL (
    SELECT * FROM bond_data 
    WHERE bond_id = b.id 
    ORDER BY date DESC 
    LIMIT 1
) bd ON true
WHERE b.is_active = true;

-- Sample data for testing
INSERT INTO etfs (name, ticker, isin, underlying_index, issuer, expense_ratio, asset_class, geographic_focus, sector_focus) VALUES
('MASI ETF', 'MASI-ETF', 'MA0000012345', 'MASI', 'CDG Capital', 0.0050, 'equity', 'Morocco', 'Broad Market'),
('MADEX ETF', 'MADEX-ETF', 'MA0000012346', 'MADEX', 'Attijari Finance', 0.0055, 'equity', 'Morocco', 'Large Cap'),
('Morocco Banks ETF', 'BANK-ETF', 'MA0000012347', 'Bank Index', 'BMCE Capital', 0.0060, 'equity', 'Morocco', 'Financial'),
('Morocco Government Bond ETF', 'GOVT-ETF', 'MA0000012348', 'Government Bond Index', 'CDG Capital', 0.0040, 'bond', 'Morocco', 'Government');

INSERT INTO bonds (name, ticker, isin, issuer, issuer_name, bond_type, face_value, coupon_rate, maturity_date, issue_size, credit_rating) VALUES
('Morocco Government Bond 2025', 'MOR-GOV-2025', 'MA0000012349', 'Government', 'Morocco Treasury', 'government', 10000.00, 0.0350, '2025-12-31', 10000000000.00, 'BBB+'),
('Morocco Government Bond 2030', 'MOR-GOV-2030', 'MA0000012350', 'Government', 'Morocco Treasury', 'government', 10000.00, 0.0400, '2030-12-31', 15000000000.00, 'BBB+'),
('Attijariwafa Bank Bond 2026', 'ATW-BOND-2026', 'MA0000012351', 'Corporate', 'Attijariwafa Bank', 'corporate', 10000.00, 0.0450, '2026-06-30', 5000000000.00, 'A-'),
('BMCE Bank Bond 2027', 'BMCE-BOND-2027', 'MA0000012352', 'Corporate', 'BMCE Bank', 'corporate', 10000.00, 0.0425, '2027-12-31', 3000000000.00, 'A-'); 