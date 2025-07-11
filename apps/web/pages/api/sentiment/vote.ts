import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Check supabase config
    if (!isSupabaseConfigured() || !supabase) {
      return res.status(500).json({ error: 'Database connection not configured' })
    }
    // Get user from auth header
    const authHeader = req.headers.authorization
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    const token = authHeader.split(' ')[1]
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)

    if (authError || !user) {
      return res.status(401).json({ error: 'Invalid token' })
    }

    const { ticker, sentiment, confidence } = req.body

    // Validate input
    if (!ticker || !sentiment) {
      return res.status(400).json({ error: 'Ticker and sentiment are required' })
    }

    if (!['bullish', 'neutral', 'bearish'].includes(sentiment)) {
      return res.status(400).json({ error: 'Invalid sentiment. Must be bullish, neutral, or bearish' })
    }

    if (confidence && (confidence < 1 || confidence > 5)) {
      return res.status(400).json({ error: 'Confidence must be between 1 and 5' })
    }

    // Check if user already voted on this ticker
    const { data: existingVote } = await supabase
      .from('sentiment_votes')
      .select('id, sentiment, confidence')
      .eq('user_id', user.id)
      .eq('ticker', ticker)
      .single()

    if (existingVote) {
      // Update existing vote
      const { data, error } = await supabase
        .from('sentiment_votes')
        .update({
          sentiment,
          confidence: confidence || existingVote.confidence,
          updated_at: new Date().toISOString(),
        })
        .eq('id', existingVote.id)
        .select()
        .single()

      if (error) {
        console.error('Error updating sentiment vote:', error)
        return res.status(500).json({ error: 'Failed to update vote' })
      }

      // Update aggregate (this would typically be done via a database trigger or background job)
      await updateSentimentAggregate(ticker)

      return res.status(200).json({
        id: data.id,
        ticker: data.ticker,
        sentiment: data.sentiment,
        confidence: data.confidence,
        user_id: data.user_id,
        created_at: data.created_at,
      })
    } else {
      // Create new vote
      const { data, error } = await supabase
        .from('sentiment_votes')
        .insert([
          {
            user_id: user.id,
            ticker,
            sentiment,
            confidence: confidence || 3,
            created_at: new Date().toISOString(),
          },
        ])
        .select()
        .single()

      if (error) {
        console.error('Error creating sentiment vote:', error)
        return res.status(500).json({ error: 'Failed to create vote' })
      }

      // Update aggregate
      await updateSentimentAggregate(ticker)

      return res.status(201).json({
        id: data.id,
        ticker: data.ticker,
        sentiment: data.sentiment,
        confidence: data.confidence,
        user_id: data.user_id,
        created_at: data.created_at,
      })
    }
  } catch (error) {
    console.error('Sentiment vote error:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to process sentiment vote'
    })
  }
}

async function updateSentimentAggregate(ticker: string) {
  try {
    if (!isSupabaseConfigured() || !supabase) {
      console.error('Supabase not configured')
      return
    }
    // Get all votes for the ticker
    const { data: votes } = await supabase
      .from('sentiment_votes')
      .select('sentiment, confidence')
      .eq('ticker', ticker)

    if (!votes || votes.length === 0) {
      // Remove aggregate if no votes
      await supabase
        .from('sentiment_aggregates')
        .delete()
        .eq('ticker', ticker)
      return
    }

    // Calculate aggregates
    const totalVotes = votes.length
    const bullishCount = votes.filter(v => v.sentiment === 'bullish').length
    const neutralCount = votes.filter(v => v.sentiment === 'neutral').length
    const bearishCount = votes.filter(v => v.sentiment === 'bearish').length

    const bullishPercentage = (bullishCount / totalVotes) * 100
    const neutralPercentage = (neutralCount / totalVotes) * 100
    const bearishPercentage = (bearishCount / totalVotes) * 100

    const averageConfidence = votes.reduce((sum, v) => sum + (v.confidence || 3), 0) / totalVotes

    // Update or create aggregate
    const { data: existingAggregate } = await supabase
      .from('sentiment_aggregates')
      .select('id')
      .eq('ticker', ticker)
      .single()

    if (existingAggregate) {
      await supabase
        .from('sentiment_aggregates')
        .update({
          bullish_count: bullishCount,
          neutral_count: neutralCount,
          bearish_count: bearishCount,
          total_votes: totalVotes,
          bullish_percentage: bullishPercentage,
          neutral_percentage: neutralPercentage,
          bearish_percentage: bearishPercentage,
          average_confidence: averageConfidence,
          last_updated: new Date().toISOString(),
        })
        .eq('id', existingAggregate.id)
    } else {
      await supabase
        .from('sentiment_aggregates')
        .insert([
          {
            ticker,
            bullish_count: bullishCount,
            neutral_count: neutralCount,
            bearish_count: bearishCount,
            total_votes: totalVotes,
            bullish_percentage: bullishPercentage,
            neutral_percentage: neutralPercentage,
            bearish_percentage: bearishPercentage,
            average_confidence: averageConfidence,
            last_updated: new Date().toISOString(),
          },
        ])
    }
  } catch (error) {
    console.error('Error updating sentiment aggregate:', error)
  }
} 