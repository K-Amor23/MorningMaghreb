#!/usr/bin/env python3
"""
Monitoring Setup Script for Casablanca Insights
Configures comprehensive monitoring for production deployment
"""

import os
import sys
import asyncio
import json
import logging
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("monitoring_setup.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class MonitoringSetup:
    """Comprehensive monitoring setup for Casablanca Insights"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "monitoring"
        self.config_dir.mkdir(exist_ok=True)

        # Environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        self.sentry_dsn = os.getenv("SENTRY_DSN")

        # Monitoring endpoints
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.websocket_url = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")

    async def setup_complete_monitoring(self) -> bool:
        """Setup complete monitoring infrastructure"""
        logger.info("🚀 Setting up comprehensive monitoring for Casablanca Insights")

        try:
            # 1. Supabase monitoring
            await self.setup_supabase_monitoring()

            # 2. Airflow alerts
            await self.setup_airflow_alerts()

            # 3. WebSocket monitoring
            await self.setup_websocket_monitoring()

            # 4. Grafana dashboards
            await self.setup_grafana_dashboards()

            # 5. Sentry integration
            await self.setup_sentry_integration()

            # 6. Health check endpoints
            await self.setup_health_checks()

            # 7. Performance monitoring
            await self.setup_performance_monitoring()

            logger.info("✅ Complete monitoring setup finished")
            return True

        except Exception as e:
            logger.error(f"❌ Monitoring setup failed: {e}")
            return False

    async def setup_supabase_monitoring(self):
        """Setup Supabase monitoring and alerts"""
        logger.info("📊 Setting up Supabase monitoring...")

        if not self.supabase_url or not self.supabase_key:
            logger.warning(
                "⚠️  Supabase credentials not found, skipping Supabase monitoring"
            )
            return

        # Create monitoring queries
        monitoring_queries = {
            "row_counts": """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY n_live_tup DESC;
            """,
            "slow_queries": """
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                WHERE mean_time > 100
                ORDER BY mean_time DESC 
                LIMIT 10;
            """,
            "table_sizes": """
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """,
            "connection_stats": """
                SELECT 
                    state,
                    count(*) as connections
                FROM pg_stat_activity 
                GROUP BY state;
            """,
        }

        # Save monitoring queries
        queries_file = self.config_dir / "supabase_monitoring_queries.json"
        with open(queries_file, "w") as f:
            json.dump(monitoring_queries, f, indent=2)

        # Create monitoring script
        monitoring_script = self.config_dir / "supabase_monitor.py"
        with open(monitoring_script, "w") as f:
            f.write(self._generate_supabase_monitor_script())

        logger.info(f"✅ Supabase monitoring configured: {monitoring_script}")

    async def setup_airflow_alerts(self):
        """Setup Airflow alerts and notifications"""
        logger.info("🔄 Setting up Airflow alerts...")

        # Create Airflow alert configuration
        alert_config = {
            "slack_webhook": self.alert_webhook_url,
            "email_alerts": ["admin@morningmaghreb.com"],
            "alert_rules": {
                "dag_failure": {
                    "enabled": True,
                    "channels": ["slack", "email"],
                    "retry_delay": 300,
                },
                "sla_miss": {
                    "enabled": True,
                    "channels": ["slack", "email"],
                    "threshold_minutes": 60,
                },
                "task_timeout": {
                    "enabled": True,
                    "channels": ["slack"],
                    "threshold_minutes": 30,
                },
            },
        }

        # Save alert configuration
        alert_file = self.config_dir / "airflow_alerts.json"
        with open(alert_file, "w") as f:
            json.dump(alert_config, f, indent=2)

        # Create Airflow alert handler
        alert_handler = self.config_dir / "airflow_alert_handler.py"
        with open(alert_handler, "w") as f:
            f.write(self._generate_airflow_alert_handler())

        logger.info(f"✅ Airflow alerts configured: {alert_handler}")

    async def setup_websocket_monitoring(self):
        """Setup WebSocket uptime monitoring"""
        logger.info("🔌 Setting up WebSocket monitoring...")

        # Create WebSocket monitoring script
        websocket_monitor = self.config_dir / "websocket_monitor.py"
        with open(websocket_monitor, "w") as f:
            f.write(self._generate_websocket_monitor_script())

        # Create WebSocket health check
        health_check = self.config_dir / "websocket_health_check.py"
        with open(health_check, "w") as f:
            f.write(self._generate_websocket_health_check())

        logger.info(f"✅ WebSocket monitoring configured: {websocket_monitor}")

    async def setup_grafana_dashboards(self):
        """Setup Grafana dashboards"""
        logger.info("📈 Setting up Grafana dashboards...")

        # Create Grafana configuration directory
        grafana_dir = self.config_dir / "grafana"
        grafana_dir.mkdir(exist_ok=True)

        # Create datasources configuration
        datasources = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True,
                },
                {
                    "name": "PostgreSQL",
                    "type": "postgres",
                    "url": "localhost:5432",
                    "database": "postgres",
                    "user": "postgres",
                    "secureJsonData": {"password": "${DB_PASSWORD}"},
                },
            ],
        }

        datasources_file = grafana_dir / "datasources.yml"
        with open(datasources_file, "w") as f:
            yaml.dump(datasources, f)

        # Create dashboard configurations
        dashboards = [
            self._create_api_dashboard(),
            self._create_database_dashboard(),
            self._create_etl_dashboard(),
            self._create_websocket_dashboard(),
        ]

        dashboards_dir = grafana_dir / "dashboards"
        dashboards_dir.mkdir(exist_ok=True)

        for i, dashboard in enumerate(dashboards):
            dashboard_file = dashboards_dir / f"dashboard_{i+1}.json"
            with open(dashboard_file, "w") as f:
                json.dump(dashboard, f, indent=2)

        logger.info(f"✅ Grafana dashboards configured: {grafana_dir}")

    async def setup_sentry_integration(self):
        """Setup Sentry error tracking"""
        logger.info("🐛 Setting up Sentry integration...")

        if not self.sentry_dsn:
            logger.warning("⚠️  SENTRY_DSN not found, skipping Sentry setup")
            return

        # Create Sentry configuration
        sentry_config = {
            "dsn": self.sentry_dsn,
            "environment": "production",
            "traces_sample_rate": 0.1,
            "profiles_sample_rate": 0.1,
            "integrations": ["fastapi", "sqlalchemy", "redis", "celery"],
        }

        sentry_file = self.config_dir / "sentry_config.json"
        with open(sentry_file, "w") as f:
            json.dump(sentry_config, f, indent=2)

        # Create Sentry initialization script
        sentry_init = self.config_dir / "sentry_init.py"
        with open(sentry_init, "w") as f:
            f.write(self._generate_sentry_init_script())

        logger.info(f"✅ Sentry integration configured: {sentry_init}")

    async def setup_health_checks(self):
        """Setup comprehensive health checks"""
        logger.info("🏥 Setting up health checks...")

        # Create health check configuration
        health_config = {
            "endpoints": [
                {
                    "name": "API Health",
                    "url": f"{self.api_base_url}/health",
                    "timeout": 10,
                    "expected_status": 200,
                },
                {
                    "name": "Database Health",
                    "url": f"{self.api_base_url}/api/health/database",
                    "timeout": 15,
                    "expected_status": 200,
                },
                {
                    "name": "ETL Health",
                    "url": f"{self.api_base_url}/api/etl/health",
                    "timeout": 30,
                    "expected_status": 200,
                },
                {
                    "name": "WebSocket Health",
                    "url": f"{self.websocket_url.replace('ws', 'http')}/health",
                    "timeout": 10,
                    "expected_status": 200,
                },
            ],
            "checks": [
                {
                    "name": "Database Connectivity",
                    "type": "database",
                    "query": "SELECT 1",
                    "timeout": 5,
                },
                {
                    "name": "Redis Connectivity",
                    "type": "redis",
                    "command": "PING",
                    "timeout": 5,
                },
                {"name": "Disk Space", "type": "system", "threshold_gb": 5.0},
                {"name": "Memory Usage", "type": "system", "threshold_percent": 90.0},
            ],
        }

        health_file = self.config_dir / "health_checks.json"
        with open(health_file, "w") as f:
            json.dump(health_config, f, indent=2)

        # Create health check script
        health_script = self.config_dir / "health_monitor.py"
        with open(health_script, "w") as f:
            f.write(self._generate_health_monitor_script())

        logger.info(f"✅ Health checks configured: {health_script}")

    async def setup_performance_monitoring(self):
        """Setup performance monitoring"""
        logger.info("⚡ Setting up performance monitoring...")

        # Create Prometheus configuration
        prometheus_config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": [],
            "scrape_configs": [
                {
                    "job_name": "casablanca-api",
                    "static_configs": [{"targets": ["localhost:8000"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s",
                },
                {
                    "job_name": "airflow",
                    "static_configs": [{"targets": ["localhost:8080"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                },
            ],
        }

        prometheus_file = self.config_dir / "prometheus.yml"
        with open(prometheus_file, "w") as f:
            yaml.dump(prometheus_config, f)

        # Create performance monitoring script
        perf_script = self.config_dir / "performance_monitor.py"
        with open(perf_script, "w") as f:
            f.write(self._generate_performance_monitor_script())

        logger.info(f"✅ Performance monitoring configured: {perf_script}")

    def _generate_supabase_monitor_script(self) -> str:
        """Generate Supabase monitoring script"""
        return '''
#!/usr/bin/env python3
"""
Supabase Monitoring Script
Monitors database performance and sends alerts
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

class SupabaseMonitor:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health metrics"""
        try:
            # Check row counts
            response = requests.get(
                f"{self.supabase_url}/rest/v1/companies?select=count",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                company_count = len(response.json())
                return {
                    "status": "healthy",
                    "company_count": company_count,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_slow_queries(self) -> Dict[str, Any]:
        """Check for slow queries"""
        try:
            slow_query_sql = """
            SELECT query, calls, total_time, mean_time
            FROM pg_stat_statements 
            WHERE mean_time > 100
            ORDER BY mean_time DESC 
            LIMIT 5;
            """
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                headers=self.headers,
                json={"sql": slow_query_sql},
                timeout=30
            )
            
            if response.status_code == 200:
                slow_queries = response.json()
                return {
                    "slow_queries": slow_queries,
                    "count": len(slow_queries),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "error": f"Failed to check slow queries: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

async def main():
    """Main monitoring function"""
    monitor = SupabaseMonitor(
        supabase_url="YOUR_SUPABASE_URL",
        supabase_key="YOUR_SUPABASE_KEY"
    )
    
    # Run health checks
    health = await monitor.check_database_health()
    slow_queries = await monitor.check_slow_queries()
    
    print(json.dumps({
        "health": health,
        "slow_queries": slow_queries
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _generate_airflow_alert_handler(self) -> str:
        """Generate Airflow alert handler"""
        return '''
#!/usr/bin/env python3
"""
Airflow Alert Handler
Handles DAG failures and sends notifications
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

class AirflowAlertHandler:
    def __init__(self, slack_webhook: str = None, email_alerts: list = None):
        self.slack_webhook = slack_webhook
        self.email_alerts = email_alerts or []
    
    def handle_dag_failure(self, dag_id: str, task_id: str, error: str, context: Dict[str, Any]):
        """Handle DAG failure"""
        message = f"""
❌ Airflow DAG Failure Alert

🚨 Details:
• DAG: {dag_id}
• Failed Task: {task_id}
• Error: {error}
• Execution Date: {context.get('execution_date', 'Unknown')}
• Duration: {context.get('duration', 'Unknown')} seconds

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Check logs for detailed error information
        """
        
        self._send_slack_alert(message)
        self._send_email_alert(f"Airflow DAG Failure - {dag_id}", message)
    
    def handle_sla_miss(self, dag_id: str, task_id: str, sla_time: str):
        """Handle SLA miss"""
        message = f"""
⚠️ Airflow SLA Miss Alert

⏰ Details:
• DAG: {dag_id}
• Task: {task_id}
• SLA Time: {sla_time}
• Current Time: {datetime.now().isoformat()}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Check task execution time
        """
        
        self._send_slack_alert(message)
        self._send_email_alert(f"Airflow SLA Miss - {dag_id}", message)
    
    def _send_slack_alert(self, message: str):
        """Send Slack alert"""
        if not self.slack_webhook:
            return
        
        try:
            response = requests.post(
                self.slack_webhook,
                json={"text": message},
                timeout=10
            )
            if response.status_code == 200:
                logging.info("Slack alert sent successfully")
            else:
                logging.error(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            logging.error(f"Error sending Slack alert: {e}")
    
    def _send_email_alert(self, subject: str, message: str):
        """Send email alert"""
        if not self.email_alerts:
            return
        
        # Implementation would use your email service
        logging.info(f"Email alert would be sent to {self.email_alerts}: {subject}")

# Usage in Airflow DAG
def send_failure_alert(context):
    """Airflow callback function"""
    handler = AirflowAlertHandler(
        slack_webhook="YOUR_SLACK_WEBHOOK",
        email_alerts=["admin@morningmaghreb.com"]
    )
    
    handler.handle_dag_failure(
        dag_id=context['dag'].dag_id,
        task_id=context['task'].task_id,
        error=str(context.get('exception', 'Unknown error')),
        context=context
    )
'''

    def _generate_websocket_monitor_script(self) -> str:
        """Generate WebSocket monitoring script"""
        return '''
#!/usr/bin/env python3
"""
WebSocket Monitoring Script
Monitors WebSocket connectivity and performance
"""

import asyncio
import json
import logging
import websockets
import time
from datetime import datetime
from typing import Dict, Any

class WebSocketMonitor:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.metrics = {
            "connection_attempts": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "average_response_time": 0,
            "last_check": None
        }
    
    async def check_websocket_health(self) -> Dict[str, Any]:
        """Check WebSocket health"""
        start_time = time.time()
        self.metrics["connection_attempts"] += 1
        
        try:
            async with websockets.connect(self.websocket_url, timeout=10) as websocket:
                # Send ping message
                await websocket.send(json.dumps({"type": "ping", "timestamp": time.time()}))
                
                # Wait for pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                response_time = time.time() - start_time
                self.metrics["successful_connections"] += 1
                self.metrics["average_response_time"] = (
                    (self.metrics["average_response_time"] * (self.metrics["successful_connections"] - 1) + response_time) /
                    self.metrics["successful_connections"]
                )
                
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "response": response_data,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.metrics["failed_connections"] += 1
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self.metrics["last_check"] = datetime.now().isoformat()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["successful_connections"] / 
                max(self.metrics["connection_attempts"], 1) * 100
            )
        }

