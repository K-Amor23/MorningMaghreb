const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env' });

// Database setup script for missing tables
const setupDatabase = async () => {
    // Check if Supabase is configured
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
        console.log('❌ Supabase not configured. Please check your .env file:');
        console.log('   NEXT_PUBLIC_SUPABASE_URL');
        console.log('   SUPABASE_SERVICE_ROLE_KEY');
        return false;
    }

    console.log('✅ Supabase configuration found');
    console.log(`URL: ${supabaseUrl}`);
    console.log(`Service Key: ${supabaseServiceKey.substring(0, 20)}...`);

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // SQL to create missing tables
    const createTablesSQL = `
    -- Create companies table if it doesn't exist
    CREATE TABLE IF NOT EXISTS companies (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      ticker VARCHAR(10) UNIQUE NOT NULL,
      name VARCHAR(255) NOT NULL,
      sector VARCHAR(100),
      market_cap DECIMAL(20,2),
      current_price DECIMAL(10,2),
      price_change DECIMAL(10,2),
      price_change_percent DECIMAL(5,2),
      pe_ratio DECIMAL(10,2),
      dividend_yield DECIMAL(5,2),
      roe DECIMAL(5,2),
      shares_outstanding BIGINT,
      size_category VARCHAR(20) CHECK (size_category IN ('large', 'medium', 'small')),
      is_active BOOLEAN DEFAULT TRUE,
      last_updated TIMESTAMPTZ DEFAULT NOW(),
      created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create company_prices table for OHLCV data
    CREATE TABLE IF NOT EXISTS company_prices (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
      ticker VARCHAR(10) NOT NULL,
      date DATE NOT NULL,
      open DECIMAL(10,2),
      high DECIMAL(10,2),
      low DECIMAL(10,2),
      close DECIMAL(10,2),
      volume BIGINT,
      adjusted_close DECIMAL(10,2),
      created_at TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(ticker, date)
    );

    -- Create company_reports table for financial reports
    CREATE TABLE IF NOT EXISTS company_reports (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
      ticker VARCHAR(10) NOT NULL,
      company_name VARCHAR(255) NOT NULL,
      title VARCHAR(500) NOT NULL,
      report_type VARCHAR(50) CHECK (report_type IN ('annual_report', 'quarterly_report', 'financial_statement', 'earnings', 'unknown')),
      report_date VARCHAR(50),
      report_year VARCHAR(4),
      report_quarter VARCHAR(10),
      url TEXT NOT NULL,
      filename VARCHAR(255),
      scraped_at TIMESTAMPTZ DEFAULT NOW(),
      created_at TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(ticker, url)
    );

    -- Create company_news table for news and sentiment
    CREATE TABLE IF NOT EXISTS company_news (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
      ticker VARCHAR(10) NOT NULL,
      headline TEXT NOT NULL,
      source VARCHAR(255),
      published_at TIMESTAMPTZ,
      sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
      sentiment_score DECIMAL(3,2),
      url TEXT,
      content_preview TEXT,
      scraped_at TIMESTAMPTZ DEFAULT NOW(),
      created_at TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(ticker, url, published_at)
    );

    -- Create sentiment_aggregates table
    CREATE TABLE IF NOT EXISTS sentiment_aggregates (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      ticker VARCHAR(10) UNIQUE NOT NULL,
      bullish_percentage DECIMAL(5,2) DEFAULT 0,
      bearish_percentage DECIMAL(5,2) DEFAULT 0,
      neutral_percentage DECIMAL(5,2) DEFAULT 0,
      total_votes INTEGER DEFAULT 0,
      average_confidence DECIMAL(3,2) DEFAULT 0,
      last_updated TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
    CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
    CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active) WHERE is_active = TRUE;

    CREATE INDEX IF NOT EXISTS idx_company_prices_ticker ON company_prices(ticker);
    CREATE INDEX IF NOT EXISTS idx_company_prices_date ON company_prices(date);
    CREATE INDEX IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date DESC);

    CREATE INDEX IF NOT EXISTS idx_company_reports_ticker ON company_reports(ticker);
    CREATE INDEX IF NOT EXISTS idx_company_reports_type ON company_reports(report_type);
    CREATE INDEX IF NOT EXISTS idx_company_reports_year ON company_reports(report_year);

    CREATE INDEX IF NOT EXISTS idx_company_news_ticker ON company_news(ticker);
    CREATE INDEX IF NOT EXISTS idx_company_news_published_at ON company_news(published_at);
    CREATE INDEX IF NOT EXISTS idx_company_news_sentiment ON company_news(sentiment);
    CREATE INDEX IF NOT EXISTS idx_company_news_ticker_published ON company_news(ticker, published_at DESC);

    CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);
  `;

    try {
        console.log('🔧 Setting up database tables...');

        // Execute the SQL to create tables
        const { error } = await supabase.rpc('exec_sql', { sql: createTablesSQL });

        if (error) {
            console.log('❌ Error creating tables:', error.message);
            console.log('\n📝 Alternative: You can run this SQL manually in your Supabase SQL editor:');
            console.log(createTablesSQL);
            return false;
        }

        console.log('✅ Database tables created successfully!');
        console.log('\n📋 Created tables:');
        console.log('   - companies');
        console.log('   - company_prices');
        console.log('   - company_reports');
        console.log('   - company_news');
        console.log('   - sentiment_aggregates');
        console.log('\n🔍 You can now access company pages with real data.');

        return true;
    } catch (error) {
        console.log('❌ Error:', error.message);
        console.log('\n📝 Please run this SQL manually in your Supabase SQL editor:');
        console.log(createTablesSQL);
        return false;
    }
};

// Run the setup
if (require.main === module) {
    setupDatabase().then(success => {
        if (success) {
            console.log('\n🎉 Database setup completed!');
        } else {
            console.log('\n💡 Please check your Supabase configuration and try again.');
        }
    });
}

module.exports = { setupDatabase }; 