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
    const { limit = '10', sentiment } = req.query;

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

        const { data: news, error: newsError } = await query;

        if (newsError) {
            console.error('Error fetching news:', newsError);
            return res.status(500).json({ error: 'Failed to fetch news data' });
        }

        // Get sentiment aggregates
        const { data: sentimentAggregates } = await supabase
            .from('sentiment_aggregates')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .single();

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
                dataQuality: news && news.length > 0 ? 'real' : 'none',
                limit: parseInt(limit as string)
            }
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in news endpoint:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 