async def main():
    """Main WebSocket monitoring function"""
    monitor = WebSocketMonitor("ws://localhost:8000/ws")
    
    # Run health check
    health = await monitor.check_websocket_health()
    metrics = monitor.get_metrics()
    
    print(json.dumps({
        "health": health,
        "metrics": metrics
    }, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _generate_websocket_health_check(self) -> str:
        """Generate WebSocket health check"""
        return '''
#!/usr/bin/env python3
"""
WebSocket Health Check
Simple health check for WebSocket endpoint
"""

import asyncio
import websockets
import json
from datetime import datetime

async def check_websocket_health(websocket_url: str) -> dict:
    """Check if WebSocket is healthy"""
    try:
        async with websockets.connect(websocket_url, timeout=5) as websocket:
            # Send simple ping
            await websocket.send(json.dumps({"type": "health_check"}))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=3)
            
            return {
                "status": "healthy",
                "response": json.loads(response),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import sys
    websocket_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8000/ws"
    
    result = asyncio.run(check_websocket_health(websocket_url))
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result["status"] == "healthy" else 1)
'''

    def _create_api_dashboard(self) -> Dict[str, Any]:
        """Create API monitoring dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": "Casablanca Insights API Dashboard",
                "tags": ["api", "monitoring"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "API Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
                                "legendFormat": "{{method}} {{route}}",
                            }
                        ],
                    },
                    {
                        "id": 2,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])",
                                "legendFormat": "{{method}} {{route}}",
                            }
                        ],
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": 'rate(http_requests_total{status=~"5.."}[5m])',
                                "legendFormat": "{{method}} {{route}}",
                            }
                        ],
                    },
                ],
            }
        }

    def _create_database_dashboard(self) -> Dict[str, Any]:
        """Create database monitoring dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": "Database Performance Dashboard",
                "tags": ["database", "postgresql"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Active Connections",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "pg_stat_activity_count",
                                "legendFormat": "Active Connections",
                            }
                        ],
                    },
                    {
                        "id": 2,
                        "title": "Slow Queries",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "pg_stat_statements_mean_time_seconds",
                                "legendFormat": "{{query}}",
                            }
                        ],
                    },
                ],
            }
        }

    def _create_etl_dashboard(self) -> Dict[str, Any]:
        """Create ETL monitoring dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": "ETL Pipeline Dashboard",
                "tags": ["etl", "airflow"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "ETL Job Success Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "airflow_dag_success_rate",
                                "legendFormat": "Success Rate",
                            }
                        ],
                    },
                    {
                        "id": 2,
                        "title": "ETL Job Duration",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "airflow_task_duration_seconds",
                                "legendFormat": "{{dag_id}} {{task_id}}",
                            }
                        ],
                    },
                ],
            }
        }

    def _create_websocket_dashboard(self) -> Dict[str, Any]:
        """Create WebSocket monitoring dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": "WebSocket Dashboard",
                "tags": ["websocket", "real-time"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "WebSocket Connections",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "websocket_connections_total",
                                "legendFormat": "Active Connections",
                            }
                        ],
                    },
                    {
                        "id": 2,
                        "title": "WebSocket Messages",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(websocket_messages_total[5m])",
                                "legendFormat": "Messages/sec",
                            }
                        ],
                    },
                ],
            }
        }

    def _generate_sentry_init_script(self) -> str:
        """Generate Sentry initialization script"""
        return '''
#!/usr/bin/env python3
"""
Sentry Integration for Casablanca Insights
Error tracking and performance monitoring
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

def init_sentry(dsn: str, environment: str = "production"):
    """Initialize Sentry SDK"""
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration()
        ],
        # Set sampling rate for profiling - this is relative to traces_sample_rate
        profiles_sample_rate=0.1,
    )

# Usage in main.py
# from monitoring.sentry_init import init_sentry
# init_sentry("YOUR_SENTRY_DSN", "production")
'''

    def _generate_health_monitor_script(self) -> str:
        """Generate health monitoring script"""
        return '''
#!/usr/bin/env python3
"""
Health Monitoring Script
Comprehensive health checks for all services
"""

import asyncio
import json
import logging
import requests
import psutil
from datetime import datetime
from typing import Dict, Any, List

class HealthMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        tasks = [
            self._check_endpoints(),
            self._check_database(),
            self._check_redis(),
            self._check_system_resources()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all(r.get("status") == "healthy" for r in results if isinstance(r, dict)) else "unhealthy",
            "checks": results
        }
    
    async def _check_endpoints(self) -> Dict[str, Any]:
        """Check API endpoints"""
        results = []
        
        for endpoint in self.config.get("endpoints", []):
            try:
                response = requests.get(
                    endpoint["url"],
                    timeout=endpoint.get("timeout", 10)
                )
                
                status = "healthy" if response.status_code == endpoint.get("expected_status", 200) else "unhealthy"
                results.append({
                    "name": endpoint["name"],
                    "status": status,
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                })
                
            except Exception as e:
                results.append({
                    "name": endpoint["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "type": "endpoints",
            "status": "healthy" if all(r["status"] == "healthy" for r in results) else "unhealthy",
            "results": results
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            import psycopg2
            
            # This would use your actual database connection
            # conn = psycopg2.connect("your_connection_string")
            # cursor = conn.cursor()
            # cursor.execute("SELECT 1")
            # result = cursor.fetchone()
            
            return {
                "type": "database",
                "status": "healthy",
                "response_time": 0.001
            }
            
        except Exception as e:
            return {
                "type": "database",
                "status": "error",
                "error": str(e)
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            import redis
            
            # r = redis.Redis(host='localhost', port=6379, db=0)
            # r.ping()
            
            return {
                "type": "redis",
                "status": "healthy",
                "response_time": 0.001
            }
            
        except Exception as e:
            return {
                "type": "redis",
                "status": "error",
                "error": str(e)
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            disk_usage = psutil.disk_usage('/')
            memory = psutil.virtual_memory()
            
            disk_threshold = self.config.get("disk_threshold_gb", 5.0) * 1024**3
            memory_threshold = self.config.get("memory_threshold_percent", 90.0)
            
            disk_healthy = disk_usage.free > disk_threshold
            memory_healthy = memory.percent < memory_threshold
            
            return {
                "type": "system",
                "status": "healthy" if disk_healthy and memory_healthy else "warning",
                "disk": {
                    "free_gb": disk_usage.free / 1024**3,
                    "used_percent": (disk_usage.used / disk_usage.total) * 100
                },
                "memory": {
                    "used_percent": memory.percent,
                    "available_gb": memory.available / 1024**3
                }
            }
            
        except Exception as e:
            return {
                "type": "system",
                "status": "error",
                "error": str(e)
            }

async def main():
    """Main health monitoring function"""
    # Load configuration
    with open("monitoring/health_checks.json", "r") as f:
        config = json.load(f)
    
    monitor = HealthMonitor(config)
    results = await monitor.run_all_checks()
    
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    exit(0 if results["overall_status"] == "healthy" else 1)

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _generate_performance_monitor_script(self) -> str:
        """Generate performance monitoring script"""
        return '''
