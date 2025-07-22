# Coding Guidelines & Data Integration Best Practices

## 🎯 **Core Principles**

### **1. Real Data First**
- **Always prioritize real data** over mock data when available
- **Graceful degradation**: Use mock data only as fallback when real data is unavailable
- **Data freshness**: Ensure data is updated regularly through automated processes
- **Source tracking**: Always maintain metadata about data sources and last update times

### **2. Data Integrity & Quality**
- **Validation**: Validate all incoming data for completeness and accuracy
- **Error handling**: Implement robust error handling for data fetching failures
- **Backup systems**: Maintain fallback data sources and mock data for critical features
- **Monitoring**: Track data quality metrics and alert on anomalies

### **3. Performance & Scalability**
- **Caching**: Implement intelligent caching strategies for frequently accessed data
- **Lazy loading**: Load data only when needed
- **Pagination**: Handle large datasets efficiently
- **Optimization**: Minimize API calls and database queries

## 📊 **78 Companies Database Management**

### **Data Sources Priority**
1. **Primary**: African Markets API (real-time when available)
2. **Secondary**: Supabase database (cached real data)
3. **Tertiary**: Local JSON files (backup/fallback)
4. **Fallback**: Mock data (development/testing only)

### **Database Schema Standards**
```sql
-- Companies table structure
CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  sector VARCHAR(100),
  subsector VARCHAR(100),
  market_cap_billion DECIMAL(10,2),
  price DECIMAL(10,2),
  change_1d_percent DECIMAL(5,2),
  change_ytd_percent DECIMAL(5,2),
  volume BIGINT,
  pe_ratio DECIMAL(8,2),
  dividend_yield DECIMAL(5,2),
  beta DECIMAL(5,2),
  size_category VARCHAR(20),
  sector_group VARCHAR(100),
  listing_date DATE,
  isin VARCHAR(20),
  source_url TEXT,
  data_source VARCHAR(50),
  last_updated TIMESTAMP DEFAULT NOW(),
  scraped_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);

-- Data refresh tracking
CREATE TABLE data_refresh_log (
  id SERIAL PRIMARY KEY,
  source_name VARCHAR(50) NOT NULL,
  refresh_type VARCHAR(20) NOT NULL, -- 'full', 'incremental', 'manual'
  records_processed INTEGER,
  records_updated INTEGER,
  records_added INTEGER,
  records_failed INTEGER,
  start_time TIMESTAMP DEFAULT NOW(),
  end_time TIMESTAMP,
  status VARCHAR(20), -- 'success', 'partial', 'failed'
  error_message TEXT,
  metadata JSONB
);
```

### **Data Refresh Workflow**
```python
# Example Airflow DAG for daily data refresh
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'cse_companies_daily_refresh',
    default_args=default_args,
    description='Daily refresh of CSE companies data',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False
)

def refresh_african_markets_data():
    """Refresh data from African Markets API"""
    # Implementation here
    pass

def refresh_supabase_cache():
    """Update Supabase with latest data"""
    # Implementation here
    pass

def validate_data_quality():
    """Validate data quality and alert on issues"""
    # Implementation here
    pass

# Task definitions
refresh_task = PythonOperator(
    task_id='refresh_african_markets',
    python_callable=refresh_african_markets_data,
    dag=dag
)

cache_task = PythonOperator(
    task_id='update_supabase_cache',
    python_callable=refresh_supabase_cache,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag
)

refresh_task >> cache_task >> validate_task
```

## 🔄 **Airflow Data Refresh Strategy**

### **Daily Refresh Schedule**
```yaml
# airflow/dags/cse_data_refresh_dag.py
schedule_intervals:
  - name: "cse_companies_daily"
    schedule: "0 6 * * *"  # 6 AM daily
    description: "Full refresh of CSE companies data"
    
  - name: "market_data_hourly"
    schedule: "0 * * * *"  # Every hour
    description: "Hourly market data updates"
    
  - name: "data_quality_check"
    schedule: "0 8 * * *"  # 8 AM daily
    description: "Daily data quality validation"
    
  - name: "backup_cleanup"
    schedule: "0 2 * * 0"  # 2 AM Sundays
    description: "Weekly backup and cleanup"
```

### **Data Quality Monitoring**
```python
def validate_data_quality():
    """Validate data quality metrics"""
    quality_checks = {
        'completeness': check_data_completeness(),
        'accuracy': check_data_accuracy(),
        'freshness': check_data_freshness(),
        'consistency': check_data_consistency()
    }
    
    # Alert if quality drops below thresholds
    for metric, score in quality_checks.items():
        if score < 0.8:  # 80% threshold
            send_alert(f"Data quality issue: {metric} = {score}")
    
    return quality_checks
```

