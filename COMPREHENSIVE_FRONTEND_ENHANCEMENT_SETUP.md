# Comprehensive Frontend Enhancement Setup Guide

This guide will walk you through setting up the complete enhanced frontend system that matches the quality and functionality of [African Markets](https://www.african-markets.com/en/stock-markets/bvc), including interactive charts, comprehensive market data, news, dividends, earnings, and real-time market status.

## 🎯 What We're Building

Your enhanced frontend will include:

- **Interactive Trading Charts** with TradingView integration
- **Comprehensive Market Data** with 52-week ranges and volume analysis
- **Company News & Announcements** with sentiment analysis
- **Dividend Tracking** and payment schedules
- **Earnings Calendar** with estimates and surprises
- **ETF Data** and performance tracking
- **Real-time Market Status** with trading hours
- **Sector Performance** analysis
- **Corporate Actions** tracking

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer      │    │   Database      │
│   Components    │◄──►│   Endpoints      │◄──►│   (Supabase)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Hooks   │    │   Airflow DAGs   │    │   Time-series   │
│   (SWR)         │    │   (ETL)          │    │   Tables        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- ✅ Supabase project with service role key
- ✅ Airflow instance running
- ✅ Python 3.8+ with required packages
- ✅ Node.js 16+ for frontend development

## 🚀 Step-by-Step Setup

### 1. Database Schema Setup

First, set up the comprehensive database schema:

```bash
# Navigate to the scripts directory
cd scripts/setup

# Run the comprehensive database setup
python setup_comprehensive_database.py \
  --supabase-url "YOUR_SUPABASE_URL" \
  --supabase-key "YOUR_SERVICE_ROLE_KEY"
```

This will create:
- `market_status` - Real-time market status
- `comprehensive_market_data` - Complete market data with 52-week ranges
- `company_news` - News and announcements
- `dividend_announcements` - Dividend tracking
- `earnings_announcements` - Earnings calendar
- `etf_data` - ETF information
- `corporate_actions` - Corporate events
- `market_sentiment` - Sentiment analysis

### 2. Deploy the Comprehensive Scraper

Copy the new scraper to your Airflow DAGs directory:

```bash
# Copy the comprehensive scraper
cp apps/backend/etl/comprehensive_market_scraper.py \
   /opt/airflow/dags/etl/

# Copy the Airflow DAG
cp apps/backend/airflow/dags/comprehensive_market_data_dag.py \
   /opt/airflow/dags/
```

### 3. Deploy Frontend Components

Copy the new frontend components:

```bash
# Enhanced trading chart
cp apps/web/components/charts/EnhancedTradingChart.tsx \
   apps/web/components/charts/

# TradingView widget
cp apps/web/components/charts/TradingViewWidget.tsx \
   apps/web/components/charts/

# Company overview component
cp apps/web/components/company/CompanyOverview.tsx \
   apps/web/components/company/

# News and announcements component
cp apps/web/components/company/NewsAndAnnouncements.tsx \
   apps/web/components/company/

# Market status component
cp apps/web/components/market/MarketStatus.tsx \
   apps/web/components/market/
```

### 4. Deploy API Endpoints

Copy the new API endpoint:

```bash
# Comprehensive market data API
cp apps/web/pages/api/market-data/comprehensive.ts \
   apps/web/pages/api/market-data/
```

### 5. Deploy React Hooks

Copy the new React hooks:

```bash
# Comprehensive market data hooks
cp apps/web/hooks/useComprehensiveMarketData.ts \
   apps/web/hooks/
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env.local`:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# TradingView (optional)
NEXT_PUBLIC_TRADINGVIEW_WIDGET_URL=https://s3.tradingview.com/tv.js
```

### Airflow Configuration

Ensure your Airflow instance has:

```python
# In airflow.cfg
[database]
sql_alchemy_conn = postgresql+psycopg2://user:pass@host:port/airflow

[webserver]
web_server_host = 0.0.0.0
web_server_port = 8080

[scheduler]
job_heartbeat_sec = 5
scheduler_heartbeat_sec = 5
```

## 📱 Frontend Integration

### 1. Update Company Page

Replace your existing company page with enhanced components:

```tsx
// pages/company/[ticker].tsx
import { useComprehensiveTickerData } from '@/hooks/useComprehensiveMarketData'
import EnhancedTradingChart from '@/components/charts/EnhancedTradingChart'
import CompanyOverview from '@/components/company/CompanyOverview'
import NewsAndAnnouncements from '@/components/company/NewsAndAnnouncements'

export default function CompanyPage({ ticker }) {
  const { marketData, news, dividends, earnings, isLoading } = 
    useComprehensiveTickerData(ticker)

  return (
    <div className="space-y-6">
      {/* Enhanced Trading Chart */}
      <EnhancedTradingChart 
        ticker={ticker} 
        marketData={marketData} 
      />
      
      {/* Company Overview */}
      <CompanyOverview 
        ticker={ticker}
        marketData={marketData}
      />
      
      {/* News and Announcements */}
      <NewsAndAnnouncements 
        ticker={ticker}
        news={news}
        dividends={dividends}
        earnings={earnings}
      />
    </div>
  )
}
```

### 2. Update Markets Page

Enhance your markets page with real-time status:

```tsx
// pages/markets.tsx
import { useRealTimeMarketStatus } from '@/hooks/useComprehensiveMarketData'
import MarketStatus from '@/components/market/MarketStatus'

export default function MarketsPage() {
  const { marketStatus, topGainers, topLosers, mostActive } = 
    useRealTimeMarketStatus()

  return (
    <div className="space-y-6">
      {/* Market Status */}
      <MarketStatus 
        marketStatus={marketStatus}
        topGainers={topGainers}
        topLosers={topLosers}
        mostActive={mostActive}
      />
      
      {/* Existing market components */}
    </div>
  )
}
```

### 3. Update Home Page

Add market overview to your home page:

```tsx
// pages/index.tsx
import { useComprehensiveMarketOverview } from '@/hooks/useComprehensiveMarketData'

export default function HomePage() {
  const { 
    marketStatus, 
    sectorPerformance, 
    recentNews, 
    upcomingDividends,
    upcomingEarnings 
  } = useComprehensiveMarketOverview()

  return (
    <div className="space-y-6">
      {/* Market Overview */}
      <MarketStatus marketStatus={marketStatus} />
      
      {/* Sector Performance */}
      <SectorPerformance data={sectorPerformance} />
      
      {/* Recent News */}
      <RecentNews news={recentNews} />
      
      {/* Upcoming Events */}
      <UpcomingEvents 
        dividends={upcomingDividends}
        earnings={upcomingEarnings}
      />
    </div>
  )
}
```

## 🔄 Data Flow

### 1. Data Collection (Airflow)

The comprehensive scraper runs daily via Airflow:

```python
# DAG Schedule: Daily at 6:00 AM UTC
dag = DAG(
    'comprehensive_market_data_pipeline',
    schedule_interval='0 6 * * *',
    # ... other config
)
```

**Data Sources:**
- African Markets (primary)
- Wafabourse
- Investing.com
- Yahoo Finance
- Casablanca Bourse

**Data Collected:**
- Market data with 52-week ranges
- Volume analysis
- News and announcements
- Dividend schedules
- Earnings estimates
- ETF information
- Market sentiment

### 2. Data Storage (Supabase)

Data is stored in time-series optimized tables:

```sql
-- Example: Comprehensive market data
CREATE TABLE comprehensive_market_data (
    ticker VARCHAR(10) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    fifty_two_week_high DECIMAL(10,2),
    fifty_two_week_low DECIMAL(10,2),
    volume BIGINT,
    -- ... other fields
    scraped_at TIMESTAMPTZ NOT NULL
);

-- Convert to hypertable for time-series
SELECT create_hypertable('comprehensive_market_data', 'scraped_at');
```

### 3. Data Serving (API)

The comprehensive API serves data efficiently:

```typescript
// GET /api/market-data/comprehensive?ticker=WAA
{
  "ticker": "WAA",
  "market_data": { /* comprehensive market data */ },
  "news": [ /* company news */ ],
  "dividends": [ /* dividend announcements */ ],
  "earnings": [ /* earnings calendar */ ]
}

// GET /api/market-data/comprehensive (market overview)
{
  "market_status": { /* real-time status */ },
  "top_gainers": [ /* top performers */ ],
  "sector_performance": { /* sector analysis */ },
  "recent_news": [ /* market news */ ]
}
```

### 4. Frontend Consumption (React)

React hooks provide real-time data:

```typescript
// Real-time market status
const { marketStatus, timeUntilOpen, timeUntilClose } = 
  useRealTimeMarketStatus()

// Company-specific data
const { marketData, news, dividends, earnings } = 
  useComprehensiveTickerData('WAA')

// Market overview
const { topGainers, sectorPerformance, recentNews } = 
  useComprehensiveMarketOverview()
```

## 📊 Data Quality & Validation

### Validation Rules

The system includes comprehensive validation:

```python
# Data quality checks
def validate_comprehensive_data(data):
    # Check required fields
    required_fields = ['ticker', 'current_price', 'fifty_two_week_high']
    
    # Validate 52-week ranges
    if data['fifty_two_week_high'] <= data['fifty_two_week_low']:
        raise ValueError("Invalid 52-week range")
    
    # Validate price consistency
    if not (data['fifty_two_week_low'] <= data['current_price'] <= data['fifty_two_week_high']):
        raise ValueError("Price outside 52-week range")
```

### Data Freshness

- **Market Data**: Updated every 30 seconds during market hours
- **News**: Updated every 5 minutes
- **Dividends/Earnings**: Updated daily
- **Market Status**: Updated every minute

## 🚨 Monitoring & Alerts

### Airflow Monitoring

The DAG includes comprehensive monitoring:

```python
# Success alerts
def send_comprehensive_success_alert(**context):
    message = f"""
    🚀 **Comprehensive Market Data Pipeline Success**
    
    ✅ **Data Collection:**
       - Companies: {total_companies}
       - News: {total_news}
       - Dividends: {total_dividends}
       - Earnings: {total_earnings}
    
    ✅ **Storage:** {stored_count} items stored
    ✅ **Validation:** {'Passed' if validation_passed else 'Failed'}
    """

# Failure alerts
def send_comprehensive_failure_alert(**context):
    message = f"""
    ❌ **Comprehensive Market Data Pipeline Failed**
    
    🕐 **Failed at:** {execution_date}
    🔍 **Failed task:** {task_instance.task_id}
    📋 **DAG:** {task_instance.dag_id}
    """
```

### Health Checks

Monitor data quality and freshness:

```typescript
// Frontend health check
const checkDataHealth = (data) => {
  const now = new Date()
  const dataAge = now - new Date(data.timestamp)
  
  if (dataAge > 5 * 60 * 1000) { // 5 minutes
    console.warn('Data may be stale')
  }
  
  if (!data.market_data?.current_price) {
    console.error('Missing critical market data')
  }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check Supabase connection
curl -H "apikey: YOUR_KEY" \
     -H "Authorization: Bearer YOUR_KEY" \
     "YOUR_URL/rest/v1/market_status?select=*&limit=1"
```

#### 2. Airflow DAG Failures

```bash
# Check Airflow logs
airflow tasks test comprehensive_market_data_pipeline scrape_comprehensive_market_data 2024-01-01

# Check Python path
echo $PYTHONPATH
# Should include: /opt/airflow/dags/etl
```

#### 3. Frontend Data Loading Issues

```typescript
// Check API responses
const debugAPI = async (url) => {
  try {
    const response = await fetch(url)
    const data = await response.json()
    console.log('API Response:', data)
    return data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}
```

### Performance Optimization

#### 1. Database Indexes

Ensure all indexes are created:

```sql
-- Check existing indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename LIKE '%comprehensive%';

-- Create missing indexes if needed
CREATE INDEX CONCURRENTLY IF NOT EXISTS 
  idx_comprehensive_market_data_ticker_scraped 
ON comprehensive_market_data(ticker, scraped_at);
```

#### 2. Frontend Caching

Optimize SWR configuration:

```typescript
// Optimize refresh intervals
const { data } = useSWR('/api/market-data/comprehensive', fetcher, {
  refreshInterval: 30000, // 30 seconds for market data
  revalidateOnFocus: false, // Reduce unnecessary requests
  revalidateOnReconnect: true, // Refresh on reconnect
})
```

#### 3. API Response Optimization

Use database functions for complex queries:

```sql
-- Use the optimized function
SELECT * FROM get_market_overview();

-- Instead of multiple queries
SELECT * FROM market_status ORDER BY scraped_at DESC LIMIT 1;
SELECT * FROM comprehensive_market_data WHERE ...;
-- etc.
```

## 🎉 What You'll Have

After completing this setup, your frontend will feature:

### ✅ Interactive Charts
- TradingView-powered charts with multiple timeframes
- Volume analysis and technical indicators
- 52-week range visualization
- Price movement tracking

### ✅ Comprehensive Market Data
- Real-time prices with 52-week ranges
- Volume analysis and ratios
- Financial metrics (P/E, ROE, debt ratios)
- Sector performance tracking

### ✅ News & Announcements
- Company-specific news feeds
- Dividend announcements and schedules
- Earnings calendar with estimates
- Corporate action tracking

### ✅ Market Status
- Real-time market open/close status
- Trading hours and countdown timers
- Top gainers/losers tracking
- Most active stocks by volume

### ✅ ETF Tracking
- ETF performance and holdings
- Asset allocation analysis
- Expense ratio comparison
- Benchmark tracking

## 🚀 Next Steps

1. **Test the Setup**: Run a test scrape to verify data collection
2. **Customize Styling**: Adjust component styling to match your design
3. **Add Features**: Implement additional features like watchlists, alerts
4. **Scale Up**: Add more data sources and companies
5. **Monitor Performance**: Track data quality and system performance

## 📞 Support

If you encounter issues:

1. Check the Airflow logs for ETL errors
2. Verify database connections and permissions
3. Test API endpoints individually
4. Check browser console for frontend errors
5. Verify environment variables are set correctly

---

**🎯 Your enhanced frontend is now ready to compete with African Markets!** 

The system provides comprehensive market data, interactive charts, and real-time updates that will give your users a professional trading experience.
