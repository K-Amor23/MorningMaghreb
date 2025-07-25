#!/usr/bin/env python3
"""
Smart IR Scraping Setup Script

This script sets up the production-ready smart IR scraping system:
1. Applies database schema for IR scraping tracking
2. Configures Airflow variables and connections
3. Sets up initial company data with fiscal calendars
4. Creates scraping configuration
5. Validates the setup

Usage:
    python setup_smart_ir_scraping.py [--test-mode] [--dry-run]
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install: pip install psycopg2-binary requests python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartIRScrapingSetup:
    """Setup class for smart IR scraping system"""
    
    def __init__(self, test_mode: bool = False, dry_run: bool = False):
        self.test_mode = test_mode
        self.dry_run = dry_run
        
        # Database connection
        self.db_config = {
            'host': os.getenv('SUPABASE_HOST'),
            'port': os.getenv('SUPABASE_PORT', '5432'),
            'database': os.getenv('SUPABASE_DATABASE'),
            'user': os.getenv('SUPABASE_USER'),
            'password': os.getenv('SUPABASE_PASSWORD'),
        }
        
        # Airflow configuration
        self.airflow_base_url = os.getenv('AIRFLOW_BASE_URL', 'http://localhost:8080')
        self.airflow_username = os.getenv('AIRFLOW_USERNAME', 'admin')
        self.airflow_password = os.getenv('AIRFLOW_PASSWORD', 'admin')
        
        # Validate required environment variables
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['SUPABASE_HOST', 'SUPABASE_DATABASE', 'SUPABASE_USER', 'SUPABASE_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.error("Please set these in your .env file")
            sys.exit(1)
    
    def setup_database(self) -> bool:
        """Apply database schema for IR scraping"""
        try:
            logger.info("Setting up database schema...")
            
            # Read schema file
            schema_file = Path(__file__).parent.parent / 'database' / 'ir_scraping_schema.sql'
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            if self.dry_run:
                logger.info("DRY RUN: Would apply database schema")
                return True
            
            # Apply schema
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(schema_sql)
                    conn.commit()
            
            logger.info("✅ Database schema applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            return False
    
    def setup_initial_company_data(self) -> bool:
        """Set up initial company data with fiscal calendars"""
        try:
            logger.info("Setting up initial company data...")
            
            # Moroccan companies with their fiscal year ends and IR pages
            companies_data = [
                {
                    'ticker': 'ATW',
                    'name': 'Attijariwafa Bank',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.attijariwafabank.com',
                    'investor_relations_url': 'https://ir.attijariwafabank.com',
                    'ir_expected_release_date': date(2024, 4, 15)
                },
                {
                    'ticker': 'IAM',
                    'name': 'Maroc Telecom',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.iam.ma',
                    'investor_relations_url': 'https://www.iam.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 4, 20)
                },
                {
                    'ticker': 'BCP',
                    'name': 'Banque Centrale Populaire',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.bcp.ma',
                    'investor_relations_url': 'https://www.bcp.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 4, 25)
                },
                {
                    'ticker': 'BMCE',
                    'name': 'BMCE Bank of Africa',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.bmcebank.ma',
                    'investor_relations_url': 'https://www.bmcebank.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 4, 30)
                },
                {
                    'ticker': 'CIH',
                    'name': 'CIH Bank',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.cihbank.ma',
                    'investor_relations_url': 'https://www.cihbank.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 5)
                },
                {
                    'ticker': 'GAZ',
                    'name': 'Afriquia Gaz',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.afriquia-gaz.ma',
                    'investor_relations_url': 'https://www.afriquia-gaz.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 10)
                },
                {
                    'ticker': 'TMA',
                    'name': 'Taqa Morocco',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.taqamorocco.ma',
                    'investor_relations_url': 'https://www.taqamorocco.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 15)
                },
                {
                    'ticker': 'CMT',
                    'name': 'Ciments du Maroc',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.cimentsdumaroc.com',
                    'investor_relations_url': 'https://www.cimentsdumaroc.com/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 20)
                },
                {
                    'ticker': 'LAFA',
                    'name': 'Lafarge Ciments',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.lafargeholcim.ma',
                    'investor_relations_url': 'https://www.lafargeholcim.ma/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 25)
                },
                {
                    'ticker': 'MNG',
                    'name': 'Managem',
                    'fiscal_year_end_month': 12,
                    'fiscal_year_end_day': 31,
                    'website_url': 'https://www.managemgroup.com',
                    'investor_relations_url': 'https://www.managemgroup.com/fr/investisseurs',
                    'ir_expected_release_date': date(2024, 5, 30)
                }
            ]
            
            if self.dry_run:
                logger.info(f"DRY RUN: Would update {len(companies_data)} companies")
                return True
            
            # Update companies in database
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    for company in companies_data:
                        update_query = """
                        UPDATE companies 
                        SET 
                            fiscal_year_end_month = %s,
                            fiscal_year_end_day = %s,
                            ir_expected_release_date = %s,
                            scraping_status = 'pending'
                        WHERE ticker = %s
                        """
                        
                        cursor.execute(update_query, (
                            company['fiscal_year_end_month'],
                            company['fiscal_year_end_day'],
                            company['ir_expected_release_date'],
                            company['ticker']
                        ))
                    
                    conn.commit()
            
            logger.info(f"✅ Updated {len(companies_data)} companies with fiscal calendar data")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up company data: {e}")
            return False
    
    def setup_airflow_variables(self) -> bool:
        """Set up Airflow variables for IR scraping"""
        try:
            logger.info("Setting up Airflow variables...")
            
            # Airflow variables configuration
            variables = {
                'SLACK_WEBHOOK_URL': os.getenv('SLACK_WEBHOOK_URL', ''),
                'ALERT_EMAILS': json.dumps(['admin@casablanca-insights.com']),
                'PROXY_ENABLED': 'false',
                'TEST_MODE': 'true' if self.test_mode else 'false',
                'IR_REPORT_PATHS': json.dumps([
                    "/investors/",
                    "/investor-relations/",
                    "/financial-reports/",
                    "/documents/",
                    "/investors/annual-report.pdf",
                    "/investors/reports/annual-report.pdf",
                    "/investor-relations/annual-report.pdf",
                    "/financial-reports/annual-report.pdf"
                ]),
                'DEFAULT_USER_AGENTS': json.dumps([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
                ]),
                'RETRY_DELAY_MIN': '3',
                'RETRY_DELAY_MAX': '10',
                'MAX_RETRIES': '3',
                'RATE_LIMIT_DELAY': '5'
            }
            
            if self.dry_run:
                logger.info("DRY RUN: Would set Airflow variables")
                for key, value in variables.items():
                    logger.info(f"  {key}: {value}")
                return True
            
            # Set variables via Airflow REST API
            session = requests.Session()
            session.auth = (self.airflow_username, self.airflow_password)
            
            for key, value in variables.items():
                try:
                    response = session.post(
                        f"{self.airflow_base_url}/api/v1/variables",
                        json={'key': key, 'value': value},
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Set Airflow variable: {key}")
                    else:
                        logger.warning(f"⚠️  Failed to set {key}: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"⚠️  Could not set {key}: {e}")
            
            logger.info("✅ Airflow variables configured")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Airflow variables: {e}")
            return False
    
    def setup_airflow_connection(self) -> bool:
        """Set up Airflow database connection"""
        try:
            logger.info("Setting up Airflow database connection...")
            
            if self.dry_run:
                logger.info("DRY RUN: Would set up Airflow connection 'supabase_postgres'")
                return True
            
            # Connection configuration
            connection_data = {
                'connection_id': 'supabase_postgres',
                'conn_type': 'postgres',
                'host': self.db_config['host'],
                'schema': 'public',
                'login': self.db_config['user'],
                'password': self.db_config['password'],
                'port': int(self.db_config['port']),
                'description': 'Supabase PostgreSQL connection for IR scraping'
            }
            
            # Set connection via Airflow REST API
            session = requests.Session()
            session.auth = (self.airflow_username, self.airflow_password)
            
            try:
                response = session.post(
                    f"{self.airflow_base_url}/api/v1/connections",
                    json=connection_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    logger.info("✅ Airflow database connection configured")
                    return True
                else:
                    logger.warning(f"⚠️  Failed to set connection: {response.status_code}")
                    return False
                    
            except Exception as e:
                logger.warning(f"⚠️  Could not set connection: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up Airflow connection: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """Validate the setup by running tests"""
        try:
            logger.info("Validating setup...")
            
            # Test database connection and schema
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    
                    # Check if tables exist
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('ir_scraping_history', 'ir_reports', 'scraping_config')
                    """)
                    
                    tables = [row['table_name'] for row in cursor.fetchall()]
                    expected_tables = ['ir_scraping_history', 'ir_reports', 'scraping_config']
                    
                    missing_tables = set(expected_tables) - set(tables)
                    if missing_tables:
                        logger.error(f"Missing tables: {missing_tables}")
                        return False
                    
                    # Check if companies have fiscal calendar data
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM companies 
                        WHERE fiscal_year_end_month IS NOT NULL 
                        AND ir_expected_release_date IS NOT NULL
                    """)
                    
                    companies_with_fiscal_data = cursor.fetchone()['count']
                    logger.info(f"Companies with fiscal calendar data: {companies_with_fiscal_data}")
                    
                    # Test the get_companies_due_for_scraping function
                    cursor.execute("SELECT * FROM get_companies_due_for_scraping() LIMIT 5")
                    companies_due = cursor.fetchall()
                    logger.info(f"Companies due for scraping: {len(companies_due)}")
                    
                    # Test the dashboard view
                    cursor.execute("SELECT COUNT(*) as count FROM ir_scraping_dashboard")
                    dashboard_count = cursor.fetchone()['count']
                    logger.info(f"Companies in dashboard: {dashboard_count}")
            
            logger.info("✅ Setup validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error validating setup: {e}")
            return False
    
    def copy_dag_file(self) -> bool:
        """Copy the DAG file to Airflow dags directory"""
        try:
            logger.info("Copying DAG file to Airflow...")
            
            dag_file = Path(__file__).parent.parent / 'airflow' / 'dags' / 'smart_ir_scraping_dag.py'
            if not dag_file.exists():
                logger.error(f"DAG file not found: {dag_file}")
                return False
            
            # Get Airflow dags directory
            airflow_dags_dir = os.getenv('AIRFLOW_HOME', '/opt/airflow/dags')
            if not os.path.exists(airflow_dags_dir):
                airflow_dags_dir = '/tmp/airflow_dags'  # Fallback for testing
                os.makedirs(airflow_dags_dir, exist_ok=True)
            
            target_file = Path(airflow_dags_dir) / 'smart_ir_scraping_dag.py'
            
            if self.dry_run:
                logger.info(f"DRY RUN: Would copy {dag_file} to {target_file}")
                return True
            
            # Copy file
            import shutil
            shutil.copy2(dag_file, target_file)
            
            logger.info(f"✅ DAG file copied to {target_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying DAG file: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run the complete setup process"""
        logger.info("🚀 Starting Smart IR Scraping Setup")
        logger.info(f"Test Mode: {self.test_mode}")
        logger.info(f"Dry Run: {self.dry_run}")
        
        steps = [
            ("Database Schema", self.setup_database),
            ("Company Data", self.setup_initial_company_data),
            ("Airflow Variables", self.setup_airflow_variables),
            ("Airflow Connection", self.setup_airflow_connection),
            ("Copy DAG File", self.copy_dag_file),
            ("Validate Setup", self.validate_setup),
        ]
        
        results = []
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            try:
                result = step_func()
                results.append((step_name, result))
                if result:
                    logger.info(f"✅ {step_name} completed successfully")
                else:
                    logger.error(f"❌ {step_name} failed")
            except Exception as e:
                logger.error(f"❌ {step_name} failed with exception: {e}")
                results.append((step_name, False))
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("📊 SETUP SUMMARY")
        logger.info("="*50)
        
        successful_steps = [name for name, result in results if result]
        failed_steps = [name for name, result in results if not result]
        
        logger.info(f"✅ Successful: {len(successful_steps)}/{len(results)}")
        for step in successful_steps:
            logger.info(f"  ✅ {step}")
        
        if failed_steps:
            logger.info(f"❌ Failed: {len(failed_steps)}/{len(results)}")
            for step in failed_steps:
                logger.info(f"  ❌ {step}")
        
        overall_success = len(failed_steps) == 0
        
        if overall_success:
            logger.info("\n🎉 Setup completed successfully!")
            logger.info("\n📝 Next Steps:")
            logger.info("1. Verify DAG appears in Airflow UI")
            logger.info("2. Test the DAG with a manual trigger")
            logger.info("3. Monitor the first automated run")
            logger.info("4. Configure Slack/email notifications")
        else:
            logger.info("\n⚠️  Setup completed with errors")
            logger.info("Please review the failed steps above")
        
        return overall_success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Setup Smart IR Scraping System')
    parser.add_argument('--test-mode', action='store_true', help='Enable test mode (limit to 5 companies)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Run setup
    setup = SmartIRScrapingSetup(test_mode=args.test_mode, dry_run=args.dry_run)
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 