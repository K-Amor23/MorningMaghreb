#!/bin/bash
# Deploy Environment Variables to Vercel
# This script syncs .env.local to Vercel environments

set -e

echo "🚀 Syncing Environment Variables to Vercel"
echo "=========================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "   npm i -g vercel"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local not found. Please create it first."
    exit 1
fi

# Check if project is linked
if ! vercel project ls &> /dev/null; then
    echo "⚠️  Project not linked. Please run 'vercel link' first."
    exit 1
fi

echo "📥 Pulling current environment variables from Vercel..."
vercel env pull .env.local

echo "📤 Pushing local environment variables to Vercel..."
echo "Note: This will add each variable individually to Vercel"
echo ""

# Read .env.local and add each variable to Vercel
while IFS='=' read -r name value; do
    # Skip blank lines or comments
    if [[ -z "$name" || "$name" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    name=$(echo "$name" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip if name is empty after trimming
    if [[ -z "$name" ]]; then
        continue
    fi
    
    echo "Adding $name to Vercel..."
    vercel env add "$name" production <<< "$value" || echo "Failed to add $name"
    vercel env add "$name" preview <<< "$value" || echo "Failed to add $name"
    vercel env add "$name" development <<< "$value" || echo "Failed to add $name"
done < .env.local

echo "✅ Environment variables synced successfully!"
echo ""
echo "📋 Current Vercel environments:"
vercel env ls

echo ""
echo "🔗 To view your project:"
vercel project ls 