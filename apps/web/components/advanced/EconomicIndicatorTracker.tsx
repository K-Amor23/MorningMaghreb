'use client'

import { useState, useEffect } from 'react'
import { ChartBarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon } from '@heroicons/react/24/outline'

interface EconomicIndicator {
  name: string
  key: string
  current_value: number
  previous_value: number
  change: number
  trend: 'increasing' | 'decreasing' | 'stable'
  unit: string
  chart_data: Array<{ date: string; value: number }>
  ai_summary: string
}

interface EconomicDashboard {
  indicators: Record<string, EconomicIndicator>
  last_updated: string
  overall_trend: string
  market_sentiment: string
}

interface EconomicIndicatorTrackerProps {
  className?: string
}

export default function EconomicIndicatorTracker({ className = '' }: EconomicIndicatorTrackerProps) {
  const [dashboard, setDashboard] = useState<EconomicDashboard | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedIndicator, setSelectedIndicator] = useState<string | null>(null)

  const fetchEconomicDashboard = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/advanced/economic-dashboard')

      if (!response.ok) {
        throw new Error('Failed to fetch economic dashboard')
      }

      const data = await response.json()
      setDashboard(data)
    } catch (error) {
      console.error('Error fetching economic dashboard:', error)
      // Fallback to mock data
      const mockDashboard: EconomicDashboard = {
        indicators: {
          key_policy_rate: {
            name: 'Key Policy Rate',
            key: 'key_policy_rate',
            current_value: 3.0,
            previous_value: 3.0,
            change: 0.0,
            trend: 'stable',
            unit: '%',
            chart_data: [
              { date: '2024-01', value: 3.0 },
              { date: '2024-02', value: 3.0 },
              { date: '2024-03', value: 3.0 },
              { date: '2024-04', value: 3.0 },
              { date: '2024-05', value: 3.0 },
              { date: '2024-06', value: 3.0 }
            ],
            ai_summary: 'Policy rate remains stable at 3.0% as BAM maintains accommodative stance to support economic recovery.'
          },
          inflation_cpi: {
            name: 'Inflation (CPI)',
            key: 'inflation_cpi',
            current_value: 2.8,
            previous_value: 2.5,
            change: 0.3,
            trend: 'increasing',
            unit: '%',
            chart_data: [
              { date: '2024-01', value: 2.1 },
              { date: '2024-02', value: 2.2 },
              { date: '2024-03', value: 2.3 },
              { date: '2024-04', value: 2.4 },
              { date: '2024-05', value: 2.5 },
              { date: '2024-06', value: 2.8 }
            ],
            ai_summary: 'Inflation rose to 2.8% in June, driven by food and energy prices. Still within BAM\'s target range.'
          },
          foreign_exchange_reserves: {
            name: 'FX Reserves',
            key: 'foreign_exchange_reserves',
            current_value: 3500000000000,
            previous_value: 3450000000000,
            change: 1.45,
            trend: 'increasing',
            unit: 'B MAD',
            chart_data: [
              { date: '2024-01', value: 3300000000000 },
              { date: '2024-02', value: 3350000000000 },
              { date: '2024-03', value: 3400000000000 },
              { date: '2024-04', value: 3420000000000 },
              { date: '2024-05', value: 3450000000000 },
              { date: '2024-06', value: 3500000000000 }
            ],
            ai_summary: 'FX reserves increased to 350B MAD, providing strong external buffer and supporting currency stability.'
          }
        },
        last_updated: new Date().toISOString(),
        overall_trend: 'stable',
        market_sentiment: 'positive'
      }
      setDashboard(mockDashboard)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEconomicDashboard()
  }, [])

  const formatValue = (value: number, unit: string) => {
    if (unit === 'B MAD' && value >= 1000000000000) {
      return `${(value / 1000000000000).toFixed(1)}B MAD`
    }
    return `${value.toFixed(2)}${unit}`
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <ArrowTrendingUpIcon className="w-4 h-4 text-green-600" />
      case 'decreasing':
        return <ArrowTrendingDownIcon className="w-4 h-4 text-red-600" />
      default:
        return <MinusIcon className="w-4 h-4 text-gray-600" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600 dark:text-green-400'
      case 'decreasing':
        return 'text-red-600 dark:text-red-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  const renderMiniChart = (chartData: Array<{ date: string; value: number }>) => {
    const values = chartData.map(d => d.value)
    const maxValue = Math.max(...values)
    const minValue = Math.min(...values)
    const range = maxValue - minValue

    return (
      <div className="h-16 flex items-end justify-between space-x-1">
        {chartData.map((point, index) => {
          const height = range > 0 ? ((point.value - minValue) / range) * 100 : 50
          return (
            <div
              key={index}
              className="flex-1 bg-casablanca-blue/20 rounded-sm"
              style={{ height: `${height}%` }}
            />
          )
        })}
      </div>
    )
  }

  if (loading) {
    return (
      <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-casablanca-blue"></div>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Failed to load economic data
        </div>
      </div>
    )
  }

  const indicators = Object.values(dashboard.indicators)

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Economic Indicators
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {new Date(dashboard.last_updated).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-sm font-medium ${getTrendColor(dashboard.overall_trend)}`}>
            {dashboard.overall_trend}
          </span>
          <ChartBarIcon className="w-6 h-6 text-gray-400" />
        </div>
      </div>

      {/* Market Sentiment */}
      <div className="mb-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
              Market Sentiment
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Overall economic outlook
            </p>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            dashboard.market_sentiment === 'positive' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
              : dashboard.market_sentiment === 'negative'
              ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
          }`}>
            {dashboard.market_sentiment}
          </div>
        </div>
      </div>

      {/* Indicators Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {indicators.map((indicator) => (
          <div
            key={indicator.key}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedIndicator === indicator.key
                ? 'border-casablanca-blue bg-casablanca-blue/5'
                : 'border-gray-200 dark:border-dark-border hover:border-gray-300 dark:hover:border-gray-600'
            }`}
            onClick={() => setSelectedIndicator(selectedIndicator === indicator.key ? null : indicator.key)}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                {indicator.name}
              </h3>
              {getTrendIcon(indicator.trend)}
            </div>

            <div className="mb-3">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatValue(indicator.current_value, indicator.unit)}
              </div>
              <div className={`text-sm ${getTrendColor(indicator.trend)}`}>
                {indicator.change >= 0 ? '+' : ''}{indicator.change.toFixed(2)}% from previous
              </div>
            </div>

            {/* Mini Chart */}
            <div className="mb-3">
              {renderMiniChart(indicator.chart_data)}
            </div>

            {/* AI Summary (shown when selected) */}
            {selectedIndicator === indicator.key && (
              <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="text-xs font-medium text-blue-900 dark:text-blue-400 mb-1">
                  AI Analysis
                </h4>
                <p className="text-xs text-blue-800 dark:text-blue-300">
                  {indicator.ai_summary}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Quick Stats
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500 dark:text-gray-400">Increasing</div>
            <div className="font-medium text-gray-900 dark:text-white">
              {indicators.filter(i => i.trend === 'increasing').length}
            </div>
          </div>
          <div>
            <div className="text-gray-500 dark:text-gray-400">Decreasing</div>
            <div className="font-medium text-gray-900 dark:text-white">
              {indicators.filter(i => i.trend === 'decreasing').length}
            </div>
          </div>
          <div>
            <div className="text-gray-500 dark:text-gray-400">Stable</div>
            <div className="font-medium text-gray-900 dark:text-white">
              {indicators.filter(i => i.trend === 'stable').length}
            </div>
          </div>
          <div>
            <div className="text-gray-500 dark:text-gray-400">Avg Change</div>
            <div className="font-medium text-gray-900 dark:text-white">
              {(indicators.reduce((sum, i) => sum + Math.abs(i.change), 0) / indicators.length).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 