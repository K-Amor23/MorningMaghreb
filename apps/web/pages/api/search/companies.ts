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

import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

// Helper function to load JSON data
function loadJsonData(filePath: string) {
  try {
    const possiblePaths = [
      path.join(process.cwd(), filePath),
      path.join(process.cwd(), '..', filePath),
      path.join(process.cwd(), '..', '..', filePath),
      path.join(process.cwd(), '..', '..', '..', filePath)
    ];

    for (const fullPath of possiblePaths) {
      if (fs.existsSync(fullPath)) {
        const data = fs.readFileSync(fullPath, 'utf8');
        return JSON.parse(data);
      }
    }
    return null;
  } catch (error) {
    console.error(`Error loading ${filePath}:`, error);
    return null;
  }
}

// Helper function to search companies
function searchCompanies(companies: any[], query: string, filters: any) {
  const searchTerm = query.toLowerCase();

  return companies.filter((company: any) => {
    // Text search
    const matchesSearch =
      company.ticker?.toLowerCase().includes(searchTerm) ||
      company.name?.toLowerCase().includes(searchTerm) ||
      company.company_name?.toLowerCase().includes(searchTerm) ||
      company.sector?.toLowerCase().includes(searchTerm) ||
      company.sector_group?.toLowerCase().includes(searchTerm);

    if (!matchesSearch) return false;

    // Apply filters
    if (filters.sector && company.sector !== filters.sector) return false;
    if (filters.size_category && company.size_category !== filters.size_category) return false;
    if (filters.has_price && !company.price) return false;
    if (filters.has_market_cap && !company.market_cap_billion) return false;

    return true;
  });
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      q = '',
      page = '1',
      limit = '20',
      sector,
      size_category,
      has_price,
      has_market_cap,
      sort_by = 'name'
    } = req.query;

    // Load data sources
    const africanMarketsData = loadJsonData('apps/backend/data/cse_companies_african_markets.json') || [];
    const bourseData = loadJsonData('apps/backend/etl/casablanca_bourse_data_20250725_123947.json') || {};

    // Transform and enrich company data
    let companies = africanMarketsData.map((company: any) => {
      const ticker = company.ticker?.toUpperCase();
      if (!ticker) return null;

      // Find matching bourse data
      let bourseInfo = null;
      if (bourseData.market_data_pages) {
        for (const page of bourseData.market_data_pages) {
          for (const table of page.tables || []) {
            for (const row of table.data || []) {
              if (row.Ticker?.toUpperCase() === ticker) {
                bourseInfo = row;
                break;
              }
            }
            if (bourseInfo) break;
          }
          if (bourseInfo) break;
        }
      }

      return {
        ticker,
        name: company.name || company.company_name || '',
        sector: company.sector || '',
        sector_group: company.sector_group || '',
        size_category: company.size_category || '',
        price: company.price || null,
        market_cap_billion: company.market_cap_billion || null,
        market_cap_formatted: company.market_cap_billion ? `${company.market_cap_billion}B MAD` : '',
        isin: company.isin || bourseInfo?.ISIN || '',
        compartment: bourseInfo?.Compartment || '',
        category: bourseInfo?.Catégorie || '',
        shares_outstanding: bourseInfo?.['Nombre de titres formant le capital'] || null,
        last_updated: company.last_updated || new Date().toISOString(),
        data_sources: ['african_markets', ...(bourseInfo ? ['casablanca_bourse'] : [])],
        data_quality: company.price ? 'real' : 'generated'
      };
    }).filter(Boolean);

    // Apply search and filters
    const filters = {
      sector: sector as string,
      size_category: size_category as string,
      has_price: has_price === 'true',
      has_market_cap: has_market_cap === 'true'
    };

    const searchResults = searchCompanies(companies, q as string, filters);

    // Apply sorting
    const sortBy = sort_by as string;
    searchResults.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'ticker':
          return a.ticker.localeCompare(b.ticker);
        case 'name':
          return a.name.localeCompare(b.name);
        case 'sector':
          return a.sector.localeCompare(b.sector);
        case 'price':
          return (b.price || 0) - (a.price || 0);
        case 'market_cap':
          return (b.market_cap_billion || 0) - (a.market_cap_billion || 0);
        case 'data_quality':
          return a.data_quality.localeCompare(b.data_quality);
        default:
          return a.name.localeCompare(b.name);
      }
    });

    // Apply pagination
    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const startIndex = (pageNum - 1) * limitNum;
    const endIndex = startIndex + limitNum;
    const paginatedResults = searchResults.slice(startIndex, endIndex);

    // Calculate pagination metadata
    const totalResults = searchResults.length;
    const totalPages = Math.ceil(totalResults / limitNum);
    const hasNextPage = pageNum < totalPages;
    const hasPrevPage = pageNum > 1;

    // Calculate search statistics
    const sectorDistribution = searchResults.reduce((acc: any, company: any) => {
      const sector = company.sector || 'Unknown';
      acc[sector] = (acc[sector] || 0) + 1;
      return acc;
    }, {});

    const sizeDistribution = searchResults.reduce((acc: any, company: any) => {
      const size = company.size_category || 'Unknown';
      acc[size] = (acc[size] || 0) + 1;
      return acc;
    }, {});

    const response = {
      success: true,
      data: {
        companies: paginatedResults,
        pagination: {
          page: pageNum,
          limit: limitNum,
          total: totalResults,
          total_pages: totalPages,
          has_next: hasNextPage,
          has_prev: hasPrevPage
        },
        search_metadata: {
          query: q,
          filters_applied: filters,
          total_results: totalResults,
          sector_distribution: sectorDistribution,
          size_distribution: sizeDistribution,
          companies_with_price: searchResults.filter((c: any) => c.price).length,
          companies_with_market_cap: searchResults.filter((c: any) => c.market_cap_billion).length
        }
      },
      timestamp: new Date().toISOString()
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Search API error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
} 