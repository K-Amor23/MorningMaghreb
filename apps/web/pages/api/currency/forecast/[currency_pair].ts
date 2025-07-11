import type { NextApiRequest, NextApiResponse } from 'next'

interface ForecastPrediction {
  date: string
  predicted_rate: number
  confidence_interval: [number, number]
  trend: 'up' | 'down' | 'stable'
}

interface ForecastResponse {
  currency_pair: string
  forecast_date: string
  predictions: ForecastPrediction[]
  confidence: number
  model_version: string
  factors: string[]
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ForecastResponse | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { currency_pair } = req.query
    const days = req.query.days ? parseInt(req.query.days as string) : 3

    // In production, this would call the backend API with ML model
    // For now, return mock forecast data
    const baseRate = 10.25
    const predictions: ForecastPrediction[] = []
    const today = new Date()

    for (let i = 1; i <= days; i++) {
      const date = new Date(today)
      date.setDate(date.getDate() + i)
      
      // Simple trend prediction
      const trend = i % 2 === 0 ? 0.01 : -0.005
      const predictedRate = baseRate + trend * i
      
      predictions.push({
        date: date.toISOString().split('T')[0],
        predicted_rate: predictedRate,
        confidence_interval: [predictedRate - 0.02, predictedRate + 0.02],
        trend: trend > 0 ? 'up' : trend < 0 ? 'down' : 'stable'
      })
    }

    const forecast: ForecastResponse = {
      currency_pair: currency_pair as string,
      forecast_date: today.toISOString().split('T')[0],
      predictions,
      confidence: 0.78,
      model_version: 'v1.0',
      factors: [
        'BAM policy rate stability',
        'USD strength index',
        'Moroccan trade balance',
        'Global market sentiment',
        'Oil price fluctuations',
        'Tourism seasonality'
      ]
    }

    res.status(200).json(forecast)
  } catch (error) {
    console.error('Error generating AI forecast:', error)
    res.status(500).json({ error: 'Failed to generate forecast' })
  }
} 