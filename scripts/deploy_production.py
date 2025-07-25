#!/usr/bin/env python3
"""
Production Deployment Script for Casablanca Insights
Handles production deployment with comprehensive verification
"""

import os
import sys
import asyncio
import logging
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductionConfig:
    """Production deployment configuration"""
    supabase_url: str
    supabase_key: str
    database_url: str
    project_root: Path
    migrations_dir: Path
    backup_dir: Path
    health_check_url: str
    alert_webhook_url: str

class ProductionDeployer:
    """Handles production deployment with comprehensive verification"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.deployment_id = f"prod_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.deployment_log = []
        
    async def deploy_to_production(self) -> bool:
        """Main production deployment process"""
        logger.info(f"🚀 Starting production deployment {self.deployment_id}")
        
        try:
            # 1. Pre-deployment verification
            if not await self._pre_deployment_verification():
                return False
            
            # 2. Create production backup
            if not await self._create_production_backup():
                return False
            
            # 3. Run migrations
            if not await self._run_production_migrations():
                return False
            
            # 4. Verify schema changes
            if not await self._verify_schema_changes():
                return False
            
            # 5. Verify data migration
            if not await self._verify_data_migration():
                return False
            
            # 6. Health checks
            if not await self._run_health_checks():
                return False
            
            # 7. Performance baseline
            if not await self._run_performance_baseline():
                return False
            
            # 8. Post-deployment tasks
            await self._post_deployment_tasks()
            
            logger.info(f"✅ Production deployment {self.deployment_id} completed successfully")
            await self._send_alert("success", "Production deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Production deployment failed: {e}")
            await self._send_alert("error", f"Production deployment failed: {str(e)}")
            return False
    
    async def _pre_deployment_verification(self) -> bool:
        """Pre-deployment verification checks"""
        logger.info("🔍 Running pre-deployment verification...")
        
        checks = [
            self._verify_production_access(),
            self._verify_migration_files(),
            self._verify_backup_space(),
            self._verify_health_check_endpoint(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Pre-deployment check {i+1} failed: {result}")
                return False
            elif not result:
                logger.error(f"❌ Pre-deployment check {i+1} failed")
                return False
        
        logger.info("✅ All pre-deployment checks passed")
        return True
    
    async def _verify_production_access(self) -> bool:
        """Verify production Supabase access"""
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}"
            }
            
            response = requests.get(
                f"{self.config.supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Production Supabase access verified")
                return True
            else:
                logger.error(f"❌ Production access failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Production access check failed: {e}")
            return False
    
    async def _verify_migration_files(self) -> bool:
        """Verify migration files are ready"""
        migration_file = self.config.migrations_dir / "migration_001_indexes_constraints.sql"
        
        if not migration_file.exists():
            logger.error(f"❌ Migration file not found: {migration_file}")
            return False
        
        content = migration_file.read_text()
        if not content.strip():
            logger.error(f"❌ Migration file is empty: {migration_file}")
            return False
        
        logger.info("✅ Migration files verified")
        return True
    
    async def _verify_backup_space(self) -> bool:
        """Verify sufficient backup space"""
        try:
            stat = os.statvfs(self.config.backup_dir)
            free_space_gb = (stat.f_frsize * stat.f_bavail) / (1024**3)
            
            if free_space_gb < 5.0:  # Need at least 5GB for production backup
                logger.error(f"❌ Insufficient backup space: {free_space_gb:.2f}GB")
                return False
            
            logger.info(f"✅ Backup space available: {free_space_gb:.2f}GB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup space check failed: {e}")
            return False
    
    async def _verify_health_check_endpoint(self) -> bool:
        """Verify health check endpoint is accessible"""
        try:
            response = requests.get(self.config.health_check_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Health check endpoint accessible")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check verification failed: {e}")
            return False
    
    async def _create_production_backup(self) -> bool:
        """Create production database backup"""
        logger.info("💾 Creating production backup...")
        
        try:
            backup_file = self.config.backup_dir / f"prod_backup_{self.deployment_id}.sql"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use pg_dump for production backup
            cmd = [
                "pg_dump",
                "--host", self.config.database_url.split("@")[1].split(":")[0],
                "--port", "5432",
                "--username", "postgres",
                "--dbname", "postgres",
                "--file", str(backup_file),
                "--verbose",
                "--no-password"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.supabase_key
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout for production backup
            )
            
            if result.returncode == 0:
                backup_size = backup_file.stat().st_size / (1024**2)  # MB
                logger.info(f"✅ Production backup created: {backup_file} ({backup_size:.2f}MB)")
                return True
            else:
                logger.error(f"❌ Production backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Production backup creation failed: {e}")
            return False
    
    async def _run_production_migrations(self) -> bool:
        """Run migrations in production"""
        logger.info("🔧 Running production migrations...")
        
        migration_file = self.config.migrations_dir / "migration_001_indexes_constraints.sql"
        
        try:
            # Read migration SQL
            migration_sql = migration_file.read_text()
            
            # Execute migration
            success = await self._execute_production_sql(migration_sql, migration_file.name)
            
            if not success:
                logger.error(f"❌ Production migration failed: {migration_file.name}")
                return False
            
            logger.info(f"✅ Production migration completed: {migration_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Production migration error: {migration_file.name} - {e}")
            return False
    
    async def _execute_production_sql(self, sql: str, migration_name: str) -> bool:
        """Execute SQL against production Supabase"""
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if not statement:
                    continue
                
                logger.info(f"Executing statement {i+1}/{len(statements)}")
                
                # Use Supabase REST API for SQL execution
                response = requests.post(
                    f"{self.config.supabase_url}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={"sql": statement},
                    timeout=60  # Longer timeout for production
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"❌ SQL execution failed: {response.status_code} - {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Production SQL execution error: {e}")
            return False
    
    async def _verify_schema_changes(self) -> bool:
        """Verify schema changes were applied correctly"""
        logger.info("🔍 Verifying schema changes...")
        
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}"
            }
            
            # Check that new indexes exist
            index_check_query = """
            SELECT indexname FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
            ORDER BY indexname;
            """
            
            response = requests.post(
                f"{self.config.supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"sql": index_check_query},
                timeout=30
            )
            
            if response.status_code == 200:
                indexes = response.json()
                logger.info(f"✅ Found {len(indexes)} indexes in production")
                
                # Check for key indexes
                expected_indexes = [
                    'idx_companies_ticker',
                    'idx_company_prices_ticker_date',
                    'idx_company_reports_ticker_type',
                    'idx_company_news_ticker_published'
                ]
                
                index_names = [idx.get('indexname', '') for idx in indexes]
                missing_indexes = [idx for idx in expected_indexes if idx not in index_names]
                
                if missing_indexes:
                    logger.error(f"❌ Missing indexes: {missing_indexes}")
                    return False
                
                logger.info("✅ All expected indexes found")
                return True
            else:
                logger.error(f"❌ Schema verification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Schema verification error: {e}")
            return False
    
    async def _verify_data_migration(self) -> bool:
        """Verify data migration was successful"""
        logger.info("🔍 Verifying data migration...")
        
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}"
            }
            
            # Check key tables have data
            tables_to_check = ["companies", "company_prices", "company_reports", "company_news"]
            
            for table in tables_to_check:
                response = requests.get(
                    f"{self.config.supabase_url}/rest/v1/{table}?select=count",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    count = len(response.json())
                    logger.info(f"✅ Table {table}: {count} records")
                    
                    if count == 0:
                        logger.warning(f"⚠️  Table {table} is empty")
                else:
                    logger.error(f"❌ Could not check table {table}: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Data migration verification failed: {e}")
            return False
    
    async def _run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        logger.info("🏥 Running health checks...")
        
        try:
            # Check API health
            response = requests.get(self.config.health_check_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return False
            
            # Check database health
            db_healthy = await self._check_database_health()
            if not db_healthy:
                logger.error("❌ Database health check failed")
                return False
            
            # Check key endpoints
            endpoints_to_check = [
                "/api/companies/IAM/summary",
                "/api/companies/ATW/summary",
                "/api/companies/BCP/summary"
            ]
            
            for endpoint in endpoints_to_check:
                full_url = f"{self.config.health_check_url.rstrip('/')}{endpoint}"
                response = requests.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ Endpoint {endpoint} healthy")
                else:
                    logger.error(f"❌ Endpoint {endpoint} failed: {response.status_code}")
                    return False
            
            logger.info("✅ All health checks passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Health checks failed: {e}")
            return False
    
    async def _check_database_health(self) -> bool:
        """Check database health"""
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}"
            }
            
            response = requests.get(
                f"{self.config.supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    async def _run_performance_baseline(self) -> bool:
        """Run performance baseline tests"""
        logger.info("⚡ Running performance baseline...")
        
        try:
            # Test key endpoints for performance
            endpoints = [
                "/api/companies/IAM/summary",
                "/api/companies/ATW/trading",
                "/api/companies/BCP/reports"
            ]
            
            performance_results = []
            
            for endpoint in endpoints:
                full_url = f"{self.config.health_check_url.rstrip('/')}{endpoint}"
                
                # Run 5 requests to get average response time
                response_times = []
                for i in range(5):
                    start_time = time.time()
                    response = requests.get(full_url, timeout=30)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_time = (end_time - start_time) * 1000  # Convert to ms
                        response_times.append(response_time)
                    else:
                        logger.error(f"❌ Performance test failed for {endpoint}: {response.status_code}")
                        return False
                
                avg_response_time = sum(response_times) / len(response_times)
                performance_results.append({
                    "endpoint": endpoint,
                    "avg_response_time_ms": avg_response_time,
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times)
                })
                
                logger.info(f"✅ {endpoint}: {avg_response_time:.2f}ms avg")
                
                # Check if response time is acceptable (< 500ms for baseline)
                if avg_response_time > 500:
                    logger.warning(f"⚠️  Slow response time for {endpoint}: {avg_response_time:.2f}ms")
            
            # Save performance baseline
            baseline_file = self.config.backup_dir / f"performance_baseline_{self.deployment_id}.json"
            with open(baseline_file, 'w') as f:
                json.dump(performance_results, f, indent=2)
            
            logger.info(f"✅ Performance baseline saved: {baseline_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance baseline failed: {e}")
            return False
    
    async def _post_deployment_tasks(self):
        """Post-deployment tasks"""
        logger.info("🔧 Running post-deployment tasks...")
        
        tasks = [
            self._update_deployment_log(),
            self._cleanup_old_backups(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _update_deployment_log(self):
        """Update deployment log"""
        try:
            log_entry = {
                "deployment_id": self.deployment_id,
                "timestamp": datetime.now().isoformat(),
                "environment": "production",
                "status": "success",
                "type": "migration_and_verification"
            }
            
            log_file = self.config.project_root / "production_deployment_history.json"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(log_entry)
            
            # Keep only last 20 production deployments
            if len(history) > 20:
                history = history[-20:]
            
            with open(log_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info("✅ Deployment log updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update deployment log: {e}")
    
    async def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backup_files = list(self.config.backup_dir.glob("prod_backup_*.sql"))
            
            # Keep only last 10 production backups
            if len(backup_files) > 10:
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                files_to_delete = backup_files[:-10]
                
                for file in files_to_delete:
                    file.unlink()
                    logger.info(f"🗑️  Deleted old backup: {file.name}")
            
        except Exception as e:
            logger.error(f"❌ Backup cleanup failed: {e}")
    
    async def _send_alert(self, alert_type: str, message: str):
        """Send deployment alert"""
        if not self.config.alert_webhook_url:
            return
        
        try:
            alert_data = {
                "deployment_id": self.deployment_id,
                "type": alert_type,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "environment": "production",
                "project": "Casablanca Insights"
            }
            
            response = requests.post(
                self.config.alert_webhook_url,
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Alert sent successfully")
            else:
                logger.error(f"❌ Failed to send alert: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Alert sending failed: {e}")

async def main():
    """Main production deployment function"""
    # Load configuration from environment
    config = ProductionConfig(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
        project_root=Path(__file__).parent.parent,
        migrations_dir=Path(__file__).parent.parent / "database",
        backup_dir=Path(__file__).parent.parent / "backups",
        health_check_url=os.getenv("HEALTH_CHECK_URL", "http://localhost:8000"),
        alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL", "")
    )
    
    # Validate configuration
    if not config.supabase_url or not config.supabase_key:
        logger.error("❌ Missing Supabase configuration")
        sys.exit(1)
    
    if not config.health_check_url:
        logger.error("❌ Missing health check URL")
        sys.exit(1)
    
    # Create deployer
    deployer = ProductionDeployer(config)
    
    # Run production deployment
    success = await deployer.deploy_to_production()
    
    if success:
        logger.info("🎉 Production deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Production deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 