import { NextApiRequest, NextApiResponse } from 'next'

interface RemittanceRate {
  service_name: string
  rate: number
  fee_amount: number
  fee_currency: string
  effective_rate: number
  spread_percentage: number
}

interface CurrencyComparison {
  currency_pair: string
  bam_rate: number
  services: RemittanceRate[]
  best_service: string
  best_rate: number
  best_spread: number
  recommendation: string
  is_good_time: boolean
  percentile_30d: number
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    const { currency_pair } = req.query
    const amount = parseFloat(req.query.amount as string) || 1000

    // Mock data for demonstration
    // In production, this would call the backend API
    const mockComparison: CurrencyComparison = {
      currency_pair: currency_pair as string,
      bam_rate: 10.25,
      services: [
        {
          service_name: "Remitly",
          rate: 10.15,
          fee_amount: 3.99,
          fee_currency: "USD",
          effective_rate: 10.12,
          spread_percentage: 1.27
        },
        {
          service_name: "Wise",
          rate: 10.20,
          fee_amount: 5.50,
          fee_currency: "USD",
          effective_rate: 10.15,
          spread_percentage: 0.98
        },
        {
          service_name: "Western Union",
          rate: 10.05,
          fee_amount: 8.00,
          fee_currency: "USD",
          effective_rate: 9.97,
          spread_percentage: 2.73
        }
      ],
      best_service: "Wise",
      best_rate: 10.15,
      best_spread: 0.98,
      recommendation: "Good timing. Today's rate is above average. Reasonable spread. Wise is 0.98% below BAM rate.",
      is_good_time: true,
      percentile_30d: 75
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))

    res.status(200).json(mockComparison)
  } catch (error) {
    console.error('Error in currency comparison API:', error)
    res.status(500).json({ message: 'Internal server error' })
  }
} 