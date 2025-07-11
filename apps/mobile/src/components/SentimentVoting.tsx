import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native'
import { apiService } from '../services/api'

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
      const data = await apiService.getSentimentAggregate(ticker)
      setSentimentData(data)
    } catch (error) {
      console.error('Error loading sentiment data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadUserVote = async () => {
    try {
      const votes = await apiService.getMySentimentVotes()
      const userVoteForTicker = votes.find(vote => vote.ticker === ticker)
      setUserVote(userVoteForTicker?.sentiment || null)
    } catch (error) {
      console.error('Error loading user vote:', error)
    }
  }

  const handleVote = async (sentiment: string) => {
    try {
      setVoting(true)
      await apiService.voteSentiment({
        ticker,
        sentiment,
        confidence: 3, // Default confidence
      })
      
      setUserVote(sentiment)
      await loadSentimentData() // Refresh aggregate data
      
      if (onVoteChange) {
        onVoteChange(sentiment)
      }
      
      Alert.alert('Vote Recorded', `Your ${sentiment} vote for ${ticker} has been recorded!`)
    } catch (error) {
      console.error('Error voting:', error)
      Alert.alert('Error', 'Failed to record your vote. Please try again.')
    } finally {
      setVoting(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish':
        return '#10b981' // Green
      case 'neutral':
        return '#6b7280' // Gray
      case 'bearish':
        return '#ef4444' // Red
      default:
        return '#6b7280'
    }
  }

  const getSentimentEmoji = (sentiment: string) => {
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
    return (
      <View style={styles.container}>
        <ActivityIndicator size="small" color="#1e3a8a" />
        <Text style={styles.loadingText}>Loading sentiment data...</Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Community Sentiment</Text>
      {companyName && <Text style={styles.subtitle}>{companyName} ({ticker})</Text>}
      
      {/* Voting Buttons */}
      <View style={styles.votingButtons}>
        {['bullish', 'neutral', 'bearish'].map((sentiment) => (
          <TouchableOpacity
            key={sentiment}
            style={[
              styles.voteButton,
              userVote === sentiment && styles.selectedVoteButton,
              { borderColor: getSentimentColor(sentiment) }
            ]}
            onPress={() => handleVote(sentiment)}
            disabled={voting}
          >
            <Text style={styles.voteEmoji}>{getSentimentEmoji(sentiment)}</Text>
            <Text style={[
              styles.voteText,
              { color: getSentimentColor(sentiment) },
              userVote === sentiment && styles.selectedVoteText
            ]}>
              {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
            </Text>
            {voting && userVote === sentiment && (
              <ActivityIndicator size="small" color={getSentimentColor(sentiment)} />
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Sentiment Results */}
      {sentimentData && sentimentData.total_votes > 0 && (
        <View style={styles.resultsContainer}>
          <Text style={styles.resultsTitle}>Community Results</Text>
          
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>📈 Bullish</Text>
            <Text style={styles.resultValue}>
              {sentimentData.bullish_count} ({sentimentData.bullish_percentage.toFixed(1)}%)
            </Text>
          </View>
          
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>➡️ Neutral</Text>
            <Text style={styles.resultValue}>
              {sentimentData.neutral_count} ({sentimentData.neutral_percentage.toFixed(1)}%)
            </Text>
          </View>
          
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>📉 Bearish</Text>
            <Text style={styles.resultValue}>
              {sentimentData.bearish_count} ({sentimentData.bearish_percentage.toFixed(1)}%)
            </Text>
          </View>
          
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Total Votes</Text>
            <Text style={styles.resultValue}>{sentimentData.total_votes}</Text>
          </View>
          
          <View style={styles.resultRow}>
            <Text style={styles.resultLabel}>Avg Confidence</Text>
            <Text style={styles.resultValue}>
              {sentimentData.average_confidence.toFixed(1)}/5
            </Text>
          </View>
        </View>
      )}

      {sentimentData && sentimentData.total_votes === 0 && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No votes yet</Text>
          <Text style={styles.emptySubtext}>Be the first to vote!</Text>
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 16,
  },
  votingButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  voteButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 2,
    borderRadius: 8,
    marginHorizontal: 4,
    backgroundColor: 'white',
  },
  selectedVoteButton: {
    backgroundColor: '#f3f4f6',
  },
  voteEmoji: {
    fontSize: 16,
    marginRight: 4,
  },
  voteText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  selectedVoteText: {
    fontWeight: 'bold',
  },
  resultsContainer: {
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 16,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
  },
  resultLabel: {
    fontSize: 14,
    color: '#4b5563',
  },
  resultValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  emptyText: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 4,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
  },
  loadingText: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 8,
    textAlign: 'center',
  },
})

export default SentimentVoting 