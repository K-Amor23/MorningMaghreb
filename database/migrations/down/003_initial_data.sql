-- Down Migration: 003_initial_data
-- Description: Remove initial data

DELETE FROM market_data WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
DELETE FROM companies WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
