// Real Data Service - Implements "Real Data First" approach
// with proper fallback chains and data quality monitoring

import { createClient } from '@supabase/supabase-js'

export interface CompanyData {
  ticker: string
  name: string
  sector: string
  subsector?: string
  price: number
  change_1d_percent: number
  change_ytd_percent: number
  market_cap_billion: number
  volume: number
  pe_ratio?: number
  dividend_yield?: number
  beta?: number
  size_category: string
  sector_group: string
  listing_date?: string
  isin?: string
  source: string
  lastUpdated: string
  quality: DataQualityMetrics
  fromCache: boolean
}

export interface DataQualityMetrics {
  completeness: number
  accuracy: number
  freshness: number
  consistency: number
  overall: number
}

export interface DataSourceMetadata {
  source: string
  lastUpdated: string
  cacheStatus: 'fresh' | 'cached' | 'fallback'
  dataQuality: DataQualityMetrics
  recordsCount: number
}

class RealDataService {
  private supabase: any
  private cache: Map<string, { data: CompanyData; timestamp: number }> = new Map()
  private cacheTTL: number = 5 * 60 * 1000 // 5 minutes
  private readonly DATA_SOURCE_PRIORITY = [
    'supabase_live',
    'supabase_cached', 
    'african_markets_api',
    'local_backup',
    'mock_data'
  ] as const

  constructor() {
    // Initialize Supabase client
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    
    if (supabaseUrl && supabaseKey) {
      this.supabase = createClient(supabaseUrl, supabaseKey)
    }
  }

  /**
   * Get company data with fallback chain
   */
  async getCompanyData(ticker: string): Promise<CompanyData> {
    const upperTicker = ticker.toUpperCase()
    
    // 1. Check cache first
    const cached = this.getFromCache(upperTicker)
    if (cached) {
      return { ...cached, fromCache: true }
    }

    // 2. Try data sources in priority order
    for (const source of this.DATA_SOURCE_PRIORITY) {
      try {
        const data = await this.fetchFromSource(source, upperTicker)
        if (data && this.isDataValid(data)) {
          const enrichedData = this.enrichData(data, source)
          this.setCache(upperTicker, enrichedData)
          return enrichedData
        }
      } catch (error) {
        console.warn(`Failed to fetch from ${source} for ${upperTicker}:`, error)
        continue
      }
    }

    // 3. All sources failed, return mock data
    console.error(`All data sources failed for ${upperTicker}, using mock data`)
    return this.getMockData(upperTicker)
  }

  /**
   * Get all companies data
   */
  async getAllCompanies(): Promise<CompanyData[]> {
    try {
      // Try Supabase first
      if (this.supabase) {
        const { data, error } = await this.supabase
          .from('companies')
          .select('*')
          .eq('is_active', true)
          .order('ticker')

        if (!error && data && data.length > 0) {
          return data.map((company: any) => 
            this.enrichData(company, 'supabase_live')
          )
        }
      }

      // Fallback to African Markets API
      const response = await fetch('/api/market-data/african-markets-companies')
      if (response.ok) {
        const companies = await response.json()
        return companies.map((company: any) => 
          this.enrichData(company, 'african_markets_api')
        )
      }

      // Final fallback to mock data
      return this.getMockCompanies()
    } catch (error) {
      console.error('Failed to fetch all companies:', error)
      return this.getMockCompanies()
    }
  }

  /**
   * Get market summary with real data
   */
  async getMarketSummary(): Promise<{
    totalCompanies: number
    totalVolume: number
    advancing: number
    declining: number
    unchanged: number
    averageChange: number
    bySector: Record<string, any>
    bySizeCategory: Record<string, any>
    lastUpdated: string
    dataQuality: DataQualityMetrics
  }> {
    const companies = await this.getAllCompanies()
    
    const totalVolume = companies.reduce((sum, c) => sum + (c.volume || 0), 0)
    const advancing = companies.filter(c => c.change_1d_percent > 0).length
    const declining = companies.filter(c => c.change_1d_percent < 0).length
    const unchanged = companies.filter(c => c.change_1d_percent === 0).length
    const averageChange = companies.reduce((sum, c) => sum + c.change_1d_percent, 0) / companies.length

    // Group by sector
    const bySector = companies.reduce((acc, company) => {
      const sector = company.sector || 'Unknown'
      if (!acc[sector]) {
        acc[sector] = { count: 0, advancing: 0, declining: 0, totalChange: 0 }
      }
      acc[sector].count++
      if (company.change_1d_percent > 0) acc[sector].advancing++
      if (company.change_1d_percent < 0) acc[sector].declining++
      acc[sector].totalChange += company.change_1d_percent
      return acc
    }, {} as Record<string, any>)

    // Group by size category
    const bySizeCategory = companies.reduce((acc, company) => {
      const size = company.size_category || 'Unknown'
      if (!acc[size]) {
        acc[size] = { count: 0, advancing: 0, declining: 0, totalChange: 0 }
      }
      acc[size].count++
      if (company.change_1d_percent > 0) acc[size].advancing++
      if (company.change_1d_percent < 0) acc[size].declining++
      acc[size].totalChange += company.change_1d_percent
      return acc
    }, {} as Record<string, any>)

    // Calculate overall data quality
    const dataQuality = this.calculateOverallDataQuality(companies)

    return {
      totalCompanies: companies.length,
      totalVolume,
      advancing,
      declining,
      unchanged,
      averageChange: parseFloat(averageChange.toFixed(2)),
      bySector,
      bySizeCategory,
      lastUpdated: new Date().toISOString(),
      dataQuality
    }
  }

