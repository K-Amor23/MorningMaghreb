import type { NextApiRequest, NextApiResponse } from 'next'

interface CrowdsourceInsight {
  id: string
  user_type: string
  message: string
  rating: number
  timestamp: string
  likes: number
  helpful_count: number
}

interface InsightsResponse {
  insights: CrowdsourceInsight[]
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<InsightsResponse | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const currency_pair = (req.query.currency_pair as string) || 'USD/MAD'
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
    const url = `${backendUrl}/currency/insights/${encodeURIComponent(currency_pair)}?limit=${limit}`
    const r = await fetch(url)
    if (!r.ok) {
      throw new Error(`Backend error ${r.status}`)
    }
    const data = await r.json()
    res.status(200).json(data as InsightsResponse)
  } catch (error) {
    console.error('Error fetching crowdsource insights:', error)
    res.status(500).json({ error: 'Failed to fetch insights' })
  }
} 