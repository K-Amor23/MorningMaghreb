interface IncomeStatement {
  revenue: number
  costOfRevenue: number
  grossProfit: number
  operatingExpenses: number
  operatingIncome: number
  netIncome: number
}

interface BalanceSheet {
  totalAssets: number
  totalLiabilities: number
  totalEquity: number
  cash: number
  debt: number
}

interface FinancialTableProps {
  incomeStatement: IncomeStatement
  balanceSheet: BalanceSheet
}

export default function FinancialTable({ incomeStatement, balanceSheet }: FinancialTableProps) {
  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(1)}B MAD`
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M MAD`
    } else {
      return `${value.toLocaleString()} MAD`
    }
  }

  const incomeStatementData = [
    { label: 'Revenue', value: incomeStatement.revenue },
    { label: 'Cost of Revenue', value: incomeStatement.costOfRevenue },
    { label: 'Gross Profit', value: incomeStatement.grossProfit, isSubtotal: true },
    { label: 'Operating Expenses', value: incomeStatement.operatingExpenses },
    { label: 'Operating Income', value: incomeStatement.operatingIncome, isSubtotal: true },
    { label: 'Net Income', value: incomeStatement.netIncome, isTotal: true }
  ]

  const balanceSheetData = [
    { label: 'Cash & Equivalents', value: balanceSheet.cash },
    { label: 'Total Assets', value: balanceSheet.totalAssets, isSubtotal: true },
    { label: 'Total Debt', value: balanceSheet.debt },
    { label: 'Total Liabilities', value: balanceSheet.totalLiabilities, isSubtotal: true },
    { label: 'Total Equity', value: balanceSheet.totalEquity, isTotal: true }
  ]

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
        Financial Statements
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Income Statement */}
        <div>
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Income Statement (TTM)
          </h3>
          <div className="space-y-2">
            {incomeStatementData.map((item, index) => (
              <div
                key={index}
                className={`flex justify-between py-2 ${
                  item.isTotal 
                    ? 'border-t-2 border-gray-300 dark:border-gray-600 font-bold text-lg'
                    : item.isSubtotal
                    ? 'border-t border-gray-200 dark:border-gray-700 font-semibold'
                    : ''
                }`}
              >
                <span className="text-gray-700 dark:text-gray-300">{item.label}</span>
                <span className="text-gray-900 dark:text-white font-mono">
                  {formatCurrency(item.value)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Balance Sheet */}
        <div>
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
            Balance Sheet
          </h3>
          <div className="space-y-2">
            {balanceSheetData.map((item, index) => (
              <div
                key={index}
                className={`flex justify-between py-2 ${
                  item.isTotal 
                    ? 'border-t-2 border-gray-300 dark:border-gray-600 font-bold text-lg'
                    : item.isSubtotal
                    ? 'border-t border-gray-200 dark:border-gray-700 font-semibold'
                    : ''
                }`}
              >
                <span className="text-gray-700 dark:text-gray-300">{item.label}</span>
                <span className="text-gray-900 dark:text-white font-mono">
                  {formatCurrency(item.value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Note:</strong> All figures are in Moroccan Dirham (MAD). TTM = Trailing Twelve Months. 
          Financial data is based on the most recent available reports.
        </p>
      </div>
    </div>
  )
} 