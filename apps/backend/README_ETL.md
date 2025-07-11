# Casablanca Insight ETL Pipeline

A modular ETL (Extract, Transform, Load) pipeline for processing Moroccan financial reports and converting them to GAAP-compliant data.

## 🏗️ Architecture Overview

```
┌────────────┐      ┌───────────────┐      ┌──────────────┐      ┌──────────────┐
│ PDF Fetch  │ ───▶ │ PDF Extractor │ ───▶ │ Data Cleaner │ ───▶ │ Translator    │
└────────────┘      └───────────────┘      └──────────────┘      └──────────────┘
       │                                                     │
       ▼                                                     ▼
    Local Storage                                Postgres (raw + cleaned)
                                                    + JSONB for tables
```

## 📁 Directory Structure

```
backend/
├── etl/
│   ├── fetch_ir_reports.py      # PDF fetching from company IR pages
│   ├── extract_from_pdf.py      # PDF data extraction
│   ├── translate_labels.py      # French to GAAP translation
│   ├── compute_ratios.py        # Financial ratio calculations
│   └── etl_orchestrator.py      # Main pipeline orchestrator
├── data/
│   └── dict_fr_to_gaap.yaml     # French to GAAP mapping dictionary
├── storage/
│   └── local_fs.py              # Local file storage handler
├── models/
│   └── financials.py            # Pydantic data models
├── api/routes/
│   └── etl.py                   # ETL API endpoints
└── database/
    └── schema.sql               # Database schema
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Run the schema
psql -d your_database -f database/schema.sql
```

### 3. Run the Pipeline

```python
from etl.etl_orchestrator import ETLOrchestrator
from storage.local_fs import LocalFileStorage

# Initialize
storage = LocalFileStorage()
orchestrator = ETLOrchestrator(storage)

# Run pipeline for ATW in 2024
results = await orchestrator.run_full_pipeline(
    companies=["ATW"],
    year=2024
)
```

## 📊 Pipeline Components

### 1. PDF Fetching (`fetch_ir_reports.py`)

**Purpose**: Scrapes company IR pages and downloads financial reports

**Features**:
- Configurable company IR pages
- Automatic report type classification
- Quarter extraction from filenames
- Robust error handling

**Supported Companies**:
- ATW (Attijariwafa Bank)
- IAM (Maroc Telecom)
- BCP (Banque Centrale Populaire)
- BMCE (BMCE Bank)

### 2. PDF Extraction (`extract_from_pdf.py`)

**Purpose**: Extracts tabular data from PDF financial reports

**Methods**:
- **pdfplumber**: Primary method for table extraction
- **PyMuPDF**: Fallback for text extraction
- Pattern matching for financial terms
- Number parsing with French format support

**Output Format**:
```json
{
  "company": "ATW",
  "year": 2024,
  "quarter": 1,
  "report_type": "pnl",
  "lines": [
    {
      "label": "Revenus nets",
      "value": 13940000000,
      "unit": "MAD",
      "confidence": 0.8
    }
  ]
}
```

### 3. Label Translation (`translate_labels.py`)

**Purpose**: Converts French financial labels to GAAP English

**Features**:
- YAML-based mapping dictionary
- Fuzzy matching for similar terms
- Confidence scoring
- Abbreviation handling
- Validation rules

**Mapping Example**:
```yaml
revenue:
  "Revenus nets": "Revenue"
  "Chiffre d'affaires": "Revenue"
  "Ventes": "Sales"
```

### 4. Ratio Computation (`compute_ratios.py`)

**Purpose**: Calculates financial ratios from GAAP data

**Supported Ratios**:
- **Profitability**: ROE, ROA, Gross Margin, Operating Margin, Net Margin
- **Liquidity**: Current Ratio, Quick Ratio, Cash Ratio
- **Solvency**: Debt-to-Equity, Debt-to-Assets, Interest Coverage
- **Efficiency**: Asset Turnover, Inventory Turnover, Receivables Turnover

### 5. ETL Orchestrator (`etl_orchestrator.py`)

