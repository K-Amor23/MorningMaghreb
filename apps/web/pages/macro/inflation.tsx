import Head from 'next/head'
import { useState } from 'react'
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, ChartBarIcon, DocumentTextIcon, CalendarIcon } from '@heroicons/react/24/outline'

// Mock inflation data - in real implementation this would come from API
const inflationData = {
    current: {
        headline: 2.8,
        core: 2.5,
        food: 3.2,
        energy: 1.8,
        services: 2.9,
        goods: 2.6,
        housing: 2.8,
        transportation: 2.1,
        health: 3.5,
        period: 'June 2024',
        previous: 2.9,
        change: -0.1
    },
    historical: [
        { month: '2024-01', headline: 3.1, core: 2.8, food: 3.5, energy: 2.1 },
        { month: '2024-02', headline: 3.0, core: 2.7, food: 3.4, energy: 2.0 },
        { month: '2024-03', headline: 2.9, core: 2.6, food: 3.3, energy: 1.9 },
        { month: '2024-04', headline: 2.9, core: 2.6, food: 3.2, energy: 1.9 },
        { month: '2024-05', headline: 2.9, core: 2.5, food: 3.2, energy: 1.8 },
        { month: '2024-06', headline: 2.8, core: 2.5, food: 3.2, energy: 1.8 }
    ],
    components: [
        { category: 'Food & Beverages', weight: 32.5, inflation: 3.2, change: -0.1 },
        { category: 'Housing & Utilities', weight: 18.2, inflation: 2.8, change: 0.0 },
        { category: 'Transportation', weight: 12.8, inflation: 2.1, change: -0.2 },
        { category: 'Health', weight: 8.5, inflation: 3.5, change: 0.1 },
        { category: 'Education', weight: 7.2, inflation: 2.9, change: 0.0 },
        { category: 'Recreation', weight: 6.1, inflation: 2.4, change: -0.1 },
        { category: 'Clothing', weight: 5.8, inflation: 2.6, change: 0.0 },
        { category: 'Other', weight: 8.9, inflation: 2.7, change: -0.1 }
    ],
    regional: [
        { region: 'Casablanca-Settat', inflation: 2.9, change: -0.1 },
        { region: 'Rabat-Salé-Kénitra', inflation: 2.7, change: -0.1 },
        { region: 'Marrakech-Safi', inflation: 2.8, change: -0.2 },
        { region: 'Fès-Meknès', inflation: 2.6, change: -0.1 },
        { region: 'Tanger-Tétouan-Al Hoceima', inflation: 2.9, change: -0.1 },
        { region: 'Souss-Massa', inflation: 2.7, change: -0.2 },
        { region: 'Oriental', inflation: 2.8, change: -0.1 },
        { region: 'Béni Mellal-Khénifra', inflation: 2.6, change: -0.1 }
    ]
}

const targetData = {
    centralBank: 2.0,
    current: 2.8,
    status: 'Above Target',
    tolerance: 1.0
}

