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
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                etfs = []
                
                # Look for ETF listings
                etf_elements = soup.find_all(['div', 'table'], class_=re.compile(r'etf|fund|product', re.I))
                
                for elem in etf_elements:
                    try:
                        # Extract ETF information
                        name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                        ticker_elem = elem.find(text=re.compile(r'[A-Z]{2,6}', re.I))
                        
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            ticker = ticker_elem.strip() if ticker_elem else name[:4].upper()
                            
                            etf = ETFData(
                                name=name,
                                ticker=ticker,
                                isin=None,
                                underlying_index=None,
                                issuer="AMMC",
                                expense_ratio=None,
                                inception_date=None,
                                listing_date=None,
                                asset_class="Equity",
                                geographic_focus="Morocco",
                                sector_focus=None,
                                source_url=url
                            )
                            
                            etfs.append(etf)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing ETF element: {e}")
                        continue
                
                logger.info(f"Scraped {len(etfs)} ETFs from AMMC")
                return etfs
                
            else:
                logger.warning(f"AMMC ETF page returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping AMMC ETFs: {e}")
            return []
    
    def scrape_cse_etfs(self) -> List[ETFData]:
        """Scrape ETF data from Casablanca Stock Exchange"""
        logger.info("Scraping ETF data from CSE...")
        
        try:
            # CSE ETF page
            url = f"{self.sources['cse']}/fr/etfs"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                etfs = []
                
                # Look for ETF listings
                etf_elements = soup.find_all(['div', 'table'], class_=re.compile(r'etf|fund|product', re.I))
                
                for elem in etf_elements:
                    try:
                        # Extract ETF information
                        name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                        ticker_elem = elem.find(text=re.compile(r'[A-Z]{2,6}', re.I))
                        
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            ticker = ticker_elem.strip() if ticker_elem else name[:4].upper()
                            
                            etf = ETFData(
                                name=name,
                                ticker=ticker,
                                isin=None,
                                underlying_index=None,
                                issuer="CSE",
                                expense_ratio=None,
                                inception_date=None,
                                listing_date=None,
                                asset_class="Equity",
                                geographic_focus="Morocco",
                                sector_focus=None,
                                source_url=url
                            )
                            
                            etfs.append(etf)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing ETF element: {e}")
                        continue
                
                logger.info(f"Scraped {len(etfs)} ETFs from CSE")
                return etfs
                
            else:
                logger.warning(f"CSE ETF page returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping CSE ETFs: {e}")
            return []
    
    def scrape_bonds(self) -> List[BondData]:
        """Scrape bond data from various sources"""
        logger.info("Scraping bond data...")
        
        bonds = []
        
        try:
            # Try to scrape from CDG Capital
            cdg_bonds = self.scrape_cdg_bonds()
            bonds.extend(cdg_bonds)
            
            # Try to scrape from Attijari Finance
            attijari_bonds = self.scrape_attijari_bonds()
            bonds.extend(attijari_bonds)
            
            # Try to scrape from BMCE Capital
            bmce_bonds = self.scrape_bmce_bonds()
            bonds.extend(bmce_bonds)
            
            logger.info(f"Total bonds scraped: {len(bonds)}")
            
        except Exception as e:
            logger.error(f"Error scraping bonds: {e}")
        
        return bonds
    
    def scrape_cdg_bonds(self) -> List[BondData]:
        """Scrape bond data from CDG Capital"""
        logger.info("Scraping bonds from CDG Capital...")
        
        try:
            url = f"{self.sources['cdg_capital']}/fr/obligations"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                bonds = []
                
                # Look for bond listings
                bond_elements = soup.find_all(['div', 'table'], class_=re.compile(r'bond|obligation|debt', re.I))
                
                for elem in bond_elements:
                    try:
                        # Extract bond information
                        name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                        ticker_elem = elem.find(text=re.compile(r'[A-Z]{2,6}', re.I))
                        
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            ticker = ticker_elem.strip() if ticker_elem else name[:4].upper()
                            
                            bond = BondData(
                                name=name,
                                ticker=ticker,
                                isin=None,
                                issuer="CDG Capital",
                                issuer_name="CDG Capital",
                                bond_type="Corporate",
                                face_value=1000.0,
                                coupon_rate=None,
                                maturity_date=date(2030, 12, 31),
                                issue_size=None,
                                credit_rating=None,
                                source_url=url
                            )
                            
                            bonds.append(bond)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing bond element: {e}")
                        continue
                
                logger.info(f"Scraped {len(bonds)} bonds from CDG Capital")
                return bonds
                
            else:
                logger.warning(f"CDG Capital bonds page returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping CDG Capital bonds: {e}")
            return []
    
    def scrape_attijari_bonds(self) -> List[BondData]:
        """Scrape bond data from Attijari Finance"""
        logger.info("Scraping bonds from Attijari Finance...")
        
        try:
            url = f"{self.sources['attijari_finance']}/fr/obligations"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                bonds = []
                
                # Look for bond listings
                bond_elements = soup.find_all(['div', 'table'], class_=re.compile(r'bond|obligation|debt', re.I))
                
                for elem in bond_elements:
                    try:
                        # Extract bond information
                        name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                        ticker_elem = elem.find(text=re.compile(r'[A-Z]{2,6}', re.I))
                        
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            ticker = ticker_elem.strip() if ticker_elem else name[:4].upper()
                            
                            bond = BondData(
                                name=name,
                                ticker=ticker,
                                isin=None,
                                issuer="Attijari Finance",
                                issuer_name="Attijari Finance",
                                bond_type="Corporate",
                                face_value=1000.0,
                                coupon_rate=None,
                                maturity_date=date(2030, 12, 31),
                                issue_size=None,
                                credit_rating=None,
                                source_url=url
                            )
                            
                            bonds.append(bond)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing bond element: {e}")
                        continue
                
                logger.info(f"Scraped {len(bonds)} bonds from Attijari Finance")
                return bonds
                
            else:
                logger.warning(f"Attijari Finance bonds page returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping Attijari Finance bonds: {e}")
            return []
    
    def scrape_bmce_bonds(self) -> List[BondData]:
        """Scrape bond data from BMCE Capital"""
        logger.info("Scraping bonds from BMCE Capital...")
        
        try:
            url = f"{self.sources['bmce_capital']}/fr/obligations"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                bonds = []
                
                # Look for bond listings
                bond_elements = soup.find_all(['div', 'table'], class_=re.compile(r'bond|obligation|debt', re.I))
                
                for elem in bond_elements:
                    try:
                        # Extract bond information
                        name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                        ticker_elem = elem.find(text=re.compile(r'[A-Z]{2,6}', re.I))
                        
                        if name_elem:
                            name = name_elem.get_text(strip=True)
                            ticker = ticker_elem.strip() if ticker_elem else name[:4].upper()
                            
                            bond = BondData(
                                name=name,
                                ticker=ticker,
                                isin=None,
                                issuer="BMCE Capital",
                                issuer_name="BMCE Capital",
                                bond_type="Corporate",
                                face_value=1000.0,
                                coupon_rate=None,
                                maturity_date=date(2030, 12, 31),
                                issue_size=None,
                                credit_rating=None,
                                source_url=url
                            )
                            
                            bonds.append(bond)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing bond element: {e}")
                        continue
                
                logger.info(f"Scraped {len(bonds)} bonds from BMCE Capital")
                return bonds
                
            else:
                logger.warning(f"BMCE Capital bonds page returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error scraping BMCE Capital bonds: {e}")
            return []
    
    def scrape_all_data(self) -> Dict[str, List]:
        """Scrape all ETF and bond data"""
        logger.info("Starting comprehensive ETF and bond data scraping...")
        
        all_data = {
            'etfs': [],
            'bonds': [],
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'sources': list(self.sources.keys())
            }
        }
        
        try:
            # Scrape ETFs
            ammc_etfs = self.scrape_ammc_etfs()
            cse_etfs = self.scrape_cse_etfs()
            
            all_data['etfs'].extend(ammc_etfs)
            all_data['etfs'].extend(cse_etfs)
            
            # Scrape bonds
            bonds = self.scrape_bonds()
            all_data['bonds'] = bonds
            
            logger.info(f"✅ Comprehensive scraping completed!")
            logger.info(f"   - ETFs: {len(all_data['etfs'])}")
            logger.info(f"   - Bonds: {len(all_data['bonds'])}")
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive scraping: {e}")
        
        return all_data
    
    def export_data(self, data: Dict[str, List], output_dir: str = "data/etf_bonds") -> str:
        """Export scraped data to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"etf_bond_data_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Data exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise

def main():
    """Main function for testing"""
    scraper = MoroccanETFBondScraper()
    data = scraper.scrape_all_data()
    
    if data['etfs'] or data['bonds']:
        output_dir = "data/etf_bonds"
        filepath = scraper.export_data(data, output_dir)
        print(f"✅ Scraping completed! Data exported to {filepath}")
        print(f"   - ETFs: {len(data['etfs'])}")
        print(f"   - Bonds: {len(data['bonds'])}")
    else:
        print("❌ No data was scraped.")

if __name__ == "__main__":
    main()
