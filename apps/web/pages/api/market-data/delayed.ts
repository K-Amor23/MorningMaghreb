import type { NextApiRequest, NextApiResponse } from 'next'
import { delayedMarketData } from '@/lib/delayedMarketData'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { ticker, summary } = req.query

    // Get specific ticker quote
    if (ticker && typeof ticker === 'string') {
      const quote = await delayedMarketData.getDelayedQuote(ticker)
      if (!quote) {
        return res.status(404).json({ error: 'Ticker not found' })
      }
      return res.status(200).json(quote)
    }

    // Get market summary
    if (summary === 'true') {
      const marketSummary = await delayedMarketData.getMarketSummary()
      return res.status(200).json(marketSummary)
    }

    // Get all quotes
    const quotes = await delayedMarketData.getAllDelayedQuotes()
    return res.status(200).json(quotes)

  } catch (error) {
    console.error('Error fetching delayed market data:', error)
    return res.status(500).json({ error: 'Failed to fetch market data' })
  }
} 