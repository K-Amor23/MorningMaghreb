import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native'
import { apiService } from '../../services/api'

interface WatchlistItem {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

interface WatchlistWidgetProps {
  size?: 'small' | 'medium' | 'large'
  maxItems?: number
  refreshInterval?: number // in minutes
  onPress?: () => void
  onStockPress?: (symbol: string) => void
}

const WatchlistWidget: React.FC<WatchlistWidgetProps> = ({
  size = 'medium',
  maxItems = 3,
  refreshInterval = 15,
  onPress,
  onStockPress
}) => {
  const [watchlistData, setWatchlistData] = useState<WatchlistItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const loadWatchlistData = async () => {
    try {
      setIsLoading(true)
      // Get user's watchlist from API
      const watchlist = await apiService.getWatchlist()
      
      // Get current market data for watchlist items
      const marketData = await apiService.getMarketData()
      
      // Combine watchlist with market data
      const watchlistWithData = watchlist
        .map(item => {
          const marketItem = marketData.find(m => m.symbol === item.symbol)
          if (marketItem) {
            return {
              symbol: item.symbol,
              name: item.name || marketItem.name,
              price: marketItem.price,
              change: marketItem.change,
              changePercent: marketItem.changePercent
            }
          }
          return null
        })
        .filter(Boolean) as WatchlistItem[]
      
      setWatchlistData(watchlistWithData.slice(0, maxItems))
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error loading watchlist data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadWatchlistData()
    
    // Set up refresh interval
    const interval = setInterval(loadWatchlistData, refreshInterval * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [refreshInterval, maxItems])

  const formatNumber = (num: number) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }

  const getWidgetStyle = () => {
    switch (size) {
      case 'small':
        return styles.small
      case 'large':
        return styles.large
      default:
        return styles.medium
    }
  }

  const getTextStyle = () => {
    switch (size) {
      case 'small':
        return styles.smallText
      case 'large':
        return styles.largeText
      default:
        return styles.mediumText
    }
  }

  if (isLoading && watchlistData.length === 0) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.loadingContainer}>
          <Text style={[styles.loadingText, getTextStyle()]}>Loading...</Text>
        </View>
      </TouchableOpacity>
    )
  }

  if (watchlistData.length === 0) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyText, getTextStyle()]}>No Watchlist</Text>
          <Text style={[styles.emptySubtext, getTextStyle()]}>Add stocks to watch</Text>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
      <View style={styles.header}>
        <Text style={[styles.title, getTextStyle()]}>Watchlist</Text>
        <Text style={[styles.time, getTextStyle()]}>{formatTime(lastUpdated)}</Text>
      </View>
      
      <ScrollView 
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        nestedScrollEnabled={true}
      >
        {watchlistData.map((item, index) => (
          <TouchableOpacity
            key={item.symbol}
            style={styles.stockItem}
            onPress={() => onStockPress?.(item.symbol)}
          >
            <View style={styles.stockInfo}>
              <Text style={[styles.symbol, getTextStyle()]} numberOfLines={1}>
                {item.symbol}
              </Text>
              {size !== 'small' && (
                <Text style={[styles.name, getTextStyle()]} numberOfLines={1}>
                  {item.name}
                </Text>
              )}
            </View>
            
            <View style={styles.stockPrice}>
              <Text style={[styles.price, getTextStyle()]}>
                {formatNumber(item.price)}
              </Text>
              <Text
                style={[
                  styles.change,
                  getTextStyle(),
                  item.changePercent >= 0 ? styles.positive : styles.negative
                ]}
              >
                {item.changePercent >= 0 ? '+' : ''}
                {item.changePercent.toFixed(2)}%
              </Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
      
      {size === 'large' && watchlistData.length > 0 && (
        <View style={styles.footer}>
          <Text style={[styles.footerText, getTextStyle()]}>
            {watchlistData.length} stocks • Tap to view all
          </Text>
        </View>
      )}
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#333',
  },
  small: {
    width: 140,
    height: 120,
  },
  medium: {
    width: 180,
    height: 160,
  },
  large: {
    width: 220,
    height: 200,
  },
  smallText: {
    fontSize: 10,
  },
  mediumText: {
    fontSize: 12,
  },
  largeText: {
    fontSize: 14,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#888',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#888',
    marginBottom: 4,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    color: '#fff',
    fontWeight: '600',
  },
  time: {
    color: '#888',
    fontSize: 10,
  },
  scrollView: {
    flex: 1,
  },
  stockItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  stockInfo: {
    flex: 1,
    marginRight: 8,
  },
  symbol: {
    color: '#fff',
    fontWeight: '600',
  },
  name: {
    color: '#888',
    marginTop: 2,
  },
  stockPrice: {
    alignItems: 'flex-end',
  },
  price: {
    color: '#fff',
    fontWeight: '500',
  },
  change: {
    fontWeight: '500',
    marginTop: 2,
  },
  positive: {
    color: '#4ade80',
  },
  negative: {
    color: '#f87171',
  },
  footer: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  footerText: {
    color: '#888',
    textAlign: 'center',
    fontSize: 10,
  },
})

export default WatchlistWidget 