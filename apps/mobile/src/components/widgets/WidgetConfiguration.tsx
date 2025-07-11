import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  Alert,
  Modal
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import AsyncStorage from '@react-native-async-storage/async-storage'

interface WidgetConfig {
  id: string
  name: string
  enabled: boolean
  size: 'small' | 'medium' | 'large'
  refreshInterval: number // in minutes
  maxItems?: number
}

interface WidgetConfigurationProps {
  visible: boolean
  onClose: () => void
  onConfigChange: (configs: WidgetConfig[]) => void
}

const WidgetConfiguration: React.FC<WidgetConfigurationProps> = ({
  visible,
  onClose,
  onConfigChange
}) => {
  const [widgetConfigs, setWidgetConfigs] = useState<WidgetConfig[]>([
    {
      id: 'masi',
      name: 'MASI Index',
      enabled: true,
      size: 'medium',
      refreshInterval: 15
    },
    {
      id: 'watchlist',
      name: 'Watchlist',
      enabled: true,
      size: 'medium',
      refreshInterval: 15,
      maxItems: 3
    },
    {
      id: 'macro',
      name: 'Macro Indicators',
      enabled: true,
      size: 'medium',
      refreshInterval: 30,
      maxItems: 3
    }
  ])

  useEffect(() => {
    loadWidgetConfigs()
  }, [])

  const loadWidgetConfigs = async () => {
    try {
      const savedConfigs = await AsyncStorage.getItem('widgetConfigs')
      if (savedConfigs) {
        const configs = JSON.parse(savedConfigs)
        setWidgetConfigs(configs)
      }
    } catch (error) {
      console.error('Error loading widget configs:', error)
    }
  }

  const saveWidgetConfigs = async (configs: WidgetConfig[]) => {
    try {
      await AsyncStorage.setItem('widgetConfigs', JSON.stringify(configs))
      onConfigChange(configs)
    } catch (error) {
      console.error('Error saving widget configs:', error)
      Alert.alert('Error', 'Failed to save widget configuration')
    }
  }

  const toggleWidget = (widgetId: string) => {
    const updatedConfigs = widgetConfigs.map(config =>
      config.id === widgetId
        ? { ...config, enabled: !config.enabled }
        : config
    )
    setWidgetConfigs(updatedConfigs)
    saveWidgetConfigs(updatedConfigs)
  }

  const changeWidgetSize = (widgetId: string, size: 'small' | 'medium' | 'large') => {
    const updatedConfigs = widgetConfigs.map(config =>
      config.id === widgetId
        ? { ...config, size }
        : config
    )
    setWidgetConfigs(updatedConfigs)
    saveWidgetConfigs(updatedConfigs)
  }

  const changeRefreshInterval = (widgetId: string, interval: number) => {
    const updatedConfigs = widgetConfigs.map(config =>
      config.id === widgetId
        ? { ...config, refreshInterval: interval }
        : config
    )
    setWidgetConfigs(updatedConfigs)
    saveWidgetConfigs(updatedConfigs)
  }

  const changeMaxItems = (widgetId: string, maxItems: number) => {
    const updatedConfigs = widgetConfigs.map(config =>
      config.id === widgetId
        ? { ...config, maxItems }
        : config
    )
    setWidgetConfigs(updatedConfigs)
    saveWidgetConfigs(updatedConfigs)
  }

  const getSizeLabel = (size: string) => {
    switch (size) {
      case 'small': return 'Small'
      case 'medium': return 'Medium'
      case 'large': return 'Large'
      default: return 'Medium'
    }
  }

  const getIntervalLabel = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`
    const hours = minutes / 60
    return `${hours}h`
  }

  const getWidgetIcon = (widgetId: string) => {
    switch (widgetId) {
      case 'masi': return '📈'
      case 'watchlist': return '👀'
      case 'macro': return '📊'
      default: return '📱'
    }
  }

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Widget Configuration</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>Done</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content}>
          <Text style={styles.sectionTitle}>Available Widgets</Text>
          
          {widgetConfigs.map((config) => (
            <View key={config.id} style={styles.widgetCard}>
              <View style={styles.widgetHeader}>
                <View style={styles.widgetInfo}>
                  <Text style={styles.widgetIcon}>{getWidgetIcon(config.id)}</Text>
                  <View>
                    <Text style={styles.widgetName}>{config.name}</Text>
                    <Text style={styles.widgetDescription}>
                      {config.id === 'masi' && 'Real-time MASI index updates'}
                      {config.id === 'watchlist' && 'Your watchlist stocks'}
                      {config.id === 'macro' && 'Key economic indicators'}
                    </Text>
                  </View>
                </View>
                <Switch
                  value={config.enabled}
                  onValueChange={() => toggleWidget(config.id)}
                  trackColor={{ false: '#333', true: '#4ade80' }}
                  thumbColor={config.enabled ? '#fff' : '#888'}
                />
              </View>

              {config.enabled && (
                <View style={styles.widgetSettings}>
                  {/* Size Selection */}
                  <View style={styles.settingGroup}>
                    <Text style={styles.settingLabel}>Size</Text>
                    <View style={styles.sizeButtons}>
                      {(['small', 'medium', 'large'] as const).map((size) => (
                        <TouchableOpacity
                          key={size}
                          style={[
                            styles.sizeButton,
                            config.size === size && styles.sizeButtonActive
                          ]}
                          onPress={() => changeWidgetSize(config.id, size)}
                        >
                          <Text style={[
                            styles.sizeButtonText,
                            config.size === size && styles.sizeButtonTextActive
                          ]}>
                            {getSizeLabel(size)}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>

                  {/* Refresh Interval */}
                  <View style={styles.settingGroup}>
                    <Text style={styles.settingLabel}>Refresh Interval</Text>
                    <View style={styles.intervalButtons}>
                      {[5, 15, 30, 60].map((interval) => (
                        <TouchableOpacity
                          key={interval}
                          style={[
                            styles.intervalButton,
                            config.refreshInterval === interval && styles.intervalButtonActive
                          ]}
                          onPress={() => changeRefreshInterval(config.id, interval)}
                        >
                          <Text style={[
                            styles.intervalButtonText,
                            config.refreshInterval === interval && styles.intervalButtonTextActive
                          ]}>
                            {getIntervalLabel(interval)}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>

                  {/* Max Items (for watchlist and macro) */}
                  {(config.id === 'watchlist' || config.id === 'macro') && (
                    <View style={styles.settingGroup}>
                      <Text style={styles.settingLabel}>Max Items</Text>
                      <View style={styles.maxItemsButtons}>
                        {[2, 3, 4, 5].map((maxItems) => (
                          <TouchableOpacity
                            key={maxItems}
                            style={[
                              styles.maxItemsButton,
                              config.maxItems === maxItems && styles.maxItemsButtonActive
                            ]}
                            onPress={() => changeMaxItems(config.id, maxItems)}
                          >
                            <Text style={[
                              styles.maxItemsButtonText,
                              config.maxItems === maxItems && styles.maxItemsButtonTextActive
                            ]}>
                              {maxItems}
                            </Text>
                          </TouchableOpacity>
                        ))}
                      </View>
                    </View>
                  )}
                </View>
              )}
            </View>
          ))}

          <View style={styles.helpSection}>
            <Text style={styles.helpTitle}>How to Add Widgets</Text>
            <Text style={styles.helpText}>
              1. Long press on your home screen{'\n'}
              2. Tap the "+" button to add widgets{'\n'}
              3. Search for "Casablanca Insight"{'\n'}
              4. Choose your preferred widget size{'\n'}
              5. Configure the widget settings here
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  closeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  closeButtonText: {
    color: '#4ade80',
    fontSize: 16,
    fontWeight: '500',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 16,
  },
  widgetCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  widgetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  widgetInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  widgetIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  widgetName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  widgetDescription: {
    fontSize: 14,
    color: '#888',
    marginTop: 2,
  },
  widgetSettings: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  settingGroup: {
    marginBottom: 16,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#fff',
    marginBottom: 8,
  },
  sizeButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  sizeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  sizeButtonActive: {
    backgroundColor: '#4ade80',
    borderColor: '#4ade80',
  },
  sizeButtonText: {
    fontSize: 12,
    color: '#888',
  },
  sizeButtonTextActive: {
    color: '#000',
    fontWeight: '600',
  },
  intervalButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  intervalButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  intervalButtonActive: {
    backgroundColor: '#4ade80',
    borderColor: '#4ade80',
  },
  intervalButtonText: {
    fontSize: 12,
    color: '#888',
  },
  intervalButtonTextActive: {
    color: '#000',
    fontWeight: '600',
  },
  maxItemsButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  maxItemsButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center',
  },
  maxItemsButtonActive: {
    backgroundColor: '#4ade80',
    borderColor: '#4ade80',
  },
  maxItemsButtonText: {
    fontSize: 12,
    color: '#888',
  },
  maxItemsButtonTextActive: {
    color: '#000',
    fontWeight: '600',
  },
  helpSection: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#333',
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 8,
  },
  helpText: {
    fontSize: 14,
    color: '#888',
    lineHeight: 20,
  },
})

export default WidgetConfiguration 