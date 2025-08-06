# 🚀 Scrapers Quick Start Guide

## Overview

The scrapers module provides a unified interface for all data collection tasks. Each scraper inherits from `BaseScraper` and implements standardized methods.

## Quick Start

### 1. Basic Usage

```python
from scrapers.financial_reports.financial_reports_scraper import FinancialReportsScraper

# Create scraper instance
scraper = FinancialReportsScraper()

# Fetch data
data = scraper.fetch()

# Validate data
if scraper.validate_data(data):
    # Save data
    scraper.save_data(data, "financial_reports.csv")
    print(f"Saved {len(data)} records")
else:
    print("Data validation failed")
```

### 2. Running All Scrapers

```python
from scrapers.orchestrator import MasterOrchestrator

# Create orchestrator
orchestrator = MasterOrchestrator()

# Run all scrapers
results = orchestrator.run_pipeline()

# Check results
for name, data in results.items():
    print(f"{name}: {len(data)} records")
```

### 3. Adding a New Scraper

```python
from scrapers.base.scraper_interface import BaseScraper
import pandas as pd

class MyNewScraper(BaseScraper):
    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://api.example.com"
    
    def fetch(self) -> pd.DataFrame:
        """Fetch data from source"""
        # Your scraping logic here
        data = []
        # ... scraping code ...
        return pd.DataFrame(data)
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        required_columns = ['id', 'name', 'value']
        return all(col in data.columns for col in required_columns)
```

## Available Scrapers

### Financial Reports
- `FinancialReportsScraper` - Scrapes financial reports and statements
- `FinancialReportsAdvancedEtl` - Advanced ETL for financial data

### News & Sentiment
- `NewsSentimentScraper` - Basic news and sentiment analysis
- `NewsSentimentAdvancedEtl` - Advanced sentiment processing

### Market Data
- `CasablancaBourseScraper` - Casablanca Stock Exchange data
- `CasablancaBourseOhlcvScraper` - OHLCV market data
- `ComprehensiveCompanyScraper` - Comprehensive company data

### Macro Data
- `MacroDataScraper` - Macroeconomic indicators
- `FetchEconomicData` - Economic data collection

### Currency Data
- `CurrencyScraper` - Currency and forex data

### Volume Data
- `VolumeScraper` - Trading volume data
- `VolumeDataIntegration` - Volume data integration

### Bank Data
- `BankAlMaghribScraper` - Bank Al-Maghrib data

### African Markets
- `AfricanMarketsScraper` - African markets data

## Configuration

Scrapers use configuration from environment variables:

```bash
# Required environment variables
export NEXT_PUBLIC_SUPABASE_URL="your_supabase_url"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_supabase_key"
export OPENAI_API_KEY="your_openai_key"
export SENDGRID_API_KEY="your_sendgrid_key"
export STRIPE_SECRET_KEY="your_stripe_key"
```

## Error Handling

All scrapers include built-in error handling:

```python
try:
    scraper = FinancialReportsScraper()
    data = scraper.fetch()
except Exception as e:
    print(f"Scraper failed: {e}")
    # Handle error appropriately
```

## Data Validation

Each scraper implements data validation:

```python
if scraper.validate_data(data):
    print("Data is valid")
else:
    print("Data validation failed")
```

## Utilities

Common utilities are available in `scrapers.utils`:

```python
from scrapers.utils import make_request, parse_date, load_config

# HTTP requests with retry logic
response = make_request("https://api.example.com/data")

# Date parsing
date = parse_date("2025-08-06")

# Configuration loading
config = load_config()
```

## Testing

Test individual scrapers:

```python
# Test scraper
scraper = FinancialReportsScraper()
data = scraper.fetch()
print(f"Fetched {len(data)} records")

# Validate data
if scraper.validate_data(data):
    print("✅ Data validation passed")
else:
    print("❌ Data validation failed")
```

## Monitoring

Monitor scraper health:

```python
from scrapers.orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()
results = orchestrator.run_pipeline()

# Check success rate
successful = len([r for r in results.values() if not r.empty])
total = len(results)
print(f"Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the correct directory
2. **Configuration Errors**: Check environment variables
3. **Network Errors**: Verify internet connection and API endpoints
4. **Data Validation Errors**: Check data format and required columns

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

scraper = FinancialReportsScraper()
data = scraper.fetch()
```

## Next Steps

1. **Review Scraper Code**: Check individual scraper implementations
2. **Test Data Quality**: Validate scraped data against requirements
3. **Optimize Performance**: Add caching and rate limiting as needed
4. **Add Monitoring**: Implement health checks and alerting

For more information, see the main `README.md` in the scrapers directory. 