
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
import sys
import os

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

class MasterOrchestrator:
    """Master orchestrator for all scrapers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.scrapers = self._initialize_scrapers()
        
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize all available scrapers"""
        scrapers = {}
        
        # Define scraper mappings
        scraper_mappings = {
            'financial_reports': [
                ('financial_reports_scraper', 'FinancialReportsScraper'),
                ('financial_reports_advanced_etl', 'FinancialReportsAdvancedEtl')
            ],
            'news_sentiment': [
                ('news_sentiment_scraper', 'NewsSentimentScraper'),
                ('news_sentiment_advanced_etl', 'NewsSentimentAdvancedEtl')
            ],
            'market_data': [
                ('casablanca_bourse_ohlcv_scraper', 'CasablancaBourseOhlcvScraper'),
                ('african_markets_scraper', 'AfricanMarketsScraper')
            ],
            'macro_data': [
                ('macro_data_scraper', 'MacroDataScraper')
            ],
            'currency_data': [
                ('currency_scraper', 'CurrencyScraper')
            ],
            'volume_data': [
                ('volume_scraper', 'VolumeScraper')
            ],
            'bank_data': [
                ('bank_al_maghrib_scraper', 'BankAlMaghribScraper')
            ]
        }
        
        # Try to import scrapers
        for category, scraper_list in scraper_mappings.items():
            for module_name, class_name in scraper_list:
                try:
                    # Import the module
                    module = __import__(f"{category}.{module_name}", fromlist=[class_name])
                    scraper_class = getattr(module, class_name)
                    
                    # Create scraper instance
                    scraper_instance = scraper_class(self.config)
                    scrapers[f"{category}_{module_name}"] = scraper_instance
                    
                    self.logger.info(f"✅ Loaded {class_name} from {category}")
                    
                except ImportError as e:
                    self.logger.warning(f"⚠️  Could not import {class_name}: {e}")
                except Exception as e:
                    self.logger.warning(f"⚠️  Error initializing {class_name}: {e}")
        
        return scrapers
    
    async def run_all_scrapers(self) -> Dict[str, pd.DataFrame]:
        """Run all scrapers and return results"""
        results = {}
        
        for name, scraper in self.scrapers.items():
            try:
                self.logger.info(f"🔄 Running {name} scraper...")
                
                # Run the scraper
                data = scraper.fetch()
                
                # Validate the data
                if scraper.validate_data(data):
                    results[name] = data
                    self.logger.info(f"✅ {name} scraper completed successfully: {len(data)} records")
                else:
                    self.logger.error(f"❌ {name} scraper validation failed")
                    
            except Exception as e:
                self.logger.error(f"❌ {name} scraper failed: {e}")
        
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
                self.logger.info(f"💾 Saved {name} data to {filepath}")
    
    def run_pipeline(self, save_results: bool = True) -> Dict[str, pd.DataFrame]:
        """Run complete data pipeline"""
        self.logger.info("🚀 Starting master data pipeline...")
        
        # Run all scrapers
        results = asyncio.run(self.run_all_scrapers())
        
        # Save results if requested
        if save_results:
            self.save_results(results)
        
        self.logger.info(f"✅ Pipeline completed. Processed {len(results)} scrapers.")
        return results

def main():
    """Main entry point for orchestrator"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = MasterOrchestrator()
    results = orchestrator.run_pipeline()
    
    print(f"🎉 Pipeline completed successfully!")
    print(f"📊 Processed {len(results)} scrapers")
    
    for name, data in results.items():
        print(f"  📈 {name}: {len(data)} records")

if __name__ == "__main__":
    main()
