import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

// Helper function to load JSON data
function loadJsonData(filePath: string) {
    try {
        // Try multiple possible paths
        const possiblePaths = [
            path.join(process.cwd(), filePath),
            path.join(process.cwd(), '..', filePath),
            path.join(process.cwd(), '..', '..', filePath),
            path.join(process.cwd(), '..', '..', '..', filePath)
        ];

        for (const fullPath of possiblePaths) {
            if (fs.existsSync(fullPath)) {
                console.log(`Found file at: ${fullPath}`);
                const data = fs.readFileSync(fullPath, 'utf8');
                return JSON.parse(data);
            }
        }

        console.log(`File not found at any of these paths:`, possiblePaths);
        return null;
    } catch (error) {
        console.error(`Error loading ${filePath}:`, error);
        return null;
    }
}

// Helper function to combine data sources
function combineDataSources() {
    // Load African Markets data
    const africanMarketsData = loadJsonData('apps/backend/data/cse_companies_african_markets.json') || [];

    // Load Bourse data
    const bourseData = loadJsonData('apps/backend/etl/casablanca_bourse_data_20250725_123947.json') || {};

    // Create combined structure
    const combined: any = {
        metadata: {
            combined_at: new Date().toISOString(),
            sources: ['African Markets', 'Casablanca Bourse'],
            total_companies: 0,
            data_quality: {}
        },
        companies: {},
        indices: {},
        market_summary: {}
    };

    // Process African Markets data
    for (const company of africanMarketsData) {
        const ticker = company.ticker?.toUpperCase();
        if (ticker) {
            combined.companies[ticker] = {
                african_markets: company,
                data_sources: ['african_markets'],
                last_updated: company.last_updated,
                completeness_score: calculateCompletenessScore(company)
            };
        }
    }

    // Process Bourse data
    if (bourseData.market_data_pages) {
        // Extract indices
        for (const page of bourseData.market_data_pages) {
            for (const table of page.tables || []) {
                for (const row of table.data || []) {
                    if (row.MASI) {
                        combined.indices[Object.keys(row)[0]] = {
                            value: Object.values(row)[0],
                            source: 'casablanca_bourse'
                        };
                    }
                }
            }
        }

        // Extract company data from Bourse tables
        for (const page of bourseData.market_data_pages) {
            for (const table of page.tables || []) {
                for (const row of table.data || []) {
                    if (row.Ticker) {
                        const ticker = row.Ticker.toUpperCase();
                        if (!combined.companies[ticker]) {
                            combined.companies[ticker] = {
                                bourse_data: row,
                                data_sources: ['casablanca_bourse'],
                                completeness_score: 0.3
                            };
                        } else {
                            combined.companies[ticker].bourse_data = row;
                            combined.companies[ticker].data_sources.push('casablanca_bourse');
                        }
                    }
                }
            }
        }
    }

    // Calculate totals and create market summary
    combined.metadata.total_companies = Object.keys(combined.companies).length;
    combined.metadata.data_quality = calculateDataQuality(combined.companies);
    combined.market_summary = createMarketSummary(combined.companies);

    return combined;
}

function calculateCompletenessScore(company: any): number {
    const requiredFields = ['ticker', 'name', 'sector', 'price', 'market_cap_billion'];
    const optionalFields = ['change_1d_percent', 'change_ytd_percent', 'size_category', 'sector_group'];

    let score = 0.0;

    // Required fields (weighted more heavily)
    for (const field of requiredFields) {
        if (company[field] != null) {
            score += 0.8 / requiredFields.length;
        }
    }

    // Optional fields
    for (const field of optionalFields) {
        if (company[field] != null) {
            score += 0.2 / optionalFields.length;
        }
    }

    return Math.min(score, 1.0);
}

function calculateDataQuality(companies: any): any {
    const totalCompanies = Object.keys(companies).length;
    if (totalCompanies === 0) return {};

    const completenessScores = Object.values(companies).map((c: any) => c.completeness_score || 0);
    const avgCompleteness = completenessScores.reduce((a: number, b: number) => a + b, 0) / completenessScores.length;

    const sourceCounts: any = {};
    for (const company of Object.values(companies)) {
        for (const source of (company as any).data_sources || []) {
            sourceCounts[source] = (sourceCounts[source] || 0) + 1;
        }
    }

    return {
        total_companies: totalCompanies,
        average_completeness: Math.round(avgCompleteness * 1000) / 1000,
        companies_with_price_data: Object.values(companies).filter((c: any) => c.african_markets?.price).length,
        companies_with_market_cap: Object.values(companies).filter((c: any) => c.african_markets?.market_cap_billion).length,
        source_coverage: sourceCounts
    };
}

