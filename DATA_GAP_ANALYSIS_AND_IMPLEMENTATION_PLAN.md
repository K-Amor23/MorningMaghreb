# Data Gap Analysis and Implementation Plan
## Casablanca Insights - Real Data Integration

### Current State Assessment

#### ✅ What We Already Have
1. **78 Companies Identified** - Complete list from African Markets
   - File: `apps/backend/data/cse_companies_african_markets.json`
   - Contains: ticker, name, sector, price, market cap, etc.
   - Status: ✅ Complete

2. **Basic Company Data** - Core information for all companies
   - Basic financial metrics
   - Sector classification
   - Market cap categories
   - Status: ✅ Complete

3. **Airflow ETL Pipeline** - Framework exists
   - File: `apps/backend/airflow/dags/casablanca_etl_dag.py`
   - Status: ⚠️ Needs enhancement for batching

4. **Comprehensive Scraper** - Company website scraper
   - File: `apps/backend/etl/comprehensive_company_scraper.py`
   - Status: ✅ Ready for production

#### ❌ What We're Missing (Critical Gaps)

### 1. Trading Data (API Challenge - Need Alternative Sources)
**Priority: HIGH - Critical for website functionality**

**❌ CRITICAL FINDING: Yahoo Finance doesn't have Moroccan stock data**
- Tested with `.MA` suffix: All tickers return "No data found, symbol may be delisted"
- This affects our immediate win strategy

**Alternative Data Sources:**
1. **Alpha Vantage API** - Has some international markets
2. **Quandl/NASDAQ Data Link** - International financial data
3. **Bloomberg API** - Professional grade (expensive)
4. **Reuters/Refinitiv** - Professional grade (expensive)
5. **Local Moroccan Data Providers** - BVC direct feeds
6. **Web Scraping** - From Moroccan financial websites

**Immediate Implementation Plan:**
```python
# Option 1: Web scraping from Moroccan financial sites
def scrape_moroccan_trading_data():
    sources = [
        "https://www.bvmt.com.tn/",  # Tunisian exchange (similar region)
        "https://www.casablanca-bourse.com/",  # CSE official site
        "https://www.maghrebsecurities.com/",  # Regional broker
    ]
    # Implement scraping logic

# Option 2: Alpha Vantage API
def fetch_alpha_vantage_data(ticker: str):
    # Use Alpha Vantage for international markets
    pass

# Option 3: Manual data entry with web scraping
def scrape_and_validate_prices():
    # Scrape from multiple sources and validate
    pass
```

**Expected Coverage:** 60-80% (depends on source availability)
**Timeline:** 1-2 weeks (need to research and implement alternatives)

### 2. Financial Reports (PDF Scraping)
**Priority: HIGH - Core value proposition**

**Missing Data:**
- Annual reports (last 3 years)
- Quarterly reports (last 8 quarters)
- Financial statements
- Earnings presentations
- Corporate governance documents

**Current Status:**
- Scraper exists but needs batching
- Need retry logic
- Need incremental updates

**Implementation Plan:**
```python
# Batch processing for 78 companies
BATCH_SIZE = 10
COMPANIES_PER_BATCH = 78 // BATCH_SIZE + (1 if 78 % BATCH_SIZE else 0)

# Process in parallel batches
for batch_num in range(COMPANIES_PER_BATCH):
    start_idx = batch_num * BATCH_SIZE
    end_idx = min((batch_num + 1) * BATCH_SIZE, 78)
    batch_companies = companies[start_idx:end_idx]
    # Process batch
```

**Expected Coverage:** 20-30% initially, growing to 80%+ over time
**Timeline:** 2-4 weeks

### 3. Financial Metrics & Ratios
**Priority: MEDIUM - Derived from reports**

**Missing Data:**
- P/E ratios
- P/B ratios
- ROE, ROA
- Debt ratios
- Growth metrics
- Sector comparisons

**Implementation:**
```python
def compute_financial_ratios(company_data):
    ratios = {
        'pe_ratio': company_data['market_cap'] / company_data['net_income'],
        'pb_ratio': company_data['market_cap'] / company_data['book_value'],
        'roe': company_data['net_income'] / company_data['equity'],
        'roa': company_data['net_income'] / company_data['total_assets']
    }
    return ratios
```

**Expected Coverage:** 60-80% (depends on report availability)
**Timeline:** 1-2 weeks after reports

