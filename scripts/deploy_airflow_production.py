#!/usr/bin/env python3
"""
Production Airflow Deployment Script for Morning Maghreb
Configures Airflow to run automated data collection with the new database
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AirflowProductionDeployer:
    """Handles production deployment of Airflow for Morning Maghreb"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.airflow_dir = self.project_root / "apps" / "backend" / "airflow"
        self.env_file = self.project_root / ".env.local"

        # New database credentials
        self.new_supabase_url = "https://gzsgehciddnrssuqxtsj.supabase.co"
        self.new_supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MTk5OTEsImV4cCI6MjA2OTk5NTk5MX0.DiaqtEop6spZT7l1g0PIdljVcBAWfalFEemlZqgwdrk"
        self.new_supabase_service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

    def deploy(self) -> bool:
        """Main deployment process"""
        logger.info("🚀 Starting Airflow Production Deployment...")

        try:
            # 1. Update environment configuration
            if not self._update_environment():
                return False

            # 2. Configure Airflow for production
            if not self._configure_airflow():
                return False

            # 3. Set up DAGs with new database
            if not self._setup_dags():
                return False

            # 4. Start Airflow services
            if not self._start_airflow():
                return False

            # 5. Configure scheduling
            if not self._configure_scheduling():
                return False

            logger.info("✅ Airflow production deployment completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False

    def _update_environment(self) -> bool:
        """Update environment configuration for new database"""
        logger.info("📝 Updating environment configuration...")

        try:
            # Create Airflow environment file
            airflow_env_file = self.airflow_dir / ".env"

            env_content = f"""# Airflow Production Environment for Morning Maghreb
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin

# Database Configuration
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow

# Supabase Configuration (New Database)
NEXT_PUBLIC_SUPABASE_URL={self.new_supabase_url}
NEXT_PUBLIC_SUPABASE_ANON_KEY={self.new_supabase_anon_key}
SUPABASE_SERVICE_ROLE_KEY={self.new_supabase_service_key}

# Environment
ENVIRONMENT=production
AIRFLOW_ENV=production

# Logging
AIRFLOW__LOGGING__LOGGING_LEVEL=INFO
AIRFLOW__LOGGING__FAB_LOGGING_LEVEL=WARN

# Email Configuration
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_USER=admin@morningmaghreb.com
AIRFLOW__SMTP__SMTP_PASSWORD=your_email_password
AIRFLOW__SMTP__SMTP_MAIL_FROM=admin@morningmaghreb.com

# Slack Configuration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url

# ETL Configuration
ETL_COMPANIES=["ATW", "IAM", "BCP", "BMCE", "CIH", "WAA", "CMT", "SID"]
ETL_BATCH_SIZE=10
ETL_MAX_RETRIES=3
ETL_SCHEDULE_INTERVAL=0 6 * * *
"""

            with open(airflow_env_file, "w") as f:
                f.write(env_content)

            logger.info("✅ Environment configuration updated")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating environment: {e}")
            return False

    def _configure_airflow(self) -> bool:
        """Configure Airflow for production use"""
        logger.info("⚙️ Configuring Airflow for production...")

        try:
            # Navigate to Airflow directory
            os.chdir(self.airflow_dir)

            # Create necessary directories
            subprocess.run(["mkdir", "-p", "dags", "logs", "plugins"], check=True)

            # Set Airflow home
            os.environ["AIRFLOW_HOME"] = str(self.airflow_dir)

            # Initialize Airflow database
            logger.info("Initializing Airflow database...")
            subprocess.run(["airflow", "db", "init"], check=True)

            # Create admin user
            logger.info("Creating admin user...")
            subprocess.run(
                [
                    "airflow",
                    "users",
                    "create",
                    "--username",
                    "admin",
                    "--firstname",
                    "Admin",
                    "--lastname",
                    "User",
                    "--role",
                    "Admin",
                    "--email",
                    "admin@morningmaghreb.com",
                    "--password",
                    "admin",
                ],
                check=True,
            )

            logger.info("✅ Airflow configured for production")
            return True

        except Exception as e:
            logger.error(f"❌ Error configuring Airflow: {e}")
            return False

    def _setup_dags(self) -> bool:
        """Set up DAGs with new database configuration"""
        logger.info("📊 Setting up DAGs with new database...")

        try:
            # Update DAG files to use new database
            dag_files = [
                "casablanca_etl_dag.py",
                "casablanca_live_quotes_dag.py",
                "enhanced_casablanca_etl_dag.py",
                "smart_ir_scraping_dag.py",
            ]

            for dag_file in dag_files:
                dag_path = self.airflow_dir / "dags" / dag_file
                if dag_path.exists():
                    self._update_dag_database_config(dag_path)

            logger.info("✅ DAGs configured with new database")
            return True

        except Exception as e:
            logger.error(f"❌ Error setting up DAGs: {e}")
            return False

    def _update_dag_database_config(self, dag_path: Path):
        """Update DAG file to use new database configuration"""
        try:
            with open(dag_path, "r") as f:
                content = f.read()

            # Update Supabase configuration
            content = content.replace(
                "https://kszekypwdjqaycpuayda.supabase.co", self.new_supabase_url
            )
            content = content.replace(
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzZXlwd2RqYXljcHVheWRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIxNjgxNTUsImV4cCI6MjA2Nzc0NDE1NX0.lEygnmyvx_7bZreLOeHOxLC8mh8GqlfTywsJ06tdZkU",
                self.new_supabase_anon_key,
            )

            with open(dag_path, "w") as f:
                f.write(content)

        except Exception as e:
            logger.warning(f"Could not update {dag_path}: {e}")

    def _start_airflow(self) -> bool:
        """Start Airflow services"""
        logger.info("🚀 Starting Airflow services...")

        try:
            # Start Airflow webserver
            logger.info("Starting Airflow webserver...")
            subprocess.Popen(
                ["airflow", "webserver", "--port", "8080"], cwd=self.airflow_dir
            )

            # Start Airflow scheduler
            logger.info("Starting Airflow scheduler...")
            subprocess.Popen(["airflow", "scheduler"], cwd=self.airflow_dir)

            logger.info("✅ Airflow services started")
            return True

        except Exception as e:
            logger.error(f"❌ Error starting Airflow: {e}")
            return False

    def _configure_scheduling(self) -> bool:
        """Configure DAG scheduling for production"""
        logger.info("⏰ Configuring DAG scheduling...")

        try:
            # Set up variables for production
            variables = {
                "ETL_COMPANIES": [
                    "ATW",
                    "IAM",
                    "BCP",
                    "BMCE",
                    "CIH",
                    "WAA",
                    "CMT",
                    "SID",
                ],
                "ETL_BATCH_SIZE": 10,
                "ETL_MAX_RETRIES": 3,
                "ENVIRONMENT": "production",
                "SUPABASE_URL": self.new_supabase_url,
                "SUPABASE_ANON_KEY": self.new_supabase_anon_key,
                "SUPABASE_SERVICE_KEY": self.new_supabase_service_key,
            }

            for key, value in variables.items():
                if isinstance(value, list):
                    value = json.dumps(value)
                subprocess.run(
                    ["airflow", "variables", "set", key, str(value)],
                    cwd=self.airflow_dir,
                    check=True,
                )

            logger.info("✅ DAG scheduling configured")
            return True

        except Exception as e:
            logger.error(f"❌ Error configuring scheduling: {e}")
            return False

    def print_deployment_summary(self):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("🎉 AIRFLOW PRODUCTION DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"📍 Airflow UI: http://localhost:8080")
        print(f"👤 Username: admin")
        print(f"🔑 Password: admin")
        print(f"🗄️ Database: {self.new_supabase_url}")
        print(f"⏰ Schedule: Daily at 6:00 AM UTC")
        print(f"📊 DAGs: casablanca_etl_dag, live_quotes_dag, smart_ir_scraping_dag")
        print("=" * 60)
        print("🚀 Your automated data collection is now running!")
        print("=" * 60)


def main():
    """Main deployment function"""
    deployer = AirflowProductionDeployer()

    print("🚀 Morning Maghreb Airflow Production Deployment")
    print("=" * 60)
    print("This will set up automated data collection with your new database")
    print("=" * 60)

    success = deployer.deploy()

    if success:
        deployer.print_deployment_summary()
        print("\n🎉 Airflow is now configured for production!")
        print("Your data collection will run automatically every day at 6:00 AM UTC.")
    else:
        print("\n❌ Airflow deployment failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
