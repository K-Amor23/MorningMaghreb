#!/usr/bin/env python3

"""
Fix Supabase Newsletter Connection Issue

This script helps you update the Supabase configuration to fix the newsletter signup issue.
"""

import os
import sys
import json
from pathlib import Path

def print_header():
    print("🔧 Fix Supabase Newsletter Connection")
    print("=" * 50)
    print()

def print_instructions():
    print("📋 The issue is that your Supabase credentials in vercel.json are placeholders.")
    print("You need to update them with your actual Supabase project credentials.")
    print()
    
    print("🔍 Step 1: Get Your Supabase Credentials")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings > API")
    print("4. Copy the following values:")
    print("   - Project URL")
    print("   - anon/public key")
    print("   - service_role key (for backend)")
    print()
    
    print("🔧 Step 2: Update Vercel Configuration")
    print("You need to update apps/web/vercel.json with your actual credentials:")
    print()
    
    print("Current (placeholder) values:")
    print("  NEXT_PUBLIC_SUPABASE_URL: https://supabase-sky-garden.supabase.co")
    print("  NEXT_PUBLIC_SUPABASE_ANON_KEY: YOUR_NEW_ANON_KEY_HERE")
    print("  SUPABASE_SERVICE_ROLE_KEY: YOUR_NEW_SERVICE_ROLE_KEY_HERE")
    print()
    
    print("Replace with your actual values:")
    print("  NEXT_PUBLIC_SUPABASE_URL: https://your-project-id.supabase.co")
    print("  NEXT_PUBLIC_SUPABASE_ANON_KEY: your-actual-anon-key")
    print("  SUPABASE_SERVICE_ROLE_KEY: your-actual-service-role-key")
    print()
    
    print("🔧 Step 3: Deploy the Changes")
    print("After updating the credentials:")
    print("1. Commit the changes: git add . && git commit -m 'Update Supabase credentials'")
    print("2. Push to GitHub: git push origin main")
    print("3. Deploy to Vercel: cd apps/web && npx vercel --prod")
    print()
    
    print("🔧 Step 4: Test the Newsletter")
    print("1. Visit your site")
    print("2. Try signing up for the newsletter")
    print("3. Check if it works now")
    print()

def check_current_config():
    print("📊 Current Configuration Status:")
    print()
    
    vercel_config_path = Path("apps/web/vercel.json")
    if vercel_config_path.exists():
        with open(vercel_config_path, 'r') as f:
            config = json.load(f)
        
        supabase_url = config.get('env', {}).get('NEXT_PUBLIC_SUPABASE_URL', 'Not found')
        supabase_anon_key = config.get('env', {}).get('NEXT_PUBLIC_SUPABASE_ANON_KEY', 'Not found')
        supabase_service_key = config.get('env', {}).get('SUPABASE_SERVICE_ROLE_KEY', 'Not found')
        
        print(f"✅ Supabase URL: {supabase_url}")
        print(f"❌ Anon Key: {supabase_anon_key}")
        print(f"❌ Service Key: {supabase_service_key}")
        
        if 'YOUR_NEW' in str(supabase_anon_key) or 'YOUR_NEW' in str(supabase_service_key):
            print("\n⚠️  ISSUE DETECTED: Using placeholder credentials!")
            print("   This is why the newsletter signup is failing.")
        else:
            print("\n✅ Credentials appear to be set correctly")
    else:
        print("❌ vercel.json not found")

def create_fix_script():
    print("🔧 Creating Fix Script...")
    
    script_content = '''#!/bin/bash

# Fix Supabase Newsletter Connection
echo "🔧 Fixing Supabase Newsletter Connection..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Update vercel.json with your actual Supabase credentials
echo "📝 Updating vercel.json..."
echo ""
echo "Please edit apps/web/vercel.json and replace:"
echo "  NEXT_PUBLIC_SUPABASE_ANON_KEY: YOUR_NEW_ANON_KEY_HERE"
echo "  SUPABASE_SERVICE_ROLE_KEY: YOUR_NEW_SERVICE_ROLE_KEY_HERE"
echo ""
echo "With your actual Supabase credentials from:"
echo "  https://supabase.com/dashboard > Settings > API"
echo ""

# Deploy the changes
echo "🚀 Deploying changes..."
cd apps/web
npx vercel --prod

echo "✅ Fix complete! Test the newsletter signup now."
'''
    
    script_path = Path("fix_newsletter.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Created fix script: {script_path}")
    print("Run: ./fix_newsletter.sh")

def main():
    print_header()
    check_current_config()
    print()
    print_instructions()
    print()
    create_fix_script()
    print()
    print("🎯 Next Steps:")
    print("1. Get your Supabase credentials from the dashboard")
    print("2. Update apps/web/vercel.json with real credentials")
    print("3. Run: ./fix_newsletter.sh")
    print("4. Test the newsletter signup")
    print()
    print("🔗 Helpful Links:")
    print("• Supabase Dashboard: https://supabase.com/dashboard")
    print("• Vercel Dashboard: https://vercel.com/dashboard")
    print("• Your Site: https://morningmaghreb.com")

if __name__ == "__main__":
    main() 