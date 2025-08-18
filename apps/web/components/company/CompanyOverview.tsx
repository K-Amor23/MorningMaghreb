import { useState } from 'react'
import {
    ChartBarIcon,
    CurrencyDollarIcon,
    ClockIcon,
    InformationCircleIcon,
    ArrowUpIcon,
    ArrowDownIcon,
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'

interface CompanyOverviewProps {
    company: {
        ticker: string
        name: string
        sector: string
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
        beta: number
        sharesOutstanding: number
        float: number
        insiderOwnership: number
        institutionalOwnership: number
        shortRatio: number
        payoutRatio: number
        roe: number
        roa: number
        debtToEquity: number
        currentRatio: number
        quickRatio: number
        grossMargin: number
        operatingMargin: number
        netMargin: number
    }
}

export default function CompanyOverview({ company }: CompanyOverviewProps) {
    const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'ownership' | 'ratios'>('overview')

    const tabs = [
        { id: 'overview', label: 'Overview', icon: InformationCircleIcon },
        { id: 'financials', label: 'Financials', icon: ChartBarIcon },
        { id: 'ownership', label: 'Ownership', icon: CurrencyDollarIcon },
        { id: 'ratios', label: 'Ratios', icon: ArrowTrendingUpIcon }
    ]

    const formatCurrency = (value: number) => {
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

    const renderOverviewTab = () => (
        <div className="space-y-6">
            {/* Price Performance */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Price Performance</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Current Price</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.currentPrice.toFixed(2)} MAD
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Change</span>
                            <span className={`text-sm font-medium ${company.change >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {company.change >= 0 ? '+' : ''}{company.change.toFixed(2)} MAD
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Change %</span>
                            <span className={`text-sm font-medium ${company.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {company.changePercent >= 0 ? '+' : ''}{company.changePercent.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Trading Data</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Open</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.open.toFixed(2)} MAD
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">High</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.high.toFixed(2)} MAD
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Low</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.low.toFixed(2)} MAD
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 52-Week Range */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-3">52-Week Range</h3>
                <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                        <span className="text-blue-700 dark:text-blue-300">Low: {company.fiftyTwoWeekLow.toFixed(2)} MAD</span>
                        <span className="text-blue-700 dark:text-blue-300">High: {company.fiftyTwoWeekHigh.toFixed(2)} MAD</span>
                    </div>
                    <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-3">
                        <div
                            className="bg-blue-600 h-3 rounded-full relative"
                            style={{
                                width: `${((company.currentPrice - company.fiftyTwoWeekLow) /
                                    (company.fiftyTwoWeekHigh - company.fiftyTwoWeekLow)) * 100}%`
                            }}
                        >
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full border-2 border-white dark:border-gray-800"></div>
                        </div>
                    </div>
                    <div className="text-center text-sm text-blue-700 dark:text-blue-300">
                        Current: {company.currentPrice.toFixed(2)} MAD
                    </div>
                </div>
            </div>

            {/* Volume Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Volume Analysis</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Volume</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatNumber(company.volume)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Avg Volume</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatNumber(company.avgVolume)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Volume Ratio</span>
                            <span className={`text-sm font-medium ${company.volumeRatio > 1 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                {company.volumeRatio.toFixed(2)}x
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Market Data</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Market Cap</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatCurrency(company.marketCap)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">P/E Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.peRatio.toFixed(1)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Beta</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.beta.toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )

    const renderFinancialsTab = () => (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Profitability</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">ROE</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.roe.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">ROA</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.roa.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Gross Margin</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.grossMargin.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Operating Margin</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.operatingMargin.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Net Margin</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.netMargin.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Financial Health</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Current Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.currentRatio.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Quick Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.quickRatio.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Debt/Equity</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.debtToEquity.toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Dividend Information */}
            {company.dividendYield > 0 && (
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-green-900 dark:text-green-100 mb-3">Dividend Information</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-lg font-bold text-green-700 dark:text-green-300">
                                {company.dividendYield.toFixed(2)}%
                            </div>
                            <div className="text-xs text-green-600 dark:text-green-400">Yield</div>
                        </div>
                        <div className="text-center">
                            <div className="text-lg font-bold text-green-700 dark:text-green-300">
                                {company.payoutRatio.toFixed(1)}%
                            </div>
                            <div className="text-xs text-green-600 dark:text-green-400">Payout Ratio</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )

    const renderOwnershipTab = () => (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Share Structure</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Shares Outstanding</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatNumber(company.sharesOutstanding)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Float</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {formatNumber(company.float)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Short Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.shortRatio.toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Ownership</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Insider Ownership</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.insiderOwnership.toFixed(1)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Institutional</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.institutionalOwnership.toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )

    const renderRatiosTab = () => (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Valuation Ratios</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">P/E Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.peRatio.toFixed(1)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">P/B Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {(company.marketCap / (company.marketCap * 0.7)).toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">P/S Ratio</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {(company.marketCap / (company.marketCap * 0.4)).toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Risk Metrics</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Beta</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.beta.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-300">Debt/Equity</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {company.debtToEquity.toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )

    const renderActiveTab = () => {
        switch (activeTab) {
            case 'overview':
                return renderOverviewTab()
            case 'financials':
                return renderFinancialsTab()
            case 'ownership':
                return renderOwnershipTab()
            case 'ratios':
                return renderRatiosTab()
            default:
                return renderOverviewTab()
        }
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            {/* Tabs */}
            <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="flex space-x-8 px-6">
                    {tabs.map((tab) => {
                        const Icon = tab.icon
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                                        ? 'border-casablanca-blue text-casablanca-blue'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                                    }`}
                            >
                                <Icon className="h-4 w-4 inline mr-2" />
                                {tab.label}
                            </button>
                        )
                    })}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
                {renderActiveTab()}
            </div>
        </div>
    )
}
