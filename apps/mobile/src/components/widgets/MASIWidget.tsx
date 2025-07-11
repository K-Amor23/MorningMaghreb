import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import { apiService } from '../../services/api'

interface MASIData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
}

interface MASIWidgetProps {
  size?: 'small' | 'medium' | 'large'
  refreshInterval?: number // in minutes
  onPress?: () => void
}

const MASIWidget: React.FC<MASIWidgetProps> = ({
  size = 'medium',
  refreshInterval = 15,
  onPress
}) => {
  const [masiData, setMasiData] = useState<MASIData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const loadMASIData = async () => {
    try {
      setIsLoading(true)
      const marketData = await apiService.getMarketData()
      const masi = marketData.find(item => item.symbol === 'MASI')
      if (masi) {
        setMasiData(masi)
        setLastUpdated(new Date())
      }
    } catch (error) {
      console.error('Error loading MASI data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadMASIData()
    
    // Set up refresh interval
    const interval = setInterval(loadMASIData, refreshInterval * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [refreshInterval])

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

  if (isLoading && !masiData) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.loadingContainer}>
          <Text style={[styles.loadingText, getTextStyle()]}>Loading...</Text>
        </View>
      </TouchableOpacity>
    )
  }

  if (!masiData) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.errorContainer}>
          <Text style={[styles.errorText, getTextStyle()]}>No Data</Text>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
      <View style={styles.header}>
        <Text style={[styles.title, getTextStyle()]}>MASI Index</Text>
        <Text style={[styles.time, getTextStyle()]}>{formatTime(lastUpdated)}</Text>
      </View>
      
      <View style={styles.mainContent}>
        <Text style={[styles.price, getTextStyle()]}>
          {formatNumber(masiData.price)}
        </Text>
        <View style={styles.changeContainer}>
          <Text
            style={[
              styles.change,
              getTextStyle(),
              masiData.changePercent >= 0 ? styles.positive : styles.negative
            ]}
          >
            {masiData.changePercent >= 0 ? '+' : ''}
            {masiData.changePercent.toFixed(2)}%
          </Text>
          <Text style={[styles.changeAmount, getTextStyle()]}>
            {masiData.change >= 0 ? '+' : ''}
            {formatNumber(masiData.change)}
          </Text>
        </View>
      </View>
      
      {size === 'large' && (
        <View style={styles.footer}>
          <Text style={[styles.volume, getTextStyle()]}>
            Vol: {(masiData.volume / 1e6).toFixed(1)}M MAD
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
    width: 120,
    height: 80,
  },
  medium: {
    width: 160,
    height: 120,
  },
  large: {
    width: 200,
    height: 160,
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: '#ff6b6b',
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
  mainContent: {
    flex: 1,
    justifyContent: 'center',
  },
  price: {
    color: '#fff',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  changeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  change: {
    fontWeight: '600',
  },
  positive: {
    color: '#4ade80',
  },
  negative: {
    color: '#f87171',
  },
  changeAmount: {
    color: '#888',
  },
  footer: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  volume: {
    color: '#888',
    textAlign: 'center',
  },
})

export default MASIWidget 