import { useState, useEffect } from 'react'
import { SparklesIcon, ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface AiSummaryProps {
  ticker: string
  language?: string
  onSummaryGenerated?: (summary: string) => void
}

interface AiSummaryData {
  ticker: string
  summary: string
  language: string
  generated_at: string
  company_data: any
  tokens_used: number
  cached: boolean
}

export default function AiSummary({
  ticker,
  language = 'en',
  onSummaryGenerated
}: AiSummaryProps) {
  const [summary, setSummary] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [summaryData, setSummaryData] = useState<AiSummaryData | null>(null)

  const fetchSummary = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/ai/company-summary/${ticker}?language=${language}`)

      if (!response.ok) {
        throw new Error('Failed to fetch AI summary')
      }

      const data: AiSummaryData = await response.json()
      setSummary(data.summary)
      setSummaryData(data)
      onSummaryGenerated?.(data.summary)
    } catch (err) {
      console.error('Error fetching AI summary:', err)
      setError('Failed to generate AI summary. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (ticker) {
      fetchSummary()
    }
  }, [ticker, language])

  const handleRefresh = () => {
    fetchSummary()
  }

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
        <div className="flex items-center mb-4">
          <SparklesIcon className="h-5 w-5 text-casablanca-blue mr-2" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Analysis
          </h2>
          <ArrowPathIcon className="h-4 w-4 text-gray-400 ml-2 animate-spin" />
        </div>

        <div className="space-y-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-1/2"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
        <div className="flex items-center mb-4">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Analysis
          </h2>
        </div>

        <div className="text-red-600 dark:text-red-400 mb-4">
          {error}
        </div>

        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <SparklesIcon className="h-5 w-5 text-casablanca-blue mr-2" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Analysis
          </h2>
          {summaryData?.cached && (
            <span className="ml-2 text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
              Cached
            </span>
          )}
        </div>
        <button
          onClick={handleRefresh}
          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          title="Refresh analysis"
        >
          <ArrowPathIcon className="h-4 w-4" />
        </button>
      </div>

      <div className="prose prose-sm max-w-none dark:prose-invert">
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {summary}
        </p>
      </div>

      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <div className="flex items-center justify-between text-xs text-blue-700 dark:text-blue-300">
          <div>
            <strong>AI Generated:</strong> This analysis is powered by GPT and based on the company's latest financial reports and market data.
            For investment decisions, please consult with a financial advisor.
          </div>
          {summaryData && (
            <div className="text-right">
              <div>Tokens: {summaryData.tokens_used}</div>
              <div>Generated: {new Date(summaryData.generated_at).toLocaleDateString()}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 