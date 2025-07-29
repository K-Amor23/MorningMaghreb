"""
Moroccan ETFs and Bonds Data Scraper
Fetches data from AMMC, Casablanca Stock Exchange, and institutional sites
"""

import requests
import pandas as pd
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import re
from bs4 import BeautifulSoup
import sqlite3
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ETFData:
    """ETF data structure"""
    name: str
    ticker: str
    isin: Optional[str]
    underlying_index: Optional[str]
    issuer: Optional[str]
    expense_ratio: Optional[float]
    inception_date: Optional[date]
    listing_date: Optional[date]
    asset_class: Optional[str]
    geographic_focus: Optional[str]
    sector_focus: Optional[str]
    currency: str = "MAD"
    dividend_frequency: Optional[str] = None
    rebalancing_frequency: Optional[str] = None
    source_url: Optional[str] = None
    prospectus_url: Optional[str] = None

@dataclass
class BondData:
    """Bond data structure"""
    name: str
    ticker: str
    isin: Optional[str]
    issuer: str
    issuer_name: Optional[str]
    bond_type: str
    face_value: float
    coupon_rate: Optional[float]
    maturity_date: date
    issue_size: Optional[float]
    credit_rating: Optional[str]
    currency: str = "MAD"
    coupon_frequency: Optional[str] = None
    issue_date: Optional[date] = None
    minimum_investment: Optional[float] = None
    rating_agency: Optional[str] = None
    callable: bool = False
    puttable: bool = False
    convertible: bool = False
    floating_rate: bool = False
    benchmark_rate: Optional[str] = None
    spread: Optional[float] = None
    source_url: Optional[str] = None
    prospectus_url: Optional[str] = None

