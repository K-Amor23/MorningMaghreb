-- Stripe Billing Schema for Casablanca Insights
-- Works with Supabase Postgres. Creates product/price/customer/subscription tables
-- and a lightweight events log for webhooks.

-- Extensions (Supabase has these; keep for local dev)
DO $$ BEGIN
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  CREATE EXTENSION IF NOT EXISTS pgcrypto;
EXCEPTION WHEN OTHERS THEN NULL; END $$;

-- ============================================================================
-- PRODUCTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_product_id text UNIQUE NOT NULL,
  active boolean NOT NULL DEFAULT true,
  name text NOT NULL,
  description text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_billing_products_active ON public.billing_products(active);

-- ============================================================================
-- PRICES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_prices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_price_id text UNIQUE NOT NULL,
  product_id uuid NOT NULL REFERENCES public.billing_products(id) ON DELETE CASCADE,
  active boolean NOT NULL DEFAULT true,
  currency text NOT NULL,
  unit_amount integer NOT NULL CHECK (unit_amount >= 0),
  interval text NOT NULL CHECK (interval IN ('day','week','month','year')),
  interval_count integer NOT NULL DEFAULT 1 CHECK (interval_count > 0),
  trial_period_days integer,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_billing_prices_product_id ON public.billing_prices(product_id);
CREATE INDEX IF NOT EXISTS idx_billing_prices_active ON public.billing_prices(active);

-- ============================================================================
-- CUSTOMERS
-- Note: In Supabase you can reference auth.users(id). If you're not on Supabase,
-- replace auth.users with your users table.
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  stripe_customer_id text UNIQUE NOT NULL,
  default_payment_method text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_billing_customers_user UNIQUE (user_id)
);

-- Optional: enforce Supabase auth.users FK (comment out if not using Supabase)
DO $$ BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'
  ) THEN
    ALTER TABLE public.billing_customers
      ADD CONSTRAINT fk_billing_customers_user
      FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_billing_customers_user_id ON public.billing_customers(user_id);

-- ============================================================================
-- SUBSCRIPTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_subscriptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  stripe_subscription_id text UNIQUE NOT NULL,
  status text NOT NULL CHECK (status IN (
    'trialing','active','past_due','canceled','incomplete','incomplete_expired','paused','unpaid'
  )),
  price_id uuid REFERENCES public.billing_prices(id) ON DELETE SET NULL,
  current_period_start timestamptz,
  current_period_end timestamptz,
  cancel_at_period_end boolean NOT NULL DEFAULT false,
  canceled_at timestamptz,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DO $$ BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'
  ) THEN
    ALTER TABLE public.billing_subscriptions
      ADD CONSTRAINT fk_billing_subscriptions_user
      FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_billing_subscriptions_user_id ON public.billing_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_subscriptions_status ON public.billing_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_billing_subscriptions_period_end ON public.billing_subscriptions(current_period_end);

-- ============================================================================
-- INVOICES (optional but useful)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  stripe_invoice_id text UNIQUE NOT NULL,
  status text,
  amount_due integer,
  amount_paid integer,
  currency text,
  hosted_invoice_url text,
  created_at timestamptz NOT NULL DEFAULT now()
);

DO $$ BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'
  ) THEN
    ALTER TABLE public.billing_invoices
      ADD CONSTRAINT fk_billing_invoices_user
      FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_billing_invoices_user_id ON public.billing_invoices(user_id);

-- ============================================================================
-- WEBHOOK EVENTS (for idempotency/logging)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.billing_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id text UNIQUE NOT NULL,
  type text NOT NULL,
  payload jsonb NOT NULL,
  processed boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- UPDATED_AT TRIGGERS (optional)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  CREATE TRIGGER trg_products_updated
    BEFORE UPDATE ON public.billing_products
    FOR EACH ROW EXECUTE PROCEDURE public.set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_prices_updated
    BEFORE UPDATE ON public.billing_prices
    FOR EACH ROW EXECUTE PROCEDURE public.set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_customers_updated
    BEFORE UPDATE ON public.billing_customers
    FOR EACH ROW EXECUTE PROCEDURE public.set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_subscriptions_updated
    BEFORE UPDATE ON public.billing_subscriptions
    FOR EACH ROW EXECUTE PROCEDURE public.set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ============================================================================
-- OPTIONAL RLS (enable and tune in Supabase if needed)
-- Note: For initial setup, you can leave RLS off or add policies later.
-- ============================================================================
-- ALTER TABLE public.billing_customers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.billing_subscriptions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.billing_invoices ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.billing_products ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.billing_prices ENABLE ROW LEVEL SECURITY;

-- Example policy (read own billing data)
-- CREATE POLICY "Users can read own billing rows"
--   ON public.billing_subscriptions FOR SELECT
--   USING (auth.uid() = user_id);


