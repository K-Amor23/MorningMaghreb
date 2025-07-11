import { SparklesIcon } from '@heroicons/react/24/outline'

interface AiSummaryProps {
  summary: string
}

export default function AiSummary({ summary }: AiSummaryProps) {
  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="flex items-center mb-4">
        <SparklesIcon className="h-5 w-5 text-casablanca-blue mr-2" />
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          AI Analysis
        </h2>
      </div>
      
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {summary}
        </p>
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p className="text-xs text-blue-700 dark:text-blue-300">
          <strong>AI Generated:</strong> This analysis is powered by GPT and based on the company's latest financial reports and market data. 
          For investment decisions, please consult with a financial advisor.
        </p>
      </div>
    </div>
  )
} 