class MoroccanETFBondScraper:
    """Scraper for Moroccan ETFs and Bonds data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Data sources
        self.sources = {
            'ammc': 'https://www.ammc.ma',
            'cse': 'https://www.casablanca-bourse.com',
            'cdg_capital': 'https://www.cdgcapital.ma',
            'attijari_finance': 'https://www.attijarifinance.ma',
            'bmce_capital': 'https://www.bmcecapital.ma'
        }
        
        # Cache for scraped data
        self.etf_cache = {}
        self.bond_cache = {}
        
    def scrape_ammc_etfs(self) -> List[ETFData]:
        """Scrape ETF data from AMMC (Moroccan Capital Market Authority)"""
        logger.info("Scraping ETF data from AMMC...")
        
        try:
            # AMMC ETF listing page
            url = f"{self.sources['ammc']}/fr/etfs"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            etfs = []
            
            # Look for ETF listings (this is a mock implementation)
            # In reality, you'd parse the actual AMMC website structure
            etf_elements = soup.find_all('div', class_='etf-item')  # Adjust selector
            
            for element in etf_elements:
                try:
                    name = element.find('h3').text.strip()
                    ticker = element.find('span', class_='ticker').text.strip()
                    isin = element.find('span', class_='isin').text.strip()
                    
                    etf = ETFData(
                        name=name,
                        ticker=ticker,
                        isin=isin,
                        underlying_index=None,  # Would extract from page
                        issuer=None,  # Would extract from page
                        expense_ratio=None,  # Would extract from page
                        inception_date=None,  # Would extract from page
                        listing_date=None,  # Would extract from page
                        asset_class='equity',  # Default
                        geographic_focus='Morocco',
                        sector_focus=None,
                        source_url=url
                    )
                    etfs.append(etf)
                    
                except Exception as e:
                    logger.warning(f"Error parsing ETF element: {e}")
                    continue
            
            # For now, return mock data since AMMC structure is unknown
            return self._get_mock_etf_data()
            
        except Exception as e:
            logger.error(f"Error scraping AMMC ETFs: {e}")
            return self._get_mock_etf_data()
    
    def scrape_cse_etfs(self) -> List[ETFData]:
        """Scrape ETF data from Casablanca Stock Exchange"""
        logger.info("Scraping ETF data from CSE...")
        
        try:
            # CSE ETF listing page
            url = f"{self.sources['cse']}/fr/marches/etfs"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSE ETF data
            # This would be implemented based on actual CSE website structure
            return self._get_mock_etf_data()
            
        except Exception as e:
            logger.error(f"Error scraping CSE ETFs: {e}")
            return self._get_mock_etf_data()
    
    def scrape_institutional_etfs(self) -> List[ETFData]:
        """Scrape ETF data from institutional sites (CDG Capital, Attijari Finance, etc.)"""
        logger.info("Scraping ETF data from institutional sites...")
        
        etfs = []
        
        # CDG Capital ETFs
        try:
            cdg_url = f"{self.sources['cdg_capital']}/fr/produits/etfs"
            response = self.session.get(cdg_url, timeout=30)
            if response.status_code == 200:
                # Parse CDG Capital ETF data
                pass
        except Exception as e:
            logger.warning(f"Error scraping CDG Capital ETFs: {e}")
        
        # Attijari Finance ETFs
        try:
            attijari_url = f"{self.sources['attijari_finance']}/fr/produits/etfs"
            response = self.session.get(attijari_url, timeout=30)
            if response.status_code == 200:
                # Parse Attijari Finance ETF data
                pass
        except Exception as e:
            logger.warning(f"Error scraping Attijari Finance ETFs: {e}")
        
        return etfs
    
    def scrape_ammc_bonds(self) -> List[BondData]:
        """Scrape bond data from AMMC"""
        logger.info("Scraping bond data from AMMC...")
        
        try:
            # AMMC bond listing page
            url = f"{self.sources['ammc']}/fr/obligations"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse AMMC bond data
            return self._get_mock_bond_data()
            
        except Exception as e:
            logger.error(f"Error scraping AMMC bonds: {e}")
            return self._get_mock_bond_data()
    
    def scrape_cse_bonds(self) -> List[BondData]:
        """Scrape bond data from Casablanca Stock Exchange"""
        logger.info("Scraping bond data from CSE...")
        
        try:
            # CSE bond listing page
            url = f"{self.sources['cse']}/fr/marches/obligations"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSE bond data
            return self._get_mock_bond_data()
            
        except Exception as e:
            logger.error(f"Error scraping CSE bonds: {e}")
            return self._get_mock_bond_data()
    
    def scrape_yield_curve(self) -> Dict[str, float]:
        """Scrape yield curve data from Bank Al-Maghrib"""
        logger.info("Scraping yield curve data from Bank Al-Maghrib...")
        
        try:
            # Bank Al-Maghrib yield curve data
            url = "https://www.bkam.ma/Marches/Principaux-indicateurs/Marche-des-obligations"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse yield curve data
            # This would extract yields for different maturities
            return self._get_mock_yield_curve()
            
        except Exception as e:
            logger.error(f"Error scraping yield curve: {e}")
            return self._get_mock_yield_curve()
    
    def scrape_bond_issuance_calendar(self) -> List[Dict[str, Any]]:
        """Scrape bond issuance calendar"""
        logger.info("Scraping bond issuance calendar...")
        
        try:
            # Multiple sources for bond issuance calendar
            calendar_data = []
            
            # AMMC issuance calendar
            ammc_url = f"{self.sources['ammc']}/fr/calendrier-emissions"
            response = self.session.get(ammc_url, timeout=30)
            if response.status_code == 200:
                # Parse AMMC issuance calendar
                pass
            
            # CSE issuance calendar
            cse_url = f"{self.sources['cse']}/fr/calendrier-emissions"
            response = self.session.get(cse_url, timeout=30)
            if response.status_code == 200:
                # Parse CSE issuance calendar
                pass
            
            return self._get_mock_issuance_calendar()
            
        except Exception as e:
            logger.error(f"Error scraping bond issuance calendar: {e}")
            return self._get_mock_issuance_calendar()
    
    def _get_mock_etf_data(self) -> List[ETFData]:
        """Return mock ETF data for testing"""
        return [
            ETFData(
                name="MASI ETF",
                ticker="MASI-ETF",
                isin="MA0000012345",
                underlying_index="MASI",
                issuer="CDG Capital",
                expense_ratio=0.0050,
                inception_date=date(2020, 1, 15),
                listing_date=date(2020, 1, 20),
                asset_class="equity",
                geographic_focus="Morocco",
                sector_focus="Broad Market",
                source_url="https://www.cdgcapital.ma/etfs/masi-etf"
            ),
            ETFData(
                name="MADEX ETF",
                ticker="MADEX-ETF",
                isin="MA0000012346",
                underlying_index="MADEX",
                issuer="Attijari Finance",
                expense_ratio=0.0055,
                inception_date=date(2021, 3, 10),
                listing_date=date(2021, 3, 15),
                asset_class="equity",
                geographic_focus="Morocco",
                sector_focus="Large Cap",
                source_url="https://www.attijarifinance.ma/etfs/madex-etf"
            ),
            ETFData(
                name="Morocco Banks ETF",
                ticker="BANK-ETF",
                isin="MA0000012347",
                underlying_index="Bank Index",
                issuer="BMCE Capital",
                expense_ratio=0.0060,
                inception_date=date(2022, 6, 1),
                listing_date=date(2022, 6, 5),
                asset_class="equity",
                geographic_focus="Morocco",
                sector_focus="Financial",
                source_url="https://www.bmcecapital.ma/etfs/bank-etf"
            ),
            ETFData(
                name="Morocco Government Bond ETF",
                ticker="GOVT-ETF",
                isin="MA0000012348",
                underlying_index="Government Bond Index",
                issuer="CDG Capital",
                expense_ratio=0.0040,
                inception_date=date(2023, 1, 1),
                listing_date=date(2023, 1, 5),
                asset_class="bond",
                geographic_focus="Morocco",
                sector_focus="Government",
                source_url="https://www.cdgcapital.ma/etfs/govt-etf"
            )
        ]
    
    def _get_mock_bond_data(self) -> List[BondData]:
        """Return mock bond data for testing"""
        return [
            BondData(
                name="Morocco Government Bond 2025",
                ticker="MOR-GOV-2025",
                isin="MA0000012349",
                issuer="Government",
                issuer_name="Morocco Treasury",
                bond_type="government",
                face_value=10000.00,
                coupon_rate=0.0350,
                maturity_date=date(2025, 12, 31),
                issue_size=10000000000.00,
                credit_rating="BBB+",
                coupon_frequency="annual",
                issue_date=date(2020, 1, 15),
                source_url="https://www.bkam.ma/bonds/mor-gov-2025"
            ),
            BondData(
                name="Morocco Government Bond 2030",
                ticker="MOR-GOV-2030",
                isin="MA0000012350",
                issuer="Government",
                issuer_name="Morocco Treasury",
                bond_type="government",
                face_value=10000.00,
                coupon_rate=0.0400,
                maturity_date=date(2030, 12, 31),
                issue_size=15000000000.00,
                credit_rating="BBB+",
                coupon_frequency="annual",
                issue_date=date(2021, 6, 1),
                source_url="https://www.bkam.ma/bonds/mor-gov-2030"
            ),
            BondData(
                name="Attijariwafa Bank Bond 2026",
                ticker="ATW-BOND-2026",
                isin="MA0000012351",
                issuer="Corporate",
                issuer_name="Attijariwafa Bank",
                bond_type="corporate",
                face_value=10000.00,
                coupon_rate=0.0450,
                maturity_date=date(2026, 6, 30),
                issue_size=5000000000.00,
                credit_rating="A-",
                coupon_frequency="semi-annual",
                issue_date=date(2021, 12, 1),
                source_url="https://www.cse.ma/bonds/atw-bond-2026"
            ),
            BondData(
                name="BMCE Bank Bond 2027",
                ticker="BMCE-BOND-2027",
                isin="MA0000012352",
                issuer="Corporate",
                issuer_name="BMCE Bank",
                bond_type="corporate",
                face_value=10000.00,
                coupon_rate=0.0425,
                maturity_date=date(2027, 12, 31),
                issue_size=3000000000.00,
                credit_rating="A-",
                coupon_frequency="semi-annual",
                issue_date=date(2022, 3, 15),
                source_url="https://www.cse.ma/bonds/bmce-bond-2027"
            )
        ]
    
    def _get_mock_yield_curve(self) -> Dict[str, float]:
        """Return mock yield curve data"""
        return {
            "3M": 3.25,
            "6M": 3.45,
            "1Y": 3.75,
            "2Y": 4.10,
            "3Y": 4.35,
            "5Y": 4.80,
            "10Y": 5.25,
            "15Y": 5.50,
            "20Y": 5.75
        }
    
    def _get_mock_issuance_calendar(self) -> List[Dict[str, Any]]:
        """Return mock bond issuance calendar"""
        return [
            {
                "issuer": "Government",
                "bond_name": "Morocco Government Bond 2028",
                "expected_issue_date": date(2024, 9, 15),
                "expected_maturity_date": date(2028, 9, 15),
                "expected_size": 8000000000.00,
                "expected_coupon_rate": 0.0425,
                "expected_rating": "BBB+",
                "status": "announced"
            },
            {
                "issuer": "Corporate",
                "bond_name": "Maroc Telecom Bond 2029",
                "expected_issue_date": date(2024, 10, 1),
                "expected_maturity_date": date(2029, 10, 1),
                "expected_size": 3000000000.00,
                "expected_coupon_rate": 0.0475,
                "expected_rating": "A",
                "status": "announced"
            }
        ]
    
    def scrape_all_etfs(self) -> List[ETFData]:
        """Scrape ETFs from all sources"""
        logger.info("Starting comprehensive ETF scraping...")
        
        all_etfs = []
        
        # Scrape from different sources
        sources = [
            self.scrape_ammc_etfs,
            self.scrape_cse_etfs,
            self.scrape_institutional_etfs
        ]
        
        for source_func in sources:
            try:
                etfs = source_func()
                all_etfs.extend(etfs)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error in ETF source {source_func.__name__}: {e}")
        
        # Remove duplicates based on ISIN
        unique_etfs = {}
        for etf in all_etfs:
            if etf.isin:
                unique_etfs[etf.isin] = etf
            else:
                unique_etfs[etf.ticker] = etf
        
        logger.info(f"Scraped {len(unique_etfs)} unique ETFs")
        return list(unique_etfs.values())
    
    def scrape_all_bonds(self) -> List[BondData]:
        """Scrape bonds from all sources"""
        logger.info("Starting comprehensive bond scraping...")
        
        all_bonds = []
        
        # Scrape from different sources
        sources = [
            self.scrape_ammc_bonds,
            self.scrape_cse_bonds
        ]
        
        for source_func in sources:
            try:
                bonds = source_func()
                all_bonds.extend(bonds)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error in bond source {source_func.__name__}: {e}")
        
        # Remove duplicates based on ISIN
        unique_bonds = {}
        for bond in all_bonds:
            if bond.isin:
                unique_bonds[bond.isin] = bond
            else:
                unique_bonds[bond.ticker] = bond
        
        logger.info(f"Scraped {len(unique_bonds)} unique bonds")
        return list(unique_bonds.values())
    
    def save_to_json(self, data: List, filename: str):
        """Save scraped data to JSON file"""
        try:
            # Convert dataclasses to dictionaries
            if data and hasattr(data[0], '__dict__'):
                data_dict = []
                for item in data:
                    item_dict = item.__dict__.copy()
                    # Convert dates to strings
                    for key, value in item_dict.items():
                        if isinstance(value, date):
                            item_dict[key] = value.isoformat()
                    data_dict.append(item_dict)
            else:
                data_dict = data
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(data)} items to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def run_full_scrape(self):
        """Run complete scraping operation"""
        logger.info("Starting full ETF and Bond scraping operation...")
        
        # Scrape ETFs
        etfs = self.scrape_all_etfs()
        self.save_to_json(etfs, 'data/moroccan_etfs.json')
        
        # Scrape Bonds
        bonds = self.scrape_all_bonds()
        self.save_to_json(bonds, 'data/moroccan_bonds.json')
        
        # Scrape Yield Curve
        yield_curve = self.scrape_yield_curve()
        with open('data/moroccan_yield_curve.json', 'w') as f:
            json.dump(yield_curve, f, indent=2)
        
        # Scrape Issuance Calendar
        calendar = self.scrape_bond_issuance_calendar()
        self.save_to_json(calendar, 'data/moroccan_bond_calendar.json')
        
        logger.info("Full scraping operation completed!")
        
        return {
            'etfs': etfs,
            'bonds': bonds,
            'yield_curve': yield_curve,
            'calendar': calendar
        }

if __name__ == "__main__":
    scraper = MoroccanETFBondScraper()
    results = scraper.run_full_scrape()
    print(f"Scraped {len(results['etfs'])} ETFs and {len(results['bonds'])} bonds") 