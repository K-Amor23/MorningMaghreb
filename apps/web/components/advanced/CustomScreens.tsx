'use client'

import { useState, useEffect } from 'react'
import { MagnifyingGlassIcon, PlusIcon, BookmarkIcon, TrashIcon } from '@heroicons/react/24/outline'

interface CustomScreen {
  id: string
  name: string
  filters: Record<string, any>
  results: Array<{
    ticker: string
    name: string
    pe_ratio: number
    dividend_yield: number
    market_cap: number
    roe: number
  }>
  created_at: string
  last_run: string
}

interface CustomScreensProps {
  className?: string
}

export default function CustomScreens({ className = '' }: CustomScreensProps) {
  const [screens, setScreens] = useState<CustomScreen[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newScreen, setNewScreen] = useState({
    name: '',
    filters: {
      pe_ratio_max: '',
      pe_ratio_min: '',
      dividend_yield_min: '',
      dividend_yield_max: '',
      market_cap_min: '',
      market_cap_max: '',
      roe_min: '',
      roe_max: ''
    }
  })

  const fetchScreens = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/advanced/screens')

      if (!response.ok) {
        throw new Error('Failed to fetch custom screens')
      }

      const data = await response.json()
      setScreens(data)
    } catch (error) {
      console.error('Error fetching screens:', error)
      // Fallback to mock data
      const mockScreens: CustomScreen[] = [
        {
          id: 'screen_1',
          name: 'Value Stocks Screen',
          filters: { pe_ratio_max: 15, dividend_yield_min: 3.0 },
          results: [
            { ticker: 'ATW', name: 'Attijariwafa Bank', pe_ratio: 11.3, dividend_yield: 4.1, market_cap: 102000000000, roe: 19.4 },
            { ticker: 'WAA', name: 'Wafa Assurance', pe_ratio: 9.2, dividend_yield: 5.2, market_cap: 45000000000, roe: 15.8 }
          ],
          created_at: new Date().toISOString(),
          last_run: new Date().toISOString()
        },
        {
          id: 'screen_2',
          name: 'High Dividend Screen',
          filters: { dividend_yield_min: 4.0 },
          results: [
            { ticker: 'WAA', name: 'Wafa Assurance', pe_ratio: 9.2, dividend_yield: 5.2, market_cap: 45000000000, roe: 15.8 },
            { ticker: 'IAM', name: 'Maroc Telecom', pe_ratio: 14.2, dividend_yield: 4.6, market_cap: 98000000000, roe: 18.5 }
          ],
          created_at: new Date().toISOString(),
          last_run: new Date().toISOString()
        }
      ]
      setScreens(mockScreens)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchScreens()
  }, [])

  const createScreen = async () => {
    if (!newScreen.name.trim()) {
      alert('Please enter a screen name')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/advanced/screens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newScreen.name,
          filters: newScreen.filters,
          user_id: 'mock_user'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create screen')
      }

      const data = await response.json()
      setScreens([...screens, data])
      setShowCreateForm(false)
      setNewScreen({
        name: '',
        filters: {
          pe_ratio_max: '',
          pe_ratio_min: '',
          dividend_yield_min: '',
          dividend_yield_max: '',
          market_cap_min: '',
          market_cap_max: '',
          roe_min: '',
          roe_max: ''
        }
      })
    } catch (error) {
      console.error('Error creating screen:', error)
      // Mock creation
      const mockScreen: CustomScreen = {
        id: `screen_${Date.now()}`,
        name: newScreen.name,
        filters: newScreen.filters,
        results: [
          { ticker: 'ATW', name: 'Attijariwafa Bank', pe_ratio: 11.3, dividend_yield: 4.1, market_cap: 102000000000, roe: 19.4 }
        ],
        created_at: new Date().toISOString(),
        last_run: new Date().toISOString()
      }
      setScreens([...screens, mockScreen])
      setShowCreateForm(false)
      setNewScreen({
        name: '',
        filters: {
          pe_ratio_max: '',
          pe_ratio_min: '',
          dividend_yield_min: '',
          dividend_yield_max: '',
          market_cap_min: '',
          market_cap_max: '',
          roe_min: '',
          roe_max: ''
        }
      })
    } finally {
      setLoading(false)
    }
  }

  const deleteScreen = async (screenId: string) => {
    if (!confirm('Are you sure you want to delete this screen?')) return

    setScreens(screens.filter(screen => screen.id !== screenId))
    // TODO: Implement actual deletion with backend
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(1)}B MAD`
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M MAD`
    } else {
      return `${value.toLocaleString()} MAD`
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Custom Screens
        </h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center space-x-2 px-4 py-2 bg-casablanca-blue text-white rounded-lg hover:bg-casablanca-blue/90 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            <span className="text-sm font-medium">New Screen</span>
          </button>
          <MagnifyingGlassIcon className="w-6 h-6 text-gray-400" />
        </div>
      </div>

      {/* Create New Screen Form */}
      {showCreateForm && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Create New Screen
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Screen Name
              </label>
              <input
                type="text"
                value={newScreen.name}
                onChange={(e) => setNewScreen({ ...newScreen, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="e.g., Value Stocks, High Dividend"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                P/E Max
              </label>
              <input
                type="number"
                step="0.1"
                value={newScreen.filters.pe_ratio_max}
                onChange={(e) => setNewScreen({
                  ...newScreen,
                  filters: { ...newScreen.filters, pe_ratio_max: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="15.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                P/E Min
              </label>
              <input
                type="number"
                step="0.1"
                value={newScreen.filters.pe_ratio_min}
                onChange={(e) => setNewScreen({
                  ...newScreen,
                  filters: { ...newScreen.filters, pe_ratio_min: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="5.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                Dividend Yield Min (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={newScreen.filters.dividend_yield_min}
                onChange={(e) => setNewScreen({
                  ...newScreen,
                  filters: { ...newScreen.filters, dividend_yield_min: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="3.0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                ROE Min (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={newScreen.filters.roe_min}
                onChange={(e) => setNewScreen({
                  ...newScreen,
                  filters: { ...newScreen.filters, roe_min: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
                placeholder="10.0"
              />
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3">
            <button
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={createScreen}
              disabled={loading || !newScreen.name.trim()}
              className="px-4 py-2 bg-casablanca-blue text-white rounded-lg hover:bg-casablanca-blue/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Creating...' : 'Create Screen'}
            </button>
          </div>
        </div>
      )}

      {/* Screens List */}
      <div className="space-y-4">
        {loading && screens.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-casablanca-blue"></div>
          </div>
        ) : screens.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <BookmarkIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No custom screens yet</p>
            <p className="text-sm">Create your first screen to get started</p>
          </div>
        ) : (
          screens.map((screen) => (
            <div
              key={screen.id}
              className="p-4 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {screen.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Created {formatDate(screen.created_at)} • Last run {formatDate(screen.last_run)}
                  </p>
                </div>
                <button
                  onClick={() => deleteScreen(screen.id)}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete screen"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>

              {/* Filters Summary */}
              <div className="mb-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Filters:</div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(screen.filters).map(([key, value]) => {
                    if (!value) return null
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                    return (
                      <span
                        key={key}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs text-gray-700 dark:text-gray-300 rounded"
                      >
                        {label}: {value}
                      </span>
                    )
                  })}
                </div>
              </div>

              {/* Results */}
              <div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  Results ({screen.results.length} companies)
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {screen.results.slice(0, 6).map((result) => (
                    <div
                      key={result.ticker}
                      className="p-3 bg-white dark:bg-dark-bg border border-gray-200 dark:border-dark-border rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {result.ticker}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {result.name}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">P/E:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{result.pe_ratio.toFixed(1)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Yield:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{result.dividend_yield.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">ROE:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{result.roe.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Market Cap:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{formatCurrency(result.market_cap)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {screen.results.length > 6 && (
                  <div className="mt-3 text-center">
                    <button className="text-sm text-casablanca-blue hover:text-casablanca-blue/80 transition-colors">
                      View all {screen.results.length} results
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
} 