### 4. News & Sentiment Data
**Priority: MEDIUM - User engagement**

**Missing Data:**
- Company news
- Market sentiment
- Analyst ratings
- Earnings announcements
- Corporate events

**Implementation:**
```python
# News API integration
def fetch_company_news(ticker: str, days: int = 30):
    # Use NewsAPI, Alpha Vantage, or similar
    pass
```

**Expected Coverage:** 70-80%
**Timeline:** 1 week

### 5. Market Data (Real-time)
**Priority: LOW - Nice to have**

**Missing Data:**
- Real-time quotes
- Live trading data
- Market depth
- Order book data

**Implementation:**
```python
# Real-time data feeds
def get_real_time_quotes(tickers: list):
    # Integrate with real-time data providers
    pass
```

**Expected Coverage:** 100% (API-based)
**Timeline:** 2-3 weeks

---

## Revised Implementation Strategy

### Phase 1: Immediate Wins (Week 1) - UPDATED
**Goal: Get website functional with partial data**

#### 1.1 Trading Data Backfill - ALTERNATIVE APPROACH
```bash
# Research and implement alternative data sources
python scripts/research_trading_data_sources.py
```

**Tasks:**
- [ ] Research Moroccan financial data sources
- [ ] Test Alpha Vantage API for international markets
- [ ] Implement web scraping from Moroccan financial sites
- [ ] Create fallback to manual data entry
- [ ] Test with 10 companies first

#### 1.2 Website Partial Data Display
```typescript
// Update company pages to handle missing data
interface CompanyData {
  basic: CompanyBasic; // Always available
  trading?: TradingData; // May be missing - need alternative sources
  reports?: FinancialReport[]; // May be missing
  news?: NewsItem[]; // May be missing
}

// Display logic
{companyData.trading ? (
  <TradingChart data={companyData.trading} />
) : (
  <DataLoadingMessage type="trading" />
)}
```

**Tasks:**
- [ ] Update company page components
- [ ] Add loading states
- [ ] Implement graceful degradation
- [ ] Add data availability indicators

#### 1.3 Enhanced Airflow Batching
```python
# Update existing DAG for batching
from airflow.utils.task_group import TaskGroup

def create_batch_tasks(dag, companies, batch_size=10):
    with TaskGroup(group_id='company_batches', dag=dag) as tg:
        for i in range(0, len(companies), batch_size):
            batch = companies[i:i+batch_size]
            # Create batch task
```

**Tasks:**
- [ ] Refactor existing DAG for batching
- [ ] Add parallel processing
- [ ] Implement retry logic
- [ ] Add progress tracking

### Phase 2: Core Data (Week 2-3)
**Goal: Build comprehensive financial data**

#### 2.1 PDF Report Scraping Enhancement
```python
# Enhanced scraper with batching and retry
class EnhancedCompanyScraper:
    def __init__(self, batch_size=10, max_retries=3):
        self.batch_size = batch_size
        self.max_retries = max_retries
    
    async def scrape_batch(self, companies: List[str]):
        # Process companies in parallel batches
        pass
```

**Tasks:**
- [ ] Enhance existing scraper
- [ ] Add retry mechanisms
- [ ] Implement incremental updates
- [ ] Add progress monitoring
- [ ] Test with first 20 companies

#### 2.2 Financial Data Extraction
```python
# PDF data extraction pipeline
def extract_financial_data(pdf_path: str):
    # Extract tables, charts, metrics
    # Translate French labels to GAAP
    # Validate data quality
    pass
```

**Tasks:**
- [ ] Implement PDF text extraction
- [ ] Add table parsing
- [ ] Create French-to-GAAP mapping
- [ ] Add data validation
- [ ] Store in database

#### 2.3 Database Schema Updates
```sql
-- Add tables for new data types
CREATE TABLE trading_data (
    ticker VARCHAR(10),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE financial_reports (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    report_type VARCHAR(50),
    year INTEGER,
    quarter INTEGER,
    file_path TEXT,
    extracted_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Tasks:**
- [ ] Design new schema
- [ ] Create migration scripts
- [ ] Update models
- [ ] Test data integrity

### Phase 3: Advanced Features (Week 4+)
**Goal: Add sophisticated analytics**

#### 3.1 Financial Ratios & Analytics
```python
# Automated ratio calculation
def calculate_company_ratios(ticker: str):
    # Fetch financial data
    # Calculate ratios
    # Compare to sector averages
    # Generate insights
    pass
