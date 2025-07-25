import { useState, useEffect } from 'react'
import { TrashIcon, EyeIcon } from '@heroicons/react/24/outline'
import { formatCurrency, formatPercent, getColorForChange } from '@/lib/utils'
import { fetchMarketData } from '@/lib/marketData'
import { MarketQuote } from '@/lib/supabase'
import toast from 'react-hot-toast'
import Link from 'next/link'

interface WatchlistItem {
  ticker: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  high: number
  low: number
  open: number
  close: number
  timestamp: string
}

interface WatchlistProps {
  userId?: string
}

export default function Watchlist({ userId }: WatchlistProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [removingTicker, setRemovingTicker] = useState<string | null>(null)

  const fetchWatchlist = async () => {
    try {
      setLoading(true)

      // Use the public watchlist API endpoint
      const response = await fetch('/api/markets/watchlist/public')

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setWatchlist(data || [])

    } catch (error) {
      console.error('Error fetching watchlist:', error)
      toast.error('Failed to load watchlist')

      // Fallback to mock data
      setWatchlist([
        {
          ticker: "ATW",
          name: "ATW Company",
          price: 125.50,
          change: 2.30,
          change_percent: 1.87,
          volume: 1500000,
          high: 127.00,
          low: 123.00,
          open: 123.20,
          close: 125.50,
          timestamp: "2024-01-01T00:00:00Z"
        },
        {
          ticker: "IAM",
          name: "IAM Company",
          price: 89.75,
          change: -1.25,
          change_percent: -1.37,
          volume: 2200000,
          high: 91.00,
          low: 88.50,
          open: 91.00,
          close: 89.75,
          timestamp: "2024-01-01T00:00:00Z"
        },
        {
          ticker: "BCP",
          name: "BCP Company",
          price: 156.80,
          change: 3.20,
          change_percent: 2.08,
          volume: 1800000,
          high: 158.00,
          low: 153.50,
          open: 153.60,
          close: 156.80,
          timestamp: "2024-01-01T00:00:00Z"
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const removeTicker = async (ticker: string) => {
    setRemovingTicker(ticker)

    try {
      // Use the public API to remove ticker
      const response = await fetch(`/api/markets/watchlist/public/${ticker}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Remove from local state
      setWatchlist(prev => prev.filter(item => item.ticker !== ticker))
      toast.success(`${ticker} removed from watchlist`)

    } catch (error) {
      toast.error('Failed to remove ticker from watchlist')
      console.error('Remove ticker error:', error)
    } finally {
      setRemovingTicker(null)
    }
  }

  useEffect(() => {
    fetchWatchlist()
  }, [])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // In a real app, you would fetch live data here
      // For now, we'll just simulate some price movements
      setWatchlist(prev => prev.map(item => ({
        ...item,
        price: item.price + (Math.random() - 0.5) * 2,
        change: item.change + (Math.random() - 0.5) * 0.5,
        change_percent: ((item.change + (Math.random() - 0.5) * 0.5) / item.price) * 100
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            My Watchlist
          </h3>
          <div className="flex items-center text-sm text-gray-500">
            <EyeIcon className="h-4 w-4 mr-1" />
            {watchlist.length} tickers
          </div>
        </div>
      </div>

      {watchlist.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <EyeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tickers in watchlist</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add some Moroccan stocks to start tracking their performance.
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {watchlist.map((item) => (
            <div key={item.ticker} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <Link href={`/company/${item.ticker}`} className="block">
                        <h4 className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">
                          {item.ticker}
                        </h4>
                      </Link>
                      <div className="mt-1 flex items-center space-x-4 text-sm">
                        <span className="text-gray-900 font-medium">
                          {formatCurrency(item.price)}
                        </span>
                        <span className={`font-medium ${getColorForChange(item.change)}`}>
                          {item.change > 0 ? '+' : ''}{item.change.toFixed(2)} ({formatPercent(item.change_percent)})
                        </span>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <div>Vol: {item.volume.toLocaleString()}</div>
                      <div>H: {formatCurrency(item.high)} L: {formatCurrency(item.low)}</div>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => removeTicker(item.ticker)}
                  disabled={removingTicker === item.ticker}
                  className="ml-4 p-1 text-gray-400 hover:text-red-500 disabled:opacity-50"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 