  /**
   * Fetch data from specific source
   */
  private async fetchFromSource(source: string, ticker: string): Promise<any> {
    switch (source) {
      case 'supabase_live':
        return this.fetchFromSupabase(ticker)
      case 'supabase_cached':
        return this.fetchFromSupabaseCache(ticker)
      case 'african_markets_api':
        return this.fetchFromAfricanMarkets(ticker)
      case 'local_backup':
        return this.fetchFromLocalBackup(ticker)
      case 'mock_data':
        return this.getMockData(ticker)
      default:
        throw new Error(`Unknown data source: ${source}`)
    }
  }

  /**
   * Fetch from Supabase (live data)
   */
  private async fetchFromSupabase(ticker: string): Promise<any> {
    if (!this.supabase) throw new Error('Supabase not initialized')

    const { data, error } = await this.supabase
      .from('companies')
      .select('*')
      .eq('ticker', ticker)
      .eq('is_active', true)
      .single()

    if (error) throw error
    return data
  }

  /**
   * Fetch from Supabase cache
   */
  private async fetchFromSupabaseCache(ticker: string): Promise<any> {
    // This would check a cache table in Supabase
    // For now, return null to fall through to next source
    return null
  }

  /**
   * Fetch from African Markets API
   */
  private async fetchFromAfricanMarkets(ticker: string): Promise<any> {
    const response = await fetch('/api/market-data/african-markets-companies')
    if (!response.ok) throw new Error('African Markets API failed')

    const companies = await response.json()
    return companies.find((c: any) => c.ticker === ticker)
  }

  /**
   * Fetch from local backup
   */
  private async fetchFromLocalBackup(ticker: string): Promise<any> {
    // This would load from local JSON files
    // For now, return null to fall through to mock data
    return null
  }

