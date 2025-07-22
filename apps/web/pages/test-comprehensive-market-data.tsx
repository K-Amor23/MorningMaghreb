import { useState, useEffect } from 'react'
import { comprehensiveMarketData, ComprehensiveQuote } from '@/lib/comprehensiveMarketData'
import toast from 'react-hot-toast'
import { 
  ClockIcon, 
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  PlayIcon,
  PauseIcon,
  ArrowPathIcon,
  FunnelIcon,
  ListBulletIcon,
  Squares2X2Icon
} from '@heroicons/react/24/outline'

export default function TestComprehensiveMarketData() {
  const [quotes, setQuotes] = useState<ComprehensiveQuote[]>([])
  const [marketSummary, setMarketSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [autoUpdate, setAutoUpdate] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [filterType, setFilterType] = useState<'all' | 'stock' | 'bond' | 'etf' | 'warrant'>('all')
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table')
  const [searchTerm, setSearchTerm] = useState('')

  const loadData = async () => {
    try {
      setLoading(true)
      const [quotesData, summaryData] = await Promise.all([
        comprehensiveMarketData.getAllQuotes(),
        comprehensiveMarketData.getMarketSummary()
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
      const interval = setInterval(loadData, 5000)
      return () => clearInterval(interval)
    }
  }, [autoUpdate])

  const filteredQuotes = quotes.filter(quote => {
    const matchesType = filterType === 'all' || quote.instrumentType === filterType
    const matchesSearch = quote.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         quote.name.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesType && matchesSearch
  })

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

  const getInstrumentTypeColor = (type: string) => {
    switch (type) {
      case 'stock': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'bond': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'etf': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      case 'warrant': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Comprehensive Market Data Test
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
            All 78 companies + bonds + ETFs + warrants from Casablanca Stock Exchange
          </p>

          {/* Controls */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
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
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <FunnelIcon className="h-4 w-4 text-gray-500" />
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value as any)}
                    className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="all">All Instruments</option>
                    <option value="stock">Stocks</option>
                    <option value="bond">Bonds</option>
                    <option value="etf">ETFs</option>
                    <option value="warrant">Warrants</option>
                  </select>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setViewMode('table')}
                    className={`p-2 rounded ${viewMode === 'table' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                  >
                    <ListBulletIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                  >
                    <Squares2X2Icon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <input
                type="text"
                placeholder="Search by ticker or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full lg:w-96 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            
            <div className="mt-4 flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <ClockIcon className="h-4 w-4" />
              <span>Last Update: {lastUpdate.toLocaleTimeString()}</span>
              <span>•</span>
              <span>Showing {filteredQuotes.length} of {quotes.length} instruments</span>
            </div>
          </div>

          {/* Market Summary */}
          {marketSummary && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Market Summary
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
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

              {/* Breakdown by Type */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(marketSummary.byType).map(([type, data]: [string, any]) => (
                  <div key={type} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white capitalize mb-2">
                      {type}
                    </h3>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 dark:text-gray-400">Total:</span>
                        <span className="font-medium">{data.count}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-green-600">Advancing:</span>
                        <span className="font-medium">{data.advancing}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-red-600">Declining:</span>
                        <span className="font-medium">{data.declining}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Delayed Data Warning */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <ClockIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Comprehensive Market Data Simulation
                </h3>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  All 78 companies from African markets + government bonds + corporate bonds + ETFs + warrants.
                  Data is simulated with 15-minute delay and realistic volatility.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Market Data Display */}
        {viewMode === 'table' ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Market Instruments ({filteredQuotes.length})
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Instrument
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Change
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Volume
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Market Cap
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Sector
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredQuotes.map((quote) => (
                    <tr key={quote.ticker} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {quote.ticker}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {quote.name}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getInstrumentTypeColor(quote.instrumentType)}`}>
                          {quote.instrumentType.toUpperCase()}
                        </span>
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
                        {formatCurrency(quote.marketCap)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {quote.sector}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredQuotes.map((quote) => (
              <div key={quote.ticker} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {quote.ticker}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {quote.name}
                    </p>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getInstrumentTypeColor(quote.instrumentType)}`}>
                    {quote.instrumentType.toUpperCase()}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Price:</span>
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
                      {formatCurrency(quote.currentPrice)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Change:</span>
                    <div className="text-right">
                      <div className={`text-sm font-medium ${getColorForChange(quote.change)}`}>
                        {formatCurrency(quote.change)}
                      </div>
                      <div className={`text-xs ${getColorForChange(quote.changePercent)}`}>
                        {formatPercent(quote.changePercent)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Volume:</span>
                    <span className="text-sm font-medium">{quote.volume.toLocaleString()}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 dark:text-gray-400">Sector:</span>
                    <span className="text-sm font-medium">{quote.sector}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex space-x-4">
          <a
            href="/paper-trading/thinkorswim"
            className="bg-casablanca-blue text-white px-6 py-3 rounded-md hover:bg-casablanca-blue/90 font-medium"
          >
            Try ThinkOrSwim-Style Trading
          </a>
          <a
            href="/test-delayed-data"
            className="bg-gray-500 text-white px-6 py-3 rounded-md hover:bg-gray-600 font-medium"
          >
            Test Basic Delayed Data
          </a>
        </div>
      </div>
    </div>
  )
} 