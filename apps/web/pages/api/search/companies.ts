import type { NextApiRequest, NextApiResponse } from 'next'
import { createClient } from '@supabase/supabase-js'

type Company = {
  ticker: string
  name: string
  sector?: string
}

async function loadPublicCompanies(req: NextApiRequest): Promise<Company[]> {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || `${req.headers['x-forwarded-proto'] || 'https'}://${req.headers.host}`
    const url = `${baseUrl}/data/cse_companies_african_markets.json`
    const r = await fetch(url)
    if (!r.ok) return []
    const raw = await r.json()
    return (raw as any[])
      .filter((c) => c?.ticker)
      .map((c) => ({ ticker: String(c.ticker).toUpperCase(), name: c.name || c.company_name || '', sector: c.sector }))
  } catch {
    return []
  }
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const q = (req.query.q as string | undefined)?.trim() || ''
  const suggest = req.query.suggest === '1' || req.query.suggest === 'true'

  // Try Supabase first (server-side admin client)
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY

  try {
    if (url && key) {
      const sb = createClient(url, key, { auth: { persistSession: false } })
      if (suggest || !q) {
        // popular suggestions by market cap or predefined list if table lacks column
        const { data, error } = await sb
          .from('companies')
          .select('ticker,name,sector,market_cap')
          .order('market_cap', { ascending: false })
          .limit(8)
        if (!error && data) {
          const items = data.map((d: any) => ({ ticker: d.ticker, name: d.name, sector: d.sector }))
          return res.status(200).json({ data: items })
        }
      } else {
        const like = `%${q}%`
        const { data, error } = await sb
          .from('companies')
          .select('ticker,name,sector')
          .or(`ticker.ilike.${like},name.ilike.${like}`)
          .limit(12)
        if (!error && data) {
          return res.status(200).json({ data })
        }
      }
    }
  } catch {}

  // Fallback to public JSON
  const all = await loadPublicCompanies(req)
  if (suggest || !q) {
    // simple top suggestions by a static priority list
    const priority = ['IAM', 'ATW', 'BCP', 'GAZ', 'BMCI', 'CIH', 'ADD', 'SNEP', 'WAA']
    const suggested = priority
      .map((t) => all.find((c) => c.ticker === t))
      .filter(Boolean)
      .slice(0, 8)
  
    return res.status(200).json({ data: suggested })
  }

  const needle = q.toLowerCase()
  
  // Improved search algorithm with better scoring
  const filtered = all
    .map(company => {
      const tickerMatch = company.ticker.toLowerCase()
      const nameMatch = company.name.toLowerCase()
      
      let score = 0
      
      // Exact ticker match gets highest score
      if (tickerMatch === needle) score += 100
      // Ticker starts with query gets high score
      else if (tickerMatch.startsWith(needle)) score += 50
      // Ticker contains query gets medium score
      else if (tickerMatch.includes(needle)) score += 30
      
      // Exact name match gets high score
      if (nameMatch === needle) score += 80
      // Name starts with query gets medium-high score
      else if (nameMatch.startsWith(needle)) score += 40
      // Name contains query gets medium score
      else if (nameMatch.includes(needle)) score += 25
      
      // Word boundary matches get bonus
      const nameWords = nameMatch.split(/\s+/)
      nameWords.forEach(word => {
        if (word.startsWith(needle)) score += 15
        if (word.includes(needle)) score += 10
      })
      
      return { ...company, score }
    })
    .filter(company => company.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 12)
    .map(({ score, ...company }) => company) // Remove score from final result

  return res.status(200).json({ data: filtered })
}