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
    const currency_pair = (req.query.currency_pair as string) || 'USD/MAD'
    const days = req.query.days ? parseInt(req.query.days as string) : 7

    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
    const url = `${backendUrl}/currency/trends/${encodeURIComponent(currency_pair)}?days=${days}`
    const r = await fetch(url)
    if (!r.ok) {
      throw new Error(`Backend error ${r.status}`)
    }
    const data = (await r.json()) as TrendsResponse
    res.status(200).json(data)
  } catch (error) {
    console.error('Error fetching rate trends:', error)
    res.status(500).json({ error: 'Failed to fetch rate trends' })
  }
} 