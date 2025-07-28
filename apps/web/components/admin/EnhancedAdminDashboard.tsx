import { useState, useEffect } from 'react'
import {
    UsersIcon,
    ChartBarIcon,
    CogIcon,
    DatabaseIcon,
    TrendingUpIcon,
    ExclamationTriangleIcon,
    CheckCircleIcon,
    ClockIcon,
    ServerIcon,
    GlobeAltIcon
} from '@heroicons/react/24/outline'

interface UserAnalytics {
    total_activities: number
    unique_users: number
    unique_sessions: number
    avg_session_duration_seconds: number
    most_visited_pages: Array<{ page: string; visits: number }>
    action_distribution: Array<{ action: string; count: number }>
    daily_activity_trend: Array<{ date: string; count: number }>
}

interface DataIngestionSummary {
    total_jobs: number
    successful_jobs: number
    failed_jobs: number
    success_rate: number
    total_records_processed: number
    total_records_successful: number
    avg_processing_time_ms: number
    source_success_rates: Array<{ source: string; success_rate: number }>
    recent_activity: Array<{
        id: string
        source_name: string
        data_type: string
        records_processed: number
        records_successful: number
        records_failed: number
        processing_time_ms: number
        started_at: string
        completed_at: string | null
        success_rate: number
    }>
}

interface SystemPerformance {
    latest_metrics: Array<{
        metric_name: string
        value: number
        unit: string
        component: string
        severity: string
        recorded_at: string
    }>
    averages: {
        response_time_ms: number
        cpu_usage_percent: number
        memory_usage_percent: number
    }
    error_count: number
    performance_trends: Array<{
        hour: string
        avg_response_time: number
    }>
}

interface AdminDashboardOverview {
    user_metrics: {
        total_users: number
        active_users_30d: number
        user_growth_rate: number
    }
    data_quality: {
        freshness_score: number
        overall_quality: string
    }
    system_health: {
        recent_errors: number
        status: string
        uptime_percentage: number
    }
    data_ingestion: {
        recent_jobs: number
        success_rate: number
        status: string
    }
    last_updated: string
}

