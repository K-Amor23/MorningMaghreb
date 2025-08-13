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

// Helper function to format volume
function formatVolume(volume: number): string {
  if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B MAD`;
  if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M MAD`;
  if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K MAD`;
  return `${volume.toFixed(0)} MAD`;
}

// Helper function to format market cap
function formatMarketCap(marketCap: number): string {
  if (marketCap >= 1e9) return `${(marketCap / 1e9).toFixed(1)}B MAD`;
  if (marketCap >= 1e6) return `${(marketCap / 1e6).toFixed(1)}M MAD`;
  return `${marketCap.toFixed(0)} MAD`;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { page = '1', limit = '20', ticker, sector, sort_by = 'market_cap_billion' } = req.query;

    // Load data sources
    let africanMarketsData = loadJsonData('apps/backend/data/cse_companies_african_markets.json') || [];
    const bourseData = loadJsonData('apps/backend/etl/casablanca_bourse_data_20250725_123947.json') || {};

    // In production on Vercel, the backend data file may not be present on the server filesystem.
    // Fall back to loading from the public data copy if needed.
    if (!africanMarketsData || africanMarketsData.length === 0) {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || ''
        const url = baseUrl ? `${baseUrl}/data/cse_companies_african_markets.json` : `${req.headers['x-forwarded-proto'] || 'https'}://${req.headers.host}/data/cse_companies_african_markets.json`
        const r = await fetch(url)
        if (r.ok) {
          africanMarketsData = await r.json()
        }
      } catch (e) {
        console.warn('Could not load public data fallback for african markets:', e)
      }
    }

    // Transform data into quotes format
    let quotes = africanMarketsData.map((company: any) => {
      const ticker = company.ticker?.toUpperCase();
      if (!ticker) return null;

      // Use actual change data if available, otherwise simulate
      const basePrice = company.price || 0;
      const changePercent = company.change_1d_percent || (Math.random() - 0.5) * 4; // Use real data or simulate
      const change = basePrice > 0 ? (changePercent / 100) * basePrice : 0;

      // Calculate volume based on market cap and price movement
      const volume = company.market_cap_billion ?
        (company.market_cap_billion * 1e9 * 0.01 * (0.5 + Math.abs(changePercent) / 10)) :
        (basePrice * 10000 * Math.random());

      return {
        ticker,
        name: company.name || company.company_name || '',
        price: basePrice,
        change: Math.round(change * 100) / 100,
        change_percent: Math.round(changePercent * 100) / 100,
        volume: Math.round(volume),
        volume_formatted: formatVolume(volume),
        market_cap: company.market_cap_billion ? company.market_cap_billion * 1e9 : 0,
        market_cap_formatted: company.market_cap_billion ? formatMarketCap(company.market_cap_billion * 1e9) : '',
        sector: company.sector || '',
        sector_group: company.sector_group || '',
        size_category: company.size_category || '',
        last_updated: company.last_updated || new Date().toISOString(),
        data_quality: company.price ? 'real' : 'generated'
      };
    }).filter(Boolean);

    // Apply filters
    if (ticker) {
      const tickerUpper = (ticker as string).toUpperCase();
      quotes = quotes.filter((quote: any) => quote.ticker === tickerUpper);
    }

    if (sector) {
      quotes = quotes.filter((quote: any) =>
        quote.sector?.toLowerCase().includes((sector as string).toLowerCase())
      );
    }

    // Apply sorting
    const sortBy = sort_by as string;
    quotes.sort((a: any, b: any) => {
      switch (sortBy) {
        case 'price':
          return b.price - a.price;
        case 'change_percent':
          // For change_percent, we want to show both gainers and losers
          // So we sort by absolute value to show biggest movers first
          return Math.abs(b.change_percent) - Math.abs(a.change_percent);
        case 'volume':
          return b.volume - a.volume;
        case 'market_cap':
          return b.market_cap - a.market_cap;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'ticker':
          return a.ticker.localeCompare(b.ticker);
        default:
          return b.market_cap - a.market_cap;
      }
    });

    // Apply pagination
    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const startIndex = (pageNum - 1) * limitNum;
    const endIndex = startIndex + limitNum;
    const paginatedQuotes = quotes.slice(startIndex, endIndex);

    // Calculate pagination metadata
    const totalQuotes = quotes.length;
    const totalPages = Math.ceil(totalQuotes / limitNum);
    const hasNextPage = pageNum < totalPages;
    const hasPrevPage = pageNum > 1;

    // Calculate market summary
    const totalMarketCap = quotes.reduce((sum: number, quote: any) => sum + quote.market_cap, 0);
    const positiveMovers = quotes.filter((quote: any) => quote.change_percent > 0).length;
    const negativeMovers = quotes.filter((quote: any) => quote.change_percent < 0).length;
    const unchanged = quotes.filter((quote: any) => quote.change_percent === 0).length;

    const response = {
      success: true,
      data: {
        quotes: paginatedQuotes,
        pagination: {
          page: pageNum,
          limit: limitNum,
          total: totalQuotes,
          total_pages: totalPages,
          has_next: hasNextPage,
          has_prev: hasPrevPage
        },
        market_summary: {
          total_companies: totalQuotes,
          total_market_cap: totalMarketCap,
          total_market_cap_formatted: formatMarketCap(totalMarketCap),
          positive_movers: positiveMovers,
          negative_movers: negativeMovers,
          unchanged,
          average_price: quotes.length > 0 ? quotes.reduce((sum: number, q: any) => sum + q.price, 0) / quotes.length : 0
        }
      },
      timestamp: new Date().toISOString()
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Quotes API error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}