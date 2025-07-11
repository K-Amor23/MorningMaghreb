import React, { useEffect } from 'react'
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  StyleSheet,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { apiService } from '../services/api'

const HomeScreen: React.FC = () => {
  const {
    marketData,
    macroData,
    newsItems,
    isLoading,
    setMarketData,
    setMacroData,
    setNewsItems,
    setLoading,
  } = useStore()

  const loadData = async () => {
    setLoading(true)
    try {
      const [market, macro, news] = await Promise.all([
        apiService.getMarketData(),
        apiService.getMacroData(),
        apiService.getNews(),
      ])
      setMarketData(market)
      setMacroData(macro)
      setNewsItems(news)
    } catch (error) {
      console.error('Error loading data:', error)
      Alert.alert('Error', 'Failed to load market data')
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

  const getCategoryEmoji = (category: string) => {
    switch (category) {
      case 'market': return '📈'
      case 'economic': return '🏦'
      case 'company': return '🏢'
      case 'regulatory': return '📋'
      default: return '📰'
    }
  }

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
          <Text style={styles.headerTitle}>
            Casablanca Insight
          </Text>
          <Text style={styles.headerSubtitle}>
            Morocco Market Research & Analytics
          </Text>
        </View>

        {/* MASI Index Card */}
        {marketData.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              Market Overview
            </Text>
            <View style={styles.marketList}>
              {marketData.slice(0, 2).map((item) => (
                <View key={item.symbol} style={styles.marketItem}>
                  <View>
                    <Text style={styles.symbolText}>
                      {item.symbol}
                    </Text>
                    <Text style={styles.nameText}>
                      {item.name}
                    </Text>
                  </View>
                  <View style={styles.priceContainer}>
                    <Text style={styles.priceText}>
                      {item.price.toLocaleString()}
                    </Text>
                    <View style={styles.changeContainer}>
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
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Top Movers */}
        {marketData.length > 2 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              Top Movers
            </Text>
            <View style={styles.moversList}>
              {marketData.slice(2, 5).map((item) => (
                <TouchableOpacity
                  key={item.symbol}
                  style={styles.moverItem}
                >
                  <View>
                    <Text style={styles.symbolText}>
                      {item.symbol}
                    </Text>
                    <Text style={styles.nameText}>
                      {item.name}
                    </Text>
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
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Macro Indicators */}
        {macroData.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              Macro Indicators
            </Text>
            <View style={styles.macroList}>
              {macroData.map((item, index) => (
                <View key={index} style={styles.macroItem}>
                  <View style={styles.macroInfo}>
                    <Text style={styles.macroTitle}>
                      {item.indicator}
                    </Text>
                    <Text style={styles.macroDescription}>
                      {item.description}
                    </Text>
                  </View>
                  <View style={styles.macroValues}>
                    <Text style={styles.macroValue}>
                      {item.value}
                    </Text>
                    <Text
                      style={[
                        styles.macroChange,
                        item.change.startsWith('+') ? styles.positiveChange : styles.negativeChange
                      ]}
                    >
                      {item.change}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* News Feed */}
        {newsItems.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              Latest News
            </Text>
            <View style={styles.newsList}>
              {newsItems.slice(0, 3).map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.newsItem}
                >
                  <View style={styles.newsContent}>
                    <Text style={styles.newsEmoji}>
                      {getCategoryEmoji(item.category)}
                    </Text>
                    <View style={styles.newsText}>
                      <Text style={styles.newsTitle}>
                        {item.title}
                      </Text>
                      <Text style={styles.newsExcerpt} numberOfLines={2}>
                        {item.excerpt}
                      </Text>
                      <View style={styles.newsMeta}>
                        <View style={styles.newsTags}>
                          <Text style={styles.newsCategory}>
                            {item.category}
                          </Text>
                          <Text style={styles.newsReadTime}>
                            {item.readTime}
                          </Text>
                        </View>
                        <Text style={styles.newsTime}>
                          {item.publishedAt}
                        </Text>
                      </View>
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Newsletter Signup */}
        <View style={styles.newsletterCard}>
          <Text style={styles.newsletterTitle}>
            Stay Informed
          </Text>
          <Text style={styles.newsletterSubtitle}>
            Get the Morning Maghreb in your inbox
          </Text>
          <TouchableOpacity
            style={styles.newsletterButton}
            onPress={() => Alert.alert('Newsletter', 'Newsletter signup coming soon!')}
          >
            <Text style={styles.newsletterButtonText}>
              Sign Up Free
            </Text>
          </TouchableOpacity>
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
    color: '#1e3a8a',
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
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  changeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
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
    marginLeft: 8,
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
  macroList: {
    gap: 12,
  },
  macroItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  macroInfo: {
    flex: 1,
  },
  macroTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
  },
  macroDescription: {
    fontSize: 12,
    color: '#6b7280',
  },
  macroValues: {
    alignItems: 'flex-end',
  },
  macroValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  macroChange: {
    fontSize: 12,
  },
  newsList: {
    gap: 16,
  },
  newsItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
    paddingBottom: 12,
  },
  newsContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  newsEmoji: {
    fontSize: 18,
    marginRight: 8,
  },
  newsText: {
    flex: 1,
  },
  newsTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 4,
  },
  newsExcerpt: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 8,
  },
  newsMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  newsTags: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  newsCategory: {
    fontSize: 12,
    color: '#6b7280',
  },
  newsReadTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  newsTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  newsletterCard: {
    margin: 16,
    backgroundColor: '#1e3a8a',
    borderRadius: 8,
    padding: 16,
  },
  newsletterTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
    marginBottom: 8,
  },
  newsletterSubtitle: {
    fontSize: 14,
    color: '#bfdbfe',
    textAlign: 'center',
    marginBottom: 16,
  },
  newsletterButton: {
    backgroundColor: '#C1272D',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  newsletterButtonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: '500',
  },
})

export default HomeScreen 