import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'

const InteractiveChart = dynamic(() => import('./charts/InteractiveChart'), { ssr: false })

interface ChartData {
  date: string
  value: number
}

// Generate mock data for the last 30 days
const generateMockData = (): ChartData[] => {
  const data: ChartData[] = []
  const baseValue = 12400
  let currentValue = baseValue
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    
    // Add some random variation
    const change = (Math.random() - 0.5) * 200
    currentValue += change
    
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: Math.round(currentValue)
    })
  }
  
  return data
}

export default function MiniChart() {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [mounted, setMounted] = useState(false)
  const [showInteractive, setShowInteractive] = useState(false)

  useEffect(() => {
    setMounted(true)
    setChartData(generateMockData())
  }, [])

  // Show loading state during SSR
  if (!mounted) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">MASI Trend</h2>
          <div className="text-sm text-gray-500">30 days</div>
        </div>
        <div className="h-48 flex items-center justify-center">
          <div className="text-gray-500">Loading chart...</div>
        </div>
      </div>
    )
  }

  return (
    <>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">MASI Trend</h2>
        <div className="text-sm text-gray-500">30 days</div>
      </div>
      
      <div className="h-48 cursor-pointer" onClick={() => setShowInteractive(true)}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis 
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              domain={['dataMin - 100', 'dataMax + 100']}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px'
              }}
              formatter={(value: any) => [value.toLocaleString(), 'MASI']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#1E3A8A" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#1E3A8A' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Current:</span>
          <span className="font-semibold text-gray-900">
            {chartData[chartData.length - 1]?.value.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-1">
          <span className="text-gray-600">Change:</span>
          <span className="text-green-600 font-medium">
            +{((chartData[chartData.length - 1]?.value || 0) - (chartData[0]?.value || 0)).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
    {showInteractive && (
      <InteractiveChart
        ticker="MASI"
        candles={chartData.map(d => ({ time: new Date(`${d.date} ${new Date().getFullYear()}`).toISOString().slice(0,10), open: d.value, high: d.value, low: d.value, close: d.value }))}
        initialStyle="line"
        dark={false}
        onClose={() => setShowInteractive(false)}
      />
    )}
    </>
  )
} 