import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
import {
    ChartBarIcon,
    ClockIcon,
    InformationCircleIcon,
    ArrowUpIcon,
    ArrowDownIcon
} from '@heroicons/react/24/outline'

// Dynamic import for TradingView widget
const TradingViewWidget = dynamic(() => import('./TradingViewWidget'), {
    ssr: false,
    loading: () => <div className="h-96 bg-gray-100 animate-pulse rounded-lg" />
})

interface MarketData {
    ticker: string
    currentPrice: number
    change: number
    changePercent: number
    open: number
    high: number
    low: number
    volume: number
    marketCap: number
    peRatio: number
    dividendYield: number
    fiftyTwoWeekHigh: number
    fiftyTwoWeekLow: number
    avgVolume: number
    volumeRatio: number
}

interface EnhancedTradingChartProps {
    ticker: string
    marketData?: MarketData
    className?: string
}

export default function EnhancedTradingChart({
    ticker,
    marketData,
    className = ''
}: EnhancedTradingChartProps) {
    const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL'>('1M')
    const [chartType, setChartType] = useState<'candlestick' | 'line' | 'area'>('candlestick')
    const [showVolume, setShowVolume] = useState(true)
    const [showIndicators, setShowIndicators] = useState(false)

    const timeframes = [
        { key: '1D', label: '1D' },
        { key: '1W', label: '1W' },
        { key: '1M', label: '1M' },
        { key: '3M', label: '3M' },
        { key: '1Y', label: '1Y' },
        { key: 'ALL', label: 'ALL' }
    ]

    const chartTypes = [
        { key: 'candlestick', label: 'Candlestick' },
        { key: 'line', label: 'Line' },
        { key: 'area', label: 'Area' }
    ]

    if (!marketData) {
        return (
            <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
                    <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
            </div>
        )
    }

    return (
        <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
            {/* Chart Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            {ticker} Chart
                        </h2>
                        <div className="flex items-center space-x-4 mt-2">
                            <span className="text-2xl font-bold text-gray-900 dark:text-white">
                                {marketData.currentPrice.toFixed(2)} MAD
                            </span>
                            <div className={`flex items-center text-sm font-medium ${marketData.change >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {marketData.change >= 0 ? (
                                    <ArrowUpIcon className="h-4 w-4 mr-1" />
                                ) : (
                                    <ArrowDownIcon className="h-4 w-4 mr-1" />
                                )}
                                {marketData.change >= 0 ? '+' : ''}{marketData.change.toFixed(2)}
                                ({marketData.changePercent >= 0 ? '+' : ''}{marketData.changePercent.toFixed(2)}%)
                            </div>
                        </div>
                    </div>

                    <div className="text-right">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            Market Cap: {(marketData.marketCap / 1e9).toFixed(2)}B MAD
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                            P/E: {marketData.peRatio.toFixed(1)}
                        </div>
                        {marketData.dividendYield > 0 && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                                Yield: {marketData.dividendYield.toFixed(2)}%
                            </div>
                        )}
                    </div>
                </div>

                {/* Key Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-500 dark:text-gray-400">Open</div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {marketData.open.toFixed(2)}
                        </div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-500 dark:text-gray-400">High</div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {marketData.high.toFixed(2)}
                        </div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-500 dark:text-gray-400">Low</div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {marketData.low.toFixed(2)}
                        </div>
                    </div>
                    <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-500 dark:text-gray-400">Volume</div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {(marketData.volume / 1e6).toFixed(1)}M
                        </div>
                    </div>
                </div>

                {/* 52-Week Range */}
                <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                        52-Week Range
                    </div>
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-blue-700 dark:text-blue-300">
                            Low: {marketData.fiftyTwoWeekLow.toFixed(2)} MAD
                        </div>
                        <div className="text-sm text-blue-700 dark:text-blue-300">
                            High: {marketData.fiftyTwoWeekHigh.toFixed(2)} MAD
                        </div>
                    </div>
                    <div className="mt-2 w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
                        <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                                width: `${((marketData.currentPrice - marketData.fiftyTwoWeekLow) /
                                    (marketData.fiftyTwoWeekHigh - marketData.fiftyTwoWeekLow)) * 100}%`
                            }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Chart Controls */}
            <div className="px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {timeframes.map((tf) => (
                            <button
                                key={tf.key}
                                onClick={() => setTimeframe(tf.key as any)}
                                className={`px-3 py-1 text-sm rounded-md transition-colors ${timeframe === tf.key
                                        ? 'bg-casablanca-blue text-white'
                                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {tf.label}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            {chartTypes.map((ct) => (
                                <button
                                    key={ct.key}
                                    onClick={() => setChartType(ct.key as any)}
                                    className={`px-3 py-1 text-sm rounded-md transition-colors ${chartType === ct.key
                                            ? 'bg-casablanca-blue text-white'
                                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {ct.label}
                                </button>
                            ))}
                        </div>

                        <div className="flex items-center space-x-2">
                            <label className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                                <input
                                    type="checkbox"
                                    checked={showVolume}
                                    onChange={(e) => setShowVolume(e.target.checked)}
                                    className="mr-2"
                                />
                                Volume
                            </label>
                            <label className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                                <input
                                    type="checkbox"
                                    checked={showIndicators}
                                    onChange={(e) => setShowIndicators(e.target.checked)}
                                    className="mr-2"
                                />
                                Indicators
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            {/* TradingView Chart */}
            <div className="p-6">
                <TradingViewWidget
                    symbol={`BVC:${ticker}`}
                    interval={timeframe === '1D' ? '1' : timeframe === '1W' ? '7' : timeframe === '1M' ? '30' : '365'}
                    style={chartType}
                    showVolume={showVolume}
                    showIndicators={showIndicators}
                />
            </div>
        </div>
    )
}