## 🏗️ **Code Architecture Guidelines**

### **Service Layer Pattern**
```typescript
// lib/services/marketDataService.ts
export class MarketDataService {
  private cache: Map<string, any> = new Map()
  private cacheTTL: number = 5 * 60 * 1000 // 5 minutes

  async getCompanyData(ticker: string): Promise<CompanyData> {
    // 1. Check cache first
    const cached = this.getFromCache(ticker)
    if (cached) return cached

    // 2. Try real data sources in order
    try {
      const data = await this.fetchFromSupabase(ticker)
      if (data) {
        this.setCache(ticker, data)
        return data
      }
    } catch (error) {
      console.warn(`Supabase fetch failed for ${ticker}:`, error)
    }

    try {
      const data = await this.fetchFromAfricanMarkets(ticker)
      if (data) {
        this.setCache(ticker, data)
        return data
      }
    } catch (error) {
      console.warn(`African Markets fetch failed for ${ticker}:`, error)
    }

    // 3. Fallback to mock data
    console.warn(`Using mock data for ${ticker}`)
    return this.getMockData(ticker)
  }

  private getFromCache(key: string): any | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      return cached.data
    }
    return null
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }
}
```

### **API Route Standards**
```typescript
// pages/api/market-data/[ticker].ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { marketDataService } from '@/lib/services/marketDataService'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { ticker } = req.query

  if (!ticker || typeof ticker !== 'string') {
    return res.status(400).json({ error: 'Ticker parameter required' })
  }

  try {
    const data = await marketDataService.getCompanyData(ticker.toUpperCase())
    
    // Add metadata about data source
    const response = {
      data,
      metadata: {
        source: data.source || 'unknown',
        lastUpdated: data.lastUpdated || new Date().toISOString(),
        cacheStatus: data.fromCache ? 'cached' : 'fresh',
        dataQuality: data.quality || 'unknown'
      }
    }

    return res.status(200).json(response)
  } catch (error) {
    console.error(`Error fetching data for ${ticker}:`, error)
    return res.status(500).json({ 
      error: 'Failed to fetch market data',
      fallback: true 
    })
  }
}
```

## 📁 **File Organization Standards**

### **Data Files Structure**
```
apps/
├── backend/
│   ├── data/
│   │   ├── current/                    # Latest data
│   │   │   ├── cse_companies.json
│   │   │   ├── market_data.json
│   │   │   └── bonds_data.json
│   │   ├── historical/                 # Historical data
│   │   │   ├── 2025/
│   │   │   ├── 2024/
│   │   │   └── ...
│   │   ├── backup/                     # Backup data
│   │   │   └── last_known_good/
│   │   └── scrapers/                   # Legacy scrapers
│   │       ├── african_markets_scraper.py
│   │       ├── wafabourse_scraper.py
│   │       └── bank_al_maghrib_scraper.py
│   └── etl/
│       ├── data_refresh.py
│       ├── quality_validation.py
│       └── backup_management.py
└── web/
    ├── lib/
    │   ├── services/                   # Service layer
    │   │   ├── marketDataService.ts
    │   │   ├── portfolioService.ts
    │   │   └── userService.ts
    │   ├── utils/                      # Utility functions
    │   │   ├── dataValidation.ts
    │   │   ├── cacheManagement.ts
    │   │   └── errorHandling.ts
    │   └── types/                      # TypeScript types
    │       ├── marketData.ts
    │       ├── company.ts
    │       └── api.ts
    └── pages/
        └── api/
            ├── market-data/
            │   ├── [ticker].ts
            │   ├── companies.ts
            │   └── summary.ts
            └── health/
                └── data-quality.ts
```

## 🔧 **Development Best Practices**

### **1. Data Source Priority Chain**
```typescript
// Always follow this priority order
const DATA_SOURCE_PRIORITY = [
  'supabase_live',      // Real-time from Supabase
  'supabase_cached',    // Cached data from Supabase
  'african_markets',    // Direct API call
  'local_backup',       // Local JSON backup
  'mock_data'           // Development fallback
] as const

async function getDataWithFallback(ticker: string) {
  for (const source of DATA_SOURCE_PRIORITY) {
    try {
      const data = await fetchFromSource(source, ticker)
      if (data && isDataValid(data)) {
        return { data, source }
      }
    } catch (error) {
      console.warn(`Failed to fetch from ${source}:`, error)
      continue
    }
  }
  throw new Error('All data sources failed')
}
```

