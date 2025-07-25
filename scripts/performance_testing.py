#!/usr/bin/env python3
"""
Performance Testing Script for Casablanca Insights API
Uses Locust to test endpoints with 78 companies and measure response times
"""

import os
import sys
import asyncio
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTester:
    """Performance testing for Casablanca Insights API"""
    
    def __init__(self, base_url: str, companies: List[str]):
        self.base_url = base_url.rstrip('/')
        self.companies = companies
        self.results = []
        
    def run_basic_performance_tests(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        logger.info("🚀 Starting basic performance tests...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_companies": len(self.companies),
            "endpoints": {},
            "summary": {}
        }
        
        # Test each endpoint
        endpoints = [
            ("summary", "/api/companies/{ticker}/summary"),
            ("trading", "/api/companies/{ticker}/trading"),
            ("reports", "/api/companies/{ticker}/reports"),
            ("news", "/api/companies/{ticker}/news")
        ]
        
        for endpoint_name, endpoint_path in endpoints:
            logger.info(f"Testing {endpoint_name} endpoint...")
            
            endpoint_results = self._test_endpoint(endpoint_name, endpoint_path)
            test_results["endpoints"][endpoint_name] = endpoint_results
            
            # Log summary
            avg_time = endpoint_results["avg_response_time_ms"]
            p95_time = endpoint_results["p95_response_time_ms"]
            success_rate = endpoint_results["success_rate"]
            
            logger.info(f"✅ {endpoint_name}: {avg_time:.2f}ms avg, {p95_time:.2f}ms p95, {success_rate:.1f}% success")
        
        # Calculate overall summary
        test_results["summary"] = self._calculate_summary(test_results["endpoints"])
        
        return test_results
    
    def _test_endpoint(self, endpoint_name: str, endpoint_path: str) -> Dict[str, Any]:
        """Test a specific endpoint with all companies"""
        results = {
            "endpoint": endpoint_name,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": []
        }
        
        for ticker in self.companies:
            url = f"{self.base_url}{endpoint_path.format(ticker=ticker)}"
            
            try:
                start_time = time.time()
                response = requests.get(url, timeout=30)
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                results["response_times"].append(response_time_ms)
                results["total_requests"] += 1
                
                if response.status_code == 200:
                    results["successful_requests"] += 1
                else:
                    results["failed_requests"] += 1
                    results["errors"].append({
                        "ticker": ticker,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    })
                    
            except Exception as e:
                results["failed_requests"] += 1
                results["total_requests"] += 1
                results["errors"].append({
                    "ticker": ticker,
                    "status_code": None,
                    "error": str(e)
                })
        
        # Calculate statistics
        if results["response_times"]:
            results["avg_response_time_ms"] = sum(results["response_times"]) / len(results["response_times"])
            results["min_response_time_ms"] = min(results["response_times"])
            results["max_response_time_ms"] = max(results["response_times"])
            results["p95_response_time_ms"] = sorted(results["response_times"])[int(len(results["response_times"]) * 0.95)]
            results["p99_response_time_ms"] = sorted(results["response_times"])[int(len(results["response_times"]) * 0.99)]
        else:
            results["avg_response_time_ms"] = 0
            results["min_response_time_ms"] = 0
            results["max_response_time_ms"] = 0
            results["p95_response_time_ms"] = 0
            results["p99_response_time_ms"] = 0
        
        results["success_rate"] = (results["successful_requests"] / results["total_requests"]) * 100 if results["total_requests"] > 0 else 0
        
        return results
    
    def _calculate_summary(self, endpoints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance summary"""
        all_response_times = []
        total_requests = 0
        total_successful = 0
        
        for endpoint_data in endpoints.values():
            all_response_times.extend(endpoint_data["response_times"])
            total_requests += endpoint_data["total_requests"]
            total_successful += endpoint_data["successful_requests"]
        
        if all_response_times:
            summary = {
                "total_requests": total_requests,
                "total_successful": total_successful,
                "overall_success_rate": (total_successful / total_requests) * 100 if total_requests > 0 else 0,
                "avg_response_time_ms": sum(all_response_times) / len(all_response_times),
                "p95_response_time_ms": sorted(all_response_times)[int(len(all_response_times) * 0.95)],
                "p99_response_time_ms": sorted(all_response_times)[int(len(all_response_times) * 0.99)],
                "max_response_time_ms": max(all_response_times),
                "min_response_time_ms": min(all_response_times)
            }
        else:
            summary = {
                "total_requests": 0,
                "total_successful": 0,
                "overall_success_rate": 0,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "max_response_time_ms": 0,
                "min_response_time_ms": 0
            }
        
        return summary

class LocustTester:
    """Locust-based load testing"""
    
    def __init__(self, base_url: str, companies: List[str]):
        self.base_url = base_url
        self.companies = companies
        self.locust_file = self._create_locust_file()
    
    def _create_locust_file(self) -> str:
        """Create Locust test file"""
        locust_content = f'''
import random
from locust import HttpUser, task, between

class CasablancaInsightsUser(HttpUser):
    wait_time = between(1, 3)
    
    companies = {self.companies}
    
    @task(3)
    def get_company_summary(self):
        """Test company summary endpoint"""
        ticker = random.choice(self.companies)
        self.client.get(f"/api/companies/{{ticker}}/summary")
    
    @task(2)
    def get_company_trading(self):
        """Test company trading endpoint"""
        ticker = random.choice(self.companies)
        self.client.get(f"/api/companies/{{ticker}}/trading?days=90")
    
    @task(1)
    def get_company_reports(self):
        """Test company reports endpoint"""
        ticker = random.choice(self.companies)
        self.client.get(f"/api/companies/{{ticker}}/reports?limit=10")
    
    @task(1)
    def get_company_news(self):
        """Test company news endpoint"""
        ticker = random.choice(self.companies)
        self.client.get(f"/api/companies/{{ticker}}/news?days=30")
'''
        
        locust_file = Path("locustfile.py")
        with open(locust_file, 'w') as f:
            f.write(locust_content)
        
        return str(locust_file)
    
    def run_load_test(self, users: int = 10, spawn_rate: int = 2, run_time: str = "5m") -> bool:
        """Run Locust load test"""
        logger.info(f"🚀 Starting Locust load test: {users} users, {spawn_rate}/s spawn rate, {run_time} duration")
        
        try:
            cmd = [
                "locust",
                "-f", self.locust_file,
                "--host", self.base_url,
                "--users", str(users),
                "--spawn-rate", str(spawn_rate),
                "--run-time", run_time,
                "--headless",
                "--html", "load_test_results.html",
                "--csv", "load_test_results"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("✅ Load test completed successfully")
                return True
            else:
                logger.error(f"❌ Load test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Load test error: {e}")
            return False

class DatabaseQueryAnalyzer:
    """Analyze database query performance"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow queries in the database"""
        logger.info("🔍 Analyzing database query performance...")
        
        try:
            # Query to find slow queries
            slow_query_sql = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows,
                shared_blks_hit,
                shared_blks_read
            FROM pg_stat_statements 
            WHERE mean_time > 100  -- Queries taking more than 100ms on average
            ORDER BY mean_time DESC 
            LIMIT 10;
            """
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/rpc/exec_sql",
                headers=self.headers,
                json={"sql": slow_query_sql},
                timeout=30
            )
            
            if response.status_code == 200:
                slow_queries = response.json()
                logger.info(f"✅ Found {len(slow_queries)} slow queries")
                
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "slow_queries": slow_queries,
                    "recommendations": self._generate_recommendations(slow_queries)
                }
                
                return analysis
            else:
                logger.error(f"❌ Failed to analyze slow queries: {response.status_code}")
                return {"error": "Failed to analyze slow queries"}
                
        except Exception as e:
            logger.error(f"❌ Query analysis failed: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, slow_queries: List[Dict]) -> List[str]:
        """Generate recommendations for slow queries"""
        recommendations = []
        
        for query in slow_queries:
            query_text = query.get('query', '')
            mean_time = query.get('mean_time', 0)
            
            if 'companies' in query_text.lower() and 'ticker' in query_text.lower():
                recommendations.append(f"Consider adding index on companies(ticker) for query taking {mean_time:.2f}ms")
            
            if 'company_prices' in query_text.lower() and 'date' in query_text.lower():
                recommendations.append(f"Consider adding index on company_prices(ticker, date) for query taking {mean_time:.2f}ms")
            
            if 'company_reports' in query_text.lower():
                recommendations.append(f"Consider adding index on company_reports(ticker, report_type) for query taking {mean_time:.2f}ms")
            
            if 'company_news' in query_text.lower():
                recommendations.append(f"Consider adding index on company_news(ticker, published_at) for query taking {mean_time:.2f}ms")
        
        return recommendations

def get_casablanca_companies() -> List[str]:
    """Get list of Casablanca Stock Exchange companies"""
    # This is a sample list - you should fetch this from your database
    companies = [
        "IAM", "ATW", "BCP", "BMCE", "CIH", "CMT", "CTM", "DEL", "DHO", "DRI",
        "FBR", "FSTR", "IAM", "JET", "LES", "MNG", "MOR", "MUT", "PJD", "SAM",
        "SID", "SNP", "SOT", "TMA", "WAA", "WAL", "ZAL", "ZIN", "ZMA", "ZMS",
        # Add more companies to reach 78 total
        "ADI", "ATL", "ATW", "BCP", "BMCE", "CIH", "CMT", "CTM", "DEL", "DHO",
        "DRI", "FBR", "FSTR", "IAM", "JET", "LES", "MNG", "MOR", "MUT", "PJD",
        "SAM", "SID", "SNP", "SOT", "TMA", "WAA", "WAL", "ZAL", "ZIN", "ZMA",
        "ZMS", "ADI", "ATL", "ATW", "BCP", "BMCE", "CIH", "CMT", "CTM", "DEL",
        "DHO", "DRI", "FBR", "FSTR", "IAM", "JET", "LES", "MNG", "MOR", "MUT"
    ]
    
    # Remove duplicates and ensure we have 78 companies
    unique_companies = list(set(companies))[:78]
    
    if len(unique_companies) < 78:
        logger.warning(f"⚠️  Only {len(unique_companies)} unique companies found, adding duplicates")
        while len(unique_companies) < 78:
            unique_companies.append(unique_companies[len(unique_companies) % len(unique_companies)])
    
    return unique_companies[:78]

async def main():
    """Main performance testing function"""
    # Configuration
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Get companies
    companies = get_casablanca_companies()
    logger.info(f"📊 Testing with {len(companies)} companies")
    
    # Create results directory
    results_dir = Path("performance_results")
    results_dir.mkdir(exist_ok=True)
    
    # 1. Basic Performance Tests
    logger.info("=" * 50)
    logger.info("BASIC PERFORMANCE TESTS")
    logger.info("=" * 50)
    
    basic_tester = PerformanceTester(base_url, companies)
    basic_results = basic_tester.run_basic_performance_tests()
    
    # Save basic results
    basic_results_file = results_dir / f"basic_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(basic_results_file, 'w') as f:
        json.dump(basic_results, f, indent=2)
    
    logger.info(f"✅ Basic performance results saved: {basic_results_file}")
    
    # 2. Load Testing with Locust
    logger.info("=" * 50)
    logger.info("LOAD TESTING WITH LOCUST")
    logger.info("=" * 50)
    
    try:
        locust_tester = LocustTester(base_url, companies)
        locust_success = locust_tester.run_load_test(users=20, spawn_rate=5, run_time="10m")
        
        if locust_success:
            logger.info("✅ Load testing completed")
        else:
            logger.error("❌ Load testing failed")
    except Exception as e:
        logger.error(f"❌ Load testing error: {e}")
    
    # 3. Database Query Analysis
    logger.info("=" * 50)
    logger.info("DATABASE QUERY ANALYSIS")
    logger.info("=" * 50)
    
    if supabase_url and supabase_key:
        db_analyzer = DatabaseQueryAnalyzer(supabase_url, supabase_key)
        query_analysis = db_analyzer.analyze_slow_queries()
        
        # Save query analysis
        query_analysis_file = results_dir / f"query_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(query_analysis_file, 'w') as f:
            json.dump(query_analysis, f, indent=2)
        
        logger.info(f"✅ Query analysis saved: {query_analysis_file}")
    else:
        logger.warning("⚠️  Skipping database query analysis (missing Supabase credentials)")
    
    # 4. Performance Summary
    logger.info("=" * 50)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("=" * 50)
    
    summary = basic_results["summary"]
    logger.info(f"Total Requests: {summary['total_requests']}")
    logger.info(f"Success Rate: {summary['overall_success_rate']:.1f}%")
    logger.info(f"Average Response Time: {summary['avg_response_time_ms']:.2f}ms")
    logger.info(f"P95 Response Time: {summary['p95_response_time_ms']:.2f}ms")
    logger.info(f"P99 Response Time: {summary['p99_response_time_ms']:.2f}ms")
    
    # Check performance targets
    p95_target = 200  # ms
    if summary['p95_response_time_ms'] <= p95_target:
        logger.info(f"✅ P95 response time ({summary['p95_response_time_ms']:.2f}ms) meets target ({p95_target}ms)")
    else:
        logger.warning(f"⚠️  P95 response time ({summary['p95_response_time_ms']:.2f}ms) exceeds target ({p95_target}ms)")
    
    if summary['overall_success_rate'] >= 99.0:
        logger.info(f"✅ Success rate ({summary['overall_success_rate']:.1f}%) meets target (99.0%)")
    else:
        logger.warning(f"⚠️  Success rate ({summary['overall_success_rate']:.1f}%) below target (99.0%)")
    
    logger.info("=" * 50)
    logger.info("PERFORMANCE TESTING COMPLETED")
    logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 