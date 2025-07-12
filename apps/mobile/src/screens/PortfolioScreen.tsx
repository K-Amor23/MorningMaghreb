import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { PortfolioHolding, PaperTradingAccount } from '../store/useStore'

const PortfolioScreen: React.FC = () => {
  const {
    user,
    isAuthenticated,
    portfolioHoldings,
    paperTradingAccounts,
    selectedTradingAccount,
    setSelectedTradingAccount,
    isLoading,
    setLoading,
  } = useStore()

  const [activeTab, setActiveTab] = useState<'holdings' | 'trading'>('holdings')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      loadPortfolioData()
    }
  }, [isAuthenticated])

  const loadPortfolioData = async () => {
    setLoading(true)
    try {
      // Load portfolio holdings and trading accounts
      // This would typically fetch from your API
      // For now, we'll use mock data
    } catch (error) {
      console.error('Error loading portfolio data:', error)
      Alert.alert('Error', 'Failed to load portfolio data')
    } finally {
      setLoading(false)
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await loadPortfolioData()
    setRefreshing(false)
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MAD',
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const formatPercent = (percent: number) => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`
  }

  const getColorForChange = (value: number) => {
    return value >= 0 ? '#10b981' : '#ef4444'
  }

  const calculateTotalValue = () => {
    return portfolioHoldings.reduce((sum, holding) => sum + holding.totalValue, 0)
  }

  const calculateTotalPnl = () => {
    return portfolioHoldings.reduce((sum, holding) => sum + holding.unrealizedPnl, 0)
  }

  const calculateTotalPnlPercent = () => {
    const totalValue = calculateTotalValue()
    const totalCost = portfolioHoldings.reduce((sum, holding) => sum + (holding.avgCost * holding.quantity), 0)
    return totalCost > 0 ? ((totalValue - totalCost) / totalCost) * 100 : 0
  }

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.authContainer}>
          <Text style={styles.authTitle}>Sign In Required</Text>
          <Text style={styles.authSubtitle}>
            Please sign in to view your portfolio and trading accounts.
          </Text>
        </View>
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Portfolio</Text>
          <Text style={styles.headerSubtitle}>
            Welcome back, {user?.name || user?.email}
          </Text>
        </View>

        {/* Tab Navigation */}
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'holdings' && styles.activeTab]}
            onPress={() => setActiveTab('holdings')}
          >
            <Text style={[styles.tabText, activeTab === 'holdings' && styles.activeTabText]}>
              Holdings
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'trading' && styles.activeTab]}
            onPress={() => setActiveTab('trading')}
          >
            <Text style={[styles.tabText, activeTab === 'trading' && styles.activeTabText]}>
              Paper Trading
            </Text>
          </TouchableOpacity>
        </View>

        {activeTab === 'holdings' ? (
          /* Holdings Tab */
          <View style={styles.content}>
            {/* Portfolio Summary */}
            <View style={styles.summaryCard}>
              <Text style={styles.summaryTitle}>Portfolio Summary</Text>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Total Value:</Text>
                <Text style={styles.summaryValue}>
                  {formatCurrency(calculateTotalValue())}
                </Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Total P&L:</Text>
                <Text style={[styles.summaryValue, { color: getColorForChange(calculateTotalPnl()) }]}>
                  {formatCurrency(calculateTotalPnl())} ({formatPercent(calculateTotalPnlPercent())})
                </Text>
              </View>
            </View>

            {/* Holdings List */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Your Holdings</Text>
              {portfolioHoldings.length === 0 ? (
                <View style={styles.emptyState}>
                  <Text style={styles.emptyStateIcon}>📊</Text>
                  <Text style={styles.emptyStateTitle}>No Holdings</Text>
                  <Text style={styles.emptyStateSubtitle}>
                    Start building your portfolio by adding your first holding.
                  </Text>
                  <TouchableOpacity style={styles.addButton}>
                    <Text style={styles.addButtonText}>Add Holding</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                portfolioHoldings.map((holding) => (
                  <View key={holding.id} style={styles.holdingCard}>
                    <View style={styles.holdingHeader}>
                      <Text style={styles.holdingTicker}>{holding.ticker}</Text>
                      <Text style={styles.holdingValue}>
                        {formatCurrency(holding.totalValue)}
                      </Text>
                    </View>
                    <View style={styles.holdingDetails}>
                      <View style={styles.holdingRow}>
                        <Text style={styles.holdingLabel}>Quantity:</Text>
                        <Text style={styles.holdingValue}>{holding.quantity}</Text>
                      </View>
                      <View style={styles.holdingRow}>
                        <Text style={styles.holdingLabel}>Avg Cost:</Text>
                        <Text style={styles.holdingValue}>
                          {formatCurrency(holding.avgCost)}
                        </Text>
                      </View>
                      <View style={styles.holdingRow}>
                        <Text style={styles.holdingLabel}>Current Price:</Text>
                        <Text style={styles.holdingValue}>
                          {formatCurrency(holding.currentPrice)}
                        </Text>
                      </View>
                      <View style={styles.holdingRow}>
                        <Text style={styles.holdingLabel}>P&L:</Text>
                        <Text style={[styles.holdingValue, { color: getColorForChange(holding.unrealizedPnl) }]}>
                          {formatCurrency(holding.unrealizedPnl)} ({formatPercent(holding.unrealizedPnlPercent)})
                        </Text>
                      </View>
                    </View>
                  </View>
                ))
              )}
            </View>
          </View>
        ) : (
          /* Trading Tab */
          <View style={styles.content}>
            {/* Account Selector */}
            {paperTradingAccounts.length > 0 && (
              <View style={styles.accountSelector}>
                <Text style={styles.accountSelectorLabel}>Trading Account:</Text>
                <TouchableOpacity style={styles.accountSelectorButton}>
                  <Text style={styles.accountSelectorText}>
                    {selectedTradingAccount?.accountName || 'Select Account'}
                  </Text>
                  <Text style={styles.accountSelectorIcon}>▼</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Trading Account Summary */}
            {selectedTradingAccount && (
              <View style={styles.summaryCard}>
                <Text style={styles.summaryTitle}>Trading Account</Text>
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>Account:</Text>
                  <Text style={styles.summaryValue}>
                    {selectedTradingAccount.accountName}
                  </Text>
                </View>
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>Balance:</Text>
                  <Text style={styles.summaryValue}>
                    {formatCurrency(selectedTradingAccount.currentBalance)}
                  </Text>
                </View>
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>Total P&L:</Text>
                  <Text style={[styles.summaryValue, { color: getColorForChange(selectedTradingAccount.totalPnl) }]}>
                    {formatCurrency(selectedTradingAccount.totalPnl)} ({formatPercent(selectedTradingAccount.totalPnlPercent)})
                  </Text>
                </View>
              </View>
            )}

            {/* Trading Actions */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Trading Actions</Text>
              <View style={styles.actionButtons}>
                <TouchableOpacity style={styles.actionButton}>
                  <Text style={styles.actionButtonIcon}>📈</Text>
                  <Text style={styles.actionButtonText}>Place Order</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionButton}>
                  <Text style={styles.actionButtonIcon}>📊</Text>
                  <Text style={styles.actionButtonText}>View Positions</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionButton}>
                  <Text style={styles.actionButtonIcon}>📋</Text>
                  <Text style={styles.actionButtonText}>Order History</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.actionButton}>
                  <Text style={styles.actionButtonIcon}>📈</Text>
                  <Text style={styles.actionButtonText}>Performance</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Create Account */}
            {paperTradingAccounts.length === 0 && (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateIcon}>💹</Text>
                <Text style={styles.emptyStateTitle}>No Trading Account</Text>
                <Text style={styles.emptyStateSubtitle}>
                  Create a paper trading account to start practicing with virtual money.
                </Text>
                <TouchableOpacity style={styles.addButton}>
                  <Text style={styles.addButtonText}>Create Account</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  authContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  authTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  authSubtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#64748b',
  },
  tabContainer: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginBottom: 20,
    backgroundColor: '#e2e8f0',
    borderRadius: 12,
    padding: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#ffffff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
  },
  activeTabText: {
    color: '#1e3a8a',
  },
  content: {
    padding: 20,
  },
  summaryCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#64748b',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16,
  },
  holdingCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  holdingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  holdingTicker: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  holdingDetails: {
    gap: 8,
  },
  holdingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  holdingLabel: {
    fontSize: 14,
    color: '#64748b',
  },
  holdingValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  emptyStateSubtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    marginBottom: 24,
  },
  addButton: {
    backgroundColor: '#1e3a8a',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  accountSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  accountSelectorLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginRight: 12,
  },
  accountSelectorButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  accountSelectorText: {
    fontSize: 14,
    color: '#1e293b',
    marginRight: 8,
  },
  accountSelectorIcon: {
    fontSize: 12,
    color: '#64748b',
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionButton: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
    minWidth: '45%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionButtonIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
})

export default PortfolioScreen 