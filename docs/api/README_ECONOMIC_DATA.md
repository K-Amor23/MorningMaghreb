# Economic Data Fetcher

This module provides automated fetching and processing of Moroccan economic data from Bank Al-Maghrib (BAM). It integrates seamlessly with the existing ETL pipeline and provides RESTful API endpoints for accessing economic indicators.

## 📊 Supported Economic Indicators

| Indicator | Frequency | Format | Description |
|-----------|-----------|--------|-------------|
| Key Policy Rate | Monthly | XLS | Interest rate decisions, 7-day rate |
| Foreign Exchange Reserves | Weekly | XLS | In MAD and foreign currencies |
| Inflation (CPI) | Monthly | XLS | From High Commission of Planning |
| Money Supply (M1/M2/M3) | Monthly | XLS | Downloadable from BAM |
| Balance of Payments | Quarterly | XLS | Foreign trade and capital flows |
| Credit to Economy | Monthly | XLS | Sectoral lending breakdown |

## 🚀 Quick Start

### 1. Installation

The economic data fetcher is already integrated into the backend. No additional installation is required.

### 2. Configuration

The data sources are configured in `data/economic_data_sources.yaml`. You can modify:

- URLs for data sources
- Parsing rules for different file formats
- Validation rules for data quality
- Request timeouts and retry settings

### 3. Testing

Run the test script to verify the setup:

```bash
cd apps/backend
python test_economic_data.py
```

### 4. API Usage

Start the backend server:

```bash
cd apps/backend
python main.py
```

## 🔌 API Endpoints

### Get Available Indicators
```bash
GET /api/economic-data/indicators
```

Response:
```json
[
  "key_policy_rate",
  "foreign_exchange_reserves", 
  "inflation_cpi",
  "money_supply",
  "balance_of_payments",
  "credit_to_economy"
]
```

### Get Economic Data Summary
```bash
GET /api/economic-data/
```

### Get Specific Indicator Data
```bash
GET /api/economic-data/{indicator}
GET /api/economic-data/key_policy_rate
```

Parameters:
- `start_date` (optional): Start date for data range (YYYY-MM-DD)
- `end_date` (optional): End date for data range (YYYY-MM-DD)
- `limit` (optional): Maximum number of data points (default: 100, max: 1000)

### Get Latest Data Point
```bash
GET /api/economic-data/{indicator}/latest
GET /api/economic-data/key_policy_rate/latest
```

### Fetch New Data from BAM
```bash
POST /api/economic-data/fetch
```

Parameters:
- `indicators` (optional): List of specific indicators to fetch

### Compare Two Indicators
```bash
GET /api/economic-data/compare/{indicator1}/{indicator2}
GET /api/economic-data/compare/key_policy_rate/inflation_cpi
```

### Get Trend Analysis
```bash
GET /api/economic-data/trends/{indicator}
GET /api/economic-data/trends/key_policy_rate?period=12m
```

### Get Economic Dashboard
```bash
GET /api/economic-data/dashboard/overview
```

## 📁 File Structure

```
apps/backend/
├── etl/
│   └── fetch_economic_data.py      # Main economic data fetcher
├── models/
│   └── economic_data.py            # Data models and schemas
├── routers/
│   └── economic_data.py            # API endpoints
├── data/
│   └── economic_data_sources.yaml  # Configuration file
├── test_economic_data.py           # Test script
└── README_ECONOMIC_DATA.md         # This file
```

## 🔧 Configuration

### Data Sources Configuration

Edit `data/economic_data_sources.yaml` to configure:

```yaml
sources:
  key_policy_rate:
    name: "Key Policy Rate"
    url: "https://www.bkam.ma/Marche-des-capitaux/Taux-et-cours/Taux-directeur"
    frequency: "monthly"
    format: "xls"
    description: "Interest rate decisions, 7-day rate"
    category: "monetary_policy"
    units: "percent"
    priority: "high"
    parsing_rules:
      date_column_patterns: ["date", "periode", "mois", "annee"]
      value_column_patterns: ["taux", "rate", "directeur", "7"]
      expected_columns: ["date", "taux_directeur"]
```

### Global Settings

```yaml
settings:
  base_url: "https://www.bkam.ma"
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  request_delay_min: 1
  request_delay_max: 3
  max_files_per_indicator: 5
  data_retention_days: 365
  backup_enabled: true
```

## 🔄 Data Processing Pipeline

1. **Discovery**: Scrape BAM website to find download links
2. **Download**: Download Excel/PDF files from BAM
3. **Parse**: Extract data using pandas and custom parsers
4. **Validate**: Apply validation rules for data quality
5. **Store**: Save raw and processed data to storage
6. **API**: Serve data through RESTful endpoints

