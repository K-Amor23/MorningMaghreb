// Comprehensive Market Data System for Casablanca Stock Exchange
// Includes all 78 companies + bonds + other instruments

export interface ComprehensiveQuote {
  ticker: string
  name: string
  instrumentType: 'stock' | 'bond' | 'etf' | 'warrant' | 'preferred'
  sector: string
  currentPrice: number
  previousClose: number
  change: number
  changePercent: number
  volume: number
  high: number
  low: number
  open: number
  marketCap: number
  sizeCategory: 'Large Cap' | 'Mid Cap' | 'Small Cap' | 'Micro Cap'
  sectorGroup: string
  lastUpdated: string
  delayMinutes: number
  // Bond-specific fields
  couponRate?: number
  maturityDate?: string
  yield?: number
  faceValue?: number
  // Additional fields
  peRatio?: number
  dividendYield?: number
  beta?: number
}

export interface MarketDataConfig {
  delayMinutes: number
  updateInterval: number
  enableRealisticVolatility: boolean
  includeBonds: boolean
  includeETFs: boolean
}

// Moroccan Government Bonds (Treasury Bills and Bonds)
const moroccanBonds = [
  {
    ticker: 'MAD-3M',
    name: 'Moroccan Treasury Bill 3M',
    instrumentType: 'bond' as const,
    sector: 'Government',
    currentPrice: 98.50,
    previousClose: 98.45,
    change: 0.05,
    changePercent: 0.05,
    volume: 5000000,
    high: 98.55,
    low: 98.40,
    open: 98.45,
    marketCap: 1000000000,
    sizeCategory: 'Large Cap' as const,
    sectorGroup: 'Government Securities',
    couponRate: 3.25,
    maturityDate: '2025-10-15',
    yield: 3.45,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'MAD-6M',
    name: 'Moroccan Treasury Bill 6M',
    instrumentType: 'bond' as const,
    sector: 'Government',
    currentPrice: 97.20,
    previousClose: 97.15,
    change: 0.05,
    changePercent: 0.05,
    volume: 3000000,
    high: 97.25,
    low: 97.10,
    open: 97.15,
    marketCap: 800000000,
    sizeCategory: 'Large Cap' as const,
    sectorGroup: 'Government Securities',
    couponRate: 3.75,
    maturityDate: '2026-01-15',
    yield: 3.95,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'MAD-1Y',
    name: 'Moroccan Treasury Bond 1Y',
    instrumentType: 'bond' as const,
    sector: 'Government',
    currentPrice: 94.80,
    previousClose: 94.75,
    change: 0.05,
    changePercent: 0.05,
    volume: 2000000,
    high: 94.85,
    low: 94.70,
    open: 94.75,
    marketCap: 600000000,
    sizeCategory: 'Large Cap' as const,
    sectorGroup: 'Government Securities',
    couponRate: 4.25,
    maturityDate: '2026-07-15',
    yield: 4.55,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'MAD-5Y',
    name: 'Moroccan Treasury Bond 5Y',
    instrumentType: 'bond' as const,
    sector: 'Government',
    currentPrice: 88.50,
    previousClose: 88.45,
    change: 0.05,
    changePercent: 0.06,
    volume: 1500000,
    high: 88.55,
    low: 88.40,
    open: 88.45,
    marketCap: 400000000,
    sizeCategory: 'Large Cap' as const,
    sectorGroup: 'Government Securities',
    couponRate: 5.25,
    maturityDate: '2030-07-15',
    yield: 6.15,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'MAD-10Y',
    name: 'Moroccan Treasury Bond 10Y',
    instrumentType: 'bond' as const,
    sector: 'Government',
    currentPrice: 82.30,
    previousClose: 82.25,
    change: 0.05,
    changePercent: 0.06,
    volume: 1000000,
    high: 82.35,
    low: 82.20,
    open: 82.25,
    marketCap: 300000000,
    sizeCategory: 'Large Cap' as const,
    sectorGroup: 'Government Securities',
    couponRate: 6.00,
    maturityDate: '2035-07-15',
    yield: 7.45,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  }
]

