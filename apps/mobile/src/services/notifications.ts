import * as Notifications from 'expo-notifications'
import * as Device from 'expo-device'
import { Platform } from 'react-native'
import { authService } from './auth'

export interface NotificationSettings {
  priceAlerts: boolean
  marketUpdates: boolean
  newsAlerts: boolean
  newsletter: boolean
  soundEnabled: boolean
  vibrationEnabled: boolean
}

export interface PriceAlert {
  id: string
  ticker: string
  targetPrice: number
  condition: 'above' | 'below'
  isActive: boolean
  createdAt: number
}

class NotificationService {
  private isInitialized = false

  async initialize() {
    if (this.isInitialized) return

    try {
      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync()
      let finalStatus = existingStatus

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync()
        finalStatus = status
      }

      if (finalStatus !== 'granted') {
        throw new Error('Permission not granted for notifications')
      }

      // Configure notification handler
      Notifications.setNotificationHandler({
        handleNotification: async () => ({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false,
        }),
      })

      // Get push token
      if (Device.isDevice) {
        const token = await Notifications.getExpoPushTokenAsync({
          projectId: process.env.EXPO_PUBLIC_PROJECT_ID,
        })
        
        // Store token for server registration
        await this.registerPushToken(token.data)
      }

      this.isInitialized = true
    } catch (error) {
      console.error('Failed to initialize notifications:', error)
    }
  }

  private async registerPushToken(token: string) {
    try {
      const user = await authService.getCurrentUser()
      if (!user) return

      // Register token with backend
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/notifications/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify({
          token,
          platform: Platform.OS,
          deviceId: Device.osInternalBuildId,
        }),
      })

      if (!response.ok) {
        console.error('Failed to register push token')
      }
    } catch (error) {
      console.error('Error registering push token:', error)
    }
  }

  private async getAuthToken(): Promise<string | null> {
    try {
      const { supabase } = await import('./supabase')
      const { data: { session } } = await supabase.auth.getSession()
      return session?.access_token || null
    } catch (error) {
      console.error('Error getting auth token:', error)
      return null
    }
  }

  // Schedule local notification
  async scheduleNotification(
    title: string,
    body: string,
    data?: any,
    trigger?: Notifications.NotificationTriggerInput
  ) {
    try {
      await this.initialize()

      const notificationId = await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: trigger || null,
      })

      return notificationId
    } catch (error) {
      console.error('Error scheduling notification:', error)
      return null
    }
  }

  // Send immediate notification
  async sendNotification(title: string, body: string, data?: any) {
    try {
      await this.initialize()

      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: null, // Send immediately
      })
    } catch (error) {
      console.error('Error sending notification:', error)
    }
  }

  // Schedule price alert
  async schedulePriceAlert(alert: PriceAlert) {
    try {
      const title = `Price Alert: ${alert.ticker}`
      const body = `${alert.ticker} is ${alert.condition === 'above' ? 'above' : 'below'} ${alert.targetPrice} MAD`
      
      await this.scheduleNotification(title, body, {
        type: 'price_alert',
        ticker: alert.ticker,
        targetPrice: alert.targetPrice,
        condition: alert.condition,
      })
    } catch (error) {
      console.error('Error scheduling price alert:', error)
    }
  }

  // Cancel scheduled notification
  async cancelNotification(notificationId: string) {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId)
    } catch (error) {
      console.error('Error canceling notification:', error)
    }
  }

  // Cancel all scheduled notifications
  async cancelAllNotifications() {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync()
    } catch (error) {
      console.error('Error canceling all notifications:', error)
    }
  }

  // Get all scheduled notifications
  async getScheduledNotifications() {
    try {
      return await Notifications.getAllScheduledNotificationsAsync()
    } catch (error) {
      console.error('Error getting scheduled notifications:', error)
      return []
    }
  }

  // Set notification settings
  async updateNotificationSettings(settings: Partial<NotificationSettings>) {
    try {
      const currentSettings = await this.getNotificationSettings()
      const updatedSettings = { ...currentSettings, ...settings }
      
      // Store settings locally
      const { AsyncStorage } = await import('@react-native-async-storage/async-storage')
      await AsyncStorage.setItem('notification_settings', JSON.stringify(updatedSettings))
      
      // Update server settings
      await this.updateServerSettings(updatedSettings)
    } catch (error) {
      console.error('Error updating notification settings:', error)
    }
  }

  // Get notification settings
  async getNotificationSettings(): Promise<NotificationSettings> {
    try {
      const { AsyncStorage } = await import('@react-native-async-storage/async-storage')
      const settings = await AsyncStorage.getItem('notification_settings')
      
      if (settings) {
        return JSON.parse(settings)
      }

      // Default settings
      return {
        priceAlerts: true,
        marketUpdates: true,
        newsAlerts: true,
        newsletter: false,
        soundEnabled: true,
        vibrationEnabled: true,
      }
    } catch (error) {
      console.error('Error getting notification settings:', error)
      return {
        priceAlerts: true,
        marketUpdates: true,
        newsAlerts: true,
        newsletter: false,
        soundEnabled: true,
        vibrationEnabled: true,
      }
    }
  }

  private async updateServerSettings(settings: NotificationSettings) {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/notifications/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await this.getAuthToken()}`,
        },
        body: JSON.stringify(settings),
      })

      if (!response.ok) {
        console.error('Failed to update server notification settings')
      }
    } catch (error) {
      console.error('Error updating server settings:', error)
    }
  }

  // Handle notification received while app is in foreground
  setNotificationReceivedListener(callback: (notification: Notifications.Notification) => void) {
    return Notifications.addNotificationReceivedListener(callback)
  }

  // Handle notification response (when user taps notification)
  setNotificationResponseListener(callback: (response: Notifications.NotificationResponse) => void) {
    return Notifications.addNotificationResponseReceivedListener(callback)
  }

  // Check if notifications are enabled
  async areNotificationsEnabled(): Promise<boolean> {
    try {
      const { status } = await Notifications.getPermissionsAsync()
      return status === 'granted'
    } catch (error) {
      console.error('Error checking notification permissions:', error)
      return false
    }
  }

  // Request notification permissions
  async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Notifications.requestPermissionsAsync()
      return status === 'granted'
    } catch (error) {
      console.error('Error requesting notification permissions:', error)
      return false
    }
  }

  // Send market update notification
  async sendMarketUpdate(marketData: any) {
    try {
      const settings = await this.getNotificationSettings()
      if (!settings.marketUpdates) return

      const title = 'Market Update'
      const body = `MASI: ${marketData.masi?.price || 0} MAD (${marketData.masi?.changePercent || 0}%)`
      
      await this.sendNotification(title, body, {
        type: 'market_update',
        data: marketData,
      })
    } catch (error) {
      console.error('Error sending market update:', error)
    }
  }

  // Send news alert
  async sendNewsAlert(newsItem: any) {
    try {
      const settings = await this.getNotificationSettings()
      if (!settings.newsAlerts) return

      const title = 'Breaking News'
      const body = newsItem.title.length > 50 
        ? `${newsItem.title.substring(0, 50)}...`
        : newsItem.title
      
      await this.sendNotification(title, body, {
        type: 'news_alert',
        newsId: newsItem.id,
        category: newsItem.category,
      })
    } catch (error) {
      console.error('Error sending news alert:', error)
    }
  }
}

export const notificationService = new NotificationService() 