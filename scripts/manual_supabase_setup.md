# Manual Supabase Database Setup Guide

This guide will help you set up your new Supabase database with the complete schema from your old instance.

## 🚀 Quick Setup Steps

### 1. Access Your Supabase Dashboard

1. Go to [https://supabase.com](https://supabase.com)
2. Sign in to your account
3. Select your project: `kszekypwdjqaycpuayda`
4. Navigate to the **SQL Editor**

### 2. Apply the Complete Schema

1. In the SQL Editor, copy and paste the entire content from:
   ```
   database/complete_supabase_schema.sql
   ```

2. Click **Run** to execute the schema

### 3. Verify Tables Were Created

After running the schema, you should see these tables in your **Table Editor**:

#### Core Tables:
- ✅ `companies` - Company information
- ✅ `company_prices` - OHLCV price data
- ✅ `company_reports` - Financial reports
- ✅ `company_news` - News and sentiment data

#### User Features:
- ✅ `profiles` - User profiles and metadata
- ✅ `watchlists` - User watchlists
- ✅ `watchlist_items` - Items in watchlists
- ✅ `price_alerts` - Price alert settings
- ✅ `sentiment_votes` - User sentiment votes
- ✅ `sentiment_aggregates` - Aggregated sentiment data

#### Trading Features:
- ✅ `paper_trading_accounts` - Paper trading accounts
- ✅ `paper_trading_orders` - Trading orders
- ✅ `paper_trading_positions` - Trading positions
- ✅ `portfolios` - User portfolios
- ✅ `portfolio_holdings` - Portfolio holdings

#### Additional Features:
- ✅ `newsletter_subscribers` - Newsletter subscribers
- ✅ `newsletter_campaigns` - Newsletter campaigns
- ✅ `contests` - Trading contests
- ✅ `contest_entries` - Contest entries
- ✅ `contest_prizes` - Contest prizes
- ✅ `contest_notifications` - Contest notifications
- ✅ `ai_summaries` - AI-generated summaries
- ✅ `chat_queries` - Chat query history
- ✅ `user_profiles` - Extended user profiles
- ✅ `cse_companies` - CSE company data
- ✅ `market_data` - Market data

### 4. Enable Row Level Security (RLS)

For each table that contains user data, enable RLS:

1. Go to **Authentication** → **Policies**
2. For each table, click **Enable RLS**
3. Add policies as needed (the schema includes basic policies)

### 5. Test Your Application

1. Visit your deployed application
2. Try to sign up/sign in
3. Test basic features like:
   - User registration
   - Watchlist creation
   - Price alerts
   - Paper trading

## 🔧 Environment Variables

Make sure these are set in your Vercel deployment:

```json
{
  "NEXT_PUBLIC_SUPABASE_URL": "https://kszekypwdjqaycpuayda.supabase.co",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY": "your_anon_key",
  "SUPABASE_SERVICE_ROLE_KEY": "your_service_role_key"
}
```

## 🐛 Troubleshooting

### Common Issues:

1. **"Table doesn't exist" errors**
   - Make sure you ran the complete schema
   - Check that all tables were created

2. **RLS Policy errors**
   - Enable RLS on user tables
   - Add appropriate policies

3. **Authentication errors**
   - Verify your Supabase URL and keys
   - Check that auth is properly configured

### Getting Help:

1. Check the Supabase logs in your dashboard
2. Verify your environment variables
3. Test with a simple query first

## 📊 Verification Checklist

- [ ] All tables created successfully
- [ ] RLS enabled on user tables
- [ ] Environment variables configured
- [ ] Application can connect to database
- [ ] User registration works
- [ ] Basic features functional
- [ ] No console errors

## 🎉 Success!

Once everything is working, your new Supabase instance will have the same functionality as your old one, but with better performance and the latest features. 