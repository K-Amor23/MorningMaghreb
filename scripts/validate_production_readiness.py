#!/usr/bin/env python3
"""
Production Readiness Validation Script
Validates all systems before locking production stability
"""

import os
import sys
import json
import time
import subprocess
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionReadinessValidator:
    """Validates production readiness before stability lock"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results_dir = self.project_root / "validation_results"
        self.results_dir.mkdir(exist_ok=True)

        # Configuration
        self.api_base_url = "http://localhost:8000"
        self.web_base_url = "http://localhost:3000"
        self.companies = ["IAM", "ATW", "BCP"]

        # Validation criteria
        self.criteria = {
            "api_performance": {"p95_target": 200, "success_rate_target": 0.95},
            "data_quality": {
                "min_companies_with_data": 70,
                "min_excellent_quality": 20,
            },
            "e2e_tests": {
                "required_tests": ["company", "auth", "data_quality", "charts"]
            },
            "system_health": {
                "required_services": ["api", "web", "database", "websocket"]
            },
        }

    def validate_production_readiness(self) -> bool:
        """Main validation method"""
        logger.info("🔍 Starting Production Readiness Validation")
        logger.info("=" * 60)

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0.0",
            "checks": {},
            "overall_status": "PENDING",
        }

        try:
            # 1. System Health Validation
            validation_results["checks"][
                "system_health"
            ] = self._validate_system_health()

            # 2. API Performance Validation
            validation_results["checks"][
                "api_performance"
            ] = self._validate_api_performance()

            # 3. Data Quality Validation
            validation_results["checks"]["data_quality"] = self._validate_data_quality()

            # 4. E2E Test Validation
            validation_results["checks"]["e2e_tests"] = self._validate_e2e_tests()

            # 5. Security Validation
            validation_results["checks"]["security"] = self._validate_security()

            # 6. Documentation Validation
            validation_results["checks"][
                "documentation"
            ] = self._validate_documentation()

            # Determine overall status
            all_passed = all(
                check.get("status") == "PASS"
                for check in validation_results["checks"].values()
            )

            validation_results["overall_status"] = "PASS" if all_passed else "FAIL"

            # Save results
            self._save_validation_results(validation_results)

            # Generate report
            self._generate_validation_report(validation_results)

            logger.info("=" * 60)
            if all_passed:
                logger.info("✅ Production readiness validation PASSED!")
                logger.info("🎯 System is ready for v1.0.0 tagging")
            else:
                logger.error("❌ Production readiness validation FAILED!")
                logger.error("🔧 Please address issues before proceeding")

            return all_passed

        except Exception as e:
            logger.error(f"❌ Validation failed with error: {e}")
            return False

    def _validate_system_health(self) -> Dict[str, Any]:
        """Validate overall system health"""
        logger.info("🏥 Validating system health...")

        health_checks = {
            "api_server": self._check_api_server(),
            "web_server": self._check_web_server(),
            "database": self._check_database(),
            "websocket": self._check_websocket(),
            "file_system": self._check_file_system(),
        }

        all_healthy = all(check["status"] == "PASS" for check in health_checks.values())

        return {
            "status": "PASS" if all_healthy else "FAIL",
            "checks": health_checks,
            "summary": f"{sum(1 for c in health_checks.values() if c['status'] == 'PASS')}/{len(health_checks)} services healthy",
        }

    def _check_api_server(self) -> Dict[str, Any]:
        """Check API server health"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "PASS",
                    "details": data,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"API returned status {response.status_code}",
                }
        except Exception as e:
            return {"status": "FAIL", "error": f"API server unreachable: {e}"}

    def _check_web_server(self) -> Dict[str, Any]:
        """Check web server health"""
        try:
            response = requests.get(f"{self.web_base_url}", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "PASS",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"Web server returned status {response.status_code}",
                }
        except Exception as e:
            return {"status": "FAIL", "error": f"Web server unreachable: {e}"}

    def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/health/database", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {"status": "PASS", "details": data}
            else:
                return {
                    "status": "FAIL",
                    "error": f"Database health check failed: {response.status_code}",
                }
        except Exception as e:
            return {"status": "FAIL", "error": f"Database health check error: {e}"}

    def _check_websocket(self) -> Dict[str, Any]:
        """Check WebSocket connectivity"""
        try:
            import websocket

            start_time = time.time()
            ws = websocket.create_connection(f"ws://localhost:8000/ws", timeout=5)
            connection_time = (time.time() - start_time) * 1000

            # Test ping/pong
            ws.send(json.dumps({"type": "ping"}))
            response = ws.recv()
            ws.close()

            return {
                "status": "PASS",
                "connection_time_ms": connection_time,
                "ping_response": response,
            }

        except ImportError:
            return {"status": "WARN", "error": "websocket-client not installed"}
        except Exception as e:
            return {"status": "FAIL", "error": f"WebSocket test failed: {e}"}

    def _check_file_system(self) -> Dict[str, Any]:
        """Check file system health"""
        try:
            # Check critical directories
            critical_dirs = ["apps/web", "apps/backend", "scripts", "docs", "tests"]

            missing_dirs = []
            for dir_path in critical_dirs:
                if not (self.project_root / dir_path).exists():
                    missing_dirs.append(dir_path)

            if missing_dirs:
                return {
                    "status": "FAIL",
                    "error": f"Missing critical directories: {missing_dirs}",
                }
            else:
                return {"status": "PASS", "details": "All critical directories present"}

        except Exception as e:
            return {"status": "FAIL", "error": f"File system check failed: {e}"}

    def _validate_api_performance(self) -> Dict[str, Any]:
        """Validate API performance meets targets"""
        logger.info("⏱️ Validating API performance...")

        endpoints = [
            "/api/companies/IAM/summary",
            "/api/companies/ATW/summary",
            "/api/companies/BCP/summary",
            "/api/companies/IAM/trading",
            "/api/companies/ATW/trading",
            "/api/companies/BCP/trading",
            "/api/markets/quotes",
        ]

        performance_data = {}
        all_passed = True

        for endpoint in endpoints:
            times = []
            success_count = 0

            for _ in range(20):  # 20 requests per endpoint
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.api_base_url}{endpoint}", timeout=10
                    )
                    end_time = time.time()

                    if response.status_code == 200:
                        times.append((end_time - start_time) * 1000)
                        success_count += 1

                    time.sleep(0.1)

                except Exception:
                    pass

            if times:
                p95 = sorted(times)[int(len(times) * 0.95)]
                success_rate = success_count / 20

                performance_data[endpoint] = {
                    "avg_ms": sum(times) / len(times),
                    "p95_ms": p95,
                    "success_rate": success_rate,
                    "status": (
                        "PASS"
                        if p95 <= self.criteria["api_performance"]["p95_target"]
                        and success_rate
                        >= self.criteria["api_performance"]["success_rate_target"]
                        else "FAIL"
                    ),
                }

                if performance_data[endpoint]["status"] == "FAIL":
                    all_passed = False
            else:
                performance_data[endpoint] = {
                    "status": "FAIL",
                    "error": "No successful requests",
                }
                all_passed = False

        return {
            "status": "PASS" if all_passed else "FAIL",
            "endpoints": performance_data,
            "targets": self.criteria["api_performance"],
        }

    def _validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality across companies"""
        logger.info("📊 Validating data quality...")

        quality_stats = {
            "total_companies": len(self.companies),
            "companies_with_data": 0,
            "quality_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0},
            "company_details": {},
        }

        for company in self.companies:
            try:
                response = requests.get(
                    f"{self.api_base_url}/api/companies/{company}/summary", timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    quality_stats["companies_with_data"] += 1

                    quality = self._assess_data_quality(data)
                    quality_stats["quality_distribution"][quality] += 1

                    quality_stats["company_details"][company] = {
                        "has_data": True,
                        "quality": quality,
                        "metrics_count": len(data.get("metrics", {})),
                    }
                else:
                    quality_stats["company_details"][company] = {
                        "has_data": False,
                        "quality": "no_data",
                    }

            except Exception as e:
                quality_stats["company_details"][company] = {
                    "has_data": False,
                    "quality": "error",
                    "error": str(e),
                }

        # Check if quality meets criteria
        excellent_count = quality_stats["quality_distribution"]["excellent"]
        companies_with_data = quality_stats["companies_with_data"]

        quality_passed = (
            companies_with_data
            >= self.criteria["data_quality"]["min_companies_with_data"]
            and excellent_count
            >= self.criteria["data_quality"]["min_excellent_quality"]
        )

        return {
            "status": "PASS" if quality_passed else "FAIL",
            "stats": quality_stats,
            "targets": self.criteria["data_quality"],
        }

    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """Assess data quality based on completeness"""
        metrics = data.get("metrics", {})

        if not metrics:
            return "poor"

        non_empty_metrics = sum(1 for v in metrics.values() if v and v != "N/A")
        completeness_ratio = non_empty_metrics / len(metrics)

        if completeness_ratio >= 0.9:
            return "excellent"
        elif completeness_ratio >= 0.7:
            return "good"
        elif completeness_ratio >= 0.5:
            return "fair"
        else:
            return "poor"

    def _validate_e2e_tests(self) -> Dict[str, Any]:
        """Validate E2E test setup and execution"""
        logger.info("🧪 Validating E2E tests...")

        e2e_dir = self.project_root / "apps" / "web" / "tests" / "e2e"

        if not e2e_dir.exists():
            return {"status": "FAIL", "error": "E2E test directory not found"}

        # Check for required test files
        required_tests = [
            "iam.spec.ts",
            "atw.spec.ts",
            "bcp.spec.ts",
            "auth.spec.ts",
            "data-quality.spec.ts",
            "charts.spec.ts",
        ]
        missing_tests = []

        for test_file in required_tests:
            if not (e2e_dir / test_file).exists():
                missing_tests.append(test_file)

        if missing_tests:
            return {
                "status": "FAIL",
                "error": f"Missing required test files: {missing_tests}",
            }

        # Check Playwright configuration
        playwright_config = self.project_root / "apps" / "web" / "playwright.config.ts"
        if not playwright_config.exists():
            return {"status": "FAIL", "error": "Playwright configuration not found"}

        return {
            "status": "PASS",
            "details": {
                "test_files_found": len(required_tests) - len(missing_tests),
                "total_required": len(required_tests),
                "playwright_config": "Found",
            },
        }

    def _validate_security(self) -> Dict[str, Any]:
        """Validate security measures"""
        logger.info("🔒 Validating security measures...")

        security_checks = {
            "https_endpoints": self._check_https_endpoints(),
            "authentication": self._check_authentication(),
            "rate_limiting": self._check_rate_limiting(),
            "cors_policy": self._check_cors_policy(),
        }

        all_secure = all(
            check["status"] in ["PASS", "WARN"] for check in security_checks.values()
        )

        return {"status": "PASS" if all_secure else "FAIL", "checks": security_checks}

    def _check_https_endpoints(self) -> Dict[str, Any]:
        """Check HTTPS endpoints (for production)"""
        # In development, this would be a warning
        return {
            "status": "WARN",
            "message": "HTTPS not configured (expected in development)",
        }

    def _check_authentication(self) -> Dict[str, Any]:
        """Check authentication endpoints"""
        try:
            response = requests.get(f"{self.api_base_url}/api/auth/status", timeout=5)
            if response.status_code in [200, 401]:  # Both valid responses
                return {
                    "status": "PASS",
                    "details": "Authentication endpoints responding",
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"Auth endpoint returned {response.status_code}",
                }
        except Exception as e:
            return {"status": "FAIL", "error": f"Auth endpoint unreachable: {e}"}

    def _check_rate_limiting(self) -> Dict[str, Any]:
        """Check rate limiting (basic test)"""
        try:
            # Make multiple rapid requests
            responses = []
            for _ in range(10):
                response = requests.get(f"{self.api_base_url}/api/health", timeout=2)
                responses.append(response.status_code)
                time.sleep(0.1)

            # Check if any were rate limited (429)
            if 429 in responses:
                return {"status": "PASS", "details": "Rate limiting active"}
            else:
                return {
                    "status": "WARN",
                    "message": "Rate limiting not detected (may be disabled in dev)",
                }
        except Exception as e:
            return {"status": "FAIL", "error": f"Rate limiting check failed: {e}"}

    def _check_cors_policy(self) -> Dict[str, Any]:
        """Check CORS policy"""
        try:
            response = requests.options(f"{self.api_base_url}/api/health", timeout=5)
            if "Access-Control-Allow-Origin" in response.headers:
                return {"status": "PASS", "details": "CORS headers present"}
            else:
                return {"status": "WARN", "message": "CORS headers not detected"}
        except Exception as e:
            return {"status": "FAIL", "error": f"CORS check failed: {e}"}

    def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness"""
        logger.info("📚 Validating documentation...")

        required_docs = [
            "docs/PRODUCTION_DEPLOYMENT_GUIDE.md",
            "docs/E2E_TESTING_GUIDE.md",
            "docs/UPCOMING_PHASES_ROADMAP.md",
            "README.md",
        ]

        missing_docs = []
        for doc_path in required_docs:
            if not (self.project_root / doc_path).exists():
                missing_docs.append(doc_path)

        if missing_docs:
            return {
                "status": "FAIL",
                "error": f"Missing required documentation: {missing_docs}",
            }

        return {
            "status": "PASS",
            "details": f"All {len(required_docs)} required documents present",
        }

    def _save_validation_results(self, results: Dict[str, Any]) -> None:
        """Save validation results to file"""
        results_file = (
            self.results_dir
            / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"📄 Validation results saved to: {results_file}")

    def _generate_validation_report(self, results: Dict[str, Any]) -> None:
        """Generate human-readable validation report"""
        report_file = (
            self.results_dir
            / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_file, "w") as f:
            f.write(self._format_validation_report(results))

        logger.info(f"📋 Validation report generated: {report_file}")

    def _format_validation_report(self, results: Dict[str, Any]) -> str:
        """Format validation results as markdown report"""
        return f"""# Production Readiness Validation Report

Generated on: {results['timestamp']}
Version: {results['version']}
Overall Status: **{results['overall_status']}**

## 📊 Validation Summary

| Category | Status | Details |
|----------|--------|---------|
{self._format_validation_summary(results['checks'])}

## 🔍 Detailed Results

{self._format_detailed_results(results['checks'])}

## 🎯 Recommendations

{self._get_recommendations(results)}

---

*Report generated automatically by Production Readiness Validator*
"""

    def _format_validation_summary(self, checks: Dict[str, Any]) -> str:
        """Format validation summary as markdown table"""
        rows = []
        for category, check in checks.items():
            status_emoji = (
                "✅"
                if check["status"] == "PASS"
                else "❌" if check["status"] == "FAIL" else "⚠️"
            )
            summary = check.get("summary", check.get("details", "N/A"))
            rows.append(
                f"| {category.replace('_', ' ').title()} | {status_emoji} {check['status']} | {summary} |"
            )

        return "\n".join(rows)

    def _format_detailed_results(self, checks: Dict[str, Any]) -> str:
        """Format detailed validation results"""
        content = []

        for category, check in checks.items():
            content.append(f"### {category.replace('_', ' ').title()}")
            content.append(f"**Status**: {check['status']}")

            if "checks" in check:
                for sub_check, sub_result in check["checks"].items():
                    content.append(
                        f"- **{sub_check.replace('_', ' ').title()}**: {sub_result['status']}"
                    )
                    if "error" in sub_result:
                        content.append(f"  - Error: {sub_result['error']}")
                    if "details" in sub_result:
                        content.append(f"  - Details: {sub_result['details']}")

            if "endpoints" in check:
                content.append("**API Endpoints Performance:**")
                for endpoint, perf in check["endpoints"].items():
                    if perf["status"] == "PASS":
                        content.append(f"- ✅ {endpoint}: {perf['p95_ms']:.1f}ms (P95)")
                    else:
                        content.append(
                            f"- ❌ {endpoint}: {perf.get('error', 'Failed')}"
                        )

            if "stats" in check:
                stats = check["stats"]
                content.append(f"**Data Quality Stats:**")
                content.append(
                    f"- Companies with data: {stats['companies_with_data']}/{stats['total_companies']}"
                )
                content.append(
                    f"- Quality distribution: {stats['quality_distribution']}"
                )

            content.append("")

        return "\n".join(content)

    def _get_recommendations(self, results: Dict[str, Any]) -> str:
        """Get recommendations based on validation results"""
        recommendations = []

        if results["overall_status"] == "PASS":
            recommendations.append(
                "✅ **All validation checks passed!** The system is ready for production."
            )
            recommendations.append(
                "🎯 Proceed with v1.0.0 tagging and baseline metrics capture."
            )
        else:
            recommendations.append(
                "❌ **Some validation checks failed.** Please address the following issues:"
            )

            for category, check in results["checks"].items():
                if check["status"] == "FAIL":
                    recommendations.append(
                        f"- **{category.replace('_', ' ').title()}**: {check.get('error', 'Check failed')}"
                    )

            recommendations.append(
                "🔧 Fix the issues above before proceeding with production deployment."
            )

        return "\n".join(recommendations)


def main():
    """Main function"""
    validator = ProductionReadinessValidator()

    success = validator.validate_production_readiness()

    if success:
        logger.info("🎉 Production readiness validation completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Production readiness validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
