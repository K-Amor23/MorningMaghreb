#!/usr/bin/env python3
"""
Final Supabase Migration Setup
Creates basic migration structure without any formatting issues
"""

import os
from pathlib import Path
from datetime import datetime


class FinalMigrationManager:
    def __init__(self):
        self.migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.migrations_dir / "up").mkdir(exist_ok=True)
        (self.migrations_dir / "down").mkdir(exist_ok=True)
        (self.migrations_dir / "checks").mkdir(exist_ok=True)

    def create_migration_structure(self):
        """Create basic migration structure"""
        print("🚀 Setting up Supabase Migration System")
        print("=" * 50)

        self._create_initial_migration()
        self._create_schema_migration()
        self._create_data_migration()
        self._create_indexes_migration()
        self._create_migration_script()
        self._create_ci_hook()
        self._create_readme()

        print("✅ Migration system setup complete!")

    def _create_initial_migration(self):
        """Create initial database setup migration"""
        timestamp = datetime.now().isoformat()

        migration_content = (
            """-- Migration: 001_initial_setup
-- Description: Initial database setup for Casablanca Insights
-- Created: """
            + timestamp
            + """

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
"""
        )

        migration_file = self.migrations_dir / "up" / "001_initial_setup.sql"
        with open(migration_file, "w") as f:
            f.write(migration_content)

        # Create down migration
        down_migration = """-- Down Migration: 001_initial_setup
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
"""

        down_file = self.migrations_dir / "down" / "001_initial_setup.sql"
        with open(down_file, "w") as f:
            f.write(down_migration)

        print("✅ Created initial migration (001_initial_setup.sql)")

    def _create_schema_migration(self):
        """Create schema expansion migration"""
        timestamp = datetime.now().isoformat()

        migration_content = (
            """-- Migration: 002_schema_expansion
-- Description: Add additional tables for advanced features
-- Created: """
            + timestamp
            + """

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
    tickers TEXT[],
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
"""
        )

        migration_file = self.migrations_dir / "up" / "002_schema_expansion.sql"
        with open(migration_file, "w") as f:
            f.write(migration_content)

        # Create down migration
        down_migration = """-- Down Migration: 002_schema_expansion
-- Description: Rollback schema expansion

DROP TRIGGER IF EXISTS update_portfolio_holdings_updated_at ON portfolio_holdings;
DROP TRIGGER IF EXISTS update_portfolios_updated_at ON portfolios;

DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS portfolio_holdings;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS news_articles;
DROP TABLE IF EXISTS financial_reports;
"""

        down_file = self.migrations_dir / "down" / "002_schema_expansion.sql"
        with open(down_file, "w") as f:
            f.write(down_migration)

        print("✅ Created schema migration (002_schema_expansion.sql)")

    def _create_data_migration(self):
        """Create data migration for initial data"""
        timestamp = datetime.now().isoformat()

        migration_content = (
            """-- Migration: 003_initial_data
-- Description: Insert initial data for development
-- Created: """
            + timestamp
            + """

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
"""
        )

        migration_file = self.migrations_dir / "up" / "003_initial_data.sql"
        with open(migration_file, "w") as f:
            f.write(migration_content)

        # Create down migration
        down_migration = """-- Down Migration: 003_initial_data
-- Description: Remove initial data

DELETE FROM market_data WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
DELETE FROM companies WHERE ticker IN ('ATW', 'BMCE', 'IAM', 'CIH', 'CMT');
"""

        down_file = self.migrations_dir / "down" / "003_initial_data.sql"
        with open(down_file, "w") as f:
            f.write(down_migration)

        print("✅ Created data migration (003_initial_data.sql)")

    def _create_indexes_migration(self):
        """Create indexes migration for performance"""
        timestamp = datetime.now().isoformat()

        migration_content = (
            """-- Migration: 004_performance_indexes
-- Description: Add performance indexes for better query performance
-- Created: """
            + timestamp
            + """

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
"""
        )

        migration_file = self.migrations_dir / "up" / "004_performance_indexes.sql"
        with open(migration_file, "w") as f:
            f.write(migration_content)

        # Create down migration
        down_migration = """-- Down Migration: 004_performance_indexes
-- Description: Remove performance indexes

DROP INDEX IF EXISTS idx_news_articles_title_search;
DROP INDEX IF EXISTS idx_companies_name_search;
DROP INDEX IF EXISTS idx_portfolios_public;
DROP INDEX IF EXISTS idx_alerts_active_ticker;
DROP INDEX IF EXISTS idx_news_articles_tickers;
DROP INDEX IF EXISTS idx_financial_reports_type_period;
DROP INDEX IF EXISTS idx_companies_sector_market_cap;
DROP INDEX IF EXISTS idx_market_data_ticker_date_price;
"""

        down_file = self.migrations_dir / "down" / "004_performance_indexes.sql"
        with open(down_file, "w") as f:
            f.write(down_migration)

        print("✅ Created indexes migration (004_performance_indexes.sql)")

    def _create_migration_script(self):
        """Create migration runner script"""
        script_content = """#!/usr/bin/env python3
\"\"\"
Migration Runner Script
Applies or rolls back database migrations
\"\"\"

import os
import sys
from pathlib import Path

def run_migration(direction, migration_name=None):
    \"\"\"Run a migration in the specified direction\"\"\"
    migrations_dir = Path(__file__).parent / "database" / "migrations"
    
    if direction == "up":
        # Apply all migrations
        up_dir = migrations_dir / "up"
        for migration_file in sorted(up_dir.glob("*.sql")):
            print(f"Applying {migration_file.name}...")
            # Here you would run the SQL against your database
            # For now, just print the file content
            with open(migration_file, 'r') as f:
                print(f.read())
    
    elif direction == "down":
        # Rollback migrations
        down_dir = migrations_dir / "down"
        if migration_name:
            down_file = down_dir / f"{migration_name}.sql"
            if down_file.exists():
                print(f"Rolling back {migration_name}...")
                with open(down_file, 'r') as f:
                    print(f.read())
        else:
            # Rollback all migrations in reverse order
            for migration_file in sorted(down_dir.glob("*.sql"), reverse=True):
                print(f"Rolling back {migration_file.name}...")
                with open(migration_file, 'r') as f:
                    print(f.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py [up|down] [migration_name]")
        sys.exit(1)
    
    direction = sys.argv[1]
    migration_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_migration(direction, migration_name)
"""

        script_file = self.migrations_dir.parent / "run_migrations.py"
        with open(script_file, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_file, 0o755)
        print("✅ Created migration runner script (run_migrations.py)")

    def _create_ci_hook(self):
        """Create CI hook for migration validation"""
        hook_content = """#!/bin/bash
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
"""

        hook_file = self.migrations_dir.parent / "ci_hook.sh"
        with open(hook_file, "w") as f:
            f.write(hook_content)

        # Make executable
        os.chmod(hook_file, 0o755)
        print("✅ Created CI hook (ci_hook.sh)")

    def _create_readme(self):
        """Create migration README"""
        readme_content = """# Database Migrations

This directory contains database migrations for the Casablanca Insights project.

## Structure

- `up/` - Migration files to apply
- `down/` - Rollback files for each migration
- `checks/` - Validation scripts

## Migrations

1. **001_initial_setup.sql** - Initial database setup with core tables
2. **002_schema_expansion.sql** - Additional tables for advanced features
3. **003_initial_data.sql** - Sample data for development
4. **004_performance_indexes.sql** - Performance optimization indexes

## Usage

### Apply all migrations
```bash
python run_migrations.py up
```

### Rollback specific migration
```bash
python run_migrations.py down 002_schema_expansion
```

### Validate migrations (CI)
```bash
./ci_hook.sh
```

## Development

When creating new migrations:
1. Create both up and down files
2. Test the rollback works correctly
3. Update this README with migration details
"""

        readme_file = self.migrations_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

        print("✅ Created migration README")


def main():
    manager = FinalMigrationManager()
    manager.create_migration_structure()


if __name__ == "__main__":
    main()