```

#### 3.2 News & Sentiment Integration
```python
# News aggregation and sentiment analysis
def aggregate_company_news(ticker: str):
    # Fetch from multiple sources
    # Analyze sentiment
    # Extract key events
    # Store in database
    pass
```

#### 3.3 Real-time Data Feeds
```python
# Real-time market data
def setup_real_time_feeds():
    # WebSocket connections
    # Data streaming
    # Real-time updates
    pass
```

---

## Alternative Trading Data Sources Research

### 1. Alpha Vantage API
```python
# Test Alpha Vantage for international markets
import requests

def test_alpha_vantage():
    api_key = "YOUR_API_KEY"
    base_url = "https://www.alphavantage.co/query"
    
    # Test with Moroccan stocks
    tickers = ["ATW", "IAM", "BCP"]
    
    for ticker in tickers:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": api_key
        }
        response = requests.get(base_url, params=params)
        # Check if data exists
```

### 2. Web Scraping from Moroccan Sites
```python
# Scrape from Moroccan financial websites
import requests
from bs4 import BeautifulSoup

def scrape_moroccan_financial_sites():
    sites = [
        "https://www.casablanca-bourse.com/",
        "https://www.maghrebsecurities.com/",
        "https://www.attijariwafa.com/",
        "https://www.iam.ma/"
    ]
    
    for site in sites:
        # Implement scraping logic
        pass
```

### 3. Manual Data Entry with Validation
```python
# Manual data entry system
def manual_data_entry():
    # Create interface for manual data entry
    # Validate data quality
    # Store in database
    pass
