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
    const currency_pair = (req.query.currency_pair as string) || 'USD/MAD'
    const amount = parseFloat(req.query.amount as string) || 1000

    // Call backend FastAPI to get real data
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000'
    const url = `${backendUrl}/currency/compare/${encodeURIComponent(currency_pair)}?amount=${amount}`
    const r = await fetch(url)
    if (!r.ok) {
      throw new Error(`Backend error ${r.status}`)
    }
    const data = await r.json()
    res.status(200).json(data as CurrencyComparison)
  } catch (error) {
    console.error('Error in currency comparison API:', error)
    res.status(500).json({ message: 'Internal server error' })
  }
} 