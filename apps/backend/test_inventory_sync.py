#!/usr/bin/env python3
"""
Comprehensive test script for inventory sync functionality
Tests Business Central and Zoho integration with detailed logging
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import json
import httpx
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('inventory_sync_test.log')
    ]
)
logger = logging.getLogger(__name__)

class InventorySyncAuditor:
    """Comprehensive auditor for inventory sync functionality"""
    
    def __init__(self):
        self.test_results = []
        self.server_url = "http://localhost:8000"
        self.start_time = datetime.now()
        
    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result with timestamp"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now(),
            "details": details
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        logger.info(f"{status_symbol} {test_name}: {status}")
        
        if details:
            for key, value in details.items():
                logger.info(f"  {key}: {value}")

    async def test_server_startup(self):
        """Test if the server starts successfully"""
        logger.info("=" * 60)
        logger.info("TESTING SERVER STARTUP")
        logger.info("=" * 60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/health", timeout=10.0)
                
                if response.status_code == 200:
                    self.log_test_result(
                        "Server Health Check",
                        "PASS",
                        {
                            "status_code": response.status_code,
                            "response_time_ms": response.elapsed.total_seconds() * 1000,
                            "server_status": "healthy"
                        }
                    )
                else:
                    self.log_test_result(
                        "Server Health Check",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": "Server not healthy"
                        }
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Server Health Check",
                "FAIL",
                {
                    "error": str(e),
                    "suggestion": "Make sure server is running with: uvicorn main:app --reload"
                }
            )

    async def test_inventory_endpoints(self):
        """Test inventory sync endpoints"""
        logger.info("=" * 60)
        logger.info("TESTING INVENTORY SYNC ENDPOINTS")
        logger.info("=" * 60)
        
        endpoints = [
            ("/api/inventory/health", "GET", "Inventory Health Check"),
            ("/api/inventory/test-bc-connection", "GET", "Business Central Connection Test"),
            ("/api/inventory/test-zoho-connection", "GET", "Zoho Connection Test"),
            ("/api/inventory/history", "GET", "Sync History"),
            ("/api/inventory/logs", "GET", "Sync Logs")
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, method, test_name in endpoints:
                try:
                    url = f"{self.server_url}{endpoint}"
                    response = await client.request(method, url, timeout=30.0)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        self.log_test_result(
                            test_name,
                            "PASS",
                            {
                                "status_code": response.status_code,
                                "response_time_ms": response.elapsed.total_seconds() * 1000,
                                "endpoint": endpoint,
                                "response_keys": list(response_data.keys()) if isinstance(response_data, dict) else "non-dict"
                            }
                        )
                    else:
                        self.log_test_result(
                            test_name,
                            "FAIL",
                            {
                                "status_code": response.status_code,
                                "endpoint": endpoint,
                                "error": response.text[:200]
                            }
                        )
                        
                except Exception as e:
                    self.log_test_result(
                        test_name,
                        "FAIL",
                        {
                            "endpoint": endpoint,
                            "error": str(e)
                        }
                    )

    async def test_business_central_integration(self):
        """Test Business Central integration specifically"""
        logger.info("=" * 60)
        logger.info("TESTING BUSINESS CENTRAL INTEGRATION")
        logger.info("=" * 60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/api/inventory/test-bc-connection",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        self.log_test_result(
                            "Business Central OAuth Token",
                            "PASS",
                            {
                                "status_code": response.status_code,
                                "bc_status": data.get("status"),
                                "response_preview": data.get("response_preview", "")[:100]
                            }
                        )
                    else:
                        self.log_test_result(
                            "Business Central OAuth Token",
                            "FAIL",
                            {
                                "bc_status": data.get("status"),
                                "error": data.get("error", "Unknown error"),
                                "suggestion": "Check BC_CLIENT_ID, BC_CLIENT_SECRET, BC_TENANT_ID environment variables"
                            }
                        )
                else:
                    self.log_test_result(
                        "Business Central OAuth Token",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": response.text[:200]
                        }
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Business Central OAuth Token",
                "FAIL",
                {
                    "error": str(e),
                    "suggestion": "Check network connectivity and BC configuration"
                }
            )

    async def test_zoho_integration(self):
        """Test Zoho integration specifically"""
        logger.info("=" * 60)
        logger.info("TESTING ZOHO INTEGRATION")
        logger.info("=" * 60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/api/inventory/test-zoho-connection",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        self.log_test_result(
                            "Zoho OAuth Token",
                            "PASS",
                            {
                                "status_code": response.status_code,
                                "zoho_status": data.get("status"),
                                "response_preview": data.get("response_preview", "")[:100]
                            }
                        )
                    else:
                        self.log_test_result(
                            "Zoho OAuth Token",
                            "FAIL",
                            {
                                "zoho_status": data.get("status"),
                                "error": data.get("error", "Unknown error"),
                                "suggestion": "Check ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN environment variables"
                            }
                        )
                else:
                    self.log_test_result(
                        "Zoho OAuth Token",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": response.text[:200]
                        }
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Zoho OAuth Token",
                "FAIL",
                {
                    "error": str(e),
                    "suggestion": "Check network connectivity and Zoho configuration"
                }
            )

    async def test_full_inventory_sync(self):
        """Test the full inventory sync process"""
        logger.info("=" * 60)
        logger.info("TESTING FULL INVENTORY SYNC")
        logger.info("=" * 60)
        
        try:
            async with httpx.AsyncClient() as client:
                # Start sync
                logger.info("Initiating inventory sync...")
                response = await client.post(
                    f"{self.server_url}/api/inventory/sync",
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    sync_status = data.get("status")
                    items_processed = data.get("items_processed", 0)
                    items_synced = data.get("items_synced", 0)
                    errors = data.get("errors", [])
                    duration = data.get("duration_seconds", 0)
                    
                    if sync_status == "success":
                        self.log_test_result(
                            "Full Inventory Sync",
                            "PASS",
                            {
                                "status": sync_status,
                                "items_processed": items_processed,
                                "items_synced": items_synced,
                                "duration_seconds": duration,
                                "errors_count": len(errors)
                            }
                        )
                    elif sync_status == "partial":
                        self.log_test_result(
                            "Full Inventory Sync",
                            "WARN",
                            {
                                "status": sync_status,
                                "items_processed": items_processed,
                                "items_synced": items_synced,
                                "duration_seconds": duration,
                                "errors_count": len(errors),
                                "first_error": errors[0] if errors else None
                            }
                        )
                    else:
                        self.log_test_result(
                            "Full Inventory Sync",
                            "FAIL",
                            {
                                "status": sync_status,
                                "items_processed": items_processed,
                                "items_synced": items_synced,
                                "errors_count": len(errors),
                                "errors": errors[:3]  # First 3 errors
                            }
                        )
                else:
                    self.log_test_result(
                        "Full Inventory Sync",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": response.text[:200]
                        }
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Full Inventory Sync",
                "FAIL",
                {
                    "error": str(e),
                    "suggestion": "Check both BC and Zoho configurations"
                }
            )

    async def audit_configuration(self):
        """Audit the configuration and environment setup"""
        logger.info("=" * 60)
        logger.info("AUDITING CONFIGURATION")
        logger.info("=" * 60)
        
        # Check environment variables
        required_env_vars = [
            "BC_TENANT_ID",
            "BC_ENVIRONMENT", 
            "BC_COMPANY_ID",
            "BC_CLIENT_ID",
            "BC_CLIENT_SECRET",
            "ZOHO_CLIENT_ID",
            "ZOHO_CLIENT_SECRET",
            "ZOHO_REFRESH_TOKEN"
        ]
        
        missing_vars = []
        test_vars = []
        
        for var in required_env_vars:
            value = os.getenv(var, "")
            if not value:
                missing_vars.append(var)
            elif value.startswith("test-"):
                test_vars.append(var)
        
        if missing_vars:
            self.log_test_result(
                "Environment Variables Check",
                "FAIL",
                {
                    "missing_variables": missing_vars,
                    "suggestion": "Set required environment variables for production"
                }
            )
        elif test_vars:
            self.log_test_result(
                "Environment Variables Check",
                "WARN",
                {
                    "test_variables": test_vars,
                    "suggestion": "Replace test values with actual credentials"
                }
            )
        else:
            self.log_test_result(
                "Environment Variables Check",
                "PASS",
                {
                    "all_variables_set": True,
                    "variables_count": len(required_env_vars)
                }
            )

    async def check_server_logs(self):
        """Check server logs for any issues"""
        logger.info("=" * 60)
        logger.info("CHECKING SERVER LOGS")
        logger.info("=" * 60)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/api/inventory/logs")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "Server Logs Check",
                        "PASS",
                        {
                            "logs_accessible": True,
                            "log_level": data.get("log_level", "INFO"),
                            "suggestion": "Check console output for detailed logs"
                        }
                    )
                else:
                    self.log_test_result(
                        "Server Logs Check",
                        "FAIL",
                        {
                            "status_code": response.status_code,
                            "error": "Could not access logs endpoint"
                        }
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Server Logs Check",
                "FAIL",
                {
                    "error": str(e)
                }
            )

    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        logger.info("=" * 60)
        logger.info("GENERATING AUDIT REPORT")
        logger.info("=" * 60)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warned = sum(1 for r in self.test_results if r["status"] == "WARN")
        
        report = {
            "audit_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_tests": len(self.test_results),
                "passed": passed,
                "failed": failed,
                "warnings": warned,
                "success_rate": (passed / len(self.test_results)) * 100 if self.test_results else 0
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        with open("inventory_sync_audit_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info(f"Audit completed in {duration:.2f} seconds")
        logger.info(f"Tests: {len(self.test_results)} total, {passed} passed, {failed} failed, {warned} warnings")
        logger.info(f"Success rate: {report['audit_summary']['success_rate']:.1f}%")
        
        if failed > 0:
            logger.error("❌ Some tests failed. Check the detailed report for issues.")
        elif warned > 0:
            logger.warning("⚠️ Some tests had warnings. Review recommendations.")
        else:
            logger.info("✅ All tests passed successfully!")
        
        return report

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r["status"] == "FAIL"]
        warned_tests = [r for r in self.test_results if r["status"] == "WARN"]
        
        if any("Server Health Check" in r["test_name"] for r in failed_tests):
            recommendations.append("Start the server with: cd apps/backend && uvicorn main:app --reload")
        
        if any("Business Central" in r["test_name"] for r in failed_tests):
            recommendations.append("Configure Business Central OAuth credentials in environment variables")
            recommendations.append("Verify Azure AD app registration and permissions")
            recommendations.append("Check if application user is created in Business Central")
        
        if any("Zoho" in r["test_name"] for r in failed_tests):
            recommendations.append("Configure Zoho OAuth credentials in environment variables")
            recommendations.append("Verify Zoho app registration and refresh token")
        
        if any("Environment Variables" in r["test_name"] for r in failed_tests + warned_tests):
            recommendations.append("Set all required environment variables with actual values")
            recommendations.append("Replace test values with production credentials")
        
        if any("Inventory Sync" in r["test_name"] for r in failed_tests):
            recommendations.append("Ensure both Business Central and Zoho connections are working")
            recommendations.append("Check API permissions and user roles")
            recommendations.append("Review the troubleshooting guide for 403 errors")
        
        return recommendations

async def main():
    """Main test execution function"""
    print("🔍 Starting Inventory Sync Audit and Testing")
    print("=" * 60)
    
    auditor = InventorySyncAuditor()
    
    # Run all tests
    await auditor.test_server_startup()
    await auditor.audit_configuration()
    await auditor.test_inventory_endpoints()
    await auditor.test_business_central_integration()
    await auditor.test_zoho_integration()
    await auditor.test_full_inventory_sync()
    await auditor.check_server_logs()
    
    # Generate report
    report = auditor.generate_audit_report()
    
    print("\n📊 Audit Report Generated:")
    print(f"  - JSON Report: inventory_sync_audit_report.json")
    print(f"  - Log File: inventory_sync_test.log")
    print(f"  - Success Rate: {report['audit_summary']['success_rate']:.1f}%")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())