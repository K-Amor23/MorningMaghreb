#!/usr/bin/env python3
"""
Supabase Migration Setup Script
Sets up migration system and creates initial schema migrations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

class SupabaseMigrationManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.migrations_dir = self.root_dir / "database" / "migrations"
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.migrations_dir / "up").mkdir(exist_ok=True)
        (self.migrations_dir / "down").mkdir(exist_ok=True)
        (self.migrations_dir / "checks").mkdir(exist_ok=True)
    
    def create_migration_structure(self):
        """Create the migration directory structure"""
        print("🏗️  Setting up Supabase migration structure...")
        
        # Create migration files
        self._create_initial_migration()
        self._create_schema_migration()
        self._create_data_migration()
        self._create_indexes_migration()
        
        # Create migration utilities
        self._create_migration_utils()
        self._create_migration_config()
        
        print("✅ Migration structure created successfully")
    
    def _create_initial_migration(self):
        """Create initial database setup migration"""
        migration_content = f'''-- Migration: 001_initial_setup
-- Description: Initial database setup for Casablanca Insights
-- Created: {datetime.now().isoformat()}

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_tier AS ENUM ('free', 'pro', 'admin');
CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due', 'trialing');
CREATE TYPE notification_type AS ENUM ('price_alert', 'news_alert', 'system_notification');

-- Create base tables
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    tier user_tier DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'active',
    subscription_id TEXT,
    stripe_customer_id TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sector TEXT,
    market_cap NUMERIC,
    current_price NUMERIC,
    price_change_percent NUMERIC,
    volume BIGINT,
    pe_ratio NUMERIC,
    dividend_yield NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL REFERENCES companies(ticker),
    price NUMERIC NOT NULL,
    change_percent NUMERIC,
    volume BIGINT,
    high NUMERIC,
    low NUMERIC,
    open_price NUMERIC,
    close_price NUMERIC,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date ON market_data(ticker, date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
'''
        
        migration_file = self.migrations_dir / "up" / "001_initial_setup.sql"
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        # Create down migration
        down_migration = '''-- Down Migration: 001_initial_setup
-- Description: Rollback initial database setup

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
DROP FUNCTION IF EXISTS update_updated_at_column();

DROP TABLE IF EXISTS market_data;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS profiles;

DROP TYPE IF EXISTS notification_type;
DROP TYPE IF EXISTS subscription_status;
DROP TYPE IF EXISTS user_tier;
'''
        
        down_file = self.migrations_dir / "down" / "001_initial_setup.sql"
        with open(down_file, 'w') as f:
            f.write(down_migration)
    
    def _create_schema_migration(self):
        """Create schema expansion migration"""
        migration_content = f'''-- Migration: 002_schema_expansion
-- Description: Add additional tables for advanced features
-- Created: {datetime.now().isoformat()}

-- Financial reports table
CREATE TABLE IF NOT EXISTS financial_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    report_type TEXT NOT NULL,
    period TEXT NOT NULL,
    revenue NUMERIC,
    net_income NUMERIC,
    assets NUMERIC,
    liabilities NUMERIC,
    report_date DATE NOT NULL,
    file_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- News and sentiment table
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT,
    source TEXT,
    url TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    sentiment_score NUMERIC,
    sentiment_label TEXT,
    tickers TEXT[], -- Array of related tickers
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id),
    name TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id),
    ticker TEXT NOT NULL,
    shares NUMERIC NOT NULL,
    average_price NUMERIC NOT NULL,
    purchase_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id),
    ticker TEXT,
    alert_type TEXT NOT NULL,
    condition TEXT NOT NULL,
    threshold NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_financial_reports_company_date ON financial_reports(company_id, report_date);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment ON news_articles(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio ON portfolio_holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON alerts(user_id, is_active);

-- Apply triggers
CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_holdings_updated_at BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
'''
        
        migration_file = self.migrations_dir / "up" / "002_schema_expansion.sql"
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        # Create down migration
        down_migration = '''-- Down Migration: 002_schema_expansion
-- Description: Rollback schema expansion

DROP TRIGGER IF EXISTS update_portfolio_holdings_updated_at ON portfolio_holdings;
DROP TRIGGER IF EXISTS update_portfolios_updated_at ON portfolios;

DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS portfolio_holdings;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS news_articles;
DROP TABLE IF EXISTS financial_reports;
'''
        
        down_file = self.migrations_dir / "down" / "002_schema_expansion.sql"
        with open(down_file, 'w') as f:
            f.write(down_migration)
    
    def _create_data_migration(self):
        """Create data migration for initial data"""
        migration_content = f'''-- Migration: 003_initial_data
-- Description: Insert initial data for development
-- Created: {datetime.now().isoformat()}

-- Insert sample companies
INSERT INTO companies (ticker, name, sector, market_cap, current_price, price_change_percent) VALUES
('ATW', 'Attijariwafa Bank', 'Banking', 45000000000, 45.50, 2.1),
('BMCE', 'BMCE Bank of Africa', 'Banking', 28000000000, 32.80, -1.2),
('IAM', 'Maroc Telecom', 'Telecommunications', 65000000000, 78.90, 0.8),
('CIH', 'CIH Bank', 'Banking', 15000000000, 18.20, 1.5),
('CMT', 'Compagnie Minière de Touissit', 'Mining', 8500000000, 12.40, -0.5)
ON CONFLICT (ticker) DO NOTHING;

-- Insert sample market data
INSERT INTO market_data (ticker, price, change_percent, volume, high, low, open_price, close_price, date) VALUES
('ATW', 45.50, 2.1, 1250000, 46.20, 44.80, 44.90, 45.50, CURRENT_DATE),
('BMCE', 32.80, -1.2, 890000, 33.50, 32.40, 33.20, 32.80, CURRENT_DATE),
('IAM', 78.90, 0.8, 2100000, 79.50, 78.20, 78.30, 78.90, CURRENT_DATE),
('CIH', 18.20, 1.5, 450000, 18.50, 17.90, 17.95, 18.20, CURRENT_DATE),
('CMT', 12.40, -0.5, 320000, 12.60, 12.20, 12.45, 12.40, CURRENT_DATE)
ON CONFLICT DO NOTHING;
'''
        
        migration_file = self.migrations_dir / "up" / "003_initial_data.sql"
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        # Create down migration
        down_migration = '''-- Down Migration: 003_initial_data
-- Description: Remove initial data

DELETE FROM market_data WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
DELETE FROM companies WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
'''
        
        down_file = self.migrations_dir / "down" / "003_initial_data.sql"
        with open(down_file, 'w') as f:
            f.write(down_migration)
    
    def _create_indexes_migration(self):
        """Create indexes migration for performance"""
        migration_content = f'''-- Migration: 004_performance_indexes
-- Description: Add performance indexes for better query performance
-- Created: {datetime.now().isoformat()}

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date_price ON market_data(ticker, date, price);
CREATE INDEX IF NOT EXISTS idx_companies_sector_market_cap ON companies(sector, market_cap);
CREATE INDEX IF NOT EXISTS idx_financial_reports_type_period ON financial_reports(report_type, period);
CREATE INDEX IF NOT EXISTS idx_news_articles_tickers ON news_articles USING GIN(tickers);

-- Partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_alerts_active_ticker ON alerts(ticker) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_portfolios_public ON portfolios(id) WHERE is_public = TRUE;

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_title_search ON news_articles USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_companies_name_search ON companies USING GIN(to_tsvector('english', name));

-- Statistics for query planner
ANALYZE companies;
ANALYZE market_data;
ANALYZE financial_reports;
ANALYZE news_articles;
'''
        
        migration_file = self.migrations_dir / "up" / "004_performance_indexes.sql"
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        # Create down migration
        down_migration = '''-- Down Migration: 004_performance_indexes
-- Description: Remove performance indexes

DROP INDEX IF EXISTS idx_news_articles_title_search;
DROP INDEX IF EXISTS idx_companies_name_search;
DROP INDEX IF EXISTS idx_portfolios_public;
DROP INDEX IF EXISTS idx_alerts_active_ticker;
DROP INDEX IF EXISTS idx_news_articles_tickers;
DROP INDEX IF EXISTS idx_financial_reports_type_period;
DROP INDEX IF EXISTS idx_companies_sector_market_cap;
DROP INDEX IF EXISTS idx_market_data_ticker_date_price;
'''
        
        down_file = self.migrations_dir / "down" / "004_performance_indexes.sql"
        with open(down_file, 'w') as f:
            f.write(down_migration)
    
    def _create_migration_utils(self):
        """Create migration utility functions"""
        utils_content = '''-- Migration Utilities
-- Helper functions for migration management

-- Function to check if migration has been applied
CREATE OR REPLACE FUNCTION migration_applied(migration_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'migration_log'
    ) AND EXISTS (
        SELECT 1 FROM migration_log 
        WHERE migration_name = migration_applied.migration_name
    );
END;
$$ LANGUAGE plpgsql;

-- Function to log migration
CREATE OR REPLACE FUNCTION log_migration(migration_name TEXT, direction TEXT)
RETURNS VOID AS $$
BEGIN
    -- Create migration_log table if it doesn't exist
    CREATE TABLE IF NOT EXISTS migration_log (
        id SERIAL PRIMARY KEY,
        migration_name TEXT NOT NULL,
        direction TEXT NOT NULL,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    INSERT INTO migration_log (migration_name, direction)
    VALUES (migration_name, direction);
END;
$$ LANGUAGE plpgsql;

-- Function to get migration status
CREATE OR REPLACE FUNCTION get_migration_status()
RETURNS TABLE (
    migration_name TEXT,
    applied_at TIMESTAMP WITH TIME ZONE,
    direction TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT ml.migration_name, ml.applied_at, ml.direction
    FROM migration_log ml
    ORDER BY ml.applied_at DESC;
END;
$$ LANGUAGE plpgsql;
'''
        
        utils_file = self.migrations_dir / "migration_utils.sql"
        with open(utils_file, 'w') as f:
            f.write(utils_content)
    
    def _create_migration_config(self):
        """Create migration configuration"""
        config = {
            "migrations_dir": str(self.migrations_dir),
            "supabase_url": os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
            "supabase_key": os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
            "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            "migrations": [
                {
                    "name": "001_initial_setup",
                    "description": "Initial database setup",
                    "file": "001_initial_setup.sql",
                    "dependencies": []
                },
                {
                    "name": "002_schema_expansion",
                    "description": "Add additional tables for advanced features",
                    "file": "002_schema_expansion.sql",
                    "dependencies": ["001_initial_setup"]
                },
                {
                    "name": "003_initial_data",
                    "description": "Insert initial development data",
                    "file": "003_initial_data.sql",
                    "dependencies": ["001_initial_setup", "002_schema_expansion"]
                },
                {
                    "name": "004_performance_indexes",
                    "description": "Add performance indexes",
                    "file": "004_performance_indexes.sql",
                    "dependencies": ["001_initial_setup", "002_schema_expansion"]
                }
            ]
        }
        
        config_file = self.migrations_dir / "migration_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_migration_script(self):
        """Create migration runner script"""
        script_content = '''#!/usr/bin/env python3
"""
Supabase Migration Runner
Applies migrations to Supabase database
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json
import argparse

