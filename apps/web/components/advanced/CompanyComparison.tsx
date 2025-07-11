'use client'

import { useState, useEffect } from 'react'
import { ChartBarIcon, TableCellsIcon } from '@heroicons/react/24/outline'

interface CompanyData {
  ticker: string
  name: string
  revenue: number
  net_income: number
  roe: number
  pe_ratio: number
  debt_equity: number
  market_cap: number
  dividend_yield: number
}

interface ComparisonData {
  companies: string[]
  metrics: string[]
  data: Record<string, CompanyData>
  comparison_chart_data: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      backgroundColor: string
    }>
  }
}

interface CompanyComparisonProps {
  className?: string
}

export default function CompanyComparison({ className = '' }: CompanyComparisonProps) {
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    'revenue', 'net_income', 'roe', 'pe_ratio', 'debt_equity'
  ])
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null)
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table')
  const [loading, setLoading] = useState(false)

  const availableCompanies = [
    { ticker: 'ATW', name: 'Attijariwafa Bank' },
    { ticker: 'IAM', name: 'Maroc Telecom' },
    { ticker: 'BCP', name: 'Banque Centrale Populaire' },
    { ticker: 'BMCE', name: 'BMCE Bank' },
    { ticker: 'WAA', name: 'Wafa Assurance' },
    { ticker: 'CMA', name: 'Ciments du Maroc' }
  ]

  const availableMetrics = [
    { key: 'revenue', label: 'Revenue', format: 'currency' },
    { key: 'net_income', label: 'Net Income', format: 'currency' },
    { key: 'roe', label: 'ROE', format: 'percentage' },
    { key: 'pe_ratio', label: 'P/E Ratio', format: 'number' },
    { key: 'debt_equity', label: 'Debt/Equity', format: 'number' },
    { key: 'market_cap', label: 'Market Cap', format: 'currency' },
    { key: 'dividend_yield', label: 'Dividend Yield', format: 'percentage' }
  ]

  const formatValue = (value: number, format: string) => {
    switch (format) {
      case 'currency':
        if (value >= 1000000000) {
          return `${(value / 1000000000).toFixed(1)}B MAD`
        } else if (value >= 1000000) {
          return `${(value / 1000000).toFixed(1)}M MAD`
        } else {
          return `${value.toLocaleString()} MAD`
        }
      case 'percentage':
        return `${value.toFixed(1)}%`
      case 'number':
        return value.toFixed(2)
      default:
        return value.toString()
    }
  }

  const compareCompanies = async () => {
    if (selectedCompanies.length < 2 || selectedCompanies.length > 3) {
      alert('Please select 2-3 companies to compare')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/advanced/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          companies: selectedCompanies,
          metrics: selectedMetrics
        })
      })

      if (!response.ok) {
        throw new Error('Failed to compare companies')
      }

      const data = await response.json()
      setComparisonData(data)
    } catch (error) {
      console.error('Error comparing companies:', error)
      // Fallback to mock data
      const mockData: ComparisonData = {
        companies: selectedCompanies,
        metrics: selectedMetrics,
        data: {},
        comparison_chart_data: {
          labels: selectedCompanies,
          datasets: []
        }
      }

      selectedCompanies.forEach((company, index) => {
        mockData.data[company] = {
          ticker: company,
          name: availableCompanies.find(c => c.ticker === company)?.name || company,
          revenue: 40000000000 + (index * 5000000000),
          net_income: 8000000000 + (index * 1000000000),
          roe: 15.0 + (index * 2),
          pe_ratio: 12.0 + (index * 1.5),
          debt_equity: 0.8 + (index * 0.1),
          market_cap: 100000000000 + (index * 20000000000),
          dividend_yield: 3.5 + (index * 0.5)
        }
      })

      // Prepare chart data
      selectedMetrics.forEach((metric, index) => {
        const metricInfo = availableMetrics.find(m => m.key === metric)
        if (metricInfo && ['revenue', 'net_income', 'market_cap'].includes(metric)) {
          const values = selectedCompanies.map(company => mockData.data[company][metric as keyof CompanyData] as number)
          mockData.comparison_chart_data.datasets.push({
            label: metricInfo.label,
            data: values,
            backgroundColor: `rgba(${50 + index * 50}, ${100 + index * 30}, 255, 0.6)`
          })
        }
      })

      setComparisonData(mockData)
    } finally {
      setLoading(false)
    }
  }

  const toggleCompany = (ticker: string) => {
    if (selectedCompanies.includes(ticker)) {
      setSelectedCompanies(selectedCompanies.filter(c => c !== ticker))
    } else if (selectedCompanies.length < 3) {
      setSelectedCompanies([...selectedCompanies, ticker])
    }
  }

  const toggleMetric = (metric: string) => {
    if (selectedMetrics.includes(metric)) {
      setSelectedMetrics(selectedMetrics.filter(m => m !== metric))
    } else {
      setSelectedMetrics([...selectedMetrics, metric])
    }
  }

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Company Comparison Tool
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('table')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'table'
                ? 'bg-casablanca-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <TableCellsIcon className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('chart')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'chart'
                ? 'bg-casablanca-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <ChartBarIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Company Selection */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Select Companies (2-3)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {availableCompanies.map((company) => (
            <button
              key={company.ticker}
              onClick={() => toggleCompany(company.ticker)}
              className={`p-3 text-left rounded-lg border transition-colors ${
                selectedCompanies.includes(company.ticker)
                  ? 'border-casablanca-blue bg-casablanca-blue/10 text-casablanca-blue'
                  : 'border-gray-200 dark:border-dark-border hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="font-medium text-sm">{company.ticker}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{company.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Selection */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Select Metrics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {availableMetrics.map((metric) => (
            <button
              key={metric.key}
              onClick={() => toggleMetric(metric.key)}
              className={`p-2 text-sm rounded-lg border transition-colors ${
                selectedMetrics.includes(metric.key)
                  ? 'border-casablanca-blue bg-casablanca-blue/10 text-casablanca-blue'
                  : 'border-gray-200 dark:border-dark-border hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      {/* Compare Button */}
      <div className="mb-6">
        <button
          onClick={compareCompanies}
          disabled={selectedCompanies.length < 2 || loading}
          className="w-full bg-casablanca-blue text-white py-3 px-4 rounded-lg font-medium hover:bg-casablanca-blue/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Comparing...' : 'Compare Companies'}
        </button>
      </div>

      {/* Results */}
      {comparisonData && (
        <div className="mt-6">
          {viewMode === 'table' ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-dark-border">
                    <th className="text-left py-3 px-2 font-medium text-gray-900 dark:text-white">
                      Metric
                    </th>
                    {comparisonData.companies.map((company) => (
                      <th key={company} className="text-right py-3 px-2 font-medium text-gray-900 dark:text-white">
                        {company}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {selectedMetrics.map((metric) => {
                    const metricInfo = availableMetrics.find(m => m.key === metric)
                    return (
                      <tr key={metric} className="border-b border-gray-100 dark:border-gray-800">
                        <td className="py-3 px-2 font-medium text-gray-700 dark:text-gray-300">
                          {metricInfo?.label || metric}
                        </td>
                        {comparisonData.companies.map((company) => {
                          const value = comparisonData.data[company]?.[metric as keyof CompanyData] as number
                          return (
                            <td key={company} className="py-3 px-2 text-right font-mono text-gray-900 dark:text-white">
                              {value ? formatValue(value, metricInfo?.format || 'number') : 'N/A'}
                            </td>
                          )
                        })}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="h-64 flex items-end justify-between space-x-4">
              {comparisonData.companies.map((company, companyIndex) => (
                <div key={company} className="flex-1 flex flex-col items-center">
                  {comparisonData.comparison_chart_data.datasets.map((dataset, datasetIndex) => {
                    const value = dataset.data[companyIndex]
                    const maxValue = Math.max(...dataset.data)
                    const height = maxValue > 0 ? (value / maxValue) * 100 : 0
                    
                    return (
                      <div
                        key={datasetIndex}
                        className="w-full mb-2 relative"
                        style={{ height: `${height}%` }}
                      >
                        <div
                          className="w-full rounded-t"
                          style={{
                            backgroundColor: dataset.backgroundColor,
                            height: '100%'
                          }}
                        />
                      </div>
                    )
                  })}
                  <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-center">
                    <div className="font-medium">{company}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
} 