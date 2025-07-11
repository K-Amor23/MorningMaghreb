import { useState } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import toast from 'react-hot-toast'

interface AddTickerFormProps {
  userId: string
  onTickerAdded: () => void
}

export default function AddTickerForm({ userId, onTickerAdded }: AddTickerFormProps) {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!ticker.trim()) {
      toast.error('Please enter a ticker symbol')
      return
    }

    if (!isSupabaseConfigured() || !supabase) {
      toast.error('Database connection not configured')
      return
    }

    const tickerUpper = ticker.trim().toUpperCase()
    setLoading(true)

    try {
      // Check if ticker already exists in user's watchlist
      const { data: existingTicker } = await supabase
        .from('watchlists')
        .select('id')
        .eq('user_id', userId)
        .eq('ticker', tickerUpper)
        .single()

      if (existingTicker) {
        toast.error(`${tickerUpper} is already in your watchlist`)
        return
      }

      // Add ticker to watchlist
      const { error } = await supabase
        .from('watchlists')
        .insert([
          {
            user_id: userId,
            ticker: tickerUpper,
          }
        ])

      if (error) {
        toast.error('Failed to add ticker to watchlist')
        console.error('Error adding ticker:', error)
        return
      }

      toast.success(`${tickerUpper} added to watchlist`)
      setTicker('')
      onTickerAdded()
    } catch (error) {
      toast.error('An error occurred. Please try again.')
      console.error('Add ticker error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="ticker" className="block text-sm font-medium text-gray-700">
          Add Stock Ticker
        </label>
        <div className="mt-1 flex rounded-md shadow-sm">
          <input
            type="text"
            name="ticker"
            id="ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
            placeholder="e.g., IAM, BCP, ATW"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !ticker.trim()}
            className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="loading-spinner h-4 w-4" />
            ) : (
              'Add'
            )}
          </button>
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Enter a Moroccan stock ticker symbol (e.g., IAM for Maroc Telecom)
        </p>
      </div>
    </form>
  )
} 