import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { 
  CurrencyDollarIcon, 
  ChartBarIcon, 
  BellIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon
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

export default function CurrencyConverter() {
  const router = useRouter()
  const [amount, setAmount] = useState(1000)
  const [currencyPair, setCurrencyPair] = useState('USD/MAD')
  const [comparison, setComparison] = useState<CurrencyComparison | null>(null)
  const [loading, setLoading] = useState(false)
  const [alertRate, setAlertRate] = useState('')
  const [showAlertForm, setShowAlertForm] = useState(false)

  const fetchComparison = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/currency/compare/${currencyPair}?amount=${amount}`)
      if (response.ok) {
        const data = await response.json()
        setComparison(data)
      }
    } catch (error) {
      console.error('Error fetching comparison:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComparison()
  }, [amount, currencyPair])

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

  return (
    <>
      <Head>
        <title>Currency Converter & Remittance Advisor | Casablanca Insights</title>
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
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  {loading ? 'Updating...' : 'Compare Rates'}
                </button>
              </div>
            </div>
          </div>

          {comparison && (
            <>
              {/* BAM Rate Display */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
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
              </div>

              {/* Best Rate Recommendation */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Best Remittance Service
                  </h2>
                  {comparison.is_good_time ? (
                    <div className="flex items-center text-green-600">
                      <CheckCircleIcon className="h-6 w-6 mr-2" />
                      <span className="font-medium">Good Time to Transfer</span>
                    </div>
                  ) : (
                    <div className="flex items-center text-yellow-600">
                      <XCircleIcon className="h-6 w-6 mr-2" />
                      <span className="font-medium">Consider Waiting</span>
                    </div>
                  )}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-4 rounded-lg">
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
              </div>

              {/* AI Recommendation */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-start">
                  <InformationCircleIcon className="h-6 w-6 text-blue-500 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      AI Recommendation
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {comparison.recommendation}
                    </p>
                  </div>
                </div>
              </div>

              {/* All Services Comparison */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  All Remittance Services
                </h2>
                
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

              {/* Rate Alert Section */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Rate Alerts
                  </h2>
                  <button
                    onClick={() => setShowAlertForm(!showAlertForm)}
                    className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    <BellIcon className="h-5 w-5 mr-2" />
                    Set Alert
                  </button>
                </div>
                
                {showAlertForm && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Alert when USD/MAD goes above
                        </label>
                        <input
                          type="number"
                          value={alertRate}
                          onChange={(e) => setAlertRate(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white"
                          placeholder="10.00"
                          step="0.01"
                        />
                      </div>
                      <div className="flex items-end">
                        <button
                          onClick={createAlert}
                          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
                        >
                          Create Alert
                        </button>
                      </div>
                    </div>
                  </div>
                )}
                
                <p className="text-gray-600 dark:text-gray-300">
                  Get notified when the USD to MAD exchange rate reaches your target level.
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
} 