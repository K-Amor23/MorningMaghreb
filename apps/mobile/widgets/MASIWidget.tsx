import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { apiService } from '../services/api'

interface MASIWidgetProps {
  size?: 'small' | 'medium' | 'large'
  showChange?: boolean
  showVolume?: boolean
}

interface MASIData {
  current: number
  change: number
  change_percent: number
  volume: number
  last_updated: string
}

const MASIWidget: React.FC<MASIWidgetProps> = ({
  size = 'medium',
  showChange = true,
  showVolume = false,
}) => {
  const [masiData, setMasiData] = useState<MASIData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMASIData()
    // Refresh every 5 minutes
    const interval = setInterval(loadMASIData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const loadMASIData = async () => {
    try {
      const data = await apiService.getMarketData()
      const masiIndex = data.find(item => item.symbol === 'MASI')
      if (masiIndex) {
        setMasiData({
          current: masiIndex.price,
          change: masiIndex.change_amount || 0,
          change_percent: masiIndex.change_percent || 0,
          volume: masiIndex.volume || 0,
          last_updated: new Date().toISOString(),
        })
      }
    } catch (error) {
      console.error('Error loading MASI data:', error)
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

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`
    return volume.toString()
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

  if (!masiData) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.errorText}>No data</Text>
      </View>
    )
  }

  return (
    <View style={[styles.container, styles[size]]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>MASI</Text>
        <Text style={styles.subtitle}>Morocco All Shares</Text>
      </View>

      {/* Main Value */}
      <View style={styles.mainValue}>
        <Text style={styles.price}>{formatNumber(masiData.current)}</Text>
        <Text style={styles.currency}>MAD</Text>
      </View>

      {/* Change Information */}
      {showChange && (
        <View style={styles.changeContainer}>
          <Text style={styles.changeIcon}>{getChangeIcon(masiData.change)}</Text>
          <Text style={[styles.changeValue, { color: getChangeColor(masiData.change) }]}>
            {masiData.change >= 0 ? '+' : ''}{formatNumber(masiData.change)}
          </Text>
          <Text style={[styles.changePercent, { color: getChangeColor(masiData.change) }]}>
            ({masiData.change_percent >= 0 ? '+' : ''}{masiData.change_percent.toFixed(2)}%)
          </Text>
        </View>
      )}

      {/* Volume */}
      {showVolume && size !== 'small' && (
        <View style={styles.volumeContainer}>
          <Text style={styles.volumeLabel}>Volume:</Text>
          <Text style={styles.volumeValue}>{formatVolume(masiData.volume)}</Text>
        </View>
      )}

      {/* Last Updated */}
      {size === 'large' && (
        <Text style={styles.lastUpdated}>
          Updated: {new Date(masiData.last_updated).toLocaleTimeString()}
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
  header: {
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 10,
    color: '#6b7280',
    marginTop: 2,
  },
  mainValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'center',
    marginBottom: 8,
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  currency: {
    fontSize: 12,
    color: '#6b7280',
    marginLeft: 4,
  },
  changeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  changeIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  changeValue: {
    fontSize: 14,
    fontWeight: '600',
    marginRight: 4,
  },
  changePercent: {
    fontSize: 12,
    fontWeight: '500',
  },
  volumeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 4,
  },
  volumeLabel: {
    fontSize: 10,
    color: '#6b7280',
    marginRight: 4,
  },
  volumeValue: {
    fontSize: 10,
    fontWeight: '600',
    color: '#1f2937',
  },
  lastUpdated: {
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
  errorText: {
    fontSize: 12,
    color: '#ef4444',
    textAlign: 'center',
  },
})

export default MASIWidget 