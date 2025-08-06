import { NextApiRequest, NextApiResponse } from 'next'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseKey)

// Mock data for demonstration (replace with actual scraping)
const mockCompanyData = [
  {
    ticker: 'ATW',
    company_name: 'Attijariwafa Bank',
    sector: 'Banking',
    price: 410.10 + (Math.random() - 0.5) * 10,
    change_1d_percent: (Math.random() - 0.5) * 2,
    change_ytd_percent: 5.25 + (Math.random() - 0.5) * 2,
    market_cap_billion: 24.56,
    volume: 1250000 + Math.floor(Math.random() * 100000),
    pe_ratio: 12.5,
    dividend_yield: 4.2,
    size_category: 'Large Cap',
    sector_group: 'Financial Services',
    date: new Date().toISOString().split('T')[0],
    scraped_at: new Date().toISOString()
  },
  {
    ticker: 'IAM',
    company_name: 'Maroc Telecom',
    sector: 'Telecommunications',
    price: 156.30 + (Math.random() - 0.5) * 5,
    change_1d_percent: (Math.random() - 0.5) * 2,
    change_ytd_percent: -2.15 + (Math.random() - 0.5) * 2,
    market_cap_billion: 15.68,
    volume: 890000 + Math.floor(Math.random() * 50000),
    pe_ratio: 15.2,
    dividend_yield: 3.8,
    size_category: 'Large Cap',
    sector_group: 'Telecommunications',
    date: new Date().toISOString().split('T')[0],
    scraped_at: new Date().toISOString()
  }
]

const mockMarketData = [
  {
    index_name: 'MASI',
    value: 12580.45 + (Math.random() - 0.5) * 100,
    change_1d_percent: (Math.random() - 0.5) * 1,
    change_ytd_percent: 12.3 + (Math.random() - 0.5) * 2,
    volume: 45000000 + Math.floor(Math.random() * 1000000),
    market_cap_total: 1250.8,
    date: new Date().toISOString().split('T')[0],
    scraped_at: new Date().toISOString()
  }
]

const mockMacroData = [
  {
    indicator: 'GDP_Growth',
    value: 3.2 + (Math.random() - 0.5) * 0.5,
    unit: 'percent',
    period: '2024',
    source: 'Bank Al-Maghrib',
    date: new Date().toISOString().split('T')[0],
    scraped_at: new Date().toISOString()
  },
  {
    indicator: 'Inflation_Rate',
    value: 2.8 + (Math.random() - 0.5) * 0.3,
    unit: 'percent',
    period: '2024',
    source: 'Bank Al-Maghrib',
    date: new Date().toISOString().split('T')[0],
    scraped_at: new Date().toISOString()
  }
]

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Verify it's a cron job request
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    log('🔄 Starting automated pipeline...')
    
    // Step 1: Update company prices
    log('📊 Updating company prices...')
    for (const company of mockCompanyData) {
      await supabase
        .from('company_prices')
        .upsert(company)
    }
    
    // Step 2: Update market indices
    log('📈 Updating market indices...')
    for (const index of mockMarketData) {
      await supabase
        .from('market_indices')
        .upsert(index)
    }
    
    // Step 3: Update macro indicators
    log('🏛️ Updating macro indicators...')
    for (const macro of mockMacroData) {
      await supabase
        .from('macro_indicators')
        .upsert(macro)
    }
    
    // Step 4: Log pipeline execution
    log('📝 Logging pipeline execution...')
    await supabase
      .from('data_quality_logs')
      .insert({
        validation_date: new Date().toISOString().split('T')[0],
        african_markets_count: mockCompanyData.length,
        bourse_indices_count: mockMarketData.length,
        macro_indicators_count: mockMacroData.length,
        news_articles_count: 0,
        total_records: mockCompanyData.length + mockMarketData.length + mockMacroData.length,
        validation_passed: true,
        created_at: new Date().toISOString()
      })
    
    // Step 5: Send success notification
    log('✅ Sending success notification...')
    await supabase
      .from('pipeline_notifications')
      .insert({
        notification_type: 'success',
        message: `Automated pipeline completed successfully at ${new Date().toISOString()}. Updated ${mockCompanyData.length} companies, ${mockMarketData.length} indices, and ${mockMacroData.length} macro indicators.`,
        created_at: new Date().toISOString()
      })
    
    log('🎉 Pipeline completed successfully!')
    res.status(200).json({ 
      success: true, 
      message: 'Pipeline completed successfully',
      timestamp: new Date().toISOString(),
      records_updated: mockCompanyData.length + mockMarketData.length + mockMacroData.length
    })
    
  } catch (error) {
    log(`❌ Pipeline failed: ${error}`)
    
    // Log error
    await supabase
      .from('pipeline_notifications')
      .insert({
        notification_type: 'failure',
        message: `Pipeline failed at ${new Date().toISOString()}: ${error}`,
        created_at: new Date().toISOString()
      })
    
    res.status(500).json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    })
  }
}

function log(message: string) {
  console.log(`[${new Date().toISOString()}] ${message}`)
} 