import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'

interface DataQualityMetrics {
    total_companies: number
    companies_with_price: number
    companies_with_market_cap: number
    price_coverage: number
    market_cap_coverage: number
    companies_with_reports: number
    companies_with_news: number
    reports_coverage: number
    news_coverage: number
}

interface DataQualityResponse {
    success: boolean
    data: {
        metadata: {
            total_companies: number
            data_quality: DataQualityMetrics
        }
        quality_metrics: DataQualityMetrics
    }
}

// Fetcher function for SWR
const fetcher = (url: string) => fetch(url).then(res => res.json())

// Client-side time component to prevent hydration errors
function ClientTime() {
    const [mounted, setMounted] = useState(false)
    const [time, setTime] = useState<string>('')

    useEffect(() => {
        setMounted(true)
        const updateTime = () => {
            setTime(new Date().toLocaleTimeString())
        }

        updateTime()
        const interval = setInterval(updateTime, 1000)

        return () => clearInterval(interval)
    }, [])

    // Show a placeholder during SSR and initial render
    if (!mounted) {
        return <span>--:--:--</span>
    }

    return <span>{time}</span>
}

const DataQualityIndicator = () => {
    const { data, error, isLoading } = useSWR<DataQualityResponse>(
        '/api/market-data/unified?type=data-quality',
        fetcher,
        { refreshInterval: 60000 } // Refresh every minute
    )

    const getQualityColor = (percentage: number) => {
        if (percentage >= 80) return 'text-green-600'
        if (percentage >= 60) return 'text-yellow-600'
        return 'text-red-600'
    }

    const getQualityIcon = (percentage: number) => {
        if (percentage >= 80) return <CheckCircleIcon className="h-5 w-5 text-green-600" />
        if (percentage >= 60) return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />
        return <InformationCircleIcon className="h-5 w-5 text-red-600" />
    }

    const getQualityLabel = (percentage: number) => {
        if (percentage >= 80) return 'Excellent'
        if (percentage >= 60) return 'Good'
        if (percentage >= 40) return 'Fair'
        return 'Poor'
    }

    if (isLoading) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality</h3>
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
                    <div className="space-y-3">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="h-8 bg-gray-200 rounded"></div>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    if (error || !data?.data?.quality_metrics) {
        return (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality</h3>
                <div className="text-center py-4">
                    <p className="text-red-600 mb-2">Failed to load data quality metrics</p>
                    <p className="text-sm text-gray-500">Please try again later</p>
                </div>
            </div>
        )
    }

    const metrics = data.data.quality_metrics
    const totalCompanies = metrics.total_companies || 0

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Data Quality</h3>
                <div className="text-sm text-gray-500">
                    {totalCompanies} companies
                </div>
            </div>

            <div className="space-y-4">
                {/* Price Data Coverage */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getQualityIcon(metrics.price_coverage)}
                        <span className="text-sm font-medium text-gray-700">Price Data</span>
                    </div>
                    <div className="text-right">
                        <div className={`text-sm font-semibold ${getQualityColor(metrics.price_coverage)}`}>
                            {metrics.price_coverage}%
                        </div>
                        <div className="text-xs text-gray-500">
                            {metrics.companies_with_price}/{totalCompanies} companies
                        </div>
                    </div>
                </div>

                {/* Market Cap Coverage */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getQualityIcon(metrics.market_cap_coverage)}
                        <span className="text-sm font-medium text-gray-700">Market Cap</span>
                    </div>
                    <div className="text-right">
                        <div className={`text-sm font-semibold ${getQualityColor(metrics.market_cap_coverage)}`}>
                            {metrics.market_cap_coverage}%
                        </div>
                        <div className="text-xs text-gray-500">
                            {metrics.companies_with_market_cap}/{totalCompanies} companies
                        </div>
                    </div>
                </div>

                {/* Financial Reports Coverage */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getQualityIcon(metrics.reports_coverage)}
                        <span className="text-sm font-medium text-gray-700">Financial Reports</span>
                    </div>
                    <div className="text-right">
                        <div className={`text-sm font-semibold ${getQualityColor(metrics.reports_coverage)}`}>
                            {metrics.reports_coverage}%
                        </div>
                        <div className="text-xs text-gray-500">
                            {metrics.companies_with_reports}/{totalCompanies} companies
                        </div>
                    </div>
                </div>

                {/* News Coverage */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        {getQualityIcon(metrics.news_coverage)}
                        <span className="text-sm font-medium text-gray-700">News Coverage</span>
                    </div>
                    <div className="text-right">
                        <div className={`text-sm font-semibold ${getQualityColor(metrics.news_coverage)}`}>
                            {metrics.news_coverage}%
                        </div>
                        <div className="text-xs text-gray-500">
                            {metrics.companies_with_news}/{totalCompanies} companies
                        </div>
                    </div>
                </div>
            </div>

            {/* Overall Quality Score */}
            <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Overall Quality</span>
                    <div className="text-right">
                        <div className="text-lg font-bold text-casablanca-blue">
                            {getQualityLabel(Math.round((metrics.price_coverage + metrics.market_cap_coverage + metrics.reports_coverage + metrics.news_coverage) / 4))}
                        </div>
                        <div className="text-xs text-gray-500">
                            Average coverage
                        </div>
                    </div>
                </div>
            </div>

            {/* Data Quality Legend */}
            <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                        <CheckCircleIcon className="h-3 w-3 text-green-600" />
                        <span>≥80% Excellent</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <ExclamationTriangleIcon className="h-3 w-3 text-yellow-600" />
                        <span>60-79% Good</span>
                    </div>
                    <div className="flex items-center space-x-1">
                        <InformationCircleIcon className="h-3 w-3 text-red-600" />
                        <span>&lt;60% Needs Improvement</span>
                    </div>
                </div>
            </div>

            {/* Last Updated */}
            <div className="mt-4 text-xs text-gray-400 text-center">
                Last updated: <ClientTime />
            </div>
        </div>
    )
}

export default DataQualityIndicator 