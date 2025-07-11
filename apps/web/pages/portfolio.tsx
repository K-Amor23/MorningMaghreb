import Head from 'next/head'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import MiniChart from '@/components/MiniChart'

export default function Portfolio() {
  const { user, profile, loading } = useUser()

  // Check access control
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  // Mock portfolio data
  const portfolio = [
    {
      symbol: 'ATW',
      name: 'Attijariwafa Bank',
      shares: 100,
      avgPrice: 45.50,
      currentPrice: 48.75
    },
    {
      symbol: 'BMCE',
      name: 'Bank of Africa',
      shares: 50,
      avgPrice: 32.20,
      currentPrice: 35.80
    },
    {
      symbol: 'CIH',
      name: 'CIH Bank',
      shares: 75,
      avgPrice: 28.90,
      currentPrice: 31.25
    },
    {
      symbol: 'IAM',
      name: 'Maroc Telecom',
      shares: 200,
      avgPrice: 85.30,
      currentPrice: 89.45
    }
  ]

  const totalValue = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.currentPrice), 0)
  const totalCost = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.avgPrice), 0)
  const totalGain = totalValue - totalCost
  const totalGainPercent = ((totalGain / totalCost) * 100).toFixed(2)

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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Value</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">MAD {totalValue.toLocaleString()}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Cost</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">MAD {totalCost.toLocaleString()}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Gain/Loss</h3>
              <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalGain >= 0 ? '+' : ''}MAD {totalGain.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Return %</h3>
              <p className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalGain >= 0 ? '+' : ''}{totalGainPercent}%
              </p>
            </div>
          </div>

          {/* Portfolio Holdings */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden mb-8">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Holdings</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {portfolio.map((stock) => {
                    const stockValue = stock.shares * stock.currentPrice
                    const stockGain = stockValue - (stock.shares * stock.avgPrice)
                    const stockGainPercent = ((stockGain / (stock.shares * stock.avgPrice)) * 100).toFixed(2)
                    
                    return (
                      <tr key={stock.symbol} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{stock.symbol}</div>
                            <div className="text-sm text-gray-500">{stock.name}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stock.shares}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MAD {stock.avgPrice}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MAD {stock.currentPrice}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${stockGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {stockGain >= 0 ? '+' : ''}{stockGainPercent}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">MAD {stockValue.toLocaleString()}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Portfolio Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Portfolio Performance</h2>
            <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
              <p className="text-gray-500">Performance chart coming soon</p>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 