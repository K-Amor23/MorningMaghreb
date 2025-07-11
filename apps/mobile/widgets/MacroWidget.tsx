import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { apiService } from '../services/api'

interface MacroWidgetProps {
  size?: 'small' | 'medium' | 'large'
  showPolicyRate?: boolean
  showInflation?: boolean
  showFXReserves?: boolean
}

interface MacroData {
  policy_rate: number
  inflation_rate: number
  fx_reserves: number
  trade_balance: number
  last_updated: string
}

const MacroWidget: React.FC<MacroWidgetProps> = ({
  size = 'medium',
  showPolicyRate = true,
  showInflation = true,
  showFXReserves = true,
}) => {
  const [macroData, setMacroData] = useState<MacroData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMacroData()
    // Refresh every 30 minutes (macro data changes less frequently)
    const interval = setInterval(loadMacroData, 30 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const loadMacroData = async () => {
    try {
      setLoading(true)
      const data = await apiService.getMacroData()
      
      // Find specific macro indicators
      const policyRate = data.find((item: any) => item.indicator === 'policy_rate')
      const inflation = data.find((item: any) => item.indicator === 'inflation_rate')
      const fxReserves = data.find((item: any) => item.indicator === 'fx_reserves')
      const tradeBalance = data.find((item: any) => item.indicator === 'trade_balance')
      
      setMacroData({
        policy_rate: policyRate?.value || 0,
        inflation_rate: inflation?.value || 0,
        fx_reserves: fxReserves?.value || 0,
        trade_balance: tradeBalance?.value || 0,
        last_updated: new Date().toISOString(),
      })
    } catch (error) {
      console.error('Error loading macro data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  const formatLargeNumber = (num: number) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`
    return num.toString()
  }

  const getIndicatorColor = (indicator: string, value: number) => {
    switch (indicator) {
      case 'inflation':
        return value > 3 ? '#ef4444' : value > 2 ? '#f59e0b' : '#10b981'
      case 'policy_rate':
        return value > 4 ? '#ef4444' : value > 3 ? '#f59e0b' : '#10b981'
      case 'fx_reserves':
        return value > 300 ? '#10b981' : value > 200 ? '#f59e0b' : '#ef4444'
      case 'trade_balance':
        return value > 0 ? '#10b981' : '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const getIndicatorIcon = (indicator: string) => {
    switch (indicator) {
      case 'policy_rate':
        return '🏦'
      case 'inflation':
        return '📊'
      case 'fx_reserves':
        return '💱'
      case 'trade_balance':
        return '📈'
      default:
        return '📋'
    }
  }

  if (loading) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    )
  }

  if (!macroData) {
    return (
      <View style={[styles.container, styles[size]]}>
        <Text style={styles.errorText}>No data</Text>
      </View>
    )
  }

  return (
    <View style={[styles.container, styles[size]]}>
      <Text style={styles.title}>Macro Indicators</Text>
      
      <View style={styles.indicatorsContainer}>
        {showPolicyRate && (
          <View style={styles.indicator}>
            <View style={styles.indicatorHeader}>
              <Text style={styles.indicatorIcon}>{getIndicatorIcon('policy_rate')}</Text>
              <Text style={styles.indicatorLabel}>Policy Rate</Text>
            </View>
            <Text style={[
              styles.indicatorValue,
              { color: getIndicatorColor('policy_rate', macroData.policy_rate) }
            ]}>
              {formatNumber(macroData.policy_rate, 2)}%
            </Text>
          </View>
        )}
        
        {showInflation && (
          <View style={styles.indicator}>
            <View style={styles.indicatorHeader}>
              <Text style={styles.indicatorIcon}>{getIndicatorIcon('inflation')}</Text>
              <Text style={styles.indicatorLabel}>Inflation</Text>
            </View>
            <Text style={[
              styles.indicatorValue,
              { color: getIndicatorColor('inflation', macroData.inflation_rate) }
            ]}>
              {formatNumber(macroData.inflation_rate, 2)}%
            </Text>
          </View>
        )}
        
        {showFXReserves && size !== 'small' && (
          <View style={styles.indicator}>
            <View style={styles.indicatorHeader}>
              <Text style={styles.indicatorIcon}>{getIndicatorIcon('fx_reserves')}</Text>
              <Text style={styles.indicatorLabel}>FX Reserves</Text>
            </View>
            <Text style={[
              styles.indicatorValue,
              { color: getIndicatorColor('fx_reserves', macroData.fx_reserves) }
            ]}>
              {formatLargeNumber(macroData.fx_reserves)} MAD
            </Text>
          </View>
        )}
        
        {size === 'large' && (
          <View style={styles.indicator}>
            <View style={styles.indicatorHeader}>
              <Text style={styles.indicatorIcon}>{getIndicatorIcon('trade_balance')}</Text>
              <Text style={styles.indicatorLabel}>Trade Balance</Text>
            </View>
            <Text style={[
              styles.indicatorValue,
              { color: getIndicatorColor('trade_balance', macroData.trade_balance) }
            ]}>
              {macroData.trade_balance >= 0 ? '+' : ''}{formatLargeNumber(macroData.trade_balance)} MAD
            </Text>
          </View>
        )}
      </View>
      
      {size === 'large' && (
        <Text style={styles.lastUpdated}>
          Updated: {new Date(macroData.last_updated).toLocaleTimeString()}
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
  indicatorsContainer: {
    flex: 1,
    justifyContent: 'space-around',
  },
  indicator: {
    marginBottom: 8,
  },
  indicatorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  indicatorIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  indicatorLabel: {
    fontSize: 10,
    color: '#6b7280',
    fontWeight: '500',
  },
  indicatorValue: {
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 16,
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

export default MacroWidget 