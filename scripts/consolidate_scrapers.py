#!/usr/bin/env python3
"""
Scraper Consolidation Script
Extracts scrapers into modular structure with common interface
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any
import json

class ScraperConsolidator:
    def __init__(self, source_dir: str = "apps/backend/etl", target_dir: str = "scrapers"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.scraper_files = []
        self.common_interface = """
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

class BaseScraper(ABC):
    \"\"\"Base class for all scrapers with common interface\"\"\"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        \"\"\"Fetch data and return as DataFrame\"\"\"
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        \"\"\"Validate fetched data\"\"\"
        pass
    
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Transform data to standard format\"\"\"
        return data
    
    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        \"\"\"Save data to destination\"\"\"
        try:
            data.to_csv(destination, index=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            return False
"""
    
    def identify_scrapers(self) -> List[Dict[str, Any]]:
        """Identify all scraper files in the source directory"""
        scrapers = []
        
        # Common scraper patterns
        scraper_patterns = [
            r".*_scraper\.py$",
            r".*_etl\.py$",
            r"scraper.*\.py$",
            r"etl.*\.py$"
        ]
        
        for file_path in self.source_dir.rglob("*.py"):
            if any(re.match(pattern, file_path.name) for pattern in scraper_patterns):
                # Skip certain files
                if any(skip in file_path.name.lower() for skip in [
                    'test_', 'mock_', 'scheduler', 'orchestrator', 'celery'
                ]):
                    continue
                
                scrapers.append({
                    "file": file_path,
                    "name": file_path.stem,
                    "type": self._classify_scraper(file_path),
                    "dependencies": self._extract_dependencies(file_path)
                })
        
        return scrapers
    
    def _classify_scraper(self, file_path: Path) -> str:
        """Classify scraper based on filename and content"""
        name = file_path.name.lower()
        
        if 'financial' in name or 'reports' in name:
            return 'financial_reports'
        elif 'news' in name or 'sentiment' in name:
            return 'news_sentiment'
        elif 'market' in name or 'ohlcv' in name:
            return 'market_data'
        elif 'macro' in name or 'economic' in name:
            return 'macro_data'
        elif 'currency' in name or 'forex' in name:
            return 'currency_data'
        elif 'volume' in name:
            return 'volume_data'
        elif 'bank' in name or 'bam' in name:
            return 'bank_data'
        elif 'african' in name:
            return 'african_markets'
        else:
            return 'general'
    
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from scraper file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract imports
            imports = []
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith(('import ', 'from ')):
                    imports.append(line.strip())
            
            return imports
        except Exception:
            return []
    
    def create_scraper_structure(self):
        """Create the new scraper directory structure"""
        print("🏗️  Creating scraper directory structure...")
        
        # Create main directories
        (self.target_dir / "base").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "financial_reports").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "news_sentiment").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "market_data").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "macro_data").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "currency_data").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "volume_data").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "bank_data").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "african_markets").mkdir(parents=True, exist_ok=True)
        (self.target_dir / "utils").mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        for subdir in self.target_dir.iterdir():
            if subdir.is_dir():
                (subdir / "__init__.py").touch()
    
    def create_base_interface(self):
        """Create the base scraper interface"""
        print("📋 Creating base scraper interface...")
        
        base_file = self.target_dir / "base" / "scraper_interface.py"
        with open(base_file, 'w') as f:
            f.write(self.common_interface)
        
        # Create __init__.py for base
        init_content = """
from .scraper_interface import BaseScraper

__all__ = ['BaseScraper']
"""
        with open(self.target_dir / "base" / "__init__.py", 'w') as f:
            f.write(init_content)
    
    def extract_common_utils(self):
        """Extract common utilities used across scrapers"""
        print("🔧 Extracting common utilities...")
        
        utils = {
            "http_helpers.py": self._create_http_helpers(),
            "date_parsers.py": self._create_date_parsers(),
            "config_loader.py": self._create_config_loader(),
            "data_validators.py": self._create_data_validators()
        }
        
        for filename, content in utils.items():
            with open(self.target_dir / "utils" / filename, 'w') as f:
                f.write(content)
        
        # Create utils __init__.py
        utils_init = """
from .http_helpers import *
from .date_parsers import *
from .config_loader import *
from .data_validators import *

__all__ = [
    'make_request',
    'parse_date',
    'load_config',
    'validate_dataframe'
]
"""
        with open(self.target_dir / "utils" / "__init__.py", 'w') as f:
            f.write(utils_init)
    
    def _create_http_helpers(self) -> str:
        return '''
import requests
import time
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 3
) -> requests.Response:
    """Make HTTP request with retry logic"""
    
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Add default headers
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    response = session.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=data,
        timeout=timeout
    )
    
    response.raise_for_status()
    return response

def add_delay(seconds: float = 1.0):
    """Add delay between requests"""
    time.sleep(seconds)
'''
    
    def _create_date_parsers(self) -> str:
        return '''
from datetime import datetime, date
from typing import Union, Optional
import re

def parse_date(
    date_str: str,
    formats: Optional[list] = None,
    default: Optional[date] = None
) -> Optional[date]:
    """Parse date string with multiple format support"""
    
    if formats is None:
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return default

def extract_date_from_text(text: str) -> Optional[date]:
    """Extract date from text using regex patterns"""
    
    patterns = [
        r"\\b\\d{4}-\\d{2}-\\d{2}\\b",
        r"\\b\\d{2}/\\d{2}/\\d{4}\\b",
        r"\\b\\d{2}-\\d{2}-\\d{4}\\b"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return parse_date(match.group())
    
    return None
'''
    
    def _create_config_loader(self) -> str:
        return '''
import os
from typing import Dict, Any, Optional
from pathlib import Path
import json

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment"""
    
    config = {}
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config.update(json.load(f))
    
    # Load from environment variables
    env_config = {
        "SUPABASE_URL": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY")
    }
    
    config.update({k: v for k, v in env_config.items() if v})
    
    return config

def get_scraper_config(scraper_name: str) -> Dict[str, Any]:
    """Get configuration for specific scraper"""
    
    config = load_config()
    
    # Scraper-specific configurations
    scraper_configs = {
        "financial_reports": {
            "base_url": "https://www.casablanca-bourse.com",
            "delay": 2.0,
            "max_retries": 3
        },
        "news_sentiment": {
            "base_url": "https://api.newsapi.org",
            "delay": 1.0,
            "max_retries": 5
        },
        "market_data": {
            "base_url": "https://api.marketdata.com",
            "delay": 0.5,
            "max_retries": 3
        }
    }
    
    return {**config, **scraper_configs.get(scraper_name, {})}
'''
    
    def _create_data_validators(self) -> str:
        return '''
import pandas as pd
from typing import List, Dict, Any, Optional

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    date_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None
) -> bool:
    """Validate DataFrame structure and data types"""
    
    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for empty DataFrame
    if df.empty:
        print("DataFrame is empty")
        return False
    
    # Check date columns
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col])
                except:
                    print(f"Invalid date format in column: {col}")
                    return False
    
    # Check numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    print(f"Invalid numeric format in column: {col}")
                    return False
    
    return True

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame by removing duplicates and nulls"""
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Remove rows where all values are null
    df = df.dropna(how='all')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df
'''
    
    def migrate_scrapers(self):
        """Migrate existing scrapers to new structure"""
        print("🔄 Migrating scrapers to new structure...")
        
        scrapers = self.identify_scrapers()
        
        for scraper in scrapers:
            self._migrate_scraper(scraper)
    
    def _migrate_scraper(self, scraper: Dict[str, Any]):
        """Migrate individual scraper"""
        source_file = scraper["file"]
        scraper_type = scraper["type"]
        target_dir = self.target_dir / scraper_type
        
        # Create target file
        target_file = target_dir / f"{scraper['name']}.py"
        
        print(f"  📦 Migrating {source_file.name} to {target_file}")
        
        try:
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Transform content to use new interface
            transformed_content = self._transform_scraper_content(content, scraper['name'])
            
            # Write to target
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(transformed_content)
                
        except Exception as e:
            print(f"  ❌ Failed to migrate {source_file.name}: {e}")
    
    def _transform_scraper_content(self, content: str, scraper_name: str) -> str:
        """Transform scraper content to use new interface"""
        
        # Add imports for new structure
        new_imports = f'''
from ..base.scraper_interface import BaseScraper
from ..utils.http_helpers import make_request, add_delay
from ..utils.date_parsers import parse_date, extract_date_from_text
from ..utils.config_loader import get_scraper_config
from ..utils.data_validators import validate_dataframe, clean_dataframe
import pandas as pd
import logging
from typing import Dict, Any, Optional
'''
        
        # Add class definition if not present
        if f"class {scraper_name.title().replace('_', '')}" not in content:
            class_def = f'''

class {scraper_name.title().replace('_', '')}Scraper(BaseScraper):
    """{scraper_name.replace('_', ' ').title()} Scraper"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = get_scraper_config("{scraper_name}")
    
    def fetch(self) -> pd.DataFrame:
        """Fetch data from source"""
        # TODO: Implement fetch logic
        return pd.DataFrame()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        # TODO: Implement validation logic
        return True
