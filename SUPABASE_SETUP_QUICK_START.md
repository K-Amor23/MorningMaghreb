# 🚀 Supabase Database Setup - Quick Start

## ✅ **Connection Test Results**

Great news! Your Supabase connection is working perfectly:
- ✅ Supabase URL: Configured
- ✅ Service Role Key: Configured  
- ✅ Connection: Successful
- ✅ Newsletter subscribers table: Already exists

## 🎯 **Next Step: Set Up Database Schema**

Since the connection is working, you need to manually set up the database schema in the Supabase dashboard.

### **Step 1: Access Supabase Dashboard**

1. Go to [supabase.com](https://supabase.com)
2. Open your **Casablanca Insights** project
3. Navigate to **SQL Editor** in the left sidebar

### **Step 2: Execute the Schema**

1. **Open SQL Editor**
2. **Copy the entire content** from `database/enhanced_schema_with_rls.sql`
3. **Paste it** into the SQL Editor
4. **Click "Run"** to execute

### **Step 3: Verify Tables Created**

After running the schema, you should see these tables in the **Table Editor**:

**Core Tables:**
- ✅ `users` - User profiles
- ✅ `user_profiles` - Extended user data  
- ✅ `companies` - Company information
- ✅ `quotes` - Market quotes
- ✅ `volume_data` - Volume analysis

**Newsletter Tables:**
- ✅ `newsletter_subscribers` - Already exists
- ✅ `newsletter_campaigns` - Email campaigns
- ✅ `newsletter_campaign_recipients` - Campaign tracking
- ✅ `newsletter_templates` - Email templates

**Trading Tables:**
- ✅ `watchlists` - User watchlists
- ✅ `watchlist_items` - Watchlist stocks
- ✅ `price_alerts` - Price alerts
- ✅ `paper_trading_accounts` - Paper trading
- ✅ `paper_trading_positions` - Trading positions

**Analytics Tables:**
- ✅ `sentiment_votes` - User sentiment
- ✅ `volume_alerts` - Volume alerts

### **Step 4: Test the Setup**

After setting up the schema, run this test:

```bash
python3 scripts/test_supabase_connection.py
```

You should now see all tables as accessible instead of "not found" warnings.

## 🔒 **RLS Policies**

The schema automatically sets up Row Level Security policies that ensure:
- Users can only access their own data
- Watchlists are private
- Paper trading accounts are isolated
- Price alerts are user-specific

## 📡 **Real-time Subscriptions**

Real-time is enabled for:
- `quotes` - Live market data
- `volume_data` - Volume updates  
- `volume_alerts` - Volume alerts
- `sentiment_votes` - Sentiment changes
- `price_alerts` - Price alerts

## 🎯 **What You Get**

After setup, your database will have:

1. **Complete user management** with authentication
2. **Newsletter system** for email campaigns
3. **Volume data tracking** with alerts
4. **Paper trading system** for simulation
5. **Sentiment voting** for community insights
6. **Watchlists** for tracking stocks
7. **Price alerts** for notifications
8. **Real-time updates** for live data

## 🚨 **Troubleshooting**

**If you get errors:**

1. **"Extension not found"** - Enable TimescaleDB in Supabase dashboard
2. **"Permission denied"** - Check if you're using the service role key
3. **"Table already exists"** - Drop existing tables first if needed

**To reset everything:**

```sql
-- DANGER: This deletes all data
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

## 📞 **Need Help?**

1. **Check the full guide**: `SUPABASE_DATABASE_SETUP_GUIDE.md`
2. **View the schema file**: `database/enhanced_schema_with_rls.sql`
3. **Run tests**: `python3 scripts/test_supabase_connection.py`

---

**🎯 Bottom Line**: Your Supabase connection is working! Just copy and paste the schema into the SQL Editor to complete the setup.

**Status**: 🔄 **Ready for Schema Setup** 