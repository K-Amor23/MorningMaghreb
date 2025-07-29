import Head from 'next/head'
import { useState } from 'react'
import { CurrencyDollarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, ChartBarIcon, DocumentTextIcon, GlobeAltIcon } from '@heroicons/react/24/outline'

// Mock exchange rate data - in real implementation this would come from API
const exchangeRateData = {
    current: {
        usd: 9.85,
        eur: 10.75,
        gbp: 12.45,
        cny: 1.36,
        date: '2024-07-24',
        change: -0.05,
        changePercent: -0.51
    },
    historical: [
        { date: '2024-01', usd: 9.90, eur: 10.80, gbp: 12.60, cny: 1.38 },
        { date: '2024-02', usd: 9.88, eur: 10.78, gbp: 12.55, cny: 1.37 },
        { date: '2024-03', usd: 9.87, eur: 10.77, gbp: 12.52, cny: 1.37 },
        { date: '2024-04', usd: 9.86, eur: 10.76, gbp: 12.48, cny: 1.36 },
        { date: '2024-05', usd: 9.85, eur: 10.75, gbp: 12.45, cny: 1.36 },
        { date: '2024-06', usd: 9.84, eur: 10.74, gbp: 12.42, cny: 1.35 },
        { date: '2024-07', usd: 9.85, eur: 10.75, gbp: 12.45, cny: 1.36 }
    ],
    currencyPairs: [
        { pair: 'MAD/USD', rate: 9.85, change: -0.05, changePercent: -0.51, direction: 'down' },
        { pair: 'MAD/EUR', rate: 10.75, change: -0.03, changePercent: -0.28, direction: 'down' },
        { pair: 'MAD/GBP', rate: 12.45, change: 0.03, changePercent: 0.24, direction: 'up' },
        { pair: 'MAD/CNY', rate: 1.36, change: 0.01, changePercent: 0.74, direction: 'up' },
        { pair: 'USD/MAD', rate: 0.1015, change: 0.0005, changePercent: 0.51, direction: 'up' },
        { pair: 'EUR/MAD', rate: 0.0930, change: 0.0003, changePercent: 0.28, direction: 'up' }
    ],
    volatility: [
        { currency: 'USD', volatility: 2.1, trend: 'decreasing' },
        { currency: 'EUR', volatility: 1.8, trend: 'stable' },
        { currency: 'GBP', volatility: 2.5, trend: 'increasing' },
        { currency: 'CNY', volatility: 1.2, trend: 'stable' }
    ],
    reserves: {
        total: 34.2,
        usd: 18.5,
        eur: 12.8,
        gold: 2.9,
        unit: 'Billion USD',
        change: 0.8,
        changePercent: 2.4
    }
}

const policyData = {
    regime: 'Managed Float',
    centralBank: 'Bank Al-Maghrib',
    lastIntervention: '2024-06-15',
    targetRange: '±2%',
    status: 'Stable'
}

