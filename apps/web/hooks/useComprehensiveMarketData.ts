import { useState, useEffect } from 'react'
import useSWR from 'swr'

// Types for comprehensive market data
export interface MarketData {
    ticker: string
    name: string
    sector: string
    current_price: number
    change: number
    change_percent: number
    open: number
    high: number
    low: number
    volume: number
    market_cap: number
    pe_ratio: number
    dividend_yield: number
    fifty_two_week_high: number
    fifty_two_week_low: number
    avg_volume: number
    volume_ratio: number
    beta: number
    shares_outstanding: number
    float: number
    insider_ownership: number
    institutional_ownership: number
    short_ratio: number
    payout_ratio: number
    roe: number
    roa: number
    debt_to_equity: number
    current_ratio: number
    quick_ratio: number
    gross_margin: number
    operating_margin: number
    net_margin: number
    fifty_two_week_position?: number
    book_value_per_share?: number
    scraped_at: string
}

export interface NewsItem {
    id: string
    ticker: string
    title: string
    summary: string
    source: string
    published_at: string
    url: string
    category: string
    sentiment: string
    impact: string
    scraped_at: string
}

export interface DividendAnnouncement {
    id: string
    ticker: string
    type: string
    amount: number
    currency: string
    ex_date: string
    record_date: string
    payment_date: string
    description: string
    status: string
    scraped_at: string
}

export interface EarningsAnnouncement {
    id: string
    ticker: string
    period: string
    report_date: string
    estimate: number
    actual?: number
    surprise?: number
    surprise_percent?: number
    status: string
    scraped_at: string
}

export interface MarketStatus {
    status: string
    current_time: string
    trading_hours: string
    total_market_cap: number
    total_volume: number
    advancers: number
    decliners: number
    unchanged: number
    top_gainer: {
        ticker: string
        name: string
        change: number
        change_percent: number
    }
    top_loser: {
        ticker: string
        name: string
        change: number
        change_percent: number
    }
    most_active: {
        ticker: string
        name: string
        volume: number
        change: number
    }
    scraped_at: string
}

export interface ComprehensiveTickerData {
    ticker: string
    market_data: MarketData | null
    news: NewsItem[]
    dividends: DividendAnnouncement[]
    earnings: EarningsAnnouncement[]
    timestamp: string
}

export interface MarketOverview {
    market_status: MarketStatus | null
    top_gainers: Array<{
        ticker: string
        name: string
        current_price: number
        change: number
        change_percent: number
        volume: number
    }>
    top_losers: Array<{
        ticker: string
        name: string
        current_price: number
        change: number
        change_percent: number
        volume: number
    }>
    most_active: Array<{
        ticker: string
        name: string
        current_price: number
        volume: number
        change: number
    }>
    sector_performance: {
        [sector: string]: {
            count: number
            totalChange: number
            avgChange: number
        }
    }
    recent_news: Array<{
        ticker: string
        title: string
        published_at: string
        category: string
        impact: string
    }>
    upcoming_dividends: Array<{
        ticker: string
        amount: number
        ex_date: string
        type: string
    }>
    upcoming_earnings: Array<{
        ticker: string
        period: string
        report_date: string
        estimate: number
    }>
    timestamp: string
}

// Fetcher function for SWR
const fetcher = async (url: string) => {
    const response = await fetch(url)
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
}

// Hook for comprehensive data for a specific ticker
export function useComprehensiveTickerData(ticker: string | null) {
    const { data, error, isLoading, mutate } = useSWR<ComprehensiveTickerData>(
        ticker ? `/api/market-data/comprehensive?ticker=${ticker}` : null,
        fetcher,
        {
            refreshInterval: 30000, // Refresh every 30 seconds
            revalidateOnFocus: true,
            revalidateOnReconnect: true,
        }
    )

    return {
        data,
        error,
        isLoading,
        mutate,
        // Convenience getters
        marketData: data?.market_data || null,
        news: data?.news || [],
        dividends: data?.dividends || [],
        earnings: data?.earnings || [],
        timestamp: data?.timestamp || null,
    }
}

// Hook for specific data types for a ticker
export function useTickerDataByType(ticker: string | null, dataType: 'market' | 'news' | 'dividends' | 'earnings') {
    const { data, error, isLoading, mutate } = useSWR<any>(
        ticker ? `/api/market-data/comprehensive?ticker=${ticker}&data_type=${dataType}` : null,
        fetcher,
        {
            refreshInterval: 30000,
            revalidateOnFocus: true,
            revalidateOnReconnect: true,
        }
    )

    return {
        data,
        error,
        isLoading,
        mutate,
    }
}

// Hook for comprehensive market overview
export function useComprehensiveMarketOverview() {
    const { data, error, isLoading, mutate } = useSWR<MarketOverview>(
        '/api/market-data/comprehensive',
        fetcher,
        {
            refreshInterval: 60000, // Refresh every minute
            revalidateOnFocus: true,
            revalidateOnReconnect: true,
        }
    )

    return {
        data,
        error,
        isLoading,
        mutate,
        // Convenience getters
        marketStatus: data?.market_status || null,
        topGainers: data?.top_gainers || [],
        topLosers: data?.top_losers || [],
        mostActive: data?.most_active || [],
        sectorPerformance: data?.sector_performance || {},
        recentNews: data?.recent_news || [],
        upcomingDividends: data?.upcoming_dividends || [],
        upcomingEarnings: data?.upcoming_earnings || [],
        timestamp: data?.timestamp || null,
    }
}

