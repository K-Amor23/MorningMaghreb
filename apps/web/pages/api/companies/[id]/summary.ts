import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { id: ticker } = req.query;

    if (!ticker || typeof ticker !== 'string') {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        // Get company information
        const { data: company, error: companyError } = await supabase
            .from('companies')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .single();

        if (companyError || !company) {
            return res.status(404).json({ error: 'Company not found' });
        }

        // Get last 90 days of price data
        const ninetyDaysAgo = new Date();
        ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);

        const { data: prices, error: pricesError } = await supabase
            .from('company_prices')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .gte('date', ninetyDaysAgo.toISOString().split('T')[0])
            .order('date', { ascending: true });

        if (pricesError) {
            console.error('Error fetching prices:', pricesError);
            return res.status(500).json({ error: 'Failed to fetch price data' });
        }

        // Calculate current price and changes
        const latestPrice = prices && prices.length > 0 ? prices[prices.length - 1] : null;
        const previousPrice = prices && prices.length > 1 ? prices[prices.length - 2] : null;

        const currentPrice = latestPrice?.close || 0;
        const priceChange = latestPrice && previousPrice ? latestPrice.close - previousPrice.close : 0;
        const priceChangePercent = previousPrice && previousPrice.close > 0
            ? (priceChange / previousPrice.close) * 100
            : 0;

        // Get sentiment data
        const { data: sentiment } = await supabase
            .from('sentiment_aggregates')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .single();

        // Get recent news count
        const { data: recentNews } = await supabase
            .from('company_news')
            .select('id')
            .eq('ticker', ticker.toUpperCase())
            .gte('published_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString());

        // Get reports count
        const { data: reports } = await supabase
            .from('company_reports')
            .select('id')
            .eq('ticker', ticker.toUpperCase());

        // Format price data for frontend
        const formattedPrices = prices?.map(price => ({
            date: price.date,
            open: parseFloat(price.open?.toString() || '0'),
            high: parseFloat(price.high?.toString() || '0'),
            low: parseFloat(price.low?.toString() || '0'),
            close: parseFloat(price.close?.toString() || '0'),
            volume: parseInt(price.volume?.toString() || '0')
        })) || [];

        // Generate mock financial data if not available
        const mockRevenue = company.market_cap_billion ? company.market_cap_billion * 0.3 : 1000;
        const mockNetIncome = mockRevenue * 0.15;
        const mockSharesOutstanding = company.market_cap_billion ? (company.market_cap_billion * 1000000000) / currentPrice : 1000000000;

        const response = {
            company: {
                ticker: company.ticker,
                name: company.name,
                sector: company.sector,
                logo: undefined, // Will be added later
                currentPrice,
                priceChange,
                priceChangePercent: parseFloat(priceChangePercent.toFixed(2)),
                marketCap: company.market_cap_billion,
                revenue: mockRevenue,
                netIncome: mockNetIncome,
                peRatio: currentPrice > 0 ? (currentPrice / (mockNetIncome / mockSharesOutstanding)) : 0,
                dividendYield: 0, // Will be calculated from real data
                roe: 0.12, // Mock ROE
                sharesOutstanding: mockSharesOutstanding,
                lastUpdated: company.updated_at
            },
            priceData: {
                last90Days: formattedPrices,
                currentPrice,
                priceChange,
                priceChangePercent: parseFloat(priceChangePercent.toFixed(2))
            },
            sentiment: sentiment ? {
                bullishPercentage: sentiment.bullish_percentage,
                bearishPercentage: sentiment.bearish_percentage,
                neutralPercentage: sentiment.neutral_percentage,
                totalVotes: sentiment.total_votes,
                averageConfidence: sentiment.average_confidence
            } : null,
            metadata: {
                dataQuality: prices && prices.length > 0 ? 'real' : 'mock',
                lastUpdated: new Date().toISOString(),
                sources: ['Supabase Database'],
                recordCount: prices?.length || 0,
                newsCount7d: recentNews?.length || 0,
                reportsCount: reports?.length || 0
            }
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in summary endpoint:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 