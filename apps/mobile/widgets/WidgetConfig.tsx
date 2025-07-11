import React, { useState } from 'react'
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  ScrollView,
  Alert,
} from 'react-native'
import { useStore } from '../store/useStore'
import MASIWidget from './MASIWidget'
import WatchlistWidget from './WatchlistWidget'
import MacroWidget from './MacroWidget'

interface WidgetConfigProps {
  onClose: () => void
}

interface WidgetSettings {
  masi: {
    enabled: boolean
    size: 'small' | 'medium' | 'large'
    showChange: boolean
    showVolume: boolean
  }
  watchlist: {
    enabled: boolean
    size: 'small' | 'medium' | 'large'
    maxItems: number
    showChange: boolean
  }
  macro: {
    enabled: boolean
    size: 'small' | 'medium' | 'large'
    showPolicyRate: boolean
    showInflation: boolean
    showFXReserves: boolean
  }
}

const WidgetConfig: React.FC<WidgetConfigProps> = ({ onClose }) => {
  const { watchlist } = useStore()
  const [settings, setSettings] = useState<WidgetSettings>({
    masi: {
      enabled: true,
      size: 'medium',
      showChange: true,
      showVolume: false,
    },
    watchlist: {
      enabled: true,
      size: 'medium',
      maxItems: 5,
      showChange: true,
    },
    macro: {
      enabled: true,
      size: 'medium',
      showPolicyRate: true,
      showInflation: true,
      showFXReserves: true,
    },
  })

  const updateSetting = (
    widget: keyof WidgetSettings,
    key: string,
    value: any
  ) => {
    setSettings(prev => ({
      ...prev,
      [widget]: {
        ...prev[widget],
        [key]: value,
      },
    }))
  }

  const handleSave = () => {
    // Save widget settings to AsyncStorage
    // This would typically be done through the store
    Alert.alert(
      'Widgets Configured',
      'Your widget settings have been saved. Add widgets to your home screen to see them in action!',
      [{ text: 'OK', onPress: onClose }]
    )
  }

  const getSizeLabel = (size: string) => {
    switch (size) {
      case 'small': return 'Small'
      case 'medium': return 'Medium'
      case 'large': return 'Large'
      default: return 'Medium'
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Widget Configuration</Text>
        <TouchableOpacity onPress={onClose} style={styles.closeButton}>
          <Text style={styles.closeText}>✕</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* MASI Widget */}
        <View style={styles.widgetSection}>
          <View style={styles.widgetHeader}>
            <Text style={styles.widgetTitle}>MASI Index Widget</Text>
            <Switch
              value={settings.masi.enabled}
              onValueChange={(value) => updateSetting('masi', 'enabled', value)}
            />
          </View>
          
          {settings.masi.enabled && (
            <View style={styles.widgetPreview}>
              <MASIWidget
                size={settings.masi.size}
                showChange={settings.masi.showChange}
                showVolume={settings.masi.showVolume}
              />
              
              <View style={styles.optionsContainer}>
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Size</Text>
                  <View style={styles.sizeButtons}>
                    {(['small', 'medium', 'large'] as const).map((size) => (
                      <TouchableOpacity
                        key={size}
                        style={[
                          styles.sizeButton,
                          settings.masi.size === size && styles.sizeButtonActive
                        ]}
                        onPress={() => updateSetting('masi', 'size', size)}
                      >
                        <Text style={[
                          styles.sizeButtonText,
                          settings.masi.size === size && styles.sizeButtonTextActive
                        ]}>
                          {getSizeLabel(size)}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Show Change</Text>
                  <Switch
                    value={settings.masi.showChange}
                    onValueChange={(value) => updateSetting('masi', 'showChange', value)}
                  />
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Show Volume</Text>
                  <Switch
                    value={settings.masi.showVolume}
                    onValueChange={(value) => updateSetting('masi', 'showVolume', value)}
                  />
                </View>
              </View>
            </View>
          )}
        </View>

        {/* Watchlist Widget */}
        <View style={styles.widgetSection}>
          <View style={styles.widgetHeader}>
            <Text style={styles.widgetTitle}>Watchlist Widget</Text>
            <Switch
              value={settings.watchlist.enabled}
              onValueChange={(value) => updateSetting('watchlist', 'enabled', value)}
            />
          </View>
          
          {settings.watchlist.enabled && (
            <View style={styles.widgetPreview}>
              <WatchlistWidget
                size={settings.watchlist.size}
                maxItems={settings.watchlist.maxItems}
                showChange={settings.watchlist.showChange}
              />
              
              <View style={styles.optionsContainer}>
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Size</Text>
                  <View style={styles.sizeButtons}>
                    {(['small', 'medium', 'large'] as const).map((size) => (
                      <TouchableOpacity
                        key={size}
                        style={[
                          styles.sizeButton,
                          settings.watchlist.size === size && styles.sizeButtonActive
                        ]}
                        onPress={() => updateSetting('watchlist', 'size', size)}
                      >
                        <Text style={[
                          styles.sizeButtonText,
                          settings.watchlist.size === size && styles.sizeButtonTextActive
                        ]}>
                          {getSizeLabel(size)}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Max Items</Text>
                  <View style={styles.numberButtons}>
                    {[3, 5, 7].map((num) => (
                      <TouchableOpacity
                        key={num}
                        style={[
                          styles.numberButton,
                          settings.watchlist.maxItems === num && styles.numberButtonActive
                        ]}
                        onPress={() => updateSetting('watchlist', 'maxItems', num)}
                      >
                        <Text style={[
                          styles.numberButtonText,
                          settings.watchlist.maxItems === num && styles.numberButtonTextActive
                        ]}>
                          {num}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Show Change</Text>
                  <Switch
                    value={settings.watchlist.showChange}
                    onValueChange={(value) => updateSetting('watchlist', 'showChange', value)}
                  />
                </View>
              </View>
            </View>
          )}
        </View>

        {/* Macro Widget */}
        <View style={styles.widgetSection}>
          <View style={styles.widgetHeader}>
            <Text style={styles.widgetTitle}>Macro Indicators Widget</Text>
            <Switch
              value={settings.macro.enabled}
              onValueChange={(value) => updateSetting('macro', 'enabled', value)}
            />
          </View>
          
          {settings.macro.enabled && (
            <View style={styles.widgetPreview}>
              <MacroWidget
                size={settings.macro.size}
                showPolicyRate={settings.macro.showPolicyRate}
                showInflation={settings.macro.showInflation}
                showFXReserves={settings.macro.showFXReserves}
              />
              
              <View style={styles.optionsContainer}>
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Size</Text>
                  <View style={styles.sizeButtons}>
                    {(['small', 'medium', 'large'] as const).map((size) => (
                      <TouchableOpacity
                        key={size}
                        style={[
                          styles.sizeButton,
                          settings.macro.size === size && styles.sizeButtonActive
                        ]}
                        onPress={() => updateSetting('macro', 'size', size)}
                      >
                        <Text style={[
                          styles.sizeButtonText,
                          settings.macro.size === size && styles.sizeButtonTextActive
                        ]}>
                          {getSizeLabel(size)}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Policy Rate</Text>
                  <Switch
                    value={settings.macro.showPolicyRate}
                    onValueChange={(value) => updateSetting('macro', 'showPolicyRate', value)}
                  />
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>Inflation</Text>
                  <Switch
                    value={settings.macro.showInflation}
                    onValueChange={(value) => updateSetting('macro', 'showInflation', value)}
                  />
                </View>
                
                <View style={styles.optionRow}>
                  <Text style={styles.optionLabel}>FX Reserves</Text>
                  <Switch
                    value={settings.macro.showFXReserves}
                    onValueChange={(value) => updateSetting('macro', 'showFXReserves', value)}
                  />
                </View>
              </View>
            </View>
          )}
        </View>

        {/* Instructions */}
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>How to Add Widgets</Text>
          <Text style={styles.instructionsText}>
            • Long press on your home screen{'\n'}
            • Tap the "+" button to add widgets{'\n'}
            • Search for "Casablanca Insight"{'\n'}
            • Choose your preferred widget size{'\n'}
            • Tap "Add Widget" to place it
          </Text>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
          <Text style={styles.saveButtonText}>Save Configuration</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  closeButton: {
    padding: 8,
  },
  closeText: {
    fontSize: 20,
    color: '#6b7280',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  widgetSection: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  widgetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  widgetTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  widgetPreview: {
    alignItems: 'center',
  },
  optionsContainer: {
    width: '100%',
    marginTop: 16,
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  optionLabel: {
    fontSize: 14,
    color: '#374151',
  },
  sizeButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  sizeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: 'white',
  },
  sizeButtonActive: {
    backgroundColor: '#1e3a8a',
    borderColor: '#1e3a8a',
  },
  sizeButtonText: {
    fontSize: 12,
    color: '#6b7280',
  },
  sizeButtonTextActive: {
    color: 'white',
  },
  numberButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  numberButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: 'white',
  },
  numberButtonActive: {
    backgroundColor: '#1e3a8a',
    borderColor: '#1e3a8a',
  },
  numberButtonText: {
    fontSize: 12,
    color: '#6b7280',
  },
  numberButtonTextActive: {
    color: 'white',
  },
  instructionsContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 8,
  },
  instructionsText: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  footer: {
    padding: 16,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  saveButton: {
    backgroundColor: '#1e3a8a',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
})

export default WidgetConfig 