
# Scrapers Module

This module contains all data scrapers organized by type with a common interface.

## Structure

```
scrapers/
├── base/
│   └── scraper_interface.py    # Common interface for all scrapers
├── financial_reports/          # Financial reports scrapers
├── news_sentiment/            # News and sentiment scrapers
├── market_data/               # Market data scrapers
├── macro_data/                # Macroeconomic data scrapers
├── currency_data/             # Currency and forex scrapers
├── volume_data/               # Volume data scrapers
├── bank_data/                 # Bank data scrapers
├── african_markets/           # African markets scrapers
├── utils/                     # Common utilities
├── orchestrator.py            # Master orchestrator
└── requirements.txt           # Dependencies
```

## Usage

### Running Individual Scrapers

```python
from scrapers.financial_reports.financial_reports_scraper import FinancialReportsScraper

scraper = FinancialReportsScraper()
data = scraper.fetch()
```

### Running All Scrapers

```python
from scrapers.orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()
results = orchestrator.run_pipeline()
```

## Adding New Scrapers

1. Create a new file in the appropriate directory
2. Inherit from `BaseScraper`
3. Implement `fetch()` and `validate_data()` methods
4. Add to orchestrator if needed

## Configuration

Scrapers use configuration from environment variables or config files.
See `utils/config_loader.py` for details.
