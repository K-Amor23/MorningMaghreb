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

    // Get user's sentiment votes
    const { data: votes, error } = await supabase
      .from('sentiment_votes')
      .select('id, ticker, sentiment, confidence, created_at, updated_at')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching user votes:', error)
      return res.status(500).json({ error: 'Failed to fetch votes' })
    }

    res.status(200).json(votes || [])
  } catch (error) {
    console.error('Error in my-votes endpoint:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to fetch user votes'
    })
  }
} 