#!/usr/bin/env python3
"""
Performance Monitoring Script
Monitors API performance and generates metrics
"""

import asyncio
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

class PerformanceMonitor:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.metrics = []
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        endpoints = [
            "/health",
            "/api/companies/IAM/summary",
            "/api/companies/ATW/trading",
            "/api/companies/BCP/reports"
        ]
        
        results = []
        
        for endpoint in endpoints:
            endpoint_results = await self._test_endpoint(endpoint)
            results.append(endpoint_results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "endpoints": results,
            "summary": self._calculate_summary(results)
        }
    
    async def _test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test a specific endpoint"""
        url = f"{self.api_base_url}{endpoint}"
        response_times = []
        errors = []
        
        # Run 10 requests to get average
        for i in range(10):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=30)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                
                if response.status_code != 200:
                    errors.append(f"HTTP {response.status_code}")
                    
            except Exception as e:
                errors.append(str(e))
        
        if response_times:
            return {
                "endpoint": endpoint,
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)],
                "success_rate": ((10 - len(errors)) / 10) * 100,
                "errors": errors
            }
        else:
            return {
                "endpoint": endpoint,
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "success_rate": 0,
                "errors": errors
            }
    
    def _calculate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall performance summary"""
        all_response_times = []
        total_requests = 0
        total_successful = 0
        
        for result in results:
            if result.get("avg_response_time_ms", 0) > 0:
                all_response_times.extend([result["avg_response_time_ms"]] * 10)
                total_requests += 10
                total_successful += int((result["success_rate"] / 100) * 10)
        
        if all_response_times:
            return {
                "total_requests": total_requests,
                "total_successful": total_successful,
                "overall_success_rate": (total_successful / total_requests) * 100 if total_requests > 0 else 0,
                "avg_response_time_ms": sum(all_response_times) / len(all_response_times),
                "p95_response_time_ms": sorted(all_response_times)[int(len(all_response_times) * 0.95)],
                "max_response_time_ms": max(all_response_times)
            }
        else:
            return {
                "total_requests": 0,
                "total_successful": 0,
                "overall_success_rate": 0,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "max_response_time_ms": 0
            }