// Corporate Bonds (Major Moroccan Companies)
const corporateBonds = [
  {
    ticker: 'ATW-BOND',
    name: 'Attijariwafa Bank Corporate Bond',
    instrumentType: 'bond' as const,
    sector: 'Banking',
    currentPrice: 95.20,
    previousClose: 95.15,
    change: 0.05,
    changePercent: 0.05,
    volume: 500000,
    high: 95.25,
    low: 95.10,
    open: 95.15,
    marketCap: 200000000,
    sizeCategory: 'Mid Cap' as const,
    sectorGroup: 'Financial Services',
    couponRate: 5.50,
    maturityDate: '2028-06-15',
    yield: 6.25,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'IAM-BOND',
    name: 'Maroc Telecom Corporate Bond',
    instrumentType: 'bond' as const,
    sector: 'Telecommunications',
    currentPrice: 96.80,
    previousClose: 96.75,
    change: 0.05,
    changePercent: 0.05,
    volume: 400000,
    high: 96.85,
    low: 96.70,
    open: 96.75,
    marketCap: 150000000,
    sizeCategory: 'Mid Cap' as const,
    sectorGroup: 'Telecommunications',
    couponRate: 5.00,
    maturityDate: '2027-12-15',
    yield: 5.75,
    faceValue: 100,
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  }
]

// ETFs (Exchange Traded Funds)
const moroccanETFs = [
  {
    ticker: 'MASI-ETF',
    name: 'MASI Index ETF',
    instrumentType: 'etf' as const,
    sector: 'ETF',
    currentPrice: 125.50,
    previousClose: 125.20,
    change: 0.30,
    changePercent: 0.24,
    volume: 250000,
    high: 125.60,
    low: 125.10,
    open: 125.25,
    marketCap: 50000000,
    sizeCategory: 'Small Cap' as const,
    sectorGroup: 'Exchange Traded Funds',
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  },
  {
    ticker: 'MADEX-ETF',
    name: 'MADEX Index ETF',
    instrumentType: 'etf' as const,
    sector: 'ETF',
    currentPrice: 118.75,
    previousClose: 118.50,
    change: 0.25,
    changePercent: 0.21,
    volume: 200000,
    high: 118.85,
    low: 118.40,
    open: 118.55,
    marketCap: 40000000,
    sizeCategory: 'Small Cap' as const,
    sectorGroup: 'Exchange Traded Funds',
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  }
]

// Warrants and Derivatives
const moroccanWarrants = [
  {
    ticker: 'ATW-WARRANT',
    name: 'Attijariwafa Bank Warrant',
    instrumentType: 'warrant' as const,
    sector: 'Derivatives',
    currentPrice: 15.20,
    previousClose: 15.15,
    change: 0.05,
    changePercent: 0.33,
    volume: 100000,
    high: 15.25,
    low: 15.10,
    open: 15.15,
    marketCap: 10000000,
    sizeCategory: 'Micro Cap' as const,
    sectorGroup: 'Derivatives',
    lastUpdated: new Date().toISOString(),
    delayMinutes: 15
  }
]

import { makeApiUrl } from './getBaseUrl'

class ComprehensiveMarketDataService {
  private config: MarketDataConfig = {
    delayMinutes: 15,
    updateInterval: 5000,
    enableRealisticVolatility: true,
    includeBonds: true,
    includeETFs: true
  }

  private allInstruments: ComprehensiveQuote[] = []
  private updateInterval: NodeJS.Timeout | null = null

  constructor() {
    this.initializeInstruments()
    this.startRealTimeUpdates()
  }

  private async initializeInstruments() {
    try {
      // Load the 78 companies from African markets data
      const response = await fetch(makeApiUrl('/api/market-data/african-markets-companies'))
      if (response.ok) {
        const companies = await response.json()
        this.allInstruments = [
          ...companies.map((company: any) => this.convertToQuote(company)),
          ...moroccanBonds,
          ...corporateBonds,
          ...moroccanETFs,
          ...moroccanWarrants
        ]
      } else {
        // Fallback to mock data if API is not available
        this.allInstruments = [
          ...this.getMockCompanies(),
          ...moroccanBonds,
          ...corporateBonds,
          ...moroccanETFs,
          ...moroccanWarrants
        ]
      }
    } catch (error) {
      console.error('Error loading companies:', error)
      // Use mock data as fallback
      this.allInstruments = [
        ...this.getMockCompanies(),
        ...moroccanBonds,
        ...corporateBonds,
        ...moroccanETFs,
        ...moroccanWarrants
      ]
    }
  }

