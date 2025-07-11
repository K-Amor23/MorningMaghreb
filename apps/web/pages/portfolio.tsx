import Head from 'next/head'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useUser } from '@/lib/useUser'
import { portfolioService, PortfolioHolding, PortfolioSummary } from '@/lib/portfolioService'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import PortfolioHoldings from '@/components/PortfolioHoldings'
import AddHoldingForm from '@/components/AddHoldingForm'
import toast from 'react-hot-toast'

export default function Portfolio() {
  const { user, profile, loading } = useUser()
  const router = useRouter()
  const [holdings, setHoldings] = useState<PortfolioHolding[]>([])
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [portfolioLoading, setPortfolioLoading] = useState(true)
  const [portfolioId] = useState('portfolio_1') // Default portfolio ID

  // Check access control - require login
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  if (!user) {
    // Redirect to login if not authenticated
    router.push('/login?redirect=/portfolio')
    return null
  }

  // Load portfolio data
  useEffect(() => {
    const loadPortfolioData = async () => {
      try {
        setPortfolioLoading(true)
        const [holdingsData, summaryData] = await Promise.all([
          portfolioService.getPortfolioHoldings(portfolioId),
          portfolioService.getPortfolioSummary(portfolioId)
        ])
        setHoldings(holdingsData)
        setSummary(summaryData)
      } catch (error) {
        console.error('Error loading portfolio data:', error)
        toast.error('Failed to load portfolio data')
      } finally {
        setPortfolioLoading(false)
      }
    }

    loadPortfolioData()
  }, [portfolioId])

  const handleHoldingsUpdate = () => {
    // Reload portfolio data when holdings are updated
    const loadPortfolioData = async () => {
      try {
        const [holdingsData, summaryData] = await Promise.all([
          portfolioService.getPortfolioHoldings(portfolioId),
          portfolioService.getPortfolioSummary(portfolioId)
        ])
        setHoldings(holdingsData)
        setSummary(summaryData)
      } catch (error) {
        console.error('Error reloading portfolio data:', error)
      }
    }
    loadPortfolioData()
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MAD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <>
      <Head>
        <title>Portfolio - Casablanca Insight</title>
        <meta name="description" content="Track your Moroccan stock portfolio with advanced analytics and performance metrics." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        <TickerBar />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Portfolio Overview
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Track your investments and performance
            </p>
          </div>

          {/* Portfolio Summary Cards */}
          {portfolioLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2"></div>
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : summary ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Value</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.total_value)}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Cost</h3>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.total_cost)}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Gain/Loss</h3>
                <p className={`text-2xl font-bold ${summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {summary.total_gain_loss >= 0 ? '+' : ''}{formatCurrency(summary.total_gain_loss)}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Return %</h3>
                <p className={`text-2xl font-bold ${summary.total_gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(summary.total_gain_loss_percent)}
                </p>
              </div>
            </div>
          ) : null}

          {/* Add Holding Form */}
          <div className="mb-8">
            <AddHoldingForm portfolioId={portfolioId} onHoldingAdded={handleHoldingsUpdate} />
          </div>

          {/* Portfolio Holdings */}
          {portfolioLoading ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <PortfolioHoldings 
              portfolioId={portfolioId}
              holdings={holdings}
              onHoldingsUpdate={handleHoldingsUpdate}
            />
          )}

          {/* Portfolio Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Portfolio Performance</h2>
            <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">Performance chart coming soon</p>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 