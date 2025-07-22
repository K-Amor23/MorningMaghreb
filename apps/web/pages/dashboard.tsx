import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useTranslation } from 'react-i18next'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  ClockIcon,
  UserIcon,
  BellIcon,
  CogIcon,
  PlusIcon,
  EyeIcon,
  BanknotesIcon,
  GlobeAltIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import { formatCurrency, formatPercent, getColorForChange } from '@/lib/utils'
import { useUser } from '@/lib/useUser'
import Watchlist from '@/components/Watchlist'
import AddTickerForm from '@/components/AddTickerForm'
import toast from 'react-hot-toast'

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

  if (!mounted) {
    return <span>--:--:--</span>
  }

  return <span>{time}</span>
}

// Mock data - in real app, this would come from API
const mockMarketData = [
  { ticker: 'MASI', name: 'MASI Index', price: 13456.78, change: 2.34, changePercent: 0.017 },
  { ticker: 'MADEX', name: 'MADEX Index', price: 11234.56, change: -1.23, changePercent: -0.011 },
  { ticker: 'MASI-ESG', name: 'MASI ESG Index', price: 987.65, change: 0.98, changePercent: 0.001 },
  { ticker: 'ATW', name: 'Attijariwafa Bank', price: 534.50, change: 4.50, changePercent: 0.008 },
  { ticker: 'IAM', name: 'Maroc Telecom', price: 156.30, change: -2.10, changePercent: -0.013 },
]

const mockPortfolio = {
  totalValue: 125000,
  totalChange: 2340,
  totalChangePercent: 1.87,
  holdings: [
    { ticker: 'ATW', quantity: 100, value: 53450, change: 450, changePercent: 0.008 },
    { ticker: 'IAM', quantity: 200, value: 31260, change: -420, changePercent: -0.013 },
    { ticker: 'BCP', quantity: 150, value: 40290, change: 1210, changePercent: 0.031 },
  ]
}

const mockPaperTrading = {
  accountBalance: 50000,
  totalPnL: 1250,
  totalPnLPercent: 2.5,
  positions: [
    { ticker: 'ATW', quantity: 50, avgPrice: 530, currentPrice: 534.50, pnl: 225, pnlPercent: 0.85 },
    { ticker: 'IAM', quantity: 100, avgPrice: 158, currentPrice: 156.30, pnl: -170, pnlPercent: -1.08 },
  ],
  recentTrades: [
    { ticker: 'ATW', type: 'BUY', quantity: 25, price: 532, timestamp: '2024-01-15T10:30:00Z' },
    { ticker: 'IAM', type: 'SELL', quantity: 50, price: 157, timestamp: '2024-01-15T09:45:00Z' },
  ]
}

const mockCurrencyRates = {
  USD: { MAD: 10.25, EUR: 0.92 },
  EUR: { MAD: 11.15, USD: 1.09 },
  MAD: { USD: 0.098, EUR: 0.090 },
}

const mockAlerts = [
  { id: 1, type: 'price', ticker: 'ATW', condition: 'above', target: 540, active: true },
  { id: 2, type: 'price', ticker: 'IAM', condition: 'below', target: 150, active: true },
  { id: 3, type: 'currency', pair: 'USD/MAD', condition: 'above', target: 10.50, active: false },
]

