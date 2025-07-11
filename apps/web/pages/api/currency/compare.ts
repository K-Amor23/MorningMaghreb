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
  console.log('Currency compare API called:', req.url, req.query)
  
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    const currency_pair = req.query.currency_pair as string || 'USD/MAD'
    const amount = parseFloat(req.query.amount as string) || 1000
    
    console.log('Currency pair:', currency_pair, 'Amount:', amount)

    // Enhanced mock data with all services
    const mockComparison: CurrencyComparison = {
      currency_pair: currency_pair,
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
        },
        {
          service_name: "TransferWise",
          rate: 10.18,
          fee_amount: 4.25,
          fee_currency: "USD",
          effective_rate: 10.14,
          spread_percentage: 1.07
        },
        {
          service_name: "CIH Bank",
          rate: 10.22,
          fee_amount: 15.00,
          fee_currency: "MAD",
          effective_rate: 10.07,
          spread_percentage: 1.76
        },
        {
          service_name: "Attijari Bank",
          rate: 10.24,
          fee_amount: 20.00,
          fee_currency: "MAD",
          effective_rate: 10.04,
          spread_percentage: 2.05
        }
      ],
      best_service: "Wise",
      best_rate: 10.15,
      best_spread: 0.98,
      recommendation: "Excellent timing! Today's rate is better than 75% of the past 30 days. Wise offers the best effective rate at 10.15 MAD per USD with only a 0.98% spread below the official BAM rate. This is a great time to transfer money.",
      is_good_time: true,
      percentile_30d: 75
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300))

    console.log('Returning comparison data:', mockComparison)
    res.status(200).json(mockComparison)
  } catch (error) {
    console.error('Error in currency comparison API:', error)
    res.status(500).json({ message: 'Internal server error' })
  }
} 