import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Switch,
  StyleSheet,
  Alert,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { authService } from '../services/auth'
import { notificationService } from '../services/notifications'
import { offlineStorage } from '../services/offlineStorage'
import { WidgetConfiguration } from '../components/widgets'

const SettingsScreen: React.FC = () => {
  const {
    user,
    isAuthenticated,
    biometricEnabled,
    notifications,
    language,
    isOnline,
    isSyncing,
    setNotifications,
    setLanguage,
    setUser,
    setAuthenticated,
    setBiometricEnabled,
    signOut,
  } = useStore()

  const [isLoading, setIsLoading] = useState(false)
  const [showWidgetConfig, setShowWidgetConfig] = useState(false)
  const [biometricSupported, setBiometricSupported] = useState(false)
  const [storageStats, setStorageStats] = useState({ cachedItems: 0, queuedItems: 0 })

  useEffect(() => {
    checkBiometricSupport()
    loadStorageStats()
  }, [])

  const checkBiometricSupport = async () => {
    try {
      const { hasHardware, isEnrolled } = await authService.checkBiometricSupport()
      setBiometricSupported(hasHardware && isEnrolled)
    } catch (error) {
      console.error('Error checking biometric support:', error)
    }
  }

  const loadStorageStats = async () => {
    try {
      const stats = await offlineStorage.getStorageStats()
      setStorageStats(stats)
    } catch (error) {
      console.error('Error loading storage stats:', error)
    }
  }

  const handleSignOut = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            try {
              await signOut()
            } catch (error) {
              console.error('Error signing out:', error)
            }
          },
        },
      ]
    )
  }

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. Are you sure you want to delete your account?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            // Handle account deletion
            Alert.alert('Account Deleted', 'Your account has been deleted.')
          },
        },
      ]
    )
  }

  const handleBiometricToggle = async () => {
    if (!biometricSupported) {
      Alert.alert('Not Supported', 'Biometric authentication is not available on this device.')
      return
    }

    setIsLoading(true)
    try {
      if (biometricEnabled) {
        const success = await authService.disableBiometric()
        if (success) {
          setBiometricEnabled(false)
          Alert.alert('Success', 'Biometric authentication has been disabled.')
        }
      } else {
        const success = await authService.enableBiometric()
        if (success) {
          setBiometricEnabled(true)
          Alert.alert('Success', 'Biometric authentication has been enabled.')
        }
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update biometric settings')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data. You may need to reload data when you reconnect.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              await offlineStorage.clearAll()
              await loadStorageStats()
              Alert.alert('Success', 'Cache cleared successfully.')
            } catch (error) {
              Alert.alert('Error', 'Failed to clear cache.')
            }
          },
        },
      ]
    )
  }

  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ar', name: 'العربية', flag: '🇲🇦' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
  ]

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Settings</Text>
          <Text style={styles.headerSubtitle}>
            Manage your preferences and account
          </Text>
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <View style={styles.card}>
            {isAuthenticated && user ? (
              <View style={styles.userInfo}>
                <View style={styles.avatar}>
                  <Text style={styles.avatarText}>
                    {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                  </Text>
                </View>
                <View style={styles.userDetails}>
                  <Text style={styles.userName}>
                    {user.name || 'User'}
                  </Text>
                  <Text style={styles.userEmail}>{user.email}</Text>
                  <Text style={styles.userTier}>
                    {user.tier === 'pro' ? 'Pro Plan' : user.tier === 'admin' ? 'Admin' : 'Free Plan'}
                  </Text>
                </View>
              </View>
            ) : (
              <TouchableOpacity style={styles.signInButton}>
                <Text style={styles.signInButtonText}>Sign In</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Security Section */}
        {isAuthenticated && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Security</Text>
            <View style={styles.card}>
              <View style={styles.settingItem}>
                <View style={styles.settingInfo}>
                  <Text style={styles.settingTitle}>
                    {authService.getBiometricType()} Authentication
                  </Text>
                  <Text style={styles.settingDescription}>
                    Use {authService.getBiometricType()} to sign in quickly
                  </Text>
                </View>
                <Switch
                  value={biometricEnabled}
                  onValueChange={handleBiometricToggle}
                  disabled={!biometricSupported || isLoading}
                  trackColor={{ false: '#e5e7eb', true: '#1e3a8a' }}
                  thumbColor={biometricEnabled ? '#ffffff' : '#f3f4f6'}
                />
              </View>
              {!biometricSupported && (
                <Text style={styles.settingNote}>
                  {authService.getBiometricType()} is not available on this device
                </Text>
              )}
            </View>
          </View>
        )}

        {/* Notifications Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          <View style={styles.card}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Push Notifications</Text>
                <Text style={styles.settingDescription}>
                  Receive alerts for market updates and news
                </Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#e5e7eb', true: '#1e3a8a' }}
                thumbColor={notifications ? '#ffffff' : '#f3f4f6'}
              />
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Market Alerts</Text>
                <Text style={styles.settingDescription}>
                  Get notified about significant market movements
                </Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#e5e7eb', true: '#1e3a8a' }}
                thumbColor={notifications ? '#ffffff' : '#f3f4f6'}
              />
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Price Alerts</Text>
                <Text style={styles.settingDescription}>
                  Get notified when stocks reach target prices
                </Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#e5e7eb', true: '#1e3a8a' }}
                thumbColor={notifications ? '#ffffff' : '#f3f4f6'}
              />
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Newsletter</Text>
                <Text style={styles.settingDescription}>
                  Daily Morning Maghreb email digest
                </Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#e5e7eb', true: '#1e3a8a' }}
                thumbColor={notifications ? '#ffffff' : '#f3f4f6'}
              />
            </View>
          </View>
        </View>

        {/* Language Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Language</Text>
          <View style={styles.card}>
            {languages.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.languageItem,
                  language === lang.code && styles.languageItemActive
                ]}
                onPress={() => setLanguage(lang.code as 'en' | 'ar' | 'fr')}
              >
                <View style={styles.languageInfo}>
                  <Text style={styles.languageFlag}>{lang.flag}</Text>
                  <Text style={styles.languageName}>{lang.name}</Text>
                </View>
                {language === lang.code && (
                  <View style={styles.checkmark}>
                    <Text style={styles.checkmarkText}>✓</Text>
                  </View>
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Offline & Sync Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Offline & Sync</Text>
          <View style={styles.card}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Connection Status</Text>
                <Text style={styles.settingDescription}>
                  {isOnline ? 'Online' : 'Offline'}
                </Text>
              </View>
              <View style={[styles.statusIndicator, { backgroundColor: isOnline ? '#10b981' : '#ef4444' }]} />
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Sync Status</Text>
                <Text style={styles.settingDescription}>
                  {isSyncing ? 'Syncing...' : 'Up to date'}
                </Text>
              </View>
              {isSyncing && <Text style={styles.syncIcon}>🔄</Text>}
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Cached Data</Text>
                <Text style={styles.settingDescription}>
                  {storageStats.cachedItems} items cached
                </Text>
              </View>
              <TouchableOpacity onPress={handleClearCache}>
                <Text style={styles.clearButton}>Clear</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Pending Sync</Text>
                <Text style={styles.settingDescription}>
                  {storageStats.queuedItems} items queued
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Widgets Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Home Screen Widgets</Text>
          <View style={styles.card}>
            <TouchableOpacity 
              style={styles.settingItem}
              onPress={() => setShowWidgetConfig(true)}
            >
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Configure Widgets</Text>
                <Text style={styles.settingDescription}>
                  Customize MASI index, watchlist, and macro indicators
                </Text>
              </View>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Account Actions */}
        {isAuthenticated && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Account Actions</Text>
            <View style={styles.card}>
              <TouchableOpacity 
                style={styles.dangerButton}
                onPress={handleSignOut}
              >
                <Text style={styles.dangerButtonText}>Sign Out</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.dangerButton, styles.deleteButton]}
                onPress={handleDeleteAccount}
              >
                <Text style={styles.deleteButtonText}>Delete Account</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* App Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Information</Text>
          <View style={styles.card}>
            <View style={styles.infoItem}>
              <Text style={styles.infoLabel}>Version</Text>
              <Text style={styles.infoValue}>1.0.0</Text>
            </View>
            <View style={styles.infoItem}>
              <Text style={styles.infoLabel}>Build</Text>
              <Text style={styles.infoValue}>2024.1</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Widget Configuration Modal */}
      {showWidgetConfig && (
        <WidgetConfiguration 
          onClose={() => setShowWidgetConfig(false)}
        />
      )}
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
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginHorizontal: 20,
    marginBottom: 8,
  },
  card: {
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#1e3a8a',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  avatarText: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 4,
  },
  userTier: {
    fontSize: 12,
    color: '#1e3a8a',
    fontWeight: '600',
  },
  signInButton: {
    backgroundColor: '#1e3a8a',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  signInButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#64748b',
  },
  settingNote: {
    fontSize: 12,
    color: '#ef4444',
    marginTop: 8,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  syncIcon: {
    fontSize: 16,
  },
  clearButton: {
    color: '#1e3a8a',
    fontSize: 14,
    fontWeight: '600',
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  languageItemActive: {
    backgroundColor: '#f8fafc',
  },
  languageInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  languageFlag: {
    fontSize: 20,
    marginRight: 12,
  },
  languageName: {
    fontSize: 16,
    color: '#1e293b',
  },
  checkmark: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#10b981',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmarkText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  chevron: {
    fontSize: 18,
    color: '#64748b',
  },
  dangerButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 8,
  },
  dangerButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  deleteButton: {
    backgroundColor: '#dc2626',
  },
  deleteButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#64748b',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
  },
})

export default SettingsScreen 