export default function Dashboard() {
  const { t } = useTranslation()
  const router = useRouter()
  const { user, profile, dashboard, loading: authLoading, signOut } = useUser()
  const [marketData, setMarketData] = useState(mockMarketData)
  const [portfolio, setPortfolio] = useState(mockPortfolio)
  const [paperTrading, setPaperTrading] = useState(mockPaperTrading)
  const [currencyRates, setCurrencyRates] = useState(mockCurrencyRates)
  const [alerts, setAlerts] = useState(mockAlerts)
  const [loading, setLoading] = useState(false)
  const [watchlistRefresh, setWatchlistRefresh] = useState(0)
  const [activeTab, setActiveTab] = useState('overview')

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace('/login')
    }
  }, [authLoading, user, router])

  const handleSignOut = async () => {
    try {
      await signOut()
      toast.success('Signed out successfully')
      router.push('/')
    } catch (error) {
      toast.error('Error signing out')
      console.error('Sign out error:', error)
    }
  }

  const handleWatchlistRefresh = () => {
    setWatchlistRefresh(prev => prev + 1)
  }

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setMarketData(prev => prev.map(item => ({
        ...item,
        price: item.price + (Math.random() - 0.5) * 2,
        change: item.change + (Math.random() - 0.5) * 0.5,
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'portfolio', name: 'Portfolio', icon: CurrencyDollarIcon },
    { id: 'paper-trading', name: 'Paper Trading', icon: BanknotesIcon },
    { id: 'currency', name: 'Currency', icon: GlobeAltIcon },
    { id: 'alerts', name: 'Alerts', icon: BellIcon },
    { id: 'watchlist', name: 'Watchlist', icon: EyeIcon },
  ]

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Dashboard - Casablanca Insight</title>
        <meta name="description" content="Your financial dashboard" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-casablanca-blue">
                  Casablanca Insight
                </h1>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  <ClockIcon className="inline h-4 w-4 mr-1" />
                  <ClientTime />
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.push('/account/settings')}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <CogIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={handleSignOut}
                  className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {profile?.full_name || user?.email?.split('@')[0] || 'User'}!
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Here's your financial overview for today
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-8 w-8 text-casablanca-blue" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Portfolio Value</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {formatCurrency(portfolio.totalValue)}
                  </p>
                  <p className={`text-sm ${getColorForChange(portfolio.totalChangePercent)}`}>
                    {formatPercent(portfolio.totalChangePercent)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BanknotesIcon className="h-8 w-8 text-green-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Paper Trading</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {formatCurrency(paperTrading.accountBalance)}
                  </p>
                  <p className={`text-sm ${getColorForChange(paperTrading.totalPnLPercent)}`}>
                    {formatPercent(paperTrading.totalPnLPercent)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <GlobeAltIcon className="h-8 w-8 text-purple-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">USD/MAD Rate</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {currencyRates.USD.MAD}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Live Rate
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BellIcon className="h-8 w-8 text-orange-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Alerts</p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {alerts.filter(a => a.active).length}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Price & Currency
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-8">
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="-mb-px flex space-x-8 px-6">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                      activeTab === tab.id
                        ? 'border-casablanca-blue text-casablanca-blue'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                    }`}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Market Overview</h3>
                      <div className="space-y-3">
                        {marketData.slice(0, 5).map((item) => (
                          <div key={item.ticker} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{item.ticker}</p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">{item.name}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-gray-900 dark:text-white">
                                {formatCurrency(item.price)}
                              </p>
                              <p className={`text-sm ${getColorForChange(item.changePercent)}`}>
                                {formatPercent(item.changePercent)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
                      <div className="space-y-3">
                        {paperTrading.recentTrades.slice(0, 5).map((trade, index) => (
                          <div key={index} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">
                                {trade.type} {trade.ticker}
                              </p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">
                                {new Date(trade.timestamp).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-gray-900 dark:text-white">
                                {trade.quantity} @ {formatCurrency(trade.price)}
                              </p>
                              <p className={`text-sm ${trade.type === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                                {trade.type}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Portfolio Tab */}
              {activeTab === 'portfolio' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">Portfolio Holdings</h3>
                    <button className="bg-casablanca-blue text-white px-4 py-2 rounded-md hover:bg-casablanca-blue/90">
                      <PlusIcon className="h-4 w-4 inline mr-2" />
                      Add Holding
                    </button>
                  </div>
                  <div className="space-y-3">
                    {portfolio.holdings.map((holding) => (
                      <div key={holding.ticker} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{holding.ticker}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {holding.quantity} shares
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-gray-900 dark:text-white">
                            {formatCurrency(holding.value)}
                          </p>
                          <p className={`text-sm ${getColorForChange(holding.changePercent)}`}>
                            {formatPercent(holding.changePercent)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Paper Trading Tab */}
              {activeTab === 'paper-trading' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">Paper Trading Account</h3>
                    <button 
                      onClick={() => router.push('/paper-trading')}
                      className="bg-casablanca-blue text-white px-4 py-2 rounded-md hover:bg-casablanca-blue/90"
                    >
                      Trade Now
                    </button>
                  </div>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">Open Positions</h4>
                      <div className="space-y-3">
                        {paperTrading.positions.map((position) => (
                          <div key={position.ticker} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <div className="flex justify-between items-center">
                              <span className="font-medium text-gray-900 dark:text-white">{position.ticker}</span>
                              <span className={`text-sm ${getColorForChange(position.pnlPercent)}`}>
                                {formatPercent(position.pnlPercent)}
                              </span>
                            </div>
                            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 mt-1">
                              <span>{position.quantity} shares</span>
                              <span>{formatCurrency(position.pnl)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-3">Account Summary</h4>
                      <div className="space-y-3">
                        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex justify-between">
                            <span className="text-gray-500 dark:text-gray-400">Balance</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {formatCurrency(paperTrading.accountBalance)}
                            </span>
                          </div>
                        </div>
                        <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex justify-between">
                            <span className="text-gray-500 dark:text-gray-400">Total P&L</span>
                            <span className={`font-medium ${getColorForChange(paperTrading.totalPnLPercent)}`}>
                              {formatCurrency(paperTrading.totalPnL)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Currency Tab */}
              {activeTab === 'currency' && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Currency Converter</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {Object.entries(currencyRates).map(([base, rates]) => (
                      <div key={base} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-3">{base} Exchange Rates</h4>
                        <div className="space-y-2">
                          {Object.entries(rates).map(([target, rate]) => (
                            <div key={target} className="flex justify-between">
                              <span className="text-gray-500 dark:text-gray-400">{base}/{target}</span>
                              <span className="font-medium text-gray-900 dark:text-white">{rate}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6">
                    <button 
                      onClick={() => router.push('/convert')}
                      className="bg-casablanca-blue text-white px-4 py-2 rounded-md hover:bg-casablanca-blue/90"
                    >
                      Advanced Currency Converter
                    </button>
                  </div>
                </div>
              )}

              {/* Alerts Tab */}
              {activeTab === 'alerts' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">Price & Currency Alerts</h3>
                    <button className="bg-casablanca-blue text-white px-4 py-2 rounded-md hover:bg-casablanca-blue/90">
                      <PlusIcon className="h-4 w-4 inline mr-2" />
                      Add Alert
                    </button>
                  </div>
                  <div className="space-y-3">
                    {alerts.map((alert) => (
                      <div key={alert.id} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {alert.type === 'price' ? alert.ticker : alert.pair}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {alert.condition} {formatCurrency(alert.target)}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            alert.active 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                          }`}>
                            {alert.active ? 'Active' : 'Inactive'}
                          </span>
                          <button className="text-red-600 hover:text-red-800">
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Watchlist Tab */}
              {activeTab === 'watchlist' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">Watchlist</h3>
                    <AddTickerForm onAdd={handleWatchlistRefresh} />
                  </div>
                  <Watchlist key={watchlistRefresh} />
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  )
}