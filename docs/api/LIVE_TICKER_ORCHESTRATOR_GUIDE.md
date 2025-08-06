# 🚀 Morning Maghreb Live Ticker Orchestrator Guide

## 📊 **Overview**

The Live Ticker Orchestrator is a real-time data collection system that scrapes live ticker data from multiple sources every few minutes. It's designed to provide up-to-the-minute market data for priority Moroccan companies.

## 🎯 **Key Features**

### **Real-Time Data Collection**
- ⏰ Updates every 5 minutes (configurable)
- 📈 Tracks 16 priority tickers
- 🔄 Multiple data sources for redundancy
- 💾 Automatic database updates and file saves

### **Data Sources**
1. **African Markets** - Comprehensive company data
2. **Casablanca Bourse** - Official exchange data
3. **Wafa Bourse** - Additional market data

### **Priority Tickers**
```
ATW  - Attijariwafa Bank
IAM  - Maroc Telecom
BCP  - Banque Centrale Populaire
BMCE - BMCE Bank of Africa
CIH  - Crédit Immobilier et Hôtelier
WAA  - Wafa Assurance
SAH  - Saham Assurance
ADH  - Addoha
LBV  - Label Vie
MAR  - Marjane Holding
LES  - Lesieur Cristal
CEN  - Ciments du Maroc
HOL  - Holcim Maroc
LAF  - Lafarge Ciments
MSA  - Managem
TMA  - Taqa Morocco
```

## 🔧 **Technical Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Live Ticker    │───▶│  Data Sources   │───▶│  Supabase DB    │
│  Orchestrator   │    │  (3 Sources)    │    │  + File Storage │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Schedule every         Merge & Prioritize      Live Ticker Table
    5 minutes              Most Recent Data        + JSON Files
```

## 📋 **Installation & Setup**

### **1. Install Dependencies**
```bash
python3 -m pip install schedule requests aiohttp beautifulsoup4
```

### **2. Test the Orchestrator**
```bash
# Run a single test
./scripts/test_live_orchestrator.sh

# Or directly
python3 scripts/live_ticker_orchestrator.py test
```

### **3. Start the Live Orchestrator**
```bash
# Start the orchestrator
./scripts/start_live_orchestrator.sh

# Or directly
python3 scripts/live_ticker_orchestrator.py
```

## 🛠️ **Configuration**

### **Update Interval**
Edit `scripts/live_ticker_orchestrator.py`:
```python
self.update_interval_minutes = 5  # Change to desired interval
```

### **Priority Tickers**
Edit the priority tickers list:
```python
self.priority_tickers = [
    "ATW", "IAM", "BCP", "BMCE", "CIH", "WAA", "SAH", "ADH", 
    "LBV", "MAR", "LES", "CEN", "HOL", "LAF", "MSA", "TMA"
]
```

### **Data Sources**
The orchestrator automatically uses all available scrapers:
- African Markets Scraper
- Casablanca Bourse Scraper
- Wafa Bourse Scraper

## 📊 **Data Structure**

### **LiveTickerData Class**
```python
@dataclass
class LiveTickerData:
    ticker: str                    # Company ticker (e.g., "ATW")
    name: str                      # Company name
    price: float                   # Current price
    change_1d_percent: Optional[float]  # Daily change %
    change_ytd_percent: Optional[float] # YTD change %
    volume: Optional[int]          # Trading volume
    market_cap_billion: Optional[float]  # Market cap
    high_24h: Optional[float]      # 24h high
    low_24h: Optional[float]       # 24h low
    open_price: Optional[float]    # Opening price
    previous_close: Optional[float] # Previous close
    source: str                    # Data source
    timestamp: str                 # Update timestamp
    exchange: str = "Casablanca Stock Exchange"
    country: str = "Morocco"
```

## 📈 **Output Files**

### **Live Ticker Data**
- **Location**: `apps/backend/data/live_tickers/`
- **Format**: `live_tickers_YYYYMMDD_HHMMSS.json`
- **Content**: All live ticker data with metadata

### **Logs**
- **Location**: `logs/live_ticker_orchestrator.log`
- **Content**: Real-time updates, errors, statistics

## 🗄️ **Database Integration**

### **Supabase Table**
The orchestrator updates a `live_tickers` table with:
- Real-time price data
- Market movements
- Volume information
- Source attribution

### **Database Schema**
```sql
CREATE TABLE live_tickers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    change_1d_percent DECIMAL(5,2),
    change_ytd_percent DECIMAL(5,2),
    volume BIGINT,
    market_cap_billion DECIMAL(10,2),
    high_24h DECIMAL(10,2),
    low_24h DECIMAL(10,2),
    open_price DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    source VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    exchange VARCHAR(100) DEFAULT 'Casablanca Stock Exchange',
    country VARCHAR(100) DEFAULT 'Morocco'
);
```

## 🚀 **Production Deployment**

### **1. Systemd Service (Linux)**
```bash
# Copy service file
sudo cp scripts/morning-maghreb-live-ticker.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable morning-maghreb-live-ticker
sudo systemctl start morning-maghreb-live-ticker

# Check status
sudo systemctl status morning-maghreb-live-ticker
```

### **2. Background Process (macOS)**
```bash
# Start in background
nohup python3 scripts/live_ticker_orchestrator.py > logs/orchestrator.out 2>&1 &

# Check if running
ps aux | grep live_ticker_orchestrator
```

### **3. Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "scripts/live_ticker_orchestrator.py"]
```

## 📊 **Monitoring & Logs**

### **Real-Time Monitoring**
```bash
# View live logs
tail -f logs/live_ticker_orchestrator.log

# Check recent updates
ls -la apps/backend/data/live_tickers/

# View latest data
cat apps/backend/data/live_tickers/live_tickers_*.json | jq '.live_tickers[0:5]'
```

### **Statistics**
The orchestrator tracks:
- Total updates
- Successful updates
- Failed updates
- Last run time
- Start time

## 🔧 **Troubleshooting**

### **Common Issues**

1. **No Data Collected**
   - Check internet connection
   - Verify scraper dependencies
   - Check source website availability

2. **Database Errors**
   - Verify Supabase credentials
   - Check table schema exists
   - Review API rate limits

3. **High CPU Usage**
   - Increase update interval
   - Reduce priority tickers
   - Add error backoff

### **Error Recovery**
- Automatic retry on failures
- Exponential backoff
- Source fallback (if one source fails, others continue)

## 📈 **Performance Optimization**

### **Recommended Settings**
- **Update Interval**: 5 minutes (balance between real-time and server load)
- **Priority Tickers**: 16 companies (focus on most liquid)
- **Data Sources**: 3 sources (redundancy and accuracy)

### **Scaling Options**
- Add more data sources
- Increase ticker list
- Reduce update interval
- Parallel scraping

## 🎉 **Status: PRODUCTION READY**

Your live ticker orchestrator is ready for production deployment! It will provide real-time market data for your priority Moroccan companies every 5 minutes.

### **What's Working**
- ✅ Real-time data collection from multiple sources
- ✅ Automatic database updates
- ✅ File-based data storage
- ✅ Comprehensive logging and monitoring
- ✅ Error handling and recovery
- ✅ Configurable update intervals

### **Next Steps**
1. **Test the orchestrator** - Run the test script
2. **Deploy to production** - Use systemd service or background process
3. **Monitor performance** - Check logs and database updates
4. **Scale as needed** - Add more tickers or sources

The live ticker orchestrator will provide the real-time data foundation for your Morning Maghreb platform! 🚀 