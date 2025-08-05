import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import { checkPremiumAccess } from '@/lib/featureFlags'
import { safeRandom } from '@/lib/hydration'
import { 
  CurrencyDollarIcon, 
  ChartBarIcon, 
  BellIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UsersIcon,
  SparklesIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

interface RemittanceRate {
  service_name: string
  rate: number
  fee_amount: number
  fee_currency: string
  effective_rate: number
  spread_percentage: number
}

interface CurrencyComparison {
  currency_pair: string
  bam_rate: number
  services: RemittanceRate[]
  best_service: string
  best_rate: number
  best_spread: number
  recommendation: string
  is_good_time: boolean
  percentile_30d: number
}

interface RateTrend {
  date: string
  bam_rate: number
  best_rate: number
  avg_rate: number
}

interface CrowdsourceInsight {
  id: string
  user_type: string
  message: string
  rating: number
  timestamp: string
  likes: number
}

export default function CurrencyConverter() {
  const router = useRouter()
  const { user, profile, loading } = useUser()
  const [amount, setAmount] = useState(1000)
  const [currencyPair, setCurrencyPair] = useState('USD/MAD')
  const [comparison, setComparison] = useState<CurrencyComparison | null>(null)
  const [loadingComparison, setLoadingComparison] = useState(false)
  const [alertRate, setAlertRate] = useState('')
  const [showAlertForm, setShowAlertForm] = useState(false)
  const [activeTab, setActiveTab] = useState('comparison')
  const [rateTrends, setRateTrends] = useState<RateTrend[]>([])
  const [crowdsourceInsights, setCrowdsourceInsights] = useState<CrowdsourceInsight[]>([])

  // Dev bypass for premium access and user loading
  if (loading && process.env.NODE_ENV === 'production') {
    return <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">Loading...</div>
  }

  // Temporarily disable premium check for development
  const isPro = true // checkPremiumAccess(profile?.tier || 'free')

  if (!isPro) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Premium Required</h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
              Upgrade to Premium to use the Smart FX Converter and get AI-powered remittance recommendations.
            </p>
            <Link href="/premium">
              <button className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white font-medium rounded-lg transition-colors">
                See Premium Plans
              </button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const fetchComparison = async () => {
    setLoadingComparison(true)
    try {
      console.log('Fetching comparison for:', currencyPair, 'amount:', amount)
      const response = await fetch(`/api/currency/compare?currency_pair=${currencyPair}&amount=${amount}`)
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Received data:', data)
        setComparison(data)
        
        // Fetch trend and crowdsource data
        fetchTrendData()
        fetchCrowdsourceData()
      } else {
        console.error('API error:', response.status, response.statusText)
        const errorText = await response.text()
        console.error('Error response:', errorText)
      }
    } catch (error) {
      console.error('Error fetching comparison:', error)
    } finally {
      setLoadingComparison(false)
    }
  }

  const fetchTrendData = async () => {
    try {
      const response = await fetch(`/api/currency/trends?currency_pair=${currencyPair}&days=7`)
      if (response.ok) {
        const data = await response.json()
        setRateTrends(data.trends)
      }
    } catch (error) {
      console.error('Error fetching trend data:', error)
      // Fallback to mock data
      generateMockTrendData()
    }
  }

  const fetchCrowdsourceData = async () => {
    try {
      const response = await fetch(`/api/currency/insights?currency_pair=${currencyPair}&limit=5`)
      if (response.ok) {
        const data = await response.json()
        setCrowdsourceInsights(data.insights)
      }
    } catch (error) {
      console.error('Error fetching crowdsource data:', error)
      // Fallback to mock data
      generateMockCrowdsourceData()
    }
  }

  const generateMockTrendData = () => {
    const trends: RateTrend[] = []
    const today = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      
      trends.push({
        date: date.toISOString().split('T')[0],
        bam_rate: 10.25 + safeRandom(-0.05, 0.05),
        best_rate: 10.15 + safeRandom(-0.05, 0.05),
        avg_rate: 10.20 + safeRandom(-0.025, 0.025)
      })
    }
    
    setRateTrends(trends)
  }

  const generateMockCrowdsourceData = () => {
    const insights: CrowdsourceInsight[] = [
      {
        id: '1',
        user_type: 'Frequent User',
        message: 'Remitly usually has the best rates on Tuesdays and Wednesdays. Avoid weekends!',
        rating: 4.8,
        timestamp: '2 hours ago',
        likes: 23
      },
      {
        id: '2',
        user_type: 'Expat',
        message: 'I always check Bank Al-Maghrib rate first, then compare with Wise. Usually saves me 1-2%',
        rating: 4.6,
        timestamp: '5 hours ago',
        likes: 18
      },
      {
        id: '3',
        user_type: 'Business Owner',
        message: 'Western Union has good rates for large amounts (>$5000). Smaller amounts, go with Remitly.',
        rating: 4.4,
        timestamp: '1 day ago',
        likes: 15
      }
    ]
    
    setCrowdsourceInsights(insights)
  }

  const createAlert = async () => {
    if (!alertRate) return
    
    try {
      const response = await fetch('/api/currency/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currency_pair: currencyPair,
          target_rate: parseFloat(alertRate),
          alert_type: 'above'
        })
      })
      
      if (response.ok) {
        setShowAlertForm(false)
        setAlertRate('')
        alert('Rate alert created successfully!')
      }
    } catch (error) {
      console.error('Error creating alert:', error)
    }
  }

  const getRateChangeIcon = (current: number, previous: number) => {
    if (current > previous) {
      return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
    } else if (current < previous) {
      return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
    }
    return <ClockIcon className="h-4 w-4 text-gray-500" />
  }

  const getRateChangeColor = (current: number, previous: number) => {
    if (current > previous) return 'text-green-600'
    if (current < previous) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <>
      <Head>
        <title>Currency Converter & Remittance Advisor | Morning Maghreb</title>
        <meta name="description" content="Compare USD to MAD exchange rates across remittance services and get AI-powered recommendations for the best time to transfer money." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Currency Converter & Remittance Advisor
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Find the best USD to MAD exchange rates and get AI-powered recommendations
            </p>
          </div>

          {/* Input Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Transfer Amount (USD)
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="1000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Currency Pair
                </label>
                <select
                  value={currencyPair}
                  onChange={(e) => setCurrencyPair(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="USD/MAD">USD → MAD</option>
                  <option value="EUR/MAD">EUR → MAD</option>
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={fetchComparison}
                  disabled={loadingComparison}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {loadingComparison ? 'Updating...' : 'Compare Rates'}
                </button>
              </div>
            </div>
          </div>

          {comparison && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Content - 2/3 width */}
              <div className="lg:col-span-2 space-y-6">
                {/* Tab Navigation */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
                  <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="flex space-x-8 px-6" aria-label="Tabs">
                      {[
                        { id: 'comparison', name: 'Rate Comparison', icon: CurrencyDollarIcon },
                        { id: 'trends', name: 'Rate Trends', icon: ChartBarIcon },
                        { id: 'insights', name: 'Community Insights', icon: UsersIcon }
                      ].map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                            activeTab === tab.id
                              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                          }`}
                        >
                          <tab.icon className="h-5 w-5" />
                          <span className="hidden sm:inline">{tab.name}</span>
                        </button>
                      ))}
                    </nav>
                  </div>

                  {/* Tab Content */}
                  <div className="p-6">
                    {activeTab === 'comparison' && (
                      <div className="space-y-6">
                        {/* BAM Rate Display */}
                        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 rounded-lg">
                          <div>
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                              Official BAM Rate
                            </h2>
                            <p className="text-gray-600 dark:text-gray-300">
                              Bank Al-Maghrib official exchange rate
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-3xl font-bold text-green-600">
                              {comparison.bam_rate.toFixed(4)} MAD
                            </div>
                            <div className="text-sm text-gray-500">
                              per 1 USD
                            </div>
                          </div>
                        </div>

                        {/* All Services Comparison */}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                            All Remittance Services
                          </h3>
                          <div className="overflow-x-auto">
                            <table className="w-full">
                              <thead>
                                <tr className="border-b border-gray-200 dark:border-gray-700">
                                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">Service</th>
                                  <th className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">Rate</th>
                                  <th className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">Fee</th>
                                  <th className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">Effective Rate</th>
                                  <th className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">Spread</th>
                                </tr>
                              </thead>
                              <tbody>
                                {comparison.services.map((service, index) => (
                                  <tr 
                                    key={index}
                                    className={`border-b border-gray-100 dark:border-gray-700 ${
                                      service.service_name === comparison.best_service 
                                        ? 'bg-green-50 dark:bg-green-900/20' 
                                        : ''
                                    }`}
                                  >
                                    <td className="py-3 px-4">
                                      <div className="font-medium text-gray-900 dark:text-white">
                                        {service.service_name}
                                      </div>
                                      {service.service_name === comparison.best_service && (
                                        <div className="text-xs text-green-600 dark:text-green-400">
                                          Best Rate
                                        </div>
                                      )}
                                    </td>
                                    <td className="text-right py-3 px-4 text-gray-900 dark:text-white">
                                      {service.rate.toFixed(4)}
                                    </td>
                                    <td className="text-right py-3 px-4 text-gray-600 dark:text-gray-300">
                                      ${service.fee_amount} {service.fee_currency}
                                    </td>
                                    <td className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white">
                                      {service.effective_rate.toFixed(4)}
                                    </td>
                                    <td className="text-right py-3 px-4">
                                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                        service.spread_percentage <= 1 
                                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                          : service.spread_percentage <= 2
                                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                      }`}>
                                        {service.spread_percentage.toFixed(2)}%
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

                    {activeTab === 'trends' && (
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                          7-Day Rate Trend
                        </h3>
                        
                        {/* Rate Trend Chart */}
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                          <div className="space-y-4">
                            {rateTrends.map((trend, index) => {
                              const prevTrend = index > 0 ? rateTrends[index - 1] : null
                              return (
                                <div key={trend.date} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg">
                                  <div className="flex items-center space-x-4">
                                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                                      {new Date(trend.date).toLocaleDateString('en-US', { 
                                        month: 'short', 
                                        day: 'numeric' 
                                      })}
                                    </div>
                                    {prevTrend && getRateChangeIcon(trend.bam_rate, prevTrend.bam_rate)}
                                  </div>
                                  
                                  <div className="flex items-center space-x-6">
                                    <div className="text-right">
                                      <div className="text-sm text-gray-500">BAM Rate</div>
                                      <div className={`font-medium ${prevTrend ? getRateChangeColor(trend.bam_rate, prevTrend.bam_rate) : 'text-gray-900 dark:text-white'}`}>
                                        {trend.bam_rate.toFixed(4)}
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="text-sm text-gray-500">Best Rate</div>
                                      <div className={`font-medium ${prevTrend ? getRateChangeColor(trend.best_rate, prevTrend.best_rate) : 'text-gray-900 dark:text-white'}`}>
                                        {trend.best_rate.toFixed(4)}
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="text-sm text-gray-500">30d Avg</div>
                                      <div className="font-medium text-gray-900 dark:text-white">
                                        {trend.avg_rate.toFixed(4)}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        </div>

                        {/* Trend Annotations */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                     <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                             <div className="flex items-center space-x-2 mb-2">
                               <ArrowTrendingUpIcon className="h-5 w-5 text-blue-600" />
                               <span className="font-medium text-blue-900 dark:text-blue-100">Best Rate This Week</span>
                             </div>
                            <p className="text-sm text-blue-700 dark:text-blue-200">
                              {rateTrends.length > 0 ? `${rateTrends[0].best_rate.toFixed(4)} MAD on ${new Date(rateTrends[0].date).toLocaleDateString()}` : 'Loading...'}
                            </p>
                          </div>
                          
                          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                            <div className="flex items-center space-x-2 mb-2">
                              <ChartBarIcon className="h-5 w-5 text-green-600" />
                              <span className="font-medium text-green-900 dark:text-green-100">Today vs Average</span>
                            </div>
                            <p className="text-sm text-green-700 dark:text-green-200">
                              {rateTrends.length > 0 ? 
                                `${((rateTrends[0].bam_rate / rateTrends[0].avg_rate - 1) * 100).toFixed(1)}% ${rateTrends[0].bam_rate > rateTrends[0].avg_rate ? 'above' : 'below'} 30-day average` 
                                : 'Loading...'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {activeTab === 'insights' && (
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                          Community Insights
                        </h3>
                        
                        <div className="space-y-4">
                          {crowdsourceInsights.map((insight) => (
                            <div key={insight.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                                    {insight.user_type}
                                  </span>
                                  <div className="flex items-center space-x-1">
                                    {[...Array(5)].map((_, i) => (
                                      <span key={i} className={`text-sm ${i < Math.floor(insight.rating) ? 'text-yellow-400' : 'text-gray-300'}`}>
                                        ★
                                      </span>
                                    ))}
                                  </div>
                                </div>
                                <span className="text-xs text-gray-500">{insight.timestamp}</span>
                              </div>
                              <p className="text-gray-700 dark:text-gray-300 mb-2">{insight.message}</p>
                              <div className="flex items-center space-x-4 text-xs text-gray-500">
                                <button className="flex items-center space-x-1 hover:text-blue-600">
                                  <span>👍</span>
                                  <span>{insight.likes}</span>
                                </button>
                                <button className="hover:text-blue-600">Reply</button>
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                          <div className="flex items-center space-x-2 mb-2">
                            <SparklesIcon className="h-5 w-5 text-yellow-600" />
                            <span className="font-medium text-yellow-900 dark:text-yellow-100">Coming Soon</span>
                          </div>
                          <p className="text-sm text-yellow-700 dark:text-yellow-200">
                            Share your own FX strategies and get insights from the community. Earn points for helpful tips!
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Sidebar - 1/3 width */}
              <div className="space-y-6">
                {/* Best Rate Recommendation */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      Best Service
                    </h2>
                    {comparison.is_good_time ? (
                      <div className="flex items-center text-green-600">
                        <CheckCircleIcon className="h-5 w-5 mr-1" />
                        <span className="text-sm font-medium">Good Time</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-yellow-600">
                        <XCircleIcon className="h-5 w-5 mr-1" />
                        <span className="text-sm font-medium">Wait</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-4 rounded-lg mb-4">
                    <div className="text-sm text-blue-600 dark:text-blue-300 mb-1">
                      Best Service
                    </div>
                    <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                      {comparison.best_service}
                    </div>
                    <div className="text-lg text-blue-700 dark:text-blue-200">
                      {comparison.best_rate.toFixed(4)} MAD per USD
                    </div>
                    <div className="text-sm text-blue-600 dark:text-blue-300">
                      Spread: {comparison.best_spread.toFixed(2)}% below BAM
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-4 rounded-lg">
                    <div className="text-sm text-green-600 dark:text-green-300 mb-1">
                      Rate Quality
                    </div>
                    <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                      {comparison.percentile_30d}%
                    </div>
                    <div className="text-sm text-green-700 dark:text-green-200">
                      Better than {comparison.percentile_30d}% of past 30 days
                    </div>
                  </div>
                </div>

                {/* AI Recommendation */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-start mb-4">
                    <InformationCircleIcon className="h-6 w-6 text-blue-500 mt-1 mr-3 flex-shrink-0" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      AI Recommendation
                    </h3>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {comparison.recommendation}
                  </p>
                </div>

                {/* AI Smart Forecast */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <SparklesIcon className="h-6 w-6 text-purple-500" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      AI Smart Forecast
                    </h3>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                    <div className="text-sm text-purple-600 dark:text-purple-300 mb-2">
                      Coming Soon
                    </div>
                    <p className="text-sm text-purple-700 dark:text-purple-200">
                      AI prediction model for next 3-day trend estimate. Get ahead of the market with machine learning insights.
                    </p>
                  </div>
                </div>

                {/* Rate Alert Section */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Rate Alerts
                    </h2>
                    <button
                      onClick={() => setShowAlertForm(!showAlertForm)}
                      className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                    >
                      <BellIcon className="h-4 w-4 mr-1" />
                      Set Alert
                    </button>
                  </div>
                  
                  {showAlertForm && (
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Alert when USD/MAD goes above
                          </label>
                          <input
                            type="number"
                            value={alertRate}
                            onChange={(e) => setAlertRate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white text-sm"
                            placeholder="10.00"
                            step="0.01"
                          />
                        </div>
                        <button
                          onClick={createAlert}
                          className="w-full bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                        >
                          Create Alert
                        </button>
                      </div>
                    </div>
                  )}
                  
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Get notified when the USD to MAD exchange rate reaches your target level.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
} 