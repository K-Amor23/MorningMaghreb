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
    const { currency_pair } = req.query
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10

    // In production, this would call the backend API
    // For now, return mock data
    const insights: CrowdsourceInsight[] = [
      {
        id: '1',
        user_type: 'Frequent User',
        message: 'Remitly usually has the best rates on Tuesdays and Wednesdays. Avoid weekends!',
        rating: 4.8,
        timestamp: '2 hours ago',
        likes: 23,
        helpful_count: 15
      },
      {
        id: '2',
        user_type: 'Expat',
        message: 'I always check Bank Al-Maghrib rate first, then compare with Wise. Usually saves me 1-2%',
        rating: 4.6,
        timestamp: '5 hours ago',
        likes: 18,
        helpful_count: 12
      },
      {
        id: '3',
        user_type: 'Business Owner',
        message: 'Western Union has good rates for large amounts (>$5000). Smaller amounts, go with Remitly.',
        rating: 4.4,
        timestamp: '1 day ago',
        likes: 15,
        helpful_count: 8
      },
      {
        id: '4',
        user_type: 'Student',
        message: 'CIH Bank has the best rates for students with student accounts. Check their special programs!',
        rating: 4.7,
        timestamp: '2 days ago',
        likes: 12,
        helpful_count: 6
      },
      {
        id: '5',
        user_type: 'Traveler',
        message: 'For small amounts (<$500), Wise is usually the best. For larger amounts, compare all services.',
        rating: 4.5,
        timestamp: '3 days ago',
        likes: 10,
        helpful_count: 5
      }
    ]

    res.status(200).json({ insights: insights.slice(0, limit) })
  } catch (error) {
    console.error('Error fetching crowdsource insights:', error)
    res.status(500).json({ error: 'Failed to fetch insights' })
  }
} 