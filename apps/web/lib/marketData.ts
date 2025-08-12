// Market data types
export interface MarketQuote {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap?: number
  high?: number
  low?: number
  open?: number
  previousClose?: number
  timestamp: string
}

// Mock market data for development
const mockMarketData: MarketQuote[] = [
  {
    symbol: 'MASI',
    price: 12500.50,
    change: 125.30,
    changePercent: 1.01,
    volume: 1500000,
    marketCap: 125000000000,
    high: 12600.00,
    low: 12400.00,
    open: 12450.00,
    previousClose: 12375.20,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'ATW',
    price: 45.20,
    change: -0.80,
    changePercent: -1.74,
    volume: 500000,
    marketCap: 5000000000,
    high: 46.00,
    low: 44.50,
    open: 45.50,
    previousClose: 46.00,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'CIH',
    price: 12.80,
    change: 0.15,
    changePercent: 1.19,
    volume: 800000,
    marketCap: 2000000000,
    high: 13.00,
    low: 12.60,
    open: 12.70,
    previousClose: 12.65,
    timestamp: new Date().toISOString()
  }
]

// Fetch market data for given symbols
export async function fetchMarketData(symbols: string[]): Promise<MarketQuote[]> {
  try {
    // In a real implementation, this would call an API
    // For now, return mock data filtered by symbols
    return mockMarketData.filter(quote => symbols.includes(quote.symbol))
  } catch (error) {
    console.error('Error fetching market data:', error)
    return []
  }
}

// Subscribe to real-time market data updates
export function subscribeToMarketData(
  symbols: string[], 
  callback: (data: MarketQuote[]) => void
): () => void {
  // In a real implementation, this would set up WebSocket connection
  // For now, simulate real-time updates with setInterval
  const interval = setInterval(() => {
    const updatedData = mockMarketData.map(quote => ({
      ...quote,
      price: quote.price + (Math.random() - 0.5) * 2, // Random price movement
      timestamp: new Date().toISOString()
    }))
    
    const filteredData = updatedData.filter(quote => symbols.includes(quote.symbol))
    callback(filteredData)
  }, 5000) // Update every 5 seconds

  // Return unsubscribe function
  return () => clearInterval(interval)
}

// Get single quote for a symbol
export async function getQuote(symbol: string): Promise<MarketQuote | null> {
  try {
    const quotes = await fetchMarketData([symbol])
    return quotes[0] || null
  } catch (error) {
    console.error('Error fetching quote:', error)
    return null
  }
}

// Get market summary
export async function getMarketSummary(): Promise<{
  totalVolume: number
  gainers: number
  losers: number
  unchanged: number
}> {
  try {
    const quotes = await fetchMarketData([])
    const gainers = quotes.filter(q => q.change > 0).length
    const losers = quotes.filter(q => q.change < 0).length
    const unchanged = quotes.filter(q => q.change === 0).length
    const totalVolume = quotes.reduce((sum, q) => sum + q.volume, 0)

    return {
      totalVolume,
      gainers,
      losers,
      unchanged
    }
  } catch (error) {
    console.error('Error fetching market summary:', error)
    return {
      totalVolume: 0,
      gainers: 0,
      losers: 0,
      unchanged: 0
    }
  }
} 