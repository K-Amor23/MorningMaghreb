#!/usr/bin/env python3
"""
Newsletter Dashboard

Interactive dashboard for managing newsletter generation, subscribers, and content.
Provides real-time monitoring and management capabilities.

Usage:
    python scripts/newsletter_dashboard.py [--interactive] [--generate] [--stats]
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

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

class NewsletterDashboard:
    """Interactive newsletter dashboard"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get newsletter dashboard statistics"""
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "openai_available": bool(self.openai_api_key),
                "api_status": "unknown",
                "subscribers": 0,
                "campaigns": 0,
                "recent_content": []
            }
            
            # Test API connectivity
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=5)
                stats["api_status"] = "online" if response.status_code == 200 else "error"
            except:
                stats["api_status"] = "offline"
            
            # Get subscribers count
            try:
                response = requests.get(f"{self.api_base_url}/api/newsletter/subscribers", timeout=10)
                if response.status_code == 200:
                    subscribers = response.json()
                    stats["subscribers"] = len(subscribers)
            except:
                pass
            
            # Get recent campaigns
            try:
                response = requests.get(f"{self.api_base_url}/api/newsletter/campaigns", timeout=10)
                if response.status_code == 200:
                    campaigns = response.json()
                    stats["campaigns"] = len(campaigns)
                    stats["recent_content"] = campaigns[:5]  # Last 5 campaigns
            except:
                pass
            
            return stats
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {"error": str(e)}
    
    def display_dashboard(self, stats: Dict[str, Any]):
        """Display the dashboard"""
        print("\n" + "=" * 60)
        print("📧 CASABLANCA INSIGHTS - NEWSLETTER DASHBOARD")
        print("=" * 60)
        print(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # System Status
        print(f"\n🔧 System Status:")
        print(f"   API: {'🟢 Online' if stats.get('api_status') == 'online' else '🔴 Offline'}")
        print(f"   OpenAI: {'🟢 Available' if stats.get('openai_available') else '🔴 Not Available'}")
        
        # Newsletter Stats
        print(f"\n📊 Newsletter Statistics:")
        print(f"   Subscribers: {stats.get('subscribers', 0)}")
        print(f"   Campaigns: {stats.get('campaigns', 0)}")
        
        # Recent Content
        recent_content = stats.get('recent_content', [])
        if recent_content:
            print(f"\n📝 Recent Content:")
            for i, content in enumerate(recent_content[:3], 1):
                subject = content.get('subject', 'No Subject')
                created = content.get('created_at', 'Unknown')
                print(f"   {i}. {subject[:50]}... ({created})")
        
        print("\n" + "=" * 60)
    
    async def generate_newsletter_content(self, content_type: str, language: str = "en", ticker: str = None) -> Dict[str, Any]:
        """Generate newsletter content"""
        print(f"\n📧 Generating {content_type} newsletter in {language.upper()}")
        
        try:
            if content_type == "weekly":
                url = f"{self.api_base_url}/api/newsletter/generate-weekly-recap"
                payload = {
                    "include_macro": True,
                    "include_sectors": True,
                    "include_top_movers": True,
                    "language": language
                }
            elif content_type == "daily":
                url = f"{self.api_base_url}/api/newsletter/weekly-recap/preview"
                payload = {"language": language}
            else:
                print(f"❌ Unknown content type: {content_type}")
                return {}
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {content_type.title()} newsletter generated successfully!")
                return data
            else:
                print(f"❌ Failed to generate {content_type} newsletter: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error generating {content_type} newsletter: {e}")
            return {}
    
    async def send_test_email(self, email: str) -> bool:
        """Send test email"""
        print(f"\n📧 Sending test email to {email}")
        
        try:
            url = f"{self.api_base_url}/api/newsletter/send-test"
            payload = {"email": email}
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Test email sent successfully!")
                return True
            else:
                print(f"❌ Failed to send test email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending test email: {e}")
            return False
    
    async def get_subscribers(self) -> List[Dict[str, Any]]:
        """Get newsletter subscribers"""
        try:
            response = requests.get(f"{self.api_base_url}/api/newsletter/subscribers", timeout=10)
            
            if response.status_code == 200:
                subscribers = response.json()
                return subscribers
            else:
                print(f"❌ Failed to get subscribers: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting subscribers: {e}")
            return []
    
    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get newsletter campaigns"""
        try:
            response = requests.get(f"{self.api_base_url}/api/newsletter/campaigns", timeout=10)
            
            if response.status_code == 200:
                campaigns = response.json()
                return campaigns
            else:
                print(f"❌ Failed to get campaigns: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting campaigns: {e}")
            return []
    
    def display_subscribers(self, subscribers: List[Dict[str, Any]]):
        """Display subscribers"""
        print(f"\n👥 Newsletter Subscribers ({len(subscribers)})")
        print("-" * 40)
        
        if not subscribers:
            print("   No subscribers found")
            return
        
        for i, subscriber in enumerate(subscribers[:10], 1):  # Show first 10
            email = subscriber.get('email', 'No Email')
            status = subscriber.get('status', 'Unknown')
            created = subscriber.get('created_at', 'Unknown')
            print(f"   {i}. {email} ({status}) - {created}")
        
        if len(subscribers) > 10:
            print(f"   ... and {len(subscribers) - 10} more subscribers")
    
    def display_campaigns(self, campaigns: List[Dict[str, Any]]):
        """Display campaigns"""
        print(f"\n📝 Newsletter Campaigns ({len(campaigns)})")
        print("-" * 40)
        
        if not campaigns:
            print("   No campaigns found")
            return
        
        for i, campaign in enumerate(campaigns[:10], 1):  # Show first 10
            subject = campaign.get('subject', 'No Subject')
            created = campaign.get('created_at', 'Unknown')
            sent = campaign.get('sent_at', 'Not Sent')
            recipients = campaign.get('recipient_count', 0)
            print(f"   {i}. {subject[:50]}...")
            print(f"      Created: {created} | Sent: {sent} | Recipients: {recipients}")
            print()
    
    async def interactive_menu(self):
        """Interactive menu system"""
        while True:
            print("\n📧 Newsletter Dashboard Menu")
            print("=" * 30)
            print("1. 📊 View Dashboard Stats")
            print("2. 👥 View Subscribers")
            print("3. 📝 View Campaigns")
            print("4. 📧 Generate Weekly Newsletter")
            print("5. 📧 Generate Daily Newsletter")
            print("6. 📧 Send Test Email")
            print("7. 🔄 Refresh All Data")
            print("0. ❌ Exit")
            
            try:
                choice = input("\nSelect an option (0-7): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    stats = await self.get_dashboard_stats()
                    self.display_dashboard(stats)
                elif choice == "2":
                    subscribers = await self.get_subscribers()
                    self.display_subscribers(subscribers)
                elif choice == "3":
                    campaigns = await self.get_campaigns()
                    self.display_campaigns(campaigns)
                elif choice == "4":
                    language = input("Language (en/fr/ar) [en]: ").strip() or "en"
                    content = await self.generate_newsletter_content("weekly", language)
                    if content:
                        print(f"\n📄 Generated Content Preview:")
                        print(f"Subject: {content.get('subject', 'N/A')}")
                        print(f"Content Length: {len(content.get('content', ''))} characters")
                elif choice == "5":
                    language = input("Language (en/fr/ar) [en]: ").strip() or "en"
                    content = await self.generate_newsletter_content("daily", language)
                    if content:
                        print(f"\n📄 Generated Content Preview:")
                        print(f"Subject: {content.get('subject', 'N/A')}")
                        print(f"Content Length: {len(content.get('content', ''))} characters")
                elif choice == "6":
                    email = input("Enter email address: ").strip()
                    if email:
                        await self.send_test_email(email)
                    else:
                        print("❌ Email address required")
                elif choice == "7":
                    print("🔄 Refreshing data...")
                    stats = await self.get_dashboard_stats()
                    self.display_dashboard(stats)
                else:
                    print("❌ Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Newsletter Dashboard')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--generate', type=str, choices=['weekly', 'daily'], help='Generate newsletter content')
    parser.add_argument('--language', type=str, choices=['en', 'fr', 'ar'], default='en', help='Language for content')
    parser.add_argument('--stats', action='store_true', help='Show dashboard statistics')
    parser.add_argument('--subscribers', action='store_true', help='Show subscribers')
    parser.add_argument('--campaigns', action='store_true', help='Show campaigns')
    parser.add_argument('--test-email', type=str, help='Send test email')
    
    args = parser.parse_args()
    
    dashboard = NewsletterDashboard()
    
    if args.interactive:
        # Interactive mode
        await dashboard.interactive_menu()
    else:
        # Command-line mode
        if args.stats:
            stats = await dashboard.get_dashboard_stats()
            dashboard.display_dashboard(stats)
        
        if args.subscribers:
            subscribers = await dashboard.get_subscribers()
            dashboard.display_subscribers(subscribers)
        
        if args.campaigns:
            campaigns = await dashboard.get_campaigns()
            dashboard.display_campaigns(campaigns)
        
        if args.generate:
            content = await dashboard.generate_newsletter_content(args.generate, args.language)
            if content:
                print(f"\n📄 Generated Content:")
                print(f"Subject: {content.get('subject', 'N/A')}")
                print(f"Content Length: {len(content.get('content', ''))} characters")
        
        if args.test_email:
            await dashboard.send_test_email(args.test_email)
        
        # If no specific action, show dashboard
        if not any([args.stats, args.subscribers, args.campaigns, args.generate, args.test_email]):
            stats = await dashboard.get_dashboard_stats()
            dashboard.display_dashboard(stats)

if __name__ == '__main__':
    asyncio.run(main()) 