export default function ExchangeRatesPage() {
    const [selectedCurrency, setSelectedCurrency] = useState('USD')
    const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y'>('3M')

    const formatNumber = (num: number, decimals: number = 4) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
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

    const getDirectionColor = (direction: string) => {
        switch (direction.toLowerCase()) {
            case 'up': return 'text-green-600'
            case 'down': return 'text-red-600'
            case 'stable': return 'text-gray-600'
            default: return 'text-gray-600'
        }
    }

    const getVolatilityColor = (volatility: number) => {
        if (volatility > 3.0) return 'text-red-600'
        if (volatility > 2.0) return 'text-orange-600'
        if (volatility > 1.0) return 'text-yellow-600'
        return 'text-green-600'
    }

    return (
        <>
            <Head>
                <title>Morocco Exchange Rates - Forex Data | Casablanca Insight</title>
                <meta name="description" content="Morocco exchange rates, currency pairs, forex trends, and foreign exchange analysis. Real-time data from Bank Al-Maghrib." />
            </Head>

            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <CurrencyDollarIcon className="h-8 w-8 text-yellow-600" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Morocco Exchange Rates</h1>
                            <p className="text-gray-600">Foreign Exchange and Currency Trends</p>
                        </div>
                    </div>

                    {/* Current Exchange Rate Card */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">MAD/USD Rate</h3>
                                <p className="text-3xl font-bold text-gray-900">{formatNumber(exchangeRateData.current.usd)}</p>
                                <p className="text-sm text-gray-500">{exchangeRateData.current.date}</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Daily Change</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-2xl font-bold ${getChangeColor(exchangeRateData.current.change)}`}>
                                        {exchangeRateData.current.change > 0 ? '+' : ''}{formatNumber(exchangeRateData.current.change, 4)}
                                    </span>
                                    {getChangeIcon(exchangeRateData.current.change)}
                                </div>
                                <p className="text-sm text-gray-500">{exchangeRateData.current.changePercent}%</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">MAD/EUR Rate</h3>
                                <p className="text-2xl font-bold text-gray-900">{formatNumber(exchangeRateData.current.eur)}</p>
                                <p className="text-sm text-gray-500">Euro Exchange</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">FX Reserves</h3>
                                <p className="text-2xl font-bold text-gray-900">{exchangeRateData.reserves.total} {exchangeRateData.reserves.unit}</p>
                                <p className="text-sm text-gray-500">+{exchangeRateData.reserves.changePercent}%</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Currency Pairs Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {exchangeRateData.currencyPairs.map((pair) => (
                        <div key={pair.pair} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">{pair.pair}</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-sm font-medium ${getChangeColor(pair.change)}`}>
                                        {pair.change > 0 ? '+' : ''}{formatNumber(pair.change, 4)}
                                    </span>
                                    {getChangeIcon(pair.change)}
                                </div>
                            </div>
                            <div className="text-center">
                                <p className="text-3xl font-bold text-gray-900">{formatNumber(pair.rate, 4)}</p>
                                <p className={`text-sm font-medium ${getDirectionColor(pair.direction)}`}>
                                    {pair.changePercent > 0 ? '+' : ''}{pair.changePercent}%
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Exchange Rate Trend Chart */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Exchange Rate Trend</h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setTimeframe('1M')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '1M'
                                            ? 'bg-yellow-100 text-yellow-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    1M
                                </button>
                                <button
                                    onClick={() => setTimeframe('3M')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '3M'
                                            ? 'bg-yellow-100 text-yellow-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    3M
                                </button>
                                <button
                                    onClick={() => setTimeframe('6M')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '6M'
                                            ? 'bg-yellow-100 text-yellow-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    6M
                                </button>
                                <button
                                    onClick={() => setTimeframe('1Y')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '1Y'
                                            ? 'bg-yellow-100 text-yellow-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    1Y
                                </button>
                            </div>
                        </div>
                        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                            <div className="text-center">
                                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                                <p className="text-gray-500">Interactive chart coming soon</p>
                                <p className="text-sm text-gray-400">Exchange rate trends over time</p>
                            </div>
                        </div>
                    </div>

                    {/* Currency Volatility */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Currency Volatility</h3>
                        <div className="space-y-3">
                            {exchangeRateData.volatility.map((currency) => (
                                <div key={currency.currency} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{currency.currency}</span>
                                            <span className="text-sm text-gray-500">{currency.volatility}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${getVolatilityColor(currency.volatility).replace('text-', 'bg-')}`}
                                                style={{ width: `${(currency.volatility / 4) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4">
                                        <span className={`text-sm font-medium ${getDirectionColor(currency.trend)}`}>
                                            {currency.trend}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* FX Reserves Breakdown */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Foreign Exchange Reserves</h3>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Total Reserves</h4>
                                <p className="text-2xl font-bold text-gray-900">{exchangeRateData.reserves.total} {exchangeRateData.reserves.unit}</p>
                                <p className="text-sm text-green-600">+{exchangeRateData.reserves.changePercent}%</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">USD Reserves</h4>
                                <p className="text-2xl font-bold text-gray-900">{exchangeRateData.reserves.usd} {exchangeRateData.reserves.unit}</p>
                                <p className="text-sm text-gray-500">54.1% of total</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">EUR Reserves</h4>
                                <p className="text-2xl font-bold text-gray-900">{exchangeRateData.reserves.eur} {exchangeRateData.reserves.unit}</p>
                                <p className="text-sm text-gray-500">37.4% of total</p>
                            </div>
                            <div className="text-center">
                                <h4 className="text-sm font-medium text-gray-900 mb-2">Gold Reserves</h4>
                                <p className="text-2xl font-bold text-gray-900">{exchangeRateData.reserves.gold} {exchangeRateData.reserves.unit}</p>
                                <p className="text-sm text-gray-500">8.5% of total</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Historical Data Table */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Historical Exchange Rates</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAD/USD</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAD/EUR</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAD/GBP</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MAD/CNY</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {exchangeRateData.historical.map((item) => (
                                    <tr key={item.date} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.date}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.usd)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.eur)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.gbp)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.cny)}</td>
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
                            <li>• MAD/USD rate at 9.85, showing slight depreciation</li>
                            <li>• FX reserves increased by 2.4% to $34.2 billion</li>
                            <li>• Euro remains the second-largest reserve currency</li>
                            <li>• Currency volatility is generally low and stable</li>
                            <li>• Bank Al-Maghrib maintains managed float regime</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Exchange Rate Policy</h3>
                        <div className="space-y-3 text-sm text-gray-600">
                            <div className="flex justify-between items-center">
                                <span>Regime Type</span>
                                <span className="font-medium">{policyData.regime}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>Central Bank</span>
                                <span className="font-medium">{policyData.centralBank}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>Last Intervention</span>
                                <span className="font-medium">{policyData.lastIntervention}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>Target Range</span>
                                <span className="font-medium">{policyData.targetRange}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span>Status</span>
                                <span className="font-medium">{policyData.status}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 