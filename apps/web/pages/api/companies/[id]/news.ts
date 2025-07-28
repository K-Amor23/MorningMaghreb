import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Mock data for when database tables don't exist
const getMockNewsData = (ticker: string, limit: number) => {
    const mockNews = [
        {
            id: '1',
            headline: `${ticker.toUpperCase()} Reports Strong Q3 Earnings`,
            source: 'Financial Times',
            publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            sentiment: 'positive',
            sentimentScore: 0.8,
            url: '#',
            contentPreview: `${ticker.toUpperCase()} exceeded analyst expectations with quarterly earnings of $2.8 billion...`
        },
        {
            id: '2',
            headline: `${ticker.toUpperCase()} Announces New Strategic Partnership`,
            source: 'Reuters',
            publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            sentiment: 'positive',
            sentimentScore: 0.7,
            url: '#',
            contentPreview: 'The company has entered into a strategic partnership to expand its market presence...'
        },
        {
            id: '3',
            headline: `${ticker.toUpperCase()} Faces Regulatory Challenges`,
            source: 'Bloomberg',
            publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            sentiment: 'negative',
            sentimentScore: -0.3,
            url: '#',
            contentPreview: 'Regulatory authorities have raised concerns about recent business practices...'
        },
        {
            id: '4',
            headline: `${ticker.toUpperCase()} Expands Operations in North Africa`,
            source: 'Morocco Business News',
            publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
            sentiment: 'positive',
            sentimentScore: 0.6,
            url: '#',
            contentPreview: 'The company has announced plans to expand its operations across North Africa...'
        },
        {
            id: '5',
            headline: `${ticker.toUpperCase()} Board Approves Dividend Increase`,
            source: 'Market Watch',
            publishedAt: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(),
            sentiment: 'positive',
            sentimentScore: 0.9,
            url: '#',
            contentPreview: 'The board of directors has approved a 15% increase in quarterly dividends...'
        }
    ];

    return {
        company: {
            ticker: ticker.toUpperCase(),
            name: `${ticker.toUpperCase()} Company`,
            sector: 'Technology'
        },
        news: {
            items: mockNews.slice(0, limit),
            sentimentDistribution: {
                positive: 4,
                negative: 1,
                neutral: 0,
                total: 5
            },
            totalCount: 5
        },
        sentiment: {
            bullishPercentage: 65,
            bearishPercentage: 20,
            neutralPercentage: 15,
            totalVotes: 150,
            averageConfidence: 3.8
        },
        metadata: {
            lastUpdated: new Date().toISOString(),
            sources: ['Mock Data'],
            dataQuality: 'mock',
            limit: limit
        }
    };
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { id: ticker } = req.query;
    const { limit = '10', sentiment } = req.query;

    if (!ticker || typeof ticker !== 'string') {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        // Try to get data from database
        let company = null;
        let news = null;
        let sentimentAggregates = null;

        try {
            // Get company information
            const { data: companyData, error: companyError } = await supabase
                .from('companies')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .single();

            if (!companyError && companyData) {
                company = companyData;
            }

            // Build query for news
            let query = supabase
                .from('company_news')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .order('published_at', { ascending: false })
                .limit(parseInt(limit as string));

            // Filter by sentiment if provided
            if (sentiment && typeof sentiment === 'string' && ['positive', 'negative', 'neutral'].includes(sentiment)) {
                query = query.eq('sentiment', sentiment);
            }

            const { data: newsData, error: newsError } = await query;

            if (!newsError && newsData) {
                news = newsData;
            }

            // Get sentiment aggregates
            const { data: sentimentData } = await supabase
                .from('sentiment_aggregates')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .single();

            if (sentimentData) {
                sentimentAggregates = sentimentData;
            }

        } catch (dbError) {
            console.log(`Database tables not available for ${ticker}, using mock data`);
        }

        // If we have real data, use it; otherwise use mock data
        if (company && news) {
            // Format news for frontend
            const formattedNews = news?.map(item => ({
                id: item.id,
                headline: item.headline,
                source: item.source,
                publishedAt: item.published_at,
                sentiment: item.sentiment,
                sentimentScore: item.sentiment_score,
                url: item.url,
                contentPreview: item.content_preview
            })) || [];

            // Calculate sentiment distribution
            const sentimentDistribution = {
                positive: formattedNews.filter(n => n.sentiment === 'positive').length,
                negative: formattedNews.filter(n => n.sentiment === 'negative').length,
                neutral: formattedNews.filter(n => n.sentiment === 'neutral').length,
                total: formattedNews.length
            };

            const response = {
                company: {
                    ticker: company.ticker,
                    name: company.name,
                    sector: company.sector
                },
                news: {
                    items: formattedNews,
                    sentimentDistribution,
                    totalCount: news?.length || 0
                },
                sentiment: sentimentAggregates ? {
                    bullishPercentage: sentimentAggregates.bullish_percentage,
                    bearishPercentage: sentimentAggregates.bearish_percentage,
                    neutralPercentage: sentimentAggregates.neutral_percentage,
                    totalVotes: sentimentAggregates.total_votes,
                    averageConfidence: sentimentAggregates.average_confidence
                } : null,
                metadata: {
                    lastUpdated: new Date().toISOString(),
                    sources: ['Supabase Database'],
                    dataQuality: 'real',
                    limit: parseInt(limit as string)
                }
            };

            res.status(200).json(response);
        } else {
            // Use mock data when database tables don't exist
            const mockData = getMockNewsData(ticker, parseInt(limit as string));
            res.status(200).json(mockData);
        }

    } catch (error) {
        console.error('Error in news endpoint:', error);
        // Fallback to mock data on any error
        const mockData = getMockNewsData(ticker, parseInt(limit as string));
        res.status(200).json(mockData);
    }
} 