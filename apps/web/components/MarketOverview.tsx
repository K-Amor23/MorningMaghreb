import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'
import { useState, useEffect } from 'react'
import useSWR from 'swr'

interface IndexData {
  name: string
  symbol: string
  value: number
  change: number
  changePercent: number
  volume: string
}

interface MarketData {
  indices: {
    [key: string]: {
      value: number
      source: string
    }
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

// Fetcher function for SWR
const fetcher = (url: string) => fetch(url).then(res => res.json())

// Client-side time component to prevent hydration errors
function ClientTime() {
  const [mounted, setMounted] = useState(false)
  const [time, setTime] = useState<string>('')

  useEffect(() => {
    setMounted(true)
    const updateTime = () => {
      setTime(new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }))
    }

    updateTime()
    const interval = setInterval(updateTime, 1000)

    return () => clearInterval(interval)
  }, [])

  // Show a placeholder during SSR and initial render
  if (!mounted) {
    return <span className="text-gray-900 font-medium">--:--:--</span>
  }

  return <span className="text-gray-900 font-medium">{time}</span>
}

export default function MarketOverview() {
  const { data, error, isLoading } = useSWR<{ success: boolean; data: MarketData }>(
    '/api/market-data/unified?type=market-summary',
    fetcher,
    { refreshInterval: 30000 } // Refresh every 30 seconds
  )

  // Create indices data from API response
  const getIndicesData = (): IndexData[] => {
    if (!data?.data?.indices) {
      return []
    }

    const indices = data.data.indices
    const marketSummary = data.data.market_summary

    return [
      {
        name: 'Moroccan All Shares Index',
        symbol: 'MASI',
        value: indices.MASI?.value || 12456.78,
        change: 45.23, // Simulated for now
        changePercent: 0.36, // Simulated for now
        volume: '2.3B MAD'
      },
      {
        name: 'Most Active Shares Index',
        symbol: 'MADEX',
        value: indices.MADEX?.value || 10234.56,
        change: -23.45, // Simulated for now
        changePercent: -0.23, // Simulated for now
        volume: '1.8B MAD'
      },
      {
        name: 'Market Summary',
        symbol: 'SUMMARY',
        value: marketSummary?.total_companies || 0,
        change: (marketSummary?.positive_movers || 0) - (marketSummary?.negative_movers || 0),
        changePercent: marketSummary?.total_companies ?
          ((marketSummary.positive_movers - marketSummary.negative_movers) / marketSummary.total_companies) * 100 : 0,
        volume: marketSummary?.total_market_cap_formatted || '0 MAD'
      }
    ]
  }

  const indices = getIndicesData()

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-gray-50 rounded-lg p-4">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-24 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-20"></div>
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
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>
        <div className="text-center py-8">
          <p className="text-red-600 mb-2">Failed to load market data</p>
          <p className="text-sm text-gray-500">Please try again later</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {indices.map((index) => (
          <div key={index.symbol} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-900">{index.symbol}</h3>
              <span className="text-xs text-gray-500">{index.name}</span>
            </div>

            <div className="flex items-baseline space-x-2 mb-2">
              <span className="text-2xl font-bold text-gray-900">
                {index.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <div className={`flex items-center text-sm font-medium ${index.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                {index.changePercent >= 0 ? (
                  <ArrowUpIcon className="h-4 w-4 mr-1" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 mr-1" />
                )}
                {Math.abs(index.changePercent).toFixed(2)}%
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>
                {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}
              </span>
              <span>Vol: {index.volume}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Last updated:</span>
          <ClientTime />
        </div>
        {data?.data?.market_summary && (
          <div className="mt-2 text-xs text-gray-500">
            <span className="mr-4">Companies: {data.data.market_summary.total_companies}</span>
            <span className="mr-4">Advancing: {data.data.market_summary.positive_movers}</span>
            <span className="mr-4">Declining: {data.data.market_summary.negative_movers}</span>
            <span>Market Cap: {data.data.market_summary.total_market_cap_formatted}</span>
          </div>
        )}
      </div>
    </div>
  )
} 