import { CalendarIcon, CurrencyDollarIcon, ChartBarIcon } from '@heroicons/react/24/outline'

interface CorporateActions {
  dividends: { date: string; amount: number }[]
  earnings: { date: string; estimate: number }[]
  splits: { date: string; ratio: string }[]
}

interface CorporateActionsProps {
  actions: CorporateActions
}

export default function CorporateActions({ actions }: CorporateActionsProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Corporate Actions
      </h3>

      {/* Dividends */}
      {actions.dividends.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <CurrencyDollarIcon className="h-4 w-4 text-green-600 mr-2" />
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              Dividends
            </h4>
          </div>
          <div className="space-y-2">
            {actions.dividends.map((dividend, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-dark-hover rounded">
                <div className="flex items-center">
                  <CalendarIcon className="h-3 w-3 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {formatDate(dividend.date)}
                  </span>
                </div>
                <span className="text-sm font-medium text-green-600">
                  {dividend.amount.toFixed(2)} MAD
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Earnings */}
      {actions.earnings.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <ChartBarIcon className="h-4 w-4 text-blue-600 mr-2" />
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              Earnings Dates
            </h4>
          </div>
          <div className="space-y-2">
            {actions.earnings.map((earning, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-dark-hover rounded">
                <div className="flex items-center">
                  <CalendarIcon className="h-3 w-3 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {formatDate(earning.date)}
                  </span>
                </div>
                <span className="text-sm font-medium text-blue-600">
                  Est. {earning.estimate.toFixed(2)} MAD
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stock Splits */}
      {actions.splits.length > 0 && (
        <div>
          <div className="flex items-center mb-3">
            <ChartBarIcon className="h-4 w-4 text-purple-600 mr-2" />
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              Stock Splits
            </h4>
          </div>
          <div className="space-y-2">
            {actions.splits.map((split, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-dark-hover rounded">
                <div className="flex items-center">
                  <CalendarIcon className="h-3 w-3 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {formatDate(split.date)}
                  </span>
                </div>
                <span className="text-sm font-medium text-purple-600">
                  {split.ratio}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {actions.dividends.length === 0 && actions.earnings.length === 0 && actions.splits.length === 0 && (
        <div className="text-center py-8">
          <CalendarIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No upcoming corporate actions
          </p>
        </div>
      )}
    </div>
  )
} 