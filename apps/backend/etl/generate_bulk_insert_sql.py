#!/usr/bin/env python3
"""
Generate Bulk Insert SQL for Companies

This script generates SQL INSERT statements that can be run directly
in the Supabase SQL Editor to bypass RLS issues.
"""

import json
from pathlib import Path
from datetime import datetime

def generate_bulk_insert_sql():
    """Generate SQL INSERT statements for all companies"""
    
    # Load African Markets data
    data_file = Path("apps/backend/data/cse_companies_african_markets_database.json")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies = data.get('companies', [])
    
    if not companies:
        print("❌ No companies found in data file")
        return
    
    # Generate SQL
    sql_statements = []
    sql_statements.append("-- Bulk Insert CSE Companies")
    sql_statements.append("-- Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sql_statements.append("")
    
    # Start with DELETE to avoid duplicates (optional)
    sql_statements.append("-- Optional: Clear existing data first")
    sql_statements.append("-- DELETE FROM cse_companies WHERE source_url LIKE '%african-markets%';")
    sql_statements.append("")
    
    # Generate INSERT statements
    sql_statements.append("-- Insert all companies")
    sql_statements.append("INSERT INTO cse_companies (name, ticker, sector, source_url, scraped_at) VALUES")
    
    insert_values = []
    for company in companies:
        name = company.get('name', '').replace("'", "''")  # Escape single quotes
        ticker = company.get('ticker', '').replace("'", "''")
        sector = company.get('sector', '').replace("'", "''")
        source_url = company.get('url', '').replace("'", "''")
        scraped_at = company.get('scraped_at', datetime.now().isoformat())
        
        insert_values.append(f"('{name}', '{ticker}', '{sector}', '{source_url}', '{scraped_at}')")
    
    # Join all values with commas
    sql_statements.append(",\n".join(insert_values))
    sql_statements.append("ON CONFLICT (ticker) DO UPDATE SET")
    sql_statements.append("  name = EXCLUDED.name,")
    sql_statements.append("  sector = EXCLUDED.sector,")
    sql_statements.append("  source_url = EXCLUDED.source_url,")
    sql_statements.append("  scraped_at = EXCLUDED.scraped_at,")
    sql_statements.append("  updated_at = CURRENT_TIMESTAMP;")
    
    # Write to file
    sql_file = Path("bulk_insert_companies.sql")
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ Generated SQL file: {sql_file}")
    print(f"📊 Total companies: {len(companies)}")
    print(f"\n💡 To use this:")
    print(f"   1. Open Supabase Dashboard → SQL Editor")
    print(f"   2. Copy and paste the contents of {sql_file}")
    print(f"   3. Run the SQL query")
    print(f"   4. All {len(companies)} companies will be imported!")
    
    return sql_file

if __name__ == "__main__":
    generate_bulk_insert_sql() 