import { useState } from 'react'
import dynamic from 'next/dynamic'

const InteractiveChart = dynamic(() => import('../charts/InteractiveChart'), { ssr: false })

interface FinancialData {
  revenue: { year: number; value: number }[]
  netIncome: { year: number; value: number }[]
  eps: { year: number; value: number }[]
}

interface FinancialChartProps {
  data: FinancialData
}

type ChartType = 'revenue' | 'netIncome' | 'eps'

export default function FinancialChart({ data }: FinancialChartProps) {
  const [selectedMetric, setSelectedMetric] = useState<ChartType>('revenue')
  const [showInteractive, setShowInteractive] = useState(false)

  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(1)}B`
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`
    } else {
      return value.toLocaleString()
    }
  }

  const getChartData = () => {
    switch (selectedMetric) {
      case 'revenue':
        return data.revenue
      case 'netIncome':
        return data.netIncome
      case 'eps':
        return data.eps
      default:
        return data.revenue
    }
  }

  const chartData = getChartData()
  const maxValue = Math.max(...chartData.map(d => d.value))
  const minValue = Math.min(...chartData.map(d => d.value))

  const getBarHeight = (value: number) => {
    const range = maxValue - minValue
    return range > 0 ? ((value - minValue) / range) * 100 : 50
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Financial Performance
        </h2>
        <div className="flex space-x-2">
          {[
            { key: 'revenue' as ChartType, label: 'Revenue' },
            { key: 'netIncome' as ChartType, label: 'Net Income' },
            { key: 'eps' as ChartType, label: 'EPS' }
          ].map((metric) => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                selectedMetric === metric.key
                  ? 'bg-casablanca-blue text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>
      <div className="h-64 flex items-end justify-between space-x-2 cursor-pointer" onClick={() => setShowInteractive(true)}>
        {chartData.map((item, index) => (
          <div key={item.year} className="flex-1 flex flex-col items-center">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-t relative" style={{ height: `${getBarHeight(item.value)}%` }}>
              <div className="absolute inset-0 bg-casablanca-blue rounded-t"></div>
            </div>
            <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
              <div className="font-medium">{item.year}</div>
              <div className="text-xs">
                {selectedMetric === 'eps' 
                  ? item.value.toFixed(2)
                  : formatCurrency(item.value)
                }
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-500 dark:text-gray-400 text-center">
        {selectedMetric === 'revenue' && 'Revenue in MAD'}
        {selectedMetric === 'netIncome' && 'Net Income in MAD'}
        {selectedMetric === 'eps' && 'Earnings Per Share in MAD'}
      </div>

      {showInteractive && (
        <InteractiveChart
          ticker={selectedMetric.toUpperCase()}
          candles={chartData.map((d) => ({ time: `${d.year}-01-01`, open: d.value, high: d.value, low: d.value, close: d.value }))}
          onClose={() => setShowInteractive(false)}
          dark={false}
          initialStyle="line"
        />
      )}
    </div>
  )
} 