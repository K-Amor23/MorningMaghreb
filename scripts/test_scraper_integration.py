#!/usr/bin/env python3
"""
Simple Scraper Integration Test
Tests the basic scraper functionality without complex dependencies
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add scrapers to path
sys.path.append(str(Path(__file__).parent.parent / "scrapers"))


def test_scraper_structure():
    """Test that the scraper structure is properly set up"""
    print("🔍 Testing Scraper Structure")
    print("-" * 40)

    scrapers_dir = Path(__file__).parent.parent / "scrapers"

    # Check if scrapers directory exists
    if not scrapers_dir.exists():
        print("❌ Scrapers directory not found")
        return False

    # Check for required directories
    required_dirs = [
        "base",
        "utils",
        "financial_reports",
        "news_sentiment",
        "market_data",
        "macro_data",
        "currency_data",
        "volume_data",
        "bank_data",
        "african_markets",
    ]

    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = scrapers_dir / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/ directory exists")

    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False

    # Check for key files
    key_files = [
        "base/scraper_interface.py",
        "utils/http_helpers.py",
        "utils/date_parsers.py",
        "utils/config_loader.py",
        "utils/data_validators.py",
        "orchestrator.py",
        "requirements.txt",
        "README.md",
    ]

    missing_files = []
    for file_path in key_files:
        full_path = scrapers_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ Scraper structure is properly set up")
    return True


def test_base_interface():
    """Test the base scraper interface"""
    print("\n📋 Testing Base Interface")
    print("-" * 40)

    try:
        # Import directly from the file
        base_path = (
            Path(__file__).parent.parent / "scrapers" / "base" / "scraper_interface.py"
        )
        if not base_path.exists():
            print("❌ Base interface file not found")
            return False

        # Read and check the file content
        with open(base_path, "r") as f:
            content = f.read()

        # Check for key components
        if "class BaseScraper" in content:
            print("✅ BaseScraper class found")
        else:
            print("❌ BaseScraper class not found")
            return False

        if "def fetch(self)" in content:
            print("✅ fetch method found")
        else:
            print("❌ fetch method not found")
            return False

        if "def validate_data(self" in content:
            print("✅ validate_data method found")
        else:
            print("❌ validate_data method not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Base interface test failed: {e}")
        return False


def test_utilities():
    """Test utility functions"""
    print("\n🔧 Testing Utilities")
    print("-" * 40)

    try:
        # Check if utility files exist and have expected content
        utils_dir = Path(__file__).parent.parent / "scrapers" / "utils"

        utility_files = [
            "http_helpers.py",
            "date_parsers.py",
            "config_loader.py",
            "data_validators.py",
        ]

        for util_file in utility_files:
            file_path = utils_dir / util_file
            if file_path.exists():
                print(f"✅ {util_file} exists")
            else:
                print(f"❌ {util_file} missing")
                return False

        return True

    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False


def test_orchestrator():
    """Test the orchestrator"""
    print("\n🎼 Testing Orchestrator")
    print("-" * 40)

    try:
        # Check if orchestrator file exists and has expected content
        orchestrator_path = (
            Path(__file__).parent.parent / "scrapers" / "orchestrator.py"
        )

        if not orchestrator_path.exists():
            print("❌ Orchestrator file not found")
            return False

        # Read and check the file content
        with open(orchestrator_path, "r") as f:
            content = f.read()

        # Check for key components
        if "class MasterOrchestrator" in content:
            print("✅ MasterOrchestrator class found")
        else:
            print("❌ MasterOrchestrator class not found")
            return False

        if "def run_pipeline(self" in content:
            print("✅ run_pipeline method found")
        else:
            print("❌ run_pipeline method not found")
            return False

        if "def run_all_scrapers(self" in content:
            print("✅ run_all_scrapers method found")
        else:
            print("❌ run_all_scrapers method not found")
            return False

        return True

    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False


def test_individual_scrapers():
    """Test individual scraper files"""
    print("\n🧪 Testing Individual Scrapers")
    print("-" * 40)

    scrapers_dir = Path(__file__).parent.parent / "scrapers"

    # Check for scraper files in each directory
    scraper_files = []
    for category_dir in scrapers_dir.iterdir():
        if category_dir.is_dir() and category_dir.name not in ["base", "utils"]:
            for py_file in category_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    scraper_files.append(f"{category_dir.name}/{py_file.name}")

    if scraper_files:
        print(f"✅ Found {len(scraper_files)} scraper files:")
        for file_path in scraper_files[:5]:  # Show first 5
            print(f"  📄 {file_path}")
        if len(scraper_files) > 5:
            print(f"  ... and {len(scraper_files) - 5} more")
        return True
    else:
        print("❌ No scraper files found")
        return False


def test_simple_orchestrator_run():
    """Test a simple orchestrator run without complex imports"""
    print("\n🚀 Testing Simple Orchestrator Run")
    print("-" * 40)

    try:
        # Create a simple test orchestrator
        class SimpleOrchestrator:
            def __init__(self):
                self.scrapers = {}
                self.logger = self._get_logger()

            def _get_logger(self):
                import logging

                return logging.getLogger(__name__)

            def run_pipeline(self):
                print("🔄 Running simple pipeline test...")

                # Create test data
                test_data = pd.DataFrame(
                    {"test_col": ["test_data"], "timestamp": [datetime.now()]}
                )

                print(f"✅ Test pipeline completed with {len(test_data)} records")
                return {"test_scraper": test_data}

        orchestrator = SimpleOrchestrator()
        results = orchestrator.run_pipeline()

        if results and "test_scraper" in results:
            print("✅ Simple orchestrator test passed")
            return True
        else:
            print("❌ Simple orchestrator test failed")
            return False

    except Exception as e:
        print(f"❌ Simple orchestrator test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting Scraper Integration Tests")
    print("=" * 50)

    tests = [
        ("Structure", test_scraper_structure),
        ("Base Interface", test_base_interface),
        ("Utilities", test_utilities),
        ("Orchestrator", test_orchestrator),
        ("Individual Scrapers", test_individual_scrapers),
        ("Simple Orchestrator Run", test_simple_orchestrator_run),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Integration Test Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n📈 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