'''
            content += class_def
        
        return new_imports + content
    
    def create_orchestrator(self):
        """Create the master orchestrator"""
        print("🎼 Creating master orchestrator...")
        
        orchestrator_content = '''
"""
Master Orchestrator for All Scrapers
Coordinates execution of all scrapers and manages data flow
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime

# Import all scrapers
from .financial_reports import *
from .news_sentiment import *
from .market_data import *
from .macro_data import *
from .currency_data import *
from .volume_data import *
from .bank_data import *
from .african_markets import *

class MasterOrchestrator:
    """Master orchestrator for all scrapers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize all available scrapers"""
        scrapers = {}
        
        # Financial Reports Scrapers
        try:
            from .financial_reports.financial_reports_scraper import FinancialReportsScraper
            scrapers['financial_reports'] = FinancialReportsScraper(self.config)
        except ImportError:
            self.logger.warning("Financial reports scraper not available")
        
        # News Sentiment Scrapers
        try:
            from .news_sentiment.news_sentiment_scraper import NewsSentimentScraper
            scrapers['news_sentiment'] = NewsSentimentScraper(self.config)
        except ImportError:
            self.logger.warning("News sentiment scraper not available")
        
        # Market Data Scrapers
        try:
            from .market_data.casablanca_bourse_scraper import CasablancaBourseScraper
            scrapers['market_data'] = CasablancaBourseScraper(self.config)
        except ImportError:
            self.logger.warning("Market data scraper not available")
        
        # Add more scrapers as needed...
        
        return scrapers
    
    async def run_all_scrapers(self) -> Dict[str, pd.DataFrame]:
        """Run all scrapers and return results"""
        results = {}
        
        for name, scraper in self.scrapers.items():
            try:
                self.logger.info(f"Running {name} scraper...")
                data = scraper.fetch()
                
                if scraper.validate_data(data):
                    results[name] = data
                    self.logger.info(f"{name} scraper completed successfully")
                else:
                    self.logger.error(f"{name} scraper validation failed")
                    
            except Exception as e:
                self.logger.error(f"{name} scraper failed: {e}")
        
        return results
    
    def save_results(self, results: Dict[str, pd.DataFrame], output_dir: str = "data"):
        """Save all results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, data in results.items():
            if not data.empty:
                filename = f"{name}_{timestamp}.csv"
                filepath = output_path / filename
                data.to_csv(filepath, index=False)
                self.logger.info(f"Saved {name} data to {filepath}")
    
    def run_pipeline(self, save_results: bool = True) -> Dict[str, pd.DataFrame]:
        """Run complete data pipeline"""
        self.logger.info("Starting master data pipeline...")
        
        # Run all scrapers
        results = asyncio.run(self.run_all_scrapers())
        
        # Save results if requested
        if save_results:
            self.save_results(results)
        
        self.logger.info(f"Pipeline completed. Processed {len(results)} scrapers.")
        return results

