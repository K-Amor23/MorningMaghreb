'use client'

import { useState, useEffect } from 'react'
import { CurrencyDollarIcon, FunnelIcon } from '@heroicons/react/24/outline'

interface DividendEvent {
  company: string
  ticker: string
  ex_date: string
  payment_date: string
  amount: number
  dividend_yield: number
  payout_ratio: number
  frequency: string
}

interface DividendTrackerProps {
  className?: string
}

export default function DividendTracker({ className = '' }: DividendTrackerProps) {
  const [dividends, setDividends] = useState<DividendEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    minYield: '',
    maxYield: '',
    minPayoutRatio: '',
    maxPayoutRatio: '',
    frequency: ''
  })
  const [showFilters, setShowFilters] = useState(false)

  const frequencies = ['Semi-annual', 'Annual', 'Quarterly']

  const fetchDividends = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.minYield) params.append('min_yield', filters.minYield)
      if (filters.maxYield) params.append('max_yield', filters.maxYield)
      if (filters.minPayoutRatio) params.append('min_payout_ratio', filters.minPayoutRatio)
      if (filters.maxPayoutRatio) params.append('max_payout_ratio', filters.maxPayoutRatio)

      const response = await fetch(`/api/advanced/dividends?${params.toString()}`)

      if (!response.ok) {
        throw new Error('Failed to fetch dividend events')
      }

      const data = await response.json()
      setDividends(data)
    } catch (error) {
      console.error('Error fetching dividends:', error)
      // Fallback to mock data
      const mockDividends: DividendEvent[] = [
        {
          company: 'Attijariwafa Bank',
          ticker: 'ATW',
          ex_date: '2024-12-15',
          payment_date: '2024-12-20',
          amount: 15.0,
          dividend_yield: 4.1,
          payout_ratio: 45.2,
          frequency: 'Semi-annual'
        },
        {
          company: 'Maroc Telecom',
          ticker: 'IAM',
          ex_date: '2024-12-10',
          payment_date: '2024-12-15',
          amount: 3.5,
          dividend_yield: 4.6,
          payout_ratio: 52.1,
          frequency: 'Semi-annual'
        },
        {
          company: 'Banque Centrale Populaire',
          ticker: 'BCP',
          ex_date: '2024-12-20',
          payment_date: '2024-12-25',
          amount: 8.5,
          dividend_yield: 3.8,
          payout_ratio: 38.5,
          frequency: 'Semi-annual'
        },
        {
          company: 'Wafa Assurance',
          ticker: 'WAA',
          ex_date: '2024-11-30',
          payment_date: '2024-12-05',
          amount: 2.1,
          dividend_yield: 5.2,
          payout_ratio: 65.3,
          frequency: 'Annual'
        },
        {
          company: 'Ciments du Maroc',
          ticker: 'CMA',
          ex_date: '2024-12-25',
          payment_date: '2024-12-30',
          amount: 12.0,
          dividend_yield: 3.2,
          payout_ratio: 42.1,
          frequency: 'Annual'
        }
      ]
      setDividends(mockDividends)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDividends()
  }, [filters])

  const clearFilters = () => {
    setFilters({
      minYield: '',
      maxYield: '',
      minPayoutRatio: '',
      maxPayoutRatio: '',
      frequency: ''
    })
  }

  const getDaysUntilExDate = (exDate: string) => {
    const today = new Date()
    const ex = new Date(exDate)
    const diffTime = ex.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getYieldColor = (yield_: number) => {
    if (yield_ >= 5.0) return 'text-green-600 dark:text-green-400'
    if (yield_ >= 3.5) return 'text-blue-600 dark:text-blue-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  const getPayoutRatioColor = (ratio: number) => {
    if (ratio > 80) return 'text-red-600 dark:text-red-400'
    if (ratio > 60) return 'text-orange-600 dark:text-orange-400'
    return 'text-green-600 dark:text-green-400'
  }

  const filteredDividends = dividends.filter(dividend => {
    if (filters.frequency && dividend.frequency !== filters.frequency) return false
    return true
  })

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Dividend Tracker
        </h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg transition-colors ${
              showFilters
                ? 'bg-casablanca-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <FunnelIcon className="w-5 h-5" />
          </button>
          <CurrencyDollarIcon className="w-6 h-6 text-gray-400" />
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Min Yield (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.minYield}
                onChange={(e) => setFilters({ ...filters, minYield: e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="0.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Max Yield (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.maxYield}
                onChange={(e) => setFilters({ ...filters, maxYield: e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="10.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Min Payout Ratio (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.minPayoutRatio}
                onChange={(e) => setFilters({ ...filters, minPayoutRatio: e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="0.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Max Payout Ratio (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.maxPayoutRatio}
                onChange={(e) => setFilters({ ...filters, maxPayoutRatio: e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="100.0"
              />
            </div>
          </div>
          
          <div className="mt-4 flex items-center justify-between">
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Frequency
              </label>
              <select
                value={filters.frequency}
                onChange={(e) => setFilters({ ...filters, frequency: e.target.value })}
                className="px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
              >
                <option value="">All Frequencies</option>
                {frequencies.map(freq => (
                  <option key={freq} value={freq}>{freq}</option>
                ))}
              </select>
            </div>
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      )}

      {/* Dividend List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Upcoming Dividends ({filteredDividends.length})
          </h3>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Sorted by ex-date
          </div>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-casablanca-blue"></div>
          </div>
        ) : filteredDividends.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No dividends found matching your criteria
          </div>
        ) : (
          filteredDividends
            .sort((a, b) => new Date(a.ex_date).getTime() - new Date(b.ex_date).getTime())
            .map((dividend) => {
              const daysUntilEx = getDaysUntilExDate(dividend.ex_date)
              
              return (
                <div
                  key={`${dividend.ticker}-${dividend.ex_date}`}
                  className="p-4 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {dividend.company} ({dividend.ticker})
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {dividend.frequency} • {formatDate(dividend.ex_date)} → {formatDate(dividend.payment_date)}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-gray-900 dark:text-white">
                            {dividend.amount.toFixed(2)} MAD
                          </div>
                          <div className={`text-sm font-medium ${getYieldColor(dividend.dividend_yield)}`}>
                            {dividend.dividend_yield.toFixed(1)}% Yield
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-4">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Ex-Date: </span>
                            <span className={daysUntilEx <= 7 ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-900 dark:text-white'}>
                              {daysUntilEx === 0 ? 'Today' : 
                               daysUntilEx < 0 ? `${Math.abs(daysUntilEx)} days ago` :
                               `${daysUntilEx} days`}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Payout Ratio: </span>
                            <span className={`font-medium ${getPayoutRatioColor(dividend.payout_ratio)}`}>
                              {dividend.payout_ratio.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {dividend.frequency}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })
        )}
      </div>

      {/* Summary Stats */}
      {filteredDividends.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Summary
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-500 dark:text-gray-400">Avg Yield</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {(filteredDividends.reduce((sum, d) => sum + d.dividend_yield, 0) / filteredDividends.length).toFixed(1)}%
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Avg Payout Ratio</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {(filteredDividends.reduce((sum, d) => sum + d.payout_ratio, 0) / filteredDividends.length).toFixed(1)}%
              </div>
            </div>
                         <div>
               <div className="text-gray-500 dark:text-gray-400">High Yield (&gt;5%)</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {filteredDividends.filter(d => d.dividend_yield > 5).length}
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Next 7 Days</div>
              <div className="font-medium text-gray-900 dark:text-white">
                {filteredDividends.filter(d => getDaysUntilExDate(d.ex_date) <= 7 && getDaysUntilExDate(d.ex_date) >= 0).length}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 