class MigrationRunner:
    def __init__(self, config_file: str = "migration_config.json"):
        self.migrations_dir = Path(__file__).parent
        self.config_file = self.migrations_dir / config_file
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def run_migration(self, migration_name: str, direction: str = "up"):
        """Run a specific migration"""
        print(f"🔄 Running migration: {migration_name} ({direction})")
        
        migration_file = self.migrations_dir / direction / f"{migration_name}.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        try:
            # Read migration SQL
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Apply migration using Supabase CLI
            result = subprocess.run([
                "supabase", "db", "push",
                "--db-url", self.config["supabase_url"],
                "--password", self.config["supabase_key"]
            ], input=sql.encode(), capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Migration {migration_name} applied successfully")
                return True
            else:
                print(f"❌ Migration {migration_name} failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running migration {migration_name}: {e}")
            return False
    
    def run_all_migrations(self, direction: str = "up"):
        """Run all migrations in order"""
        print(f"🚀 Running all migrations ({direction})")
        
        migrations = self.config["migrations"]
        if direction == "down":
            migrations = list(reversed(migrations))
        
        for migration in migrations:
            success = self.run_migration(migration["name"], direction)
            if not success:
                print(f"❌ Stopping migration process due to failure")
                return False
        
        print("✅ All migrations completed successfully")
        return True
    
    def check_migration_status(self):
        """Check which migrations have been applied"""
        print("📋 Checking migration status...")
        
        try:
            result = subprocess.run([
                "supabase", "db", "diff",
                "--schema", "public"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Database schema is up to date")
                return True
            else:
                print("⚠️  Database schema has pending changes")
                return False
                
        except Exception as e:
            print(f"❌ Error checking migration status: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Supabase Migration Runner")
    parser.add_argument("action", choices=["up", "down", "status"], help="Migration action")
    parser.add_argument("--migration", help="Specific migration to run")
    
    args = parser.parse_args()
    
    runner = MigrationRunner()
    
    if args.action == "status":
        runner.check_migration_status()
    elif args.migration:
        runner.run_migration(args.migration, args.action)
    else:
        runner.run_all_migrations(args.action)

if __name__ == "__main__":
    main()
'''
        
        script_file = self.migrations_dir / "run_migrations.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
    
    def create_ci_hook(self):
        """Create CI/CD hook for migration validation"""
        ci_hook = '''#!/bin/bash
# CI/CD Migration Hook
# Validates migrations on pull requests

set -e

echo "🔍 Checking database migrations..."

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Please install it first."
    exit 1
fi

# Generate migration diff
echo "📊 Generating migration diff..."
supabase db diff --schema public > migration_diff.sql

# Check if there are pending changes
if [ -s migration_diff.sql ]; then
    echo "⚠️  Pending database changes detected:"
    cat migration_diff.sql
    echo ""
    echo "💡 Please create a migration file for these changes."
    exit 1
else
    echo "✅ No pending database changes"
fi

# Clean up
rm -f migration_diff.sql

echo "✅ Migration validation passed"
'''
        
        hook_file = self.migrations_dir / "ci_hook.sh"
        with open(hook_file, 'w') as f:
            f.write(ci_hook)
        
        # Make hook executable
        os.chmod(hook_file, 0o755)
    
    def create_readme(self):
        """Create migration README"""
        readme_content = '''# Database Migrations

This directory contains database migrations for the Casablanca Insights project.

## Structure

```
migrations/
├── up/                    # Migration files to apply
├── down/                  # Rollback migration files
├── checks/                # Migration validation checks
├── migration_config.json  # Migration configuration
├── migration_utils.sql    # Migration utility functions
├── run_migrations.py      # Migration runner script
└── ci_hook.sh            # CI/CD validation hook
```

## Usage

### Running Migrations

```bash
# Run all migrations
python run_migrations.py up

# Run specific migration
python run_migrations.py up --migration 001_initial_setup

# Rollback all migrations
python run_migrations.py down

# Check migration status
python run_migrations.py status
```

### CI/CD Integration

The `ci_hook.sh` script validates migrations on pull requests:

```bash
./ci_hook.sh
```

## Migration Files

1. **001_initial_setup.sql** - Initial database setup
2. **002_schema_expansion.sql** - Additional tables for advanced features
3. **003_initial_data.sql** - Initial development data
4. **004_performance_indexes.sql** - Performance optimization indexes

## Best Practices

1. **Always test migrations** in development before applying to production
2. **Use descriptive names** for migration files
3. **Include rollback scripts** in the down/ directory
4. **Validate migrations** using the CI hook
5. **Document schema changes** in migration comments

## Troubleshooting

### Common Issues

1. **Migration conflicts**: Ensure migrations are applied in order
2. **Permission errors**: Check Supabase credentials
3. **Schema drift**: Use `supabase db diff` to identify differences

### Rollback

To rollback a migration:

```bash
python run_migrations.py down --migration 004_performance_indexes
```

## Monitoring

Monitor migration status:

```sql
SELECT * FROM get_migration_status();
```

Check for pending changes:

```bash
supabase db diff --schema public
```
'''
        
        readme_file = self.migrations_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)

def main():
    """Main migration setup execution"""
    print("🚀 Setting up Supabase Migration System")
    print("=" * 50)
    
    manager = SupabaseMigrationManager()
    
    # Create migration structure
    manager.create_migration_structure()
    
    # Create migration runner
    manager.create_migration_script()
    
    # Create CI hook
    manager.create_ci_hook()
    
    # Create documentation
    manager.create_readme()
    
    print("✅ Migration system setup complete!")
    print(f"📁 Migrations directory: {manager.migrations_dir}")
    print("📖 See README.md for usage instructions")

if __name__ == "__main__":
    main() 