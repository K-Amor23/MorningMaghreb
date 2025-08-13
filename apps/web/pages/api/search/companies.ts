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
    const priority = ['IAM', 'ATW', 'BCP', 'GAZ', 'BMCI', 'CIH', 'ADD', 'SNEP']
    const suggested = priority
      .map((t) => all.find((c) => c.ticker === t))
      .filter(Boolean)
      .slice(0, 8)
  
    return res.status(200).json({ data: suggested })
  }

  const needle = q.toLowerCase()
  const filtered = all
    .filter((c) => c.ticker.toLowerCase().includes(needle) || c.name.toLowerCase().includes(needle))
    .slice(0, 12)
  return res.status(200).json({ data: filtered })
}