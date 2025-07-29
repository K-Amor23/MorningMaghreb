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
        const { type } = req.query;

        // Load data sources
        const africanMarketsData = loadJsonData('apps/backend/data/cse_companies_african_markets.json') || [];
        const bourseData = loadJsonData('apps/backend/etl/casablanca_bourse_data_20250725_123947.json') || {};

        // Calculate market summary
        const totalMarketCap = africanMarketsData.reduce((sum: number, company: any) => {
            return sum + (company.market_cap_billion ? company.market_cap_billion * 1e9 : 0);
        }, 0);

        const positiveMovers = africanMarketsData.filter((company: any) =>
            company.change_1d_percent && company.change_1d_percent > 0
        ).length;

        const negativeMovers = africanMarketsData.filter((company: any) =>
            company.change_1d_percent && company.change_1d_percent < 0
        ).length;

        const unchanged = africanMarketsData.filter((company: any) =>
            !company.change_1d_percent || company.change_1d_percent === 0
        ).length;

        // Create indices data (simulated for now)
        const indices = {
            MASI: {
                value: 12456.78,
                source: 'simulated'
            },
            MADEX: {
                value: 10234.56,
                source: 'simulated'
            },
            'MASI-ESG': {
                value: 987.65,
                source: 'simulated'
            }
        };

        // If bourse data has indices, use them
        if (bourseData.indices) {
            Object.assign(indices, bourseData.indices);
        }

        const marketSummary = {
            total_companies: africanMarketsData.length,
            total_market_cap: totalMarketCap,
            total_market_cap_formatted: formatMarketCap(totalMarketCap),
            positive_movers: positiveMovers,
            negative_movers: negativeMovers,
            unchanged: unchanged,
            average_price: africanMarketsData.length > 0 ?
                africanMarketsData.reduce((sum: number, company: any) => sum + (company.price || 0), 0) / africanMarketsData.length : 0
        };

        const response = {
            success: true,
            data: {
                indices,
                market_summary: marketSummary
            },
            timestamp: new Date().toISOString()
        };

        return res.status(200).json(response);
    } catch (error) {
        console.error('Unified market data API error:', error);
        return res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: error instanceof Error ? error.message : 'Unknown error'
        });
    }
} 