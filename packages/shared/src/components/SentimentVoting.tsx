import React, { useState, useEffect } from 'react'
import type { SentimentData, SentimentVote } from '../types'
import { BaseApiService } from '../services/api'

export interface SentimentVotingProps {
  ticker: string
  companyName?: string
  onVoteChange?: (sentiment: string) => void
  apiService: BaseApiService
  renderButton: (props: {
    sentiment: string
    label: string
    icon: React.ReactNode
    isSelected: boolean
    isLoading: boolean
    onPress: () => void
  }) => React.ReactNode
  renderResults: (props: {
    sentimentData: SentimentData
  }) => React.ReactNode
  renderLoading: () => React.ReactNode
  renderError?: (error: string) => React.ReactNode
}

export const SentimentVoting: React.FC<SentimentVotingProps> = ({
  ticker,
  companyName,
  onVoteChange,
  apiService,
  renderButton,
  renderResults,
  renderLoading,
  renderError,
}) => {
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null)
  const [userVote, setUserVote] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [voting, setVoting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSentimentData()
    loadUserVote()
  }, [ticker])

  const loadSentimentData = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiService.getSentimentAggregate(ticker)
      setSentimentData(data)
    } catch (err) {
      console.error('Error loading sentiment data:', err)
      setError('Failed to load sentiment data')
    } finally {
      setLoading(false)
    }
  }

  const loadUserVote = async () => {
    try {
      const votes = await apiService.getMySentimentVotes()
      const userVoteForTicker = votes.find((vote: SentimentVote) => vote.ticker === ticker)
      setUserVote(userVoteForTicker?.sentiment || null)
    } catch (err) {
      console.error('Error loading user vote:', err)
      // Don't show error for user vote loading as it's not critical
    }
  }

  const handleVote = async (sentiment: string) => {
    try {
      setVoting(true)
      setError(null)
      
      await apiService.voteSentiment({
        ticker,
        sentiment: sentiment as 'bullish' | 'neutral' | 'bearish',
        confidence: 3, // Default confidence
      })
      
      setUserVote(sentiment)
      await loadSentimentData() // Refresh aggregate data
      
      if (onVoteChange) {
        onVoteChange(sentiment)
      }
    } catch (err) {
      console.error('Error voting:', err)
      setError('Failed to record your vote. Please try again.')
    } finally {
      setVoting(false)
    }
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish':
        return '📈'
      case 'neutral':
        return '➡️'
      case 'bearish':
        return '📉'
      default:
        return '❓'
    }
  }

  if (loading) {
    return renderLoading()
  }

  if (error && renderError) {
    return renderError(error)
  }

  return (
    <div>
      <h3>Community Sentiment</h3>
      {companyName && <p>{companyName} ({ticker})</p>}
      
      {/* Voting Buttons */}
      <div>
        {[
          { sentiment: 'bullish', label: 'Bullish' },
          { sentiment: 'neutral', label: 'Neutral' },
          { sentiment: 'bearish', label: 'Bearish' }
        ].map(({ sentiment, label }) => 
          renderButton({
            sentiment,
            label,
            icon: getSentimentIcon(sentiment),
            isSelected: userVote === sentiment,
            isLoading: voting,
            onPress: () => handleVote(sentiment)
          })
        )}
      </div>

      {/* Sentiment Results */}
      {sentimentData && sentimentData.total_votes > 0 && (
        renderResults({ sentimentData })
      )}
    </div>
  )
} 