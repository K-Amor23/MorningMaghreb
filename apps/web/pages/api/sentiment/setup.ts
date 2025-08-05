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

        // Create sentiment_votes table
        const { error: votesError } = await supabase.rpc('exec_sql', {
            sql: `
        CREATE TABLE IF NOT EXISTS sentiment_votes (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id TEXT NOT NULL,
          ticker VARCHAR(10) NOT NULL,
          sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('bullish', 'neutral', 'bearish')),
          confidence INTEGER NOT NULL DEFAULT 3 CHECK (confidence >= 1 AND confidence <= 5),
          created_at TIMESTAMPTZ DEFAULT NOW(),
          updated_at TIMESTAMPTZ DEFAULT NOW(),
          UNIQUE(user_id, ticker)
        );
      `
        })

        if (votesError) {
            console.error('Error creating sentiment_votes table:', votesError)
            return res.status(500).json({ error: 'Failed to create sentiment_votes table' })
        }

        // Create sentiment_aggregates table
        const { error: aggregatesError } = await supabase.rpc('exec_sql', {
            sql: `
        CREATE TABLE IF NOT EXISTS sentiment_aggregates (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          ticker VARCHAR(10) NOT NULL UNIQUE,
          bullish_count INTEGER DEFAULT 0,
          neutral_count INTEGER DEFAULT 0,
          bearish_count INTEGER DEFAULT 0,
          total_votes INTEGER DEFAULT 0,
          bullish_percentage DECIMAL(5,2) DEFAULT 0.0,
          neutral_percentage DECIMAL(5,2) DEFAULT 0.0,
          bearish_percentage DECIMAL(5,2) DEFAULT 0.0,
          average_confidence DECIMAL(3,2) DEFAULT 0.0,
          last_updated TIMESTAMPTZ DEFAULT NOW()
        );
      `
        })

        if (aggregatesError) {
            console.error('Error creating sentiment_aggregates table:', aggregatesError)
            return res.status(500).json({ error: 'Failed to create sentiment_aggregates table' })
        }

        // Create indexes
        const { error: indexesError } = await supabase.rpc('exec_sql', {
            sql: `
        CREATE INDEX IF NOT EXISTS idx_sentiment_votes_user_id ON sentiment_votes(user_id);
        CREATE INDEX IF NOT EXISTS idx_sentiment_votes_ticker ON sentiment_votes(ticker);
        CREATE INDEX IF NOT EXISTS idx_sentiment_votes_sentiment ON sentiment_votes(sentiment);
        CREATE INDEX IF NOT EXISTS idx_sentiment_aggregates_ticker ON sentiment_aggregates(ticker);
      `
        })

        if (indexesError) {
            console.error('Error creating indexes:', indexesError)
            return res.status(500).json({ error: 'Failed to create indexes' })
        }

        res.status(200).json({
            success: true,
            message: 'Sentiment voting tables created successfully'
        })
    } catch (error) {
        console.error('Setup error:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to setup sentiment voting tables'
        })
    }
} 