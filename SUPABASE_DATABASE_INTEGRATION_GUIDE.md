# 🗄️ Supabase Database Integration Guide for Casablanca Insights

This guide covers the complete database integration setup using **Supabase** instead of local PostgreSQL, which is much more efficient and aligns with the project's architecture.

## 🎯 Why Supabase?

- **Managed PostgreSQL** - No need to install and manage PostgreSQL locally
- **Built-in authentication** - Already configured in the project
- **Real-time subscriptions** - Perfect for financial data updates
- **Row Level Security (RLS)** - Better security for financial data
- **Database backups** - Automatic and reliable
- **API generation** - Auto-generated REST and GraphQL APIs
- **Dashboard** - Built-in admin interface

## 📋 Prerequisites

- ✅ Existing Supabase project (you mentioned you already have this)
- ✅ Supabase credentials configured in environment variables
- ✅ Python virtual environment with Supabase client installed

## 🚀 Step-by-Step Setup

### 1. **Add Financial Data Schema to Supabase**

Run the following SQL in your Supabase SQL Editor:

```sql
-- Copy and paste the contents of apps/backend/database/supabase_financial_schema.sql
```

This will create:
- `cse_companies` - Casablanca Stock Exchange company data
- `financials_raw` - Raw financial data from PDFs
- `financials_gaap` - Clean GAAP financial data
- `label_mappings` - French to GAAP label translations
- `etl_jobs` - ETL job tracking
- `market_data` - Real-time market data
- Proper indexes, triggers, and RLS policies

### 2. **Set Up Environment Variables**

Ensure your `.env` file has the Supabase credentials:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. **Initialize Company Data**

Run the Supabase-compatible initialization script:

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables (if not already set)
export NEXT_PUBLIC_SUPABASE_URL="your_supabase_url"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_supabase_anon_key"

# Run the initialization script
python apps/backend/etl/initialize_supabase_cse.py
```

This script will:
- Scrape company data from CSE website
- Import data into your Supabase project
- Generate backup files (JSON/CSV)
- Provide detailed statistics

### 4. **Set Up Data Refresh Pipeline**

Create a cron job for daily data updates:

```bash
# Add to crontab (run: crontab -e)
0 6 * * * cd /path/to/project && source venv/bin/activate && python apps/backend/etl/supabase_data_refresh.py
```

Or run manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Run data refresh
python apps/backend/etl/supabase_data_refresh.py
```

## 📊 Database Schema Overview

### Core Tables

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `cse_companies` | Company information | Ticker, ISIN, sector, listing date |
| `market_data` | Real-time prices | Price, volume, market cap, 24h changes |
| `financials_raw` | Raw PDF data | JSONB storage, extraction metadata |
| `financials_gaap` | Clean financial data | GAAP-compliant, ratios, AI summaries |
| `etl_jobs` | Job tracking | Status, metadata, error handling |

### Row Level Security (RLS)

- **Public read access** to market data and company information
- **Authenticated users** can access raw financial data
- **Admin users** can manage ETL jobs
- **User-specific data** (watchlists, alerts) protected by user ID

## 🔄 Data Refresh Process

The data refresh pipeline:

1. **Fetches market data** from African Markets
2. **Gets central bank data** from Bank Al-Maghrib
3. **Updates CSE companies** with latest information
4. **Logs ETL jobs** for monitoring
5. **Generates reports** for backup and analysis

## 📈 Real-time Features

### Supabase Real-time Subscriptions

```javascript
// Example: Subscribe to market data updates
const subscription = supabase
  .channel('market_data')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'market_data' },
    (payload) => {
      console.log('New market data:', payload.new)
      // Update UI with real-time data
    }
  )
  .subscribe()
```

### Automatic Updates

- Market data updates trigger real-time notifications
- Company information changes are broadcast to connected clients
- ETL job status updates are available for monitoring

## 🛠️ Scripts Overview

### 1. `initialize_supabase_cse.py`
- **Purpose**: Initial company data import
- **Usage**: One-time setup or data refresh
- **Output**: JSON/CSV backups, database statistics

### 2. `supabase_data_refresh.py`
- **Purpose**: Daily data refresh pipeline
- **Usage**: Automated via cron or manual execution
- **Features**: Multi-source data fetching, error handling, reporting

### 3. `supabase_financial_schema.sql`
- **Purpose**: Database schema setup
- **Usage**: Run once in Supabase SQL Editor
- **Includes**: Tables, indexes, functions, RLS policies

## 🔍 Monitoring and Maintenance

### Check ETL Job Status

```sql
-- View recent ETL jobs
SELECT * FROM etl_jobs 
ORDER BY created_at DESC 
LIMIT 10;
```

### Database Statistics

```sql
-- Get company statistics
SELECT * FROM get_cse_company_stats();

-- Search companies
SELECT * FROM search_cse_companies('ATW');
```

### Real-time Monitoring

- Supabase Dashboard → Logs
- ETL job status in `etl_jobs` table
- Refresh reports in `data/refresh/` directory

## 🚨 Troubleshooting

### Common Issues

1. **"Supabase client not configured"**
   - Check environment variables
   - Verify Supabase URL and key

2. **"Permission denied"**
   - Check RLS policies
   - Verify user authentication

3. **"Connection timeout"**
   - Check network connectivity
   - Verify Supabase project status

### Debug Commands

```bash
# Test Supabase connection
python -c "
from supabase import create_client
import os
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
supabase = create_client(url, key)
print('✅ Supabase connection successful')
"

# Check environment variables
echo "URL: $NEXT_PUBLIC_SUPABASE_URL"
echo "KEY: ${NEXT_PUBLIC_SUPABASE_ANON_KEY:0:20}..."
```

## 📁 File Structure

```
apps/backend/
├── database/
│   └── supabase_financial_schema.sql    # Database schema
├── etl/
│   ├── initialize_supabase_cse.py       # Initial data import
│   └── supabase_data_refresh.py         # Daily refresh pipeline
└── data/
    ├── cse_companies_supabase.json      # Backup files
    ├── cse_companies_supabase.csv
    └── refresh/                         # Refresh reports
        └── refresh_report_*.json
```

## 🎉 Benefits of This Approach

1. **No local database setup** - Everything managed by Supabase
2. **Real-time capabilities** - Instant updates across all clients
3. **Better security** - Row Level Security and authentication
4. **Scalability** - Managed infrastructure handles growth
5. **Monitoring** - Built-in dashboard and logging
6. **Backup** - Automatic database backups
7. **API generation** - Auto-generated REST APIs

## 🔄 Next Steps

1. **Run the schema setup** in your Supabase SQL Editor
2. **Execute the initialization script** to import company data
3. **Set up the cron job** for daily data refresh
4. **Test real-time subscriptions** in your frontend
5. **Monitor ETL jobs** through the dashboard

This approach leverages Supabase's powerful features while maintaining the same functionality as the original PostgreSQL setup, but with much better scalability, security, and ease of management.