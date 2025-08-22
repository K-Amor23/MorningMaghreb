"""
Airflow DAG for Moroccan ETFs and Bonds Data Scraping
Runs daily to fetch and update ETF and Bond data
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import sys
import os

# Add backend ETL path for local and container execution
from pathlib import Path
dag_dir = Path(__file__).resolve().parent
backend_root = dag_dir.parent.parent  # apps/backend
sys.path.append(str(backend_root / 'etl'))
sys.path.append(str(backend_root))

# Import the scraper
from etf_bond_scraper import MoroccanETFBondScraper

# Default arguments for the DAG
default_args = {
    'owner': 'casablanca_insights',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'moroccan_etf_bond_scraping',
    default_args=default_args,
    description='Scrape Moroccan ETFs and Bonds data daily',
    schedule_interval='0 6 * * *',  # Run daily at 6 AM
    catchup=False,
    tags=['morocco', 'etfs', 'bonds', 'scraping'],
)

def scrape_etfs_and_bonds():
    """Scrape ETFs and Bonds data"""
    try:
        scraper = MoroccanETFBondScraper()
        results = scraper.run_full_scrape()
        
        print(f"Successfully scraped {len(results['etfs'])} ETFs and {len(results['bonds'])} bonds")
        print(f"Yield curve points: {len(results['yield_curve'])}")
        print(f"Calendar entries: {len(results['calendar'])}")
        
        return {
            'etfs_count': len(results['etfs']),
            'bonds_count': len(results['bonds']),
            'yield_curve_points': len(results['yield_curve']),
            'calendar_entries': len(results['calendar'])
        }
        
    except Exception as e:
        print(f"Error in ETF/Bond scraping: {e}")
        raise e

def update_supabase_etfs_bonds():
    """Update Supabase with scraped ETF and Bond data"""
    try:
        import json
        from supabase import create_client, Client
        
        # Initialize Supabase client
        supabase_url = Variable.get("SUPABASE_URL")
        supabase_key = Variable.get("SUPABASE_SERVICE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Load scraped data
        with open('data/moroccan_etfs.json', 'r') as f:
            etfs_data = json.load(f)
        
        with open('data/moroccan_bonds.json', 'r') as f:
            bonds_data = json.load(f)
        
        with open('data/moroccan_yield_curve.json', 'r') as f:
            yield_curve_data = json.load(f)
        
        with open('data/moroccan_bond_calendar.json', 'r') as f:
            calendar_data = json.load(f)
        
        # Update ETFs table
        for etf in etfs_data:
            etf_dict = etf.__dict__ if hasattr(etf, '__dict__') else etf
            # Convert date strings to proper format
            if 'inception_date' in etf_dict and etf_dict['inception_date']:
                etf_dict['inception_date'] = etf_dict['inception_date']
            if 'listing_date' in etf_dict and etf_dict['listing_date']:
                etf_dict['listing_date'] = etf_dict['listing_date']
            
            # Upsert ETF data
            supabase.table('etfs').upsert(etf_dict).execute()
        
        # Update Bonds table
        for bond in bonds_data:
            bond_dict = bond.__dict__ if hasattr(bond, '__dict__') else bond
            # Convert date strings to proper format
            if 'issue_date' in bond_dict and bond_dict['issue_date']:
                bond_dict['issue_date'] = bond_dict['issue_date']
            if 'maturity_date' in bond_dict and bond_dict['maturity_date']:
                bond_dict['maturity_date'] = bond_dict['maturity_date']
            
            # Upsert Bond data
            supabase.table('bonds').upsert(bond_dict).execute()
        
        # Update Yield Curve table
        for point in yield_curve_data:
            point_dict = {
                'date': datetime.now().date().isoformat(),
                'maturity_months': int(point),
                'yield': yield_curve_data[point],
                'source': 'bam'
            }
            supabase.table('yield_curve').upsert(point_dict).execute()
        
        # Update Bond Issuance Calendar table
        for item in calendar_data:
            item_dict = item.__dict__ if hasattr(item, '__dict__') else item
            # Convert date strings to proper format
            if 'expected_issue_date' in item_dict and item_dict['expected_issue_date']:
                item_dict['expected_issue_date'] = item_dict['expected_issue_date']
            if 'expected_maturity_date' in item_dict and item_dict['expected_maturity_date']:
                item_dict['expected_maturity_date'] = item_dict['expected_maturity_date']
            
            # Upsert Calendar data
            supabase.table('bond_issuance_calendar').upsert(item_dict).execute()
        
        print("Successfully updated Supabase with ETF and Bond data")
        
    except Exception as e:
        print(f"Error updating Supabase: {e}")
        raise e

def generate_etf_bond_reports():
    """Generate reports for ETF and Bond data"""
    try:
        import json
        from datetime import datetime
        
        # Load data
        with open('data/moroccan_etfs.json', 'r') as f:
            etfs_data = json.load(f)
        
        with open('data/moroccan_bonds.json', 'r') as f:
            bonds_data = json.load(f)
        
        # Generate summary report
        report = {
            'timestamp': datetime.now().isoformat(),
            'etfs_summary': {
                'total_count': len(etfs_data),
                'total_aum': sum(etf.get('total_assets', 0) for etf in etfs_data),
                'avg_expense_ratio': sum(etf.get('expense_ratio', 0) for etf in etfs_data) / len(etfs_data) if etfs_data else 0,
                'equity_count': len([e for e in etfs_data if e.get('asset_class') == 'equity']),
                'bond_count': len([e for e in etfs_data if e.get('asset_class') == 'bond'])
            },
            'bonds_summary': {
                'total_count': len(bonds_data),
                'government_count': len([b for b in bonds_data if b.get('bond_type') == 'government']),
                'corporate_count': len([b for b in bonds_data if b.get('bond_type') == 'corporate']),
                'avg_yield': sum(b.get('yield_to_maturity', 0) for b in bonds_data) / len(bonds_data) if bonds_data else 0,
                'total_issue_size': sum(b.get('issue_size', 0) for b in bonds_data)
            }
        }
        
        # Save report
        with open(f'data/etf_bond_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("Successfully generated ETF and Bond reports")
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        raise e

# Define tasks
scrape_task = PythonOperator(
    task_id='scrape_etfs_and_bonds',
    python_callable=scrape_etfs_and_bonds,
    dag=dag,
)

update_supabase_task = PythonOperator(
    task_id='update_supabase_etfs_bonds',
    python_callable=update_supabase_etfs_bonds,
    dag=dag,
)

generate_reports_task = PythonOperator(
    task_id='generate_etf_bond_reports',
    python_callable=generate_etf_bond_reports,
    dag=dag,
)

# Define task dependencies
scrape_task >> update_supabase_task >> generate_reports_task 