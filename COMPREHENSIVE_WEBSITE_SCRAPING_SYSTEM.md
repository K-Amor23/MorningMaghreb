# Comprehensive Website Scraping System

## 🎯 **Overview**

We've enhanced the Casablanca Insights ETL pipeline to automatically discover and scrape **all 78 companies' websites** for their annual reports, financial statements, and other investor relations documents. This creates a comprehensive financial data collection system.

## 🔍 **What the System Does**

### **1. Automatic Website Discovery**
- **Discovers IR pages** for all 78 companies automatically
- **Finds investor relations sections** using common URL patterns
- **Identifies financial document pages** across different company websites
- **Supports multiple languages** (French, English, Arabic)

### **2. Intelligent Document Detection**
- **Scans for PDFs, Excel files, Word documents**
- **Identifies annual reports, quarterly reports, financial statements**
- **Extracts metadata** (year, quarter, report type, file size)
- **Handles embedded documents** (PDFs in iframes, etc.)

### **3. Automated Download & Processing**
- **Downloads all discovered documents** with proper naming
- **Organizes files by company and date**
- **Integrates with existing PDF extraction pipeline**
- **Stores metadata for tracking and analysis**

## 🏗️ **System Architecture**

### **Core Components**

1. **`ComprehensiveCompanyScraper`** - Main scraping engine
2. **`CompanyWebsite`** - Company website configuration
3. **`DiscoveredReport`** - Report metadata structure
4. **Airflow Integration** - Automated daily execution

### **Data Flow**
```
Company Websites → Discovery → Scraping → Download → PDF Extraction → Data Processing
```

## 📊 **Supported Companies**

### **Banking Sector**
- **ATW** - Attijariwafa Bank
- **BCP** - Banque Centrale Populaire  
- **BMCE** - BMCE Bank of Africa
- **CIH** - CIH Bank

### **Telecommunications**
- **IAM** - Maroc Telecom

### **Energy**
- **GAZ** - Afriquia Gaz
- **TMA** - Taqa Morocco

### **Materials**
- **CMT** - Ciments du Maroc
- **LAFA** - Lafarge Ciments
- **MNG** - Managem

### **Insurance**
- **AMA** - Alliance Marocaine de l'Assurance
- **WAA** - Wafa Assurance

### **Real Estate**
- **RISM** - Risma
- **ADH** - Addoha

### **Distribution**
- **LBV** - Label'Vie

*And many more... (78 total companies)*

## 🔧 **Technical Implementation**

### **Website Discovery Patterns**
```python
ir_page_patterns = [
    "/investisseurs",
    "/investors", 
    "/relations-investisseurs",
    "/investor-relations",
    "/informations-financieres",
    "/financial-information",
    "/resultats-financiers",
    "/financial-results",
    "/rapports-annuels",
    "/annual-reports",
    "/documents-financiers",
    "/financial-documents"
]
```

### **Document Classification**
```python
report_patterns = {
    ReportType.ANNUAL_REPORT: [
        r"rapport.*annuel.*(\d{4})",
        r"annual.*report.*(\d{4})",
        r"comptes.*annuels.*(\d{4})",
        r"annual.*accounts.*(\d{4})"
    ],
    ReportType.QUARTERLY_REPORT: [
        r"trimestre.*(\d{4})",
        r"quarter.*(\d{4})",
        r"q[1-4].*(\d{4})",
        r"t[1-4].*(\d{4})"
    ],
    ReportType.FINANCIAL_STATEMENTS: [
        r"etats.*financiers.*(\d{4})",
        r"financial.*statements.*(\d{4})"
    ]
}
```

### **File Organization**
```
/tmp/company_reports/
├── 20250122/
│   ├── ATW_Annual_Report_2024_20250122_060000.pdf
│   ├── IAM_Quarterly_Report_Q4_2024_20250122_060000.pdf
│   ├── BCP_Financial_Statements_2024_20250122_060000.pdf
│   └── ...
└── company_discovery_results_20250122.json
```

## 📈 **Enhanced Airflow Pipeline**

### **Updated Pipeline Flow**
```
1. 🔄 Refresh 78 companies data from African Markets
2. 🌐 Scrape all company websites for annual reports and financial documents
3. 📄 Fetch IR reports from company websites
4. 🔍 Extract financial data from PDFs
5. 🔄 Translate French labels to GAAP
6. 💾 Store processed data in database
7. ✅ Validate data quality
8. 📢 Send success/failure alerts
```

### **New Task: `scrape_company_websites`**
- **Discovers IR pages** for all 78 companies
- **Scrapes financial documents** automatically
- **Downloads reports** with proper organization
- **Saves discovery metadata** for tracking

### **Enhanced Success Alerts**
```
🎉 Casablanca Insights ETL Pipeline Completed Successfully!

📊 Pipeline Results:
• African Markets: 78 companies refreshed
• Company Websites: 45 companies scraped
• Financial Reports: 156 reports discovered
• Files Downloaded: 142 files
• Reports Processed: 4
• Data Validation: ✅ Passed
• Execution Date: 2025-01-22T06:00:00

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Casablanca API: http://localhost:8000
```

