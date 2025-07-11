import React, { useEffect } from 'react'
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { apiService } from '../services/api'

const MarketsScreen: React.FC = () => {
  const {
    marketData,
    isLoading,
    setMarketData,
    setLoading,
  } = useStore()

  const loadData = async () => {
    setLoading(true)
    try {
      const market = await apiService.getMarketData()
      setMarketData(market)
    } catch (error) {
      console.error('Error loading market data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const onRefresh = () => {
    loadData()
  }

  const formatNumber = (num: number) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`
    return num.toString()
  }

  const sectors = [
    { name: 'Banks', change: '+2.4%', color: '#059669' },
    { name: 'Insurance', change: '+1.8%', color: '#059669' },
    { name: 'Real Estate', change: '+0.9%', color: '#059669' },
    { name: 'Industry', change: '-0.5%', color: '#dc2626' },
    { name: 'Mining', change: '+1.2%', color: '#059669' },
    { name: 'Energy', change: '+0.7%', color: '#059669' },
    { name: 'Transport', change: '-0.3%', color: '#dc2626' },
    { name: 'Services', change: '+1.5%', color: '#059669' },
  ]

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Markets</Text>
          <Text style={styles.headerSubtitle}>
            Real-time Casablanca Stock Exchange data
          </Text>
        </View>

        {/* Market Overview */}
        {marketData.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Market Overview</Text>
            <View style={styles.marketList}>
              {marketData.slice(0, 3).map((item) => (
                <View key={item.symbol} style={styles.marketItem}>
                  <View>
                    <Text style={styles.symbolText}>{item.symbol}</Text>
                    <Text style={styles.nameText}>{item.name}</Text>
                  </View>
                  <View style={styles.priceContainer}>
                    <Text style={styles.priceText}>
                      {item.price.toLocaleString()}
                    </Text>
                    <Text
                      style={[
                        styles.changeText,
                        item.changePercent >= 0 ? styles.positiveChange : styles.negativeChange
                      ]}
                    >
                      {item.changePercent >= 0 ? '+' : ''}
                      {item.changePercent.toFixed(2)}%
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Market Sectors */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Market Sectors</Text>
          <View style={styles.sectorsGrid}>
            {sectors.map((sector, index) => (
              <TouchableOpacity
                key={index}
                style={styles.sectorItem}
              >
                <Text style={styles.sectorName}>{sector.name}</Text>
                <Text style={[styles.sectorChange, { color: sector.color }]}>
                  {sector.change}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Top Movers */}
        {marketData.length > 3 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Top Movers</Text>
            <View style={styles.moversList}>
              {marketData.slice(3).map((item) => (
                <TouchableOpacity
                  key={item.symbol}
                  style={styles.moverItem}
                >
                  <View>
                    <Text style={styles.symbolText}>{item.symbol}</Text>
                    <Text style={styles.nameText}>{item.name}</Text>
                  </View>
                  <View style={styles.priceContainer}>
                    <Text style={styles.priceText}>
                      {item.price.toFixed(2)}
                    </Text>
                    <Text
                      style={[
                        styles.changeText,
                        item.changePercent >= 0 ? styles.positiveChange : styles.negativeChange
                      ]}
                    >
                      {item.changePercent >= 0 ? '+' : ''}
                      {item.changePercent.toFixed(2)}%
                    </Text>
                    <Text style={styles.volumeText}>
                      Vol: {formatNumber(item.volume)} MAD
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Market Statistics */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Market Statistics</Text>
          <View style={styles.statsList}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Total Market Cap</Text>
              <Text style={styles.statValue}>MAD 650.2B</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Daily Volume</Text>
              <Text style={styles.statValue}>MAD 245.8M</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Active Stocks</Text>
              <Text style={styles.statValue}>78</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Advancers</Text>
              <Text style={[styles.statValue, styles.positiveChange]}>45</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Decliners</Text>
              <Text style={[styles.statValue, styles.negativeChange]}>23</Text>
            </View>
          </View>
        </View>

        {/* Trading Volume Chart Placeholder */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Trading Volume</Text>
          <View style={styles.chartPlaceholder}>
            <Text style={styles.chartPlaceholderText}>
              Volume chart coming soon
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  card: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    padding: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  marketList: {
    gap: 12,
  },
  marketItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  symbolText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
  },
  nameText: {
    fontSize: 12,
    color: '#6b7280',
  },
  priceContainer: {
    alignItems: 'flex-end',
  },
  priceText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
  },
  changeText: {
    fontSize: 14,
    fontWeight: '500',
  },
  positiveChange: {
    color: '#059669',
  },
  negativeChange: {
    color: '#dc2626',
  },
  volumeText: {
    fontSize: 12,
    color: '#6b7280',
  },
  sectorsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  sectorItem: {
    width: '48%',
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  sectorName: {
    fontSize: 12,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 4,
  },
  sectorChange: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  moversList: {
    gap: 8,
  },
  moverItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 8,
    borderRadius: 4,
    backgroundColor: '#f9fafb',
  },
  statsList: {
    gap: 12,
  },
  statItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  chartPlaceholder: {
    height: 200,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chartPlaceholderText: {
    fontSize: 14,
    color: '#6b7280',
  },
})

export default MarketsScreen 