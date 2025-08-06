#!/usr/bin/env python3
"""
Monitoring and Health Checks System
Comprehensive monitoring for Casablanca Insights infrastructure
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# Add scrapers to path
sys.path.append(str(Path(__file__).parent.parent / "scrapers"))

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class HealthMonitor:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.reports_dir = self.root_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        config = {
            "supabase_url": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
            "supabase_key": os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
            "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            "web_url": os.getenv("WEB_URL", "https://casablanca-insights.vercel.app"),
            "notification_webhook": os.getenv("SLACK_WEBHOOK_URL"),
            "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "300")),  # 5 minutes
            "critical_threshold": int(os.getenv("CRITICAL_THRESHOLD", "3")),  # 3 failures
        }
        return config
    
    def check_supabase_connection(self) -> HealthCheck:
        """Check Supabase database connection"""
        try:
            from supabase import create_client, Client
            
            if not self.config["supabase_url"] or not self.config["supabase_key"]:
                return HealthCheck(
                    name="supabase_connection",
                    status=HealthStatus.CRITICAL,
                    message="Supabase credentials not configured",
                    timestamp=datetime.now()
                )
            
            supabase: Client = create_client(
                self.config["supabase_url"],
                self.config["supabase_key"]
            )
            
            # Test connection with a simple query
            response = supabase.table('companies').select('count').limit(1).execute()
            
            return HealthCheck(
                name="supabase_connection",
                status=HealthStatus.HEALTHY,
                message="Supabase connection successful",
                timestamp=datetime.now(),
                details={"response_time": "fast"}
            )
            
        except Exception as e:
            return HealthCheck(
                name="supabase_connection",
                status=HealthStatus.CRITICAL,
                message=f"Supabase connection failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_database_tables(self) -> HealthCheck:
        """Check if required database tables exist and have data"""
        try:
            from supabase import create_client, Client
            
            supabase: Client = create_client(
                self.config["supabase_url"],
                self.config["supabase_key"]
            )
            
            required_tables = ['companies', 'market_data', 'profiles']
            table_status = {}
            
            for table in required_tables:
                try:
                    response = supabase.table(table).select('count').limit(1).execute()
                    table_status[table] = "exists"
                except Exception as e:
                    table_status[table] = f"error: {str(e)}"
            
            # Check for data in key tables
            companies_response = supabase.table('companies').select('count').execute()
            companies_count = len(companies_response.data) if companies_response.data else 0
            
            market_data_response = supabase.table('market_data').select('count').execute()
            market_data_count = len(market_data_response.data) if market_data_response.data else 0
            
            if companies_count < 5:
                status = HealthStatus.WARNING
                message = f"Low company data: {companies_count} records"
            elif market_data_count < 50:
                status = HealthStatus.WARNING
                message = f"Low market data: {market_data_count} records"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database tables healthy: {companies_count} companies, {market_data_count} market records"
            
            return HealthCheck(
                name="database_tables",
                status=status,
                message=message,
                timestamp=datetime.now(),
                details={
                    "table_status": table_status,
                    "companies_count": companies_count,
                    "market_data_count": market_data_count
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="database_tables",
                status=HealthStatus.CRITICAL,
                message=f"Database check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_scraper_health(self) -> HealthCheck:
        """Check scraper health and recent data"""
        try:
            from supabase import create_client, Client
            
            supabase: Client = create_client(
                self.config["supabase_url"],
                self.config["supabase_key"]
            )
            
            # Check for recent market data (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_data = supabase.table('market_data').select('*').gte('created_at', yesterday.isoformat()).execute()
            
            recent_count = len(recent_data.data) if recent_data.data else 0
            
            # Check for recent financial reports
            recent_reports = supabase.table('financial_reports').select('*').gte('created_at', yesterday.isoformat()).execute()
            reports_count = len(recent_reports.data) if recent_reports.data else 0
            
            if recent_count == 0:
                status = HealthStatus.CRITICAL
                message = "No recent market data found (last 24 hours)"
            elif recent_count < 10:
                status = HealthStatus.WARNING
                message = f"Low recent market data: {recent_count} records"
            else:
                status = HealthStatus.HEALTHY
                message = f"Scrapers healthy: {recent_count} recent market records, {reports_count} reports"
            
            return HealthCheck(
                name="scraper_health",
                status=status,
                message=message,
                timestamp=datetime.now(),
                details={
                    "recent_market_data": recent_count,
                    "recent_reports": reports_count,
                    "last_check": yesterday.isoformat()
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="scraper_health",
                status=HealthStatus.CRITICAL,
                message=f"Scraper health check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_web_application(self) -> HealthCheck:
        """Check web application health"""
        try:
            response = requests.get(f"{self.config['web_url']}/api/health", timeout=10)
            
            if response.status_code == 200:
                return HealthCheck(
                    name="web_application",
                    status=HealthStatus.HEALTHY,
                    message="Web application responding",
                    timestamp=datetime.now(),
                    details={"response_time": response.elapsed.total_seconds()}
                )
            else:
                return HealthCheck(
                    name="web_application",
                    status=HealthStatus.WARNING,
                    message=f"Web application returned status {response.status_code}",
                    timestamp=datetime.now()
                )
                
        except requests.exceptions.RequestException as e:
            return HealthCheck(
                name="web_application",
                status=HealthStatus.CRITICAL,
                message=f"Web application unreachable: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_api_endpoints(self) -> HealthCheck:
        """Check API endpoints health"""
        try:
            endpoints = [
                "/api/companies",
                "/api/market-data",
                "/api/macro"
            ]
            
            endpoint_status = {}
            failed_endpoints = []
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.config['web_url']}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        endpoint_status[endpoint] = "healthy"
                    else:
                        endpoint_status[endpoint] = f"status_{response.status_code}"
                        failed_endpoints.append(endpoint)
                except Exception as e:
                    endpoint_status[endpoint] = f"error: {str(e)}"
                    failed_endpoints.append(endpoint)
            
            if failed_endpoints:
                status = HealthStatus.WARNING
                message = f"Some API endpoints failed: {', '.join(failed_endpoints)}"
            else:
                status = HealthStatus.HEALTHY
                message = "All API endpoints healthy"
            
            return HealthCheck(
                name="api_endpoints",
                status=status,
                message=message,
                timestamp=datetime.now(),
                details={"endpoint_status": endpoint_status}
            )
            
        except Exception as e:
            return HealthCheck(
                name="api_endpoints",
                status=HealthStatus.CRITICAL,
                message=f"API health check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_orchestrator_status(self) -> HealthCheck:
        """Check orchestrator status and recent runs"""
        try:
            # Check if orchestrator files exist
            orchestrator_file = self.root_dir / "scrapers" / "orchestrator.py"
            
            if not orchestrator_file.exists():
                return HealthCheck(
                    name="orchestrator_status",
                    status=HealthStatus.CRITICAL,
                    message="Orchestrator file not found",
                    timestamp=datetime.now()
                )
            
            # Check for recent orchestrator logs
            logs_dir = self.root_dir / "logs"
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                recent_logs = [f for f in log_files if f.stat().st_mtime > time.time() - 86400]  # Last 24 hours
                
                if recent_logs:
                    return HealthCheck(
                        name="orchestrator_status",
                        status=HealthStatus.HEALTHY,
                        message=f"Orchestrator active with {len(recent_logs)} recent logs",
                        timestamp=datetime.now(),
                        details={"recent_logs": len(recent_logs)}
                    )
                else:
                    return HealthCheck(
                        name="orchestrator_status",
                        status=HealthStatus.WARNING,
                        message="No recent orchestrator logs found",
                        timestamp=datetime.now()
                    )
            else:
                return HealthCheck(
                    name="orchestrator_status",
                    status=HealthStatus.WARNING,
                    message="No logs directory found",
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return HealthCheck(
                name="orchestrator_status",
                status=HealthStatus.CRITICAL,
                message=f"Orchestrator check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def check_system_resources(self) -> HealthCheck:
        """Check system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine overall status
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%, Disk {disk_percent}%"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 70:
                status = HealthStatus.WARNING
                message = f"Elevated resource usage: CPU {cpu_percent}%, Memory {memory_percent}%, Disk {disk_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"System resources healthy: CPU {cpu_percent}%, Memory {memory_percent}%, Disk {disk_percent}%"
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                timestamp=datetime.now(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent
                }
            )
            
        except ImportError:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message="psutil not available for system resource check",
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"System resource check failed: {str(e)}",
                timestamp=datetime.now()
            )
    
    def run_all_health_checks(self) -> List[HealthCheck]:
        """Run all health checks"""
        print("🏥 Running Health Checks")
        print("=" * 40)
        
        checks = [
            self.check_supabase_connection(),
            self.check_database_tables(),
            self.check_scraper_health(),
            self.check_web_application(),
            self.check_api_endpoints(),
            self.check_orchestrator_status(),
            self.check_system_resources()
        ]
        
        # Print results
        for check in checks:
            status_emoji = {
                HealthStatus.HEALTHY: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.CRITICAL: "❌",
                HealthStatus.UNKNOWN: "❓"
            }.get(check.status, "❓")
            
            print(f"{status_emoji} {check.name}: {check.message}")
        
        return checks
    
    def generate_health_report(self, checks: List[HealthCheck]) -> str:
        """Generate comprehensive health report"""
        print("\n📋 Generating Health Report")
        print("-" * 40)
        
        # Calculate summary
        total_checks = len(checks)
        healthy_checks = len([c for c in checks if c.status == HealthStatus.HEALTHY])
        warning_checks = len([c for c in checks if c.status == HealthStatus.WARNING])
        critical_checks = len([c for c in checks if c.status == HealthStatus.CRITICAL])
        
        overall_status = HealthStatus.HEALTHY
        if critical_checks > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_checks > 0:
            overall_status = HealthStatus.WARNING
        
        # Generate report content
        report_content = [
            "# 🏥 Health Check Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Overall Status**: {overall_status.value.upper()}",
            "",
            "## 📊 Summary",
            "",
            f"- **Total Checks**: {total_checks}",
            f"- **Healthy**: {healthy_checks}",
            f"- **Warnings**: {warning_checks}",
            f"- **Critical**: {critical_checks}",
            f"- **Health Score**: {(healthy_checks/total_checks*100):.1f}%",
            "",
            "## 📋 Check Details",
            "",
        ]
        
        # Group checks by status
        status_groups = {
            HealthStatus.CRITICAL: [],
            HealthStatus.WARNING: [],
            HealthStatus.HEALTHY: [],
            HealthStatus.UNKNOWN: []
        }
        
        for check in checks:
            status_groups[check.status].append(check)
        
        # Add critical issues first
        if status_groups[HealthStatus.CRITICAL]:
            report_content.append("### 🚨 Critical Issues")
            for check in status_groups[HealthStatus.CRITICAL]:
                report_content.append(f"- **{check.name}**: {check.message}")
            report_content.append("")
        
        # Add warnings
        if status_groups[HealthStatus.WARNING]:
            report_content.append("### ⚠️  Warnings")
            for check in status_groups[HealthStatus.WARNING]:
                report_content.append(f"- **{check.name}**: {check.message}")
            report_content.append("")
        
        # Add healthy checks
        if status_groups[HealthStatus.HEALTHY]:
            report_content.append("### ✅ Healthy Systems")
            for check in status_groups[HealthStatus.HEALTHY]:
                report_content.append(f"- **{check.name}**: {check.message}")
            report_content.append("")
        
        # Add recommendations
        report_content.extend([
            "## 💡 Recommendations",
            "",
        ])
        
        if critical_checks > 0:
            report_content.append("### 🚨 Immediate Actions Required")
            report_content.append("The following critical issues need immediate attention:")
            for check in status_groups[HealthStatus.CRITICAL]:
                report_content.append(f"- **{check.name}**: Investigate and resolve immediately")
            report_content.append("")
        
        if warning_checks > 0:
            report_content.append("### ⚠️  Monitor Closely")
            report_content.append("The following warnings should be monitored:")
            for check in status_groups[HealthStatus.WARNING]:
                report_content.append(f"- **{check.name}**: Monitor for degradation")
            report_content.append("")
        
        if overall_status == HealthStatus.HEALTHY:
            report_content.append("### ✅ All Systems Operational")
            report_content.append("All systems are healthy. Continue monitoring for any changes.")
        
        # Add next steps
        report_content.extend([
            "",
            "## 🎯 Next Steps",
            "",
            "1. **Address Critical Issues**: Resolve any critical problems immediately",
            "2. **Monitor Warnings**: Keep an eye on warning conditions",
            "3. **Review Logs**: Check application logs for more details",
            "4. **Update Monitoring**: Adjust thresholds if needed",
            "5. **Schedule Maintenance**: Plan regular maintenance windows"
        ])
        
        return "\n".join(report_content)
    
    def send_notification(self, checks: List[HealthCheck]):
        """Send notification if there are critical issues"""
        critical_checks = [c for c in checks if c.status == HealthStatus.CRITICAL]
        
        if not critical_checks or not self.config["notification_webhook"]:
            return
        
        # Prepare notification message
        message = {
            "text": "🚨 Casablanca Insights Health Alert",
            "attachments": [{
                "color": "danger",
                "title": "Critical Health Issues Detected",
                "fields": [
                    {
                        "title": check.name,
                        "value": check.message,
                        "short": True
                    }
                    for check in critical_checks
                ],
                "footer": f"Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        }
        
        try:
            response = requests.post(
                self.config["notification_webhook"],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Notification sent successfully")
            else:
                print(f"❌ Failed to send notification: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
    
    def run_monitoring_cycle(self):
        """Run complete monitoring cycle"""
        print("🚀 Starting Health Monitoring Cycle")
        print("=" * 50)
        
        # Run all health checks
        checks = self.run_all_health_checks()
        
        # Generate report
        report = self.generate_health_report(checks)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"health_check_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save detailed results
        results_file = self.reports_dir / f"health_check_results_{timestamp}.json"
        
        # Convert checks to JSON-serializable format
        check_data = []
        for check in checks:
            check_data.append({
                "name": check.name,
                "status": check.status.value,
                "message": check.message,
                "timestamp": check.timestamp.isoformat(),
                "details": check.details
            })
        
        with open(results_file, 'w') as f:
            json.dump(check_data, f, indent=2)
        
        print(f"📄 Health report saved to: {report_file}")
        print(f"📊 Detailed results saved to: {results_file}")
        
        # Send notifications if needed
        self.send_notification(checks)
        
        # Print summary
        critical_count = len([c for c in checks if c.status == HealthStatus.CRITICAL])
        warning_count = len([c for c in checks if c.status == HealthStatus.WARNING])
        
        print(f"\n📊 Health Summary:")
        print(f"   Critical Issues: {critical_count}")
        print(f"   Warnings: {warning_count}")
        
        if critical_count > 0:
            print("\n🚨 CRITICAL: Immediate attention required!")
        elif warning_count > 0:
            print("\n⚠️  WARNING: Monitor closely")
        else:
            print("\n✅ HEALTHY: All systems operational")

def main():
    """Main monitoring execution"""
    monitor = HealthMonitor()
    monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main() 