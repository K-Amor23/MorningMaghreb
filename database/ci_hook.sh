#!/bin/bash
# CI Hook for Migration Validation
# This script validates that migrations are properly formatted

set -e

echo "🔍 Validating database migrations..."

MIGRATIONS_DIR="database/migrations"
UP_DIR="$MIGRATIONS_DIR/up"
DOWN_DIR="$MIGRATIONS_DIR/down"

# Check if directories exist
if [ ! -d "$UP_DIR" ] || [ ! -d "$DOWN_DIR" ]; then
    echo "❌ Migration directories not found"
    exit 1
fi

# Check for matching up/down migrations
for up_file in $UP_DIR/*.sql; do
    if [ -f "$up_file" ]; then
        filename=$(basename "$up_file")
        down_file="$DOWN_DIR/$filename"
        
        if [ ! -f "$down_file" ]; then
            echo "❌ Missing down migration for $filename"
            exit 1
        fi
    fi
done

echo "✅ All migrations validated successfully"