  private convertToQuote(company: any): ComprehensiveQuote {
    return {
      ticker: company.ticker,
      name: company.name,
      instrumentType: 'stock',
      sector: company.sector,
      currentPrice: company.price || 100,
      previousClose: (company.price || 100) * (1 - (company.change_1d_percent || 0) / 100),
      change: (company.price || 100) * (company.change_1d_percent || 0) / 100,
      changePercent: company.change_1d_percent || 0,
      volume: Math.floor(Math.random() * 1000000) + 100000,
      high: (company.price || 100) * 1.02,
      low: (company.price || 100) * 0.98,
      open: (company.price || 100) * (1 + (Math.random() - 0.5) * 0.01),
      marketCap: (company.market_cap_billion || 1) * 1000000000,
      sizeCategory: company.size_category || 'Small Cap',
      sectorGroup: company.sector_group || company.sector,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15,
      peRatio: Math.random() * 20 + 10,
      dividendYield: Math.random() * 5,
      beta: Math.random() * 2 + 0.5
    }
  }

  private getMockCompanies(): ComprehensiveQuote[] {
    // Return a subset of the 78 companies as mock data
    const mockCompanies = [
      { ticker: 'AFM', name: 'AFMA', sector: 'Financials', price: 1105.0 },
      { ticker: 'AFI', name: 'Afric Industries', sector: 'Industrials', price: 329.0 },
      { ticker: 'GAZ', name: 'Afriquia Gaz', sector: 'Oil & Gas', price: 4400.0 },
      { ticker: 'AGM', name: 'AGMA', sector: 'Financials', price: 6600.0 },
      { ticker: 'ADI', name: 'Alliances', sector: 'Financials', price: 480.0 },
      { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banking', price: 410.10 },
      { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications', price: 156.30 },
      { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banking', price: 268.60 },
      { ticker: 'BMCE', name: 'BMCE Bank', sector: 'Banking', price: 187.40 },
      { ticker: 'CIH', name: 'CIH Bank', sector: 'Banking', price: 312.25 },
      { ticker: 'CMT', name: 'Ciments du Maroc', sector: 'Materials', price: 234.50 },
      { ticker: 'LAFA', name: 'Lafarge Ciments', sector: 'Materials', price: 189.80 },
      { ticker: 'MNG', name: 'Managem', sector: 'Materials', price: 445.60 },
      { ticker: 'TMA', name: 'Taqa Morocco', sector: 'Energy', price: 123.40 },
      { ticker: 'ONA', name: 'Omnium Nord Africain', sector: 'Conglomerates', price: 456.20 }
    ]

    return mockCompanies.map(company => this.convertToQuote(company))
  }

  private startRealTimeUpdates() {
    this.updateInterval = setInterval(() => {
      this.updateQuotes()
    }, this.config.updateInterval)
  }

  private updateQuotes() {
    this.allInstruments = this.allInstruments.map(quote => {
      const volatility = this.calculateVolatility(quote)
      const priceChange = (Math.random() - 0.5) * volatility * quote.currentPrice
      const newPrice = Math.max(0.01, quote.currentPrice + priceChange)
      
      const change = newPrice - quote.previousClose
      const changePercent = (change / quote.previousClose) * 100
      
      const newHigh = Math.max(quote.high, newPrice)
      const newLow = Math.min(quote.low, newPrice)
      
      const volumeChange = Math.floor((Math.random() - 0.5) * quote.volume * 0.1)
      const newVolume = Math.max(0, quote.volume + volumeChange)

      return {
        ...quote,
        currentPrice: parseFloat(newPrice.toFixed(2)),
        change: parseFloat(change.toFixed(2)),
        changePercent: parseFloat(changePercent.toFixed(2)),
        volume: newVolume,
        high: parseFloat(newHigh.toFixed(2)),
        low: parseFloat(newLow.toFixed(2)),
        lastUpdated: new Date().toISOString()
      }
    })
  }

  private calculateVolatility(quote: ComprehensiveQuote): number {
    let baseVolatility = 0.002 // 0.2% base volatility
    
    // Adjust volatility based on instrument type
    switch (quote.instrumentType) {
      case 'bond':
        baseVolatility *= 0.3 // Bonds are less volatile
        break
      case 'etf':
        baseVolatility *= 0.8 // ETFs are moderately volatile
        break
      case 'warrant':
        baseVolatility *= 2.0 // Warrants are more volatile
        break
      default: // stocks
        baseVolatility *= 1.0
    }
    
    // Adjust based on market cap
    if (quote.marketCap > 10000000000) { // Large cap
      baseVolatility *= 0.7
    } else if (quote.marketCap < 1000000000) { // Small cap
      baseVolatility *= 1.5
    }
    
    return baseVolatility * (0.5 + Math.random())
  }

  // Public API methods
  async getAllQuotes(): Promise<ComprehensiveQuote[]> {
    await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300))
    return [...this.allInstruments]
  }

  async getQuotesByType(type: 'stock' | 'bond' | 'etf' | 'warrant'): Promise<ComprehensiveQuote[]> {
    const quotes = await this.getAllQuotes()
    return quotes.filter(q => q.instrumentType === type)
  }

  async getQuoteByTicker(ticker: string): Promise<ComprehensiveQuote | null> {
    const quotes = await this.getAllQuotes()
    return quotes.find(q => q.ticker === ticker.toUpperCase()) || null
  }

  async getMarketSummary(): Promise<{
    totalVolume: number
    advancing: number
    declining: number
    unchanged: number
    averageChange: number
    lastUpdated: string
    byType: {
      stocks: { count: number, advancing: number, declining: number }
      bonds: { count: number, advancing: number, declining: number }
      etfs: { count: number, advancing: number, declining: number }
      warrants: { count: number, advancing: number, declining: number }
    }
  }> {
    const quotes = await this.getAllQuotes()
    
    const totalVolume = quotes.reduce((sum, q) => sum + q.volume, 0)
    const advancing = quotes.filter(q => q.change > 0).length
    const declining = quotes.filter(q => q.change < 0).length
    const unchanged = quotes.filter(q => q.change === 0).length
    const averageChange = quotes.reduce((sum, q) => sum + q.changePercent, 0) / quotes.length

    const byType = {
      stocks: {
        count: quotes.filter(q => q.instrumentType === 'stock').length,
        advancing: quotes.filter(q => q.instrumentType === 'stock' && q.change > 0).length,
        declining: quotes.filter(q => q.instrumentType === 'stock' && q.change < 0).length
      },
      bonds: {
        count: quotes.filter(q => q.instrumentType === 'bond').length,
        advancing: quotes.filter(q => q.instrumentType === 'bond' && q.change > 0).length,
        declining: quotes.filter(q => q.instrumentType === 'bond' && q.change < 0).length
      },
      etfs: {
        count: quotes.filter(q => q.instrumentType === 'etf').length,
        advancing: quotes.filter(q => q.instrumentType === 'etf' && q.change > 0).length,
        declining: quotes.filter(q => q.instrumentType === 'etf' && q.change < 0).length
      },
      warrants: {
        count: quotes.filter(q => q.instrumentType === 'warrant').length,
        advancing: quotes.filter(q => q.instrumentType === 'warrant' && q.change > 0).length,
        declining: quotes.filter(q => q.instrumentType === 'warrant' && q.change < 0).length
      }
    }

    return {
      totalVolume,
      advancing,
      declining,
      unchanged,
      averageChange: parseFloat(averageChange.toFixed(2)),
      lastUpdated: new Date().toISOString(),
      byType
    }
  }

  stopUpdates() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
      this.updateInterval = null
    }
  }

  updateConfig(config: Partial<MarketDataConfig>) {
    this.config = { ...this.config, ...config }
    if (this.updateInterval) {
      this.stopUpdates()
      this.startRealTimeUpdates()
    }
  }
}

// Create singleton instance
export const comprehensiveMarketData = new ComprehensiveMarketDataService()

// Export types for use in components 