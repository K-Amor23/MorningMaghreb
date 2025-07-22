# 📊 Volume Scraping Implementation for Casablanca Stock Exchange

## 🎯 Overview

This implementation provides comprehensive volume data scraping for the Casablanca Stock Exchange (CSE), including daily volume, volume trends, alerts, and analysis. The system scrapes volume data from multiple sources and provides detailed analytics.

## 🏗️ Architecture

### **Core Components:**

1. **Volume Scraper** (`volume_scraper.py`) - Main scraper for volume data
2. **Enhanced African Markets Scraper** - Updated to include volume data
3. **Volume Data Integration** (`volume_data_integration.py`) - Database integration
4. **Volume Analysis Schema** (`volume_analysis_schema.sql`) - Database schema
5. **Test Script** (`test_volume_scraping.py`) - Testing and validation

### **Data Sources:**
- **African Markets** - Primary source for CSE volume data
- **Wafabourse** - Moroccan financial portal
- **Investing.com** - International financial data
- **Yahoo Finance** - Backup source for volume data

## 📁 File Structure

```
apps/backend/etl/
├── volume_scraper.py              # Main volume scraper
├── volume_data_integration.py     # Database integration
├── african_markets_scraper.py     # Enhanced with volume support
└── ...

database/
└── volume_analysis_schema.sql     # Database schema

test_volume_scraping.py            # Test script
```

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
cd apps/backend
pip install -r requirements.txt
```

### **2. Set Environment Variables**

```bash
# Add to your .env.local file
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

### **3. Run Volume Scraping**

```bash
# Test the volume scraping
python test_volume_scraping.py

# Run full volume integration
cd apps/backend/etl
python volume_data_integration.py
```

## 📊 Features

### **Volume Data Collection**
- ✅ **Multi-source scraping** from African Markets, Wafabourse, Investing.com
- ✅ **Volume cleaning** handles various formats (K, M, B, commas)
- ✅ **Data validation** ensures quality and completeness
- ✅ **Concurrent scraping** for faster data collection

### **Volume Analysis**
- ✅ **Moving averages** (5-day, 20-day)
- ✅ **Volume ratios** (current vs average)
- ✅ **Volume alerts** (high/low volume detection)
- ✅ **Trend analysis** (increasing/decreasing patterns)

### **Database Integration**
- ✅ **Supabase integration** for real-time updates
- ✅ **Volume analysis tables** for comprehensive storage
- ✅ **Views and functions** for easy querying
- ✅ **Data quality tracking** for reliability

## 🗄️ Database Schema

### **Main Tables:**

1. **`volume_analysis`** - Core volume data
2. **`volume_trends`** - Aggregated trends
3. **`volume_alerts`** - Volume-based alerts
4. **`sector_volume_analysis`** - Sector-level analysis
5. **`market_volume_summary`** - Market-wide metrics
6. **`volume_data_quality`** - Data quality tracking

### **Key Views:**
- `latest_volume_analysis` - Most recent volume data
- `high_volume_alerts` - High volume stocks
- `active_volume_alerts` - Active alerts
- `market_volume_dashboard` - Market overview

## 📈 Usage Examples

### **1. Basic Volume Scraping**

```python
from volume_scraper import VolumeScraper

async with VolumeScraper() as scraper:
    volume_data = await scraper.scrape_all_volume_data()
    
    for data in volume_data:
        print(f"{data.ticker}: {data.volume:,} shares")
```

### **2. Volume Integration**

```python
from volume_data_integration import VolumeDataIntegration

integration = VolumeDataIntegration(supabase_url, supabase_key)
results = await integration.run_volume_integration()
```

### **3. Database Queries**

```sql
-- Get latest volume data
SELECT * FROM latest_volume_analysis;

-- Find high volume stocks
SELECT * FROM high_volume_alerts;

-- Market volume summary
SELECT * FROM market_volume_dashboard;
```

## 🔧 Configuration

### **Volume Scraper Settings**

```python
# In volume_scraper.py
class VolumeScraper:
    def __init__(self):
        self.sources = {
            "african_markets": {
                "url": "https://www.african-markets.com/en/stock-markets/bvc/listed-companies",
                "name": "African Markets"
            },
            # Add more sources as needed
        }
```

### **Alert Thresholds**

```python
# High volume alert: > 2x average
HIGH_VOLUME_THRESHOLD = 2.0

# Low volume alert: < 0.5x average  
LOW_VOLUME_THRESHOLD = 0.5
```

## 📊 Data Quality

### **Volume Data Validation**
- ✅ **Format validation** - Ensures proper number formats
- ✅ **Range validation** - Checks for reasonable volume values
- ✅ **Source verification** - Validates data source reliability
- ✅ **Completeness check** - Ensures all required fields present

### **Quality Metrics**
- **Data completeness ratio** - Percentage of stocks with volume data
- **Volume confidence score** - Confidence in volume accuracy
- **Data freshness** - Hours since last update
- **Overall quality score** - Composite quality metric

## 🚨 Alerts and Notifications

### **Volume Alert Types**
1. **High Volume Alert** - Volume > 2x average
2. **Low Volume Alert** - Volume < 0.5x average
3. **Volume Spike Alert** - Sudden volume increase
4. **Volume Drop Alert** - Sudden volume decrease