export default function EnhancedAdminDashboard() {
    const [overview, setOverview] = useState<AdminDashboardOverview | null>(null)
    const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null)
    const [dataIngestion, setDataIngestion] = useState<DataIngestionSummary | null>(null)
    const [systemPerformance, setSystemPerformance] = useState<SystemPerformance | null>(null)
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'ingestion' | 'performance'>('overview')

    useEffect(() => {
        fetchDashboardData()
    }, [])

    const fetchDashboardData = async () => {
        try {
            setLoading(true)
            const [overviewData, analyticsData, ingestionData, performanceData] = await Promise.all([
                fetch('/api/admin/dashboard/overview').then(res => res.json()),
                fetch('/api/admin/dashboard/analytics/engagement?days=30').then(res => res.json()),
                fetch('/api/admin/dashboard/ingestion/summary?days=30').then(res => res.json()),
                fetch('/api/admin/dashboard/performance/summary?hours=24').then(res => res.json())
            ])

            setOverview(overviewData)
            setUserAnalytics(analyticsData)
            setDataIngestion(ingestionData)
            setSystemPerformance(performanceData)
        } catch (error) {
            console.error('Error fetching dashboard data:', error)
        } finally {
            setLoading(false)
        }
    }

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'healthy':
            case 'good':
                return 'text-green-600 bg-green-100'
            case 'warning':
            case 'needs attention':
                return 'text-yellow-600 bg-yellow-100'
            case 'error':
            case 'critical':
                return 'text-red-600 bg-red-100'
            default:
                return 'text-gray-600 bg-gray-100'
        }
    }

    const getStatusIcon = (status: string) => {
        switch (status.toLowerCase()) {
            case 'healthy':
            case 'good':
                return <CheckCircleIcon className="w-5 h-5" />
            case 'warning':
            case 'needs attention':
                return <ExclamationTriangleIcon className="w-5 h-5" />
            case 'error':
            case 'critical':
                return <ExclamationTriangleIcon className="w-5 h-5" />
            default:
                return <ClockIcon className="w-5 h-5" />
        }
    }

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
                <h1 className="text-2xl font-bold text-gray-900">Enhanced Admin Dashboard</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Comprehensive monitoring and analytics for platform administration
                </p>
            </div>

            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    {[
                        { id: 'overview', name: 'Overview', icon: ChartBarIcon },
                        { id: 'analytics', name: 'User Analytics', icon: UsersIcon },
                        { id: 'ingestion', name: 'Data Ingestion', icon: DatabaseIcon },
                        { id: 'performance', name: 'System Performance', icon: ServerIcon }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`${activeTab === tab.id
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
                        >
                            <tab.icon className="w-4 h-4 mr-2" />
                            {tab.name}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && overview && (
                <div className="space-y-6">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                                            <UsersIcon className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Total Users
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {overview.user_metrics.total_users.toLocaleString()}
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                                            <TrendingUpIcon className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Active Users (30d)
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {overview.user_metrics.active_users_30d.toLocaleString()}
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                                            <DatabaseIcon className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                Data Quality
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {overview.data_quality.freshness_score.toFixed(1)}%
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="p-5">
                                <div className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                                            <ServerIcon className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                    <div className="ml-5 w-0 flex-1">
                                        <dl>
                                            <dt className="text-sm font-medium text-gray-500 truncate">
                                                System Uptime
                                            </dt>
                                            <dd className="text-lg font-medium text-gray-900">
                                                {overview.system_health.uptime_percentage.toFixed(1)}%
                                            </dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Status Cards */}
                    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                        <div className="bg-white shadow rounded-lg p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">Status</span>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(overview.system_health.status)}`}>
                                        {getStatusIcon(overview.system_health.status)}
                                        <span className="ml-1">{overview.system_health.status}</span>
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">Recent Errors</span>
                                    <span className="text-sm font-medium text-gray-900">{overview.system_health.recent_errors}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white shadow rounded-lg p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Data Ingestion</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">Status</span>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(overview.data_ingestion.status)}`}>
                                        {getStatusIcon(overview.data_ingestion.status)}
                                        <span className="ml-1">{overview.data_ingestion.status}</span>
                                    </span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">Success Rate</span>
                                    <span className="text-sm font-medium text-gray-900">{overview.data_ingestion.success_rate.toFixed(1)}%</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">Recent Jobs</span>
                                    <span className="text-sm font-medium text-gray-900">{overview.data_ingestion.recent_jobs}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* User Analytics Tab */}
            {activeTab === 'analytics' && userAnalytics && (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Total Activities</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{userAnalytics.total_activities.toLocaleString()}</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Unique Users</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{userAnalytics.unique_users.toLocaleString()}</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Unique Sessions</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{userAnalytics.unique_sessions.toLocaleString()}</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Avg Session Duration</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{Math.round(userAnalytics.avg_session_duration_seconds / 60)}m</dd>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                        <div className="bg-white shadow rounded-lg p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Most Visited Pages</h3>
                            <div className="space-y-3">
                                {userAnalytics.most_visited_pages.slice(0, 5).map((page, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">{page.page}</span>
                                        <span className="text-sm font-medium text-gray-900">{page.visits.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-white shadow rounded-lg p-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Action Distribution</h3>
                            <div className="space-y-3">
                                {userAnalytics.action_distribution.slice(0, 5).map((action, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">{action.action}</span>
                                        <span className="text-sm font-medium text-gray-900">{action.count.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Data Ingestion Tab */}
            {activeTab === 'ingestion' && dataIngestion && (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Total Jobs</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{dataIngestion.total_jobs.toLocaleString()}</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Success Rate</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{dataIngestion.success_rate.toFixed(1)}%</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Records Processed</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{dataIngestion.total_records_processed.toLocaleString()}</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Avg Processing Time</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{Math.round(dataIngestion.avg_processing_time_ms)}ms</dd>
                        </div>
                    </div>

                    <div className="bg-white shadow rounded-lg">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-medium text-gray-900">Recent Ingestion Activity</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {dataIngestion.recent_activity.map((activity) => (
                                        <tr key={activity.id}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{activity.source_name}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{activity.data_type}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{activity.records_processed.toLocaleString()}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{activity.success_rate.toFixed(1)}%</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{activity.processing_time_ms}ms</td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${activity.success_rate > 95 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {activity.success_rate > 95 ? 'Success' : 'Failed'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* System Performance Tab */}
            {activeTab === 'performance' && systemPerformance && (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Avg Response Time</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{systemPerformance.averages.response_time_ms.toFixed(1)}ms</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">CPU Usage</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{systemPerformance.averages.cpu_usage_percent.toFixed(1)}%</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Memory Usage</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{systemPerformance.averages.memory_usage_percent.toFixed(1)}%</dd>
                        </div>
                        <div className="bg-white overflow-hidden shadow rounded-lg p-5">
                            <dt className="text-sm font-medium text-gray-500">Recent Errors</dt>
                            <dd className="mt-1 text-3xl font-semibold text-gray-900">{systemPerformance.error_count}</dd>
                        </div>
                    </div>

                    <div className="bg-white shadow rounded-lg">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-medium text-gray-900">Latest Metrics</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {systemPerformance.latest_metrics.map((metric, index) => (
                                        <tr key={index}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{metric.metric_name}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{metric.value} {metric.unit}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric.component}</td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${metric.severity === 'error' ? 'bg-red-100 text-red-800' :
                                                        metric.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-green-100 text-green-800'
                                                    }`}>
                                                    {metric.severity}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(metric.recorded_at).toLocaleTimeString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
} 