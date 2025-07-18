#!/usr/bin/env python3
"""
Casablanca Stock Exchange Database Initialization for Supabase

This script:
1. Scrapes company data from CSE website
2. Normalizes and validates the data
3. Upserts into Supabase database
4. Provides a summary report
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys
import os
import csv

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from etl.cse_company_scraper import CSEScraper, CSECompany

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)

logger = logging.getLogger(__name__)

class SupabaseCSEManager:
    """Manages CSE company database operations with Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table_name = "cse_companies"
    
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
    
    def upsert_companies(self, companies: List[CSECompany]) -> Tuple[int, int, int]:
        """Upsert companies into Supabase and return counts"""
        existing_companies = self.get_existing_companies()
        
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        
        try:
            for company in companies:
                company_dict = company.to_dict()
                
                if company.ticker in existing_companies:
                    # Check if company needs updating
                    existing = existing_companies[company.ticker]
                    needs_update = self._company_needs_update(existing, company_dict)
                    
                    if needs_update:
                        # Update existing company
                        response = self.supabase.table(self.table_name)\
                            .update({
                                'name': company.name,
                                'isin': company.isin,
                                'sector': company.sector,
                                'listing_date': company.listing_date.isoformat() if company.listing_date else None,
                                'source_url': company.source_url,
                                'scraped_at': company.scraped_at.isoformat() if company.scraped_at else None,
                                'updated_at': datetime.now().isoformat()
                            })\
                            .eq('ticker', company.ticker)\
                            .execute()
                        
                        updated_count += 1
                        logger.info(f"Updated company: {company.name} ({company.ticker})")
                    else:
                        unchanged_count += 1
                        logger.debug(f"No changes for company: {company.name} ({company.ticker})")
                else:
                    # Insert new company
                    response = self.supabase.table(self.table_name)\
                        .insert({
                            'name': company.name,
                            'ticker': company.ticker,
                            'isin': company.isin,
                            'sector': company.sector,
                            'listing_date': company.listing_date.isoformat() if company.listing_date else None,
                            'source_url': company.source_url,
                            'scraped_at': company.scraped_at.isoformat() if company.scraped_at else None
                        })\
                        .execute()
                    
                    new_count += 1
                    logger.info(f"Added new company: {company.name} ({company.ticker})")
            
            logger.info(f"Supabase update completed: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
                
        except Exception as e:
            logger.error(f"Error upserting companies: {e}")
            return 0, 0, 0
        
        return new_count, updated_count, unchanged_count
    
    def _company_needs_update(self, existing: Dict, new: Dict) -> bool:
        """Check if company data needs updating"""
        fields_to_check = ['name', 'isin', 'sector', 'listing_date', 'source_url']
        
        for field in fields_to_check:
            existing_val = existing.get(field)
            new_val = new.get(field)
            
            # Handle date comparison
            if field == 'listing_date':
                if existing_val and new_val:
                    # Convert to date objects for comparison
                    existing_date = existing_val.split('T')[0] if isinstance(existing_val, str) else existing_val
                    new_date = new_val.split('T')[0] if isinstance(new_val, str) else new_val
                    if existing_date != new_date:
                        return True
                elif existing_val != new_val:
                    return True
            else:
                if existing_val != new_val:
                    return True
        
        return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics from Supabase"""
        try:
            # Get company stats using the function
            response = self.supabase.rpc('get_cse_company_stats').execute()
            stats = response.data[0] if response.data else {}
            
            # Get sector breakdown
            response = self.supabase.table(self.table_name)\
                .select('sector')\
                .not_.is_('sector', 'null')\
                .execute()
            
            sector_counts = {}
            for row in response.data:
                sector = row['sector']
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            return {
                'stats': stats,
                'sector_breakdown': [{'sector': k, 'count': v} for k, v in sector_counts.items()]
            }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def export_to_json(self, filepath: str):
        """Export all companies to JSON file"""
        try:
            response = self.supabase.table(self.table_name)\
                .select('*')\
                .order('name')\
                .execute()
            
            companies = response.data
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(companies)} companies to {filepath}")
                
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

async def main():
    """Main function to initialize CSE database in Supabase"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Initializing Casablanca Stock Exchange Company Database in Supabase")
    print("=" * 70)
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        print("Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY")
        return
    
    # Initialize Supabase manager
    db_manager = SupabaseCSEManager(supabase_url, supabase_key)
    
    # Step 1: Scrape companies
    print("\n📊 Step 1: Fetching company data from CSE...")
    async with CSEScraper() as scraper:
        companies = await scraper.scrape_companies()
    
    if not companies:
        print("❌ No companies found. Exiting.")
        return
    
    print(f"✅ Successfully fetched {len(companies)} companies")
    
    # Step 2: Import to Supabase
    print("\n🗄️ Step 2: Importing data to Supabase...")
    new_count, updated_count, unchanged_count = db_manager.upsert_companies(companies)
    
    print(f"✅ Import completed: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
    
    # Step 3: Export data for backup
    print("\n📁 Step 3: Exporting data for backup...")
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Export to JSON
    companies_data = [company.to_dict() for company in companies]
    json_file = output_dir / "cse_companies_supabase.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(companies_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Export to CSV
    csv_file = output_dir / "cse_companies_supabase.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if companies_data:
            fieldnames = companies_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(companies_data)
    
    # Get database stats
    print("\n📈 Step 4: Getting database statistics...")
    stats = db_manager.get_database_stats()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎉 CSE Database Initialization Complete!")
    print("=" * 70)
    
    print(f"\n📊 Summary:")
    print(f"  • Total Companies Processed: {len(companies)}")
    print(f"  • New Companies Added: {new_count}")
    print(f"  • Companies Updated: {updated_count}")
    print(f"  • Companies Unchanged: {unchanged_count}")
    
    if stats.get('stats'):
        print(f"\n📈 Database Statistics:")
        stats_data = stats['stats']
        print(f"  • Total Companies in DB: {stats_data.get('total_companies', 0)}")
        print(f"  • Companies with ISIN: {stats_data.get('companies_with_isin', 0)}")
        print(f"  • Companies with Sector: {stats_data.get('companies_with_sector', 0)}")
        print(f"  • Sectors Count: {stats_data.get('sectors_count', 0)}")
    
    print(f"\n📁 Output Files:")
    print(f"  • JSON: {json_file}")
    print(f"  • CSV: {csv_file}")
    
    print(f"\n🔍 Sample Companies:")
    for i, company in enumerate(companies[:5]):
        print(f"  {i+1}. {company.name} ({company.ticker}) - {company.sector}")
    
    if len(companies) > 5:
        print(f"  ... and {len(companies) - 5} more")
    
    return {
        'total_companies': len(companies),
        'new_count': new_count,
        'updated_count': updated_count,
        'unchanged_count': unchanged_count,
        'output_files': {
            'json': str(json_file),
            'csv': str(csv_file)
        }
    }

if __name__ == "__main__":
    asyncio.run(main())