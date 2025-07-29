-- Migration script to update ticker field lengths for ETFs and Bonds
-- Run this script to fix the "value too long for type character varying(10)" error

-- Update ETFs table ticker field
ALTER TABLE IF EXISTS etfs 
ALTER COLUMN ticker TYPE VARCHAR(20);

-- Update Bonds table ticker field  
ALTER TABLE IF EXISTS bonds 
ALTER COLUMN ticker TYPE VARCHAR(20);

-- Update yield_curve table benchmark_bond field
ALTER TABLE IF EXISTS yield_curve 
ALTER COLUMN benchmark_bond TYPE VARCHAR(25);

-- Verify the changes
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name IN ('etfs', 'bonds', 'yield_curve')
AND column_name IN ('ticker', 'benchmark_bond')
ORDER BY table_name, column_name; 