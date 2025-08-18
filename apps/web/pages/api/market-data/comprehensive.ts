import { NextApiRequest, NextApiResponse } from 'next'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { ticker, data_type } = req.query

        // If specific ticker is requested
        if (ticker) {
            return await getComprehensiveDataForTicker(ticker as string, data_type as string, res)
        }

        // Get comprehensive market overview
        return await getComprehensiveMarketOverview(res)

    } catch (error) {
        console.error('Error in comprehensive market data API:', error)
        return res.status(500).json({
            error: 'Internal server error',
            details: error instanceof Error ? error.message : 'Unknown error'
        })
    }
}

async function getComprehensiveDataForTicker(
    ticker: string,
    dataType: string,
    res: NextApiResponse
) {
    try {
        const tickerUpper = ticker.toUpperCase()

        // Get market data
        const { data: marketData, error: marketError } = await supabase
            .from('comprehensive_market_data')
            .select('*')
            .eq('ticker', tickerUpper)
            .order('scraped_at', { ascending: false })
            .limit(1)
            .single()

        if (marketError && marketError.code !== 'PGRST116') {
            console.error('Error fetching market data:', marketError)
        }

        // Get news and announcements
        const { data: newsData, error: newsError } = await supabase
            .from('company_news')
            .select('*')
            .eq('ticker', tickerUpper)
            .order('published_at', { ascending: false })
            .limit(10)

        if (newsError) {
            console.error('Error fetching news data:', newsError)
        }

        // Get dividend announcements
        const { data: dividendData, error: dividendError } = await supabase
            .from('dividend_announcements')
            .select('*')
            .eq('ticker', tickerUpper)
            .order('ex_date', { ascending: false })
            .limit(10)

        if (dividendError) {
            console.error('Error fetching dividend data:', dividendError)
        }

        // Get earnings announcements
        const { data: earningsData, error: earningsError } = await supabase
            .from('earnings_announcements')
            .select('*')
            .eq('ticker', tickerUpper)
            .order('report_date', { ascending: false })
            .limit(10)

        if (earningsError) {
            console.error('Error fetching earnings data:', earningsError)
        }

        // If specific data type is requested, return only that
        if (dataType) {
            switch (dataType.toLowerCase()) {
                case 'market':
                    return res.status(200).json({
                        ticker: tickerUpper,
                        market_data: marketData || null,
                        timestamp: new Date().toISOString()
                    })

                case 'news':
                    return res.status(200).json({
                        ticker: tickerUpper,
                        news: newsData || [],
                        timestamp: new Date().toISOString()
                    })

                case 'dividends':
                    return res.status(200).json({
                        ticker: tickerUpper,
                        dividends: dividendData || [],
                        timestamp: new Date().toISOString()
                    })

                case 'earnings':
                    return res.status(200).json({
                        ticker: tickerUpper,
                        earnings: earningsData || [],
                        timestamp: new Date().toISOString()
                    })

                default:
                    return res.status(400).json({ error: 'Invalid data type specified' })
            }
        }

        // Return comprehensive data for the ticker
        return res.status(200).json({
            ticker: tickerUpper,
            market_data: marketData || null,
            news: newsData || [],
            dividends: dividendData || [],
            earnings: earningsData || [],
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error(`Error fetching comprehensive data for ${ticker}:`, error)
        return res.status(500).json({
            error: 'Failed to fetch comprehensive data',
            ticker,
            details: error instanceof Error ? error.message : 'Unknown error'
        })
    }
}

async function getComprehensiveMarketOverview(res: NextApiResponse) {
    try {
        // Get market status
        const { data: marketStatus, error: statusError } = await supabase
            .from('market_status')
            .select('*')
            .order('scraped_at', { ascending: false })
            .limit(1)
            .single()

        if (statusError && statusError.code !== 'PGRST116') {
            console.error('Error fetching market status:', statusError)
        }

        // Get top gainers and losers
        const { data: topMovers, error: moversError } = await supabase
            .from('comprehensive_market_data')
            .select('ticker, name, current_price, change, change_percent, volume')
            .not('change_percent', 'is', null)
            .order('change_percent', { ascending: false })
            .limit(10)

        if (moversError) {
            console.error('Error fetching top movers:', moversError)
        }

        // Get most active stocks by volume
        const { data: mostActive, error: activeError } = await supabase
            .from('comprehensive_market_data')
            .select('ticker, name, current_price, volume, change')
            .not('volume', 'is', null)
            .order('volume', { ascending: false })
            .limit(10)

        if (activeError) {
            console.error('Error fetching most active stocks:', activeError)
        }

        // Get sector performance
        const { data: sectorPerformance, error: sectorError } = await supabase
            .from('comprehensive_market_data')
            .select('sector, current_price, change_percent')
            .not('sector', 'is', null)
            .not('change_percent', 'is', null)

        if (sectorError) {
            console.error('Error fetching sector performance:', sectorError)
        }

        // Calculate sector averages
        const sectorAverages: { [key: string]: { count: number; totalChange: number; avgChange: number } } = {}

        if (sectorPerformance) {
            sectorPerformance.forEach(item => {
                if (item.sector && item.change_percent !== null) {
                    if (!sectorAverages[item.sector]) {
                        sectorAverages[item.sector] = { count: 0, totalChange: 0, avgChange: 0 }
                    }
                    sectorAverages[item.sector].count++
                    sectorAverages[item.sector].totalChange += item.change_percent
                }
            })

            // Calculate averages
            Object.keys(sectorAverages).forEach(sector => {
                sectorAverages[sector].avgChange = sectorAverages[sector].totalChange / sectorAverages[sector].count
            })
        }

        // Get recent news highlights
        const { data: recentNews, error: newsError } = await supabase
            .from('company_news')
            .select('ticker, title, published_at, category, impact')
            .order('published_at', { ascending: false })
            .limit(15)

        if (newsError) {
            console.error('Error fetching recent news:', newsError)
        }

        // Get upcoming dividends
        const { data: upcomingDividends, error: dividendError } = await supabase
            .from('dividend_announcements')
            .select('ticker, amount, ex_date, type')
            .gte('ex_date', new Date().toISOString())
            .order('ex_date', { ascending: true })
            .limit(10)

        if (dividendError) {
            console.error('Error fetching upcoming dividends:', dividendError)
        }

        // Get upcoming earnings
        const { data: upcomingEarnings, error: earningsError } = await supabase
            .from('earnings_announcements')
            .select('ticker, period, report_date, estimate')
            .gte('report_date', new Date().toISOString())
            .order('report_date', { ascending: true })
            .limit(10)

        if (earningsError) {
            console.error('Error fetching upcoming earnings:', earningsError)
        }

        return res.status(200).json({
            market_status: marketStatus || null,
            top_gainers: topMovers?.slice(0, 5) || [],
            top_losers: topMovers?.slice(-5).reverse() || [],
            most_active: mostActive || [],
            sector_performance: sectorAverages,
            recent_news: recentNews || [],
            upcoming_dividends: upcomingDividends || [],
            upcoming_earnings: upcomingEarnings || [],
            timestamp: new Date().toISOString()
        })

    } catch (error) {
        console.error('Error fetching comprehensive market overview:', error)
        return res.status(500).json({
            error: 'Failed to fetch market overview',
            details: error instanceof Error ? error.message : 'Unknown error'
        })
    }
}