```

---

## Database Schema Requirements

### New Tables Needed

#### 1. Trading Data
```sql
CREATE TABLE trading_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    adj_close DECIMAL(10,2),
    data_source VARCHAR(50), -- 'manual', 'scraped', 'api'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, date)
);
```

#### 2. Financial Reports
```sql
CREATE TABLE financial_reports (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    title TEXT,
    file_path TEXT,
    file_size BIGINT,
    url TEXT,
    language VARCHAR(10) DEFAULT 'fr',
    extracted_data JSONB,
    processing_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. Financial Metrics
```sql
CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'MAD',
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, year, quarter, metric_name)
);
```

#### 4. News & Events
```sql
CREATE TABLE company_news (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP,
    sentiment_score DECIMAL(3,2),
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Airflow DAG Enhancements

### 1. Trading Data DAG - UPDATED
```python
# Updated DAG for alternative trading data sources
dag = DAG(
    'trading_data_pipeline',
    schedule_interval='0 8 * * 1-5',  # Weekdays at 8 AM
    catchup=False
)

def fetch_trading_data_alternative(tickers: List[str]):
    """Fetch trading data from alternative sources"""
    # Try multiple sources in order of preference
    sources = [
        'alpha_vantage',
        'web_scraping',
        'manual_entry'
    ]
    
    for source in sources:
        try:
            if source == 'alpha_vantage':
                return fetch_alpha_vantage_data(tickers)
            elif source == 'web_scraping':
                return scrape_moroccan_sites(tickers)
            elif source == 'manual_entry':
                return get_manual_data(tickers)
        except Exception as e:
            logger.warning(f"Source {source} failed: {e}")
            continue
    
    return []

def validate_trading_data(ticker: str):
    """Validate trading data quality"""
    pass

# Create dynamic tasks for each batch
for i in range(0, len(ALL_TICKERS), BATCH_SIZE):
    batch = ALL_TICKERS[i:i+BATCH_SIZE]
    fetch_task = PythonOperator(
        task_id=f'fetch_batch_{i//BATCH_SIZE}',
        python_callable=fetch_trading_data_alternative,
        op_kwargs={'tickers': batch}
    )
```

### 2. Enhanced ETL DAG
```python
# Enhanced existing DAG with batching
def create_company_batches():
    """Create batches of companies for parallel processing"""
    companies = get_all_companies()
    return [companies[i:i+BATCH_SIZE] for i in range(0, len(companies), BATCH_SIZE)]

# Use TaskGroup for parallel processing
with TaskGroup(group_id='company_batches') as tg:
    for batch_num, batch in enumerate(create_company_batches()):
        with TaskGroup(group_id=f'batch_{batch_num}') as batch_tg:
            # Scrape reports for this batch
            scrape_task = PythonOperator(
                task_id='scrape_reports',
                python_callable=scrape_company_reports,
                op_kwargs={'companies': batch}
            )
            
            # Extract data from reports
            extract_task = PythonOperator(
                task_id='extract_data',
                python_callable=extract_financial_data,
                op_kwargs={'companies': batch}
            )
            
            scrape_task >> extract_task
```

---

## Website Implementation

### 1. Company Page Updates
```typescript
// Enhanced company page with partial data handling
const CompanyPage: React.FC<{ticker: string}> = ({ticker}) => {
  const {data, loading, error} = useCompanyData(ticker);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div>
      {/* Always show basic info */}
      <CompanyHeader company={data.basic} />
      
      {/* Show trading data if available */}
      {data.trading ? (
        <TradingChart data={data.trading} />
      ) : (
        <DataLoadingMessage type="trading" />
      )}
      
      {/* Show reports if available */}
      {data.reports && data.reports.length > 0 ? (
        <FinancialReports reports={data.reports} />
      ) : (
        <DataLoadingMessage type="reports" />
      )}
      
      {/* Show news if available */}
      {data.news && data.news.length > 0 ? (
        <CompanyNews news={data.news} />
      ) : (
        <DataLoadingMessage type="news" />
      )}
    </div>
  );
};
```

### 2. Data Loading Components
```typescript
// Graceful data loading messages
const DataLoadingMessage: React.FC<{type: string}> = ({type}) => {
  const messages = {
    trading: "Trading data is loading, check back soon.",
    reports: "Financial reports are being processed, check back soon.",
    news: "News and updates are loading, check back soon."
  };
  
  return (
    <div className="data-loading-message">
      <Icon type={type} />
      <p>{messages[type]}</p>
    </div>
  );
};
```

### 3. Data Availability Indicators
```typescript
// Show data completeness for each company
const DataCompletenessIndicator: React.FC<{company: Company}> = ({company}) => {
  const completeness = calculateDataCompleteness(company);
  
  return (
    <div className="data-completeness">
      <ProgressBar value={completeness} />
      <span>{completeness}% complete</span>
    </div>
  );
};
```

---

## Immediate Action Items

### Week 1 Priorities - UPDATED
1. **Research Trading Data Sources**
   - [ ] Test Alpha Vantage API
   - [ ] Research Moroccan financial websites
   - [ ] Identify alternative data providers
   - [ ] Create fallback data entry system

2. **Implement Alternative Trading Data Pipeline**
   - [ ] Create multi-source trading data DAG
   - [ ] Implement web scraping from Moroccan sites
   - [ ] Add manual data entry interface
   - [ ] Test with 10 companies first

3. **Update Website for Partial Data**
   - [ ] Add loading states
   - [ ] Implement graceful degradation
   - [ ] Test with missing data
   - [ ] Deploy updates

4. **Enhance Existing ETL**
   - [ ] Add batching to current DAG
   - [ ] Implement retry logic
   - [ ] Add progress tracking
   - [ ] Test with first 20 companies

### Success Metrics - UPDATED
- **Week 1:** Website functional with basic data + alternative trading data for 20+ companies
- **Week 2:** 30+ companies with financial reports
- **Week 3:** 50+ companies with complete data
- **Week 4:** 70+ companies with full coverage

### Risk Mitigation
1. **API Rate Limits:** Implement rate limiting and caching
2. **Scraping Blocks:** Use rotating proxies and delays
3. **Data Quality:** Implement validation and error handling
4. **Performance:** Use caching and CDN for static data
5. **Trading Data Unavailability:** Multiple fallback sources

---

## Conclusion

**CRITICAL UPDATE:** Yahoo Finance doesn't provide Moroccan stock data, which requires us to pivot to alternative data sources. However, this doesn't prevent us from building a functional website. We can:

1. **Start with what we have** (basic company data + financial reports)
2. **Research alternative trading data sources** (Alpha Vantage, web scraping, manual entry)
3. **Show progress** (partial data with loading states)
4. **Build incrementally** (batch processing for reports)
5. **Maintain quality** (validation and error handling)

The website will still feel complete and functional from day one, with data coverage improving over time as we implement alternative trading data sources. 