# 🚀 Master Schema Migration Guide for Casablanca Insights

This guide will help you migrate your complete database schema to your new Supabase instance.

## 📋 **What's Included in the Master Schema**

The `database/MASTER_SCHEMA_MIGRATION.sql` file contains **everything** you need:

### **🏢 Core Business Tables (25+ tables)**
- **Companies & Market Data**: `companies`, `company_prices`, `company_reports`, `company_news`
- **User Management**: `profiles`, `user_profiles`, authentication integration
- **Trading Features**: `watchlists`, `price_alerts`, `paper_trading_accounts`
- **Analytics**: `sentiment_votes`, `sentiment_aggregates`, `ai_summaries`
- **Advanced Features**: `etfs`, `bonds`, `contests`, `newsletter_management`
- **Portfolio Management**: `portfolios`, `portfolio_holdings`

### **🔧 Technical Infrastructure**
- **50+ Performance Indexes** for optimal query speed
- **Row Level Security (RLS)** policies for data protection
- **Triggers & Functions** for automated data management
- **Views** for analytics and reporting
- **Complete Permissions** setup

## 🎯 **Quick Migration Steps**

### **Step 1: Access Your Supabase Dashboard**
1. Go to [https://supabase.com](https://supabase.com)
2. Sign in to your account
3. Select your project: `supabase-sky-garden`
4. Navigate to **SQL Editor**

### **Step 2: Run the Master Migration**
1. Copy the entire content from `database/MASTER_SCHEMA_MIGRATION.sql`
2. Paste it into the SQL Editor
3. Click **Run** to execute the complete schema

### **Step 3: Verify the Migration**
After running the migration, you should see:
- ✅ **Success message**: "Master schema migration completed successfully!"
- ✅ **All tables created** in the Table Editor
- ✅ **All indexes created** for performance
- ✅ **All functions and triggers** working

## 📊 **Database Structure Overview**

### **Core Tables (Essential)**
```sql
-- Company data
companies              -- Master company information
company_prices         -- OHLCV price data
company_reports        -- Financial reports
company_news           -- News and sentiment

-- User management
profiles               -- User profiles (extends auth.users)
user_profiles          -- Extended user data

-- Trading features
watchlists             -- User watchlists
watchlist_items        -- Watchlist contents
price_alerts           -- Price alert system
paper_trading_accounts -- Paper trading accounts
paper_trading_orders   -- Trading orders
paper_trading_positions -- Current positions

-- Analytics
sentiment_votes        -- User sentiment votes
sentiment_aggregates   -- Aggregated sentiment data
ai_summaries           -- AI-generated summaries
chat_queries           -- Chat system queries
```

### **Advanced Features**
```sql
-- Portfolio management
portfolios             -- User portfolios
portfolio_holdings     -- Portfolio contents

-- Contest system
contests               -- Trading contests
contest_entries        -- Contest participants
contest_prizes         -- Contest prizes
contest_notifications  -- Contest notifications

-- Newsletter system
newsletter_subscribers -- Email subscribers
newsletter_campaigns   -- Email campaigns

-- ETFs & Bonds
etfs                   -- ETF information
etf_data              -- ETF price data
bonds                  -- Bond information
bond_data             -- Bond price data

-- Market data
cse_companies         -- CSE company list
market_data           -- Real-time market data
```

## 🔐 **Security Features**

### **Row Level Security (RLS)**
- ✅ **User data protection**: Users can only access their own data
- ✅ **Public data access**: Market data is publicly readable
- ✅ **Admin controls**: Proper permission management

### **Authentication Integration**
- ✅ **Supabase Auth**: Seamless integration with auth.users
- ✅ **Automatic profile creation**: Profiles created on user signup
- ✅ **Session management**: Proper session handling

## 📈 **Performance Optimizations**

### **Indexes Created (50+)**
- **Company data**: `ticker`, `sector`, `date` indexes
- **User data**: `email`, `tier`, `status` indexes
- **Trading data**: `user_id`, `ticker`, `status` indexes
- **Analytics**: `sentiment`, `timestamp` indexes

### **Views for Analytics**
- `latest_market_data` - Latest prices for all tickers
- `sentiment_summary` - Aggregated sentiment data
- `portfolio_performance` - Portfolio performance calculations

## 🛠 **Functions & Triggers**

### **Automated Functions**
- `update_updated_at_column()` - Auto-updates timestamps
- `update_sentiment_aggregate()` - Real-time sentiment aggregation
- `handle_new_user()` - Automatic profile creation
- `ensure_single_default_watchlist()` - Watchlist management

### **Triggers**
- **Sentiment aggregation**: Real-time sentiment updates
- **User creation**: Automatic profile setup
- **Watchlist management**: Default watchlist handling
- **Timestamp updates**: Automatic updated_at maintenance

## 🔄 **Migration Verification Checklist**

After running the migration, verify these items:

### **✅ Core Tables (Check in Table Editor)**
- [ ] `companies` - Company master data
- [ ] `company_prices` - Price history
- [ ] `company_reports` - Financial reports
- [ ] `company_news` - News and sentiment
- [ ] `profiles` - User profiles
- [ ] `watchlists` - User watchlists
- [ ] `paper_trading_accounts` - Paper trading
- [ ] `sentiment_votes` - Sentiment system
- [ ] `contests` - Contest system
- [ ] `etfs` - ETF data
- [ ] `bonds` - Bond data

### **✅ Advanced Features**
- [ ] `portfolios` - Portfolio management
- [ ] `newsletter_subscribers` - Email system
- [ ] `ai_summaries` - AI features
- [ ] `chat_queries` - Chat system

### **✅ Technical Infrastructure**
- [ ] All indexes created (50+ indexes)
- [ ] RLS policies enabled
- [ ] Functions created (4+ functions)
- [ ] Triggers active (10+ triggers)
- [ ] Views created (3+ views)
- [ ] Permissions granted

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue: "Extension not available"**
```
NOTICE: TimescaleDB extension not available, using standard PostgreSQL
```
**Solution**: This is normal - TimescaleDB is optional. Your database will work fine without it.

#### **Issue: "Policy already exists"**
```
ERROR: policy "Users can view own profile" already exists
```
**Solution**: This is expected if you've run migrations before. The `CREATE POLICY IF NOT EXISTS` handles this.

#### **Issue: "Function already exists"**
```
ERROR: function update_updated_at_column() already exists
```
**Solution**: This is normal - functions are replaced with `CREATE OR REPLACE`.

### **Verification Commands**
Run these in SQL Editor to verify the migration:

```sql
-- Check table count
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Check index count
SELECT COUNT(*) as index_count FROM pg_indexes 
WHERE schemaname = 'public';

-- Check function count
SELECT COUNT(*) as function_count FROM pg_proc 
WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
```

## 🎉 **Post-Migration Steps**

### **1. Test Core Functionality**
- [ ] User registration works
- [ ] Watchlist creation works
- [ ] Price alerts work
- [ ] Paper trading works
- [ ] Sentiment voting works

### **2. Import Your Data**
- [ ] Import company data to `companies` table
- [ ] Import price data to `company_prices` table
- [ ] Import news data to `company_news` table
- [ ] Import reports data to `company_reports` table

### **3. Configure Environment Variables**
Ensure your app has the correct Supabase credentials:
```env
NEXT_PUBLIC_SUPABASE_URL=https://supabase-sky-garden.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 📞 **Support**

If you encounter any issues:

1. **Check the logs**: Look for error messages in the SQL Editor
2. **Verify permissions**: Ensure your Supabase project has the right permissions
3. **Contact support**: Use the Supabase support if needed

## 🎯 **Success Indicators**

You'll know the migration was successful when you see:
- ✅ **Success message**: "Master schema migration completed successfully!"
- ✅ **All tables visible** in the Table Editor
- ✅ **No error messages** in the SQL Editor
- ✅ **Your app connects** to the database successfully

---

**🎉 Congratulations!** Your Casablanca Insights database is now fully migrated and ready for production use. 