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
  UserIcon
} from '@heroicons/react/24/outline'
import { formatCurrency, formatPercent, getColorForChange } from '@/lib/utils'
import { supabase } from '@/lib/supabase'
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

  // Show a placeholder during SSR and initial render
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

export default function Dashboard() {
  const { t } = useTranslation()
  const router = useRouter()
  const [marketData, setMarketData] = useState(mockMarketData)
  const [portfolio, setPortfolio] = useState(mockPortfolio)
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [watchlistRefresh, setWatchlistRefresh] = useState(0)

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!supabase) {
          console.error('Supabase not configured')
          setAuthLoading(false)
          return
        }

        const { data: { session } } = await supabase.auth.getSession()
        
        if (!session) {
          router.replace('/login')
          return
        }

        setUser(session.user)
      } catch (error) {
        console.error('Auth check error:', error)
        router.replace('/login')
      } finally {
        setAuthLoading(false)
      }
    }

    checkAuth()

    // Listen for auth changes
    if (supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          if (event === 'SIGNED_OUT') {
            setUser(null)
            router.replace('/login')
          } else if (session) {
            setUser(session.user)
          }
        }
      )

      return () => subscription.unsubscribe()
    }
  }, [router])

  // Redirect if not authenticated (after auth check is complete)
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace('/login')
    }
  }, [authLoading, user, router])

  const handleSignOut = async () => {
    try {
      if (!supabase) {
        toast.error('Supabase not configured')
        return
      }
      await supabase.auth.signOut()
      toast.success('Signed out successfully')
    } catch (error) {
      toast.error('Error signing out')
      console.error('Sign out error:', error)
    }
  }

  const handleWatchlistRefresh = () => {
    setWatchlistRefresh(prev => prev + 1)
  }

  useEffect(() => {
    // Simulate real-time updates - only run on client side
    const interval = setInterval(() => {
      setMarketData(prev => prev.map(item => ({
        ...item,
        price: item.price + (Math.random() - 0.5) * 2,
        change: item.change + (Math.random() - 0.5) * 0.5,
        changePercent: item.changePercent + (Math.random() - 0.5) * 0.001,
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-casablanca-light dark:bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  // Don't render anything if not authenticated (redirect will happen in useEffect)
  if (!user) {
    return (
      <div className="min-h-screen bg-casablanca-light dark:bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Dashboard - Casablanca Insight</title>
        <meta name="description" content="Morocco market dashboard with real-time data" />
      </Head>

      <div className="min-h-screen bg-casablanca-light dark:bg-dark-bg">
        {/* Header */}
        <header className="bg-white dark:bg-dark-card shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-dark-text">
                  Market Dashboard
                </h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-dark-text-secondary">
                  Real-time Morocco market data and portfolio insights
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-dark-text-secondary">
                  <ClockIcon className="h-4 w-4" />
                  <span>Last updated: <ClientTime /></span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 text-sm text-gray-700 dark:text-dark-text">
                    <UserIcon className="h-4 w-4" />
                    <span>{user.email}</span>
                  </div>
                  <button
                    onClick={handleSignOut}
                    className="text-sm text-gray-500 hover:text-gray-700 dark:text-dark-text-secondary dark:hover:text-dark-text"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Market Overview Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
            <div className="bg-white dark:bg-dark-card overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-dark-text-secondary truncate">
                        MASI Index
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-dark-text">
                        {formatCurrency(marketData[0]?.price || 0)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-dark-border px-5 py-3">
                <div className="text-sm">
                  <span className={`font-medium ${getColorForChange(marketData[0]?.change || 0)}`}>
                    {marketData[0]?.change > 0 ? '+' : ''}{marketData[0]?.change.toFixed(2)} ({formatPercent(marketData[0]?.changePercent || 0)})
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-dark-card overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CurrencyDollarIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-dark-text-secondary truncate">
                        Portfolio Value
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-dark-text">
                        {formatCurrency(portfolio.totalValue)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-dark-border px-5 py-3">
                <div className="text-sm">
                  <span className={`font-medium ${getColorForChange(portfolio.totalChange)}`}>
                    {portfolio.totalChange > 0 ? '+' : ''}{formatCurrency(portfolio.totalChange)} ({formatPercent(portfolio.totalChangePercent)})
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-dark-card overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ArrowTrendingUpIcon className="h-6 w-6 text-green-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-dark-text-secondary truncate">
                        Top Performer
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-dark-text">
                        ATW
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-dark-border px-5 py-3">
                <div className="text-sm">
                  <span className="font-medium text-green-600">
                    +0.8%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Watchlist Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            <div className="lg:col-span-2">
              <Watchlist userId={user.id} key={watchlistRefresh} />
            </div>
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-dark-card shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text mb-4">
                  Add to Watchlist
                </h3>
                <AddTickerForm userId={user.id} onTickerAdded={handleWatchlistRefresh} />
              </div>
            </div>
          </div>

          {/* Market Data Table */}
          <div className="bg-white dark:bg-dark-card shadow overflow-hidden sm:rounded-md mb-8">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-dark-text">
                Live Market Data
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-dark-text-secondary">
                Real-time quotes from Casablanca Stock Exchange
              </p>
            </div>
            <div className="border-t border-gray-200 dark:border-dark-border">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                  <thead className="bg-gray-50 dark:bg-dark-border">
                                          <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Symbol
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Price
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Change
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Change %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-dark-card divide-y divide-gray-200 dark:divide-dark-border">
                                          {marketData.map((item) => (
                        <tr key={item.ticker}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900 dark:text-dark-text">
                                {item.ticker}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-dark-text-secondary">
                                {item.name}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-dark-text">
                            {formatCurrency(item.price)}
                          </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={getColorForChange(item.change)}>
                            {item.change > 0 ? '+' : ''}{item.change.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={getColorForChange(item.change)}>
                            {item.changePercent > 0 ? '+' : ''}{formatPercent(item.changePercent)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Portfolio Holdings */}
          <div className="bg-white dark:bg-dark-card shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-dark-text">
                Portfolio Holdings
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-dark-text-secondary">
                Your current positions and performance
              </p>
            </div>
            <div className="border-t border-gray-200 dark:border-dark-border">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                  <thead className="bg-gray-50 dark:bg-dark-border">
                                          <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Symbol
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Quantity
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Value
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          P&L
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-dark-card divide-y divide-gray-200 dark:divide-dark-border">
                                          {portfolio.holdings.map((holding) => (
                        <tr key={holding.ticker}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-dark-text">
                            {holding.ticker}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-dark-text">
                            {holding.quantity}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-dark-text">
                            {formatCurrency(holding.value)}
                          </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={getColorForChange(holding.change)}>
                            {holding.change > 0 ? '+' : ''}{formatCurrency(holding.change)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}