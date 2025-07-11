import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet, ScrollView } from 'react-native'
import { useStore } from '../store/useStore'
import { apiService } from '../services/api'

interface WatchlistWidgetProps {
  size?: 'small' | 'medium' | 'large'
  maxItems?: number
  showChange?: boolean
}

interface WatchlistItem {
  ticker: string
  name: string
  price: number
  change_amount: number
  change_percent: number
}

const WatchlistWidget: React.FC<WatchlistWidgetProps> = ({
  size = 'medium',
  maxItems = 5,
  showChange = true,
}) => {
  const { watchlist } = useStore()
  const [watchlistData, setWatchlistData] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (watchlist.length > 0) {
      loadWatchlistData()
    } else {
      setLoading(false)
    }
    // Refresh every 5 minutes
    const interval = setInterval(() => {
      if (watchlist.length > 0) {
        loadWatchlistData()
      }
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [watchlist])

  const loadWatchlistData = async () => {
    try {
      setLoading(true)
      const marketData = await apiService.getMarketData()
      
      const watchlistItems = watchlist
        .map(ticker => {
          const item = marketData.find((data: any) => data.symbol === ticker)
          if (item) {
            return {
              ticker: item.symbol,
              name: item.name || ticker,
              price: item.price,
              change_amount: item.change_amount || 0,
              change_percent: item.change_percent || 0,
            }
          }
          return null
        })
        .filter(Boolean)
        .slice(0, maxItems) as WatchlistItem[]
      
      setWatchlistData(watchlistItems)
    } catch (error) {
      console.error('Error loading watchlist data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  const getChangeColor = (change: number) => {
    return change >= 0 ? '#10b981' : '#ef4444'
  }

  const getChangeIcon = (change: number) => {
    return change >= 0 ? '📈' : '📉'
  }

  if (loading) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    )
  }

  if (watchlist.length === 0) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.title}>Watchlist</Text>
        <Text style={styles.emptyText}>No stocks in watchlist</Text>
      </View>
    )
  }

  if (watchlistData.length === 0) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.title}>Watchlist</Text>
        <Text style={styles.errorText}>No data available</Text>
      </View>
    )
  }

  return (
    <View style={[styles.container, styles[size]]}>
      <Text style={styles.title}>Watchlist</Text>
      
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        nestedScrollEnabled={true}
      >
        {watchlistData.map((item, index) => (
          <View key={item.ticker} style={styles.itemContainer}>
            <View style={styles.itemHeader}>
              <Text style={styles.ticker}>{item.ticker}</Text>
              {showChange && (
                <Text style={styles.changeIcon}>{getChangeIcon(item.change_percent)}</Text>
              )}
            </View>
            
            <Text style={styles.price}>{formatNumber(item.price)} MAD</Text>
            
            {showChange && (
              <View style={styles.changeContainer}>
                <Text style={[styles.changeValue, { color: getChangeColor(item.change_percent) }]}>
                  {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                </Text>
                <Text style={[styles.changeAmount, { color: getChangeColor(item.change_amount) }]}>
                  {item.change_amount >= 0 ? '+' : ''}{formatNumber(item.change_amount)}
                </Text>
              </View>
            )}
            
            {index < watchlistData.length - 1 && <View style={styles.separator} />}
          </View>
        ))}
      </ScrollView>
      
      {size === 'large' && (
        <Text style={styles.footer}>
          {watchlistData.length} of {watchlist.length} stocks
        </Text>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  small: {
    width: 140,
    height: 100,
  },
  medium: {
    width: 180,
    height: 140,
  },
  large: {
    width: 220,
    height: 180,
  },
  title: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  scrollView: {
    flex: 1,
  },
  itemContainer: {
    marginBottom: 8,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  ticker: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1f2937',
  },
  changeIcon: {
    fontSize: 10,
  },
  price: {
    fontSize: 11,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 2,
  },
  changeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  changeValue: {
    fontSize: 10,
    fontWeight: '600',
  },
  changeAmount: {
    fontSize: 9,
    fontWeight: '500',
  },
  separator: {
    height: 1,
    backgroundColor: '#e5e7eb',
    marginTop: 6,
  },
  footer: {
    fontSize: 8,
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 8,
  },
  loadingText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 8,
  },
  errorText: {
    fontSize: 12,
    color: '#ef4444',
    textAlign: 'center',
    marginTop: 8,
  },
})

export default WatchlistWidget 