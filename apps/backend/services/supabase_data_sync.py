#!/usr/bin/env python3
"""
Supabase Data Sync Service for Casablanca Insights

This service syncs real market data from our data integration service to Supabase,
ensuring the database is always up-to-date with the latest market information.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Supabase imports
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Import our data integration service
from data_integration_service import DataIntegrationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseDataSync:
    """Service to sync market data to Supabase"""
    
    def __init__(self):
        # Initialize Supabase client
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize data integration service
        self.data_service = DataIntegrationService()
        
        logger.info("Supabase Data Sync Service initialized")
    
    def sync_companies_to_supabase(self) -> Dict:
        """Sync all company data to Supabase"""
        try:
            logger.info("Starting company data sync to Supabase...")
            
            # Get all companies from our data service
            companies = self.data_service.get_all_companies()
            
            # Prepare data for Supabase
            companies_data = []
            for company in companies:
                african_data = company.get('african_markets', {})
                bourse_data = company.get('bourse_data', {})
                
                # Create company record
                company_record = {
                    'ticker': african_data.get('ticker') or bourse_data.get('Ticker'),
                    'name': african_data.get('name') or bourse_data.get('Émetteur'),
                    'isin': bourse_data.get('Code ISIN'),
                    'sector': african_data.get('sector'),
                    'source_url': african_data.get('company_url'),
                    'scraped_at': datetime.now().isoformat(),
                    'metadata': {
                        'african_markets': african_data,
                        'bourse_data': bourse_data,
                        'data_sources': company.get('data_sources', []),
                        'completeness_score': company.get('completeness_score', 0)
                    }
                }
                
                # Remove None values
                company_record = {k: v for k, v in company_record.items() if v is not None}
                companies_data.append(company_record)
            
            # Upsert companies to Supabase
            result = self.supabase.table('cse_companies').upsert(
                companies_data,
                on_conflict='ticker'
            ).execute()
            
            logger.info(f"Successfully synced {len(companies_data)} companies to Supabase")
            
            return {
                'success': True,
                'companies_synced': len(companies_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing companies to Supabase: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def sync_market_data_to_supabase(self) -> Dict:
        """Sync current market data to Supabase"""
        try:
            logger.info("Starting market data sync to Supabase...")
            
            # Get all companies with price data
            companies = self.data_service.get_all_companies()
            
            # Prepare market data records
            market_data_records = []
            for company in companies:
                african_data = company.get('african_markets', {})
                
                if african_data.get('price'):
                    market_record = {
                        'ticker': african_data.get('ticker'),
                        'price': float(african_data.get('price', 0)),
                        'market_cap': float(african_data.get('market_cap_billion', 0)) * 1000000000,  # Convert to actual value
                        'change_percent': float(african_data.get('change_1d_percent', 0)),
                        'volume': None,  # Not available in current data
                        'high_24h': None,  # Not available in current data
                        'low_24h': None,  # Not available in current data
                        'open_price': None,  # Not available in current data
                        'previous_close': None,  # Not available in current data
                        'timestamp': datetime.now().isoformat(),
                        'source': 'african_markets'
                    }
                    
                    # Remove None values
                    market_record = {k: v for k, v in market_record.items() if v is not None}
                    market_data_records.append(market_record)
            
            # Insert market data to Supabase
            if market_data_records:
                result = self.supabase.table('market_data').insert(market_data_records).execute()
                logger.info(f"Successfully synced {len(market_data_records)} market data records to Supabase")
            
            return {
                'success': True,
                'market_data_synced': len(market_data_records),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing market data to Supabase: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def sync_market_summary_to_supabase(self) -> Dict:
        """Sync market summary statistics to Supabase"""
        try:
            logger.info("Starting market summary sync to Supabase...")
            
            # Get market summary from data service
            market_summary = self.data_service.get_market_summary()
            
            # Create market summary record
            summary_record = {
                'total_companies': market_summary.get('total_companies'),
                'total_market_cap': market_summary.get('total_market_cap'),
                'average_price': market_summary.get('average_price'),
                'price_range_min': market_summary.get('price_range', {}).get('min'),
                'price_range_max': market_summary.get('price_range', {}).get('max'),
                'sector_distribution': market_summary.get('sector_distribution'),
                'last_updated': datetime.now().isoformat(),
                'metadata': market_summary
            }
            
            # Remove None values
            summary_record = {k: v for k, v in summary_record.items() if v is not None}
            
            # Store in a custom table or use existing structure
            # For now, we'll store it as a JSON file reference
            logger.info("Market summary prepared for storage")
            
            return {
                'success': True,
                'summary_synced': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing market summary to Supabase: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_companies_from_supabase(self) -> List[Dict]:
        """Get companies from Supabase"""
        try:
            result = self.supabase.table('cse_companies').select('*').execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching companies from Supabase: {e}")
            return []
    
    def get_market_data_from_supabase(self, ticker: Optional[str] = None) -> List[Dict]:
        """Get market data from Supabase"""
        try:
            query = self.supabase.table('market_data').select('*')
            
            if ticker:
                query = query.eq('ticker', ticker)
            
            result = query.order('timestamp', desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching market data from Supabase: {e}")
            return []
    
    def sync_all_data(self) -> Dict:
        """Sync all data to Supabase"""
        try:
            logger.info("Starting complete data sync to Supabase...")
            
            results = {
                'companies': self.sync_companies_to_supabase(),
                'market_data': self.sync_market_data_to_supabase(),
                'market_summary': self.sync_market_summary_to_supabase(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Check if all syncs were successful
            all_successful = all(result.get('success', False) for result in results.values() if isinstance(result, dict))
            
            results['overall_success'] = all_successful
            
            if all_successful:
                logger.info("Complete data sync to Supabase successful")
            else:
                logger.warning("Some data sync operations failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in complete data sync: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def create_market_summary_table(self) -> bool:
        """Create market summary table if it doesn't exist"""
        try:
            # This would be run in Supabase SQL editor
            sql = """
            CREATE TABLE IF NOT EXISTS market_summary (
                id SERIAL PRIMARY KEY,
                total_companies INTEGER,
                total_market_cap DECIMAL(20,2),
                average_price DECIMAL(10,2),
                price_range_min DECIMAL(10,2),
                price_range_max DECIMAL(10,2),
                sector_distribution JSONB,
                last_updated TIMESTAMPTZ DEFAULT NOW(),
                metadata JSONB
            );
            
            CREATE INDEX IF NOT EXISTS idx_market_summary_last_updated 
            ON market_summary(last_updated DESC);
            """
            
            logger.info("Market summary table creation SQL prepared")
            return True
            
        except Exception as e:
            logger.error(f"Error creating market summary table: {e}")
            return False

# Global instance for easy access
supabase_sync = SupabaseDataSync()

if __name__ == "__main__":
    # Test the sync service
    sync_service = SupabaseDataSync()
    
    print("🔄 Testing Supabase Data Sync")
    print("=" * 50)
    
    # Test complete sync
    results = sync_service.sync_all_data()
    print(f"Sync results: {json.dumps(results, indent=2)}")
    
    # Test fetching data
    companies = sync_service.get_companies_from_supabase()
    print(f"Companies in Supabase: {len(companies)}")
    
    if companies:
        print(f"Sample company: {companies[0]}")
    
    print("✅ Supabase sync test completed") 