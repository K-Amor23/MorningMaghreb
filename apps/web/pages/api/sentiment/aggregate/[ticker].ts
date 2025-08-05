import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Check supabase config
    if (!isSupabaseConfigured() || !supabase) {
      return res.status(500).json({ error: 'Database connection not configured' })
    }

    const { ticker } = req.query

    if (!ticker || typeof ticker !== 'string') {
      return res.status(400).json({ error: 'Ticker is required' })
    }

    // For now, return mock aggregate data for testing
    const mockAggregate = {
      ticker: ticker.toUpperCase(),
      bullish_count: Math.floor(Math.random() * 50) + 10,
      neutral_count: Math.floor(Math.random() * 30) + 5,
      bearish_count: Math.floor(Math.random() * 20) + 2,
      total_votes: 0,
      bullish_percentage: 0,
      neutral_percentage: 0,
      bearish_percentage: 0,
      average_confidence: 3.5,
      last_updated: new Date().toISOString(),
    }

    // Calculate percentages
    const total = mockAggregate.bullish_count + mockAggregate.neutral_count + mockAggregate.bearish_count
    mockAggregate.total_votes = total
    mockAggregate.bullish_percentage = total > 0 ? (mockAggregate.bullish_count / total) * 100 : 0
    mockAggregate.neutral_percentage = total > 0 ? (mockAggregate.neutral_count / total) * 100 : 0
    mockAggregate.bearish_percentage = total > 0 ? (mockAggregate.bearish_count / total) * 100 : 0

    res.status(200).json(mockAggregate)

    // TODO: Uncomment this when database is properly configured
    /*
    // Get sentiment aggregate for the ticker
    const { data: aggregate, error } = await supabase
      .from('sentiment_aggregates')
      .select('*')
      .eq('ticker', ticker.toUpperCase())
      .single()

    if (error && error.code !== 'PGRST116') { // PGRST116 is "not found"
      console.error('Error fetching sentiment aggregate:', error)
      return res.status(500).json({ error: 'Failed to fetch sentiment data' })
    }

    if (!aggregate) {
      // Return empty aggregate if no data exists
      return res.status(200).json({
        ticker: ticker.toUpperCase(),
        bullish_count: 0,
        neutral_count: 0,
        bearish_count: 0,
        total_votes: 0,
        bullish_percentage: 0,
        neutral_percentage: 0,
        bearish_percentage: 0,
        average_confidence: 0,
        last_updated: null,
      })
    }

    res.status(200).json(aggregate)
    */
  } catch (error) {
    console.error('Error in aggregate endpoint:', error)
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch sentiment aggregate'
    })
  }
} 