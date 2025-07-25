import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import useSWR from 'swr'

interface StockData {
  ticker: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  volume_formatted: string
  market_cap_formatted: string
  sector: string
  data_quality: string
}

interface QuotesResponse {
  success: boolean
  data: {
    quotes: StockData[]
    pagination: {
      page: number
      limit: number
      total: number
      total_pages: number
      has_next: boolean
      has_prev: boolean
    }
    market_summary: {
      total_companies: number
      total_market_cap: number
      total_market_cap_formatted: string
      positive_movers: number
      negative_movers: number
      unchanged: number
      average_price: number
    }
  }
}

// Fetcher function for SWR
const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function MoversTable() {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortBy, setSortBy] = useState<'change_percent' | 'volume' | 'market_cap'>('change_percent')

  const { data, error, isLoading } = useSWR<QuotesResponse>(
    `/api/markets/quotes?page=${currentPage}&limit=20&sort_by=${sortBy}`,
    fetcher,
    { refreshInterval: 30000 } // Refresh every 30 seconds
  )

  // Get top gainers and losers from the data
  const getTopMovers = () => {
    if (!data?.data?.quotes) return { gainers: [], losers: [] }

    const quotes = data.data.quotes
    const gainers = quotes
      .filter(quote => quote.change_percent > 0)
      .sort((a, b) => b.change_percent - a.change_percent)
      .slice(0, 5)

    const losers = quotes
      .filter(quote => quote.change_percent < 0)
      .sort((a, b) => a.change_percent - b.change_percent)
      .slice(0, 5)

    return { gainers, losers }
  }

  const { gainers, losers } = getTopMovers()

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Movers</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <div key={i}>
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-24 mb-3"></div>
                <div className="space-y-3">
                  {[...Array(5)].map((_, j) => (
                    <div key={j} className="h-12 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Movers</h2>
        <div className="text-center py-8">
          <p className="text-red-600 mb-2">Failed to load market data</p>
          <p className="text-sm text-gray-500">Please try again later</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Top Movers</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="change_percent">Change %</option>
            <option value="volume">Volume</option>
            <option value="market_cap">Market Cap</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div>
          <h3 className="text-sm font-medium text-green-600 mb-3 flex items-center">
            <ArrowUpIcon className="h-4 w-4 mr-1" />
            Top Gainers
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Symbol</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Price</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Change</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Volume</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {gainers.map((stock) => (
                  <tr key={stock.ticker} className="hover:bg-gray-50">
                    <td className="py-2">
                      <Link href={`/company/${stock.ticker}`} className="block hover:bg-gray-50">
                        <div>
                          <div className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">{stock.ticker}</div>
                          <div className="text-xs text-gray-500">{stock.name}</div>
                        </div>
                      </Link>
                    </td>
                    <td className="py-2 text-sm text-gray-900">{stock.price.toFixed(2)}</td>
                    <td className="py-2">
                      <div className="flex items-center text-sm text-green-600">
                        <ArrowUpIcon className="h-3 w-3 mr-1" />
                        +{stock.change_percent.toFixed(2)}%
                      </div>
                    </td>
                    <td className="py-2 text-xs text-gray-500">{stock.volume_formatted}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Losers */}
        <div>
          <h3 className="text-sm font-medium text-red-600 mb-3 flex items-center">
            <ArrowDownIcon className="h-4 w-4 mr-1" />
            Top Losers
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Symbol</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Price</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Change</th>
                  <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider py-2">Volume</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {losers.map((stock) => (
                  <tr key={stock.ticker} className="hover:bg-gray-50">
                    <td className="py-2">
                      <Link href={`/company/${stock.ticker}`} className="block hover:bg-gray-50">
                        <div>
                          <div className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">{stock.ticker}</div>
                          <div className="text-xs text-gray-500">{stock.name}</div>
                        </div>
                      </Link>
                    </td>
                    <td className="py-2 text-sm text-gray-900">{stock.price.toFixed(2)}</td>
                    <td className="py-2">
                      <div className="flex items-center text-sm text-red-600">
                        <ArrowDownIcon className="h-3 w-3 mr-1" />
                        {stock.change_percent.toFixed(2)}%
                      </div>
                    </td>
                    <td className="py-2 text-xs text-gray-500">{stock.volume_formatted}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pagination */}
      {data?.data?.pagination && (
        <div className="mt-6 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Showing {((data.data.pagination.page - 1) * data.data.pagination.limit) + 1} to{' '}
            {Math.min(data.data.pagination.page * data.data.pagination.limit, data.data.pagination.total)} of{' '}
            {data.data.pagination.total} companies
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={!data.data.pagination.has_prev}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-3 py-1 text-sm text-gray-700">
              Page {data.data.pagination.page} of {data.data.pagination.total_pages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={!data.data.pagination.has_next}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Market Summary */}
      {data?.data?.market_summary && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Total Companies:</span>
              <span className="ml-2 font-medium">{data.data.market_summary.total_companies}</span>
            </div>
            <div>
              <span className="text-gray-500">Advancing:</span>
              <span className="ml-2 font-medium text-green-600">{data.data.market_summary.positive_movers}</span>
            </div>
            <div>
              <span className="text-gray-500">Declining:</span>
              <span className="ml-2 font-medium text-red-600">{data.data.market_summary.negative_movers}</span>
            </div>
            <div>
              <span className="text-gray-500">Market Cap:</span>
              <span className="ml-2 font-medium">{data.data.market_summary.total_market_cap_formatted}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 