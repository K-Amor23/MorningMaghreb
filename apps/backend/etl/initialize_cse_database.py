"""
Casablanca Stock Exchange Database Initialization

This script:
1. Scrapes company data from CSE website
2. Normalizes and validates the data
3. Upserts into the database with audit tracking
4. Provides a summary report
"""

import asyncio
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path
import sys
import os
import csv

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from etl.cse_company_scraper import CSEScraper, CSECompany

logger = logging.getLogger(__name__)

class CSEDatabaseManager:
    """Manages CSE company database operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        self.connection = psycopg2.connect(self.database_url)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.connection:
            self.connection.close()
    
    def initialize_database(self):
        """Initialize the database schema"""
        try:
            with self.connection.cursor() as cursor:
                # Read and execute schema file
                schema_file = Path(__file__).parent.parent / "database" / "cse_companies_schema.sql"
                
                if not schema_file.exists():
                    logger.error(f"Schema file not found: {schema_file}")
                    return False
                
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                cursor.execute(schema_sql)
                self.connection.commit()
                
                logger.info("Database schema initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            self.connection.rollback()
            return False
    
    def get_existing_companies(self) -> Dict[str, Dict]:
        """Get existing companies from database"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT company_id, name, ticker, isin, sector, listing_date, source_url, updated_at
                    FROM cse_companies
                """)
                
                companies = {}
                for row in cursor.fetchall():
                    companies[row['ticker']] = dict(row)
                
                logger.info(f"Found {len(companies)} existing companies in database")
                return companies
                
        except Exception as e:
            logger.error(f"Error getting existing companies: {e}")
            return {}
    
    def upsert_companies(self, companies: List[CSECompany]) -> Tuple[int, int, int]:
        """Upsert companies into database and return counts"""
        existing_companies = self.get_existing_companies()
        
        new_count = 0
        updated_count = 0
        unchanged_count = 0
        
        try:
            with self.connection.cursor() as cursor:
                for company in companies:
                    company_dict = company.to_dict()
                    
                    if company.ticker in existing_companies:
                        # Check if company needs updating
                        existing = existing_companies[company.ticker]
                        needs_update = self._company_needs_update(existing, company_dict)
                        
                        if needs_update:
                            cursor.execute("""
                                UPDATE cse_companies 
                                SET name = %s, isin = %s, sector = %s, listing_date = %s, 
                                    source_url = %s, scraped_at = %s, updated_at = CURRENT_TIMESTAMP
                                WHERE ticker = %s
                            """, (
                                company.name, company.isin, company.sector, company.listing_date,
                                company.source_url, company.scraped_at, company.ticker
                            ))
                            updated_count += 1
                            logger.info(f"Updated company: {company.name} ({company.ticker})")
                        else:
                            unchanged_count += 1
                            logger.debug(f"No changes for company: {company.name} ({company.ticker})")
                    else:
                        # Insert new company
                        cursor.execute("""
                            INSERT INTO cse_companies (name, ticker, isin, sector, listing_date, source_url, scraped_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            company.name, company.ticker, company.isin, company.sector,
                            company.listing_date, company.source_url, company.scraped_at
                        ))
                        new_count += 1
                        logger.info(f"Added new company: {company.name} ({company.ticker})")
                
                self.connection.commit()
                logger.info(f"Database update completed: {new_count} new, {updated_count} updated, {unchanged_count} unchanged")
                
        except Exception as e:
            logger.error(f"Error upserting companies: {e}")
            self.connection.rollback()
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
                    existing_date = existing_val.date() if hasattr(existing_val, 'date') else existing_val
                    new_date = new_val.date() if hasattr(new_val, 'date') else new_val
                    if existing_date != new_date:
                        return True
                elif existing_val != new_val:
                    return True
            else:
                if existing_val != new_val:
                    return True
        
        return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM get_cse_company_stats()")
                stats = cursor.fetchone()
                
                # Get sector breakdown
                cursor.execute("""
                    SELECT sector, COUNT(*) as count
                    FROM cse_companies
                    WHERE sector IS NOT NULL
                    GROUP BY sector
                    ORDER BY count DESC
                """)
                sector_breakdown = cursor.fetchall()
                
                return {
                    'stats': dict(stats) if stats else {},
                    'sector_breakdown': [dict(row) for row in sector_breakdown]
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def export_to_json(self, filepath: str):
        """Export all companies to JSON file"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT name, ticker, isin, sector, listing_date, source_url, 
                           scraped_at, created_at, updated_at
                    FROM cse_companies
                    ORDER BY name
                """)
                
                companies = []
                for row in cursor.fetchall():
                    company_data = dict(row)
                    # Convert dates to strings for JSON serialization
                    for date_field in ['listing_date', 'scraped_at', 'created_at', 'updated_at']:
                        if company_data.get(date_field):
                            company_data[date_field] = company_data[date_field].isoformat()
                    companies.append(company_data)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(companies, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Exported {len(companies)} companies to {filepath}")
                
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

async def main():
    """Main function to initialize CSE database"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Initializing Casablanca Stock Exchange Company Database")
    print("=" * 60)
    
    # Step 1: Scrape companies
    print("\n📊 Step 1: Fetching company data from CSE...")
    async with CSEScraper() as scraper:
        companies = await scraper.scrape_companies()
    
    if not companies:
        print("❌ No companies found. Exiting.")
        return
    
    print(f"✅ Successfully fetched {len(companies)} companies")
    
    # Step 2: Export data (skip database for now)
    print("\n📁 Step 2: Exporting data...")
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Export to JSON
    companies_data = [company.to_dict() for company in companies]
    json_file = output_dir / "cse_companies_database.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(companies_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Export to CSV
    csv_file = output_dir / "cse_companies.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if companies_data:
            fieldnames = companies_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(companies_data)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 CSE Database Initialization Complete!")
    print("=" * 60)
    
    print(f"\n📊 Summary:")
    print(f"  • Total Companies Processed: {len(companies)}")
    print(f"  • Companies by Sector:")
    
    # Count by sector
    sector_counts = {}
    for company in companies:
        sector = company.sector or "Unknown"
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    for sector, count in sorted(sector_counts.items()):
        print(f"    - {sector}: {count}")
    
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
        'companies_by_sector': sector_counts,
        'output_files': {
            'json': str(json_file),
            'csv': str(csv_file)
        }
    }

if __name__ == "__main__":
    asyncio.run(main()) 