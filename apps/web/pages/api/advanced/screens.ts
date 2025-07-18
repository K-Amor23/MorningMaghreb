import type { NextApiRequest, NextApiResponse } from 'next'

interface CustomScreen {
  id: string
  name: string
  filters: Record<string, any>
  results: Array<{
    ticker: string
    name: string
    pe_ratio: number
    dividend_yield: number
    market_cap: number
    roe: number
  }>
  created_at: string
  last_run: string
}

// Mock data for development
const mockScreens: CustomScreen[] = [
  {
    id: 'screen_1',
    name: 'Value Stocks Screen',
    filters: { pe_ratio_max: 15, dividend_yield_min: 3.0 },
    results: [
      { ticker: 'ATW', name: 'Attijariwafa Bank', pe_ratio: 11.3, dividend_yield: 4.1, market_cap: 102000000000, roe: 19.4 },
      { ticker: 'WAA', name: 'Wafa Assurance', pe_ratio: 9.2, dividend_yield: 5.2, market_cap: 45000000000, roe: 15.8 },
      { ticker: 'CIH', name: 'CIH Bank', pe_ratio: 12.1, dividend_yield: 3.8, market_cap: 89000000000, roe: 16.2 }
    ],
    created_at: new Date().toISOString(),
    last_run: new Date().toISOString()
  },
  {
    id: 'screen_2',
    name: 'High Dividend Screen',
    filters: { dividend_yield_min: 4.0 },
    results: [
      { ticker: 'WAA', name: 'Wafa Assurance', pe_ratio: 9.2, dividend_yield: 5.2, market_cap: 45000000000, roe: 15.8 },
      { ticker: 'IAM', name: 'Maroc Telecom', pe_ratio: 14.2, dividend_yield: 4.6, market_cap: 98000000000, roe: 18.5 },
      { ticker: 'BMCE', name: 'BMCE Bank', pe_ratio: 13.8, dividend_yield: 4.2, market_cap: 75000000000, roe: 17.1 }
    ],
    created_at: new Date().toISOString(),
    last_run: new Date().toISOString()
  },
  {
    id: 'screen_3',
    name: 'Growth Stocks Screen',
    filters: { roe_min: 15, market_cap_min: 50000000000 },
    results: [
      { ticker: 'ATW', name: 'Attijariwafa Bank', pe_ratio: 11.3, dividend_yield: 4.1, market_cap: 102000000000, roe: 19.4 },
      { ticker: 'IAM', name: 'Maroc Telecom', pe_ratio: 14.2, dividend_yield: 4.6, market_cap: 98000000000, roe: 18.5 },
      { ticker: 'CIH', name: 'CIH Bank', pe_ratio: 12.1, dividend_yield: 3.8, market_cap: 89000000000, roe: 16.2 }
    ],
    created_at: new Date().toISOString(),
    last_run: new Date().toISOString()
  }
]

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<CustomScreen[] | CustomScreen | { error: string }>
) {
  if (req.method === 'GET') {
    // Return all screens
    res.status(200).json(mockScreens)
  } else if (req.method === 'POST') {
    // Create new screen
    try {
      const { name, filters, user_id } = req.body

      if (!name || !filters) {
        return res.status(400).json({ error: 'Name and filters are required' })
      }

      const newScreen: CustomScreen = {
        id: `screen_${Date.now()}`,
        name,
        filters,
        results: [
          // Mock results based on filters
          { ticker: 'ATW', name: 'Attijariwafa Bank', pe_ratio: 11.3, dividend_yield: 4.1, market_cap: 102000000000, roe: 19.4 },
          { ticker: 'WAA', name: 'Wafa Assurance', pe_ratio: 9.2, dividend_yield: 5.2, market_cap: 45000000000, roe: 15.8 }
        ],
        created_at: new Date().toISOString(),
        last_run: new Date().toISOString()
      }

      // In a real app, you would save this to the database
      mockScreens.push(newScreen)

      res.status(201).json(newScreen)
    } catch (error) {
      console.error('Error creating screen:', error)
      res.status(500).json({ error: 'Failed to create screen' })
    }
  } else if (req.method === 'DELETE') {
    // Delete screen
    try {
      const { id } = req.query

      if (!id) {
        return res.status(400).json({ error: 'Screen ID is required' })
      }

      const screenIndex = mockScreens.findIndex(screen => screen.id === id)
      
      if (screenIndex === -1) {
        return res.status(404).json({ error: 'Screen not found' })
      }

      mockScreens.splice(screenIndex, 1)
      res.status(200).json({ message: 'Screen deleted successfully' } as any)
    } catch (error) {
      console.error('Error deleting screen:', error)
      res.status(500).json({ error: 'Failed to delete screen' })
    }
  } else {
    res.setHeader('Allow', ['GET', 'POST', 'DELETE'])
    res.status(405).json({ error: `Method ${req.method} Not Allowed` })
  }
} 