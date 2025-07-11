import { useState, useEffect } from 'react'
import { useUser } from '@/lib/useUser'

interface TradingAccountOverviewProps {
  accountId: string
}

interface AccountSummary {
  account: {
    id: string
    account_name: string
    initial_balance: number
    current_balance: number
    total_pnl: number
    total_pnl_percent: number
  }
  positions: Array<{
    id: string
    ticker: string
    quantity: number
    avg_cost: number
    total_cost: number
    current_value: number
    unrealized_pnl: number
    unrealized_pnl_percent: number
  }>
  total_positions_value: number
  total_unrealized_pnl: number
  total_unrealized_pnl_percent: number
  available_cash: number
  total_account_value: number
}

export default function TradingAccountOverview({ accountId }: TradingAccountOverviewProps) {
  const { user } = useUser()
  const [accountSummary, setAccountSummary] = useState<AccountSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (user && accountId) {
      fetchAccountSummary()
    }
  }, [user, accountId])

  const fetchAccountSummary = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/paper-trading/accounts/${accountId}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setAccountSummary(data)
      } else {
        setError('Failed to fetch account summary')
      }
    } catch (err) {
      setError('Error loading account data')
      console.error('Error fetching account summary:', err)
    } finally {
      setLoading(false)
    }
  }

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
    if (value > 0) return 'text-green-600 dark:text-green-400'
    if (value < 0) return 'text-red-600 dark:text-red-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              Error
            </h3>
            <div className="mt-2 text-sm text-red-700 dark:text-red-300">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!accountSummary) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Account Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Account Value</h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(accountSummary.total_account_value)}
          </p>
          <p className={`text-sm ${getColorForChange(accountSummary.total_unrealized_pnl_percent)}`}>
            {formatPercent(accountSummary.total_unrealized_pnl_percent)} from initial
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Available Cash</h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(accountSummary.available_cash)}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {((accountSummary.available_cash / accountSummary.total_account_value) * 100).toFixed(1)}% of portfolio
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Positions Value</h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(accountSummary.total_positions_value)}
          </p>
          <p className={`text-sm ${getColorForChange(accountSummary.total_unrealized_pnl)}`}>
            {formatPercent(accountSummary.total_unrealized_pnl_percent)} unrealized P&L
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total P&L</h3>
          <p className={`text-2xl font-bold ${getColorForChange(accountSummary.account.total_pnl)}`}>
            {formatCurrency(accountSummary.account.total_pnl)}
          </p>
          <p className={`text-sm ${getColorForChange(accountSummary.account.total_pnl_percent)}`}>
            {formatPercent(accountSummary.account.total_pnl_percent)} return
          </p>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Current Positions</h2>
        </div>
        
        {accountSummary.positions.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No positions</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Start trading to build your portfolio
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Stock
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Avg Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Current Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Unrealized P&L
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    P&L %
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {accountSummary.positions.map((position) => (
                  <tr key={position.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {position.ticker}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {position.quantity.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatCurrency(position.avg_cost)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatCurrency(position.current_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getColorForChange(position.unrealized_pnl)}>
                        {formatCurrency(position.unrealized_pnl)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getColorForChange(position.unrealized_pnl_percent)}>
                        {formatPercent(position.unrealized_pnl_percent)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
} 