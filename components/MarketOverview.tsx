import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'
import { useState, useEffect } from 'react'

interface IndexData {
  name: string
  symbol: string
  value: number
  change: number
  changePercent: number
  volume: string
}

const mockIndices: IndexData[] = [
  {
    name: 'Moroccan All Shares Index',
    symbol: 'MASI',
    value: 12456.78,
    change: 45.23,
    changePercent: 0.36,
    volume: '2.3B MAD'
  },
  {
    name: 'Most Active Shares Index',
    symbol: 'MADEX',
    value: 10234.56,
    change: -23.45,
    changePercent: -0.23,
    volume: '1.8B MAD'
  },
  {
    name: 'ESG Index',
    symbol: 'MASI-ESG',
    value: 8901.34,
    change: 12.67,
    changePercent: 0.14,
    volume: '456M MAD'
  }
]

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
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {mockIndices.map((index) => (
          <div key={index.symbol} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-900">{index.symbol}</h3>
              <span className="text-xs text-gray-500">{index.name}</span>
            </div>
            
            <div className="flex items-baseline space-x-2 mb-2">
              <span className="text-2xl font-bold text-gray-900">
                {index.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <div className={`flex items-center text-sm font-medium ${
                index.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
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
      </div>
    </div>
  )
} 