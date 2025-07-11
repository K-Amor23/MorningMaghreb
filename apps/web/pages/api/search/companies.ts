import type { NextApiRequest, NextApiResponse } from 'next'

// Mock company data - in real app, this would come from database
const mockCompanies = [
  { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banks' },
  { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications' },
  { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banks' },
  { ticker: 'BMCE', name: 'BMCE Bank', sector: 'Banks' },
  { ticker: 'ONA', name: 'Omnium Nord Africain', sector: 'Conglomerates' },
  { ticker: 'MASI', name: 'MASI Index', sector: 'Index' },
  { ticker: 'MADEX', name: 'MADEX Index', sector: 'Index' },
  { ticker: 'MASI-ESG', name: 'MASI ESG Index', sector: 'Index' },
  { ticker: 'CIH', name: 'CIH Bank', sector: 'Banks' },
  { ticker: 'WAA', name: 'Wafa Assurance', sector: 'Insurance' },
  { ticker: 'CMA', name: 'Ciments du Maroc', sector: 'Construction Materials' },
  { ticker: 'LES', name: 'Lesieur Cristal', sector: 'Consumer Goods' },
  { ticker: 'SOT', name: 'SOTHEMA', sector: 'Pharmaceuticals' },
  { ticker: 'TMA', name: 'Taqa Morocco', sector: 'Utilities' },
  { ticker: 'COL', name: 'Colorado', sector: 'Real Estate' },
  { ticker: 'DRI', name: 'Dari Couspate', sector: 'Consumer Goods' },
  { ticker: 'FBR', name: 'Fenêtre Bab Rbat', sector: 'Construction' },
  { ticker: 'JET', name: 'Jet Contractors', sector: 'Construction' },
  { ticker: 'LBV', name: 'Label\'Vie', sector: 'Retail' },
  { ticker: 'MNG', name: 'Managem', sector: 'Mining' },
  { ticker: 'MUT', name: 'Mutandis', sector: 'Consumer Goods' },
  { ticker: 'SID', name: 'SOMACA', sector: 'Automotive' },
  { ticker: 'SNP', name: 'SNEP', sector: 'Oil & Gas' },
  { ticker: 'SOT', name: 'SOTHEMA', sector: 'Pharmaceuticals' },
  { ticker: 'TMA', name: 'Taqa Morocco', sector: 'Utilities' },
  { ticker: 'TMA', name: 'Taqa Morocco', sector: 'Utilities' },
  { ticker: 'WAA', name: 'Wafa Assurance', sector: 'Insurance' },
]

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { q: query } = req.query

    if (!query || typeof query !== 'string') {
      return res.status(200).json({
        success: true,
        data: [],
        total: 0
      })
    }

    // Filter companies based on query
    const filteredCompanies = mockCompanies.filter(company =>
      company.ticker.toLowerCase().includes(query.toLowerCase()) ||
      company.name.toLowerCase().includes(query.toLowerCase()) ||
      (company.sector && company.sector.toLowerCase().includes(query.toLowerCase()))
    )

    // Limit results to 10 for performance
    const limitedResults = filteredCompanies.slice(0, 10)

    res.status(200).json({
      success: true,
      data: limitedResults,
      total: filteredCompanies.length,
      query: query
    })
  } catch (error) {
    console.error('Error searching companies:', error)
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to search companies'
    })
  }
} 