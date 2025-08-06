#!/bin/bash
# Sync Environment Variables to GitHub Secrets
# This script creates GitHub Actions secrets from .env.local

set -e

echo "🔐 Syncing Environment Variables to GitHub Secrets"
echo "=================================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub. Please run 'gh auth login' first."
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local not found. Please create it first."
    exit 1
fi

echo "📋 Reading environment variables from .env.local..."
echo ""

# Counter for tracking
count=0
skipped=0

# Loop through each line in .env.local
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
    
    echo "🔑 Setting secret: $name"
    
    # Create/update the secret
    if gh secret set "$name" --body "$value" &> /dev/null; then
        echo "  ✅ Success"
        ((count++))
    else
        echo "  ❌ Failed"
        ((skipped++))
    fi
done < .env.local

echo ""
echo "📊 Summary:"
echo "  ✅ Successfully set: $count secrets"
echo "  ❌ Failed: $skipped secrets"
echo ""
echo "🔗 View secrets in GitHub:"
echo "  https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/settings/secrets/actions"
echo ""
echo "💡 To verify secrets are available in CI:"
echo "  - Create a test PR"
echo "  - Check the GitHub Actions logs"
echo "  - Look for 'Using secret' messages" 