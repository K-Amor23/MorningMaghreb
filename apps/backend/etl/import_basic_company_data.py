#!/usr/bin/env python3
"""
Import Basic Company Data to Supabase

This script imports the basic company data (name, ticker, sector) 
from the African Markets database to match the existing Supabase schema.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    exit(1)

logger = logging.getLogger(__name__)

class BasicCompanyImporter:
    """Import basic company data to Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table_name = "cse_companies"
        
    def load_african_markets_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load African Markets data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            companies = data.get('companies', [])
            metadata = data.get('metadata', {})
            
            logger.info(f"Loaded {len(companies)} companies from African Markets")
            logger.info(f"Source: {metadata.get('source', 'Unknown')}")
            logger.info(f"Scraped at: {metadata.get('scraped_at', 'Unknown')}")
            
            return companies
            
        except Exception as e:
            logger.error(f"Error loading African Markets data: {e}")
            return []
    
    def transform_company_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Transform African Markets company data to basic Supabase schema"""
        return {
            'name': company.get('name', ''),
            'ticker': company.get('ticker', ''),
            'sector': company.get('sector', ''),
            'source_url': company.get('url', ''),
            'scraped_at': company.get('scraped_at', datetime.now().isoformat())
        }
    
    def get_existing_companies(self) -> Dict[str, Dict]:
        """Get existing companies from Supabase"""
        try:
            response = self.supabase.table(self.table_name).select("*").execute()
            
            companies = {}
            for row in response.data:
                companies[row['ticker']] = row
            
            logger.info(f"Found {len(companies)} existing companies in Supabase")
            return companies
            
        except Exception as e:
            logger.error(f"Error getting existing companies: {e}")
            return {}
    
    def upsert_companies(self, companies: List[Dict[str, Any]]) -> tuple[int, int, int]:
        """Upsert companies into Supabase"""
        existing_companies = self.get_existing_companies()
        
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        
        try:
            for company in companies:
                transformed_company = self.transform_company_data(company)
                ticker = transformed_company['ticker']
                
                if ticker in existing_companies:
                    # Update existing company
                    try:
                        # Only update if there are actual changes
                        existing = existing_companies[ticker]
                        needs_update = (
                            existing.get('name') != transformed_company['name'] or
                            existing.get('sector') != transformed_company['sector'] or
                            existing.get('source_url') != transformed_company['source_url']
                        )
                        
                        if needs_update:
                            self.supabase.table(self.table_name)\
                                .update(transformed_company)\
                                .eq('ticker', ticker)\
                                .execute()
                            updated_count += 1
                            logger.info(f"Updated: {transformed_company['name']} ({ticker})")
                        else:
                            unchanged_count += 1
                            logger.debug(f"No changes: {transformed_company['name']} ({ticker})")
                    except Exception as e:
                        logger.error(f"Error updating {ticker}: {e}")
                        unchanged_count += 1
                else:
                    # Insert new company
                    try:
                        self.supabase.table(self.table_name)\
                            .insert(transformed_company)\
                            .execute()
                        new_count += 1
                        logger.info(f"Added: {transformed_company['name']} ({ticker})")
                    except Exception as e:
                        logger.error(f"Error inserting {ticker}: {e}")
                        unchanged_count += 1
            
            logger.info(f"Import completed: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
            
        except Exception as e:
            logger.error(f"Error during upsert: {e}")
            
        return new_count, updated_count, unchanged_count
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Get total count
            response = self.supabase.table(self.table_name).select("*").execute()
            total_count = len(response.data)
            
            # Get sector breakdown
            response = self.supabase.table(self.table_name)\
                .select("sector")\
                .not_.is_("sector", "null")\
                .execute()
            
            sectors = {}
            for row in response.data:
                sector = row['sector']
                sectors[sector] = sectors.get(sector, 0) + 1
            
            return {
                'total_companies': total_count,
                'sectors': sectors
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

async def main():
    """Main function to import basic company data"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Importing Basic Company Data to Supabase")
    print("=" * 50)
    
    # Get Supabase credentials
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        print("Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY")
        return
    
    # Initialize importer
    importer = BasicCompanyImporter(supabase_url, supabase_key)
    
    # Load African Markets data
    data_file = Path("apps/backend/data/cse_companies_african_markets_database.json")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    print(f"\n📁 Loading data from: {data_file}")
    companies = importer.load_african_markets_data(str(data_file))
    
    if not companies:
        print("❌ No companies loaded. Exiting.")
        return
    
    print(f"✅ Loaded {len(companies)} companies")
    
    # Import to Supabase
    print(f"\n🗄️ Importing to Supabase...")
    new_count, updated_count, unchanged_count = importer.upsert_companies(companies)
    
    print(f"✅ Import completed: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
    
    # Get database statistics
    print(f"\n📊 Getting database statistics...")
    stats = importer.get_database_stats()
    
    # Print summary
    print(f"\n" + "=" * 50)
    print("🎉 BASIC COMPANY DATA IMPORT COMPLETE!")
    print("=" * 50)
    
    print(f"\n📊 Database Summary:")
    print(f"  • Total Companies: {stats.get('total_companies', 0)}")
    
    sectors = stats.get('sectors', {})
    if sectors:
        print(f"\n🏭 Sectors:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {sector}: {count} companies")
    
    print(f"\n🔍 Sample Companies:")
    for i, company in enumerate(companies[:10]):
        print(f"  {i+1}. {company['name']} ({company['ticker']}) - {company['sector']}")
    
    if len(companies) > 10:
        print(f"  ... and {len(companies) - 10} more")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 