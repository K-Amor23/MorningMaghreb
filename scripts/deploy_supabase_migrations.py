#!/usr/bin/env python3
"""
Supabase Deployment Automation Script
Handles migrations, seed data, and monitoring for Casablanca Insights
"""

import os
import sys
import asyncio
import logging
import subprocess
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    supabase_url: str
    supabase_key: str
    database_url: str
    project_root: Path
    migrations_dir: Path
    seed_data_dir: Path
    backup_dir: Path
    alert_webhook_url: Optional[str] = None
    health_check_url: Optional[str] = None

class SupabaseDeployer:
    """Handles Supabase deployment operations"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.deployment_id = f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.deployment_log = []
        
    async def deploy(self) -> bool:
        """Main deployment process"""
        logger.info(f"Starting deployment {self.deployment_id}")
        
        try:
            # 1. Pre-deployment checks
            if not await self._pre_deployment_checks():
                return False
            
            # 2. Create backup
            if not await self._create_backup():
                return False
            
            # 3. Run migrations
            if not await self._run_migrations():
                return False
            
            # 4. Seed data
            if not await self._seed_data():
                return False
            
            # 5. Verify deployment
            if not await self._verify_deployment():
                return False
            
            # 6. Post-deployment tasks
            await self._post_deployment_tasks()
            
            logger.info(f"Deployment {self.deployment_id} completed successfully")
            await self._send_alert("success", "Deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            await self._send_alert("error", f"Deployment failed: {str(e)}")
            return False
    
    async def _pre_deployment_checks(self) -> bool:
        """Run pre-deployment checks"""
        logger.info("Running pre-deployment checks...")
        
        checks = [
            self._check_supabase_connection(),
            self._check_migration_files(),
            self._check_seed_data_files(),
            self._check_disk_space(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Pre-deployment check {i+1} failed: {result}")
                return False
            elif not result:
                logger.error(f"Pre-deployment check {i+1} failed")
                return False
        
        logger.info("All pre-deployment checks passed")
        return True
    
    async def _check_supabase_connection(self) -> bool:
        """Check Supabase connection"""
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
                logger.info("Supabase connection verified")
                return True
            else:
                logger.error(f"Supabase connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Supabase connection check failed: {e}")
            return False
    
    async def _check_migration_files(self) -> bool:
        """Check migration files exist and are valid"""
        migration_files = list(self.config.migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.warning("No migration files found")
            return True  # Not a failure, just no migrations
        
        logger.info(f"Found {len(migration_files)} migration files")
        
        for migration_file in migration_files:
            if not migration_file.exists():
                logger.error(f"Migration file not found: {migration_file}")
                return False
            
            # Basic SQL validation
            content = migration_file.read_text()
            if not content.strip():
                logger.error(f"Migration file is empty: {migration_file}")
                return False
        
        return True
    
    async def _check_seed_data_files(self) -> bool:
        """Check seed data files"""
        seed_files = list(self.config.seed_data_dir.glob("*.json"))
        seed_files.extend(list(self.config.seed_data_dir.glob("*.csv")))
        
        if not seed_files:
            logger.warning("No seed data files found")
            return True  # Not a failure
        
        logger.info(f"Found {len(seed_files)} seed data files")
        return True
    
    async def _check_disk_space(self) -> bool:
        """Check available disk space"""
        try:
            stat = os.statvfs(self.config.project_root)
            free_space_gb = (stat.f_frsize * stat.f_bavail) / (1024**3)
            
            if free_space_gb < 1.0:  # Less than 1GB
                logger.error(f"Insufficient disk space: {free_space_gb:.2f}GB")
                return False
            
            logger.info(f"Available disk space: {free_space_gb:.2f}GB")
            return True
            
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False
    
    async def _create_backup(self) -> bool:
        """Create database backup"""
        logger.info("Creating database backup...")
        
        try:
            backup_file = self.config.backup_dir / f"backup_{self.deployment_id}.sql"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use pg_dump to create backup
            cmd = [
                "pg_dump",
                "--host", self.config.database_url.split("@")[1].split(":")[0],
                "--port", "5432",
                "--username", "postgres",
                "--dbname", "postgres",
                "--file", str(backup_file),
                "--verbose"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.supabase_key
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Backup created: {backup_file}")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    async def _run_migrations(self) -> bool:
        """Run database migrations"""
        logger.info("Running database migrations...")
        
        migration_files = sorted(self.config.migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.info("No migrations to run")
            return True
        
        for migration_file in migration_files:
            logger.info(f"Running migration: {migration_file.name}")
            
            try:
                # Read migration SQL
                migration_sql = migration_file.read_text()
                
                # Execute migration
                success = await self._execute_sql(migration_sql, migration_file.name)
                
                if not success:
                    logger.error(f"Migration failed: {migration_file.name}")
                    return False
                
                logger.info(f"Migration completed: {migration_file.name}")
                
            except Exception as e:
                logger.error(f"Migration error: {migration_file.name} - {e}")
                return False
        
        logger.info("All migrations completed successfully")
        return True
    
    async def _execute_sql(self, sql: str, migration_name: str) -> bool:
        """Execute SQL against Supabase"""
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if not statement:
                    continue
                
                # Use Supabase REST API for SQL execution
                response = requests.post(
                    f"{self.config.supabase_url}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={"sql": statement},
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"SQL execution failed: {response.status_code} - {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return False
    
    async def _seed_data(self) -> bool:
        """Seed database with initial data"""
        logger.info("Seeding database...")
        
        seed_files = list(self.config.seed_data_dir.glob("*.json"))
        seed_files.extend(list(self.config.seed_data_dir.glob("*.csv")))
        
        if not seed_files:
            logger.info("No seed data to load")
            return True
        
        for seed_file in seed_files:
            logger.info(f"Loading seed data: {seed_file.name}")
            
            try:
                if seed_file.suffix == '.json':
                    success = await self._load_json_seed(seed_file)
                elif seed_file.suffix == '.csv':
                    success = await self._load_csv_seed(seed_file)
                else:
                    logger.warning(f"Unsupported seed file format: {seed_file}")
                    continue
                
                if not success:
                    logger.error(f"Seed data loading failed: {seed_file.name}")
                    return False
                
                logger.info(f"Seed data loaded: {seed_file.name}")
                
            except Exception as e:
                logger.error(f"Seed data error: {seed_file.name} - {e}")
                return False
        
        logger.info("All seed data loaded successfully")
        return True
    
    async def _load_json_seed(self, seed_file: Path) -> bool:
        """Load JSON seed data"""
        try:
            with open(seed_file, 'r') as f:
                data = json.load(f)
            
            # Determine table name from filename
            table_name = seed_file.stem
            
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Insert data in batches
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                response = requests.post(
                    f"{self.config.supabase_url}/rest/v1/{table_name}",
                    headers=headers,
                    json=batch,
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"JSON seed insert failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"JSON seed loading error: {e}")
            return False
    
    async def _load_csv_seed(self, seed_file: Path) -> bool:
        """Load CSV seed data"""
        try:
            import pandas as pd
            
            # Read CSV
            df = pd.read_csv(seed_file)
            
            # Convert to JSON for insertion
            data = df.to_dict('records')
            
            # Determine table name from filename
            table_name = seed_file.stem
            
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}",
                "Content-Type": "application/json"
            }
            
            # Insert data in batches
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                response = requests.post(
                    f"{self.config.supabase_url}/rest/v1/{table_name}",
                    headers=headers,
                    json=batch,
                    timeout=30
                )
                
                if response.status_code not in [200, 201]:
                    logger.error(f"CSV seed insert failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"CSV seed loading error: {e}")
            return False
    
    async def _verify_deployment(self) -> bool:
        """Verify deployment was successful"""
        logger.info("Verifying deployment...")
        
        checks = [
            self._check_database_health(),
            self._check_table_counts(),
            self._check_api_endpoints(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Verification check {i+1} failed: {result}")
                return False
            elif not result:
                logger.error(f"Verification check {i+1} failed")
                return False
        
        logger.info("Deployment verification completed")
        return True
    
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
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def _check_table_counts(self) -> bool:
        """Check that tables have expected data"""
        try:
            headers = {
                "apikey": self.config.supabase_key,
                "Authorization": f"Bearer {self.config.supabase_key}"
            }
            
            # Check key tables
            tables_to_check = ["companies", "company_prices", "company_reports", "company_news"]
            
            for table in tables_to_check:
                response = requests.get(
                    f"{self.config.supabase_url}/rest/v1/{table}?select=count",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    count = len(response.json())
                    logger.info(f"Table {table}: {count} records")
                else:
                    logger.warning(f"Could not check table {table}")
            
            return True
            
        except Exception as e:
            logger.error(f"Table count check failed: {e}")
            return False
    
    async def _check_api_endpoints(self) -> bool:
        """Check API endpoints are working"""
        if not self.config.health_check_url:
            logger.info("No health check URL configured")
            return True
        
        try:
            response = requests.get(self.config.health_check_url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False
    
    async def _post_deployment_tasks(self):
        """Post-deployment tasks"""
        logger.info("Running post-deployment tasks...")
        
        tasks = [
            self._cleanup_old_backups(),
            self._update_deployment_log(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            backup_files = list(self.config.backup_dir.glob("backup_*.sql"))
            
            # Keep only last 5 backups
            if len(backup_files) > 5:
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                files_to_delete = backup_files[:-5]
                
                for file in files_to_delete:
                    file.unlink()
                    logger.info(f"Deleted old backup: {file.name}")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    async def _update_deployment_log(self):
        """Update deployment log"""
        try:
            log_entry = {
                "deployment_id": self.deployment_id,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "duration": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
            log_file = self.config.project_root / "deployment_history.json"
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(log_entry)
            
            # Keep only last 50 deployments
            if len(history) > 50:
                history = history[-50:]
            
            with open(log_file, 'w') as f:
                json.dump(history, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update deployment log: {e}")
    
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
                "project": "Casablanca Insights"
            }
            
            response = requests.post(
                self.config.alert_webhook_url,
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Alert sent successfully")
            else:
                logger.error(f"Failed to send alert: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")

# ============================================
# MONITORING AND ALERTING
# ============================================

class DeploymentMonitor:
    """Monitors deployment health and sends alerts"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
    
    async def monitor_deployment_health(self):
        """Monitor deployment health"""
        logger.info("Starting deployment health monitoring...")
        
        while True:
            try:
                health_status = await self._check_health()
                
                if not health_status["healthy"]:
                    await self._send_alert("warning", f"Deployment health check failed: {health_status['error']}")
                
                # Wait 5 minutes before next check
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_health(self) -> Dict[str, Any]:
        """Check deployment health"""
        try:
            # Check database connection
            db_healthy = await self._check_database_health()
            
            # Check API endpoints
            api_healthy = await self._check_api_health()
            
            return {
                "healthy": db_healthy and api_healthy,
                "database": db_healthy,
                "api": api_healthy,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
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
    
    async def _check_api_health(self) -> bool:
        """Check API health"""
        if not self.config.health_check_url:
            return True
        
        try:
            response = requests.get(self.config.health_check_url, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    async def _send_alert(self, alert_type: str, message: str):
        """Send health alert"""
        if not self.config.alert_webhook_url:
            return
        
        try:
            alert_data = {
                "type": alert_type,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "project": "Casablanca Insights"
            }
            
            requests.post(
                self.config.alert_webhook_url,
                json=alert_data,
                timeout=10
            )
            
        except Exception as e:
            logger.error(f"Failed to send health alert: {e}")

# ============================================
# MAIN EXECUTION
# ============================================

async def main():
    """Main deployment function"""
    # Load configuration from environment
    config = DeploymentConfig(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        database_url=os.getenv("DATABASE_URL", ""),
        project_root=Path(__file__).parent.parent,
        migrations_dir=Path(__file__).parent.parent / "database",
        seed_data_dir=Path(__file__).parent.parent / "data",
        backup_dir=Path(__file__).parent.parent / "backups",
        alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL"),
        health_check_url=os.getenv("HEALTH_CHECK_URL")
    )
    
    # Validate configuration
    if not config.supabase_url or not config.supabase_key:
        logger.error("Missing Supabase configuration")
        sys.exit(1)
    
    # Create deployer
    deployer = SupabaseDeployer(config)
    
    # Run deployment
    success = await deployer.deploy()
    
    if success:
        logger.info("Deployment completed successfully")
        sys.exit(0)
    else:
        logger.error("Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 