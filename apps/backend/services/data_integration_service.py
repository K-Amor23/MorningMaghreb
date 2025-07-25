#!/usr/bin/env python3
"""
Data Integration Service for Casablanca Insights

This service combines data from multiple sources:
1. African Markets (78 companies with comprehensive data)
2. Casablanca Bourse (official exchange data)
3. Bank Al Maghrib (economic data)
4. Morocco Financial (additional financial data)

Provides unified API endpoints for the website.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIntegrationService:
    """Service to integrate and provide unified access to all data sources"""
    
    def __init__(self, data_dir: str = "apps/backend/data"):
        self.data_dir = Path(data_dir)
        self.cache = {}
        self.last_updated = None
        
        # Data file paths
        self.african_markets_file = self.data_dir / "cse_companies_african_markets.json"
        self.bourse_data_file = Path("apps/backend/etl/casablanca_bourse_data_20250725_123947.json")
        self.bank_data_dir = self.data_dir / "bank_al_maghrib"
        self.morocco_financial_dir = self.data_dir / "morocco_financial"
        
        # Load all data on initialization
        self.load_all_data()
    
    def load_all_data(self):
        """Load and combine all data sources"""
        try:
            logger.info("Loading all data sources...")
            
            # Load African Markets data
            self.african_markets_data = self.load_african_markets_data()
            logger.info(f"Loaded {len(self.african_markets_data)} companies from African Markets")
            
            # Load Casablanca Bourse data
            self.bourse_data = self.load_bourse_data()
            logger.info(f"Loaded Bourse data with {len(self.bourse_data.get('market_data_pages', []))} pages")
            
            # Load Bank Al Maghrib data
            self.bank_data = self.load_bank_data()
            logger.info(f"Loaded Bank Al Maghrib data")
            
            # Load Morocco Financial data
            self.morocco_financial_data = self.load_morocco_financial_data()
            logger.info(f"Loaded Morocco Financial data")
            
            # Combine all data
            self.combined_data = self.combine_all_data()
            logger.info(f"Combined data ready with {len(self.combined_data['companies'])} companies")
            
            self.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def load_african_markets_data(self) -> List[Dict]:
        """Load African Markets company data"""
        try:
            if self.african_markets_file.exists():
                with open(self.african_markets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            else:
                logger.warning("African Markets data file not found")
                return []
        except Exception as e:
            logger.error(f"Error loading African Markets data: {e}")
            return []
    
    def load_bourse_data(self) -> Dict:
        """Load Casablanca Bourse data"""
        try:
            if self.bourse_data_file.exists():
                with open(self.bourse_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            else:
                logger.warning("Bourse data file not found")
                return {}
        except Exception as e:
            logger.error(f"Error loading Bourse data: {e}")
            return {}
    
    def load_bank_data(self) -> Dict:
        """Load Bank Al Maghrib data"""
        try:
            bank_data = {}
            if self.bank_data_dir.exists():
                for file_path in self.bank_data_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            bank_data[file_path.stem] = data
                    except Exception as e:
                        logger.warning(f"Error loading {file_path}: {e}")
            return bank_data
        except Exception as e:
            logger.error(f"Error loading Bank data: {e}")
            return {}
    
    def load_morocco_financial_data(self) -> Dict:
        """Load Morocco Financial data"""
        try:
            morocco_data = {}
            if self.morocco_financial_dir.exists():
                for file_path in self.morocco_financial_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            morocco_data[file_path.stem] = data
                    except Exception as e:
                        logger.warning(f"Error loading {file_path}: {e}")
            return morocco_data
        except Exception as e:
            logger.error(f"Error loading Morocco Financial data: {e}")
            return {}
    
    def combine_all_data(self) -> Dict:
        """Combine all data sources into unified structure"""
        combined = {
            'metadata': {
                'combined_at': datetime.now().isoformat(),
                'sources': ['African Markets', 'Casablanca Bourse', 'Bank Al Maghrib', 'Morocco Financial'],
                'total_companies': 0,
                'data_quality': {}
            },
            'companies': {},
            'indices': {},
            'economic_data': {},
            'market_summary': {}
        }
        
        # Process African Markets data
        for company in self.african_markets_data:
            ticker = company.get('ticker', '').upper()
            if ticker:
                combined['companies'][ticker] = {
                    'african_markets': company,
                    'data_sources': ['african_markets'],
                    'last_updated': company.get('last_updated'),
                    'completeness_score': self.calculate_completeness_score(company)
                }
        
        # Process Bourse data
        if self.bourse_data:
            # Extract indices
            for page in self.bourse_data.get('market_data_pages', []):
                for table in page.get('tables', []):
                    for row in table.get('data', []):
                        if 'MASI' in row:
                            combined['indices'][list(row.keys())[0]] = {
                                'value': list(row.values())[0],
                                'source': 'casablanca_bourse'
                            }
            
            # Extract company data from Bourse tables
            for page in self.bourse_data.get('market_data_pages', []):
                for table in page.get('tables', []):
                    for row in table.get('data', []):
                        if 'Ticker' in row:
                            ticker = row['Ticker'].upper()
                            if ticker not in combined['companies']:
                                combined['companies'][ticker] = {
                                    'bourse_data': row,
                                    'data_sources': ['casablanca_bourse'],
                                    'completeness_score': 0.3  # Basic data only
                                }
                            else:
                                combined['companies'][ticker]['bourse_data'] = row
                                combined['companies'][ticker]['data_sources'].append('casablanca_bourse')
        
        # Process Bank Al Maghrib data
        if self.bank_data:
            combined['economic_data']['bank_al_maghrib'] = self.bank_data
        
        # Process Morocco Financial data
        if self.morocco_financial_data:
            combined['economic_data']['morocco_financial'] = self.morocco_financial_data
        
        # Calculate totals and quality metrics
        combined['metadata']['total_companies'] = len(combined['companies'])
        combined['metadata']['data_quality'] = self.calculate_data_quality(combined['companies'])
        
        # Create market summary
        combined['market_summary'] = self.create_market_summary(combined['companies'])
        
        return combined
    
    def calculate_completeness_score(self, company_data: Dict) -> float:
        """Calculate data completeness score (0-1) for a company"""
        required_fields = ['ticker', 'name', 'sector', 'price', 'market_cap_billion']
        optional_fields = ['change_1d_percent', 'change_ytd_percent', 'size_category', 'sector_group']
        
        score = 0.0
        total_fields = len(required_fields) + len(optional_fields)
        
        # Required fields (weighted more heavily)
        for field in required_fields:
            if company_data.get(field) is not None:
                score += 0.8 / len(required_fields)
        
        # Optional fields
        for field in optional_fields:
            if company_data.get(field) is not None:
                score += 0.2 / len(optional_fields)
        
        return min(score, 1.0)
    
    def calculate_data_quality(self, companies: Dict) -> Dict:
        """Calculate overall data quality metrics"""
        total_companies = len(companies)
        if total_companies == 0:
            return {}
        
        completeness_scores = [company.get('completeness_score', 0) for company in companies.values()]
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        
        # Count companies by data source
        source_counts = {}
        for company in companies.values():
            for source in company.get('data_sources', []):
                source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            'total_companies': total_companies,
            'average_completeness': round(avg_completeness, 3),
            'companies_with_price_data': sum(1 for c in companies.values() if c.get('african_markets', {}).get('price')),
            'companies_with_market_cap': sum(1 for c in companies.values() if c.get('african_markets', {}).get('market_cap_billion')),
            'source_coverage': source_counts
        }
    
    def create_market_summary(self, companies: Dict) -> Dict:
        """Create market summary statistics"""
        if not companies:
            return {}
        
        # Calculate market statistics
        prices = []
        market_caps = []
        sectors = {}
        
        for company in companies.values():
            african_data = company.get('african_markets', {})
            
            if african_data.get('price'):
                prices.append(african_data['price'])
            
            if african_data.get('market_cap_billion'):
                market_caps.append(african_data['market_cap_billion'])
            
            sector = african_data.get('sector')
            if sector:
                sectors[sector] = sectors.get(sector, 0) + 1
        
        return {
            'total_companies': len(companies),
            'total_market_cap': sum(market_caps) if market_caps else None,
            'average_price': sum(prices) / len(prices) if prices else None,
            'price_range': {
                'min': min(prices) if prices else None,
                'max': max(prices) if prices else None
            },
            'sector_distribution': sectors,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    # API Methods for Website Integration
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies with unified data"""
        return list(self.combined_data['companies'].values())
    
    def get_company(self, ticker: str) -> Optional[Dict]:
        """Get specific company data"""
        return self.combined_data['companies'].get(ticker.upper())
    
    def get_market_summary(self) -> Dict:
        """Get market summary statistics"""
        return self.combined_data['market_summary']
    
    def get_indices(self) -> Dict:
        """Get market indices"""
        return self.combined_data['indices']
    
    def get_economic_data(self) -> Dict:
        """Get economic data"""
        return self.combined_data['economic_data']
    
    def get_companies_by_sector(self, sector: str) -> List[Dict]:
        """Get companies filtered by sector"""
        sector_companies = []
        for company in self.combined_data['companies'].values():
            african_data = company.get('african_markets', {})
            if african_data.get('sector', '').lower() == sector.lower():
                sector_companies.append(company)
        return sector_companies
    
    def get_top_companies(self, limit: int = 10, sort_by: str = 'market_cap_billion') -> List[Dict]:
        """Get top companies by specified criteria"""
        companies = []
        for company in self.combined_data['companies'].values():
            african_data = company.get('african_markets', {})
            if african_data.get(sort_by) is not None:
                companies.append(company)
        
        # Sort by specified criteria
        companies.sort(key=lambda x: x.get('african_markets', {}).get(sort_by, 0), reverse=True)
        return companies[:limit]
    
    def get_data_quality_report(self) -> Dict:
        """Get data quality report"""
        return {
            'metadata': self.combined_data['metadata'],
            'quality_metrics': self.combined_data['metadata']['data_quality'],
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def get_missing_data_report(self) -> Dict:
        """Get report of missing data"""
        missing_data = {
            'companies_without_price': [],
            'companies_without_market_cap': [],
            'companies_without_sector': [],
            'low_completeness_companies': []
        }
        
        for ticker, company in self.combined_data['companies'].items():
            african_data = company.get('african_markets', {})
            
            if not african_data.get('price'):
                missing_data['companies_without_price'].append(ticker)
            
            if not african_data.get('market_cap_billion'):
                missing_data['companies_without_market_cap'].append(ticker)
            
            if not african_data.get('sector'):
                missing_data['companies_without_sector'].append(ticker)
            
            if company.get('completeness_score', 0) < 0.5:
                missing_data['low_completeness_companies'].append(ticker)
        
        return missing_data

# Global instance for easy access
data_service = DataIntegrationService()

if __name__ == "__main__":
    # Test the service
    service = DataIntegrationService()
    
    print("🎯 Data Integration Service Test")
    print("=" * 50)
    
    print(f"Total companies: {len(service.get_all_companies())}")
    print(f"Market summary: {service.get_market_summary()}")
    print(f"Data quality: {service.get_data_quality_report()}")
    
    # Test specific company
    test_company = service.get_company("ATW")
    if test_company:
        print(f"ATW data: {test_company}")
    
    # Test missing data report
    missing_data = service.get_missing_data_report()
    print(f"Missing data report: {missing_data}") 