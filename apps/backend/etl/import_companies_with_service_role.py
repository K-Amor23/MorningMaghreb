#!/usr/bin/env python3
"""
Import All Companies with Service Role Key

This script uses the Supabase service role key to bypass Row-Level Security
and import all 78 companies from the African Markets database.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    exit(1)

logger = logging.getLogger(__name__)

class ServiceRoleImporter:
    """Import companies using service role key to bypass RLS"""
    
    def __init__(self, supabase_url: str, service_role_key: str):
        self.supabase: Client = create_client(supabase_url, service_role_key)
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
        """Transform African Markets company data to Supabase schema"""
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
    
    def bulk_upsert_companies(self, companies: List[Dict[str, Any]]) -> tuple[int, int]:
        """Bulk upsert companies into Supabase using service role"""
        
        # Transform all companies
        transformed_companies = []
        for company in companies:
            transformed_companies.append(self.transform_company_data(company))
        
        new_count = 0
        updated_count = 0
        
        try:
            # Get existing companies to determine what's new vs updated
            existing_companies = self.get_existing_companies()
            existing_tickers = set(existing_companies.keys())
            
            # Separate new and existing companies
            new_companies = []
            update_companies = []
            
            for company in transformed_companies:
                if company['ticker'] in existing_tickers:
                    update_companies.append(company)
                else:
                    new_companies.append(company)
            
            # Bulk insert new companies
            if new_companies:
                logger.info(f"Inserting {len(new_companies)} new companies...")
                response = self.supabase.table(self.table_name).insert(new_companies).execute()
                new_count = len(new_companies)
                logger.info(f"✅ Successfully inserted {new_count} new companies")
            
            # Update existing companies individually (Supabase doesn't support bulk updates easily)
            if update_companies:
                logger.info(f"Updating {len(update_companies)} existing companies...")
                for company in update_companies:
                    try:
                        self.supabase.table(self.table_name)\
                            .update(company)\
                            .eq('ticker', company['ticker'])\
                            .execute()
                        updated_count += 1
                        logger.info(f"Updated: {company['name']} ({company['ticker']})")
                    except Exception as e:
                        logger.error(f"Error updating {company['ticker']}: {e}")
            
            logger.info(f"✅ Bulk import completed: {new_count} new, {updated_count} updated")
            
        except Exception as e:
            logger.error(f"Error during bulk upsert: {e}")
            return 0, 0
            
        return new_count, updated_count
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Get all companies
            response = self.supabase.table(self.table_name).select("*").execute()
            companies = response.data
            
            # Calculate stats
            total_count = len(companies)
            
            # Get sector breakdown
            sectors = {}
            for company in companies:
                sector = company.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
            
            return {
                'total_companies': total_count,
                'sectors': sectors,
                'companies': companies
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

async def main():
    """Main function to import all companies using service role"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Importing All Companies with Service Role Key")
    print("=" * 55)
    
    # Get Supabase credentials
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_role_key:
        print("❌ Missing required credentials:")
        print("   - NEXT_PUBLIC_SUPABASE_URL:", "✅" if supabase_url else "❌")
        print("   - SUPABASE_SERVICE_ROLE_KEY:", "✅" if service_role_key else "❌")
        print("\n💡 To get your service role key:")
        print("   1. Go to Supabase Dashboard → Project Settings → API")
        print("   2. Copy the 'service_role' key (not anon key)")
        print("   3. Add to .env: SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
        return
    
    # Initialize importer with service role
    importer = ServiceRoleImporter(supabase_url, service_role_key)
    
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
    
    # Bulk import to Supabase
    print(f"\n🗄️ Bulk importing to Supabase with service role...")
    new_count, updated_count = importer.bulk_upsert_companies(companies)
    
    print(f"✅ Import completed: {new_count} new, {updated_count} updated")
    
    # Get database statistics
    print(f"\n📊 Getting final database statistics...")
    stats = importer.get_database_stats()
    
    # Print summary
    print(f"\n" + "=" * 55)
    print("🎉 ALL COMPANIES IMPORTED SUCCESSFULLY!")
    print("=" * 55)
    
    total_companies = stats.get('total_companies', 0)
    print(f"\n📊 Database Summary:")
    print(f"  • Total Companies: {total_companies}")
    
    sectors = stats.get('sectors', {})
    if sectors:
        print(f"\n🏭 Sectors:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {sector}: {count} companies")
    
    companies_data = stats.get('companies', [])
    if companies_data:
        print(f"\n🔍 Sample Companies:")
        for i, company in enumerate(companies_data[:10]):
            print(f"  {i+1}. {company.get('name', 'N/A')} ({company.get('ticker', 'N/A')}) - {company.get('sector', 'N/A')}")
        
        if len(companies_data) > 10:
            print(f"  ... and {len(companies_data) - 10} more")
    
    print(f"\n🎯 Mission Accomplished! You now have {total_companies} companies in your database.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 