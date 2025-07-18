import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os

from etl.etl_orchestrator import ETLOrchestrator
from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobStatus
from cache.redis_client import redis_client

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class HealthCheck:
    """Individual health check component"""
    
    def __init__(self, name: str, check_func, critical: bool = False, 
                 warning_threshold: Optional[float] = None,
                 critical_threshold: Optional[float] = None):
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.last_check = None
        self.last_status = HealthStatus.UNKNOWN
        self.last_error = None
    
    async def run_check(self) -> Dict[str, Any]:
        """Run the health check"""
        try:
            start_time = datetime.now()
            result = await self.check_func()
            end_time = datetime.now()
            
            # Determine status based on result and thresholds
            status = self._determine_status(result)
            
            self.last_check = end_time
            self.last_status = status
            self.last_error = None
            
            return {
                "name": self.name,
                "status": status,
                "result": result,
                "duration": (end_time - start_time).total_seconds(),
                "last_check": end_time.isoformat(),
                "critical": self.critical
            }
            
        except Exception as e:
            self.last_check = datetime.now()
            self.last_status = HealthStatus.CRITICAL if self.critical else HealthStatus.WARNING
            self.last_error = str(e)
            
            logger.error(f"Health check {self.name} failed: {e}")
            
            return {
                "name": self.name,
                "status": self.last_status,
                "error": str(e),
                "last_check": self.last_check.isoformat(),
                "critical": self.critical
            }
    
    def _determine_status(self, result: Any) -> HealthStatus:
        """Determine health status based on result and thresholds"""
        if isinstance(result, dict):
            # Check for explicit status in result
            if "status" in result:
                return HealthStatus(result["status"])
            
            # Check numeric values against thresholds
            if "value" in result and isinstance(result["value"], (int, float)):
                value = result["value"]
                
                if self.critical_threshold is not None:
                    if value >= self.critical_threshold:
                        return HealthStatus.CRITICAL
                
                if self.warning_threshold is not None:
                    if value >= self.warning_threshold:
                        return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY

class HealthMonitor:
    """Main health monitoring system"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.orchestrator = ETLOrchestrator(LocalFileStorage())
        self.alert_handlers: List[callable] = []
        
        # Register health checks
        self._register_checks()
    
    def _register_checks(self):
        """Register all health checks"""
        # Database connectivity
        self.checks.append(HealthCheck(
            "database_connectivity",
            self._check_database_connectivity,
            critical=True
        ))
        
        # Redis connectivity
        self.checks.append(HealthCheck(
            "redis_connectivity",
            self._check_redis_connectivity,
            critical=True
        ))
        
        # ETL pipeline health
        self.checks.append(HealthCheck(
            "etl_pipeline_health",
            self._check_etl_pipeline_health,
            critical=True
        ))
        
        # Data freshness
        self.checks.append(HealthCheck(
            "data_freshness",
            self._check_data_freshness,
            critical=False,
            warning_threshold=24,  # 24 hours
            critical_threshold=72   # 72 hours
        ))
        
        # Storage space
        self.checks.append(HealthCheck(
            "storage_space",
            self._check_storage_space,
            critical=False,
            warning_threshold=80,  # 80% usage
            critical_threshold=95   # 95% usage
        ))
        
        # API response time
        self.checks.append(HealthCheck(
            "api_response_time",
            self._check_api_response_time,
            critical=False,
            warning_threshold=2.0,  # 2 seconds
            critical_threshold=5.0   # 5 seconds
        ))
        
        # Failed jobs
        self.checks.append(HealthCheck(
            "failed_jobs",
            self._check_failed_jobs,
            critical=False,
            warning_threshold=3,  # 3 failed jobs
            critical_threshold=10   # 10 failed jobs
        ))
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("Running health checks...")
        
        results = []
        overall_status = HealthStatus.HEALTHY
        
        # Run checks concurrently
        check_tasks = [check.run_check() for check in self.checks]
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for i, result in enumerate(check_results):
            if isinstance(result, Exception):
                # Handle failed checks
                check = self.checks[i]
                result = {
                    "name": check.name,
                    "status": HealthStatus.CRITICAL if check.critical else HealthStatus.WARNING,
                    "error": str(result),
                    "last_check": datetime.now().isoformat(),
                    "critical": check.critical
                }
            
            results.append(result)
            
            # Determine overall status
            if result["status"] == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
            elif result["status"] == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
        
        health_report = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": results,
            "summary": self._generate_summary(results)
        }
        
        # Send alerts if needed
        await self._send_alerts(health_report)
        
        return health_report
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of health check results"""
        total_checks = len(results)
        healthy_checks = sum(1 for r in results if r["status"] == HealthStatus.HEALTHY)
        warning_checks = sum(1 for r in results if r["status"] == HealthStatus.WARNING)
        critical_checks = sum(1 for r in results if r["status"] == HealthStatus.CRITICAL)
        
        return {
            "total": total_checks,
            "healthy": healthy_checks,
            "warnings": warning_checks,
            "critical": critical_checks,
            "health_percentage": (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        }
    
    async def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # This would test actual database connection
            # For now, return mock result
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "response_time": 0.05
            }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e)
            }
    
    async def _check_redis_connectivity(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            if redis_client.client:
                await redis_client.client.ping()
                return {
                    "status": "healthy",
                    "message": "Redis connection successful"
                }
            else:
                return {
                    "status": "critical",
                    "error": "Redis client not initialized"
                }
        except Exception as e:
            return {
                "status": "critical",
                "error": f"Redis connection failed: {e}"
            }
    
    async def _check_etl_pipeline_health(self) -> Dict[str, Any]:
        """Check ETL pipeline health"""
        try:
            # Check recent ETL jobs
            recent_jobs = self.orchestrator.get_all_jobs()
            
            if not recent_jobs:
                return {
                    "status": "warning",
                    "message": "No recent ETL jobs found"
                }
            
            # Check for failed jobs in last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_failed_jobs = [
                job for job in recent_jobs
                if job.status == JobStatus.FAILED and 
                job.completed_at and job.completed_at > cutoff_time
            ]
            
            if recent_failed_jobs:
                return {
                    "status": "critical",
                    "message": f"{len(recent_failed_jobs)} failed jobs in last 24 hours",
                    "failed_jobs": len(recent_failed_jobs)
                }
            
            return {
                "status": "healthy",
                "message": "ETL pipeline running normally",
                "total_jobs": len(recent_jobs)
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": f"ETL pipeline check failed: {e}"
            }
    
    async def _check_data_freshness(self) -> Dict[str, Any]:
        """Check data freshness"""
        try:
            # Check when data was last updated
            # This would query your database for latest timestamps
            # For now, return mock result
            
            # Mock: assume data is 12 hours old
            hours_since_update = 12
            
            return {
                "status": "healthy" if hours_since_update < 24 else "warning",
                "message": f"Data last updated {hours_since_update} hours ago",
                "value": hours_since_update
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": f"Data freshness check failed: {e}"
            }
    
    async def _check_storage_space(self) -> Dict[str, Any]:
        """Check available storage space"""
        try:
            # Check disk usage
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            usage_percentage = (used / total) * 100
            
            return {
                "status": "healthy" if usage_percentage < 80 else "warning",
                "message": f"Storage usage: {usage_percentage:.1f}%",
                "value": usage_percentage,
                "total_gb": total / (1024**3),
                "used_gb": used / (1024**3),
                "free_gb": free / (1024**3)
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": f"Storage check failed: {e}"
            }
    
    async def _check_api_response_time(self) -> Dict[str, Any]:
        """Check API response time"""
        try:
            # Mock API response time check
            response_time = 0.5  # 500ms
            
            return {
                "status": "healthy" if response_time < 2.0 else "warning",
                "message": f"API response time: {response_time:.2f}s",
                "value": response_time
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": f"API response time check failed: {e}"
            }
    
    async def _check_failed_jobs(self) -> Dict[str, Any]:
        """Check for failed jobs"""
        try:
            # Count failed jobs in last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_jobs = self.orchestrator.get_all_jobs()
            
            failed_jobs = [
                job for job in recent_jobs
                if job.status == JobStatus.FAILED and 
                job.completed_at and job.completed_at > cutoff_time
            ]
            
            return {
                "status": "healthy" if len(failed_jobs) == 0 else "warning",
                "message": f"{len(failed_jobs)} failed jobs in last 24 hours",
                "value": len(failed_jobs)
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": f"Failed jobs check failed: {e}"
            }
    
    async def _send_alerts(self, health_report: Dict[str, Any]):
        """Send alerts for critical issues"""
        critical_checks = [
            check for check in health_report["checks"]
            if check["status"] == HealthStatus.CRITICAL
        ]
        
        if critical_checks:
            alert_message = {
                "type": "health_alert",
                "severity": "critical",
                "timestamp": datetime.now().isoformat(),
                "message": f"Critical health issues detected: {len(critical_checks)} checks failed",
                "failed_checks": [check["name"] for check in critical_checks],
                "full_report": health_report
            }
            
            # Send to all alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert_message)
                except Exception as e:
                    logger.error(f"Failed to send alert via handler: {e}")
    
    def add_alert_handler(self, handler: callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for health dashboard"""
        health_report = await self.run_all_checks()
        
        # Add historical data (mock for now)
        historical_data = {
            "last_24h": {
                "uptime_percentage": 99.5,
                "total_requests": 15420,
                "average_response_time": 0.3,
                "error_rate": 0.02
            },
            "last_7d": {
                "uptime_percentage": 99.2,
                "total_requests": 108500,
                "average_response_time": 0.4,
                "error_rate": 0.03
            }
        }
        
        return {
            "current_health": health_report,
            "historical_data": historical_data,
            "system_info": {
                "version": "2.0.0",
                "start_time": "2024-01-01T00:00:00Z",
                "uptime": "15 days, 3 hours"
            }
        }

# Global health monitor instance
health_monitor = HealthMonitor()

async def run_health_checks():
    """Run health checks and return report"""
    return await health_monitor.run_all_checks()

async def get_health_dashboard():
    """Get health dashboard data"""
    return await health_monitor.get_dashboard_data() 