// Delayed Market Data System for Paper Trading
// Simulates real-time data with 10-15 minute delay like ThinkOrSwim

export interface DelayedQuote {
  ticker: string
  name: string
  currentPrice: number
  previousClose: number
  change: number
  changePercent: number
  volume: number
  high: number
  low: number
  open: number
  marketCap: number
  lastUpdated: string
  delayMinutes: number
}

export interface MarketDataConfig {
  delayMinutes: number
  updateInterval: number // milliseconds
  enableRealisticVolatility: boolean
}

class DelayedMarketDataService {
  private config: MarketDataConfig = {
    delayMinutes: 15, // 15-minute delay like ThinkOrSwim
    updateInterval: 5000, // Update every 5 seconds
    enableRealisticVolatility: true
  }

  private baseQuotes: DelayedQuote[] = [
    {
      ticker: 'ATW',
      name: 'Attijariwafa Bank',
      currentPrice: 410.10,
      previousClose: 408.82,
      change: 1.28,
      changePercent: 0.31,
      volume: 1250000,
      high: 412.50,
      low: 408.00,
      open: 409.20,
      marketCap: 24560000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'IAM',
      name: 'Maroc Telecom',
      currentPrice: 156.30,
      previousClose: 158.40,
      change: -2.10,
      changePercent: -1.33,
      volume: 890000,
      high: 158.80,
      low: 155.90,
      open: 157.60,
      marketCap: 15680000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'BCP',
      name: 'Banque Centrale Populaire',
      currentPrice: 268.60,
      previousClose: 260.50,
      change: 8.10,
      changePercent: 3.11,
      volume: 2100000,
      high: 270.20,
      low: 261.80,
      open: 262.40,
      marketCap: 18750000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'BMCE',
      name: 'BMCE Bank',
      currentPrice: 187.40,
      previousClose: 188.30,
      change: -0.90,
      changePercent: -0.48,
      volume: 680000,
      high: 189.10,
      low: 186.50,
      open: 188.80,
      marketCap: 12400000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'ONA',
      name: 'Omnium Nord Africain',
      currentPrice: 456.20,
      previousClose: 452.80,
      change: 3.40,
      changePercent: 0.75,
      volume: 320000,
      high: 458.90,
      low: 451.60,
      open: 453.40,
      marketCap: 89100000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'CMT',
      name: 'Ciments du Maroc',
      currentPrice: 234.50,
      previousClose: 233.30,
      change: 1.20,
      changePercent: 0.51,
      volume: 450000,
      high: 236.80,
      low: 232.10,
      open: 233.90,
      marketCap: 15600000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'LAFA',
      name: 'Lafarge Ciments',
      currentPrice: 189.80,
      previousClose: 191.30,
      change: -1.50,
      changePercent: -0.78,
      volume: 380000,
      high: 192.40,
      low: 188.90,
      open: 191.60,
      marketCap: 12300000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'CIH',
      name: 'CIH Bank',
      currentPrice: 312.25,
      previousClose: 309.50,
      change: 2.75,
      changePercent: 0.89,
      volume: 520000,
      high: 314.80,
      low: 308.20,
      open: 310.10,
      marketCap: 18700000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'MNG',
      name: 'Managem',
      currentPrice: 445.60,
      previousClose: 440.20,
      change: 5.40,
      changePercent: 1.23,
      volume: 280000,
      high: 448.90,
      low: 439.80,
      open: 441.50,
      marketCap: 23400000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    },
    {
      ticker: 'TMA',
      name: 'Taqa Morocco',
      currentPrice: 123.40,
      previousClose: 124.00,
      change: -0.60,
      changePercent: -0.48,
      volume: 890000,
      high: 125.20,
      low: 122.80,
      open: 124.30,
      marketCap: 8900000000,
      lastUpdated: new Date().toISOString(),
      delayMinutes: 15
    }
  ]

  private currentQuotes: DelayedQuote[] = [...this.baseQuotes]
  private updateInterval: NodeJS.Timeout | null = null

  constructor(config?: Partial<MarketDataConfig>) {
    if (config) {
      this.config = { ...this.config, ...config }
    }
    this.startRealTimeUpdates()
  }

  // Start real-time updates with delay simulation
  private startRealTimeUpdates() {
    this.updateInterval = setInterval(() => {
      this.updateQuotes()
    }, this.config.updateInterval)
  }

  // Simulate realistic price movements
  private updateQuotes() {
    this.currentQuotes = this.currentQuotes.map(quote => {
      const volatility = this.config.enableRealisticVolatility ? 
        this.calculateVolatility(quote.currentPrice) : 0.001
      
      const priceChange = (Math.random() - 0.5) * volatility * quote.currentPrice
      const newPrice = Math.max(0.01, quote.currentPrice + priceChange)
      
      const change = newPrice - quote.previousClose
      const changePercent = (change / quote.previousClose) * 100
      
      // Update high/low
      const newHigh = Math.max(quote.high, newPrice)
      const newLow = Math.min(quote.low, newPrice)
      
      // Simulate volume changes
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

  // Calculate realistic volatility based on stock characteristics
  private calculateVolatility(price: number): number {
    // Higher priced stocks tend to have lower volatility
    const baseVolatility = 0.002 // 0.2% base volatility
    const priceFactor = Math.max(0.1, 100 / price) // Lower price = higher volatility
    return baseVolatility * priceFactor * (0.5 + Math.random())
  }

  // Get delayed quote for a specific ticker
  async getDelayedQuote(ticker: string): Promise<DelayedQuote | null> {
    const quote = this.currentQuotes.find(q => q.ticker === ticker.toUpperCase())
    if (!quote) return null

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200))
    
    return quote
  }

  // Get all delayed quotes
  async getAllDelayedQuotes(): Promise<DelayedQuote[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300))
    
    return [...this.currentQuotes]
  }

  // Get delayed quotes for multiple tickers
  async getDelayedQuotes(tickers: string[]): Promise<DelayedQuote[]> {
    const quotes = this.currentQuotes.filter(q => 
      tickers.map(t => t.toUpperCase()).includes(q.ticker)
    )
    
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 150 + Math.random() * 250))
    
    return quotes
  }

  // Get market summary with delay
  async getMarketSummary(): Promise<{
    totalVolume: number
    advancing: number
    declining: number
    unchanged: number
    averageChange: number
    lastUpdated: string
  }> {
    const quotes = await this.getAllDelayedQuotes()
    
    const totalVolume = quotes.reduce((sum, q) => sum + q.volume, 0)
    const advancing = quotes.filter(q => q.change > 0).length
    const declining = quotes.filter(q => q.change < 0).length
    const unchanged = quotes.filter(q => q.change === 0).length
    const averageChange = quotes.reduce((sum, q) => sum + q.changePercent, 0) / quotes.length

    return {
      totalVolume,
      advancing,
      declining,
      unchanged,
      averageChange: parseFloat(averageChange.toFixed(2)),
      lastUpdated: new Date().toISOString()
    }
  }

  // Stop real-time updates
  stopUpdates() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval)
      this.updateInterval = null
    }
  }

  // Reset to base quotes
  resetQuotes() {
    this.currentQuotes = [...this.baseQuotes]
  }

  // Update configuration
  updateConfig(config: Partial<MarketDataConfig>) {
    this.config = { ...this.config, ...config }
    
    // Restart updates if interval changed
    if (this.updateInterval) {
      this.stopUpdates()
      this.startRealTimeUpdates()
    }
  }
}

// Create singleton instance
export const delayedMarketData = new DelayedMarketDataService()

// Export types for use in components 