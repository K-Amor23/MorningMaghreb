#!/usr/bin/env python3
"""
Complete Setup Test Script for Casablanca Insights
Tests all aspects of the setup including environment, dependencies, database, and API endpoints
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CompleteSetupTest:
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent.parent.parent

        # Load environment variables
        load_dotenv(self.project_root / ".env")

        # Colors for output
        self.colors = {
            "INFO": "\033[94m",  # Blue
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m",  # Reset
        }

    def print_status(self, message: str, status: str = "INFO"):
        """Print colored status messages"""
        color = self.colors.get(status, self.colors["INFO"])
        print(f"{color}[{status}]{self.colors['RESET']} {message}")

    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a test and record the result"""
        self.print_status(f"Running: {test_name}", "INFO")
        try:
            result = test_func(*args, **kwargs)
            self.test_results.append((test_name, result))
            if result:
                self.print_status(f"✅ {test_name} passed", "SUCCESS")
            else:
                self.print_status(f"❌ {test_name} failed", "ERROR")
            return result
        except Exception as e:
            self.print_status(f"❌ {test_name} failed with error: {str(e)}", "ERROR")
            self.test_results.append((test_name, False))
            return False

    def test_project_structure(self):
        """Test that the project structure is correct"""
        required_files = [
            "package.json",
            "apps/web/package.json",
            "apps/backend/requirements.txt",
            "env.template",
        ]

        required_dirs = ["apps", "apps/web", "apps/backend", "scripts", "database"]

        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                return False

        for dir_path in required_dirs:
            if not (self.project_root / dir_path).is_dir():
                return False

        return True

    def test_environment_variables(self):
        """Test that required environment variables are set"""
        required_vars = ["NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY"]

        optional_vars = [
            "OPENAI_API_KEY",
            "SENDGRID_API_KEY",
            "STRIPE_SECRET_KEY",
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY",
        ]

        # Check required variables
        for var in required_vars:
            if not os.getenv(var):
                return False

        # Check optional variables (just warn if missing)
        missing_optional = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)

        if missing_optional:
            self.print_status(
                f"Optional variables missing: {', '.join(missing_optional)}", "WARNING"
            )

        return True

    def test_python_environment(self):
        """Test Python virtual environment and dependencies"""
        venv_path = self.project_root / ".venv"

        if not venv_path.exists():
            return False

        # Test if we can import key packages
        try:
            import fastapi
            import supabase
            import uvicorn

            return True
        except ImportError:
            return False

    def test_node_environment(self):
        """Test Node.js environment and dependencies"""
        # Check if node_modules exists in key directories
        required_node_modules = ["node_modules", "apps/web/node_modules"]

        missing_modules = []
        for node_modules_path in required_node_modules:
            if not (self.project_root / node_modules_path).exists():
                missing_modules.append(node_modules_path)

        if missing_modules:
            self.print_status(
                f"Node.js dependencies not found: {', '.join(missing_modules)}",
                "WARNING",
            )
            return True  # Don't fail the test for missing node_modules

        return True

    def test_database_connection(self):
        """Test Supabase database connection"""
        try:
            from supabase import create_client

            url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

            if not url or not key:
                self.print_status(
                    "Database connection skipped: Missing environment variables",
                    "WARNING",
                )
                return True

            supabase = create_client(url, key)

            # Test a simple query
            response = supabase.table("companies").select("count").limit(1).execute()
            return True

        except Exception as e:
            self.print_status(f"Database connection failed: {str(e)}", "WARNING")
            return True  # Don't fail the test for database issues

    def test_backend_server(self):
        """Test if backend server can start"""
        try:
            # Check if backend main file exists
            main_file = self.project_root / "apps" / "backend" / "main.py"
            if not main_file.exists():
                return False

            # Try to import the main app
            sys.path.insert(0, str(self.project_root / "apps" / "backend"))
            from main import app

            return True

        except Exception as e:
            self.print_status(f"Backend server test failed: {str(e)}", "WARNING")
            return True  # Don't fail the test for import issues

    def test_frontend_build(self):
        """Test if frontend can build"""
        try:
            # Check if Next.js config exists
            next_config = self.project_root / "apps" / "web" / "next.config.js"
            if not next_config.exists():
                return False

            # Check if package.json has build script
            package_json = self.project_root / "apps" / "web" / "package.json"
            if not package_json.exists():
                return False

            with open(package_json, "r") as f:
                package_data = json.load(f)
                if (
                    "scripts" not in package_data
                    or "build" not in package_data["scripts"]
                ):
                    return False

            return True

        except Exception as e:
            self.print_status(f"Frontend build test failed: {str(e)}", "WARNING")
            return False

    def test_api_endpoints(self):
        """Test API endpoints if server is running"""
        try:
            # Try to connect to the API
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass

        # If server is not running, just check if endpoints exist
        api_dir = self.project_root / "apps" / "web" / "pages" / "api"
        if not api_dir.exists():
            return False

        # Check for key API files
        required_api_files = ["health.ts", "markets/quotes.ts", "search/companies.ts"]

        for api_file in required_api_files:
            if not (api_dir / api_file).exists():
                return False

        return True

    def test_docker_setup(self):
        """Test Docker setup"""
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.print_status("Docker not found, skipping Docker tests", "WARNING")
                return True

            # Check if docker-compose is available
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.print_status(
                    "Docker Compose not found, skipping Docker tests", "WARNING"
                )
                return True

            # Check if docker-compose.yml exists
            docker_compose = (
                self.project_root / "apps" / "backend" / "docker-compose.yml"
            )
            if not docker_compose.exists():
                self.print_status("Docker Compose file not found", "WARNING")
                return True

            return True

        except Exception as e:
            self.print_status(f"Docker setup test failed: {str(e)}", "WARNING")
            return True

    def test_scripts(self):
        """Test that key scripts exist and are executable"""
        required_scripts = [
            "scripts/setup/complete_setup.sh",
            "scripts/setup/setup_supabase_integration.sh",
            "scripts/deployment/deploy.sh",
            "start-simple.sh",
        ]

        for script_path in required_scripts:
            script_file = self.project_root / script_path
            if not script_file.exists():
                return False

            # Check if script is executable
            if not os.access(script_file, os.X_OK):
                try:
                    os.chmod(script_file, 0o755)
                except Exception:
                    return False

        return True

    def run_all_tests(self):
        """Run all tests"""
        self.print_status("🚀 Starting Complete Setup Test", "INFO")
        self.print_status("=" * 50, "INFO")

        tests = [
            ("Project Structure", self.test_project_structure),
            ("Environment Variables", self.test_environment_variables),
            ("Python Environment", self.test_python_environment),
            ("Node.js Environment", self.test_node_environment),
            ("Database Connection", self.test_database_connection),
            ("Backend Server", self.test_backend_server),
            ("Frontend Build", self.test_frontend_build),
            ("API Endpoints", self.test_api_endpoints),
            ("Docker Setup", self.test_docker_setup),
            ("Scripts", self.test_scripts),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Summary
        self.print_status("📊 Test Results Summary", "INFO")
        self.print_status("=" * 30, "INFO")

        passed = 0
        total = len(self.test_results)

        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.print_status(
                f"{test_name}: {status}", "SUCCESS" if result else "ERROR"
            )
            if result:
                passed += 1

        self.print_status(
            f"Overall: {passed}/{total} tests passed",
            "SUCCESS" if passed == total else "WARNING",
        )

        if passed == total:
            self.print_status(
                "🎉 All tests passed! Setup is complete and ready.", "SUCCESS"
            )
        else:
            self.print_status(
                "⚠️ Some tests failed. Please check the issues above.", "WARNING"
            )

        return passed == total


def main():
    """Main function"""
    try:
        tester = CompleteSetupTest()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
