import type { NextApiRequest, NextApiResponse } from 'next'
import { featureFlags, isPremiumEnforced, hasDevBypass } from '@/lib/featureFlags'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Return feature flags status for debugging
    const flagsStatus = {
      flags: featureFlags,
      status: {
        premiumEnforced: isPremiumEnforced(),
        devBypass: hasDevBypass(),
        environment: process.env.NEXT_PUBLIC_ENV || 'production',
        timestamp: new Date().toISOString()
      }
    }

    res.status(200).json(flagsStatus)
  } catch (error) {
    console.error('Error fetching feature flags:', error)
    res.status(500).json({ error: 'Failed to fetch feature flags' })
  }
} 