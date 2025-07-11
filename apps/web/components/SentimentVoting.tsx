import React, { useState, useEffect } from 'react'
import { ArrowUpIcon, ArrowRightIcon, ArrowDownIcon } from '@heroicons/react/24/outline'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import toast from 'react-hot-toast'

interface SentimentVotingProps {
  ticker: string
  companyName?: string
  onVoteChange?: (sentiment: string) => void
}

interface SentimentData {
  ticker: string
  bullish_count: number
  neutral_count: number
  bearish_count: number
  total_votes: number
  bullish_percentage: number
  neutral_percentage: number
  bearish_percentage: number
  average_confidence: number
  last_updated: string
}

const SentimentVoting: React.FC<SentimentVotingProps> = ({
  ticker,
  companyName,
  onVoteChange,
}) => {
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null)
  const [userVote, setUserVote] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [voting, setVoting] = useState(false)

  useEffect(() => {
    loadSentimentData()
    loadUserVote()
  }, [ticker])

  const loadSentimentData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/sentiment/aggregate/${ticker}`)
      if (response.ok) {
        const data = await response.json()
        setSentimentData(data)
      }
    } catch (error) {
      console.error('Error loading sentiment data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadUserVote = async () => {
    try {
      if (!isSupabaseConfigured() || !supabase) {
        toast.error('Database connection not configured')
        return
      }
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const response = await fetch('/api/sentiment/my-votes', {
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        }
      })
      
      if (response.ok) {
        const votes = await response.json()
        const userVoteForTicker = votes.find((vote: any) => vote.ticker === ticker)
        setUserVote(userVoteForTicker?.sentiment || null)
      }
    } catch (error) {
      console.error('Error loading user vote:', error)
    }
  }

  const handleVote = async (sentiment: string) => {
    try {
      setVoting(true)
      if (!isSupabaseConfigured() || !supabase) {
        toast.error('Database connection not configured')
        return
      }
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        toast.error('Please sign in to vote')
        return
      }

      const response = await fetch('/api/sentiment/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        },
        body: JSON.stringify({
          ticker,
          sentiment,
          confidence: 3, // Default confidence
        }),
      })

      if (response.ok) {
        setUserVote(sentiment)
        await loadSentimentData() // Refresh aggregate data
        
        if (onVoteChange) {
          onVoteChange(sentiment)
        }
        
        toast.success(`Your ${sentiment} vote for ${ticker} has been recorded!`)
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to record your vote')
      }
    } catch (error) {
      console.error('Error voting:', error)
      toast.error('Failed to record your vote. Please try again.')
    } finally {
      setVoting(false)
    }
  }

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

  if (loading) {
    return (
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
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Community Sentiment
      </h3>
      {companyName && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {companyName} ({ticker})
        </p>
      )}
      
      {/* Voting Buttons */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {[
          { sentiment: 'bullish', label: 'Bullish', icon: getSentimentIcon('bullish') },
          { sentiment: 'neutral', label: 'Neutral', icon: getSentimentIcon('neutral') },
          { sentiment: 'bearish', label: 'Bearish', icon: getSentimentIcon('bearish') }
        ].map(({ sentiment, label, icon }) => (
          <button
            key={sentiment}
            onClick={() => handleVote(sentiment)}
            disabled={voting}
            className={`
              flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
              ${userVote === sentiment 
                ? getSentimentColor(sentiment) + ' ring-2 ring-offset-2 ring-blue-500'
                : 'border-gray-200 hover:border-gray-300 bg-white dark:bg-dark-hover dark:border-gray-600 dark:hover:border-gray-500'
              }
              ${voting ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}
            `}
          >
            <div className={`mb-2 ${userVote === sentiment ? 'text-current' : 'text-gray-400'}`}>
              {icon}
            </div>
            <span className={`text-sm font-medium ${userVote === sentiment ? 'text-current' : 'text-gray-700 dark:text-gray-300'}`}>
              {label}
            </span>
            {voting && userVote === sentiment && (
              <div className="mt-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Sentiment Results */}
      {sentimentData && sentimentData.total_votes > 0 && (
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
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>Total Votes</span>
              <span className="font-medium text-gray-900 dark:text-white">{sentimentData.total_votes}</span>
            </div>
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-1">
              <span>Avg Confidence</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {sentimentData.average_confidence.toFixed(1)}/5
              </span>
            </div>
          </div>
        </div>
      )}

      {sentimentData && sentimentData.total_votes === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <ArrowUpIcon className="h-8 w-8 mx-auto" />
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">No votes yet</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Be the first to vote!</p>
        </div>
      )}
    </div>
  )
}

export default SentimentVoting 