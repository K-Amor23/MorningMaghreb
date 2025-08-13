-- FX daily benchmark rates and remittance quotes schema

-- 1) Daily FX benchmark rates
--    Stores official and fallback benchmark rates per day per currency pair
CREATE TABLE IF NOT EXISTS fx_daily_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rate_date DATE NOT NULL,
    currency_pair TEXT NOT NULL CHECK (position('/' in currency_pair) > 0),
    source TEXT NOT NULL,
    rate NUMERIC NOT NULL CHECK (rate > 0),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (rate_date, currency_pair, source)
);

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_fx_daily_rates_pair_date ON fx_daily_rates (currency_pair, rate_date DESC);

-- 2) Remittance quotes (per provider, amount, day)
CREATE TABLE IF NOT EXISTS remittance_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_date DATE NOT NULL,
    currency_pair TEXT NOT NULL CHECK (position('/' in currency_pair) > 0),
    provider TEXT NOT NULL,
    rate NUMERIC NOT NULL CHECK (rate > 0),
    fee_amount NUMERIC DEFAULT 0,
    fee_currency TEXT DEFAULT 'USD',
    effective_rate NUMERIC NOT NULL CHECK (effective_rate > 0),
    transfer_amount NUMERIC NOT NULL CHECK (transfer_amount > 0),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (quote_date, currency_pair, provider, transfer_amount)
);

CREATE INDEX IF NOT EXISTS idx_remit_quotes_pair_date ON remittance_quotes (currency_pair, quote_date DESC);

-- Optional: view for latest daily benchmarks per pair
CREATE OR REPLACE VIEW v_latest_fx_rates AS
SELECT DISTINCT ON (currency_pair)
    currency_pair,
    rate_date,
    source,
    rate,
    scraped_at
FROM fx_daily_rates
ORDER BY currency_pair, rate_date DESC, scraped_at DESC;