function createMarketSummary(companies: any): any {
    if (Object.keys(companies).length === 0) return {};

    const prices: number[] = [];
    const marketCaps: number[] = [];
    const sectors: any = {};

    for (const company of Object.values(companies)) {
        const africanData = (company as any).african_markets;

        if (africanData?.price) {
            prices.push(africanData.price);
        }

        if (africanData?.market_cap_billion) {
            marketCaps.push(africanData.market_cap_billion);
        }

        const sector = africanData?.sector;
        if (sector) {
            sectors[sector] = (sectors[sector] || 0) + 1;
        }
    }

    return {
        total_companies: Object.keys(companies).length,
        total_market_cap: marketCaps.length > 0 ? marketCaps.reduce((a, b) => a + b, 0) : null,
        average_price: prices.length > 0 ? prices.reduce((a, b) => a + b, 0) / prices.length : null,
        price_range: {
            min: prices.length > 0 ? Math.min(...prices) : null,
            max: prices.length > 0 ? Math.max(...prices) : null
        },
        sector_distribution: sectors,
        last_updated: new Date().toISOString()
    };
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    try {
        const { method, query } = req;

        switch (method) {
            case 'GET':
                const { type, ticker, sector, limit, sort_by } = query;
                const combinedData = combineDataSources();

                switch (type) {
                    case 'all-companies':
                        const companies = Object.values(combinedData.companies);
                        return res.status(200).json({
                            success: true,
                            data: companies,
                            count: companies.length,
                            timestamp: new Date().toISOString()
                        });

                    case 'company':
                        if (!ticker) {
                            return res.status(400).json({
                                success: false,
                                error: 'Ticker parameter is required'
                            });
                        }
                        const company = combinedData.companies[(ticker as string).toUpperCase()];
                        if (!company) {
                            return res.status(404).json({
                                success: false,
                                error: `Company with ticker ${ticker} not found`
                            });
                        }
                        return res.status(200).json({
                            success: true,
                            data: company,
                            timestamp: new Date().toISOString()
                        });

                    case 'market-summary':
                        return res.status(200).json({
                            success: true,
                            data: combinedData.market_summary,
                            timestamp: new Date().toISOString()
                        });

                    case 'indices':
                        return res.status(200).json({
                            success: true,
                            data: combinedData.indices,
                            timestamp: new Date().toISOString()
                        });

                    case 'data-quality':
                        return res.status(200).json({
                            success: true,
                            data: {
                                metadata: combinedData.metadata,
                                quality_metrics: combinedData.metadata.data_quality,
                                last_updated: new Date().toISOString()
                            },
                            timestamp: new Date().toISOString()
                        });

                    case 'top-companies':
                        const topLimit = limit ? parseInt(limit as string) : 10;
                        const sortBy = sort_by ? (sort_by as string) : 'market_cap_billion';
                        const companiesList = Object.values(combinedData.companies);
                        const sortedCompanies = companiesList
                            .filter((c: any) => c.african_markets?.[sortBy] != null)
                            .sort((a: any, b: any) => (b.african_markets?.[sortBy] || 0) - (a.african_markets?.[sortBy] || 0))
                            .slice(0, topLimit);

                        return res.status(200).json({
                            success: true,
                            data: sortedCompanies,
                            count: sortedCompanies.length,
                            sort_by: sortBy,
                            limit: topLimit,
                            timestamp: new Date().toISOString()
                        });

                    default:
                        // Return all available data types
                        return res.status(200).json({
                            success: true,
                            data: {
                                companies: Object.values(combinedData.companies),
                                market_summary: combinedData.market_summary,
                                indices: combinedData.indices,
                                data_quality: combinedData.metadata.data_quality
                            },
                            count: Object.keys(combinedData.companies).length,
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
        console.error('API Error:', error);
        return res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        });
    }
} 