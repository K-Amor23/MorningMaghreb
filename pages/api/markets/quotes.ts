import type { NextApiRequest, NextApiResponse } from 'next'

// Mock data - in real app, this would come from CSE API
const mockQuotes = [
  { ticker: 'MASI', price: 13456.78, change: 2.34, changePercent: 0.017, volume: 1250000, timestamp: new Date().toISOString() },
  { ticker: 'MADEX', price: 11234.56, change: -1.23, changePercent: -0.011, volume: 890000, timestamp: new Date().toISOString() },
  { ticker: 'MASI-ESG', price: 987.65, change: 0.98, changePercent: 0.001, volume: 45000, timestamp: new Date().toISOString() },
  { ticker: 'ATW', price: 534.50, change: 4.50, changePercent: 0.008, volume: 156000, timestamp: new Date().toISOString() },
  { ticker: 'IAM', price: 156.30, change: -2.10, changePercent: -0.013, volume: 234000, timestamp: new Date().toISOString() },
  { ticker: 'BCP', price: 268.60, change: 8.10, changePercent: 0.031, volume: 189000, timestamp: new Date().toISOString() },
]

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { tickers } = req.query
    
    let filteredQuotes = mockQuotes

    // Filter by specific tickers if provided
    if (tickers && typeof tickers === 'string') {
      const tickerList = tickers.split(',').map(t => t.trim().toUpperCase())
      filteredQuotes = mockQuotes.filter(quote => 
        tickerList.includes(quote.ticker.toUpperCase())
      )
    }

    // Simulate real-time price fluctuations
    const liveQuotes = filteredQuotes.map(quote => ({
      ...quote,
      price: quote.price + (Math.random() - 0.5) * 2,
      change: quote.change + (Math.random() - 0.5) * 0.5,
      changePercent: quote.changePercent + (Math.random() - 0.5) * 0.001,
      timestamp: new Date().toISOString(),
    }))

    res.status(200).json({
      success: true,
      data: liveQuotes,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error fetching market quotes:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to fetch market quotes'
    })
  }
}