import * as SQLite from 'expo-sqlite'
import * as Network from 'expo-network'
import AsyncStorage from '@react-native-async-storage/async-storage'

export interface CachedData {
  id: string
  type: 'market' | 'macro' | 'news' | 'portfolio' | 'watchlist'
  data: any
  timestamp: number
  expiresAt: number
}

export interface SyncQueue {
  id: string
  action: 'create' | 'update' | 'delete'
  endpoint: string
  data: any
  timestamp: number
  retryCount: number
}

class OfflineStorageService {
  private db: SQLite.SQLiteDatabase | null = null
  private isInitialized = false

  async initialize() {
    if (this.isInitialized) return

    try {
      this.db = await SQLite.openDatabaseAsync('casablanca_insight.db')
      
      // Create tables
      await this.createTables()
      this.isInitialized = true
    } catch (error) {
      console.error('Failed to initialize offline storage:', error)
    }
  }

  private async createTables() {
    if (!this.db) return

    // Cached data table
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS cached_data (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
      )
    `)

    // Sync queue table
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS sync_queue (
        id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        data TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        retry_count INTEGER DEFAULT 0
      )
    `)

    // User preferences table
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS user_preferences (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at INTEGER NOT NULL
      )
    `)

    // Create indexes
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_cached_data_type ON cached_data (type)
    `)
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_cached_data_expires ON cached_data (expires_at)
    `)
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_sync_queue_timestamp ON sync_queue (timestamp)
    `)
  }

  // Cache data with expiration
  async cacheData(type: CachedData['type'], id: string, data: any, ttlMinutes: number = 60) {
    if (!this.db) await this.initialize()

    try {
      const timestamp = Date.now()
      const expiresAt = timestamp + (ttlMinutes * 60 * 1000)

      await this.db!.runAsync(
        `INSERT OR REPLACE INTO cached_data (id, type, data, timestamp, expires_at) VALUES (?, ?, ?, ?, ?)`,
        [id, type, JSON.stringify(data), timestamp, expiresAt]
      )
    } catch (error) {
      console.error('Error caching data:', error)
    }
  }

  // Get cached data if not expired
  async getCachedData(type: CachedData['type'], id: string): Promise<any | null> {
    if (!this.db) await this.initialize()

    try {
      const result = await this.db!.getFirstAsync<CachedData>(
        `SELECT * FROM cached_data WHERE type = ? AND id = ? AND expires_at > ?`,
        [type, id, Date.now()]
      )

      if (result) {
        return JSON.parse(result.data)
      }

      return null
    } catch (error) {
      console.error('Error getting cached data:', error)
      return null
    }
  }

  // Get all cached data of a specific type
  async getAllCachedData(type: CachedData['type']): Promise<any[]> {
    if (!this.db) await this.initialize()

    try {
      const results = await this.db!.getAllAsync<CachedData>(
        `SELECT * FROM cached_data WHERE type = ? AND expires_at > ? ORDER BY timestamp DESC`,
        [type, Date.now()]
      )

      return results.map(row => JSON.parse(row.data))
    } catch (error) {
      console.error('Error getting all cached data:', error)
      return []
    }
  }

  // Clear expired cache
  async clearExpiredCache() {
    if (!this.db) await this.initialize()

    try {
      await this.db!.runAsync(
        `DELETE FROM cached_data WHERE expires_at <= ?`,
        [Date.now()]
      )
    } catch (error) {
      console.error('Error clearing expired cache:', error)
    }
  }

  // Add item to sync queue
  async addToSyncQueue(action: SyncQueue['action'], endpoint: string, data: any) {
    if (!this.db) await this.initialize()

    try {
      const id = `${action}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const timestamp = Date.now()

      await this.db!.runAsync(
        `INSERT INTO sync_queue (id, action, endpoint, data, timestamp) VALUES (?, ?, ?, ?, ?)`,
        [id, action, endpoint, JSON.stringify(data), timestamp]
      )
    } catch (error) {
      console.error('Error adding to sync queue:', error)
    }
  }

  // Get sync queue items
  async getSyncQueue(): Promise<SyncQueue[]> {
    if (!this.db) await this.initialize()

    try {
      const results = await this.db!.getAllAsync<SyncQueue>(
        `SELECT * FROM sync_queue ORDER BY timestamp ASC`
      )

      return results.map(row => ({
        ...row,
        data: JSON.parse(row.data)
      }))
    } catch (error) {
      console.error('Error getting sync queue:', error)
      return []
    }
  }

  // Remove item from sync queue
  async removeFromSyncQueue(id: string) {
    if (!this.db) await this.initialize()

    try {
      await this.db!.runAsync(
        `DELETE FROM sync_queue WHERE id = ?`,
        [id]
      )
    } catch (error) {
      console.error('Error removing from sync queue:', error)
    }
  }

  // Update retry count for sync queue item
  async updateSyncQueueRetry(id: string) {
    if (!this.db) await this.initialize()

    try {
      await this.db!.runAsync(
        `UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id = ?`,
        [id]
      )
    } catch (error) {
      console.error('Error updating sync queue retry:', error)
    }
  }

  // Store user preference
  async setPreference(key: string, value: any) {
    if (!this.db) await this.initialize()

    try {
      const timestamp = Date.now()
      await this.db!.runAsync(
        `INSERT OR REPLACE INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)`,
        [key, JSON.stringify(value), timestamp]
      )
    } catch (error) {
      console.error('Error setting preference:', error)
    }
  }

  // Get user preference
  async getPreference(key: string): Promise<any | null> {
    if (!this.db) await this.initialize()

    try {
      const result = await this.db!.getFirstAsync<{ value: string }>(
        `SELECT value FROM user_preferences WHERE key = ?`,
        [key]
      )

      if (result) {
        return JSON.parse(result.value)
      }

      return null
    } catch (error) {
      console.error('Error getting preference:', error)
      return null
    }
  }

  // Check network connectivity
  async isOnline(): Promise<boolean> {
    try {
      const networkState = await Network.getNetworkStateAsync()
      return networkState.isConnected && networkState.isInternetReachable
    } catch (error) {
      console.error('Error checking network state:', error)
      return false
    }
  }

  // Sync data when online
  async syncWhenOnline() {
    const isOnline = await this.isOnline()
    if (!isOnline) return

    try {
      const syncQueue = await this.getSyncQueue()
      
      for (const item of syncQueue) {
        try {
          // Attempt to sync the item
          const response = await fetch(item.endpoint, {
            method: item.action === 'delete' ? 'DELETE' : 
                   item.action === 'create' ? 'POST' : 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: item.action !== 'delete' ? JSON.stringify(item.data) : undefined,
          })

          if (response.ok) {
            // Remove from queue if successful
            await this.removeFromSyncQueue(item.id)
          } else {
            // Update retry count if failed
            await this.updateSyncQueueRetry(item.id)
          }
        } catch (error) {
          console.error('Error syncing item:', error)
          await this.updateSyncQueueRetry(item.id)
        }
      }
    } catch (error) {
      console.error('Error during sync:', error)
    }
  }

  // Get storage statistics
  async getStorageStats() {
    if (!this.db) await this.initialize()

    try {
      const cacheCount = await this.db!.getFirstAsync<{ count: number }>(
        `SELECT COUNT(*) as count FROM cached_data`
      )
      
      const queueCount = await this.db!.getFirstAsync<{ count: number }>(
        `SELECT COUNT(*) as count FROM sync_queue`
      )

      return {
        cachedItems: cacheCount?.count || 0,
        queuedItems: queueCount?.count || 0,
      }
    } catch (error) {
      console.error('Error getting storage stats:', error)
      return { cachedItems: 0, queuedItems: 0 }
    }
  }

  // Clear all data
  async clearAll() {
    if (!this.db) await this.initialize()

    try {
      await this.db!.runAsync(`DELETE FROM cached_data`)
      await this.db!.runAsync(`DELETE FROM sync_queue`)
      await this.db!.runAsync(`DELETE FROM user_preferences`)
    } catch (error) {
      console.error('Error clearing all data:', error)
    }
  }
}

export const offlineStorage = new OfflineStorageService() 