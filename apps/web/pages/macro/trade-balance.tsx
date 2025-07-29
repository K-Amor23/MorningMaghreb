import Head from 'next/head'
import { useState } from 'react'
import { GlobeAltIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, ChartBarIcon, DocumentTextIcon, TruckIcon } from '@heroicons/react/24/outline'

// Mock trade balance data - in real implementation this would come from API
const tradeBalanceData = {
    current: {
        exports: 32.8,
        imports: 34.9,
        balance: -2.1,
        change: -0.3,
        changePercent: -16.7,
        period: 'June 2024',
        previous: -1.8
    },
    historical: [
        { month: '2024-01', exports: 31.2, imports: 33.8, balance: -2.6 },
        { month: '2024-02', exports: 30.8, imports: 33.2, balance: -2.4 },
        { month: '2024-03', exports: 31.5, imports: 33.5, balance: -2.0 },
        { month: '2024-04', exports: 32.1, imports: 34.1, balance: -2.0 },
        { month: '2024-05', exports: 32.5, imports: 34.5, balance: -2.0 },
        { month: '2024-06', exports: 32.8, imports: 34.9, balance: -2.1 }
    ],
    exports: [
        { category: 'Phosphates', value: 8.2, change: 0.3, share: 25.0 },
        { category: 'Textiles', value: 6.5, change: -0.2, share: 19.8 },
        { category: 'Automotive', value: 5.8, change: 0.4, share: 17.7 },
        { category: 'Agriculture', value: 4.2, change: 0.1, share: 12.8 },
        { category: 'Electronics', value: 3.1, change: 0.2, share: 9.5 },
        { category: 'Other', value: 5.0, change: -0.1, share: 15.2 }
    ],
    imports: [
        { category: 'Energy', value: 9.8, change: 0.5, share: 28.1 },
        { category: 'Machinery', value: 7.2, change: 0.2, share: 20.6 },
        { category: 'Chemicals', value: 5.5, change: 0.1, share: 15.8 },
        { category: 'Food', value: 4.8, change: 0.0, share: 13.8 },
        { category: 'Vehicles', value: 3.6, change: 0.1, share: 10.3 },
        { category: 'Other', value: 4.0, change: 0.0, share: 11.4 }
    ],
    partners: {
        exports: [
            { country: 'Spain', value: 6.8, share: 20.7, change: 0.2 },
            { country: 'France', value: 5.2, share: 15.9, change: -0.1 },
            { country: 'India', value: 3.8, share: 11.6, change: 0.3 },
            { country: 'USA', value: 3.2, share: 9.8, change: 0.1 },
            { country: 'Germany', value: 2.9, share: 8.8, change: 0.0 },
            { country: 'Italy', value: 2.5, share: 7.6, change: -0.1 }
        ],
        imports: [
            { country: 'Spain', value: 7.2, share: 20.6, change: 0.3 },
            { country: 'France', value: 6.1, share: 17.5, change: 0.1 },
            { country: 'China', value: 4.8, share: 13.8, change: 0.2 },
            { country: 'USA', value: 3.5, share: 10.0, change: 0.0 },
            { country: 'Germany', value: 3.2, share: 9.2, change: 0.1 },
            { country: 'Italy', value: 2.8, share: 8.0, change: -0.1 }
        ]
    }
}

const balanceOfPayments = {
    currentAccount: -2.1,
    capitalAccount: 1.8,
    financialAccount: 0.3,
    reserves: 0.8,
    unit: 'Billion USD'
}

