import Head from 'next/head'
import { useState } from 'react'
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CalendarIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

// Mock GDP data - in real implementation this would come from API
const gdpData = {
    current: {
        value: 134.18,
        unit: 'Billion USD',
        period: '2023',
        change: 3.5,
        changePercent: 3.5,
        previous: 129.62
    },
    historical: [
        { year: 2019, value: 119.7, growth: 2.6 },
        { year: 2020, value: 114.7, growth: -7.2 },
        { year: 2021, value: 132.7, growth: 7.9 },
        { year: 2022, value: 129.6, growth: 1.3 },
        { year: 2023, value: 134.2, growth: 3.5 }
    ],
    quarterly: [
        { quarter: '2023-Q1', value: 32.1, growth: 3.2 },
        { quarter: '2023-Q2', value: 33.2, growth: 3.8 },
        { quarter: '2023-Q3', value: 34.5, growth: 4.1 },
        { quarter: '2023-Q4', value: 34.4, growth: 3.1 }
    ],
    sectors: [
        { sector: 'Agriculture', contribution: 12.3, growth: 2.1 },
        { sector: 'Industry', contribution: 26.8, growth: 4.2 },
        { sector: 'Services', contribution: 47.2, growth: 3.8 },
        { sector: 'Mining', contribution: 8.7, growth: 5.1 },
        { sector: 'Construction', contribution: 5.0, growth: 2.9 }
    ]
}

const forecasts = [
    { source: 'IMF', year: '2024', growth: 3.2 },
    { source: 'World Bank', year: '2024', growth: 3.1 },
    { source: 'Bank Al-Maghrib', year: '2024', growth: 3.4 },
    { source: 'Ministry of Finance', year: '2024', growth: 3.5 }
]

export default function GDPPage() {
    const [timeframe, setTimeframe] = useState<'annual' | 'quarterly'>('annual')
    const [selectedYear, setSelectedYear] = useState(2023)

    const formatNumber = (num: number) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(num)
    }

    const getGrowthColor = (growth: number) => {
        if (growth > 0) return 'text-green-600'
        if (growth < 0) return 'text-red-600'
        return 'text-gray-600'
    }

    const getGrowthIcon = (growth: number) => {
        if (growth > 0) return <ArrowTrendingUpIcon className="h-4 w-4" />
        if (growth < 0) return <ArrowTrendingDownIcon className="h-4 w-4" />
        return null
    }

    return (
        <>
            <Head>
                <title>Morocco GDP - Economic Indicators | Casablanca Insight</title>
                <meta name="description" content="Morocco GDP data, growth rates, sector analysis, and economic forecasts. Real-time data from official sources." />
            </Head>

            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <ChartBarIcon className="h-8 w-8 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Morocco GDP</h1>
                            <p className="text-gray-600">Gross Domestic Product and Economic Growth</p>
                        </div>
                    </div>

                    {/* Current GDP Card */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Current GDP</h3>
                                <p className="text-3xl font-bold text-gray-900">{formatNumber(gdpData.current.value)} {gdpData.current.unit}</p>
                                <p className="text-sm text-gray-500">{gdpData.current.period}</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Annual Growth</h3>
                                <div className="flex items-center gap-2">
                                    <span className={`text-2xl font-bold ${getGrowthColor(gdpData.current.changePercent)}`}>
                                        {gdpData.current.changePercent > 0 ? '+' : ''}{gdpData.current.changePercent}%
                                    </span>
                                    {getGrowthIcon(gdpData.current.changePercent)}
                                </div>
                                <p className="text-sm text-gray-500">vs {gdpData.current.previous} in 2022</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-medium text-gray-500">Source</h3>
                                <p className="text-lg font-semibold text-gray-900">World Bank</p>
                                <p className="text-sm text-gray-500">Last updated: July 2024</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* GDP Growth Chart */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">GDP Growth Trend</h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setTimeframe('annual')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === 'annual'
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    Annual
                                </button>
                                <button
                                    onClick={() => setTimeframe('quarterly')}
                                    className={`px-3 py-1 text-sm rounded ${timeframe === 'quarterly'
                                            ? 'bg-blue-100 text-blue-700'
                                            : 'bg-gray-100 text-gray-600'
                                        }`}
                                >
                                    Quarterly
                                </button>
                            </div>
                        </div>
                        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                            <div className="text-center">
                                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                                <p className="text-gray-500">Interactive chart coming soon</p>
                                <p className="text-sm text-gray-400">GDP growth over time</p>
                            </div>
                        </div>
                    </div>

                    {/* Sector Contribution */}
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector Contribution to GDP</h3>
                        <div className="space-y-3">
                            {gdpData.sectors.map((sector) => (
                                <div key={sector.sector} className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-900">{sector.sector}</span>
                                            <span className="text-sm text-gray-500">{sector.contribution}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-blue-600 h-2 rounded-full"
                                                style={{ width: `${sector.contribution}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex items-center gap-1">
                                        <span className={`text-sm font-medium ${getGrowthColor(sector.growth)}`}>
                                            {sector.growth > 0 ? '+' : ''}{sector.growth}%
                                        </span>
                                        {getGrowthIcon(sector.growth)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Historical Data Table */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Historical GDP Data</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">GDP (Billion USD)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Growth Rate (%)</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {gdpData.historical.map((item) => (
                                    <tr key={item.year} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.year}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.value)}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-sm font-medium ${getGrowthColor(item.growth)}`}>
                                                    {item.growth > 0 ? '+' : ''}{item.growth}%
                                                </span>
                                                {getGrowthIcon(item.growth)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {item.year > 2019 ? `${item.growth > 0 ? '+' : ''}${item.growth}%` : '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Forecasts */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900">Economic Forecasts</h3>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {forecasts.map((forecast) => (
                                <div key={forecast.source} className="text-center p-4 border border-gray-200 rounded-lg">
                                    <h4 className="text-sm font-medium text-gray-900">{forecast.source}</h4>
                                    <p className="text-2xl font-bold text-blue-600">{forecast.growth}%</p>
                                    <p className="text-sm text-gray-500">{forecast.year} Growth</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Additional Information */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li>• Morocco's GDP grew by 3.5% in 2023, recovering from pandemic impacts</li>
                            <li>• Services sector remains the largest contributor at 47.2% of GDP</li>
                            <li>• Industrial sector showed strong growth of 4.2% in 2023</li>
                            <li>• Mining sector experienced the highest growth rate at 5.1%</li>
                            <li>• Agriculture sector contributed 12.3% with 2.1% growth</li>
                        </ul>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h3>
                        <div className="space-y-3 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>World Bank - International GDP data</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>HCP - National statistics</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Bank Al-Maghrib - Economic reports</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <DocumentTextIcon className="h-4 w-4 text-gray-400" />
                                <span>Ministry of Finance - Official data</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
} 