## 📊 Data Models

### EconomicDataPoint
```python
{
    "date": "2024-01-15",
    "value": 3.0,
    "unit": "percent",
    "indicator": "key_policy_rate",
    "source": "BAM",
    "confidence": 0.95,
    "metadata": {}
}
```

### EconomicDataResponse
```python
{
    "indicator": "key_policy_rate",
    "data_points": [...],
    "summary": {
        "latest_value": 3.0,
        "latest_date": "2024-01-15",
        "unit": "percent",
        "frequency": "monthly",
        "source": "BAM",
        "last_updated": "2024-01-15T10:30:00Z",
        "trend": "stable",
        "change_percentage": 0.0
    },
    "metadata": {
        "total_points": 12,
        "date_range": {
            "start": "2023-01-01",
            "end": "2024-01-01"
        },
        "source": "BAM"
    }
}
```

## 🛠️ Customization

### Adding New Indicators

1. Add the indicator to `EconomicIndicatorType` enum in `models/economic_data.py`
2. Add configuration to `data/economic_data_sources.yaml`
3. Implement parsing logic in `fetch_economic_data.py`
4. Add validation rules if needed

### Custom Parsers

Create custom parsing functions for specific data formats:

```python
def _extract_custom_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract data for custom indicator"""
    data_points = []
    
    # Your custom parsing logic here
    
    return data_points
```

### Data Validation

Add validation rules in the configuration:

```yaml
validation:
  value_ranges:
    custom_indicator:
      min: 0.0
      max: 100.0
```

## 🔍 Monitoring and Logging

The fetcher includes comprehensive logging:

```python
import logging
logger = logging.getLogger(__name__)

# Log levels: DEBUG, INFO, WARNING, ERROR
```

Monitor the logs for:
- Download success/failure
- Parsing errors
- Data validation issues
- API request patterns

## 🚨 Error Handling

The system handles various error scenarios:

- **Network errors**: Automatic retries with exponential backoff
- **Parsing errors**: Graceful degradation with error reporting
- **Validation errors**: Data flagged for manual review
- **Rate limiting**: Respectful delays between requests

## 🔐 Security Considerations

- Uses proper User-Agent headers
- Implements request delays to avoid overwhelming servers
- Validates all downloaded data
- Sanitizes file paths and names
- Logs all activities for audit purposes

## 📈 Performance Optimization

- Parallel processing of multiple indicators
- Caching of parsed data
- Efficient storage of large datasets
- Pagination for API responses
- Background processing for data fetching

## 🔄 Automation

### Cron Job Setup

Add to your crontab for automated data fetching:

```bash
# Fetch economic data daily at 6 AM
0 6 * * * cd /path/to/apps/backend && python -c "
import asyncio
from etl.fetch_economic_data import EconomicDataFetcher
from storage.local_fs import LocalFileStorage

async def fetch_data():
    storage = LocalFileStorage()
    fetcher = EconomicDataFetcher(storage)
    await fetcher.fetch_all_economic_data()

asyncio.run(fetch_data())
"
```

### Webhook Integration

Set up webhooks to trigger data fetching on specific events:

```python
@app.post("/webhook/economic-data")
async def economic_data_webhook(request: Request):
    # Trigger data fetch based on webhook
    pass
```

## 🧪 Testing

### Unit Tests

```bash
# Run economic data tests
python -m pytest tests/test_economic_data.py -v
```

### Integration Tests

```bash
# Test API endpoints
curl http://localhost:8000/api/economic-data/indicators
curl http://localhost:8000/api/economic-data/key_policy_rate
```

### Load Testing

```bash
# Test API performance
ab -n 1000 -c 10 http://localhost:8000/api/economic-data/
```

## 📚 Examples

### Python Client

```python
import requests

# Get latest policy rate
response = requests.get("http://localhost:8000/api/economic-data/key_policy_rate/latest")
data = response.json()
print(f"Latest policy rate: {data['latest_value']}%")

# Fetch new data
response = requests.post("http://localhost:8000/api/economic-data/fetch")
print("Data fetch initiated")
```

### JavaScript Client

```javascript
// Get economic dashboard
fetch('/api/economic-data/dashboard/overview')
  .then(response => response.json())
  .then(data => {
    console.log('Economic outlook:', data.data.economic_outlook);
    console.log('Key indicators:', data.data.key_indicators);
  });
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the logs for error details
2. Review the configuration file
3. Test with the provided test script
4. Open an issue with detailed information

## 📄 License

This module is part of the Casablanca Insight project and follows the same license terms. 