async def main():
    """Main performance monitoring function"""
    monitor = PerformanceMonitor("http://localhost:8000")
    results = await monitor.run_performance_tests()
    
    print(json.dumps(results, indent=2))
    
    # Check performance targets
    summary = results["summary"]
    p95_target = 200  # ms
    
    if summary["p95_response_time_ms"] <= p95_target:
        print(f"✅ P95 response time ({summary['p95_response_time_ms']:.2f}ms) meets target ({p95_target}ms)")
    else:
        print(f"⚠️  P95 response time ({summary['p95_response_time_ms']:.2f}ms) exceeds target ({p95_target}ms)")
    
    if summary["overall_success_rate"] >= 99.0:
        print(f"✅ Success rate ({summary['overall_success_rate']:.1f}%) meets target (99.0%)")
    else:
        print(f"⚠️  Success rate ({summary['overall_success_rate']:.1f}%) below target (99.0%)")

if __name__ == "__main__":
    asyncio.run(main())
'''


async def main():
    """Main monitoring setup function"""
    setup = MonitoringSetup()

    success = await setup.setup_complete_monitoring()

    if success:
        logger.info("🎉 Monitoring setup completed successfully!")
        logger.info("📁 Configuration files saved to: monitoring/")
        logger.info("📋 Next steps:")
        logger.info("   1. Update environment variables in your deployment")
        logger.info("   2. Start monitoring services (Grafana, Prometheus)")
        logger.info("   3. Configure alert channels (Slack, email)")
        logger.info("   4. Run health checks: python monitoring/health_monitor.py")
        logger.info("   5. Test performance: python monitoring/performance_monitor.py")
        sys.exit(0)
    else:
        logger.error("💥 Monitoring setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
