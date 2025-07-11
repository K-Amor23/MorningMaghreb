import type { NextApiRequest, NextApiResponse } from 'next'

interface RateTrend {
  date: string
  bam_rate: number
  best_rate: number
  avg_rate: number
}

interface TrendsResponse {
  trends: RateTrend[]
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<TrendsResponse | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const currency_pair = req.query.currency_pair as string || 'USD/MAD'
    const days = req.query.days ? parseInt(req.query.days as string) : 7

    // In production, this would call the backend API
    // For now, return mock data
    const trends: RateTrend[] = []
    const today = new Date()
    const baseBamRate = 10.25
    const baseBestRate = 10.15

    for (let i = 0; i < days; i++) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      
      // Add realistic variation
      const variation = (i % 3 - 1) * 0.02
      
      trends.push({
        date: date.toISOString().split('T')[0],
        bam_rate: baseBamRate + variation,
        best_rate: baseBestRate + variation,
        avg_rate: baseBamRate + variation * 0.5
      })
    }

    res.status(200).json({ trends })
  } catch (error) {
    console.error('Error fetching rate trends:', error)
    res.status(500).json({ error: 'Failed to fetch rate trends' })
  }
} 