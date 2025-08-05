# 🗄️ Manual Database Setup Guide for Morning Maghreb

## 📋 **Current Status**

The new Supabase database (`skygarden`) needs to have the complete schema set up manually. The automated script failed because the `exec_sql` function doesn't exist in the new database.

## 🔧 **Manual Setup Steps**

### **Step 1: Access Supabase Dashboard**

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Sign in to your account
3. Select the **skygarden** project (the new database)

### **Step 2: Open SQL Editor**

1. In the left sidebar, click on **"SQL Editor"**
2. Click **"New Query"** to create a new SQL query

### **Step 3: Copy and Paste Schema**

1. Open the file `database/complete_supabase_schema.sql` in your project
2. Copy the **entire contents** of the file
3. Paste it into the Supabase SQL Editor
4. Click **"Run"** to execute the schema

### **Step 4: Verify Setup**

After running the schema, you should see these tables created:

#### **Core Tables**
- ✅ `profiles` - User profiles and authentication
- ✅ `companies` - Company data
- ✅ `company_prices` - OHLCV data
- ✅ `company_reports` - Financial reports
- ✅ `company_news` - News and sentiment

#### **User Features**
- ✅ `watchlists` - User watchlists
- ✅ `watchlist_items` - Watchlist items
- ✅ `price_alerts` - Price alerts
- ✅ `sentiment_votes` - User sentiment votes
- ✅ `newsletter_subscribers` - Newsletter subscriptions
- ✅ `contests` - Trading contests
- ✅ `paper_trading_accounts` - Paper trading
- ✅ `portfolios` - User portfolios

#### **Additional Tables**
- ✅ `ai_summaries` - AI-generated summaries
- ✅ `chat_queries` - Chat history
- ✅ `cse_companies` - CSE company data
- ✅ `market_data` - Market data

## 🔍 **Verification Commands**

After setting up the schema, you can verify it's working by running:

```bash
# Test the database connection
python3 scripts/test_comprehensive_collection.sh

# Test live ticker orchestrator
python3 scripts/live_ticker_orchestrator.py test
```

## 🚀 **What This Enables**

Once the schema is set up, your Morning Maghreb application will have:

### **User Authentication & Profiles**
- ✅ User signup/login through Supabase Auth
- ✅ User profiles with tier management (free/pro/admin)
- ✅ Stripe integration for subscriptions
- ✅ User preferences and settings

### **Market Data**
- ✅ Real-time ticker data from multiple sources
- ✅ Historical price data (OHLCV)
- ✅ Company information and financial data
- ✅ News and sentiment analysis

### **User Features**
- ✅ Watchlists and portfolio tracking
- ✅ Price alerts and notifications
- ✅ Paper trading simulation
- ✅ Trading contests and leaderboards
- ✅ Newsletter subscriptions
- ✅ AI-powered summaries and chat

### **Admin Features**
- ✅ User management
- ✅ Content moderation
- ✅ Analytics and reporting
- ✅ Newsletter campaign management

## 📊 **Database Schema Overview**

The complete schema includes:

### **Authentication Tables**
- `auth.users` (managed by Supabase)
- `profiles` (user metadata and preferences)

### **Market Data Tables**
- `companies` (company information)
- `company_prices` (historical prices)
- `company_reports` (financial reports)
- `company_news` (news and sentiment)
- `market_data` (market summaries)

### **User Feature Tables**
- `watchlists` & `watchlist_items`
- `price_alerts`
- `sentiment_votes` & `sentiment_aggregates`
- `paper_trading_accounts`, `paper_trading_orders`, `paper_trading_positions`
- `portfolios` & `portfolio_holdings`
- `contests`, `contest_entries`, `contest_prizes`

### **Content Tables**
- `newsletter_subscribers` & `newsletter_campaigns`
- `ai_summaries`
- `chat_queries`

## 🔐 **Row Level Security (RLS)**

The schema includes RLS policies for:
- User data protection
- Public market data access
- Private user data isolation
- Admin-only content management

## 🎯 **Next Steps After Schema Setup**

1. **Test the application** - Verify signup/login works
2. **Populate with data** - Run the comprehensive data collection
3. **Configure live tickers** - Set up the real-time orchestrator
4. **Test Stripe integration** - Verify payment processing
5. **Deploy to production** - Ensure Vercel deployment works

## ⚠️ **Important Notes**

- The schema setup is a **one-time process**
- All user data will be stored in the new database
- The old database can be kept as backup
- Make sure to update all environment variables to point to the new database

## 🆘 **If You Need Help**

If you encounter any issues during the manual setup:

1. **Check the SQL syntax** - Make sure all statements end with semicolons
2. **Verify permissions** - Ensure you have admin access to the Supabase project
3. **Check for errors** - Look for any error messages in the SQL Editor
4. **Contact support** - If needed, reach out to Supabase support

Once the schema is set up, your Morning Maghreb application will be fully functional with user authentication, real-time data, and all premium features! 🚀 