import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import { useState, useEffect } from 'react'
import {
    CurrencyDollarIcon,
    ChartBarIcon,
    CalendarIcon,
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon,
    ClockIcon
} from '@heroicons/react/24/outline'

interface Bond {
    id: string
    name: string
    ticker: string
    isin: string
    issuer: string
    issuer_name: string
    bond_type: string
    face_value: number
    coupon_rate: number
    maturity_date: string
    issue_size: number
    credit_rating: string
    price: number
    yield_to_maturity: number
    current_yield: number
    modified_duration: number
    change_percent: number
}

interface YieldCurvePoint {
    maturity_months: number
    yield: number
    date: string
}

interface IssuanceCalendar {
    id: string
    issuer: string
    bond_name: string
    expected_issue_date: string
    expected_maturity_date: string
    expected_size: number
    expected_coupon_rate: number
    expected_rating: string
    status: string
}

export default function Bonds() {
    const [bonds, setBonds] = useState<Bond[]>([])
    const [yieldCurve, setYieldCurve] = useState<YieldCurvePoint[]>([])
    const [calendar, setCalendar] = useState<IssuanceCalendar[]>([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('all')

    useEffect(() => {
        fetchBondData()
    }, [])

    const fetchBondData = async () => {
        try {
            setLoading(true)

            // Fetch bonds data
            const bondsResponse = await fetch('/api/markets/bonds')
            const bondsData = await bondsResponse.json()
            setBonds(bondsData.bonds || [])

            // Fetch yield curve data
            const yieldResponse = await fetch('/api/markets/yield-curve')
            const yieldData = await yieldResponse.json()
            setYieldCurve(yieldData.yield_curve || [])

            // Fetch issuance calendar
            const calendarResponse = await fetch('/api/markets/bond-calendar')
            const calendarData = await calendarResponse.json()
            setCalendar(calendarData.calendar || [])

        } catch (error) {
            console.error('Error fetching bond data:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'MAD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount)
    }

    const formatPercent = (value: number) => {
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        })
    }

    const getMaturityYears = (maturityDate: string) => {
        const maturity = new Date(maturityDate)
        const today = new Date()
        const diffTime = maturity.getTime() - today.getTime()
        const diffYears = diffTime / (1000 * 60 * 60 * 24 * 365.25)
        return Math.max(0, parseFloat(diffYears.toFixed(1)))
    }

    const filteredBonds = bonds.filter(bond => {
        if (activeTab === 'all') return true
        if (activeTab === 'government') return bond.bond_type === 'government'
        if (activeTab === 'corporate') return bond.bond_type === 'corporate'
        return true
    })

    const tabs = [
        { id: 'all', name: 'All Bonds', count: bonds.length },
        { id: 'government', name: 'Government', count: bonds.filter(b => b.bond_type === 'government').length },
        { id: 'corporate', name: 'Corporate', count: bonds.filter(b => b.bond_type === 'corporate').length }
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
                <title>Bonds - Casablanca Insight</title>
                <meta name="description" content="Moroccan bond market data, yield curves, and issuance calendar" />
            </Head>

            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <Header />
                <TickerBar />

                <main className="px-4 py-6 max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="mb-6">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Bonds</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            Moroccan government and corporate bonds, yield curves, and issuance calendar
                        </p>
                    </div>

                    {/* Yield Curve Summary */}
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                        {yieldCurve.slice(0, 4).map((point) => (
                            <div key={point.maturity_months} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">
                                            {point.maturity_months}M Yield
                                        </p>
                                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                            {point.yield.toFixed(2)}%
                                        </p>
                                    </div>
                                    <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
                                </div>
                            </div>
                        ))}
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
                        {/* Bonds List */}
                        <div className="lg:col-span-2">
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                                        Bond Prices & Yields
                                    </h2>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                        <thead className="bg-gray-50 dark:bg-gray-700">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Bond
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Type
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Coupon
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Maturity
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Price
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    YTM
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                                    Change
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                            {filteredBonds.map((bond) => (
                                                <tr key={bond.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                                                                {bond.name}
                                                            </div>
                                                            <div className="text-sm text-gray-500 dark:text-gray-400">
                                                                {bond.ticker}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${bond.bond_type === 'government'
                                                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                                            : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                                            }`}>
                                                            {bond.bond_type}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {(bond.coupon_rate * 100).toFixed(2)}%
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {getMaturityYears(bond.maturity_date)}Y
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {formatCurrency(bond.price)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                        {bond.yield_to_maturity.toFixed(2)}%
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`text-sm font-medium ${bond.change_percent >= 0
                                                            ? 'text-green-600 dark:text-green-400'
                                                            : 'text-red-600 dark:text-red-400'
                                                            }`}>
                                                            {formatPercent(bond.change_percent)}
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
                            {/* Issuance Calendar */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                                        <CalendarIcon className="h-5 w-5 mr-2" />
                                        Issuance Calendar
                                    </h3>
                                </div>
                                <div className="p-6">
                                    {calendar.length > 0 ? (
                                        <div className="space-y-4">
                                            {calendar.slice(0, 5).map((item) => (
                                                <div key={item.id} className="border-l-4 border-casablanca-blue pl-4">
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                                                        {item.bond_name}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        {item.issuer} • {formatDate(item.expected_issue_date)}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        {(item.expected_coupon_rate * 100).toFixed(2)}% • {formatCurrency(item.expected_size)}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-gray-500 dark:text-gray-400 text-sm">
                                            No upcoming issuances
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
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Total Bonds</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">{bonds.length}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Government</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {bonds.filter(b => b.bond_type === 'government').length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Corporate</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {bonds.filter(b => b.bond_type === 'corporate').length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-500 dark:text-gray-400">Avg YTM</span>
                                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                                            {(bonds.reduce((sum, b) => sum + b.yield_to_maturity, 0) / bonds.length).toFixed(2)}%
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