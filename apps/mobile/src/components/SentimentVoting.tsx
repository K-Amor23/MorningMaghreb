import React from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native'
import { SentimentVoting as SharedSentimentVoting } from '@morningmaghreb/shared'
import { webApiService } from '../services/webApi'

interface SentimentVotingProps {
  ticker: string
  companyName?: string
  onVoteChange?: (sentiment: string) => void
}

const SentimentVoting: React.FC<SentimentVotingProps> = (props) => {
  const renderButton = ({
    sentiment,
    label,
    icon,
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

    return (
      <TouchableOpacity
        style={[
          styles.voteButton,
          isSelected && styles.selectedVoteButton,
          { borderColor: getSentimentColor(sentiment) }
        ]}
        onPress={onPress}
        disabled={isLoading}
      >
        <Text style={styles.voteEmoji}>{getSentimentEmoji(sentiment)}</Text>
        <Text style={[
          styles.voteText,
          { color: getSentimentColor(sentiment) },
          isSelected && styles.selectedVoteText
        ]}>
          {label}
        </Text>
        {isLoading && isSelected && (
          <ActivityIndicator size="small" color={getSentimentColor(sentiment)} />
        )}
      </TouchableOpacity>
    )
  }

  const renderResults = ({ sentimentData }: { sentimentData: any }) => (
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
  )

  const renderLoading = () => (
    <View style={styles.container}>
      <ActivityIndicator size="small" color="#1e3a8a" />
      <Text style={styles.loadingText}>Loading sentiment data...</Text>
    </View>
  )

  const renderError = (error: string) => {
    Alert.alert('Error', error)
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <SharedSentimentVoting
        {...props}
        apiService={webApiService}
        renderButton={renderButton}
        renderResults={renderResults}
        renderLoading={renderLoading}
        renderError={renderError}
      />
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
    fontSize: 20,
    marginRight: 8,
  },
  voteText: {
    fontSize: 14,
    fontWeight: '600',
  },
  selectedVoteText: {
    fontWeight: '700',
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
    marginBottom: 8,
  },
  resultLabel: {
    fontSize: 14,
    color: '#6b7280',
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
    marginTop: 8,
    fontSize: 14,
    color: '#6b7280',
  },
  errorText: {
    color: '#ef4444',
    textAlign: 'center',
    fontSize: 14,
  },
})

export default SentimentVoting 