# Database Setup Guide for Casablanca Insights

## 🗄️ Supabase Database Configuration

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note down your project URL and anon key

### 2. Environment Variables

Add these to your `.env` file in the `apps/web` directory:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# Environment
NEXT_PUBLIC_ENV=development

# Feature Flags
NEXT_PUBLIC_PREMIUM_ENFORCEMENT=false

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Database Schema Setup

Run the following SQL in your Supabase SQL Editor:

#### Core Tables

```sql
-- 1. Profiles Table (User Management)
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

-- 2. Watchlists Table
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- 3. Price Alerts Table
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

-- 4. Portfolios Table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Portfolio Holdings Table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    shares DECIMAL(15,6) NOT NULL,
    average_price DECIMAL(12,4) NOT NULL,
    purchase_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Paper Trading Tables
CREATE TABLE IF NOT EXISTS paper_trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    initial_balance DECIMAL(15,2) NOT NULL DEFAULT 100000.00,
    current_balance DECIMAL(15,2) NOT NULL DEFAULT 100000.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paper_trading_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES paper_trading_accounts(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    order_type VARCHAR(10) NOT NULL CHECK (order_type IN ('buy', 'sell')),
    shares DECIMAL(15,6) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'filled', 'cancelled', 'rejected')),
    filled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Newsletter Settings Table
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

-- 8. Billing History Table
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
```

#### Row Level Security (RLS) Policies

```sql
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_history ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert their own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Watchlists policies
CREATE POLICY "Users can view their own watchlist" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own watchlist" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own watchlist" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

-- Price alerts policies
CREATE POLICY "Users can view their own price alerts" ON price_alerts
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own price alerts" ON price_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own price alerts" ON price_alerts
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own price alerts" ON price_alerts
    FOR DELETE USING (auth.uid() = user_id);

-- Portfolios policies
CREATE POLICY "Users can view their own portfolios" ON portfolios
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own portfolios" ON portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own portfolios" ON portfolios
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own portfolios" ON portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- Portfolio holdings policies
CREATE POLICY "Users can view their own portfolio holdings" ON portfolio_holdings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = portfolio_holdings.portfolio_id 
            AND portfolios.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can insert their own portfolio holdings" ON portfolio_holdings
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = portfolio_holdings.portfolio_id 
            AND portfolios.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can update their own portfolio holdings" ON portfolio_holdings
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = portfolio_holdings.portfolio_id 
            AND portfolios.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can delete their own portfolio holdings" ON portfolio_holdings
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM portfolios 
            WHERE portfolios.id = portfolio_holdings.portfolio_id 
            AND portfolios.user_id = auth.uid()
        )
    );

-- Paper trading policies
CREATE POLICY "Users can view their own paper trading accounts" ON paper_trading_accounts
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own paper trading accounts" ON paper_trading_accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own paper trading accounts" ON paper_trading_accounts
    FOR UPDATE USING (auth.uid() = user_id);

-- Newsletter settings policies
CREATE POLICY "Users can view their own newsletter settings" ON newsletter_settings
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own newsletter settings" ON newsletter_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own newsletter settings" ON newsletter_settings
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own newsletter settings" ON newsletter_settings
    FOR DELETE USING (auth.uid() = user_id);

-- Billing history policies
CREATE POLICY "Users can view their own billing history" ON billing_history
    FOR SELECT USING (auth.uid() = user_id);
```

#### Functions and Triggers

```sql
-- Function to handle new user signup
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

-- Trigger to automatically create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update profile when user data changes
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

-- Trigger to update profile when user data changes
DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;
CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_user_update();
```

#### Views

```sql
-- User dashboard view
CREATE OR REPLACE VIEW user_dashboard AS
SELECT 
    p.id,
    p.email,
    p.full_name,
    p.tier,
    p.language_preference,
    COUNT(DISTINCT w.ticker) as watchlist_count,
    COUNT(DISTINCT pa.id) as active_alerts_count,
    COUNT(DISTINCT pf.id) as portfolio_count,
    COUNT(DISTINCT pta.id) as paper_trading_accounts_count
FROM profiles p
LEFT JOIN watchlists w ON p.id = w.user_id
LEFT JOIN price_alerts pa ON p.id = pa.user_id AND pa.is_active = true
LEFT JOIN portfolios pf ON p.id = pf.user_id
LEFT JOIN paper_trading_accounts pta ON p.id = pta.user_id AND pta.is_active = true
GROUP BY p.id, p.email, p.full_name, p.tier, p.language_preference;

-- Portfolio summary view
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    p.id as portfolio_id,
    p.name as portfolio_name,
    p.user_id,
    COUNT(ph.ticker) as total_holdings,
    SUM(ph.shares * ph.average_price) as total_invested,
    AVG(ph.average_price) as avg_price
FROM portfolios p
LEFT JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
GROUP BY p.id, p.name, p.user_id;
```

### 4. Indexes for Performance

```sql
-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles (email);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles (tier);
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_ticker ON watchlists (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_ticker ON price_alerts (ticker);
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios (user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio_id ON portfolio_holdings (portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_ticker ON portfolio_holdings (ticker);
CREATE INDEX IF NOT EXISTS idx_paper_trading_accounts_user_id ON paper_trading_accounts (user_id);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_account_id ON paper_trading_orders (account_id);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_ticker ON paper_trading_orders (ticker);
CREATE INDEX IF NOT EXISTS idx_paper_trading_orders_status ON paper_trading_orders (order_status);
```

### 5. Test the Setup

After running all the SQL above, you can test the setup by:

1. **Check if tables exist:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('profiles', 'watchlists', 'price_alerts', 'portfolios');
```

2. **Check if RLS is enabled:**
```sql
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('profiles', 'watchlists', 'price_alerts', 'portfolios');
```

3. **Check if policies exist:**
```sql
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('profiles', 'watchlists', 'price_alerts', 'portfolios');
```

### 6. Next Steps

1. **Configure Authentication** in Supabase Dashboard
2. **Set up Email Templates** for user notifications
3. **Configure Storage** for file uploads (reports, exports)
4. **Set up Edge Functions** for webhooks and background jobs
5. **Configure Real-time** subscriptions for live data

### 7. Security Checklist

- ✅ Row Level Security (RLS) enabled on all tables
- ✅ Policies restrict users to their own data
- ✅ Triggers automatically create user profiles
- ✅ Proper indexes for performance
- ✅ Input validation and constraints
- ✅ Audit trails with created_at/updated_at timestamps

Your database is now ready for account management and all the features of Casablanca Insights! 