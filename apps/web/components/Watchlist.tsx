import { useState, useEffect } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import { TrashIcon, EyeIcon } from '@heroicons/react/24/outline'
import { formatCurrency, formatPercent, getColorForChange } from '@/lib/utils'
import { fetchMarketData, subscribeToMarketData } from '@/lib/marketData'
import { MarketQuote } from '@/lib/supabase'
import toast from 'react-hot-toast'
import Link from 'next/link'

interface WatchlistItem {
  id: string
  ticker: string
  created_at: string
}

interface WatchlistProps {
  userId: string
}

export default function Watchlist({ userId }: WatchlistProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [marketData, setMarketData] = useState<{ [key: string]: MarketQuote }>({})
  const [loading, setLoading] = useState(true)
  const [removingTicker, setRemovingTicker] = useState<string | null>(null)

  const fetchWatchlist = async () => {
    try {
      if (!isSupabaseConfigured() || !supabase) {
        toast.error('Watchlist is not available. Please configure Supabase.')
        return
      }

      const { data, error } = await supabase
        .from('watchlists')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      if (error) {
        console.error('Error fetching watchlist:', error)
        toast.error('Failed to load watchlist')
        return
      }

      setWatchlist(data || [])
      
      // Fetch market data for all tickers
      if (data && data.length > 0) {
        const tickers = data.map(item => item.ticker)
        for (const ticker of tickers) {
          const quote = await fetchMarketData(ticker)
          if (quote) {
            setMarketData(prev => ({ ...prev, [ticker]: quote }))
          }
        }
      }
    } catch (error) {
      console.error('Error fetching watchlist:', error)
      toast.error('Failed to load watchlist')
    } finally {
      setLoading(false)
    }
  }

  const removeTicker = async (id: string, ticker: string) => {
    setRemovingTicker(id)
    
    try {
      if (!supabase) {
        toast.error('Watchlist service is not available.')
        return
      }

      const { error } = await supabase
        .from('watchlists')
        .delete()
        .eq('id', id)

      if (error) {
        toast.error('Failed to remove ticker from watchlist')
        console.error('Error removing ticker:', error)
        return
      }

      setWatchlist(prev => prev.filter(item => item.id !== id))
      setMarketData(prev => {
        const newData = { ...prev }
        delete newData[ticker]
        return newData
      })
      toast.success(`${ticker} removed from watchlist`)
    } catch (error) {
      toast.error('An error occurred. Please try again.')
      console.error('Remove ticker error:', error)
    } finally {
      setRemovingTicker(null)
    }
  }

  useEffect(() => {
    fetchWatchlist()
  }, [userId])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // In a real app, you would fetch live data here
      // For now, we'll just simulate some price movements
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
          {watchlist.map((item) => {
            const quote = marketData[item.ticker]
            
            return (
              <div key={item.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <Link href={`/company/${item.ticker}`} className="block">
                          <h4 className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">
                            {item.ticker}
                          </h4>
                        </Link>
                        {quote ? (
                          <div className="mt-1 flex items-center space-x-4 text-sm">
                            <span className="text-gray-900 font-medium">
                              {formatCurrency(quote.close)}
                            </span>
                            <span className={`font-medium ${getColorForChange(quote.change)}`}>
                              {quote.change > 0 ? '+' : ''}{quote.change.toFixed(2)} ({formatPercent(quote.change_percent)})
                            </span>
                          </div>
                        ) : (
                          <p className="mt-1 text-sm text-gray-500">
                            Loading price data...
                          </p>
                        )}
                      </div>
                      
                      <button
                        onClick={() => removeTicker(item.id, item.ticker)}
                        disabled={removingTicker === item.id}
                        className="ml-4 p-1 text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded disabled:opacity-50"
                        title="Remove from watchlist"
                      >
                        {removingTicker === item.id ? (
                          <div className="loading-spinner h-4 w-4" />
                        ) : (
                          <TrashIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
} 