// Hook for real-time market status updates
export function useRealTimeMarketStatus() {
    const [currentTime, setCurrentTime] = useState(new Date())

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date())
        }, 1000) // Update every second

        return () => clearInterval(interval)
    }, [])

    const { data: marketOverview, error, isLoading } = useComprehensiveMarketOverview()

    // Calculate market status based on current time
    const getMarketStatus = () => {
        if (!marketOverview?.market_status) return 'unknown'

        const now = currentTime
        const currentHour = now.getHours()

        // Moroccan market hours: 9:00 AM - 4:00 PM (UTC+1)
        // Adjust for UTC (UTC+1 during summer, UTC+0 during winter)
        const utcHour = now.getUTCHours()

        if (utcHour >= 8 && utcHour < 15) {
            return 'open'
        } else if (utcHour >= 7 && utcHour < 8) {
            return 'pre_market'
        } else if (utcHour >= 15 && utcHour < 16) {
            return 'after_hours'
        } else {
            return 'closed'
        }
    }

    const getTimeUntilOpen = () => {
        const now = currentTime
        const utcHour = now.getUTCHours()

        if (utcHour < 8) {
            // Market opens at 8:00 UTC
            const openTime = new Date(now)
            openTime.setUTCHours(8, 0, 0, 0)
            const diff = openTime.getTime() - now.getTime()
            const hours = Math.floor(diff / (1000 * 60 * 60))
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
            return `${hours}h ${minutes}m until open`
        } else if (utcHour >= 15) {
            // Market closed, next open is tomorrow
            const tomorrow = new Date(now)
            tomorrow.setDate(tomorrow.getDate() + 1)
            tomorrow.setUTCHours(8, 0, 0, 0)
            const diff = tomorrow.getTime() - now.getTime()
            const hours = Math.floor(diff / (1000 * 60 * 60))
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
            return `${hours}h ${minutes}m until open`
        }

        return null
    }

    const getTimeUntilClose = () => {
        const now = currentTime
        const utcHour = now.getUTCHours()

        if (utcHour >= 8 && utcHour < 15) {
            // Market closes at 15:00 UTC
            const closeTime = new Date(now)
            closeTime.setUTCHours(15, 0, 0, 0)
            const diff = closeTime.getTime() - now.getTime()
            const hours = Math.floor(diff / (1000 * 60 * 60))
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
            return `${hours}h ${minutes}m until close`
        }

        return null
    }

    return {
        currentTime,
        marketStatus: getMarketStatus(),
        timeUntilOpen: getTimeUntilOpen(),
        timeUntilClose: getTimeUntilClose(),
        marketOverview,
        error,
        isLoading,
    }
}

// Utility functions for data analysis
export const analyzeMarketData = (marketData: MarketData) => {
    if (!marketData) return null

    const analysis = {
        // Price analysis
        priceChange: marketData.change,
        priceChangePercent: marketData.change_percent,
        isPositive: marketData.change >= 0,

        // Volume analysis
        volumeChange: marketData.volume_ratio > 1 ? 'Above average' : 'Below average',
        volumeRatio: marketData.volume_ratio,

        // Technical analysis
        fiftyTwoWeekPosition: marketData.fifty_two_week_position || 0,
        isNearHigh: (marketData.fifty_two_week_position || 0) > 0.8,
        isNearLow: (marketData.fifty_two_week_position || 0) < 0.2,

        // Valuation metrics
        peRatio: marketData.pe_ratio,
        dividendYield: marketData.dividend_yield,
        marketCap: marketData.market_cap,

        // Financial health
        roe: marketData.roe,
        roa: marketData.roa,
        debtToEquity: marketData.debt_to_equity,
    }

    return analysis
}

export const categorizeNews = (news: NewsItem[]) => {
    const categories = {
        earnings: news.filter(item => item.category === 'earnings'),
        dividends: news.filter(item => item.category === 'dividend'),
        corporate: news.filter(item => item.category === 'corporate_action'),
        general: news.filter(item => item.category === 'news'),
    }

    return categories
}

export const getUpcomingEvents = (dividends: DividendAnnouncement[], earnings: EarningsAnnouncement[]) => {
    const now = new Date()
    const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)

    const upcomingDividends = dividends.filter(div => {
        const exDate = new Date(div.ex_date)
        return exDate >= now && exDate <= thirtyDaysFromNow
    }).sort((a, b) => new Date(a.ex_date).getTime() - new Date(b.ex_date).getTime())

    const upcomingEarnings = earnings.filter(earn => {
        const reportDate = new Date(earn.report_date)
        return reportDate >= now && reportDate <= thirtyDaysFromNow
    }).sort((a, b) => new Date(a.report_date).getTime() - new Date(b.report_date).getTime())

    return {
        upcomingDividends,
        upcomingEarnings,
        nextDividend: upcomingDividends[0] || null,
        nextEarnings: upcomingEarnings[0] || null,
    }
}
