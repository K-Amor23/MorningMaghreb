interface SnapshotMetricsProps {
  company: {
    marketCap: number
    revenue: number
    netIncome: number
    peRatio: number
    dividendYield: number
    roe: number
  }
}

export default function SnapshotMetrics({ company }: SnapshotMetricsProps) {
  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(1)}B MAD`
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M MAD`
    } else {
      return `${value.toLocaleString()} MAD`
    }
  }

  const metrics = [
    {
      label: 'Market Cap',
      value: formatCurrency(company.marketCap),
      description: 'Total market value'
    },
    {
      label: 'Revenue (TTM)',
      value: formatCurrency(company.revenue),
      description: 'Trailing 12 months'
    },
    {
      label: 'Net Income',
      value: formatCurrency(company.netIncome),
      description: 'Annual profit'
    },
    {
      label: 'P/E Ratio',
      value: company.peRatio.toFixed(1),
      description: 'Price to earnings'
    },
    {
      label: 'ROE',
      value: `${company.roe.toFixed(1)}%`,
      description: 'Return on equity'
    },
    {
      label: 'Dividend Yield',
      value: `${company.dividendYield.toFixed(1)}%`,
      description: 'Annual dividend rate'
    }
  ]

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Key Metrics
      </h2>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
        {metrics.map((metric) => (
          <div key={metric.label} className="text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {metric.value}
            </div>
            <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {metric.label}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {metric.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 