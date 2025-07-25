#!/usr/bin/env python3
"""
Deploy and Test Casablanca Insights

This script handles the complete deployment process:
1. Generate OHLCV data for top 20 companies
2. Insert data into Supabase
3. Run scrapers
4. Test API endpoints
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CasablancaDeployer:
    """Deploy and test Casablanca Insights"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.scripts_dir = self.base_dir / "scripts"
        self.backend_dir = self.base_dir / "apps" / "backend"
        self.web_dir = self.base_dir / "apps" / "web"
        
        # Check environment variables
        self.check_environment()
    
    def check_environment(self):
        """Check required environment variables"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY', 
            'SUPABASE_SERVICE_ROLE_KEY',
            'NEXT_PUBLIC_SUPABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {missing_vars}")
            logger.error("Please set these variables before running the deployment")
            sys.exit(1)
        
        logger.info("✅ Environment variables configured")
    
    def run_command(self, command: str, cwd: Path = None, check: bool = True) -> bool:
        """Run a shell command"""
        try:
            logger.info(f"🔄 Running: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Command completed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Command failed: {result.stderr}")
                if check:
                    sys.exit(1)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running command: {str(e)}")
            if check:
                sys.exit(1)
            return False
    
    def generate_ohlcv_data(self) -> bool:
        """Generate OHLCV data for top 20 companies"""
        logger.info("📊 Step 1: Generating OHLCV data...")
        
        script_path = self.scripts_dir / "generate_ohlcv_data.py"
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        return self.run_command(f"python3 {script_path}")
    
    def deploy_database_schema(self) -> bool:
        """Deploy database schema to Supabase"""
        logger.info("🗄️  Step 2: Deploying database schema...")
        
        # Check if Supabase CLI is installed
        if not self.run_command("supabase --version", check=False):
            logger.warning("⚠️  Supabase CLI not found, skipping schema deployment")
            logger.info("Please deploy schema manually using Supabase dashboard")
            return True
        
        # Deploy schema
        schema_file = self.base_dir / "database" / "casablanca_insights_schema.sql"
        if not schema_file.exists():
            logger.error(f"❌ Schema file not found: {schema_file}")
            return False
        
        return self.run_command("supabase db push")
    
    def insert_data_to_supabase(self) -> bool:
        """Insert companies and OHLCV data to Supabase"""
        logger.info("💾 Step 3: Inserting data to Supabase...")
        
        script_path = self.scripts_dir / "insert_ohlcv_to_supabase.py"
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        return self.run_command(f"python3 {script_path}")
    
    def run_financial_reports_scraper(self) -> bool:
        """Run financial reports scraper"""
        logger.info("📄 Step 4: Running financial reports scraper...")
        
        script_path = self.backend_dir / "etl" / "financial_reports_scraper_batch.py"
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        # Run with small batch size for testing
        return self.run_command(f"python3 {script_path} --batch-size 5")
    
    def run_news_sentiment_scraper(self) -> bool:
        """Run news sentiment scraper"""
        logger.info("📰 Step 5: Running news sentiment scraper...")
        
        script_path = self.backend_dir / "etl" / "news_sentiment_scraper.py"
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        return self.run_command(f"python3 {script_path}")
    
    def start_frontend_server(self) -> bool:
        """Start the Next.js development server"""
        logger.info("🌐 Step 6: Starting frontend server...")
        
        # Install dependencies if needed
        package_json = self.web_dir / "package.json"
        if package_json.exists():
            self.run_command("npm install", cwd=self.web_dir, check=False)
        
        # Start server in background
        try:
            process = subprocess.Popen(
                "npm run dev",
                shell=True,
                cwd=self.web_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            logger.info("⏳ Waiting for server to start...")
            time.sleep(10)
            
            # Check if server is running
            try:
                response = requests.get("http://localhost:3000/api/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Frontend server is running")
                    return True
                else:
                    logger.error("❌ Frontend server not responding correctly")
                    return False
            except requests.exceptions.RequestException:
                logger.error("❌ Frontend server not accessible")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting frontend server: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints"""
        logger.info("🧪 Step 7: Testing API endpoints...")
        
        test_script = self.base_dir / "tests" / "test_api_endpoints.py"
        if not test_script.exists():
            logger.error(f"❌ Test script not found: {test_script}")
            return False
        
        return self.run_command(f"python3 {test_script}")
    
    def validate_data(self) -> bool:
        """Validate data in database"""
        logger.info("🔍 Step 8: Validating data...")
        
        try:
            import requests
            
            # Test a few companies
            test_companies = ["ATW", "IAM", "BCP"]
            
            for ticker in test_companies:
                url = f"http://localhost:3000/api/companies/{ticker}/summary"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    company = data['company']
                    price_data = data['priceData']
                    
                    logger.info(f"✅ {ticker}: {company['name']}")
                    logger.info(f"   Price: {price_data['currentPrice']}")
                    logger.info(f"   Records: {len(price_data['last90Days'])}")
                else:
                    logger.warning(f"⚠️  {ticker}: Not found or error")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating data: {str(e)}")
            return False
    
    def run_complete_deployment(self) -> bool:
        """Run the complete deployment process"""
        logger.info("🚀 Starting Casablanca Insights deployment...")
        logger.info("=" * 60)
        
        steps = [
            ("Generate OHLCV Data", self.generate_ohlcv_data),
            ("Deploy Database Schema", self.deploy_database_schema),
            ("Insert Data to Supabase", self.insert_data_to_supabase),
            ("Run Financial Reports Scraper", self.run_financial_reports_scraper),
            ("Run News Sentiment Scraper", self.run_news_sentiment_scraper),
            ("Start Frontend Server", self.start_frontend_server),
            ("Test API Endpoints", self.test_api_endpoints),
            ("Validate Data", self.validate_data)
        ]
        
        results = []
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}")
            logger.info("-" * 40)
            
            try:
                success = step_func()
                results.append((step_name, success))
                
                if not success:
                    logger.error(f"❌ {step_name} failed")
                    break
                    
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {str(e)}")
                results.append((step_name, False))
                break
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEPLOYMENT SUMMARY")
        logger.info("=" * 60)
        
        for step_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} {step_name}")
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        logger.info(f"\n🎯 Results: {success_count}/{total_count} steps completed successfully")
        
        if success_count == total_count:
            logger.info("🎉 Deployment completed successfully!")
            logger.info("\n🌐 Frontend is running at: http://localhost:3000")
            logger.info("📊 API endpoints are available at: http://localhost:3000/api")
            return True
        else:
            logger.error("⚠️  Deployment completed with errors")
            return False

def main():
    """Main function"""
    deployer = CasablancaDeployer()
    success = deployer.run_complete_deployment()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 