### **Alert Configuration**
```python
# Alert thresholds
HIGH_VOLUME_RATIO = 2.0
LOW_VOLUME_RATIO = 0.5
SPIKE_THRESHOLD = 3.0
DROP_THRESHOLD = 0.3
```

## 📈 Analytics and Reporting

### **Volume Metrics**
- **Total market volume** - Sum of all stock volumes
- **Average stock volume** - Mean volume across stocks
- **Volume distribution** - Percentiles and ranges
- **Sector volume analysis** - Volume by sector

### **Trend Analysis**
- **Volume trends** - Increasing/decreasing patterns
- **Moving averages** - 5-day and 20-day averages
- **Volume volatility** - Standard deviation of volume
- **Correlation analysis** - Volume vs price correlation

## 🔄 Automation

### **Scheduled Updates**
```bash
# Daily volume update (add to crontab)
0 18 * * 1-5 cd /path/to/project && python apps/backend/etl/volume_data_integration.py

# Weekly volume analysis
0 9 * * 1 cd /path/to/project && python apps/backend/etl/volume_analysis.py
```

### **Airflow Integration**
```python
# Example Airflow DAG
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

dag = DAG('volume_data_pipeline', schedule_interval='0 18 * * 1-5')

volume_scraping = PythonOperator(
    task_id='scrape_volume_data',
    python_callable=run_volume_integration,
    dag=dag
)
```

## 🧪 Testing

### **Run Tests**
```bash
# Test volume scraping
python test_volume_scraping.py

# Test specific components
python -m pytest tests/test_volume_scraper.py
```

### **Test Coverage**
- ✅ **Volume scraper functionality**
- ✅ **Data cleaning and validation**
- ✅ **Database integration**
- ✅ **Alert generation**
- ✅ **Error handling**

## 📊 Sample Output

### **Volume Data**
```json
{
  "ticker": "ATW",
  "volume": 1500000,
  "average_volume": 800000,
  "volume_ratio": 1.875,
  "high_volume_alert": true,
  "source": "African Markets"
}
```

### **Volume Report**
```json
{
  "summary": {
    "total_volume": 85000000,
    "average_volume": 1200000,
    "high_volume_stocks": 5,
    "low_volume_stocks": 3
  },
  "alerts": {
    "high_volume": [
      {"ticker": "CIH", "volume": 2500000, "ratio": 2.5}
    ]
  }
}
```

## 🔧 Troubleshooting

### **Common Issues**

1. **No volume data found**
   - Check internet connection
   - Verify source URLs are accessible
   - Check for website changes

2. **Database connection errors**
   - Verify Supabase credentials
   - Check database schema exists
   - Ensure proper permissions

3. **Volume parsing errors**
   - Check volume format in source
   - Update cleaning functions
   - Add new format patterns

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python volume_scraper.py --debug
```

## 📈 Performance

### **Optimization Tips**
- ✅ **Concurrent scraping** - Multiple sources simultaneously
- ✅ **Connection pooling** - Reuse HTTP connections
- ✅ **Caching** - Cache frequently accessed data
- ✅ **Batch processing** - Process data in batches

### **Expected Performance**
- **Scraping speed**: ~50-100 stocks/minute
- **Database updates**: ~1000 records/second
- **Memory usage**: ~50-100MB for full dataset
- **Processing time**: 2-5 minutes for complete update

## 🔮 Future Enhancements

### **Planned Features**
- 🔄 **Real-time volume streaming**
- 📊 **Advanced volume analytics**
- 🤖 **AI-powered volume predictions**
- 📱 **Mobile volume alerts**
- 🌐 **WebSocket volume updates**

### **Integration Opportunities**
- **Trading platforms** - Real-time volume feeds
- **Analytics tools** - Volume analysis integration
- **Alert systems** - Custom volume notifications
- **Reporting tools** - Automated volume reports

## 📚 API Reference

### **VolumeScraper Class**
```python
class VolumeScraper:
    async def scrape_all_volume_data() -> List[VolumeData]
    async def scrape_african_markets_volume() -> List[VolumeData]
    async def scrape_wafabourse_volume() -> List[VolumeData]
    def clean_volume_value(value: str) -> Optional[int]
```

### **VolumeData Class**
```python
@dataclass
class VolumeData:
    ticker: str
    date: datetime
    volume: int
    average_volume: Optional[int]
    volume_ratio: Optional[float]
    high_volume_alert: bool
    source: str
```

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

### **Code Standards**
- Follow PEP 8 style guide
- Add type hints
- Include docstrings
- Write unit tests

## 📄 License

This volume scraping implementation is part of the Casablanca Insight project and follows the same licensing terms.

---

## 🎉 Summary

The volume scraping implementation provides:

✅ **Comprehensive volume data collection** from multiple sources  
✅ **Advanced volume analysis** with trends and alerts  
✅ **Robust database integration** with Supabase  
✅ **Quality assurance** with validation and testing  
✅ **Scalable architecture** for future enhancements  

This system enables detailed volume analysis for the Casablanca Stock Exchange, providing valuable insights for traders, analysts, and investors. 