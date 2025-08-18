import { useState } from 'react'
import {
    NewspaperIcon,
    DocumentTextIcon,
    CurrencyDollarIcon,
    CalendarIcon,
    ClockIcon,
    ArrowTopRightOnSquareIcon,
    ChevronDownIcon,
    ChevronUpIcon
} from '@heroicons/react/24/outline'

interface NewsItem {
    id: string
    title: string
    summary: string
    source: string
    publishedAt: string
    url: string
    category: 'news' | 'announcement' | 'earnings' | 'dividend' | 'corporate_action'
    sentiment: 'positive' | 'negative' | 'neutral'
    impact: 'high' | 'medium' | 'low'
}

interface DividendAnnouncement {
    id: string
    type: 'dividend' | 'stock_split' | 'rights_issue'
    amount: number
    currency: string
    exDate: string
    recordDate: string
    paymentDate: string
    description: string
    status: 'announced' | 'ex_dividend' | 'paid'
}

interface EarningsAnnouncement {
    id: string
    period: string
    reportDate: string
    estimate: number
    actual?: number
    surprise?: number
    surprisePercent?: number
    status: 'scheduled' | 'reported' | 'missed'
}

interface NewsAndAnnouncementsProps {
    ticker: string
    companyName: string
    news: NewsItem[]
    dividends: DividendAnnouncement[]
    earnings: EarningsAnnouncement[]
}

