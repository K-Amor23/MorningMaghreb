import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import { useState, useEffect } from 'react'
import {
    CurrencyDollarIcon,
    ChartBarIcon,
    BuildingOfficeIcon,
    GlobeAltIcon,
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'

interface ETF {
    id: string
    name: string
    ticker: string
    isin: string
    underlying_index: string
    issuer: string
    expense_ratio: number
    inception_date: string
    listing_date: string
    asset_class: string
    geographic_focus: string
    sector_focus: string
    nav: number
    price: number
    volume: number
    total_assets: number
    premium_discount: number
    change_amount: number
    change_percent: number
    high_24h: number
    low_24h: number
    open_price: number
    previous_close: number
}

export default function ETFs() {
    const [etfs, setEtfs] = useState<ETF[]>([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('all')

    useEffect(() => {
        fetchETFData()
    }, [])

    const fetchETFData = async () => {
        try {
            setLoading(true)

            // Fetch ETFs data
            const response = await fetch('/api/markets/etfs')
            const data = await response.json()
            setEtfs(data.etfs || [])

        } catch (error) {
            console.error('Error fetching ETF data:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'MAD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount)
    }

    const formatPercent = (value: number) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    }

    const formatNumber = (num: number) => {
        if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`
        if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
        if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`
        return num.toString()
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        })
    }

    const filteredETFs = etfs.filter(etf => {
        if (activeTab === 'all') return true
        if (activeTab === 'equity') return etf.asset_class === 'equity'
        if (activeTab === 'bond') return etf.asset_class === 'bond'
        return true
    })

    const tabs = [
        { id: 'all', name: 'All ETFs', count: etfs.length },
        { id: 'equity', name: 'Equity', count: etfs.filter(e => e.asset_class === 'equity').length },
        { id: 'bond', name: 'Bond', count: etfs.filter(e => e.asset_class === 'bond').length }
    ]

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Header />
                <TickerBar />
                <div className="flex items-center justify-center min-h-screen">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
                </div>
            </div>
        )
    }

    return (
        <>
            <Head>
                <title>ETFs - Casablanca Insight</title>
                <meta name="description" content="Moroccan ETF market data, NAV information, and performance metrics" />
            </Head>

            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Header />
                <TickerBar />

                <main className="px-4 py-6 max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="mb-6">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">ETFs</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Moroccan Exchange-Traded Funds with real-time NAV and performance data
                        </p>
                    </div>

                    {/* Market Summary */}
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Total AUM</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                        {formatCurrency(etfs.reduce((sum, etf) => sum + etf.total_assets, 0))}
                                    </p>
                                </div>
                                <CurrencyDollarIcon className="h-8 w-8 text-green-500" />
                            </div>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Total ETFs</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                        {etfs.length}
                                    </p>
                                </div>
                                <ChartBarIcon className="h-8 w-8 text-blue-500" />
                            </div>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Avg Expense Ratio</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                        {(etfs.reduce((sum, etf) => sum + etf.expense_ratio, 0) / etfs.length * 100).toFixed(2)}%
                                    </p>
                                </div>
                                <BuildingOfficeIcon className="h-8 w-8 text-purple-500" />
                            </div>
                        </div>
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Avg Premium/Discount</p>
                                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                        {(etfs.reduce((sum, etf) => sum + etf.premium_discount, 0) / etfs.length * 100).toFixed(2)}%
                                    </p>
                                </div>
                                <GlobeAltIcon className="h-8 w-8 text-orange-500" />
                            </div>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="mb-6">
                        <div className="border-b border-gray-200 dark:border-gray-700">
                            <nav className="-mb-px flex space-x-8">
                                {tabs.map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                                                ? 'border-casablanca-blue text-casablanca-blue'
                                                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                                            }`}
                                    >
                                        {tab.name} ({tab.count})
                                    </button>
                                ))}
                            </nav>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* ETFs List */}
                        <div className="lg:col-span-2">
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                                        ETF Prices & NAV
                                    </h2>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                        <thead className="bg-gray-50 dark:bg-gray-700">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    ETF
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Index
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    NAV
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Price
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Premium/Discount
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    AUM
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Change
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                            {filteredETFs.map((etf) => (
                                                <tr key={etf.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                                                                {etf.name}
                                                            </div>
                                                            <div className="text-sm text-gray-500 dark:text-gray-400">
                                                                {etf.ticker}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {etf.underlying_index}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {formatCurrency(etf.nav)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {formatCurrency(etf.price)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`text-sm font-medium ${etf.premium_discount >= 0
                                                                ? 'text-green-600 dark:text-green-400'
                                                                : 'text-red-600 dark:text-red-400'
                                                            }`}>
                                                            {formatPercent(etf.premium_discount * 100)}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {formatCurrency(etf.total_assets)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`text-sm font-medium ${etf.change_percent >= 0
                                                                ? 'text-green-600 dark:text-green-400'
                                                                : 'text-red-600 dark:text-red-400'
                                                            }`}>
                                                            {formatPercent(etf.change_percent)}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {/* Sidebar */}
                        <div className="space-y-6">
                            {/* ETF Details */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                        ETF Details
                                    </h3>
                                </div>
                                <div className="p-6">
                                    {etfs.length > 0 ? (
                                        <div className="space-y-4">
                                            {etfs.slice(0, 3).map((etf) => (
                                                <div key={etf.id} className="border-l-4 border-casablanca-blue pl-4">
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                                                        {etf.name}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        {etf.issuer} • {etf.underlying_index}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        Expense: {(etf.expense_ratio * 100).toFixed(2)}% • {etf.asset_class}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        Listed: {formatDate(etf.listing_date)}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 dark:text-gray-400 text-sm">
                                            No ETF data available
                                        </p>
                                    )}
                                </div>
                            </div>

                            {/* Market Stats */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                        Market Statistics
                                    </h3>
                                </div>
                                <div className="p-6 space-y-4">
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Total ETFs</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">{etfs.length}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Equity ETFs</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {etfs.filter(e => e.asset_class === 'equity').length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Bond ETFs</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {etfs.filter(e => e.asset_class === 'bond').length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Total Volume</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {formatNumber(etfs.reduce((sum, e) => sum + e.volume, 0))}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Avg Change</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {formatPercent(etfs.reduce((sum, e) => sum + e.change_percent, 0) / etfs.length)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>

                <Footer />
            </div>
        </>
    )
} 