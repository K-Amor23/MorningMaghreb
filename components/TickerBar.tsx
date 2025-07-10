import { useState, useEffect } from 'react'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'

interface TickerData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

const mockTickerData: TickerData[] = [
  { symbol: 'MASI', name: 'Moroccan All Shares Index', price: 12456.78, change: 45.23, changePercent: 0.36 },
  { symbol: 'MADEX', name: 'Most Active Shares Index', price: 10234.56, change: -23.45, changePercent: -0.23 },
  { symbol: 'MASI-ESG', name: 'ESG Index', price: 8901.34, change: 12.67, changePercent: 0.14 },
  { symbol: 'ATW', name: 'Attijariwafa Bank', price: 45.60, change: 0.85, changePercent: 1.90 },
  { symbol: 'BMCE', name: 'BMCE Bank', price: 23.45, change: -0.32, changePercent: -1.35 },
  { symbol: 'CIH', name: 'CIH Bank', price: 34.20, change: 0.45, changePercent: 1.33 },
  { symbol: 'WAA', name: 'Wafa Assurance', price: 67.80, change: -1.20, changePercent: -1.74 },
  { symbol: 'CMT', name: 'Compagnie Minière', price: 89.45, change: 2.15, changePercent: 2.46 },
]

export default function TickerBar() {
  const [tickerData, setTickerData] = useState<TickerData[]>(mockTickerData)

  // Simulate live updates - only run on client side
  useEffect(() => {
    const interval = setInterval(() => {
      setTickerData(prev => prev.map(item => ({
        ...item,
        price: item.price + (Math.random() - 0.5) * 0.1,
        change: item.change + (Math.random() - 0.5) * 0.05,
        changePercent: ((item.change + (Math.random() - 0.5) * 0.05) / item.price) * 100
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-white border-b border-gray-200 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center h-12 bg-gradient-to-r from-casablanca-blue to-blue-600 text-white px-4">
          <span className="text-sm font-medium mr-4">Live Markets</span>
          <div className="flex-1 overflow-hidden">
            <div className="flex space-x-8 animate-scroll">
              {tickerData.map((item, index) => (
                <div key={item.symbol} className="flex items-center space-x-3 whitespace-nowrap">
                  <div className="text-sm font-medium">{item.symbol}</div>
                  <div className="text-sm">{item.price.toFixed(2)}</div>
                  <div className={`flex items-center text-xs ${
                    item.changePercent >= 0 ? 'text-green-300' : 'text-red-300'
                  }`}>
                    {item.changePercent >= 0 ? (
                      <ArrowUpIcon className="h-3 w-3 mr-1" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3 mr-1" />
                    )}
                    {Math.abs(item.changePercent).toFixed(2)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 