#!/usr/bin/env python3
"""
Email Service Test Script for Casablanca Insights
Tests all email functionality including SendGrid, Supabase, and SMTP fallback
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend'))

from lib.email_service import (
    send_email,
    send_welcome_email,
    send_newsletter,
    send_password_reset,
    send_bulk_email
)

def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    
    color = colors.get(status, colors["INFO"])
    print(f"{color}[{status}]{colors['RESET']} {message}")

async def test_basic_email():
    """Test basic email sending"""
    print_status("Testing basic email sending...", "INFO")
    
    success = await send_email(
        to_email="test@example.com",
        subject="Test Email from Casablanca Insights",
        content="This is a test email to verify the email service is working correctly.",
        html_content="""
        <html>
        <body>
            <h1>Test Email</h1>
            <p>This is a test email from <strong>Casablanca Insights</strong>.</p>
            <p>If you receive this, the email service is working correctly!</p>
        </body>
        </html>
        """
    )
    
    if success:
        print_status("✅ Basic email test passed", "SUCCESS")
    else:
        print_status("❌ Basic email test failed", "ERROR")
    
    return success

async def test_welcome_email():
    """Test welcome email"""
    print_status("Testing welcome email...", "INFO")
    
    success = await send_welcome_email(
        email="test@example.com",
        name="Test User"
    )
    
    if success:
        print_status("✅ Welcome email test passed", "SUCCESS")
    else:
        print_status("❌ Welcome email test failed", "ERROR")
    
    return success

async def test_newsletter_email():
    """Test newsletter email"""
    print_status("Testing newsletter email...", "INFO")
    
    success = await send_newsletter(
        email="test@example.com",
        subject="Weekly Market Recap - Test",
        content="""
        This is a test newsletter email.
        
        Market Summary:
        - MASI Index: +2.5%
        - Top Performer: ATW (+5.2%)
        - Volume Leader: CIH (2.1M shares)
        
        Stay tuned for more insights!
        """
    )
    
    if success:
        print_status("✅ Newsletter email test passed", "SUCCESS")
    else:
        print_status("❌ Newsletter email test failed", "ERROR")
    
    return success

async def test_password_reset():
    """Test password reset email"""
    print_status("Testing password reset email...", "INFO")
    
    reset_token = "test_token_12345"
    success = await send_password_reset(
        email="test@example.com",
        reset_token=reset_token
    )
    
    if success:
        print_status("✅ Password reset email test passed", "SUCCESS")
    else:
        print_status("❌ Password reset email test failed", "ERROR")
    
    return success

async def test_bulk_email():
    """Test bulk email sending"""
    print_status("Testing bulk email sending...", "INFO")
    
    test_subscribers = [
        "test1@example.com",
        "test2@example.com",
        "test3@example.com"
    ]
    
    results = await send_bulk_email(
        subscribers=test_subscribers,
        subject="Bulk Test Email",
        content="This is a test bulk email from Casablanca Insights."
    )
    
    print_status(f"Bulk email results: {results['sent']} sent, {results['failed']} failed", "INFO")
    
    if results['sent'] > 0:
        print_status("✅ Bulk email test passed", "SUCCESS")
        return True
    else:
        print_status("❌ Bulk email test failed", "ERROR")
        return False

async def test_email_providers():
    """Test which email providers are available"""
    print_status("Checking email provider availability...", "INFO")
    
    # Check environment variables
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print_status(f"SendGrid API Key: {'✅ Set' if sendgrid_key else '❌ Not set'}", "INFO")
    print_status(f"Supabase URL: {'✅ Set' if supabase_url else '❌ Not set'}", "INFO")
    print_status(f"Supabase Service Key: {'✅ Set' if supabase_key else '❌ Not set'}", "INFO")
    
    # Check imports
    try:
        from sendgrid import SendGridAPIClient
        print_status("✅ SendGrid library available", "SUCCESS")
    except ImportError:
        print_status("❌ SendGrid library not available", "WARNING")
    
    try:
        from supabase import create_client
        print_status("✅ Supabase library available", "SUCCESS")
    except ImportError:
        print_status("❌ Supabase library not available", "WARNING")

async def run_all_tests():
    """Run all email tests"""
    print_status("🚀 Starting Email Service Tests", "INFO")
    print_status("=" * 50, "INFO")
    
    # Check providers first
    await test_email_providers()
    print()
    
    # Run individual tests
    tests = [
        ("Basic Email", test_basic_email),
        ("Welcome Email", test_welcome_email),
        ("Newsletter Email", test_newsletter_email),
        ("Password Reset", test_password_reset),
        ("Bulk Email", test_bulk_email),
    ]
    
    results = []
    for test_name, test_func in tests:
        print_status(f"Running {test_name} test...", "INFO")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"❌ {test_name} test failed with error: {str(e)}", "ERROR")
            results.append((test_name, False))
        print()
    
    # Summary
    print_status("📊 Test Results Summary", "INFO")
    print_status("=" * 30, "INFO")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"{test_name}: {status}", "SUCCESS" if result else "ERROR")
        if result:
            passed += 1
    
    print()
    print_status(f"Overall: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
    
    if passed == total:
        print_status("🎉 All email tests passed! Email service is working correctly.", "SUCCESS")
    else:
        print_status("⚠️ Some tests failed. Check your email configuration.", "WARNING")
    
    return passed == total

def main():
    """Main function"""
    print_status("📧 Casablanca Insights Email Service Test", "INFO")
    print_status(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("apps/backend/lib/email_service.py"):
        print_status("❌ Please run this script from the project root directory", "ERROR")
        sys.exit(1)
    
    # Run tests
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\n⚠️ Tests interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"❌ Test runner failed: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main() 