import { useState, useEffect } from 'react'
import { delayedMarketData, DelayedQuote } from '@/lib/delayedMarketData'
import toast from 'react-hot-toast'
import { 
  ClockIcon, 
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  PlayIcon,
  PauseIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

export default function TestDelayedData() {
  const [quotes, setQuotes] = useState<DelayedQuote[]>([])
  const [marketSummary, setMarketSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [autoUpdate, setAutoUpdate] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const loadData = async () => {
    try {
      setLoading(true)
      const [quotesData, summaryData] = await Promise.all([
        delayedMarketData.getAllDelayedQuotes(),
        delayedMarketData.getMarketSummary()
      ])
      setQuotes(quotesData)
      setMarketSummary(summaryData)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error('Failed to load market data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()

    if (autoUpdate) {
      const interval = setInterval(loadData, 5000) // Update every 5 seconds
      return () => clearInterval(interval)
    }
  }, [autoUpdate])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MAD',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
  }

  const getColorForChange = (value: number) => {
    if (value > 0) return 'text-green-600'
    if (value < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  const getChangeIcon = (value: number) => {
    if (value > 0) return <ArrowUpIcon className="h-4 w-4 text-green-600" />
    if (value < 0) return <ArrowDownIcon className="h-4 w-4 text-red-600" />
    return <MinusIcon className="h-4 w-4 text-gray-600" />
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Delayed Market Data Test
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
            Simulating ThinkOrSwim-style delayed market data (15-minute delay)
          </p>

          {/* Controls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={loadData}
                  disabled={loading}
                  className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
                >
                  <ArrowPathIcon className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  <span>Refresh Data</span>
                </button>
                
                <button
                  onClick={() => setAutoUpdate(!autoUpdate)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md ${
                    autoUpdate 
                      ? 'bg-green-500 text-white hover:bg-green-600' 
                      : 'bg-gray-500 text-white hover:bg-gray-600'
                  }`}
                >
                  {autoUpdate ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                  <span>{autoUpdate ? 'Auto Update On' : 'Auto Update Off'}</span>
                </button>
              </div>
              
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <ClockIcon className="h-4 w-4" />
                <span>Last Update: {lastUpdate.toLocaleTimeString()}</span>
              </div>
            </div>
          </div>

          {/* Market Summary */}
          {marketSummary && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Market Summary
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {marketSummary.totalVolume.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Total Volume</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {marketSummary.advancing}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Advancing</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {marketSummary.declining}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Declining</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">
                    {marketSummary.unchanged}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Unchanged</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${getColorForChange(marketSummary.averageChange)}`}>
                    {formatPercent(marketSummary.averageChange)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Avg Change</div>
                </div>
              </div>
            </div>
          )}

          {/* Delayed Data Warning */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <ClockIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Delayed Data Simulation
                </h3>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  Market data is simulated with a 15-minute delay, similar to Charles Schwab's ThinkOrSwim paper trading platform.
                  Prices update every 5 seconds with realistic volatility.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Market Data Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Delayed Market Quotes
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Volume
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    High/Low
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Market Cap
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Last Updated
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {quotes.map((quote) => (
                  <tr key={quote.ticker} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {quote.ticker}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {quote.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {formatCurrency(quote.currentPrice)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-1">
                        {getChangeIcon(quote.change)}
                        <div>
                          <div className={`text-sm font-medium ${getColorForChange(quote.change)}`}>
                            {formatCurrency(quote.change)}
                          </div>
                          <div className={`text-sm ${getColorForChange(quote.changePercent)}`}>
                            {formatPercent(quote.changePercent)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {quote.volume.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(quote.high)} / {formatCurrency(quote.low)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatCurrency(quote.marketCap)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(quote.lastUpdated).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex space-x-4">
          <a
            href="/paper-trading/thinkorswim"
            className="bg-casablanca-blue text-white px-6 py-3 rounded-md hover:bg-casablanca-blue/90 font-medium"
          >
            Try ThinkOrSwim-Style Trading
          </a>
          <a
            href="/test-portfolio-api"
            className="bg-gray-500 text-white px-6 py-3 rounded-md hover:bg-gray-600 font-medium"
          >
            Test Portfolio API
          </a>
        </div>
      </div>
    </div>
  )
} 