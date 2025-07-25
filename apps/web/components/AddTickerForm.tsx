import { useState } from 'react'
import { PlusIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface AddTickerFormProps {
  onTickerAdded?: () => void
}

export default function AddTickerForm({ onTickerAdded }: AddTickerFormProps) {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!ticker.trim()) {
      toast.error('Please enter a ticker symbol')
      return
    }

    const tickerUpper = ticker.trim().toUpperCase()
    setLoading(true)

    try {
      // Use the public API to add ticker
      const response = await fetch(`/api/markets/watchlist/public/${tickerUpper}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()

      toast.success(`${tickerUpper} added to watchlist`)
      setTicker('')

      // Trigger refresh of watchlist
      if (onTickerAdded) {
        onTickerAdded()
      }

    } catch (error) {
      console.error('Error adding ticker:', error)
      toast.error('Failed to add ticker to watchlist')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <input
        type="text"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        placeholder="Enter ticker (e.g., ATW)"
        className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-casablanca-blue focus:border-casablanca-blue"
        maxLength={10}
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !ticker.trim()}
        className="px-4 py-2 bg-casablanca-blue text-white rounded-md hover:bg-casablanca-blue-dark focus:outline-none focus:ring-2 focus:ring-casablanca-blue focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
      >
        {loading ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        ) : (
          <PlusIcon className="h-4 w-4" />
        )}
      </button>
    </form>
  )
} 