export default function NewsAndAnnouncements({
    ticker,
    companyName,
    news,
    dividends,
    earnings
}: NewsAndAnnouncementsProps) {
    const [activeTab, setActiveTab] = useState<'news' | 'dividends' | 'earnings'>('news')
    const [expandedNews, setExpandedNews] = useState<string[]>([])

    const tabs = [
        { id: 'news', label: 'News & Announcements', icon: NewspaperIcon, count: news.length },
        { id: 'dividends', label: 'Dividends', icon: CurrencyDollarIcon, count: dividends.length },
        { id: 'earnings', label: 'Earnings', icon: DocumentTextIcon, count: earnings.length }
    ]

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diffTime = Math.abs(now.getTime() - date.getTime())
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

        if (diffDays === 0) return 'Today'
        if (diffDays === 1) return 'Yesterday'
        if (diffDays < 7) return `${diffDays} days ago`
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
        return date.toLocaleDateString()
    }

    const getSentimentColor = (sentiment: string) => {
        switch (sentiment) {
            case 'positive': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'negative': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            default: return 'text-gray-600 bg-gray-100 dark:bg-gray-700'
        }
    }

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'high': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            case 'medium': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
            default: return 'text-green-600 bg-green-100 dark:bg-green-900/20'
        }
    }

    const toggleNewsExpansion = (newsId: string) => {
        setExpandedNews(prev =>
            prev.includes(newsId)
                ? prev.filter(id => id !== newsId)
                : [...prev, newsId]
        )
    }

    const renderNewsTab = () => (
        <div className="space-y-4">
            {news.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <NewspaperIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No news available for {ticker}</p>
                </div>
            ) : (
                news.map((item) => (
                    <div key={item.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                        <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center space-x-2">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSentimentColor(item.sentiment)}`}>
                                    {item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)}
                                </span>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImpactColor(item.impact)}`}>
                                    {item.impact.charAt(0).toUpperCase() + item.impact.slice(1)} Impact
                                </span>
                            </div>
                            <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                <ClockIcon className="h-3 w-3 mr-1" />
                                {formatDate(item.publishedAt)}
                            </div>
                        </div>

                        <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                            {item.title}
                        </h3>

                        <div className="flex items-center justify-between mb-3">
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                Source: {item.source}
                            </span>
                            <button
                                onClick={() => toggleNewsExpansion(item.id)}
                                className="text-sm text-casablanca-blue hover:text-casablanca-blue/80"
                            >
                                {expandedNews.includes(item.id) ? (
                                    <ChevronUpIcon className="h-4 w-4" />
                                ) : (
                                    <ChevronDownIcon className="h-4 w-4" />
                                )}
                            </button>
                        </div>

                        {expandedNews.includes(item.id) && (
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                                    {item.summary}
                                </p>
                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center text-sm text-casablanca-blue hover:text-casablanca-blue/80"
                                >
                                    Read full article
                                    <ArrowTopRightOnSquareIcon className="h-3 w-3 ml-1" />
                                </a>
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>
    )

    const renderDividendsTab = () => (
        <div className="space-y-4">
            {dividends.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No dividend announcements for {ticker}</p>
                </div>
            ) : (
                dividends.map((dividend) => (
                    <div key={dividend.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-2">
                                <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300 rounded-full">
                                    {dividend.type === 'dividend' ? 'Dividend' : dividend.type === 'stock_split' ? 'Stock Split' : 'Rights Issue'}
                                </span>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${dividend.status === 'announced' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300' :
                                        dividend.status === 'ex_dividend' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' :
                                            'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                                    }`}>
                                    {dividend.status.charAt(0).toUpperCase() + dividend.status.slice(1).replace('_', ' ')}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                            <div className="text-center">
                                <div className="text-lg font-bold text-gray-900 dark:text-white">
                                    {dividend.amount.toFixed(2)} {dividend.currency}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Amount</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {formatDate(dividend.exDate)}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Ex-Date</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {formatDate(dividend.recordDate)}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Record Date</div>
                            </div>
                            <div className="text-center">
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {formatDate(dividend.paymentDate)}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">Payment Date</div>
                            </div>
                        </div>

                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            {dividend.description}
                        </p>
                    </div>
                ))
            )}
        </div>
    )

    const renderEarningsTab = () => (
        <div className="space-y-4">
            {earnings.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No earnings announcements for {ticker}</p>
                </div>
            ) : (
                earnings.map((earning) => (
                    <div key={earning.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-2">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${earning.status === 'reported' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' :
                                        earning.status === 'scheduled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300' :
                                            'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                                    }`}>
                                    {earning.status.charAt(0).toUpperCase() + earning.status.slice(1)}
                                </span>
                                <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300 rounded-full">
                                    {earning.period}
                                </span>
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                                {formatDate(earning.reportDate)}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            <div className="text-center">
                                <div className="text-sm text-gray-500 dark:text-gray-400">Estimate</div>
                                <div className="text-lg font-bold text-gray-900 dark:text-white">
                                    {earning.estimate.toFixed(2)} MAD
                                </div>
                            </div>
                            {earning.actual !== undefined && (
                                <div className="text-center">
                                    <div className="text-sm text-gray-500 dark:text-gray-400">Actual</div>
                                    <div className={`text-lg font-bold ${earning.actual >= earning.estimate ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {earning.actual.toFixed(2)} MAD
                                    </div>
                                </div>
                            )}
                            {earning.surprise !== undefined && (
                                <div className="text-center">
                                    <div className="text-sm text-gray-500 dark:text-gray-400">Surprise</div>
                                    <div className={`text-lg font-bold ${earning.surprise >= 0 ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {earning.surprise >= 0 ? '+' : ''}{earning.surprise.toFixed(2)} MAD
                                    </div>
                                </div>
                            )}
                        </div>

                        {earning.surprisePercent !== undefined && (
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                                <div className="text-center">
                                    <div className="text-sm text-gray-500 dark:text-gray-400">Surprise %</div>
                                    <div className={`text-lg font-bold ${earning.surprisePercent >= 0 ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {earning.surprisePercent >= 0 ? '+' : ''}{earning.surprisePercent.toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))
            )}
        </div>
    )

    const renderActiveTab = () => {
        switch (activeTab) {
            case 'news':
                return renderNewsTab()
            case 'dividends':
                return renderDividendsTab()
            case 'earnings':
                return renderEarningsTab()
            default:
                return renderNewsTab()
        }
    }

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            {/* Tabs */}
            <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="flex space-x-8 px-6">
                    {tabs.map((tab) => {
                        const Icon = tab.icon
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                                        ? 'border-casablanca-blue text-casablanca-blue'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                                    }`}
                            >
                                <Icon className="h-4 w-4 inline mr-2" />
                                {tab.label}
                                {tab.count > 0 && (
                                    <span className="ml-2 px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                                        {tab.count}
                                    </span>
                                )}
                            </button>
                        )
                    })}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
                {renderActiveTab()}
            </div>
        </div>
    )
}
