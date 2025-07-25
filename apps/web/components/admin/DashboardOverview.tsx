import { useState, useEffect } from 'react'
import {
    UsersIcon,
    EnvelopeIcon,
    CurrencyDollarIcon,
    ChartBarIcon,
    ArrowUpIcon,
    ArrowDownIcon
} from '@heroicons/react/24/outline'

interface DashboardStats {
    totalUsers: number
    activeUsers: number
    premiumUsers: number
    newsletterSubscribers: number
    paperTradingAccounts: number
    activeTraders: number
    monthlyRevenue: number
    userGrowth: number
    newsletterGrowth: number
    tradingGrowth: number
}

export default function DashboardOverview() {
    const [stats, setStats] = useState<DashboardStats>({
        totalUsers: 0,
        activeUsers: 0,
        premiumUsers: 0,
        newsletterSubscribers: 0,
        paperTradingAccounts: 0,
        activeTraders: 0,
        monthlyRevenue: 0,
        userGrowth: 0,
        newsletterGrowth: 0,
        tradingGrowth: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Fetch dashboard stats
        const fetchStats = async () => {
            try {
                const response = await fetch('/api/admin/dashboard/stats')
                if (response.ok) {
                    const data = await response.json()
                    setStats({
                        totalUsers: data.totalUsers,
                        activeUsers: data.activeUsers,
                        premiumUsers: data.premiumUsers,
                        newsletterSubscribers: data.newsletterSubscribers,
                        paperTradingAccounts: data.paperTradingAccounts,
                        activeTraders: data.activeTraders,
                        monthlyRevenue: data.monthlyRevenue,
                        userGrowth: data.userGrowth,
                        newsletterGrowth: data.newsletterGrowth,
                        tradingGrowth: data.tradingGrowth
                    })
                } else {
                    console.error('Failed to fetch dashboard stats')
                }
            } catch (error) {
                console.error('Error fetching dashboard stats:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchStats()
    }, [])

    const kpiCards = [
        {
            name: 'Total Users',
            value: stats.totalUsers.toLocaleString(),
            change: stats.userGrowth,
            changeType: 'increase',
            icon: UsersIcon,
            color: 'bg-blue-500'
        },
        {
            name: 'Premium Users',
            value: stats.premiumUsers.toLocaleString(),
            change: ((stats.premiumUsers / stats.totalUsers) * 100).toFixed(1),
            changeType: 'percentage',
            icon: CurrencyDollarIcon,
            color: 'bg-green-500'
        },
        {
            name: 'Newsletter Subscribers',
            value: stats.newsletterSubscribers.toLocaleString(),
            change: stats.newsletterGrowth,
            changeType: 'increase',
            icon: EnvelopeIcon,
            color: 'bg-purple-500'
        },
        {
            name: 'Active Paper Traders',
            value: stats.activeTraders.toLocaleString(),
            change: stats.tradingGrowth,
            changeType: 'increase',
            icon: ChartBarIcon,
            color: 'bg-orange-500'
        }
    ]

    if (loading) {
        return (
            <div className="animate-pulse">
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-gray-200 rounded"></div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <div className="h-4 bg-gray-200 rounded w-24"></div>
                                        <div className="h-8 bg-gray-200 rounded w-16 mt-2"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Monitor your platform's performance and user engagement
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {kpiCards.map((card) => (
                    <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className={`w-8 h-8 rounded-md flex items-center justify-center ${card.color}`}>
                                        <card.icon className="w-5 h-5 text-white" />
                                    </div>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">
                                            {card.name}
                                        </dt>
                                        <dd className="flex items-baseline">
                                            <div className="text-2xl font-semibold text-gray-900">
                                                {card.value}
                                            </div>
                                            {card.changeType === 'increase' && (
                                                <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                                                    <ArrowUpIcon className="self-center flex-shrink-0 h-4 w-4 text-green-500" />
                                                    <span className="sr-only">Increased by</span>
                                                    {card.change}%
                                                </div>
                                            )}
                                            {card.changeType === 'percentage' && (
                                                <div className="ml-2 flex items-baseline text-sm font-semibold text-gray-500">
                                                    <span>{card.change}%</span>
                                                </div>
                                            )}
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* User Growth Chart */}
                <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">User Growth</h3>
                    <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                        <p className="text-gray-500">Chart placeholder - User growth over time</p>
                    </div>
                </div>

                {/* Newsletter Signups */}
                <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Newsletter Signups</h3>
                    <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                        <p className="text-gray-500">Chart placeholder - Newsletter signups trend</p>
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
                </div>
                <div className="p-6">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                                    <UsersIcon className="w-4 h-4 text-green-600" />
                                </div>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-gray-900">
                                    <span className="font-medium">New user registered:</span> John Doe
                                </p>
                                <p className="text-sm text-gray-500">2 minutes ago</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                    <EnvelopeIcon className="w-4 h-4 text-blue-600" />
                                </div>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-gray-900">
                                    <span className="font-medium">Newsletter signup:</span> jane@example.com
                                </p>
                                <p className="text-sm text-gray-500">5 minutes ago</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                                    <CurrencyDollarIcon className="w-4 h-4 text-purple-600" />
                                </div>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-gray-900">
                                    <span className="font-medium">Premium upgrade:</span> user@example.com
                                </p>
                                <p className="text-sm text-gray-500">10 minutes ago</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
} 