export default function InflationPage() {
    const [selectedComponent, setSelectedComponent] = useState('headline')
    const [timeframe, setTimeframe] = useState<'6M' | '1Y' | '2Y'>('1Y')

    const formatNumber = (num: number) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
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
            case 'above target': return 'text-red-600'
            case 'below target': return 'text-green-600'
            case 'at target': return 'text-blue-600'
            default: return 'text-gray-600'
        }
    }

    const getInflationColor = (inflation: number) => {
        if (inflation > 4.0) return 'text-red-600'
        if (inflation > 2.5) return 'text-orange-600'
        if (inflation > 1.5) return 'text-green-600'
        return 'text-blue-600'
    }

    return (
        <>
            <Head>
                <title>Morocco Inflation - CPI Data | Casablanca Insight</title>
                <meta name="description" content="Morocco inflation data, CPI trends, core inflation, and price analysis. Real-time data from HCP and Bank Al-Maghrib." />
            </Head>

            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-orange-100 rounded-lg">
                            <ArrowTrendingUpIcon className="h-8 w-8 text-orange-600" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Morocco Inflation</h1>
                            <p className="text-gray-600">Consumer Price Index and Price Trends</p>
                        </div>
                    </div>

                    {/* Current Inflation Card */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Headline Inflation</h3>
                                <p className={`text-3xl font-bold ${getInflationColor(inflationData.current.headline)}`}>
                                    {formatNumber(inflationData.current.headline)}%
                                </p>
                                <p className="text-sm text-gray-500">{inflationData.current.period}</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Monthly Change</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-2xl font-bold ${getChangeColor(inflationData.current.change)}`}>
                                        {inflationData.current.change > 0 ? '+' : ''}{formatNumber(inflationData.current.change)}%
                                    </span>
                                    {getChangeIcon(inflationData.current.change)}
                                </div>
                                <p className="text-sm text-gray-500">vs {formatNumber(inflationData.current.previous)}%</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Core Inflation</h3>
                                <p className={`text-2xl font-bold ${getInflationColor(inflationData.current.core)}`}>
                                    {formatNumber(inflationData.current.core)}%
                                </p>
                                <p className="text-sm text-gray-500">Excluding food & energy</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Target Status</h3>
                                <p className={`text-lg font-semibold ${getStatusColor(targetData.status)}`}>
                                    {targetData.status}
                                </p>
                                <p className="text-sm text-gray-500">Target: {targetData.centralBank}%</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Key Inflation Components */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {[
                        { name: 'Food & Beverages', value: inflationData.current.food, weight: 32.5 },
                        { name: 'Housing & Utilities', value: inflationData.current.housing, weight: 18.2 },
                        { name: 'Transportation', value: inflationData.current.transportation, weight: 12.8 },
                        { name: 'Health', value: inflationData.current.health, weight: 8.5 }
                    ].map((component) => (
                        <div key={component.name} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">{component.name}</h3>
                                <span className="text-sm text-gray-500">{component.weight}%</span>
                            </div>
                            <div className="text-center">
                                <p className={`text-3xl font-bold ${getInflationColor(component.value)}`}>
                                    {formatNumber(component.value)}%
                                </p>
                                <p className="text-sm text-gray-500">Inflation Rate</p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Inflation Trend Chart */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Inflation Trend</h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setTimeframe('6M')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '6M'
                                        ? 'bg-orange-100 text-orange-700'
                                        : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    6M
                                </button>
                                <button
                                    onClick={() => setTimeframe('1Y')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '1Y'
                                        ? 'bg-orange-100 text-orange-700'
                                        : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    1Y
                                </button>
                                <button
                                    onClick={() => setTimeframe('2Y')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === '2Y'
                                        ? 'bg-orange-100 text-orange-700'
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
                                <p className="text-sm text-gray-400">Inflation trend over time</p>
                            </div>
                        </div>
                    </div>

                    {/* CPI Components Breakdown */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">CPI Components</h3>
                        <div className="space-y-3">
                            {inflationData.components.map((component) => (
                                <div key={component.category} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{component.category}</span>
                                            <span className="text-sm text-gray-500">{formatNumber(component.inflation)}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-orange-600 h-2 rounded-full"
                                                style={{ width: `${(component.weight / 35) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getChangeColor(component.change)}`}>
                                            {component.change > 0 ? '+' : ''}{formatNumber(component.change)}%
                                        </span>
                                        {getChangeIcon(component.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Regional Inflation */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Regional Inflation</h3>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {inflationData.regional.map((region) => (
                                <div key={region.region} className="text-center p-4 border border-gray-200 rounded-lg">
                                    <h4 className="text-sm font-medium text-gray-900 mb-2">{region.region}</h4>
                                    <p className={`text-2xl font-bold ${getInflationColor(region.inflation)}`}>
                                        {formatNumber(region.inflation)}%
                                    </p>
                                    <div className="flex items-center justify-center gap-1 mt-1">
                                        <span className={`text-sm ${getChangeColor(region.change)}`}>
                                            {region.change > 0 ? '+' : ''}{formatNumber(region.change)}%
                                        </span>
                                        {getChangeIcon(region.change)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Historical Data Table */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Historical Inflation Data</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Headline (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Core (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Food (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Energy (%)</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {inflationData.historical.map((item) => (
                                    <tr key={item.month} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.month}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.headline)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.core)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.food)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.energy)}</td>
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
                            <li>• Headline inflation at 2.8% is above the 2.0% target</li>
                            <li>• Core inflation at 2.5% shows underlying price stability</li>
                            <li>• Food prices remain the largest contributor to inflation</li>
                            <li>• Energy prices have stabilized at 1.8%</li>
                            <li>• Regional variations show Casablanca-Settat highest at 2.9%</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h3>
                        <div className="space-y-3 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>HCP - National CPI data</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Bank Al-Maghrib - Core inflation</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Ministry of Finance - Price indices</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Regional statistical offices</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 