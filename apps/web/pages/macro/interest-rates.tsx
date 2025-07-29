import Head from 'next/head'
import { useState } from 'react'
import { BanknotesIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CalendarIcon, DocumentTextIcon, ChartBarIcon } from '@heroicons/react/24/outline'

// Mock interest rate data - in real implementation this would come from API
const interestRateData = {
    policyRate: {
        current: 3.00,
        previous: 3.00,
        change: 0.00,
        lastChange: '2023-09-26',
        direction: 'stable'
    },
    rates: [
        { name: 'Policy Rate', current: 3.00, previous: 3.00, change: 0.00, unit: '%' },
        { name: 'Lending Rate', current: 3.25, previous: 3.25, change: 0.00, unit: '%' },
        { name: 'Deposit Rate', current: 2.75, previous: 2.75, change: 0.00, unit: '%' },
        { name: 'Repo Rate', current: 3.00, previous: 3.00, change: 0.00, unit: '%' },
        { name: 'Reverse Repo', current: 2.50, previous: 2.50, change: 0.00, unit: '%' }
    ],
    yieldCurve: [
        { maturity: '3M', yield: 2.85, change: 0.05 },
        { maturity: '6M', yield: 3.10, change: 0.08 },
        { maturity: '1Y', yield: 3.25, change: 0.12 },
        { maturity: '2Y', yield: 3.45, change: 0.15 },
        { maturity: '3Y', yield: 3.65, change: 0.18 },
        { maturity: '5Y', yield: 3.85, change: 0.20 },
        { maturity: '10Y', yield: 4.15, change: 0.25 }
    ],
    historical: [
        { date: '2023-01', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2023-03', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2023-06', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2023-09', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2023-12', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2024-03', policy: 3.00, lending: 3.25, deposit: 2.75 },
        { date: '2024-06', policy: 3.00, lending: 3.25, deposit: 2.75 }
    ]
}

const monetaryPolicy = {
    lastMeeting: '2024-06-25',
    nextMeeting: '2024-09-24',
    status: 'Stable',
    outlook: 'Neutral',
    inflationTarget: '2.0%',
    currentInflation: '2.8%'
}

export default function InterestRatesPage() {
    const [selectedRate, setSelectedRate] = useState('policy')
    const [timeframe, setTimeframe] = useState<'1Y' | '2Y' | '5Y'>('1Y')

    const formatNumber = (num: number) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num)
    }

    const getChangeColor = (change: number) => {
        if (change > 0) return 'text-red-600'
        if (change < 0) return 'text-green-600'
        return 'text-gray-600'
    }

    const getChangeIcon = (change: number) => {
        if (change > 0) return <ArrowTrendingUpIcon className="h-4 w-4" />
        if (change < 0) return <ArrowTrendingDownIcon className="h-4 w-4" />
        return null
    }

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'stable': return 'text-green-600'
            case 'increasing': return 'text-red-600'
            case 'decreasing': return 'text-blue-600'
            default: return 'text-gray-600'
        }
    }

    return (
        <>
            <Head>
                <title>Morocco Interest Rates - Monetary Policy | Casablanca Insight</title>
                <meta name="description" content="Morocco interest rates, central bank policy, yield curves, and monetary policy analysis. Real-time data from Bank Al-Maghrib." />
            </Head>

            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <BanknotesIcon className="h-8 w-8 text-green-600" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Morocco Interest Rates</h1>
                            <p className="text-gray-600">Central Bank Policy and Monetary Indicators</p>
                        </div>
                    </div>

                    {/* Current Policy Rate Card */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Policy Rate</h3>
                                <p className="text-3xl font-bold text-gray-900">{formatNumber(interestRateData.policyRate.current)}%</p>
                                <p className="text-sm text-gray-500">Current Rate</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Last Change</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-2xl font-bold ${getChangeColor(interestRateData.policyRate.change)}`}>
                                        {interestRateData.policyRate.change > 0 ? '+' : ''}{formatNumber(interestRateData.policyRate.change)}%
                                    </span>
                                    {getChangeIcon(interestRateData.policyRate.change)}
                                </div>
                                <p className="text-sm text-gray-500">{interestRateData.policyRate.lastChange}</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Status</h3>
                                <p className={`text-lg font-semibold ${getStatusColor(interestRateData.policyRate.direction)}`}>
                                    {interestRateData.policyRate.direction}
                                </p>
                                <p className="text-sm text-gray-500">Monetary Policy</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Source</h3>
                                <p className="text-lg font-semibold text-gray-900">Bank Al-Maghrib</p>
                                <p className="text-sm text-gray-500">Central Bank</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Key Rates Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {interestRateData.rates.map((rate) => (
                        <div key={rate.name} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">{rate.name}</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-sm font-medium ${getChangeColor(rate.change)}`}>
                                        {rate.change > 0 ? '+' : ''}{formatNumber(rate.change)}%
                                    </span>
                                    {getChangeIcon(rate.change)}
                                </div>
                            </div>
                            <div className="text-center">
                                <p className="text-3xl font-bold text-gray-900">{formatNumber(rate.current)}%</p>
                                <p className="text-sm text-gray-500">Current Rate</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Yield Curve */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Government Bond Yield Curve</h3>
                        <div className="space-y-3">
                            {interestRateData.yieldCurve.map((yield_) => (
                                <div key={yield_.maturity} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{yield_.maturity}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(yield_.yield)}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-green-600 h-2 rounded-full"
                                                style={{ width: `${(yield_.yield / 5) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(yield_.change)}`}>
                                            {yield_.change > 0 ? '+' : ''}{formatNumber(yield_.change)}%
                                        </span>
                                        {getChangeIcon(yield_.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Monetary Policy Status */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monetary Policy Status</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Last Meeting</span>
                                <span className="text-sm font-medium text-gray-900">{monetaryPolicy.lastMeeting}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Next Meeting</span>
                                <span className="text-sm font-medium text-gray-900">{monetaryPolicy.nextMeeting}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Policy Status</span>
                                <span className={`text-sm font-medium ${getStatusColor(monetaryPolicy.status)}`}>
                                    {monetaryPolicy.status}
                                </span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Outlook</span>
                                <span className="text-sm font-medium text-gray-900">{monetaryPolicy.outlook}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Inflation Target</span>
                                <span className="text-sm font-medium text-gray-900">{monetaryPolicy.inflationTarget}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Current Inflation</span>
                                <span className="text-sm font-medium text-gray-900">{monetaryPolicy.currentInflation}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Historical Data Table */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Historical Interest Rates</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Policy Rate (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lending Rate (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deposit Rate (%)</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {interestRateData.historical.map((item) => (
                                    <tr key={item.date} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.date}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.policy)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.lending)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.deposit)}</td>
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
                            <li>• Bank Al-Maghrib maintains policy rate at 3.00% since September 2023</li>
                            <li>• Yield curve shows normal upward slope with 10Y at 4.15%</li>
                            <li>• Monetary policy remains accommodative to support economic recovery</li>
                            <li>• Inflation at 2.8% is above the 2.0% target but within acceptable range</li>
                            <li>• Next policy meeting scheduled for September 24, 2024</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h3>
                        <div className="space-y-3 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Bank Al-Maghrib - Official rates</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Ministry of Finance - Government bonds</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Casablanca Stock Exchange - Market rates</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>IMF - International comparisons</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 