## 🎯 **Key Features**

### **1. Intelligent Discovery**
- **Automatic IR page detection** using common patterns
- **Multi-language support** (French, English, Arabic)
- **Fallback mechanisms** for different website structures
- **Rate limiting** to be respectful to company servers

### **2. Comprehensive Coverage**
- **All 78 companies** in the database
- **Multiple document types** (annual, quarterly, financial statements)
- **Historical data** going back several years
- **Real-time updates** with daily execution

### **3. Robust Processing**
- **Error handling** for failed downloads
- **Duplicate detection** to avoid re-downloading
- **File validation** to ensure document integrity
- **Metadata extraction** for proper categorization

### **4. Integration Ready**
- **Seamless Airflow integration** with existing pipeline
- **PDF extraction compatibility** with current system
- **Database storage** for discovered metadata
- **API endpoints** for accessing scraped data

## 📋 **Discovery Results**

### **Sample Discovery Output**
```json
{
  "discovery_date": "2025-01-22T06:00:00",
  "companies_discovered": 45,
  "reports_discovered": 156,
  "companies": [
    {
      "ticker": "ATW",
      "name": "Attijariwafa Bank",
      "base_url": "https://www.attijariwafabank.com",
      "ir_url": "https://ir.attijariwafabank.com",
      "investor_relations_url": "https://www.attijariwafabank.com/investisseurs",
      "financial_reports_url": "https://ir.attijariwafabank.com/financial-information",
      "annual_reports_url": "https://ir.attijariwafabank.com/annual-reports",
      "quarterly_reports_url": "https://ir.attijariwafabank.com/quarterly-reports",
      "language": "fr"
    }
  ],
  "reports": [
    {
      "company": "ATW",
      "title": "Rapport Annuel 2024",
      "url": "https://ir.attijariwafabank.com/annual-reports/2024.pdf",
      "report_type": "annual_report",
      "year": 2024,
      "quarter": null,
      "language": "fr",
      "file_size": 5242880,
      "discovered_at": "2025-01-22T06:15:30"
    }
  ]
}
```

## 🚀 **Deployment & Usage**

### **1. Airflow Integration**
```bash
# The enhanced DAG is already integrated
# Runs daily at 6:00 AM UTC
# Monitors: http://localhost:8080
```

### **2. Manual Execution**
```python
from comprehensive_company_scraper import ComprehensiveCompanyScraper
from storage.local_fs import LocalFileStorage

async def run_scraping():
    storage = LocalFileStorage()
    async with ComprehensiveCompanyScraper(storage) as scraper:
        # Discover companies
        companies = await scraper.discover_all_companies()
        
        # Scrape reports
        reports = await scraper.scrape_all_companies_reports()
        
        # Download files
        files = await scraper.download_reports(reports)
        
        # Save results
        await scraper.save_discovery_results(companies, reports)

# Run
asyncio.run(run_scraping())
```

### **3. Configuration**
```python
# Add new companies to the database
company_websites = {
    "NEW": CompanyWebsite(
        ticker="NEW",
        name="New Company",
        base_url="https://www.newcompany.ma"
    )
}
```

## 📊 **Monitoring & Analytics**

### **Success Metrics**
- **Companies discovered**: Target 78/78
- **Reports found**: Varies by company (typically 5-20 per company)
- **Download success rate**: Target >95%
- **Processing time**: Target <30 minutes

### **Quality Checks**
- **File integrity validation**
- **Metadata completeness**
- **Document type classification accuracy**
- **Duplicate detection**

### **Error Handling**
- **Network timeouts**: Automatic retry with exponential backoff
- **Access denied**: Log and continue with other companies
- **Invalid URLs**: Skip and report
- **Large files**: Download with progress tracking

## 🔮 **Future Enhancements**

### **Advanced Features**
1. **OCR processing** for scanned documents
2. **Multi-language document extraction**
3. **Real-time monitoring** of new document uploads
4. **Machine learning** for better document classification
5. **API rate limiting** and intelligent scheduling

### **Integration Opportunities**
1. **Document analysis** with AI/ML
2. **Financial data extraction** automation
3. **Compliance monitoring** for regulatory requirements
4. **Market intelligence** from financial reports
5. **Competitive analysis** across companies

## 💡 **Best Practices**

### **Respectful Scraping**
- **Rate limiting**: 1-2 second delays between requests
- **User-Agent headers**: Identify as legitimate bot
- **Robots.txt compliance**: Check and respect
- **Error handling**: Don't overwhelm servers

### **Data Quality**
- **Validation**: Check file integrity after download
- **Metadata**: Extract and store comprehensive information
- **Organization**: Clear file naming and directory structure
- **Backup**: Keep discovery results for analysis

### **Monitoring**
- **Success rates**: Track discovery and download success
- **Performance**: Monitor execution times
- **Errors**: Log and alert on failures
- **Trends**: Analyze document availability over time

This comprehensive website scraping system ensures we capture the most up-to-date financial information from all 78 companies, providing a complete foundation for financial analysis and market intelligence. 