import React, { useEffect, useState } from 'react'
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { apiService } from '../services/api'

const NewsScreen: React.FC = () => {
  const {
    newsItems,
    isLoading,
    setNewsItems,
    setLoading,
  } = useStore()

  const [selectedCategory, setSelectedCategory] = useState('All')

  const categories = ['All', 'Markets', 'Companies', 'Economy', 'Regulation', 'Technology', 'International']

  const loadData = async () => {
    setLoading(true)
    try {
      const news = await apiService.getNews()
      setNewsItems(news)
    } catch (error) {
      console.error('Error loading news:', error)
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

  const getCategoryEmoji = (category: string) => {
    switch (category) {
      case 'market': return '📈'
      case 'economic': return '🏦'
      case 'company': return '🏢'
      case 'regulatory': return '📋'
      case 'technology': return '💻'
      case 'international': return '🌍'
      default: return '📰'
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'market': return '#3b82f6'
      case 'economic': return '#8b5cf6'
      case 'company': return '#10b981'
      case 'regulatory': return '#f59e0b'
      case 'technology': return '#06b6d4'
      case 'international': return '#ec4899'
      default: return '#6b7280'
    }
  }

  const filteredNews = selectedCategory === 'All' 
    ? newsItems 
    : newsItems.filter(item => item.category === selectedCategory.toLowerCase())

  const trendingTopics = [
    { topic: '#MASI', count: '1.2K' },
    { topic: '#Banking', count: '856' },
    { topic: '#RenewableEnergy', count: '743' },
    { topic: '#Trade', count: '621' },
    { topic: '#DigitalBanking', count: '498' },
    { topic: '#MoroccoEconomy', count: '432' },
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
          <Text style={styles.headerTitle}>News & Insights</Text>
          <Text style={styles.headerSubtitle}>
            Stay informed with the latest market news
          </Text>
        </View>

        {/* Category Filter */}
        <View style={styles.categoryContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {categories.map((category) => (
              <TouchableOpacity
                key={category}
                style={[
                  styles.categoryButton,
                  selectedCategory === category && styles.categoryButtonActive
                ]}
                onPress={() => setSelectedCategory(category)}
              >
                <Text style={[
                  styles.categoryButtonText,
                  selectedCategory === category && styles.categoryButtonTextActive
                ]}>
                  {category}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Featured News */}
        {filteredNews.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Featured Stories</Text>
            <View style={styles.newsList}>
              {filteredNews.slice(0, 2).map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.featuredNewsItem}
                >
                  <View style={styles.newsContent}>
                    <View style={styles.newsHeader}>
                      <View style={[
                        styles.categoryBadge,
                        { backgroundColor: getCategoryColor(item.category) + '20' }
                      ]}>
                        <Text style={[
                          styles.categoryText,
                          { color: getCategoryColor(item.category) }
                        ]}>
                          {item.category}
                        </Text>
                      </View>
                      <Text style={styles.newsTime}>{item.publishedAt}</Text>
                    </View>
                    <Text style={styles.newsTitle}>{item.title}</Text>
                    <Text style={styles.newsExcerpt} numberOfLines={3}>
                      {item.excerpt}
                    </Text>
                    <View style={styles.newsFooter}>
                      <Text style={styles.newsReadTime}>{item.readTime}</Text>
                      <Text style={styles.readMore}>Read more →</Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Latest News */}
        {filteredNews.length > 2 && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Latest News</Text>
            <View style={styles.newsList}>
              {filteredNews.slice(2).map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.newsItem}
                >
                  <View style={styles.newsContent}>
                    <View style={styles.newsHeader}>
                      <View style={[
                        styles.categoryBadge,
                        { backgroundColor: getCategoryColor(item.category) + '20' }
                      ]}>
                        <Text style={[
                          styles.categoryText,
                          { color: getCategoryColor(item.category) }
                        ]}>
                          {item.category}
                        </Text>
                      </View>
                      <Text style={styles.newsTime}>{item.publishedAt}</Text>
                    </View>
                    <Text style={styles.newsTitle}>{item.title}</Text>
                    <Text style={styles.newsExcerpt} numberOfLines={2}>
                      {item.excerpt}
                    </Text>
                    <View style={styles.newsFooter}>
                      <Text style={styles.newsReadTime}>{item.readTime}</Text>
                      <Text style={styles.readMore}>Read more →</Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* AI Insights */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>AI Market Insights</Text>
          <View style={styles.insightsList}>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>Market Sentiment</Text>
              <Text style={styles.insightValue}>Bullish</Text>
              <Text style={styles.insightDescription}>
                Based on recent news and technical indicators
              </Text>
            </View>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>Top Sector</Text>
              <Text style={styles.insightValue}>Banking</Text>
              <Text style={styles.insightDescription}>
                +2.4% today, strong fundamentals
              </Text>
            </View>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>Risk Level</Text>
              <Text style={styles.insightValue}>Low</Text>
              <Text style={styles.insightDescription}>
                Stable market conditions
              </Text>
            </View>
          </View>
        </View>

        {/* Trending Topics */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Trending Topics</Text>
          <View style={styles.topicsList}>
            {trendingTopics.map((topic, index) => (
              <TouchableOpacity
                key={index}
                style={styles.topicItem}
              >
                <Text style={styles.topicText}>{topic.topic}</Text>
                <Text style={styles.topicCount}>{topic.count}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Newsletter Signup */}
        <View style={styles.newsletterCard}>
          <Text style={styles.newsletterTitle}>Morning Maghreb</Text>
          <Text style={styles.newsletterSubtitle}>
            Get daily market insights delivered to your inbox
          </Text>
          <TouchableOpacity
            style={styles.newsletterButton}
            onPress={() => Alert.alert('Newsletter', 'Newsletter signup coming soon!')}
          >
            <Text style={styles.newsletterButtonText}>Subscribe</Text>
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
    color: '#111827',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  categoryContainer: {
    backgroundColor: 'white',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  categoryButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 4,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
  },
  categoryButtonActive: {
    backgroundColor: '#1e3a8a',
  },
  categoryButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
  },
  categoryButtonTextActive: {
    color: 'white',
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
  newsList: {
    gap: 16,
  },
  featuredNewsItem: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 12,
  },
  newsItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
    paddingBottom: 12,
  },
  newsContent: {
    gap: 8,
  },
  newsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '500',
  },
  newsTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  newsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    lineHeight: 22,
  },
  newsExcerpt: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  newsFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  newsReadTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  readMore: {
    fontSize: 12,
    color: '#1e3a8a',
    fontWeight: '500',
  },
  insightsList: {
    gap: 12,
  },
  insightItem: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
  },
  insightLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 4,
  },
  insightValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e3a8a',
    marginBottom: 4,
  },
  insightDescription: {
    fontSize: 12,
    color: '#6b7280',
  },
  topicsList: {
    gap: 8,
  },
  topicItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#f9fafb',
    borderRadius: 4,
  },
  topicText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
  },
  topicCount: {
    fontSize: 12,
    color: '#6b7280',
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
    backgroundColor: 'white',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  newsletterButtonText: {
    color: '#1e3a8a',
    textAlign: 'center',
    fontWeight: '500',
  },
})

export default NewsScreen 