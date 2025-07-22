import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Read the African markets companies data
    const dataPath = path.join(process.cwd(), '../../apps/backend/data/cse_companies_african_markets_database.json')
    const fileContent = fs.readFileSync(dataPath, 'utf8')
    const data = JSON.parse(fileContent)

    // Extract companies array
    const companies = data.companies || []

    // Return the companies data
    return res.status(200).json(companies)

  } catch (error) {
    console.error('Error loading African markets companies:', error)
    
    // Return fallback data if file read fails
    const fallbackCompanies = [
      {
        ticker: 'AFM',
        name: 'AFMA',
        sector: 'Financials',
        price: 1105.0,
        change_1d_percent: -0.9,
        change_ytd_percent: 0.36,
        market_cap_billion: 1.1,
        size_category: 'Small Cap',
        sector_group: 'Financial Services'
      },
      {
        ticker: 'AFI',
        name: 'Afric Industries',
        sector: 'Industrials',
        price: 329.0,
        change_1d_percent: -0.26,
        change_ytd_percent: 8.24,
        market_cap_billion: 0.09,
        size_category: 'Micro Cap',
        sector_group: 'Industrials'
      },
      {
        ticker: 'GAZ',
        name: 'Afriquia Gaz',
        sector: 'Oil & Gas',
        price: 4400.0,
        change_1d_percent: 1.15,
        change_ytd_percent: 17.02,
        market_cap_billion: 15.12,
        size_category: 'Mid Cap',
        sector_group: 'Energy'
      },
      {
        ticker: 'ATW',
        name: 'Attijariwafa Bank',
        sector: 'Banking',
        price: 410.10,
        change_1d_percent: 0.31,
        change_ytd_percent: 5.25,
        market_cap_billion: 24.56,
        size_category: 'Large Cap',
        sector_group: 'Financial Services'
      },
      {
        ticker: 'IAM',
        name: 'Maroc Telecom',
        sector: 'Telecommunications',
        price: 156.30,
        change_1d_percent: -1.33,
        change_ytd_percent: -2.15,
        market_cap_billion: 15.68,
        size_category: 'Large Cap',
        sector_group: 'Telecommunications'
      }
    ]

    return res.status(200).json(fallbackCompanies)
  }
} 