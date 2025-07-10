import type { NextApiRequest, NextApiResponse } from 'next'
import { supabase } from '@/lib/supabase'
import { handleChatQuery } from '@/lib/openai'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
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

    // Check subscription tier (pro users get more queries)
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('subscription_tier')
      .eq('user_id', user.id)
      .single()

    // Rate limiting - check recent queries
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString()
    const { data: recentQueries } = await supabase
      .from('chat_queries')
      .select('id')
      .eq('user_id', user.id)
      .gte('created_at', oneHourAgo)

    const queryLimit = profile?.subscription_tier === 'pro' ? 100 : 20
    if (recentQueries && recentQueries.length >= queryLimit) {
      return res.status(429).json({ 
        error: 'Rate limit exceeded',
        message: `You have reached your hourly limit of ${queryLimit} queries`
      })
    }

    const { messages, context } = req.body

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Messages array is required' })
    }

    // Get relevant market data context
    const marketContext = await getMarketContext(context?.tickers)

    // Generate AI response
    const response = await handleChatQuery(messages, marketContext)

    // Log the query
    await supabase
      .from('chat_queries')
      .insert([
        {
          user_id: user.id,
          query: messages[messages.length - 1]?.content || '',
          response,
          context: marketContext,
          created_at: new Date().toISOString(),
        },
      ])

    res.status(200).json({
      success: true,
      response,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Chat API error:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to process chat query'
    })
  }
}

async function getMarketContext(tickers?: string[]) {
  // Mock market context - in real app, fetch from database
  const mockContext = {
    marketData: {
      MASI: { price: 13456.78, change: 2.34, changePercent: 0.017 },
      MADEX: { price: 11234.56, change: -1.23, changePercent: -0.011 },
      ATW: { price: 534.50, change: 4.50, changePercent: 0.008 },
    },
    macroData: {
      policyRate: 3.0,
      cpi: 2.5,
      unemployment: 9.2,
    },
    timestamp: new Date().toISOString(),
  }

  return mockContext
}