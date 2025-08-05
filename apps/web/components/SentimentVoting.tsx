import React, { useState } from 'react'
import { ArrowUpIcon, ArrowRightIcon, ArrowDownIcon } from '@heroicons/react/24/outline'
// import { SentimentVoting as SharedSentimentVoting } from '@morningmaghreb/shared'
import { apiService } from '@/lib/api'
import toast from 'react-hot-toast'

interface SentimentVotingProps {
  ticker: string
  companyName?: string
  onVoteChange?: (sentiment: string) => void
}

const SentimentVoting: React.FC<SentimentVotingProps> = (props) => {
  // Temporary implementation without shared package
  const [userVote, setUserVote] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [sentimentData, setSentimentData] = useState<any>(null)

  const handleVote = async (sentiment: string) => {
    try {
      setLoading(true)
      await apiService.voteSentiment({
        ticker: props.ticker,
        sentiment: sentiment as 'bullish' | 'neutral' | 'bearish',
        confidence: 3,
      })
      setUserVote(sentiment)
      toast.success('Vote recorded successfully!')
    } catch (error) {
      toast.error('Failed to record vote')
    } finally {
      setLoading(false)
    }
  }

  const renderButton = ({
    sentiment,
    label,
    isSelected,
    isLoading,
    onPress
  }: {
    sentiment: string
    label: string
    icon: React.ReactNode
    isSelected: boolean
    isLoading: boolean
    onPress: () => void
  }) => {
    const getSentimentColor = (sentiment: string) => {
      switch (sentiment) {
        case 'bullish':
          return 'text-green-600 bg-green-50 border-green-200'
        case 'neutral':
          return 'text-gray-600 bg-gray-50 border-gray-200'
        case 'bearish':
          return 'text-red-600 bg-red-50 border-red-200'
        default:
          return 'text-gray-600 bg-gray-50 border-gray-200'
      }
    }

    const getSentimentIcon = (sentiment: string) => {
      switch (sentiment) {
        case 'bullish':
          return <ArrowUpIcon className="h-4 w-4" />
        case 'neutral':
          return <ArrowRightIcon className="h-4 w-4" />
        case 'bearish':
          return <ArrowDownIcon className="h-4 w-4" />
        default:
          return <ArrowRightIcon className="h-4 w-4" />
      }
    }

    return (
      <button
        onClick={onPress}
        disabled={isLoading}
        className={`
          flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
          ${isSelected 
            ? getSentimentColor(sentiment) + ' ring-2 ring-offset-2 ring-blue-500'
            : 'border-gray-200 hover:border-gray-300 bg-white dark:bg-dark-hover dark:border-gray-600 dark:hover:border-gray-500'
          }
          ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}
        `}
      >
        <div className={`mb-2 ${isSelected ? 'text-current' : 'text-gray-400'}`}>
          {getSentimentIcon(sentiment)}
        </div>
        <span className={`text-sm font-medium ${isSelected ? 'text-current' : 'text-gray-700 dark:text-gray-300'}`}>
          {label}
        </span>
        {isLoading && isSelected && (
          <div className="mt-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
          </div>
        )}
      </button>
    )
  }

  const renderResults = ({ sentimentData }: { sentimentData: any }) => (
    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
        Community Results
      </h4>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <ArrowUpIcon className="h-4 w-4 text-green-600 mr-2" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Bullish</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {sentimentData.bullish_count} ({sentimentData.bullish_percentage.toFixed(1)}%)
            </div>
            <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: `${sentimentData.bullish_percentage}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <ArrowRightIcon className="h-4 w-4 text-gray-600 mr-2" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Neutral</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {sentimentData.neutral_count} ({sentimentData.neutral_percentage.toFixed(1)}%)
            </div>
            <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
              <div 
                className="bg-gray-600 h-2 rounded-full" 
                style={{ width: `${sentimentData.neutral_percentage}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <ArrowDownIcon className="h-4 w-4 text-red-600 mr-2" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Bearish</span>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {sentimentData.bearish_count} ({sentimentData.bearish_percentage.toFixed(1)}%)
            </div>
            <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
              <div 
                className="bg-red-600 h-2 rounded-full" 
                style={{ width: `${sentimentData.bearish_percentage}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
          <span className="text-sm text-gray-600 dark:text-gray-400">Total Votes</span>
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            {sentimentData.total_votes}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">Avg Confidence</span>
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            {sentimentData.average_confidence.toFixed(1)}/5
          </span>
        </div>
      </div>
    </div>
  )

  const renderLoading = () => (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow p-6">
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  )

  const renderError = (error: string) => {
    toast.error(error)
    return (
      <div className="bg-white dark:bg-dark-card rounded-lg shadow p-6">
        <div className="text-red-600 text-center">
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Community Sentiment
      </h3>
      {props.companyName && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {props.companyName} ({props.ticker})
        </p>
      )}
      
      {/* Voting Buttons */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { sentiment: 'bullish', label: 'Bullish' },
          { sentiment: 'neutral', label: 'Neutral' },
          { sentiment: 'bearish', label: 'Bearish' }
        ].map(({ sentiment, label }) => 
          renderButton({
            sentiment,
            label,
            icon: null,
            isSelected: userVote === sentiment,
            isLoading: loading,
            onPress: () => handleVote(sentiment)
          })
        )}
      </div>

      {/* Simple Results */}
      <div className="text-center text-sm text-gray-600 dark:text-gray-400">
        Vote to see community sentiment
      </div>
    </div>
  )
}

export default SentimentVoting 