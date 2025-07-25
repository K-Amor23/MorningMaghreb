#!/usr/bin/env python3
"""
Newsletter Generation Test Script

This script tests the newsletter generation system with real market data
and AI-powered content creation.

Usage:
    python scripts/test_newsletter_generation.py [--preview] [--send-test] [--email test@example.com]
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install: pip install requests python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

class NewsletterTester:
    """Test the newsletter generation system"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            print("   Newsletter generation will use fallback content")
        else:
            print("✅ OpenAI API key found")
    
    async def test_newsletter_preview(self, language: str = "en") -> dict:
        """Test newsletter preview generation"""
        print(f"\n📧 Testing Newsletter Preview ({language.upper()})")
        print("=" * 50)
        
        try:
            url = f"{self.api_base_url}/api/newsletter/weekly-recap/preview"
            payload = {
                "include_macro": True,
                "include_sectors": True,
                "include_top_movers": True,
                "language": language
            }
            
            print(f"Making request to: {url}")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Newsletter preview generated successfully!")
                print(f"📝 Subject: {data.get('subject', 'N/A')}")
                print(f"📅 Generated at: {data.get('generated_at', 'N/A')}")
                print(f"📄 Content length: {len(data.get('content', ''))} characters")
                
                # Save preview to file
                preview_file = f"newsletter_preview_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(preview_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Preview saved to: {preview_file}")
                return data
            else:
                print(f"❌ Failed to generate preview: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing newsletter preview: {e}")
            return None
    
    async def test_newsletter_generation(self, language: str = "en") -> dict:
        """Test full newsletter generation"""
        print(f"\n📧 Testing Newsletter Generation ({language.upper()})")
        print("=" * 50)
        
        try:
            url = f"{self.api_base_url}/api/newsletter/generate-weekly-recap"
            payload = {
                "include_macro": True,
                "include_sectors": True,
                "include_top_movers": True,
                "language": language
            }
            
            print(f"Making request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Newsletter generated successfully!")
                print(f"📝 ID: {data.get('id', 'N/A')}")
                print(f"📝 Subject: {data.get('subject', 'N/A')}")
                print(f"📅 Sent at: {data.get('sent_at', 'N/A')}")
                print(f"👥 Recipients: {data.get('recipient_count', 'N/A')}")
                print(f"📄 Content length: {len(data.get('content', ''))} characters")
                
                # Save generated newsletter to file
                newsletter_file = f"newsletter_generated_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(newsletter_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Newsletter saved to: {newsletter_file}")
                return data
            else:
                print(f"❌ Failed to generate newsletter: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing newsletter generation: {e}")
            return None
    
    async def test_send_test_email(self, email: str) -> bool:
        """Test sending a test email"""
        print(f"\n📧 Testing Email Sending")
        print("=" * 50)
        
        try:
            url = f"{self.api_base_url}/api/newsletter/send-test"
            payload = {"email": email}
            
            print(f"Sending test email to: {email}")
            print(f"Making request to: {url}")
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Test email sent successfully!")
                return True
            else:
                print(f"❌ Failed to send test email: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending test email: {e}")
            return False
    
    async def test_market_data_integration(self) -> dict:
        """Test market data integration for newsletter"""
        print(f"\n📊 Testing Market Data Integration")
        print("=" * 50)
        
        try:
            # Test market quotes
            quotes_url = f"{self.api_base_url}/api/markets/quotes"
            print(f"Fetching market quotes from: {quotes_url}")
            
            quotes_response = requests.get(quotes_url, timeout=10)
            if quotes_response.status_code == 200:
                quotes_data = quotes_response.json()
                print(f"✅ Market quotes fetched: {len(quotes_data.get('quotes', []))} quotes")
            else:
                print(f"❌ Failed to fetch market quotes: {quotes_response.status_code}")
            
            # Test market summary
            summary_url = f"{self.api_base_url}/api/markets/summary"
            print(f"Fetching market summary from: {summary_url}")
            
            summary_response = requests.get(summary_url, timeout=10)
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print(f"✅ Market summary fetched successfully")
            else:
                print(f"❌ Failed to fetch market summary: {summary_response.status_code}")
            
            # Test sector data
            sectors_url = f"{self.api_base_url}/api/markets/sectors"
            print(f"Fetching sector data from: {sectors_url}")
            
            sectors_response = requests.get(sectors_url, timeout=10)
            if sectors_response.status_code == 200:
                sectors_data = sectors_response.json()
                print(f"✅ Sector data fetched: {len(sectors_data.get('sectors', []))} sectors")
            else:
                print(f"❌ Failed to fetch sector data: {sectors_response.status_code}")
            
            return {
                "quotes": quotes_data if quotes_response.status_code == 200 else None,
                "summary": summary_data if summary_response.status_code == 200 else None,
                "sectors": sectors_data if sectors_response.status_code == 200 else None
            }
                
        except Exception as e:
            print(f"❌ Error testing market data integration: {e}")
            return {}
    
    async def test_openai_integration(self) -> bool:
        """Test OpenAI integration"""
        print(f"\n🤖 Testing OpenAI Integration")
        print("=" * 50)
        
        if not self.openai_api_key:
            print("❌ No OpenAI API key found")
            return False
        
        try:
            # Test a simple AI request
            url = f"{self.api_base_url}/api/chat"
            payload = {
                "message": "Generate a brief market summary for Morocco",
                "context": {"ticker": "ATW", "language": "en"}
            }
            
            print(f"Testing AI chat endpoint: {url}")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ OpenAI integration working!")
                print(f"🤖 AI Response: {data.get('response', 'N/A')[:100]}...")
                return True
            else:
                print(f"❌ OpenAI integration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing OpenAI integration: {e}")
            return False
    
    async def run_comprehensive_test(self, preview_only: bool = False, test_email: str = None):
        """Run comprehensive newsletter testing"""
        print("🚀 Starting Comprehensive Newsletter Testing")
        print("=" * 60)
        
        # Test market data integration
        market_data = await self.test_market_data_integration()
        
        # Test OpenAI integration
        openai_working = await self.test_openai_integration()
        
        # Test newsletter preview in different languages
        languages = ["en", "fr", "ar"]
        preview_results = {}
        
        for lang in languages:
            preview_data = await self.test_newsletter_preview(lang)
            preview_results[lang] = preview_data
        
        # Test full newsletter generation if not preview only
        if not preview_only:
            generation_results = {}
            for lang in languages:
                generation_data = await self.test_newsletter_generation(lang)
                generation_results[lang] = generation_data
        
        # Test email sending if email provided
        if test_email:
            email_sent = await self.test_send_test_email(test_email)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TESTING SUMMARY")
        print("=" * 60)
        
        print(f"📊 Market Data: {'✅ Working' if market_data else '❌ Failed'}")
        print(f"🤖 OpenAI: {'✅ Working' if openai_working else '❌ Failed'}")
        
        print(f"\n📧 Newsletter Previews:")
        for lang, result in preview_results.items():
            status = "✅ Success" if result else "❌ Failed"
            print(f"   {lang.upper()}: {status}")
        
        if not preview_only:
            print(f"\n📧 Newsletter Generation:")
            for lang, result in generation_results.items():
                status = "✅ Success" if result else "❌ Failed"
                print(f"   {lang.upper()}: {status}")
        
        if test_email:
            print(f"\n📧 Email Sending:")
            print(f"   Test Email: {'✅ Sent' if email_sent else '❌ Failed'}")
        
        print(f"\n💾 Generated files saved in current directory")
        print(f"📝 Check the JSON files for detailed content")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test Newsletter Generation System')
    parser.add_argument('--preview', action='store_true', help='Only test preview generation')
    parser.add_argument('--send-test', action='store_true', help='Send test email')
    parser.add_argument('--email', type=str, help='Email address for test sending')
    parser.add_argument('--language', type=str, default='en', choices=['en', 'fr', 'ar'], help='Language for testing')
    
    args = parser.parse_args()
    
    # Validate email if provided
    if args.send_test and not args.email:
        print("❌ Error: --email is required when using --send-test")
        sys.exit(1)
    
    # Create tester and run tests
    tester = NewsletterTester()
    
    if args.send_test:
        # Just test email sending
        success = await tester.test_send_test_email(args.email)
        sys.exit(0 if success else 1)
    elif args.preview:
        # Just test preview
        result = await tester.test_newsletter_preview(args.language)
        sys.exit(0 if result else 1)
    else:
        # Run comprehensive test
        await tester.run_comprehensive_test(preview_only=False, test_email=args.email)

if __name__ == '__main__':
    asyncio.run(main()) 