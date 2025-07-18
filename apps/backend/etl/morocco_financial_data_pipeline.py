#!/usr/bin/env python3
"""
Morocco Financial Data Pipeline

This comprehensive pipeline integrates data from multiple sources:
1. Company data from African Markets (Casablanca Stock Exchange)
2. Central bank data from Bank Al-Maghrib
3. Economic indicators and market data

Provides a complete view of Morocco's financial ecosystem.
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any

# Import our custom scrapers
from african_markets_scraper import AfricanMarketsScraper
from bank_al_maghrib_scraper import BankAlMaghribScraper

logger = logging.getLogger(__name__)

class MoroccoFinancialDataPipeline:
    """Comprehensive Morocco financial data pipeline"""
    
    def __init__(self, output_dir: str = "data/morocco_financial"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.company_data = []
        self.central_bank_data = {}
        self.integrated_data = {}
        
    async def fetch_company_data(self) -> List[Dict]:
        """Fetch all companies from Casablanca Stock Exchange"""
        logger.info("🏢 Fetching company data from African Markets...")
        
        async with AfricanMarketsScraper() as scraper:
            companies = await scraper.scrape_all()
            
        logger.info(f"✅ Retrieved {len(companies)} companies")
        return companies
    
    async def fetch_central_bank_data(self) -> Dict[str, List[Dict]]:
        """Fetch central bank data from Bank Al-Maghrib"""
        logger.info("🏦 Fetching central bank data from Bank Al-Maghrib...")
        
        async with BankAlMaghribScraper() as scraper:
            data = await scraper.scrape_all()
            
        total_records = sum(len(items) for items in data.values())
        logger.info(f"✅ Retrieved {total_records} central bank data points")
        return data
    
    def integrate_financial_data(self) -> Dict[str, Any]:
        """Integrate company and central bank data"""
        logger.info("🔄 Integrating financial data...")
        
        # Get current exchange rates for market cap calculations
        exchange_rates = {}
        if "exchange_rates" in self.central_bank_data:
            for rate in self.central_bank_data["exchange_rates"]:
                currency = rate.get("currency", "")
                if "USD" in currency.upper():
                    exchange_rates["USD_MAD"] = rate.get("rate_18/07/2025", rate.get("rate", 0))
                elif "EUR" in currency.upper():
                    exchange_rates["EUR_MAD"] = rate.get("rate_18/07/2025", rate.get("rate", 0))
        
        # Get current interest rates
        interest_rates = {}
        if "interest_rates" in self.central_bank_data:
            for rate in self.central_bank_data["interest_rates"]:
                maturity = rate.get("maturity", "")
                if maturity:
                    interest_rates[maturity] = {
                        "bid_rate": rate.get("bid_rate"),
                        "ask_rate": rate.get("ask_rate")
                    }
        
        # Get banking sector overview
        banking_overview = {}
        if "banking_data" in self.central_bank_data:
            for item in self.central_bank_data["banking_data"]:
                indicator = item.get("indicator", "")
                value = item.get("numeric_value", item.get("value_text"))
                if indicator and value:
                    banking_overview[indicator.lower().replace(" ", "_")] = value
        
        # Enhance company data with financial context
        enhanced_companies = []
        for company in self.company_data:
            enhanced_company = company.copy()
            
            # Add exchange rate context
            if exchange_rates:
                enhanced_company["exchange_rates"] = exchange_rates
                
                # Convert market cap to USD if available
                mcap_mad = company.get("market_cap_billion", 0)
                if mcap_mad and "USD_MAD" in exchange_rates and exchange_rates["USD_MAD"]:
                    mcap_usd = mcap_mad / exchange_rates["USD_MAD"]
                    enhanced_company["market_cap_usd_billion"] = round(mcap_usd, 2)
            
            # Add interest rate environment
            if interest_rates:
                enhanced_company["interest_rate_environment"] = interest_rates
            
            # Add banking sector context
            enhanced_company["banking_sector_overview"] = banking_overview
            
            enhanced_companies.append(enhanced_company)
        
        # Create integrated dataset
        integrated_data = {
            "metadata": {
                "pipeline": "Morocco Financial Data Pipeline",
                "generated_at": datetime.now().isoformat(),
                "data_sources": [
                    "African Markets (Casablanca Stock Exchange)",
                    "Bank Al-Maghrib (Moroccan Central Bank)"
                ],
                "total_companies": len(enhanced_companies),
                "total_central_bank_indicators": sum(len(items) for items in self.central_bank_data.values())
            },
            
            "market_overview": {
                "exchange": "Casablanca Stock Exchange (BVC)",
                "total_listed_companies": len(enhanced_companies),
                "sectors": self._get_sector_breakdown(enhanced_companies),
                "market_cap_distribution": self._get_market_cap_distribution(enhanced_companies),
                "exchange_rates": exchange_rates,
                "interest_rates": interest_rates,
                "banking_sector": banking_overview
            },
            
            "companies": enhanced_companies,
            
            "central_bank_data": self.central_bank_data,
            
            "economic_indicators": {
                "exchange_rates": exchange_rates,
                "interest_rates": interest_rates,
                "banking_metrics": banking_overview,
                "market_operations": self._extract_market_operations()
            }
        }
        
        return integrated_data
    
    def _get_sector_breakdown(self, companies: List[Dict]) -> Dict[str, int]:
        """Get breakdown of companies by sector"""
        sectors = {}
        for company in companies:
            sector = company.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + 1
        return dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True))
    
    def _get_market_cap_distribution(self, companies: List[Dict]) -> Dict[str, Any]:
        """Get market capitalization distribution"""
        market_caps = []
        for company in companies:
            mcap = company.get("market_cap_billion", 0)
            if mcap and mcap > 0:
                market_caps.append(mcap)
        
        if not market_caps:
            return {}
        
        return {
            "total_market_cap_billion_mad": round(sum(market_caps), 2),
            "average_market_cap_billion_mad": round(sum(market_caps) / len(market_caps), 2),
            "largest_company_mcap_billion_mad": max(market_caps),
            "smallest_company_mcap_billion_mad": min(market_caps),
            "companies_with_mcap_data": len(market_caps)
        }
    
    def _extract_market_operations(self) -> Dict[str, Any]:
        """Extract market operations data"""
        if "market_operations" not in self.central_bank_data:
            return {}
        
        operations = self.central_bank_data["market_operations"]
        if not operations:
            return {}
        
        # Get latest operations
        latest_operations = []
        for op in operations[:5]:  # Get last 5 operations
            latest_operations.append({
                "date": op.get("indicator", ""),
                "value": op.get("numeric_value", 0),
                "value_text": op.get("value_text", "")
            })
        
        return {
            "latest_operations": latest_operations,
            "total_operations_tracked": len(operations)
        }
    
    def export_integrated_data(self, data: Dict[str, Any]) -> Path:
        """Export integrated data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main integrated file
        main_file = self.output_dir / f"morocco_financial_data_{timestamp}.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Companies CSV for easy analysis
        companies_file = self.output_dir / f"morocco_companies_{timestamp}.csv"
        if data.get("companies"):
            df = pd.DataFrame(data["companies"])
            df.to_csv(companies_file, index=False, encoding='utf-8')
        
        # Market overview summary
        summary_file = self.output_dir / f"morocco_market_summary_{timestamp}.json"
        summary = {
            "metadata": data["metadata"],
            "market_overview": data["market_overview"],
            "economic_indicators": data["economic_indicators"]
        }
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Integrated data exported to:")
        logger.info(f"  📄 Main file: {main_file}")
        logger.info(f"  📊 Companies CSV: {companies_file}")
        logger.info(f"  📋 Summary: {summary_file}")
        
        return main_file
    
    def print_summary(self, data: Dict[str, Any]):
        """Print a comprehensive summary of the integrated data"""
        logger.info("\n" + "="*80)
        logger.info("🇲🇦 MOROCCO FINANCIAL DATA PIPELINE SUMMARY")
        logger.info("="*80)
        
        # Metadata
        metadata = data.get("metadata", {})
        logger.info(f"📅 Generated: {metadata.get('generated_at', 'Unknown')}")
        logger.info(f"🏢 Total Companies: {metadata.get('total_companies', 0)}")
        logger.info(f"📊 Central Bank Indicators: {metadata.get('total_central_bank_indicators', 0)}")
        
        # Market overview
        market_overview = data.get("market_overview", {})
        logger.info(f"\n📈 MARKET OVERVIEW:")
        logger.info(f"  Exchange: {market_overview.get('exchange', 'Unknown')}")
        logger.info(f"  Listed Companies: {market_overview.get('total_listed_companies', 0)}")
        
        # Sector breakdown
        sectors = market_overview.get("sectors", {})
        if sectors:
            logger.info(f"\n🏭 SECTOR BREAKDOWN:")
            for sector, count in list(sectors.items())[:10]:  # Top 10 sectors
                logger.info(f"  {sector}: {count} companies")
        
        # Market cap distribution
        mcap_dist = market_overview.get("market_cap_distribution", {})
        if mcap_dist:
            logger.info(f"\n💰 MARKET CAPITALIZATION:")
            logger.info(f"  Total Market Cap: {mcap_dist.get('total_market_cap_billion_mad', 0):.2f} billion MAD")
            logger.info(f"  Average Market Cap: {mcap_dist.get('average_market_cap_billion_mad', 0):.2f} billion MAD")
            logger.info(f"  Largest Company: {mcap_dist.get('largest_company_mcap_billion_mad', 0):.2f} billion MAD")
        
        # Exchange rates
        exchange_rates = market_overview.get("exchange_rates", {})
        if exchange_rates:
            logger.info(f"\n💱 EXCHANGE RATES:")
            for currency, rate in exchange_rates.items():
                logger.info(f"  {currency}: {rate}")
        
        # Interest rates
        interest_rates = market_overview.get("interest_rates", {})
        if interest_rates:
            logger.info(f"\n📊 INTEREST RATES:")
            for maturity, rates in list(interest_rates.items())[:5]:  # Top 5 maturities
                bid = rates.get("bid_rate", "N/A")
                ask = rates.get("ask_rate", "N/A")
                logger.info(f"  {maturity}: Bid {bid}% / Ask {ask}%")
        
        # Banking sector
        banking = market_overview.get("banking_sector", {})
        if banking:
            logger.info(f"\n🏦 BANKING SECTOR:")
            for metric, value in list(banking.items())[:5]:  # Top 5 metrics
                logger.info(f"  {metric.replace('_', ' ').title()}: {value}")
        
        logger.info("\n" + "="*80)
        logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
    
    async def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete financial data pipeline"""
        logger.info("🚀 Starting Morocco Financial Data Pipeline")
        
        # Fetch data from both sources
        self.company_data = await self.fetch_company_data()
        self.central_bank_data = await self.fetch_central_bank_data()
        
        # Integrate the data
        integrated_data = self.integrate_financial_data()
        
        # Export integrated data
        main_file = self.export_integrated_data(integrated_data)
        
        # Print summary
        self.print_summary(integrated_data)
        
        return integrated_data

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    pipeline = MoroccoFinancialDataPipeline()
    integrated_data = await pipeline.run_pipeline()
    
    return integrated_data

if __name__ == "__main__":
    asyncio.run(main()) 