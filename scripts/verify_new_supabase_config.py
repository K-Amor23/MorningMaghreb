#!/usr/bin/env python3
"""
Verification script to ensure all authentication and newsletter signups 
are pointing to the new Supabase instance: supabase-sky-garden
"""

import os
import re
import requests
from typing import List, Dict, Tuple


class SupabaseConfigVerifier:
    def __init__(self):
        self.new_supabase_url = "https://supabase-sky-garden.supabase.co"
        self.old_supabase_url = "https://kszekypwdjqaycpuayda.supabase.co"
        self.files_to_check = [
            "vercel.json",
            "apps/web/vercel.json",
            "apps/web/lib/supabase.ts",
            "apps/web/pages/api/newsletter/signup.ts",
            "apps/web/pages/api/auth/login.ts",
            "apps/web/pages/api/auth/register.ts",
            "apps/web/pages/api/auth/webhook.ts",
            "apps/mobile/src/services/auth.ts",
            "packages/shared/src/services/api.ts",
        ]

    def check_file_configuration(self, filepath: str) -> Dict:
        """Check if a file is configured to use the new Supabase instance"""
        result = {"file": filepath, "status": "unknown", "issues": [], "fixed": False}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for old Supabase URL
            if self.old_supabase_url in content:
                result["status"] = "needs_update"
                result["issues"].append(
                    f"Contains old Supabase URL: {self.old_supabase_url}"
                )

            # Check for new Supabase URL
            if self.new_supabase_url in content:
                result["status"] = "correct"
                result["issues"].append(
                    f"✅ Using new Supabase URL: {self.new_supabase_url}"
                )
            else:
                result["status"] = "needs_update"
                result["issues"].append(
                    f"Missing new Supabase URL: {self.new_supabase_url}"
                )

            # Check for placeholder API keys
            if (
                "YOUR_NEW_ANON_KEY_HERE" in content
                or "YOUR_NEW_SERVICE_ROLE_KEY_HERE" in content
            ):
                result["status"] = "needs_keys"
                result["issues"].append("⚠️ API keys need to be updated")

        except FileNotFoundError:
            result["status"] = "not_found"
            result["issues"].append("File not found")
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error reading file: {str(e)}")

        return result

    def check_environment_variables(self) -> Dict:
        """Check environment variables for Supabase configuration"""
        result = {"env_vars": {}, "status": "unknown", "issues": []}

        env_vars = [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ]

        for var in env_vars:
            value = os.getenv(var)
            if value:
                result["env_vars"][var] = value
                if self.old_supabase_url in value:
                    result["issues"].append(f"⚠️ {var} contains old Supabase URL")
                elif self.new_supabase_url in value:
                    result["issues"].append(f"✅ {var} uses new Supabase URL")
                else:
                    result["issues"].append(f"ℹ️ {var} has different URL")
            else:
                result["issues"].append(f"❌ {var} not set")

        return result

    def test_supabase_connection(self, url: str, key: str) -> Dict:
        """Test connection to Supabase instance"""
        result = {"url": url, "status": "unknown", "error": None}

        try:
            headers = {"apikey": key, "Authorization": f"Bearer {key}"}

            # Test basic connection
            response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)

            if response.status_code == 200:
                result["status"] = "connected"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}: {response.text}"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def generate_fix_script(self, issues: List[Dict]) -> str:
        """Generate a script to fix configuration issues"""
        script = """#!/bin/bash
# Fix Supabase Configuration Script
# Run this script to update all configuration files

echo "🔧 Fixing Supabase configuration..."

# Update vercel.json files
sed -i '' 's|https://kszekypwdjqaycpuayda.supabase.co|https://supabase-sky-garden.supabase.co|g' vercel.json
sed -i '' 's|https://kszekypwdjqaycpuayda.supabase.co|https://supabase-sky-garden.supabase.co|g' apps/web/vercel.json

# Update environment variables (you'll need to set these manually)
echo "Please update your environment variables:"
echo "NEXT_PUBLIC_SUPABASE_URL=https://supabase-sky-garden.supabase.co"
echo "NEXT_PUBLIC_SUPABASE_ANON_KEY=your_new_anon_key"
echo "SUPABASE_SERVICE_ROLE_KEY=your_new_service_role_key"

echo "✅ Configuration updated!"
"""
        return script

    def run_verification(self) -> Dict:
        """Run complete verification"""
        print("🔍 Verifying Supabase Configuration...")
        print("=" * 60)

        results = {
            "files": [],
            "environment": {},
            "connection_tests": [],
            "summary": {
                "total_files": 0,
                "correct_files": 0,
                "needs_update": 0,
                "errors": 0,
            },
        }

        # Check files
        print("📁 Checking configuration files...")
        for filepath in self.files_to_check:
            result = self.check_file_configuration(filepath)
            results["files"].append(result)
            results["summary"]["total_files"] += 1

            if result["status"] == "correct":
                results["summary"]["correct_files"] += 1
            elif result["status"] in ["needs_update", "needs_keys"]:
                results["summary"]["needs_update"] += 1
            elif result["status"] == "error":
                results["summary"]["errors"] += 1

            # Print file status
            status_emoji = {
                "correct": "✅",
                "needs_update": "⚠️",
                "needs_keys": "🔑",
                "error": "❌",
                "not_found": "📄",
                "unknown": "❓",
            }

            print(f"{status_emoji.get(result['status'], '❓')} {filepath}")
            for issue in result["issues"]:
                print(f"   {issue}")

        # Check environment variables
        print("\n🌍 Checking environment variables...")
        env_result = self.check_environment_variables()
        results["environment"] = env_result

        for issue in env_result["issues"]:
            print(f"   {issue}")

        # Test connections if keys are available
        print("\n🔗 Testing Supabase connections...")

        # Test old instance (if keys available)
        old_url = os.getenv("OLD_SUPABASE_URL", self.old_supabase_url)
        old_key = os.getenv("OLD_SUPABASE_ANON_KEY")
        if old_key:
            old_test = self.test_supabase_connection(old_url, old_key)
            results["connection_tests"].append({"instance": "old", "result": old_test})
            print(f"   Old instance ({old_url}): {old_test['status']}")

        # Test new instance (if keys available)
        new_url = os.getenv("NEW_SUPABASE_URL", self.new_supabase_url)
        new_key = os.getenv("NEW_SUPABASE_ANON_KEY")
        if new_key:
            new_test = self.test_supabase_connection(new_url, new_key)
            results["connection_tests"].append({"instance": "new", "result": new_test})
            print(f"   New instance ({new_url}): {new_test['status']}")
        else:
            print(f"   New instance ({new_url}): ⚠️ No API key provided")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"📁 Files checked: {results['summary']['total_files']}")
        print(f"✅ Correctly configured: {results['summary']['correct_files']}")
        print(f"⚠️ Needs update: {results['summary']['needs_update']}")
        print(f"❌ Errors: {results['summary']['errors']}")

        if results["summary"]["needs_update"] > 0:
            print("\n🔧 GENERATED FIX SCRIPT:")
            print("-" * 40)
            print(self.generate_fix_script(results["files"]))

        print("\n🎯 NEXT STEPS:")
        print("1. Update API keys in vercel.json files")
        print("2. Set environment variables for new Supabase instance")
        print("3. Run the master schema migration on the new instance")
        print("4. Test authentication and newsletter signups")

        return results


def main():
    verifier = SupabaseConfigVerifier()
    results = verifier.run_verification()

    # Exit with error code if there are issues
    if results["summary"]["needs_update"] > 0 or results["summary"]["errors"] > 0:
        exit(1)
    else:
        print("\n🎉 All configurations are correct!")
        exit(0)


if __name__ == "__main__":
    main()
