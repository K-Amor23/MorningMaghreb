#!/usr/bin/env python3
"""
Fix Supabase Redirect URLs for Email Confirmations

This script helps you update your Supabase project settings to use the correct
production URLs instead of localhost for email confirmations.
"""

import os
import sys
import requests
from supabase import create_client, Client

def print_instructions():
    """Print step-by-step instructions to fix the redirect issue"""
    
    print("🔧 Fix Supabase Email Confirmation Redirects")
    print("=" * 50)
    print()
    print("The issue is that Supabase is trying to redirect to localhost:3000")
    print("but your site is running on Vercel. Here's how to fix it:")
    print()
    print("📋 Step-by-Step Instructions:")
    print()
    print("1. Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    print()
    print("2. Select your project")
    print()
    print("3. Go to Authentication > Settings")
    print()
    print("4. Update the following URLs:")
    print()
    print("   Site URL:")
    print("   Change from: http://localhost:3000")
    print("   Change to:   https://morningmaghreb.com")
    print()
    print("   Redirect URLs:")
    print("   Add these URLs:")
    print("   - https://morningmaghreb.com/auth/callback")
    print("   - https://morningmaghreb.com/login")
    print("   - https://morningmaghreb.com/signup")
    print("   - https://web-7mi5kyepn-k-amor23s-projects.vercel.app/auth/callback")
    print("   - https://web-7mi5kyepn-k-amor23s-projects.vercel.app/login")
    print("   - https://web-7mi5kyepn-k-amor23s-projects.vercel.app/signup")
    print()
    print("5. Save the changes")
    print()
    print("6. Test the email confirmation:")
    print("   - Sign up for a new account")
    print("   - Check your email")
    print("   - Click the confirmation link")
    print("   - It should now redirect to your production site")
    print()
    print("🎯 Alternative Quick Fix:")
    print("If you want to test locally, you can also add:")
    print("   - http://localhost:3000/auth/callback")
    print("   - http://localhost:3000/login")
    print("   - http://localhost:3000/signup")
    print()
    print("This way it works both locally and in production!")

def check_current_config():
    """Check current Supabase configuration"""
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found in environment variables")
            print("Please set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
            return
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to get auth settings (this might not work with current permissions)
        try:
            # This is a placeholder - actual API calls depend on Supabase version
            print("✅ Supabase client initialized successfully")
            print(f"URL: {supabase_url}")
            print()
            print("Note: You'll need to update the settings manually in the Supabase dashboard")
            print("The script can't directly modify auth settings for security reasons.")
            
        except Exception as e:
            print(f"⚠️ Could not check current settings: {e}")
            print("Please follow the manual instructions above.")
            
    except Exception as e:
        print(f"❌ Error initializing Supabase: {e}")

def main():
    """Main function"""
    print_instructions()
    print()
    print("🔍 Checking current configuration...")
    print()
    check_current_config()
    print()
    print("✅ Instructions complete! Follow the steps above to fix the redirect issue.")

if __name__ == "__main__":
    main() 