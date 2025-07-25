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

    const { ticker } = req.query;

    try {
        if (ticker && typeof ticker === 'string') {
            // Get data quality for specific company
            const { data: company, error: companyError } = await supabase
                .from('companies')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .single();

            if (companyError || !company) {
                return res.status(404).json({ error: 'Company not found' });
            }

            // Get detailed data quality metrics
            const { data: ohlcvData } = await supabase
                .from('company_prices')
                .select('date')
                .eq('ticker', ticker.toUpperCase())
                .order('date', { ascending: false });

            const { data: reportsData } = await supabase
                .from('company_reports')
                .select('report_date, report_type')
                .eq('ticker', ticker.toUpperCase())
                .order('report_date', { ascending: false });

            const { data: newsData } = await supabase
                .from('company_news')
                .select('published_at, sentiment')
                .eq('ticker', ticker.toUpperCase())
                .gte('published_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString())
                .order('published_at', { ascending: false });

            // Calculate detailed metrics
            const ohlcvCoverage = ohlcvData?.length || 0;
            const reportsCount = reportsData?.length || 0;
            const newsCount7d = newsData?.length || 0;
            const latestOhlcv = ohlcvData?.[0]?.date;
            const latestReport = reportsData?.[0]?.report_date;
            const latestNews = newsData?.[0]?.published_at;

            // Calculate sentiment distribution
            const sentimentDistribution = {
                positive: newsData?.filter(n => n.sentiment === 'positive').length || 0,
                negative: newsData?.filter(n => n.sentiment === 'negative').length || 0,
                neutral: newsData?.filter(n => n.sentiment === 'neutral').length || 0
            };

            // Calculate completeness score (0-100)
            let completenessScore = 0;
            if (ohlcvCoverage >= 90) completenessScore += 40; // 40% for OHLCV
            else if (ohlcvCoverage >= 30) completenessScore += 20;
            else if (ohlcvCoverage >= 7) completenessScore += 10;

            if (reportsCount >= 5) completenessScore += 30; // 30% for reports
            else if (reportsCount >= 2) completenessScore += 20;
            else if (reportsCount >= 1) completenessScore += 10;

            if (newsCount7d >= 10) completenessScore += 30; // 30% for news
            else if (newsCount7d >= 5) completenessScore += 20;
            else if (newsCount7d >= 1) completenessScore += 10;

            const response = {
                company: {
                    ticker: company.ticker,
                    name: company.name,
                    sector: company.sector,
                    dataQuality: company.data_quality,
                    completenessScore
                },
                metrics: {
                    ohlcv: {
                        coverageDays: ohlcvCoverage,
                        latestDate: latestOhlcv,
                        status: ohlcvCoverage >= 30 ? 'good' : ohlcvCoverage >= 7 ? 'partial' : 'missing'
                    },
                    reports: {
                        count: reportsCount,
                        latestDate: latestReport,
                        types: reportsData?.map(r => r.report_type) || [],
                        status: reportsCount >= 2 ? 'good' : reportsCount >= 1 ? 'partial' : 'missing'
                    },
                    news: {
                        count7d: newsCount7d,
                        latestDate: latestNews,
                        sentimentDistribution,
                        status: newsCount7d >= 5 ? 'good' : newsCount7d >= 1 ? 'partial' : 'missing'
                    }
                },
                summary: {
                    overallQuality: company.data_quality,
                    completenessScore,
                    lastUpdated: company.data_quality_updated_at,
                    recommendations: generateRecommendations(ohlcvCoverage, reportsCount, newsCount7d)
                }
            };

            res.status(200).json(response);

        } else {
            // Get overall data quality statistics
            const { data: stats, error: statsError } = await supabase
                .rpc('get_data_quality_stats');

            if (statsError) {
                console.error('Error getting data quality stats:', statsError);
                return res.status(500).json({ error: 'Failed to get data quality statistics' });
            }

            // Get companies by data quality
            const { data: completeCompanies } = await supabase
                .from('companies_complete_data')
                .select('ticker, name, sector, market_cap_billion')
                .limit(10);

            const { data: partialCompanies } = await supabase
                .from('companies_partial_data')
                .select('ticker, name, sector, market_cap_billion')
                .limit(10);

            const { data: missingCompanies } = await supabase
                .from('companies_missing_data')
                .select('ticker, name, sector, market_cap_billion')
                .limit(10);

            const response = {
                overall: stats?.[0] || {
                    total_companies: 0,
                    complete_count: 0,
                    partial_count: 0,
                    missing_count: 0,
                    complete_percentage: 0,
                    partial_percentage: 0,
                    missing_percentage: 0,
                    avg_ohlcv_coverage: 0,
                    avg_reports_count: 0,
                    avg_news_count_7d: 0
                },
                companies: {
                    complete: completeCompanies || [],
                    partial: partialCompanies || [],
                    missing: missingCompanies || []
                },
                lastUpdated: new Date().toISOString()
            };

            res.status(200).json(response);
        }

    } catch (error) {
        console.error('Error in data quality endpoint:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

function generateRecommendations(ohlcvCoverage: number, reportsCount: number, newsCount7d: number): string[] {
    const recommendations = [];

    if (ohlcvCoverage < 30) {
        recommendations.push('Add more historical OHLCV data (target: 30+ days)');
    }
    if (ohlcvCoverage < 7) {
        recommendations.push('Add basic OHLCV data (minimum: 7 days)');
    }

    if (reportsCount < 2) {
        recommendations.push('Add more financial reports (target: 2+ reports)');
    }
    if (reportsCount === 0) {
        recommendations.push('Add financial reports data');
    }

    if (newsCount7d < 5) {
        recommendations.push('Increase news coverage (target: 5+ articles/week)');
    }
    if (newsCount7d === 0) {
        recommendations.push('Add news sentiment data');
    }

    if (recommendations.length === 0) {
        recommendations.push('Data quality is excellent - no recommendations needed');
    }

    return recommendations;
} 