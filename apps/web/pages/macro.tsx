import Head from 'next/head'
import { ChartBarIcon, CurrencyDollarIcon, ArrowTrendingUpIcon, BanknotesIcon, UserGroupIcon, GlobeAltIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'

const macroIndicators = [
    {
        name: 'Policy Rate',
        value: '3.00%',
        prev: '3.00%',
        unit: '%',
        date: '2024-07-01',
        source: 'Bank Al-Maghrib',
        icon: CurrencyDollarIcon,
        color: 'bg-blue-500',
        description: 'Central bank benchmark rate'
    },
    {
        name: 'Inflation Rate',
        value: '2.8%',
        prev: '2.9%',
        unit: '%',
        date: '2024-06-01',
        source: 'HCP',
        icon: ArrowTrendingUpIcon,
        color: 'bg-orange-500',
        description: 'Consumer price index YoY'
    },
    {
        name: 'FX Reserves',
        value: '$34.2B',
        prev: '$33.4B',
        unit: 'USD',
        date: '2024-06-30',
        source: 'Bank Al-Maghrib',
        icon: BanknotesIcon,
        color: 'bg-green-500',
        description: 'Foreign exchange reserves'
    },
    {
        name: 'GDP Growth',
        value: '3.5%',
        prev: '3.2%',
        unit: '%',
        date: '2023',
        source: 'World Bank',
        icon: ChartBarIcon,
        color: 'bg-purple-500',
        description: 'Annual GDP growth rate'
    },
    {
        name: 'Unemployment Rate',
        value: '11.8%',
        prev: '12.1%',
        unit: '%',
        date: '2024-Q1',
        source: 'HCP',
        icon: UserGroupIcon,
        color: 'bg-red-500',
        description: 'National unemployment rate'
    },
    {
        name: 'Trade Balance',
        value: '-$2.1B',
        prev: '-$1.8B',
        unit: 'USD',
        date: '2024-06',
        source: 'Bank Al-Maghrib',
        icon: GlobeAltIcon,
        color: 'bg-casablanca-blue',
        description: 'Monthly trade deficit'
    },
    {
        name: 'Government Debt',
        value: '69.7%',
        prev: '70.2%',
        unit: '% of GDP',
        date: '2023',
        source: 'Ministry of Finance',
        icon: ChartBarIcon,
        color: 'bg-gray-700',
        description: 'Central government debt'
    },
    {
        name: 'MAD/USD',
        value: '9.85',
        prev: '9.90',
        unit: '',
        date: '2024-07-24',
        source: 'Bank Al-Maghrib',
        icon: CurrencyDollarIcon,
        color: 'bg-yellow-500',
        description: 'Dirham to US Dollar'
    }
]

const allIndicators = [
    ...macroIndicators,
    // Add more mock indicators as needed
]

export default function MacroPage() {
    const [sortKey, setSortKey] = useState('name')
    const [sortAsc, setSortAsc] = useState(true)

    const sortedIndicators = [...allIndicators].sort((a, b) => {
        if (a[sortKey] < b[sortKey]) return sortAsc ? -1 : 1
        if (a[sortKey] > b[sortKey]) return sortAsc ? 1 : -1
        return 0
    })

    const handleSort = (key: string) => {
        if (sortKey === key) setSortAsc(!sortAsc)
        else {
            setSortKey(key)
            setSortAsc(true)
        }
    }

    const downloadCSV = () => {
        const header = 'Indicator,Value,Previous,Unit,Date,Source\n'
        const rows = allIndicators.map(i => `${i.name},${i.value},${i.prev},${i.unit},${i.date},${i.source}`).join('\n')
        const csv = header + rows
        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'morocco_macro_indicators.csv'
        a.click()
        URL.revokeObjectURL(url)
    }

    return (
        <>
            <Head>
                <title>Morocco Macro Dashboard - Casablanca Insight</title>
                <meta name="description" content="Macroeconomic indicators and analysis for Morocco" />
            </Head>
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Hero Section */}
                <div className="flex items-center mb-8 gap-4">
                    <span className="text-4xl">🇲🇦</span>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Morocco Macroeconomic Dashboard</h1>
                        <p className="text-gray-500 max-w-2xl mt-1">Key indicators, trends, and analysis for Morocco’s economy. Data sourced from Bank Al-Maghrib, HCP, World Bank, and more. Updated regularly for investors, analysts, and policymakers.</p>
                    </div>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                    {macroIndicators.map((card) => (
                        <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className={`w-8 h-8 rounded-md flex items-center justify-center ${card.color}`}>
                                        <card.icon className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">{card.name}</dt>
                                            <dd className="text-2xl font-semibold text-gray-900">{card.value}</dd>
                                            <dd className="text-xs text-gray-500">{card.description}</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-8">
                    <div className="bg-white shadow rounded-lg p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Policy Rate Trend</h3>
                        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                            <p className="text-gray-500">Chart placeholder - Policy rate over time</p>
                        </div>
                    </div>
                    <div className="bg-white shadow rounded-lg p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Inflation Rate Trend</h3>
                        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                            <p className="text-gray-500">Chart placeholder - Inflation rate over time</p>
                        </div>
                    </div>
                </div>

                {/* Indicators Table & Download */}
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xl font-semibold text-gray-900">All Macroeconomic Indicators</h2>
                    <button onClick={downloadCSV} className="flex items-center bg-casablanca-blue text-white px-4 py-2 rounded hover:bg-blue-700">
                        <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                        Download CSV
                    </button>
                </div>
                <div className="overflow-x-auto bg-white shadow rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('name')}>Indicator</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('value')}>Value</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('prev')}>Previous</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('unit')}>Unit</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('date')}>Date</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('source')}>Source</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {sortedIndicators.map((ind) => (
                                <tr key={ind.name}>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{ind.name}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{ind.value}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{ind.prev}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{ind.unit}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{ind.date}</td>
                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{ind.source}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                    <span>Sources: Bank Al-Maghrib, HCP, World Bank, Ministry of Finance, TradingEconomics</span>
                </div>
            </div>
        </>
    )
} 