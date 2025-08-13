import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

type Company = {
  ticker?: string
  name?: string
  company_name?: string
  price?: number
  change_1d_percent?: number
  market_cap_billion?: number
  sector?: string
  sector_group?: string
  size_category?: string
  last_updated?: string
}

function loadJsonData(filePath: string) {
  try {
    const possiblePaths = [
      path.join(process.cwd(), filePath),
      path.join(process.cwd(), '..', filePath),
      path.join(process.cwd(), '..', '..', filePath),
      path.join(process.cwd(), '..', '..', '..', filePath)
    ]

    for (const fullPath of possiblePaths) {
      if (fs.existsSync(fullPath)) {
        const data = fs.readFileSync(fullPath, 'utf8')
        return JSON.parse(data)
      }
    }
    return null
  } catch (error) {
    console.error(`Error loading ${filePath}:`, error)
    return null
  }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET'])
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Load primary dataset
    let companies: Company[] = loadJsonData('apps/backend/data/cse_companies_african_markets.json') || []

    // Fallback to public data file in production deployments
    if (!companies || companies.length === 0) {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || ''
        const url = baseUrl
          ? `${baseUrl}/data/cse_companies_african_markets.json`
          : `${req.headers['x-forwarded-proto'] || 'https'}://${req.headers.host}/data/cse_companies_african_markets.json`
        const r = await fetch(url)
        if (r.ok) {
          companies = await r.json()
        }
      } catch (e) {
        console.warn('Movers API: public data fallback failed:', e)
      }
    }

    const normalized = (companies || []).map((c) => {
      const price = typeof c.price === 'number' ? c.price : 0
      let changePercent = typeof c.change_1d_percent === 'number' ? c.change_1d_percent : 0
      if (Number.isNaN(changePercent)) changePercent = 0
      return {
        ticker: (c.ticker || '').toUpperCase(),
        name: c.name || c.company_name || '',
        price,
        change_percent: Math.round(changePercent * 100) / 100,
        market_cap: c.market_cap_billion ? c.market_cap_billion * 1e9 : 0,
        sector: c.sector || '',
        last_updated: c.last_updated || null,
      }
    }).filter((c) => c.ticker)

    // Compute global top 5 gainers/losers by daily change percent
    const gainers = normalized
      .filter((q) => q.change_percent > 0)
      .sort((a, b) => b.change_percent - a.change_percent)
      .slice(0, 5)

    const losers = normalized
      .filter((q) => q.change_percent < 0)
      .sort((a, b) => a.change_percent - b.change_percent)
      .slice(0, 5)

    // Cache at the CDN for 10 minutes
    res.setHeader('Cache-Control', 's-maxage=600, stale-while-revalidate=60')

    return res.status(200).json({
      success: true,
      data: {
        top_gainers: gainers,
        top_losers: losers,
        total_companies: normalized.length,
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Movers API error:', error)
    return res.status(500).json({ success: false, error: 'Internal server error' })
  }
}


