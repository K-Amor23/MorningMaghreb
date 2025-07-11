import type { NextApiRequest, NextApiResponse } from 'next'

interface CompanyComparisonRequest {
  companies: string[]
  metrics: string[]
}

interface CompanyComparisonResponse {
  companies: string[]
  metrics: string[]
  data: Record<string, any>
  comparison_chart_data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor: string
    }>
  }
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { companies, metrics }: CompanyComparisonRequest = req.body

    if (!companies || companies.length < 2 || companies.length > 3) {
      return res.status(400).json({ error: 'Must compare 2-3 companies' })
    }

    // Mock data for demonstration
    const comparisonData: Record<string, any> = {}
    const chartData = {
      labels: companies,
      datasets: [] as Array<{
        label: string
        data: number[]
        backgroundColor: string
      }>
    }

    companies.forEach((company, index) => {
      // Generate mock financial data
      comparisonData[company] = {
        revenue: 40000000000 + (index * 5000000000),
        net_income: 8000000000 + (index * 1000000000),
        roe: 15.0 + (index * 2),
        pe_ratio: 12.0 + (index * 1.5),
        debt_equity: 0.8 + (index * 0.1),
        market_cap: 100000000000 + (index * 20000000000),
        dividend_yield: 3.5 + (index * 0.5)
      }
    })

    // Prepare chart data for numeric metrics
    metrics.forEach((metric, index) => {
      if (['revenue', 'net_income', 'market_cap'].includes(metric)) {
        const values = companies.map(company => comparisonData[company][metric])
        chartData.datasets.push({
          label: metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
          data: values,
          backgroundColor: `rgba(${50 + index * 50}, ${100 + index * 30}, 255, 0.6)`
        })
      }
    })

    const response: CompanyComparisonResponse = {
      companies,
      metrics,
      data: comparisonData,
      comparison_chart_data: chartData
    }

    res.status(200).json(response)
  } catch (error) {
    console.error('Error in company comparison:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to compare companies'
    })
  }
} 