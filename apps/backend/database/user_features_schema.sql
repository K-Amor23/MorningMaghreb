-- Enhanced User Features Schema for Casablanca Insights
-- Run this in your Supabase SQL editor

-- 1. Enhanced profiles table (User Metadata)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'admin')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
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
CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles (status);
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

-- 2. Enhanced watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for watchlists
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_is_default ON watchlists (is_default) WHERE is_default = true;

-- Enable Row Level Security for watchlists
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;

-- Create policies for watchlists
CREATE POLICY "Users can view their own watchlists" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own watchlists" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own watchlists" ON watchlists
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own watchlists" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- 3. Watchlist items table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES watchlists(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    notes TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(watchlist_id, ticker)
);

-- Create indexes for watchlist items
CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON watchlist_items (watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_ticker ON watchlist_items (ticker);

-- Enable Row Level Security for watchlist items
ALTER TABLE watchlist_items ENABLE ROW LEVEL SECURITY;

-- Create policies for watchlist items (users can only access items in their own watchlists)
CREATE POLICY "Users can view their own watchlist items" ON watchlist_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM watchlists 
            WHERE watchlists.id = watchlist_items.watchlist_id 
            AND watchlists.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own watchlist items" ON watchlist_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM watchlists 
            WHERE watchlists.id = watchlist_items.watchlist_id 
            AND watchlists.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own watchlist items" ON watchlist_items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM watchlists 
            WHERE watchlists.id = watchlist_items.watchlist_id 
            AND watchlists.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own watchlist items" ON watchlist_items
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM watchlists 
            WHERE watchlists.id = watchlist_items.watchlist_id 
            AND watchlists.user_id = auth.uid()
        )
    );

-- 4. Enhanced price alerts table
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('above', 'below', 'change_percent', 'volume_spike')),
    price_threshold DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    triggered_at TIMESTAMPTZ,
    notification_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for price alerts
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_price_alerts_alert_type ON price_alerts (alert_type);

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

-- 5. Functions for automatic profile creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile when user signs up
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 6. Function to ensure only one default watchlist per user
CREATE OR REPLACE FUNCTION public.ensure_single_default_watchlist()
RETURNS TRIGGER AS $$
BEGIN
    -- If this watchlist is being set as default, unset others
    IF NEW.is_default = true THEN
        UPDATE watchlists 
        SET is_default = false 
        WHERE user_id = NEW.user_id 
        AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to ensure only one default watchlist per user
CREATE TRIGGER on_watchlist_default_change
    AFTER INSERT OR UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION public.ensure_single_default_watchlist();

-- 7. Function to update watchlist updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_watchlist_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE watchlists 
    SET updated_at = NOW() 
    WHERE id = NEW.watchlist_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update watchlist timestamp when items change
CREATE TRIGGER on_watchlist_item_change
    AFTER INSERT OR UPDATE OR DELETE ON watchlist_items
    FOR EACH ROW EXECUTE FUNCTION public.update_watchlist_updated_at();

-- 8. Function to update profile updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update profile timestamp
CREATE TRIGGER on_profile_update
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_profile_updated_at();

-- 9. Function to update price alert updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_price_alert_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update price alert timestamp
CREATE TRIGGER on_price_alert_update
    BEFORE UPDATE ON price_alerts
    FOR EACH ROW EXECUTE FUNCTION public.update_price_alert_updated_at();

-- 10. View for user dashboard data
CREATE OR REPLACE VIEW user_dashboard AS
SELECT 
    p.id as user_id,
    p.email,
    p.full_name,
    p.tier,
    p.status,
    COUNT(DISTINCT w.id) as watchlist_count,
    COUNT(DISTINCT pa.id) as alert_count,
    COUNT(DISTINCT CASE WHEN pa.is_active = true THEN pa.id END) as active_alert_count,
    p.created_at as user_created_at,
    p.updated_at as profile_updated_at
FROM profiles p
LEFT JOIN watchlists w ON p.id = w.user_id
LEFT JOIN price_alerts pa ON p.id = pa.user_id
GROUP BY p.id, p.email, p.full_name, p.tier, p.status, p.created_at, p.updated_at;

-- 11. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated; 