**Purpose**: Coordinates all pipeline components

**Features**:
- Job tracking and monitoring
- Error handling and recovery
- Background processing
- Data persistence
- Pipeline metrics

## 🗄️ Database Schema

### Tables

1. **financials_raw**: Raw extracted data from PDFs
2. **financials_gaap**: Clean GAAP-compliant data
3. **label_mappings**: French to GAAP label mappings
4. **etl_jobs**: Job tracking and monitoring

### Key Features:
- JSONB columns for flexible data storage
- UUID primary keys
- Automatic timestamps
- Indexes for performance
- Foreign key relationships

## 🔌 API Endpoints

### ETL Management

- `POST /api/etl/trigger-pipeline` - Start ETL pipeline
- `GET /api/etl/jobs` - List all jobs
- `GET /api/etl/jobs/{job_id}` - Get job status
- `GET /api/etl/health` - Health check

### Data Access

- `GET /api/etl/financials/{company}` - Get company financials
- `GET /api/etl/companies` - List available companies
- `POST /api/etl/cleanup` - Clean up old data

### Example Usage

```bash
# Trigger pipeline
curl -X POST "http://localhost:8000/api/etl/trigger-pipeline" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"companies": ["ATW"], "year": 2024}'

# Get job status
curl "http://localhost:8000/api/etl/jobs/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get company financials
curl "http://localhost:8000/api/etl/financials/ATW?year=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/casablanca_insights

# Storage
STORAGE_PATH=data/

# API Keys (for translation services)
DEEPL_API_KEY=your_deepl_key
OPENAI_API_KEY=your_openai_key
```

### Company Configuration

Add new companies in `fetch_ir_reports.py`:

```python
self.company_ir_pages = {
    "NEW_COMPANY": {
        "base_url": "https://company.com/investors",
        "selectors": {
            "reports": "a[href*='.pdf']",
            "title": "h1, h2, h3",
            "date": ".date"
        }
    }
}
```

## 📈 Monitoring and Logging

### Job Tracking

Each ETL job is tracked with:
- Job ID and type
- Status (pending, running, completed, failed)
- Start/completion timestamps
- Error messages
- Metadata

### Logging

Comprehensive logging at all levels:
- Pipeline progress
- Extraction quality metrics
- Translation confidence scores
- Error details

### Metrics

Pipeline provides metrics on:
- Processing time
- Success rates
- Data quality scores
- Error counts

## 🧪 Testing

### Unit Tests

```bash
# Run tests
pytest tests/etl/

# Test specific component
pytest tests/etl/test_extract_from_pdf.py
```

### Integration Tests

```bash
# Test full pipeline
pytest tests/integration/test_pipeline.py
```

## 🚨 Error Handling

### Common Issues

1. **PDF Extraction Failures**
   - Try different extraction methods
   - Check PDF format and quality
   - Verify financial terms in mapping

2. **Translation Issues**
   - Review confidence scores
   - Add missing mappings to dictionary
   - Check for typos in French labels

3. **Storage Issues**
   - Verify disk space
   - Check file permissions
   - Validate storage path

### Recovery

- Failed jobs can be retried
- Partial data is preserved
- Error logs provide debugging info
- Pipeline can resume from last successful step

## 🔮 Future Enhancements

### Planned Features

1. **AI-Powered Translation**
   - OpenAI integration for unknown labels
   - Context-aware translations
   - Learning from corrections

2. **Advanced Analytics**
   - Trend analysis
   - Peer comparison
   - Anomaly detection

3. **Real-time Processing**
   - Webhook notifications
   - Live data updates
   - Streaming analytics

4. **Cloud Storage**
   - S3 integration
   - Multi-region support
   - Backup and recovery

### Scalability

- Horizontal scaling with Celery
- Database sharding
- Caching layer (Redis)
- Load balancing

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs)
- [Database Schema](database/schema.sql)
- [Mapping Dictionary](data/dict_fr_to_gaap.yaml)
- [Configuration Guide](docs/configuration.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details. 