import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    try {
        const { method, query } = req;

        switch (method) {
            case 'GET':
                const { type, ticker, sector, limit, sort_by } = query;

                switch (type) {
                    case 'all-companies':
                        const { data: companies, error: companiesError } = await supabase
                            .from('cse_companies')
                            .select('*')
                            .order('ticker');

                        if (companiesError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch companies from Supabase',
                                details: companiesError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: companies,
                            count: companies?.length || 0,
                            timestamp: new Date().toISOString()
                        });

                    case 'company':
                        if (!ticker) {
                            return res.status(400).json({
                                success: false,
                                error: 'Ticker parameter is required'
                            });
                        }

                        const { data: company, error: companyError } = await supabase
                            .from('cse_companies')
                            .select('*')
                            .eq('ticker', (ticker as string).toUpperCase())
                            .single();

                        if (companyError) {
                            return res.status(404).json({
                                success: false,
                                error: `Company with ticker ${ticker} not found`,
                                details: companyError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: company,
                            timestamp: new Date().toISOString()
                        });

                    case 'market-data':
                        const { data: marketData, error: marketDataError } = await supabase
                            .from('market_data')
                            .select('*')
                            .order('timestamp', { ascending: false });

                        if (marketDataError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch market data from Supabase',
                                details: marketDataError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: marketData,
                            count: marketData?.length || 0,
                            timestamp: new Date().toISOString()
                        });

                    case 'company-market-data':
                        if (!ticker) {
                            return res.status(400).json({
                                success: false,
                                error: 'Ticker parameter is required'
                            });
                        }

                        const { data: companyMarketData, error: companyMarketDataError } = await supabase
                            .from('market_data')
                            .select('*')
                            .eq('ticker', (ticker as string).toUpperCase())
                            .order('timestamp', { ascending: false })
                            .limit(30); // Last 30 data points

                        if (companyMarketDataError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch company market data from Supabase',
                                details: companyMarketDataError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: companyMarketData,
                            count: companyMarketData?.length || 0,
                            timestamp: new Date().toISOString()
                        });

                    case 'sector':
                        if (!sector) {
                            return res.status(400).json({
                                success: false,
                                error: 'Sector parameter is required'
                            });
                        }

                        const { data: sectorCompanies, error: sectorError } = await supabase
                            .from('cse_companies')
                            .select('*')
                            .eq('sector', sector)
                            .order('ticker');

                        if (sectorError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch sector companies from Supabase',
                                details: sectorError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: sectorCompanies,
                            count: sectorCompanies?.length || 0,
                            sector: sector,
                            timestamp: new Date().toISOString()
                        });

                    case 'top-companies':
                        const topLimit = limit ? parseInt(limit as string) : 10;
                        const sortBy = sort_by ? (sort_by as string) : 'market_cap';

                        // Get companies with market data
                        const { data: topCompaniesData, error: topCompaniesError } = await supabase
                            .from('market_data')
                            .select(`
                ticker,
                price,
                market_cap,
                change_percent,
                timestamp,
                cse_companies!inner(name, sector)
              `)
                            .order(sortBy, { ascending: false })
                            .limit(topLimit);

                        if (topCompaniesError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch top companies from Supabase',
                                details: topCompaniesError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: topCompaniesData,
                            count: topCompaniesData?.length || 0,
                            sort_by: sortBy,
                            limit: topLimit,
                            timestamp: new Date().toISOString()
                        });

                    case 'market-summary':
                        // Get latest market data for summary
                        const { data: latestMarketData, error: summaryError } = await supabase
                            .from('market_data')
                            .select('*')
                            .order('timestamp', { ascending: false });

                        if (summaryError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch market summary from Supabase',
                                details: summaryError.message
                            });
                        }

                        // Calculate summary statistics
                        const summary = calculateMarketSummary(latestMarketData || []);

                        return res.status(200).json({
                            success: true,
                            data: summary,
                            timestamp: new Date().toISOString()
                        });

                    case 'data-quality':
                        // Get data quality metrics
                        const { data: allCompanies, error: qualityError } = await supabase
                            .from('cse_companies')
                            .select('*');

                        if (qualityError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch data quality metrics from Supabase',
                                details: qualityError.message
                            });
                        }

                        const qualityMetrics = calculateDataQuality(allCompanies || []);

                        return res.status(200).json({
                            success: true,
                            data: qualityMetrics,
                            timestamp: new Date().toISOString()
                        });

                    default:
                        // Return overview of available data
                        const { data: overviewData, error: overviewError } = await supabase
                            .from('cse_companies')
                            .select('count');

                        if (overviewError) {
                            return res.status(500).json({
                                success: false,
                                error: 'Failed to fetch overview from Supabase',
                                details: overviewError.message
                            });
                        }

                        return res.status(200).json({
                            success: true,
                            data: {
                                companies_count: overviewData?.[0]?.count || 0,
                                available_endpoints: [
                                    'all-companies',
                                    'company',
                                    'market-data',
                                    'company-market-data',
                                    'sector',
                                    'top-companies',
                                    'market-summary',
                                    'data-quality'
                                ]
                            },
                            timestamp: new Date().toISOString()
                        });
                }

            default:
                res.setHeader('Allow', ['GET']);
                return res.status(405).json({
                    success: false,
                    error: `Method ${method} Not Allowed`
                });
        }
    } catch (error) {
        console.error('Supabase API Error:', error);
        return res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        });
    }
}

// Helper function to calculate market summary
function calculateMarketSummary(marketData: any[]): any {
    if (marketData.length === 0) {
        return {
            total_companies: 0,
            total_market_cap: 0,
            average_price: 0,
            price_range: { min: 0, max: 0 },
            last_updated: new Date().toISOString()
        };
    }

    const prices = marketData.map(d => d.price).filter(p => p != null);
    const marketCaps = marketData.map(d => d.market_cap).filter(m => m != null);

    return {
        total_companies: marketData.length,
        total_market_cap: marketCaps.reduce((sum, cap) => sum + cap, 0),
        average_price: prices.reduce((sum, price) => sum + price, 0) / prices.length,
        price_range: {
            min: Math.min(...prices),
            max: Math.max(...prices)
        },
        last_updated: new Date().toISOString()
    };
}

// Helper function to calculate data quality
function calculateDataQuality(companies: any[]): any {
    if (companies.length === 0) {
        return {
            total_companies: 0,
            completeness_score: 0,
            data_sources: {}
        };
    }

    const totalCompanies = companies.length;
    const companiesWithMetadata = companies.filter(c => c.metadata);

    // Calculate completeness based on metadata
    const completenessScores = companiesWithMetadata.map(c => {
        const metadata = c.metadata;
        const sources = metadata.data_sources || [];
        return sources.length > 0 ? 1 : 0.5;
    });

    const avgCompleteness = completenessScores.reduce((sum, score) => sum + score, 0) / completenessScores.length;

    return {
        total_companies: totalCompanies,
        completeness_score: avgCompleteness,
        companies_with_metadata: companiesWithMetadata.length,
        last_updated: new Date().toISOString()
    };
} 