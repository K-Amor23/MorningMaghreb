import { NextApiRequest, NextApiResponse } from 'next'

interface EarningsEvent {
  company: string
  ticker: string
  earnings_date: string
  estimate?: number
  actual?: number
  surprise?: number
  sector: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { start_date, end_date, companies } = req.body

    // Mock earnings data - in a real implementation, this would come from a database
    const mockEarnings: EarningsEvent[] = [
      {
        company: 'Attijariwafa Bank',
        ticker: 'ATW',
        earnings_date: '2024-11-15',
        estimate: 4.2,
        sector: 'Banking'
      },
      {
        company: 'Maroc Telecom',
        ticker: 'IAM',
        earnings_date: '2024-11-20',
        estimate: 1.8,
        sector: 'Telecommunications'
      },
      {
        company: 'Banque Centrale Populaire',
        ticker: 'BCP',
        earnings_date: '2024-11-25',
        estimate: 2.8,
        sector: 'Banking'
      },
      {
        company: 'BMCE Bank',
        ticker: 'BMCE',
        earnings_date: '2024-12-05',
        estimate: 1.5,
        sector: 'Banking'
      },
      {
        company: 'Wafa Assurance',
        ticker: 'WAA',
        earnings_date: '2024-12-10',
        estimate: 0.8,
        sector: 'Insurance'
      },
      {
        company: 'Ciments du Maroc',
        ticker: 'CMA',
        earnings_date: '2024-12-15',
        estimate: 2.1,
        sector: 'Construction Materials'
      }
    ]

    // Filter by date range
    let filteredEarnings = mockEarnings.filter(earning => {
      const earningsDate = new Date(earning.earnings_date)
      const startDate = new Date(start_date)
      const endDate = new Date(end_date)
      return earningsDate >= startDate && earningsDate <= endDate
    })

    // Filter by selected companies if provided
    if (companies && companies.length > 0) {
      filteredEarnings = filteredEarnings.filter(earning => 
        companies.includes(earning.ticker)
      )
    }

    // Sort by earnings date
    filteredEarnings.sort((a, b) => 
      new Date(a.earnings_date).getTime() - new Date(b.earnings_date).getTime()
    )

    res.status(200).json(filteredEarnings)
  } catch (error) {
    console.error('Error in earnings calendar API:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
} 