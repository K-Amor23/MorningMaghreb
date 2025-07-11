import Head from 'next/head'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TickerBar from '@/components/TickerBar'
import MiniChart from '@/components/MiniChart'

export default function Portfolio() {
  // Mock portfolio data
  const portfolio = [
    { symbol: 'ATW', name: 'Attijariwafa Bank', shares: 100, avgPrice: 45.20, currentPrice: 47.80, change: '+5.75%' },
    { symbol: 'BMCE', name: 'BMCE Bank', shares: 50, avgPrice: 32.10, currentPrice: 33.45, change: '+4.20%' },
    { symbol: 'CIH', name: 'CIH Bank', shares: 75, avgPrice: 18.50, currentPrice: 19.20, change: '+3.78%' },
    { symbol: 'WAA', name: 'Wafa Assurance', shares: 200, avgPrice: 12.30, currentPrice: 12.80, change: '+4.07%' },
  ]

  const totalValue = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.currentPrice), 0)
  const totalCost = portfolio.reduce((sum, stock) => sum + (stock.shares * stock.avgPrice), 0)
  const totalGain = totalValue - totalCost
  const totalGainPercent = ((totalGain / totalCost) * 100).toFixed(2)

  return (
    <>
      <Head>
        <title>Portfolio - Casablanca Insight</title>
        <meta 
          name="description" 
          content="Track your Casablanca Stock Exchange investments, portfolio performance, and real-time P&L." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 text-gray-900">
        <Header />
        <TickerBar />

        <main className="px-4 py-6 max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
            <p className="text-gray-600 mt-2">Track your investments and performance</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <section className="lg:col-span-2 space-y-6">
              {/* Portfolio Summary */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Portfolio Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Total Value</div>
                    <div className="text-2xl font-bold text-gray-900">MAD {totalValue.toLocaleString()}</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Total Gain/Loss</div>
                    <div className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {totalGain >= 0 ? '+' : ''}MAD {totalGain.toLocaleString()}
                    </div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Return %</div>
                    <div className={`text-2xl font-bold ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {totalGain >= 0 ? '+' : ''}{totalGainPercent}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Portfolio Holdings */}
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-semibold">Holdings</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
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
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Portfolio Performance</h2>
                <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
                  <p className="text-gray-500">Performance chart coming soon</p>
                </div>
              </div>
            </section>

            <aside className="space-y-6">
              <MiniChart />
              
              {/* Quick Actions */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button className="w-full bg-casablanca-blue text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                    Add Stock
                  </button>
                  <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                    Export Portfolio
                  </button>
                  <button className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors">
                    Set Alerts
                  </button>
                </div>
              </div>

              {/* Watchlist */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Watchlist</h3>
                <div className="space-y-3">
                  {['IAM', 'SNP', 'TMA', 'CMT'].map((symbol) => (
                    <div key={symbol} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded cursor-pointer">
                      <span className="font-medium">{symbol}</span>
                      <span className="text-green-600 text-sm">+1.2%</span>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 