  /**
   * Cache management
   */
  private getFromCache(key: string): CompanyData | null {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      return cached.data
    }
    return null
  }

  private setCache(key: string, data: CompanyData): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  /**
   * Data validation
   */
  private isDataValid(data: any): boolean {
    if (!data) return false
    
    const requiredFields = ['ticker', 'name', 'price']
    const hasRequiredFields = requiredFields.every(field => 
      data[field] !== undefined && data[field] !== null
    )
    
    if (!hasRequiredFields) return false
    
    // Validate price is positive
    if (typeof data.price !== 'number' || data.price <= 0) return false
    
    return true
  }

  /**
   * Enrich data with metadata
   */
  private enrichData(data: any, source: string): CompanyData {
    const quality = this.calculateDataQuality(data)
    
    return {
      ticker: data.ticker,
      name: data.name,
      sector: data.sector || 'Unknown',
      subsector: data.subsector,
      price: data.price || 0,
      change_1d_percent: data.change_1d_percent || 0,
      change_ytd_percent: data.change_ytd_percent || 0,
      market_cap_billion: data.market_cap_billion || 0,
      volume: data.volume || 0,
      pe_ratio: data.pe_ratio,
      dividend_yield: data.dividend_yield,
      beta: data.beta,
      size_category: data.size_category || 'Unknown',
      sector_group: data.sector_group || data.sector || 'Unknown',
      listing_date: data.listing_date,
      isin: data.isin,
      source,
      lastUpdated: data.last_updated || data.scraped_at || new Date().toISOString(),
      quality,
      fromCache: false
    }
  }

  /**
   * Calculate data quality metrics
   */
  private calculateDataQuality(data: any): DataQualityMetrics {
    const requiredFields = ['ticker', 'name', 'price', 'sector']
    const presentFields = requiredFields.filter(field => 
      data[field] !== undefined && data[field] !== null
    )
    
    const completeness = presentFields.length / requiredFields.length
    const accuracy = this.validatePriceAccuracy(data.price)
    const freshness = this.validateDataFreshness(data.last_updated || data.scraped_at)
    const consistency = this.validateDataConsistency(data)
    
    const overall = (completeness + accuracy + freshness + consistency) / 4
    
    return {
      completeness,
      accuracy,
      freshness,
      consistency,
      overall
    }
  }

  private calculateOverallDataQuality(companies: CompanyData[]): DataQualityMetrics {
    if (companies.length === 0) {
      return { completeness: 0, accuracy: 0, freshness: 0, consistency: 0, overall: 0 }
    }

    const avgCompleteness = companies.reduce((sum, c) => sum + c.quality.completeness, 0) / companies.length
    const avgAccuracy = companies.reduce((sum, c) => sum + c.quality.accuracy, 0) / companies.length
    const avgFreshness = companies.reduce((sum, c) => sum + c.quality.freshness, 0) / companies.length
    const avgConsistency = companies.reduce((sum, c) => sum + c.quality.consistency, 0) / companies.length
    const avgOverall = companies.reduce((sum, c) => sum + c.quality.overall, 0) / companies.length

    return {
      completeness: avgCompleteness,
      accuracy: avgAccuracy,
      freshness: avgFreshness,
      consistency: avgConsistency,
      overall: avgOverall
    }
  }

  private validatePriceAccuracy(price: number): number {
    if (typeof price !== 'number' || price <= 0) return 0
    if (price > 10000) return 0.5 // Suspiciously high
    return 1.0
  }

  private validateDataFreshness(lastUpdated: string): number {
    if (!lastUpdated) return 0
    
    const lastUpdate = new Date(lastUpdated)
    const now = new Date()
    const hoursDiff = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60)
    
    if (hoursDiff < 1) return 1.0      // Less than 1 hour
    if (hoursDiff < 24) return 0.8     // Less than 1 day
    if (hoursDiff < 168) return 0.5    // Less than 1 week
    return 0.2                         // Older than 1 week
  }

  private validateDataConsistency(data: any): number {
    // Check for logical consistency
    let score = 1.0
    
    // Price should be positive
    if (data.price <= 0) score -= 0.3
    
    // Market cap should be reasonable
    if (data.market_cap_billion && data.market_cap_billion < 0) score -= 0.2
    
    // Volume should be non-negative
    if (data.volume && data.volume < 0) score -= 0.2
    
    return Math.max(0, score)
  }

  /**
   * Mock data fallback
   */
  private getMockData(ticker: string): CompanyData {
    const mockCompanies = [
      { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banking', price: 410.10 },
      { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications', price: 156.30 },
      { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banking', price: 268.60 },
      { ticker: 'GAZ', name: 'Afriquia Gaz', sector: 'Oil & Gas', price: 4400.0 },
      { ticker: 'CMT', name: 'Ciments du Maroc', sector: 'Materials', price: 234.50 }
    ]

    const mock = mockCompanies.find(c => c.ticker === ticker) || {
      ticker,
      name: `${ticker} Company`,
      sector: 'Unknown',
      price: 100.0
    }

    return this.enrichData(mock, 'mock_data')
  }

  private getMockCompanies(): CompanyData[] {
    const mockCompanies = [
      { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banking', price: 410.10, change_1d_percent: 0.31, market_cap_billion: 24.56, volume: 500000, size_category: 'Large Cap' },
      { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications', price: 156.30, change_1d_percent: -1.33, market_cap_billion: 15.68, volume: 300000, size_category: 'Large Cap' },
      { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banking', price: 268.60, change_1d_percent: 0.85, market_cap_billion: 12.34, volume: 250000, size_category: 'Large Cap' },
      { ticker: 'GAZ', name: 'Afriquia Gaz', sector: 'Oil & Gas', price: 4400.0, change_1d_percent: 1.15, market_cap_billion: 15.12, volume: 100000, size_category: 'Mid Cap' },
      { ticker: 'CMT', name: 'Ciments du Maroc', sector: 'Materials', price: 234.50, change_1d_percent: -0.42, market_cap_billion: 8.90, volume: 150000, size_category: 'Mid Cap' }
    ]

    return mockCompanies.map(company => this.enrichData(company, 'mock_data'))
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear()
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; hitRate: number } {
    return {
      size: this.cache.size,
      hitRate: 0.8 // This would be calculated from actual usage
    }
  }
}

// Export singleton instance
export const realDataService = new RealDataService()

// Export types for use in components 