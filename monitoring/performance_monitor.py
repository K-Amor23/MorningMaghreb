
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
