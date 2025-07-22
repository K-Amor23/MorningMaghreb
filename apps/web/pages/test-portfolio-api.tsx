import { useState, useEffect } from 'react'
import { portfolioService } from '@/lib/portfolioService'

export default function TestPortfolioAPI() {
  const [testResults, setTestResults] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    runTests()
  }, [])

  const runTests = async () => {
    setLoading(true)
    const results: string[] = []

    try {
      // Test 1: Get portfolio summary
      results.push('🧪 Testing portfolio summary...')
      const summary = await portfolioService.getPortfolioSummary('portfolio_1')
      results.push(`✅ Portfolio summary loaded: ${summary.total_value} MAD`)
      results.push(`   - Total cost: ${summary.total_cost} MAD`)
      results.push(`   - Gain/Loss: ${summary.total_gain_loss} MAD (${summary.total_gain_loss_percent.toFixed(2)}%)`)

      // Test 2: Get portfolio holdings
      results.push('🧪 Testing portfolio holdings...')
      const holdings = await portfolioService.getPortfolioHoldings('portfolio_1')
      results.push(`✅ Portfolio holdings loaded: ${holdings.length} holdings`)
      holdings.forEach(holding => {
        results.push(`   - ${holding.ticker}: ${holding.quantity} shares @ ${holding.purchase_price} MAD`)
      })

      // Test 3: Add a new holding
      results.push('🧪 Testing add holding...')
      const newHolding = await portfolioService.addHolding('portfolio_1', {
        ticker: 'TEST',
        quantity: 10,
        purchase_price: 50.00,
        notes: 'Test holding'
      })
      results.push(`✅ New holding added: ${newHolding.ticker} - ${newHolding.quantity} shares`)

    } catch (error: any) {
      results.push(`❌ Test failed: ${error.message}`)
      console.error('Test error:', error)
    }

    setTestResults(results)
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Portfolio API Test
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            API Test Results
          </h2>
          
          {loading ? (
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {testResults.map((result, index) => (
                <div key={index} className="text-sm font-mono">
                  {result}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={runTests}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Run Tests Again
          </button>
        </div>

        <div className="mt-6">
          <a
            href="/portfolio"
            className="text-blue-500 hover:text-blue-600 underline"
          >
            Go to Portfolio Page
          </a>
        </div>
      </div>
    </div>
  )
} 