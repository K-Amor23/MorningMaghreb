#!/bin/bash

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
