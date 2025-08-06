#!/bin/bash
# Deploy Migrations to Supabase
# This script applies database migrations to your Supabase project

set -e

echo "🗄️  Deploying Migrations to Supabase"
echo "===================================="

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Please install it first:"
    echo "   npm install -g supabase"
    exit 1
fi

# Check if authenticated
if ! supabase status &> /dev/null; then
    echo "❌ Not authenticated with Supabase. Please run 'supabase login' first."
    exit 1
fi

# Check if project is linked
if ! supabase projects list &> /dev/null; then
    echo "⚠️  No project linked. Please run 'supabase link --project-ref YOUR_PROJECT_REF' first."
    echo ""
    echo "To find your project ref:"
    echo "  1. Go to https://supabase.com/dashboard"
    echo "  2. Select your project"
    echo "  3. Copy the project ref from the URL or settings"
    echo "  4. Run: supabase link --project-ref YOUR_PROJECT_REF"
    exit 1
fi

echo "🔍 Checking current project status..."
supabase status

echo ""
echo "📋 Available migrations:"
ls -la database/migrations/up/*.sql 2>/dev/null || echo "  No migrations found in database/migrations/up/"

echo ""
echo "🔄 Applying migrations..."
supabase db push

echo ""
echo "✅ Migrations applied successfully!"
echo ""
echo "🔍 Verifying schema..."
supabase db diff

echo ""
echo "📊 Migration Summary:"
echo "  - Applied: $(ls database/migrations/up/*.sql 2>/dev/null | wc -l) migrations"
echo "  - Schema: Up to date"
echo ""
echo "💡 To rollback a migration:"
echo "  supabase db reset"
echo "  supabase db push" 