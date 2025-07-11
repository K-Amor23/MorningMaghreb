import { ArrowUpIcon, ArrowDownIcon, StarIcon } from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'

interface CompanyHeaderProps {
  company: {
    ticker: string
    name: string
    sector: string
    currentPrice: number
    priceChange: number
    priceChangePercent: number
  }
  isInWatchlist: boolean
  onToggleWatchlist: () => void
}

export default function CompanyHeader({ company, isInWatchlist, onToggleWatchlist }: CompanyHeaderProps) {
  const isPositive = company.priceChangePercent >= 0

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {company.name}
            </h1>
            <span className="text-lg font-medium text-gray-500 dark:text-gray-400">
              {company.ticker}
            </span>
            <button
              onClick={onToggleWatchlist}
              className="p-1 hover:bg-gray-100 dark:hover:bg-dark-hover rounded-full transition-colors"
            >
              {isInWatchlist ? (
                <StarIconSolid className="h-5 w-5 text-yellow-500" />
              ) : (
                <StarIcon className="h-5 w-5 text-gray-400 hover:text-yellow-500" />
              )}
            </button>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            {company.sector}
          </p>

          <div className="flex items-center space-x-6">
            <div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {company.currentPrice.toFixed(2)} MAD
              </div>
              <div className={`flex items-center text-sm ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {isPositive ? (
                  <ArrowUpIcon className="h-4 w-4 mr-1" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 mr-1" />
                )}
                {isPositive ? '+' : ''}{company.priceChange.toFixed(2)} ({isPositive ? '+' : ''}{company.priceChangePercent.toFixed(2)}%)
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end space-y-2">
          <button
            onClick={onToggleWatchlist}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isInWatchlist
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            {isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
          </button>
        </div>
      </div>
    </div>
  )
} 