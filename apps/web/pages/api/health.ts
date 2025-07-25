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

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        res.setHeader('Allow', ['GET']);
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Check data sources
        const africanMarketsData = loadJsonData('apps/backend/data/cse_companies_african_markets.json');
        const bourseData = loadJsonData('apps/backend/etl/casablanca_bourse_data_20250725_123947.json');

        // Calculate data quality metrics
        const totalCompanies = africanMarketsData?.length || 0;
        const companiesWithPrice = africanMarketsData?.filter((c: any) => c.price != null).length || 0;
        const companiesWithMarketCap = africanMarketsData?.filter((c: any) => c.market_cap_billion != null).length || 0;

        const dataQuality = {
            total_companies: totalCompanies,
            companies_with_price: companiesWithPrice,
            companies_with_market_cap: companiesWithMarketCap,
            price_coverage: totalCompanies > 0 ? Math.round((companiesWithPrice / totalCompanies) * 100) : 0,
            market_cap_coverage: totalCompanies > 0 ? Math.round((companiesWithMarketCap / totalCompanies) * 100) : 0
        };

        // Check system status
        const systemStatus = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            memory_usage: process.memoryUsage(),
            data_sources: {
                african_markets: africanMarketsData ? 'available' : 'unavailable',
                casablanca_bourse: bourseData ? 'available' : 'unavailable'
            },
            data_quality: dataQuality,
            version: '2.0.0',
            environment: process.env.NODE_ENV || 'development'
        };

        return res.status(200).json(systemStatus);
    } catch (error) {
        console.error('Health check error:', error);
        return res.status(500).json({
            status: 'unhealthy',
            error: 'Internal server error',
            timestamp: new Date().toISOString()
        });
    }
} 