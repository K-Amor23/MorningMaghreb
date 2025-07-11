import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'
import Link from 'next/link'

interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: string
  marketCap: string
}

const mockGainers: StockData[] = [
  { symbol: 'ATW', name: 'Attijariwafa Bank', price: 45.60, change: 0.85, changePercent: 1.90, volume: '234M MAD', marketCap: '45.6B MAD' },
  { symbol: 'CIH', name: 'CIH Bank', price: 34.20, change: 0.45, changePercent: 1.33, volume: '156M MAD', marketCap: '12.8B MAD' },
  { symbol: 'CMT', name: 'Compagnie Minière', price: 89.45, change: 2.15, changePercent: 2.46, volume: '89M MAD', marketCap: '8.9B MAD' },
  { symbol: 'WAA', name: 'Wafa Assurance', price: 67.80, change: 1.20, changePercent: 1.80, volume: '67M MAD', marketCap: '6.8B MAD' },
  { symbol: 'BMCE', name: 'BMCE Bank', price: 23.45, change: 0.32, changePercent: 1.38, volume: '123M MAD', marketCap: '23.5B MAD' },
]

const mockLosers: StockData[] = [
  { symbol: 'WAA', name: 'Wafa Assurance', price: 67.80, change: -1.20, changePercent: -1.74, volume: '67M MAD', marketCap: '6.8B MAD' },
  { symbol: 'BMCE', name: 'BMCE Bank', price: 23.45, change: -0.32, changePercent: -1.35, volume: '123M MAD', marketCap: '23.5B MAD' },
  { symbol: 'ATW', name: 'Attijariwafa Bank', price: 45.60, change: -0.85, changePercent: -1.83, volume: '234M MAD', marketCap: '45.6B MAD' },
  { symbol: 'CIH', name: 'CIH Bank', price: 34.20, change: -0.45, changePercent: -1.30, volume: '156M MAD', marketCap: '12.8B MAD' },
  { symbol: 'CMT', name: 'Compagnie Minière', price: 89.45, change: -2.15, changePercent: -2.35, volume: '89M MAD', marketCap: '8.9B MAD' },
]

export default function MoversTable() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Movers</h2>
      
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
                {mockGainers.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50">
                    <td className="py-2">
                      <Link href={`/company/${stock.symbol}`} className="block hover:bg-gray-50">
                        <div>
                          <div className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">{stock.symbol}</div>
                          <div className="text-xs text-gray-500">{stock.name}</div>
                        </div>
                      </Link>
                    </td>
                    <td className="py-2 text-sm text-gray-900">{stock.price.toFixed(2)}</td>
                    <td className="py-2">
                      <div className="flex items-center text-sm text-green-600">
                        <ArrowUpIcon className="h-3 w-3 mr-1" />
                        +{stock.changePercent.toFixed(2)}%
                      </div>
                    </td>
                    <td className="py-2 text-xs text-gray-500">{stock.volume}</td>
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
                {mockLosers.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50">
                    <td className="py-2">
                      <Link href={`/company/${stock.symbol}`} className="block hover:bg-gray-50">
                        <div>
                          <div className="text-sm font-medium text-gray-900 hover:text-casablanca-blue">{stock.symbol}</div>
                          <div className="text-xs text-gray-500">{stock.name}</div>
                        </div>
                      </Link>
                    </td>
                    <td className="py-2 text-sm text-gray-900">{stock.price.toFixed(2)}</td>
                    <td className="py-2">
                      <div className="flex items-center text-sm text-red-600">
                        <ArrowDownIcon className="h-3 w-3 mr-1" />
                        {stock.changePercent.toFixed(2)}%
                      </div>
                    </td>
                    <td className="py-2 text-xs text-gray-500">{stock.volume}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
} 