import { useState, useEffect } from 'react'
import {
    ClockIcon,
    ChartBarIcon,
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon,
    CurrencyDollarIcon,
    GlobeAltIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon
} from '@heroicons/react/24/outline'

interface MarketStatusData {
    status: 'open' | 'closed' | 'pre_market' | 'after_hours'
    currentTime: string
    nextOpen: string
    nextClose: string
    tradingHours: string
    timezone: string
    lastUpdate: string
}

interface MarketMetrics {
    totalMarketCap: number
    totalVolume: number
    totalTransactions: number
    advancers: number
    decliners: number
    unchanged: number
    gainers: number
    losers: number
    mostActive: {
        ticker: string
        name: string
        volume: number
        change: number
    }
    topGainer: {
        ticker: string
        name: string
        change: number
        changePercent: number
    }
    topLoser: {
        ticker: string
        name: string
        change: number
        changePercent: number
    }
}

interface MarketStatusProps {
    className?: string
}

export default function MarketStatus({ className = '' }: MarketStatusProps) {
    const [marketStatus, setMarketStatus] = useState<MarketStatusData>({
        status: 'closed',
        currentTime: new Date().toLocaleTimeString('en-US', {
            timeZone: 'Africa/Casablanca',
            hour12: false
        }),
        nextOpen: '09:00',
        nextClose: '16:00',
        tradingHours: '09:00 - 16:00',
        timezone: 'Africa/Casablanca',
        lastUpdate: new Date().toLocaleString('en-US', {
            timeZone: 'Africa/Casablanca'
        })
    })

    const [marketMetrics, setMarketMetrics] = useState<MarketMetrics>({
        totalMarketCap: 1016840000000, // 1.01684 trillion MAD
        totalVolume: 212321128.20,
        totalTransactions: 0,
        advancers: 45,
        decliners: 23,
        unchanged: 10,
        gainers: 12,
        losers: 8,
        mostActive: {
            ticker: 'NAKL',
            name: 'Ennakl',
            volume: 232399,
            change: 3.78
        },
        topGainer: {
            ticker: 'SBM',
            name: 'Société des Boissons du Maroc',
            change: 120.00,
            changePercent: 6.03
        },
        topLoser: {
            ticker: 'ZDJ',
            name: 'Zellidja S.A',
            change: -18.80,
            changePercent: -5.99
        }
    })

    useEffect(() => {
        const updateTime = () => {
            const now = new Date()
            const casablancaTime = new Date(now.toLocaleString('en-US', { timeZone: 'Africa/Casablanca' }))
            const currentHour = casablancaTime.getHours()
            const currentMinute = casablancaTime.getMinutes()

            let status: 'open' | 'closed' | 'pre_market' | 'after_hours' = 'closed'

            if (currentHour >= 9 && currentHour < 16) {
                status = 'open'
            } else if (currentHour >= 8 && currentHour < 9) {
                status = 'pre_market'
            } else if (currentHour >= 16 && currentHour < 17) {
                status = 'after_hours'
            }

            setMarketStatus(prev => ({
                ...prev,
                status,
                currentTime: casablancaTime.toLocaleTimeString('en-US', {
                    timeZone: 'Africa/Casablanca',
                    hour12: false
                }),
                lastUpdate: casablancaTime.toLocaleString('en-US', {
                    timeZone: 'Africa/Casablanca'
                })
            }))
        }

        updateTime()
        const interval = setInterval(updateTime, 1000)

        return () => clearInterval(interval)
    }, [])

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'open':
                return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'closed':
                return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            case 'pre_market':
                return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
            case 'after_hours':
                return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
            default:
                return 'text-gray-600 bg-gray-100 dark:bg-gray-700'
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'open':
                return <CheckCircleIcon className="h-5 w-5 text-green-600" />
            case 'closed':
                return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
            case 'pre_market':
                return <ClockIcon className="h-5 w-5 text-yellow-600" />
            case 'after_hours':
                return <ClockIcon className="h-5 w-5 text-blue-600" />
            default:
                return <ClockIcon className="h-5 w-5 text-gray-600" />
        }
    }

    const formatCurrency = (value: number) => {
        if (value >= 1e12) return `${(value / 1e12).toFixed(2)}T MAD`
        if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B MAD`
        if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M MAD`
        if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K MAD`
        return `${value.toFixed(2)} MAD`
    }

    const formatNumber = (value: number) => {
        if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
        if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`
        return value.toLocaleString()
    }

    return (
        <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
            {/* Market Status Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        Market Status
                    </h2>
                    <div className="flex items-center space-x-2">
                        <GlobeAltIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                            {marketStatus.timezone}
                        </span>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Trading Status */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-center justify-center mb-2">
                            {getStatusIcon(marketStatus.status)}
                        </div>
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                            Trading Status
                        </div>
                        <div className={`px-3 py-1 text-sm font-medium rounded-full inline-block ${getStatusColor(marketStatus.status)}`}>
                            {marketStatus.status === 'open' ? 'OPEN' :
                                marketStatus.status === 'closed' ? 'CLOSED' :
                                    marketStatus.status === 'pre_market' ? 'PRE-MARKET' : 'AFTER HOURS'}
                        </div>
                    </div>

                    {/* Current Time */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <ClockIcon className="h-5 w-5 text-gray-400 mx-auto mb-2" />
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                            Current Time
                        </div>
                        <div className="text-lg font-bold text-gray-900 dark:text-white">
                            {marketStatus.currentTime}
                        </div>
                    </div>

                    {/* Trading Hours */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <ChartBarIcon className="h-5 w-5 text-gray-400 mx-auto mb-2" />
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                            Trading Hours
                        </div>
                        <div className="text-lg font-bold text-gray-900 dark:text-white">
                            {marketStatus.tradingHours}
                        </div>
                    </div>
                </div>

                {/* Next Session Info */}
                {marketStatus.status === 'closed' && (
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-sm text-blue-900 dark:text-blue-100 text-center">
                            Next trading session: <span className="font-medium">Monday at 09:00</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Market Metrics */}
            <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Market Overview
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {formatCurrency(marketMetrics.totalMarketCap)}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Total Market Cap
                        </div>
                    </div>

                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {formatCurrency(marketMetrics.totalVolume)}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Total Volume
                        </div>
                    </div>

                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {marketMetrics.totalTransactions}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Transactions
                        </div>
                    </div>

                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {marketMetrics.advancers + marketMetrics.decliners + marketMetrics.unchanged}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Active Stocks
                        </div>
                    </div>
                </div>

                {/* Market Breadth */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                                    <ArrowTrendingUpIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-green-600">
                            {marketMetrics.advancers}
                        </div>
                        <div className="text-sm text-green-700 dark:text-green-300">
                            Advancers
                        </div>
                    </div>

                    <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                                                    <ArrowTrendingDownIcon className="h-8 w-8 text-red-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-red-600">
                            {marketMetrics.decliners}
                        </div>
                        <div className="text-sm text-red-700 dark:text-red-300">
                            Decliners
                        </div>
                    </div>

                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <ChartBarIcon className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {marketMetrics.unchanged}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Unchanged
                        </div>
                    </div>
                </div>

                {/* Top Performers */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <h4 className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
                            Top Gainer
                        </h4>
                        <div className="text-lg font-bold text-green-700 dark:text-green-300">
                            {marketMetrics.topGainer.ticker}
                        </div>
                        <div className="text-sm text-green-600 dark:text-green-400 mb-1">
                            {marketMetrics.topGainer.name}
                        </div>
                        <div className="text-lg font-bold text-green-700 dark:text-green-300">
                            +{marketMetrics.topGainer.change.toFixed(2)} MAD
                        </div>
                        <div className="text-sm text-green-600 dark:text-green-400">
                            +{marketMetrics.topGainer.changePercent.toFixed(2)}%
                        </div>
                    </div>

                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
                            Top Loser
                        </h4>
                        <div className="text-lg font-bold text-red-700 dark:text-red-300">
                            {marketMetrics.topLoser.ticker}
                        </div>
                        <div className="text-sm text-red-600 dark:text-red-400 mb-1">
                            {marketMetrics.topLoser.name}
                        </div>
                        <div className="text-lg font-bold text-red-700 dark:text-red-300">
                            {marketMetrics.topLoser.change.toFixed(2)} MAD
                        </div>
                        <div className="text-sm text-red-600 dark:text-red-400">
                            {marketMetrics.topLoser.changePercent.toFixed(2)}%
                        </div>
                    </div>

                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
                            Most Active
                        </h4>
                        <div className="text-lg font-bold text-blue-700 dark:text-blue-300">
                            {marketMetrics.mostActive.ticker}
                        </div>
                        <div className="text-sm text-blue-600 dark:text-blue-400 mb-1">
                            {marketMetrics.mostActive.name}
                        </div>
                        <div className="text-lg font-bold text-blue-700 dark:text-blue-300">
                            {formatNumber(marketMetrics.mostActive.volume)}
                        </div>
                        <div className="text-sm text-blue-600 dark:text-blue-400">
                            Volume
                        </div>
                    </div>
                </div>
            </div>

            {/* Last Update */}
            <div className="px-6 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    Last updated: {marketStatus.lastUpdate}
                </div>
            </div>
        </div>
    )
}
