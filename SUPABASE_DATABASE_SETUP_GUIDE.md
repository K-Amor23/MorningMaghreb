# 🗄️ Supabase Database Setup Guide - Casablanca Insights

## 🎯 **Overview**

This guide will help you set up the complete Supabase database for your Casablanca Insights platform, including:

- ✅ **Enhanced Database Schema** with all tables
- ✅ **Row Level Security (RLS)** policies
- ✅ **Real-time Subscriptions** for live data
- ✅ **Newsletter Management** system
- ✅ **Volume Data** tracking
- ✅ **User Management** and authentication
- ✅ **Paper Trading** system
- ✅ **Sentiment Voting** system

---

## 🚀 **Quick Setup (Automated)**

### **Step 1: Run the Setup Script**

```bash
# From project root directory
python3 scripts/setup_supabase_database.py
```

This script will automatically:
- Set up all database tables
- Configure RLS policies
- Insert sample data
- Test connectivity
- Verify real-time subscriptions

---

## 📋 **Manual Setup (Step by Step)**

### **Step 1: Access Supabase Dashboard**

1. **Go to Supabase**: [supabase.com](https://supabase.com)
2. **Open your project**: Casablanca Insights
3. **Navigate to SQL Editor**

### **Step 2: Execute Schema**

1. **Open SQL Editor** in Supabase dashboard
2. **Copy and paste** the content from `database/enhanced_schema_with_rls.sql`
3. **Click "Run"** to execute the schema

### **Step 3: Verify Tables**

Check that these tables were created:

**Core Tables:**
- `users` - User profiles
- `user_profiles` - Extended user data
- `companies` - Company information
- `quotes` - Market quotes
- `volume_data` - Volume analysis

**Newsletter Tables:**
- `newsletter_subscribers` - Email subscribers
- `newsletter_campaigns` - Email campaigns
- `newsletter_campaign_recipients` - Campaign tracking
- `newsletter_templates` - Email templates

**Trading Tables:**
- `watchlists` - User watchlists
- `watchlist_items` - Watchlist stocks
- `price_alerts` - Price alerts
- `paper_trading_accounts` - Paper trading
- `paper_trading_positions` - Trading positions

**Analytics Tables:**
- `sentiment_votes` - User sentiment
- `volume_alerts` - Volume alerts

---

## 🔒 **Row Level Security (RLS) Policies**

### **What RLS Does**

RLS ensures that users can only access their own data:

- **Users** can only see their own profile
- **Watchlists** are private to each user
- **Paper trading** accounts are isolated
- **Price alerts** are user-specific
- **Sentiment votes** are private but aggregated

### **Policy Examples**

```sql
-- Users can only view their own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

-- Users can only manage their own watchlists
CREATE POLICY "Users can manage own watchlists" ON public.watchlists
    FOR ALL USING (auth.uid() = user_id);
```

### **Testing RLS**

```sql
-- Test as authenticated user
SELECT * FROM users WHERE id = auth.uid();

-- Test as anonymous user (should be restricted)
SELECT * FROM users;
```

---

## 📡 **Real-time Subscriptions**

### **Enabled Tables**

Real-time is enabled for these tables:
- `quotes` - Live market data
- `volume_data` - Volume updates
- `volume_alerts` - Volume alerts
- `sentiment_votes` - Sentiment changes
- `price_alerts` - Price alerts

### **Frontend Integration**

```javascript
// Subscribe to live quotes
const subscription = supabase
  .channel('quotes')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'quotes' },
    (payload) => {
      console.log('New quote:', payload.new);
    }
  )
  .subscribe();

// Subscribe to volume alerts
const volumeSubscription = supabase
  .channel('volume_alerts')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'volume_alerts' },
    (payload) => {
      console.log('Volume alert:', payload.new);
    }
  )
  .subscribe();
```

---

## 📧 **Newsletter System**

### **Tables Overview**

1. **`newsletter_subscribers`** - Email subscribers
2. **`newsletter_campaigns`** - Email campaigns
3. **`newsletter_campaign_recipients`** - Delivery tracking
4. **`newsletter_templates`** - Email templates

### **Adding Subscribers**

```sql
-- Add a new subscriber
INSERT INTO newsletter_subscribers (email, name, preferences)
VALUES ('user@example.com', 'John Doe', '{"frequency": "weekly"}');
```

### **Creating Campaigns**

```sql
-- Create a newsletter campaign
INSERT INTO newsletter_campaigns (name, subject, content, status)
VALUES ('Weekly Recap', 'Market Update', 'Content here...', 'draft');
```

---

## 📊 **Volume Data System**

### **Volume Analysis**

The `volume_data` table includes:
- **Volume** - Daily trading volume
- **Volume MA 5** - 5-day moving average
- **Volume MA 20** - 20-day moving average
- **Volume Ratio** - Current volume / 20-day average
- **Volume Alert** - Flag for unusual volume

### **Volume Alerts**

```sql
-- Check for volume alerts
SELECT * FROM volume_alerts 
WHERE is_triggered = TRUE 
ORDER BY triggered_at DESC;
```

### **Volume Analytics**

```sql
-- Get volume summary
SELECT 
    ticker,
    AVG(volume) as avg_volume,
    MAX(volume) as max_volume,
    COUNT(*) as days_with_data
FROM volume_data 
GROUP BY ticker;
```

---

## 🎯 **Paper Trading System**

### **Account Management**

```sql
-- Create paper trading account
INSERT INTO paper_trading_accounts (user_id, account_name, initial_balance)
VALUES (auth.uid(), 'My Trading Account', 100000.00);
```

### **Position Tracking**

```sql
-- View current positions
SELECT 
    p.ticker,
    p.quantity,
    p.avg_cost,
    p.current_value,
    p.unrealized_pnl
FROM paper_trading_positions p
JOIN paper_trading_accounts a ON p.account_id = a.id
WHERE a.user_id = auth.uid();
```

---

## 🗳️ **Sentiment Voting System**

### **Voting**

```sql
-- Add sentiment vote
INSERT INTO sentiment_votes (user_id, ticker, sentiment, confidence_level)
VALUES (auth.uid(), 'ATW', 'bullish', 4);
```

### **Sentiment Analysis**

```sql
-- Get sentiment summary
SELECT 
    ticker,
    sentiment,
    COUNT(*) as vote_count,
    AVG(confidence_level) as avg_confidence
FROM sentiment_votes
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY ticker, sentiment;
```

---

## 🧪 **Testing the Setup**

### **Test Database Connectivity**

```bash
# Run the test script
python3 scripts/setup_supabase_database.py
```

### **Manual Testing**

```sql
-- Test user table
SELECT * FROM users LIMIT 1;

-- Test newsletter subscribers
SELECT * FROM newsletter_subscribers LIMIT 1;

-- Test companies
SELECT * FROM companies LIMIT 5;

-- Test volume data
SELECT * FROM volume_data LIMIT 1;
```

### **Test RLS Policies**

```sql
-- This should only return your own data
SELECT * FROM users WHERE id = auth.uid();

-- This should be empty for other users
SELECT * FROM watchlists;
```

---

## 📈 **Performance Optimization**

### **Indexes**

The schema includes optimized indexes for:
- **Time-series data** (quotes, volume_data)
- **User queries** (watchlists, alerts)
- **Analytics** (sentiment, volume alerts)

### **Compression**

Time-series data is automatically compressed after 7 days to save storage.

### **Retention**

- **Quotes**: 5 years retention
- **Volume data**: 5 years retention
- **User data**: Indefinite retention

---

## 🔧 **Troubleshooting**

### **Common Issues**

**"Table doesn't exist"**
- Check if schema was executed successfully
- Verify table names in Supabase dashboard

**"Permission denied"**
- Check RLS policies are enabled
- Verify user authentication

**"Real-time not working"**
- Check if real-time is enabled in Supabase dashboard
- Verify subscription setup in frontend

### **Reset Database**

```sql
-- Drop all tables (DANGER - will delete all data)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

---

## 📊 **Monitoring & Analytics**

### **Database Health**

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;
```

### **Performance Metrics**

```sql
-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🎯 **Next Steps**

After database setup:

1. **Test the API endpoints** with the new schema
2. **Update frontend** to use new table structures
3. **Configure real-time** subscriptions in your app
4. **Set up monitoring** for database performance
5. **Test RLS policies** with different user roles

---

## 📞 **Support**

### **Useful Commands**

```bash
# Test database setup
python3 scripts/setup_supabase_database.py

# Check environment variables
echo $NEXT_PUBLIC_SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# View schema file
cat database/enhanced_schema_with_rls.sql
```

### **Resources**

- **Supabase Docs**: https://supabase.com/docs
- **RLS Guide**: https://supabase.com/docs/guides/auth/row-level-security
- **Real-time Guide**: https://supabase.com/docs/guides/realtime

---

**🎯 Bottom Line**: Your Supabase database is now ready with comprehensive schema, security, and real-time capabilities for the Casablanca Insights platform!

**Last Updated**: July 2025
**Status**: ✅ **Ready for Production** 