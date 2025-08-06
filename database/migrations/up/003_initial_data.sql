-- Migration: 003_initial_data
-- Description: Insert initial data for development
-- Created: 2025-08-06T16:16:17.157063

-- Insert sample companies
INSERT INTO companies (ticker, name, sector, market_cap, current_price, price_change_percent) VALUES
('ATW', 'Attijariwafa Bank', 'Banking', 45000000000, 45.50, 2.1),
('BMCE', 'BMCE Bank of Africa', 'Banking', 28000000000, 32.80, -1.2),
('IAM', 'Maroc Telecom', 'Telecommunications', 65000000000, 78.90, 0.8),
('CIH', 'CIH Bank', 'Banking', 15000000000, 18.20, 1.5),
('CMT', 'Compagnie Minière de Touissit', 'Mining', 8500000000, 12.40, -0.5)
ON CONFLICT (ticker) DO NOTHING;

-- Insert sample market data
INSERT INTO market_data (ticker, price, change_percent, volume, high, low, open_price, close_price, date) VALUES
('ATW', 45.50, 2.1, 1250000, 46.20, 44.80, 44.90, 45.50, CURRENT_DATE),
('BMCE', 32.80, -1.2, 890000, 33.50, 32.40, 33.20, 32.80, CURRENT_DATE),
('IAM', 78.90, 0.8, 2100000, 79.50, 78.20, 78.30, 78.90, CURRENT_DATE),
('CIH', 18.20, 1.5, 450000, 18.50, 17.90, 17.95, 18.20, CURRENT_DATE),
('CMT', 12.40, -0.5, 320000, 12.60, 12.20, 12.45, 12.40, CURRENT_DATE)
ON CONFLICT DO NOTHING;