export default function TradeBalancePage() {
    const [selectedView, setSelectedView] = useState<'balance' | 'exports' | 'imports'>('balance')
    const [timeframe, setTimeframe] = useState<'6M' | '1Y' | '2Y'>('1Y')

    const formatNumber = (num: number) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(num)
    }

    const getChangeColor = (change: number) => {
        if (change > 0) return 'text-green-600'
        if (change < 0) return 'text-red-600'
        return 'text-gray-600'
    }

    const getChangeIcon = (change: number) => {
        if (change > 0) return <ArrowTrendingUpIcon className="h-4 w-4" />
        if (change < 0) return <ArrowTrendingDownIcon className="h-4 w-4" />
        return null
    }

    const getBalanceColor = (balance: number) => {
        if (balance > 0) return 'text-green-600'
        if (balance < 0) return 'text-red-600'
        return 'text-gray-600'
    }

    return (
        <>
            <Head>
                <title>Morocco Trade Balance - Import/Export Data | Casablanca Insight</title>
                <meta name="description" content="Morocco trade balance, import/export data, trade partners, and balance of payments analysis. Real-time data from customs and central bank." />
            </Head>

            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <GlobeAltIcon className="h-8 w-8 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Morocco Trade Balance</h1>
                            <p className="text-gray-600">Import/Export Data and Trade Analysis</p>
                        </div>
                    </div>

                    {/* Current Trade Balance Card */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Trade Balance</h3>
                                <p className={`text-3xl font-bold ${getBalanceColor(tradeBalanceData.current.balance)}`}>
                                    {formatNumber(tradeBalanceData.current.balance)} {tradeBalanceData.current.balance < 0 ? 'Billion USD' : 'Billion USD'}
                                </p>
                                <p className="text-sm text-gray-500">{tradeBalanceData.current.period}</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Monthly Change</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-2xl font-bold ${getChangeColor(tradeBalanceData.current.change)}`}>
                                        {tradeBalanceData.current.change > 0 ? '+' : ''}{formatNumber(tradeBalanceData.current.change)}B
                                    </span>
                                    {getChangeIcon(tradeBalanceData.current.change)}
                                </div>
                                <p className="text-sm text-gray-500">{tradeBalanceData.current.changePercent}%</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Exports</h3>
                                <p className="text-2xl font-bold text-green-600">{formatNumber(tradeBalanceData.current.exports)}B USD</p>
                                <p className="text-sm text-gray-500">+2.1% vs previous</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Imports</h3>
                                <p className="text-2xl font-bold text-red-600">{formatNumber(tradeBalanceData.current.imports)}B USD</p>
                                <p className="text-sm text-gray-500">+1.2% vs previous</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Balance of Payments */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Balance of Payments</h3>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Current Account</h4>
                                <p className={`text-2xl font-bold ${getBalanceColor(balanceOfPayments.currentAccount)}`}>
                                    {formatNumber(balanceOfPayments.currentAccount)} {balanceOfPayments.unit}
                                </p>
                                <p className="text-sm text-gray-500">Trade + Services</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Capital Account</h4>
                                <p className="text-2xl font-bold text-green-600">{formatNumber(balanceOfPayments.capitalAccount)} {balanceOfPayments.unit}</p>
                                <p className="text-sm text-gray-500">Investment flows</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Financial Account</h4>
                                <p className="text-2xl font-bold text-blue-600">{formatNumber(balanceOfPayments.financialAccount)} {balanceOfPayments.unit}</p>
                                <p className="text-sm text-gray-500">Banking flows</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Reserves Change</h4>
                                <p className="text-2xl font-bold text-green-600">{formatNumber(balanceOfPayments.reserves)} {balanceOfPayments.unit}</p>
                                <p className="text-sm text-gray-500">FX reserves</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Trade Balance Trend Chart */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Trade Balance Trend</h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setTimeframe('6M')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '6M'
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    6M
                                </button>
                                <button
                                    onClick={() => setTimeframe('1Y')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '1Y'
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    1Y
                                </button>
                                <button
                                    onClick={() => setTimeframe('2Y')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '2Y'
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    2Y
                                </button>
                            </div>
                        </div>
                        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                            <div className="text-center">
                                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                                <p className="text-gray-500">Interactive chart coming soon</p>
                                <p className="text-sm text-gray-400">Trade balance over time</p>
                            </div>
                        </div>
                    </div>

                    {/* Top Export Categories */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Export Categories</h3>
                        <div className="space-y-3">
                            {tradeBalanceData.exports.map((category) => (
                                <div key={category.category} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{category.category}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(category.value)}B</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-green-600 h-2 rounded-full"
                                                style={{ width: `${(category.share / 30) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(category.change)}`}>
                                            {category.change > 0 ? '+' : ''}{formatNumber(category.change)}B
                                        </span>
                                        {getChangeIcon(category.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Top Import Categories */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Top Import Categories</h3>
                    </div>
                    <div className="p-6">
                        <div className="space-y-3">
                            {tradeBalanceData.imports.map((category) => (
                                <div key={category.category} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{category.category}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(category.value)}B</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-red-600 h-2 rounded-full"
                                                style={{ width: `${(category.share / 30) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(category.change)}`}>
                                            {category.change > 0 ? '+' : ''}{formatNumber(category.change)}B
                                        </span>
                                        {getChangeIcon(category.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Trade Partners */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Top Export Partners */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Export Partners</h3>
                        <div className="space-y-3">
                            {tradeBalanceData.partners.exports.map((partner) => (
                                <div key={partner.country} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{partner.country}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(partner.value)}B</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-green-600 h-2 rounded-full"
                                                style={{ width: `${(partner.share / 25) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(partner.change)}`}>
                                            {partner.change > 0 ? '+' : ''}{formatNumber(partner.change)}B
                                        </span>
                                        {getChangeIcon(partner.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Top Import Partners */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Import Partners</h3>
                        <div className="space-y-3">
                            {tradeBalanceData.partners.imports.map((partner) => (
                                <div key={partner.country} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{partner.country}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(partner.value)}B</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-red-600 h-2 rounded-full"
                                                style={{ width: `${(partner.share / 25) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(partner.change)}`}>
                                            {partner.change > 0 ? '+' : ''}{formatNumber(partner.change)}B
                                        </span>
                                        {getChangeIcon(partner.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Historical Data Table */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Historical Trade Data</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exports (B USD)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Imports (B USD)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Balance (B USD)</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {tradeBalanceData.historical.map((item) => (
                                    <tr key={item.month} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.month}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.exports)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.imports)}</td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getBalanceColor(item.balance)}`}>
                                            {formatNumber(item.balance)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Additional Information */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li>• Trade deficit widened to $2.1B in June 2024</li>
                            <li>• Exports increased by 2.1% to $32.8B</li>
                            <li>• Imports rose by 1.2% to $34.9B</li>
                            <li>• Spain remains the largest trading partner</li>
                            <li>• Phosphates continue to be the top export</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h3>
                        <div className="space-y-3 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Customs Administration - Trade data</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Bank Al-Maghrib - Balance of payments</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Ministry of Trade - Export/Import statistics</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>OECD - International trade comparisons</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 