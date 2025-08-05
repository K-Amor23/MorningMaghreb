import {
  CurrencyDollarIcon,
  BanknotesIcon,
  ChartBarIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'
import { useState, useEffect } from 'react'

interface MacroIndicator {
  name: string
  value: string
  change: string
  changePercent: number
  icon: any
  description: string
}

// Client-side date component to prevent hydration errors
function ClientDate() {
  const [mounted, setMounted] = useState(false)
  const [date, setDate] = useState<string>('')

  useEffect(() => {
    setMounted(true)
    const updateDate = () => {
      setDate(new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      }))
    }

    updateDate()
    const interval = setInterval(updateDate, 60000) // Update every minute

    return () => clearInterval(interval)
  }, [])

  // Show a placeholder during SSR and initial render
  if (!mounted) {
    return <span>--</span>
  }

  return <span>{date}</span>
}

const macroData: MacroIndicator[] = [
  {
    name: 'BAM Policy Rate',
    value: '3.00%',
    change: '0.00%',
    changePercent: 0,
    icon: BanknotesIcon,
    description: 'Bank Al-Maghrib benchmark rate'
  },
  {
    name: 'FX Reserves',
    value: '$34.2B',
    change: '+$0.8B',
    changePercent: 2.4,
    icon: CurrencyDollarIcon,
    description: 'Foreign exchange reserves'
  },
  {
    name: 'Inflation Rate',
    value: '2.8%',
    change: '-0.1%',
    changePercent: -3.4,
    icon: ChartBarIcon,
    description: 'Consumer price index YoY'
  },
  {
    name: 'Trade Balance',
    value: '-$2.1B',
    change: '-$0.3B',
    changePercent: -16.7,
    icon: GlobeAltIcon,
    description: 'Monthly trade deficit'
  }
]

export default function MacroStats() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Macro Indicators</h2>

      <div className="space-y-4">
        {macroData.map((indicator) => (
          <div key={indicator.name} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              <indicator.icon className="h-6 w-6 text-casablanca-blue" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900">{indicator.name}</h3>
                <div className="text-right">
                  <div className="text-sm font-semibold text-gray-900">{indicator.value}</div>
                  <div className={`text-xs ${indicator.changePercent > 0 ? 'text-green-600' :
                      indicator.changePercent < 0 ? 'text-red-600' : 'text-gray-500'
                    }`}>
                    {indicator.change}
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">{indicator.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Source: Bank Al-Maghrib</span>
          <ClientDate />
        </div>
      </div>
    </div>
  )
} 