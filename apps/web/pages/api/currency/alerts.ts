import { NextApiRequest, NextApiResponse } from 'next'

interface RateAlertCreate {
  currency_pair: string
  target_rate: number
  alert_type: string
}

interface RateAlertResponse {
  id: string
  currency_pair: string
  target_rate: number
  alert_type: string
  is_active: boolean
  created_at: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    try {
      const { currency_pair, target_rate, alert_type }: RateAlertCreate = req.body

      // Validate input
      if (!currency_pair || !target_rate) {
        return res.status(400).json({ message: 'Missing required fields' })
      }

      // Mock alert creation
      // In production, this would save to database
      const mockAlert: RateAlertResponse = {
        id: `alert_${Date.now()}`,
        currency_pair,
        target_rate,
        alert_type: alert_type || 'above',
        is_active: true,
        created_at: new Date().toISOString()
      }

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300))

      res.status(201).json(mockAlert)
    } catch (error) {
      console.error('Error creating rate alert:', error)
      res.status(500).json({ message: 'Internal server error' })
    }
  } else if (req.method === 'GET') {
    try {
      // Mock user alerts
      // In production, this would fetch from database based on user ID
      const mockAlerts: RateAlertResponse[] = [
        {
          id: 'alert_123',
          currency_pair: 'USD/MAD',
          target_rate: 10.00,
          alert_type: 'above',
          is_active: true,
          created_at: new Date().toISOString()
        }
      ]

      res.status(200).json(mockAlerts)
    } catch (error) {
      console.error('Error fetching rate alerts:', error)
      res.status(500).json({ message: 'Internal server error' })
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' })
  }
} 