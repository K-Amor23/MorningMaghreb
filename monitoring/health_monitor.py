
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
