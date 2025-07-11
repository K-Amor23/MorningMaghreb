import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import { apiService } from '../../services/api'

interface MacroIndicator {
  indicator: string
  description: string
  value: string
  change: string
  unit: string
}

interface MacroWidgetProps {
  size?: 'small' | 'medium' | 'large'
  maxIndicators?: number
  refreshInterval?: number // in minutes
  onPress?: () => void
}

const MacroWidget: React.FC<MacroWidgetProps> = ({
  size = 'medium',
  maxIndicators = 3,
  refreshInterval = 30,
  onPress
}) => {
  const [macroData, setMacroData] = useState<MacroIndicator[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const loadMacroData = async () => {
    try {
      setIsLoading(true)
      const data = await apiService.getMacroData()
      
      // Transform the data to match our interface
      const transformedData = data.slice(0, maxIndicators).map((item: any) => ({
        indicator: item.indicator,
        description: item.description,
        value: item.value,
        change: item.change,
        unit: item.unit || ''
      }))
      
      setMacroData(transformedData)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error loading macro data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadMacroData()
    
    // Set up refresh interval
    const interval = setInterval(loadMacroData, refreshInterval * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [refreshInterval, maxIndicators])

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

  const getIndicatorIcon = (indicator: string) => {
    const lowerIndicator = indicator.toLowerCase()
    if (lowerIndicator.includes('inflation')) return '📊'
    if (lowerIndicator.includes('rate') || lowerIndicator.includes('interest')) return '🏦'
    if (lowerIndicator.includes('reserve') || lowerIndicator.includes('fx')) return '💱'
    if (lowerIndicator.includes('gdp')) return '📈'
    if (lowerIndicator.includes('unemployment')) return '👥'
    return '📋'
  }

  if (isLoading && macroData.length === 0) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.loadingContainer}>
          <Text style={[styles.loadingText, getTextStyle()]}>Loading...</Text>
        </View>
      </TouchableOpacity>
    )
  }

  if (macroData.length === 0) {
    return (
      <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyText, getTextStyle()]}>No Macro Data</Text>
          <Text style={[styles.emptySubtext, getTextStyle()]}>Check back later</Text>
        </View>
      </TouchableOpacity>
    )
  }

  return (
    <TouchableOpacity style={[styles.container, getWidgetStyle()]} onPress={onPress}>
      <View style={styles.header}>
        <Text style={[styles.title, getTextStyle()]}>Macro Indicators</Text>
        <Text style={[styles.time, getTextStyle()]}>{formatTime(lastUpdated)}</Text>
      </View>
      
      <View style={styles.content}>
        {macroData.map((item, index) => (
          <View key={index} style={styles.indicatorItem}>
            <View style={styles.indicatorHeader}>
              <Text style={[styles.indicatorIcon, getTextStyle()]}>
                {getIndicatorIcon(item.indicator)}
              </Text>
              <View style={styles.indicatorInfo}>
                <Text style={[styles.indicatorName, getTextStyle()]} numberOfLines={1}>
                  {item.indicator}
                </Text>
                {size !== 'small' && (
                  <Text style={[styles.indicatorDescription, getTextStyle()]} numberOfLines={1}>
                    {item.description}
                  </Text>
                )}
              </View>
            </View>
            
            <View style={styles.indicatorValue}>
              <Text style={[styles.value, getTextStyle()]}>
                {item.value}{item.unit}
              </Text>
              <Text
                style={[
                  styles.change,
                  getTextStyle(),
                  item.change.startsWith('+') ? styles.positive : styles.negative
                ]}
              >
                {item.change}
              </Text>
            </View>
          </View>
        ))}
      </View>
      
      {size === 'large' && macroData.length > 0 && (
        <View style={styles.footer}>
          <Text style={[styles.footerText, getTextStyle()]}>
            {macroData.length} indicators • Updated {refreshInterval}min
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
    width: 160,
    height: 120,
  },
  medium: {
    width: 200,
    height: 160,
  },
  large: {
    width: 240,
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
  content: {
    flex: 1,
  },
  indicatorItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  indicatorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 8,
  },
  indicatorIcon: {
    marginRight: 6,
  },
  indicatorInfo: {
    flex: 1,
  },
  indicatorName: {
    color: '#fff',
    fontWeight: '500',
  },
  indicatorDescription: {
    color: '#888',
    marginTop: 2,
  },
  indicatorValue: {
    alignItems: 'flex-end',
  },
  value: {
    color: '#fff',
    fontWeight: '600',
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

export default MacroWidget 