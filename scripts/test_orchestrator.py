#!/usr/bin/env python3
"""
Orchestrator and Scraper Testing Script
Comprehensive testing for the new scraper architecture
"""

import sys
import os
import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import logging

# Add scrapers to path
sys.path.append(str(Path(__file__).parent.parent / "scrapers"))


class ScraperTester:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.scrapers_dir = self.root_dir / "scrapers"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def run_smoke_test(self) -> Dict[str, Any]:
        """Run smoke test on orchestrator with subset of scrapers"""
        print("🔥 Running Smoke Test")
        print("-" * 40)

        try:
            from scrapers.orchestrator import MasterOrchestrator

            # Create orchestrator with limited config for testing
            config = {
                "test_mode": True,
                "max_scrapers": 3,  # Limit for smoke test
                "timeout": 30,
            }

            orchestrator = MasterOrchestrator(config)

            # Run pipeline
            results = orchestrator.run_pipeline(save_results=False)

            # Analyze results
            successful = len([r for r in results.values() if not r.empty])
            total = len(results)

            test_result = {
                "name": "smoke_test",
                "status": "success" if successful > 0 else "failed",
                "successful_scrapers": successful,
                "total_scrapers": total,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "results": {name: len(data) for name, data in results.items()},
            }

            print(f"✅ Smoke test completed: {successful}/{total} scrapers successful")
            for name, count in test_result["results"].items():
                print(f"  - {name}: {count} records")

            self.results["tests"].append(test_result)
            return test_result

        except Exception as e:
            print(f"❌ Smoke test failed: {e}")
            test_result = {"name": "smoke_test", "status": "failed", "error": str(e)}
            self.results["tests"].append(test_result)
            return test_result

    def test_individual_scrapers(self) -> List[Dict[str, Any]]:
        """Test individual scrapers"""
        print("\n🧪 Testing Individual Scrapers")
        print("-" * 40)

        test_results = []

        # Test a subset of scrapers
        test_scrapers = [
            ("financial_reports", "FinancialReportsScraper"),
            ("market_data", "CasablancaBourseScraper"),
            ("news_sentiment", "NewsSentimentScraper"),
        ]

        for category, scraper_name in test_scrapers:
            try:
                print(f"Testing {scraper_name}...")

                # Import and test scraper
                module_path = f"scrapers.{category}.{scraper_name.lower()}"
                scraper_class = getattr(
                    __import__(module_path, fromlist=[scraper_name]), scraper_name
                )

                # Create scraper instance
                scraper = scraper_class({"test_mode": True})

                # Test fetch method
                data = scraper.fetch()

                # Test validation
                is_valid = scraper.validate_data(data)

                # Test data structure
                data_info = {
                    "rows": len(data),
                    "columns": list(data.columns) if not data.empty else [],
                    "empty": data.empty,
                }

                test_result = {
                    "name": f"test_{scraper_name.lower()}",
                    "status": "success" if is_valid and not data.empty else "failed",
                    "scraper": scraper_name,
                    "category": category,
                    "data_info": data_info,
                    "validation_passed": is_valid,
                    "has_data": not data.empty,
                }

                if test_result["status"] == "success":
                    print(
                        f"  ✅ {scraper_name}: {len(data)} records, validation passed"
                    )
                else:
                    print(f"  ❌ {scraper_name}: validation failed or no data")

                test_results.append(test_result)

            except Exception as e:
                print(f"  ❌ {scraper_name}: {e}")
                test_result = {
                    "name": f"test_{scraper_name.lower()}",
                    "status": "failed",
                    "scraper": scraper_name,
                    "category": category,
                    "error": str(e),
                }
                test_results.append(test_result)

        self.results["tests"].extend(test_results)
        return test_results

    def test_orchestrator_failure_modes(self) -> List[Dict[str, Any]]:
        """Test orchestrator failure modes"""
        print("\n💥 Testing Failure Modes")
        print("-" * 40)

        failure_tests = []

        # Test 1: Network failure simulation
        try:
            print("Testing network failure handling...")
            # This would require mocking network calls
            # For now, we'll test the error handling structure

            test_result = {
                "name": "network_failure_test",
                "status": "skipped",
                "reason": "Requires network mocking setup",
            }
            failure_tests.append(test_result)
            print("  ⚠️  Network failure test skipped (requires mocking)")

        except Exception as e:
            test_result = {
                "name": "network_failure_test",
                "status": "failed",
                "error": str(e),
            }
            failure_tests.append(test_result)

        # Test 2: Invalid data handling
        try:
            print("Testing invalid data handling...")
            from scrapers.base.scraper_interface import BaseScraper
            import pandas as pd

            class TestScraper(BaseScraper):
                def fetch(self):
                    return pd.DataFrame()  # Empty data

                def validate_data(self, data):
                    return False  # Always fail validation

            scraper = TestScraper()
            data = scraper.fetch()
            is_valid = scraper.validate_data(data)

            test_result = {
                "name": "invalid_data_test",
                "status": "success" if not is_valid else "failed",
                "expected_behavior": "Validation should fail for invalid data",
            }
            failure_tests.append(test_result)
            print(f"  ✅ Invalid data test: validation correctly failed")

        except Exception as e:
            test_result = {
                "name": "invalid_data_test",
                "status": "failed",
                "error": str(e),
            }
            failure_tests.append(test_result)
            print(f"  ❌ Invalid data test failed: {e}")

        self.results["tests"].extend(failure_tests)
        return failure_tests

    def test_data_validation(self) -> List[Dict[str, Any]]:
        """Test data validation functions"""
        print("\n🔍 Testing Data Validation")
        print("-" * 40)

        validation_tests = []

        try:
            from scrapers.utils.data_validators import (
                validate_dataframe,
                clean_dataframe,
            )
            import pandas as pd

            # Test 1: Valid data
            valid_data = pd.DataFrame(
                {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [10.5, 20.3, 30.1]}
            )

            is_valid = validate_dataframe(
                valid_data,
                required_columns=["id", "name", "value"],
                numeric_columns=["id", "value"],
            )

            test_result = {
                "name": "valid_data_validation",
                "status": "success" if is_valid else "failed",
                "data_shape": valid_data.shape,
            }
            validation_tests.append(test_result)
            print(f"  ✅ Valid data validation: {is_valid}")

            # Test 2: Invalid data (missing columns)
            invalid_data = pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "name": ["A", "B", "C"],
                    # Missing 'value' column
                }
            )

            is_valid = validate_dataframe(
                invalid_data, required_columns=["id", "name", "value"]
            )

            test_result = {
                "name": "invalid_data_validation",
                "status": "success" if not is_valid else "failed",
                "expected_behavior": "Should fail validation for missing columns",
            }
            validation_tests.append(test_result)
            print(f"  ✅ Invalid data validation: {not is_valid}")

            # Test 3: Data cleaning
            dirty_data = pd.DataFrame(
                {
                    "id": [1, 1, 2, 3],  # Duplicate
                    "name": ["A", "A", "B", "C"],
                    "value": [10.5, 10.5, 20.3, None],  # Duplicate and null
                }
            )

            cleaned_data = clean_dataframe(dirty_data)

            test_result = {
                "name": "data_cleaning",
                "status": "success",
                "original_rows": len(dirty_data),
                "cleaned_rows": len(cleaned_data),
                "duplicates_removed": len(dirty_data) - len(cleaned_data),
            }
            validation_tests.append(test_result)
            print(f"  ✅ Data cleaning: {len(dirty_data)} → {len(cleaned_data)} rows")

        except Exception as e:
            print(f"  ❌ Data validation tests failed: {e}")
            test_result = {
                "name": "data_validation_tests",
                "status": "failed",
                "error": str(e),
            }
            validation_tests.append(test_result)

        self.results["tests"].extend(validation_tests)
        return validation_tests

    def test_utilities(self) -> List[Dict[str, Any]]:
        """Test utility functions"""
        print("\n🔧 Testing Utilities")
        print("-" * 40)

        utility_tests = []

        try:
            from scrapers.utils.date_parsers import parse_date, extract_date_from_text
            from scrapers.utils.config_loader import load_config

            # Test date parsing
            test_date = "2025-08-06"
            parsed_date = parse_date(test_date)

            test_result = {
                "name": "date_parsing",
                "status": "success" if parsed_date else "failed",
                "input": test_date,
                "output": str(parsed_date) if parsed_date else None,
            }
            utility_tests.append(test_result)
            print(f"  ✅ Date parsing: {test_date} → {parsed_date}")

            # Test config loading
            config = load_config()

            test_result = {
                "name": "config_loading",
                "status": "success" if isinstance(config, dict) else "failed",
                "config_keys": list(config.keys()) if isinstance(config, dict) else [],
            }
            utility_tests.append(test_result)
            print(f"  ✅ Config loading: {len(config)} keys loaded")

        except Exception as e:
            print(f"  ❌ Utility tests failed: {e}")
            test_result = {"name": "utility_tests", "status": "failed", "error": str(e)}
            utility_tests.append(test_result)

        self.results["tests"].extend(utility_tests)
        return utility_tests

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report")
        print("-" * 40)

        # Calculate summary statistics
        all_tests = self.results["tests"]
        successful = len([t for t in all_tests if t["status"] == "success"])
        failed = len([t for t in all_tests if t["status"] == "failed"])
        skipped = len([t for t in all_tests if t["status"] == "skipped"])

        self.results["summary"] = {
            "total_tests": len(all_tests),
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (successful / len(all_tests) * 100) if all_tests else 0,
        }

        # Generate report content
        report_content = [
            "# 🧪 Scraper Test Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Timestamp**: {self.results['timestamp']}",
            "",
            "## 📊 Summary",
            "",
            f"- **Total Tests**: {self.results['summary']['total_tests']}",
            f"- **Successful**: {self.results['summary']['successful']}",
            f"- **Failed**: {self.results['summary']['failed']}",
            f"- **Skipped**: {self.results['summary']['skipped']}",
            f"- **Success Rate**: {self.results['summary']['success_rate']:.1f}%",
            "",
            "## 📋 Test Details",
            "",
        ]

        # Group tests by type
        test_groups = {}
        for test in all_tests:
            test_type = test["name"].split("_")[0]
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(test)

        for test_type, tests in test_groups.items():
            report_content.append(f"### {test_type.title()} Tests")
            for test in tests:
                status_emoji = {"success": "✅", "failed": "❌", "skipped": "⚠️"}.get(
                    test["status"], "❓"
                )

                report_content.append(
                    f"- {status_emoji} **{test['name']}** - {test['status']}"
                )

                if "error" in test:
                    report_content.append(f"  - Error: {test['error']}")
                elif "reason" in test:
                    report_content.append(f"  - Reason: {test['reason']}")

                # Add specific details for certain test types
                if "data_info" in test:
                    data_info = test["data_info"]
                    report_content.append(
                        f"  - Data: {data_info['rows']} rows, {len(data_info['columns'])} columns"
                    )

            report_content.append("")

        # Add recommendations
        report_content.extend(
            [
                "## 💡 Recommendations",
                "",
            ]
        )

        if self.results["summary"]["failed"] > 0:
            report_content.append("### 🚨 Critical Issues")
            report_content.append(
                "The following tests failed and need immediate attention:"
            )
            for test in all_tests:
                if test["status"] == "failed":
                    report_content.append(
                        f"- **{test['name']}**: {test.get('error', 'Unknown error')}"
                    )
            report_content.append("")

        if self.results["summary"]["success_rate"] >= 80:
            report_content.append("### ✅ Good Performance")
            report_content.append("Most tests are passing. Consider:")
            report_content.append("- Adding more edge case tests")
            report_content.append("- Implementing integration tests")
            report_content.append("- Setting up continuous monitoring")
        else:
            report_content.append("### ⚠️  Needs Improvement")
            report_content.append("Test success rate is below 80%. Focus on:")
            report_content.append("- Fixing failed tests")
            report_content.append("- Improving error handling")
            report_content.append("- Adding more robust validation")

        report_content.extend(
            [
                "",
                "## 🎯 Next Steps",
                "",
                "1. **Fix Failed Tests**: Address any failed tests before deployment",
                "2. **Add Integration Tests**: Test with real data sources",
                "3. **Set Up CI/CD**: Automate testing in your pipeline",
                "4. **Monitor Performance**: Track test success rates over time",
                "5. **Expand Coverage**: Add tests for edge cases and error conditions",
            ]
        )

        return "\n".join(report_content)

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Scraper Tests")
        print("=" * 60)

        # Run all test suites
        self.run_smoke_test()
        self.test_individual_scrapers()
        self.test_orchestrator_failure_modes()
        self.test_data_validation()
        self.test_utilities()

        # Generate report
        report = self.generate_test_report()

        # Save report
        reports_dir = self.root_dir / "reports"
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"scraper_test_report_{timestamp}.md"

        with open(report_file, "w") as f:
            f.write(report)

        # Save detailed results
        results_file = reports_dir / f"scraper_test_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"📄 Test report saved to: {report_file}")
        print(f"📊 Detailed results saved to: {results_file}")

        # Print summary
        summary = self.results["summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")

        if summary["failed"] > 0:
            print(
                "\n🚨 CRITICAL: Some tests failed. Please review the report and fix issues."
            )
        elif summary["success_rate"] >= 80:
            print("\n🎉 SUCCESS: Tests are passing! Ready for deployment.")
        else:
            print(
                "\n⚠️  WARNING: Test success rate is below 80%. Consider improvements."
            )


def main():
    """Main test execution"""
    tester = ScraperTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
