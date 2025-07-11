-- Supabase Setup for Casablanca Insights
-- Run this in your Supabase SQL editor

-- 1. Create profiles table (User Metadata) - This is the key table for user management
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'admin')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    language_preference VARCHAR(10) DEFAULT 'en' CHECK (language_preference IN ('en', 'fr', 'ar')),
    newsletter_frequency VARCHAR(20) DEFAULT 'weekly' CHECK (newsletter_frequency IN ('daily', 'weekly', 'monthly')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for profiles
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles (email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles (tier);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer ON profiles (stripe_customer_id);

-- Enable Row Level Security for profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for profiles
CREATE POLICY "Users can view their own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 2. Create watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_ticker ON watchlists (ticker);

-- Enable Row Level Security (RLS)
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to only see their own watchlist items
CREATE POLICY "Users can view their own watchlist items" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own watchlist items
CREATE POLICY "Users can insert their own watchlist items" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own watchlist items
CREATE POLICY "Users can delete their own watchlist items" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- Create policy to allow users to update their own watchlist items
CREATE POLICY "Users can update their own watchlist items" ON watchlists
    FOR UPDATE USING (auth.uid() = user_id);

-- 3. Create price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(5) NOT NULL CHECK (alert_type IN ('above', 'below')),
    price_threshold DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    triggered_at TIMESTAMPTZ,
    UNIQUE(user_id, ticker, alert_type, price_threshold)
);

-- Create indexes for price alerts
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (is_active) WHERE is_active = true;

-- Enable Row Level Security for price alerts
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;

-- Create policies for price alerts
CREATE POLICY "Users can view their own price alerts" ON price_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own price alerts" ON price_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own price alerts" ON price_alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own price alerts" ON price_alerts
    FOR DELETE USING (auth.uid() = user_id);

-- 4. Create newsletter settings table
CREATE TABLE IF NOT EXISTS newsletter_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    frequency VARCHAR(20) DEFAULT 'weekly' CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    language VARCHAR(10) DEFAULT 'en' CHECK (language IN ('en', 'fr', 'ar')),
    categories JSONB DEFAULT '["markets", "earnings", "macro"]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, email)
);

-- Create indexes for newsletter settings
CREATE INDEX IF NOT EXISTS idx_newsletter_settings_user_id ON newsletter_settings (user_id);
CREATE INDEX IF NOT EXISTS idx_newsletter_settings_active ON newsletter_settings (is_active) WHERE is_active = true;

-- Enable Row Level Security for newsletter settings
ALTER TABLE newsletter_settings ENABLE ROW LEVEL SECURITY;

-- Create policies for newsletter settings
CREATE POLICY "Users can view their own newsletter settings" ON newsletter_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own newsletter settings" ON newsletter_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own newsletter settings" ON newsletter_settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own newsletter settings" ON newsletter_settings
    FOR DELETE USING (auth.uid() = user_id);

-- 5. Create billing history table (for Stripe webhook storage)
CREATE TABLE IF NOT EXISTS billing_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50),
    billing_period_start TIMESTAMPTZ,
    billing_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for billing history
CREATE INDEX IF NOT EXISTS idx_billing_history_user_id ON billing_history (user_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_stripe_customer ON billing_history (stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_created_at ON billing_history (created_at DESC);

-- Enable Row Level Security for billing history
ALTER TABLE billing_history ENABLE ROW LEVEL SECURITY;

-- Create policies for billing history
CREATE POLICY "Users can view their own billing history" ON billing_history
    FOR SELECT USING (auth.uid() = user_id);

-- 6. Create function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Create trigger to automatically create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 8. Create function to update profile when user data changes
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.profiles
    SET 
        email = NEW.email,
        updated_at = NOW()
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Create trigger to update profile when user data changes
DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;
CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_user_update();

-- 10. Create function to handle Stripe webhook updates
CREATE OR REPLACE FUNCTION public.handle_stripe_webhook()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user tier based on subscription status
    IF NEW.status = 'active' THEN
        UPDATE public.profiles
        SET tier = 'pro'
        WHERE stripe_customer_id = NEW.stripe_customer_id;
    ELSIF NEW.status IN ('canceled', 'past_due', 'unpaid') THEN
        UPDATE public.profiles
        SET tier = 'free'
        WHERE stripe_customer_id = NEW.stripe_customer_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 11. Create trigger for Stripe webhook handling
DROP TRIGGER IF EXISTS on_billing_history_insert ON billing_history;
CREATE TRIGGER on_billing_history_insert
    AFTER INSERT ON billing_history
    FOR EACH ROW EXECUTE FUNCTION public.handle_stripe_webhook();

-- 12. Create view for user dashboard data
CREATE OR REPLACE VIEW user_dashboard AS
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.tier,
    p.language_preference,
    p.newsletter_frequency,
    COUNT(w.ticker) as watchlist_count,
    COUNT(pa.id) as active_alerts_count,
    ns.is_active as newsletter_active
FROM profiles p
LEFT JOIN watchlists w ON p.id = w.user_id
LEFT JOIN price_alerts pa ON p.id = pa.user_id AND pa.is_active = true
LEFT JOIN newsletter_settings ns ON p.id = ns.user_id
GROUP BY p.id, p.email, p.full_name, p.tier, p.language_preference, p.newsletter_frequency, ns.is_active;

-- 13. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- 14. Insert sample data for testing (optional)
-- Only uncomment if you want to add test data
/*
INSERT INTO profiles (id, email, full_name, tier) VALUES 
    ('00000000-0000-0000-0000-000000000000', 'test@example.com', 'Test User', 'free')
ON CONFLICT (id) DO NOTHING;

INSERT INTO watchlists (user_id, ticker) VALUES 
    ('00000000-0000-0000-0000-000000000000', 'IAM'),
    ('00000000-0000-0000-0000-000000000000', 'BCP'),
    ('00000000-0000-0000-0000-000000000000', 'ATW')
ON CONFLICT (user_id, ticker) DO NOTHING;
*/ 