def main():
    """Main entry point for orchestrator"""
    orchestrator = MasterOrchestrator()
    results = orchestrator.run_pipeline()
    
    print(f"Pipeline completed successfully!")
    print(f"Processed {len(results)} scrapers")
    
    for name, data in results.items():
        print(f"  {name}: {len(data)} records")

if __name__ == "__main__":
    main()
'''
        
        orchestrator_file = self.target_dir / "orchestrator.py"
        with open(orchestrator_file, 'w') as f:
            f.write(orchestrator_content)
    
    def create_requirements(self):
        """Create requirements.txt for scrapers"""
        print("📦 Creating requirements.txt...")
        
        requirements = '''
# Scraper Dependencies
requests>=2.28.0
pandas>=1.5.0
numpy>=1.21.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
webdriver-manager>=3.8.0

# Data Processing
openpyxl>=3.0.0
xlrd>=2.0.0

# Database
supabase>=1.0.0
psycopg2-binary>=2.9.0

# Utilities
python-dotenv>=0.19.0
schedule>=1.2.0
loguru>=0.6.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
'''
        
        with open(self.target_dir / "requirements.txt", 'w') as f:
            f.write(requirements)
    
    def create_readme(self):
        """Create README for scrapers"""
        print("📖 Creating README...")
        
        readme_content = '''
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
'''
        
        with open(self.target_dir / "README.md", 'w') as f:
            f.write(readme_content)

def main():
    """Main consolidation execution"""
    print("🚀 Starting scraper consolidation...")
    
    consolidator = ScraperConsolidator()
    
    # Create structure
    consolidator.create_scraper_structure()
    consolidator.create_base_interface()
    consolidator.extract_common_utils()
    
    # Migrate scrapers
    consolidator.migrate_scrapers()
    
    # Create orchestrator
    consolidator.create_orchestrator()
    consolidator.create_requirements()
    consolidator.create_readme()
    
    print("✅ Scraper consolidation complete!")
    print(f"📁 New structure created at: {consolidator.target_dir}")
    print("📖 See README.md for usage instructions")

if __name__ == "__main__":
    main() 