### **2. Error Handling Standards**
```typescript
// lib/utils/errorHandling.ts
export class DataFetchError extends Error {
  constructor(
    message: string,
    public source: string,
    public fallbackUsed: boolean = false
  ) {
    super(message)
    this.name = 'DataFetchError'
  }
}

export function handleDataError(error: any, context: string) {
  // Log error with context
  console.error(`Data error in ${context}:`, error)
  
  // Send to monitoring service
  if (process.env.NODE_ENV === 'production') {
    // Send to Sentry, DataDog, etc.
  }
  
  // Return graceful fallback
  return {
    error: true,
    message: 'Data temporarily unavailable',
    fallback: true,
    timestamp: new Date().toISOString()
  }
}
```

### **3. Data Validation**
```typescript
// lib/utils/dataValidation.ts
export interface DataQualityMetrics {
  completeness: number
  accuracy: number
  freshness: number
  consistency: number
}

export function validateCompanyData(data: any): DataQualityMetrics {
  const requiredFields = ['ticker', 'name', 'price', 'sector']
  const presentFields = requiredFields.filter(field => data[field] !== undefined)
  
  return {
    completeness: presentFields.length / requiredFields.length,
    accuracy: validatePriceAccuracy(data.price),
    freshness: validateDataFreshness(data.lastUpdated),
    consistency: validateDataConsistency(data)
  }
}

function validatePriceAccuracy(price: number): number {
  if (typeof price !== 'number' || price <= 0) return 0
  if (price > 10000) return 0.5 // Suspiciously high
  return 1.0
}
```

## 🚀 **Deployment & Monitoring**

### **Health Check Endpoints**
```typescript
// pages/api/health/data-quality.ts
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const qualityMetrics = await getDataQualityMetrics()
  
  const isHealthy = qualityMetrics.overall > 0.8
  
  res.status(isHealthy ? 200 : 503).json({
    status: isHealthy ? 'healthy' : 'degraded',
    metrics: qualityMetrics,
    timestamp: new Date().toISOString()
  })
}
```

### **Monitoring Alerts**
```yaml
# monitoring/alerts.yml
alerts:
  - name: "data_freshness_alert"
    condition: "data_last_updated > 24h"
    severity: "warning"
    
  - name: "data_quality_alert"
    condition: "data_quality_score < 0.8"
    severity: "critical"
    
  - name: "api_failure_alert"
    condition: "api_error_rate > 0.1"
    severity: "critical"
```

## 📋 **Legacy Code Management**

### **Scraper Preservation Strategy**
```python
# etl/legacy_scrapers/README.md
"""
Legacy Scrapers - Preserved for Emergency Use

These scrapers are kept for emergency data recovery or when primary sources fail.
They should be updated periodically to ensure they still work.

Usage:
    python -m etl.legacy_scrapers.african_markets_scraper --emergency
    python -m etl.legacy_scrapers.wafabourse_scraper --backup-only

Maintenance:
    - Test monthly to ensure they still work
    - Update selectors if websites change
    - Keep dependencies updated
    - Document any changes needed
"""
```

### **Migration Checklist**
- [ ] **Identify critical scrapers** that must be preserved
- [ ] **Document dependencies** and requirements
- [ ] **Create test scripts** to verify functionality
- [ ] **Set up monitoring** to detect when scrapers break
- [ ] **Plan migration path** to newer data sources
- [ ] **Maintain backup data** from legacy sources

## 🎯 **Implementation Checklist**

### **Immediate Actions**
- [ ] **Set up Airflow DAGs** for daily data refresh
- [ ] **Implement service layer** with fallback chain
- [ ] **Add data quality monitoring** and alerts
- [ ] **Create health check endpoints** for monitoring
- [ ] **Document all data sources** and their reliability

### **Short-term Goals**
- [ ] **Migrate to real data** for all 78 companies
- [ ] **Implement intelligent caching** strategy
- [ ] **Add data validation** at all entry points
- [ ] **Set up automated testing** for data pipelines
- [ ] **Create data lineage tracking**

### **Long-term Vision**
- [ ] **Real-time data feeds** where possible
- [ ] **Advanced analytics** and insights
- [ ] **Machine learning** for data quality improvement
- [ ] **Multi-source data fusion** for better accuracy
- [ ] **Predictive analytics** for market trends

## 💡 **Key Takeaways**

1. **Always prioritize real data** but have robust fallbacks
2. **Automate everything** - manual data updates are error-prone
3. **Monitor data quality** continuously
4. **Keep legacy code** but maintain it properly
5. **Document everything** - data sources, schemas, processes
6. **Test regularly** - both automated and manual testing
7. **Plan for failure** - multiple data sources and backup strategies

This comprehensive approach ensures we maintain high-quality, reliable data while being prepared for any source failures or changes. 