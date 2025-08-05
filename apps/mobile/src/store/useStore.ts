import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { authService, AuthUser } from '../services/auth'
import { offlineStorage } from '../services/offlineStorage'
import { notificationService } from '../services/notifications'

export interface MarketData {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
}

export interface MacroData {
  indicator: string
  value: string
  change: string
  description: string
}

export interface NewsItem {
  id: string
  title: string
  excerpt: string
  category: string
  publishedAt: string
  readTime: string
}

export interface PortfolioHolding {
  id: string
  ticker: string
  quantity: number
  avgCost: number
  currentPrice: number
  totalValue: number
  unrealizedPnl: number
  unrealizedPnlPercent: number
}

export interface PaperTradingAccount {
  id: string
  accountName: string
  initialBalance: number
  currentBalance: number
  totalPnl: number
  totalPnlPercent: number
  isActive: boolean
}

export interface PriceAlert {
  id: string
  ticker: string
  targetPrice: number
  condition: 'above' | 'below'
  isActive: boolean
  createdAt: number
}

interface AppState {
  // Authentication
  user: AuthUser | null
  isAuthenticated: boolean
  biometricEnabled: boolean
  authLoading: boolean
  
  // Market data
  marketData: MarketData[]
  macroData: MacroData[]
  newsItems: NewsItem[]
  
  // Portfolio & Trading
  portfolioHoldings: PortfolioHolding[]
  paperTradingAccounts: PaperTradingAccount[]
  selectedTradingAccount: PaperTradingAccount | null
  
  // User preferences
  watchlist: string[]
  priceAlerts: PriceAlert[]
  notifications: boolean
  language: 'en' | 'ar' | 'fr'
  
  // Offline & Sync
  isOnline: boolean
  syncQueue: any[]
  cachedData: any[]
  
  // Loading states
  isLoading: boolean
  isSyncing: boolean
  
  // Actions
  // Authentication
  setUser: (user: AuthUser | null) => void
  setAuthenticated: (isAuthenticated: boolean) => void
  setBiometricEnabled: (enabled: boolean) => void
  setAuthLoading: (loading: boolean) => void
  
  // Data management
  setMarketData: (data: MarketData[]) => void
  setMacroData: (data: MacroData[]) => void
  setNewsItems: (items: NewsItem[]) => void
  setPortfolioHoldings: (holdings: PortfolioHolding[]) => void
  setPaperTradingAccounts: (accounts: PaperTradingAccount[]) => void
  setSelectedTradingAccount: (account: PaperTradingAccount | null) => void
  
  // User preferences
  addToWatchlist: (symbol: string) => void
  removeFromWatchlist: (symbol: string) => void
  addPriceAlert: (alert: PriceAlert) => void
  removePriceAlert: (alertId: string) => void
  setNotifications: (enabled: boolean) => void
  setLanguage: (language: 'en' | 'ar' | 'fr') => void
  
  // Offline & Sync
  setOnline: (isOnline: boolean) => void
  setSyncQueue: (queue: any[]) => void
  setCachedData: (data: any[]) => void
  setSyncing: (syncing: boolean) => void
  
  // Loading states
  setLoading: (loading: boolean) => void
  
  // Complex actions
  initializeApp: () => Promise<void>
  syncData: () => Promise<void>
  loadCachedData: () => Promise<void>
  signOut: () => Promise<void>
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      biometricEnabled: false,
      authLoading: false,
      
      marketData: [],
      macroData: [],
      newsItems: [],
      
      portfolioHoldings: [],
      paperTradingAccounts: [],
      selectedTradingAccount: null,
      
      watchlist: [],
      priceAlerts: [],
      notifications: true,
      language: 'en',
      
      isOnline: true,
      syncQueue: [],
      cachedData: [],
      
      isLoading: false,
      isSyncing: false,
      
      // Actions
      setUser: (user) => set({ user }),
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      setBiometricEnabled: (biometricEnabled) => set({ biometricEnabled }),
      setAuthLoading: (authLoading) => set({ authLoading }),
      
      setMarketData: (marketData) => set({ marketData }),
      setMacroData: (macroData) => set({ macroData }),
      setNewsItems: (newsItems) => set({ newsItems }),
      setPortfolioHoldings: (portfolioHoldings) => set({ portfolioHoldings }),
      setPaperTradingAccounts: (paperTradingAccounts) => set({ paperTradingAccounts }),
      setSelectedTradingAccount: (selectedTradingAccount) => set({ selectedTradingAccount }),
      
      addToWatchlist: (symbol) => {
        const { watchlist } = get()
        if (!watchlist.includes(symbol)) {
          set({ watchlist: [...watchlist, symbol] })
        }
      },
      removeFromWatchlist: (symbol) => {
        const { watchlist } = get()
        set({ watchlist: watchlist.filter(s => s !== symbol) })
      },
      addPriceAlert: (alert) => {
        const { priceAlerts } = get()
        set({ priceAlerts: [...priceAlerts, alert] })
      },
      removePriceAlert: (alertId) => {
        const { priceAlerts } = get()
        set({ priceAlerts: priceAlerts.filter(alert => alert.id !== alertId) })
      },
      setNotifications: (notifications) => set({ notifications }),
      setLanguage: (language) => set({ language }),
      
      setOnline: (isOnline) => set({ isOnline }),
      setSyncQueue: (syncQueue) => set({ syncQueue }),
      setCachedData: (cachedData) => set({ cachedData }),
      setSyncing: (isSyncing) => set({ isSyncing }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      // Complex actions
      initializeApp: async () => {
        const { setAuthLoading, setUser, setAuthenticated, setBiometricEnabled } = get()
        
        try {
          setAuthLoading(true)
          
          // Initialize offline storage
          await offlineStorage.initialize()
          
          // Check for existing user session
          const user = await authService.getCurrentUser()
          if (user) {
            setUser(user)
            setAuthenticated(true)
            
            // Check biometric status
            const biometricEnabled = await authService.isBiometricEnabled()
            setBiometricEnabled(biometricEnabled)
          }
          
          // Initialize notifications
          await notificationService.initialize()
          
          // Load cached data
          await get().loadCachedData()
          
        } catch (error) {
          console.error('Error initializing app:', error)
        } finally {
          setAuthLoading(false)
        }
      },
      
      syncData: async () => {
        const { setSyncing, setOnline, isOnline } = get()
        
        try {
          setSyncing(true)
          
          // Check network connectivity
          const online = await offlineStorage.isOnline()
          setOnline(online)
          
          if (online) {
            // Sync queued operations
            await offlineStorage.syncWhenOnline()
            
            // Refresh data from server
            // This would typically fetch fresh data from your API
            // For now, we'll just clear expired cache
            await offlineStorage.clearExpiredCache()
          }
          
        } catch (error) {
          console.error('Error syncing data:', error)
        } finally {
          setSyncing(false)
        }
      },
      
      loadCachedData: async () => {
        const { setMarketData, setMacroData, setNewsItems } = get()
        
        try {
          // Load cached market data
          const cachedMarketData = await offlineStorage.getAllCachedData('market')
          if (cachedMarketData.length > 0) {
            setMarketData(cachedMarketData)
          }
          
          // Load cached macro data
          const cachedMacroData = await offlineStorage.getAllCachedData('macro')
          if (cachedMacroData.length > 0) {
            setMacroData(cachedMacroData)
          }
          
          // Load cached news
          const cachedNews = await offlineStorage.getAllCachedData('news')
          if (cachedNews.length > 0) {
            setNewsItems(cachedNews)
          }
          
        } catch (error) {
          console.error('Error loading cached data:', error)
        }
      },
      
      signOut: async () => {
        const { setUser, setAuthenticated, setBiometricEnabled } = get()
        
        try {
          await authService.signOut()
          await offlineStorage.clearAll()
          await notificationService.cancelAllNotifications()
          
          setUser(null)
          setAuthenticated(false)
          setBiometricEnabled(false)
        } catch (error) {
          console.error('Error signing out:', error)
        }
      },
    }),
    {
      name: 'morningmaghreb-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        biometricEnabled: state.biometricEnabled,
        watchlist: state.watchlist,
        priceAlerts: state.priceAlerts,
        notifications: state.notifications,
        language: state.language,
        portfolioHoldings: state.portfolioHoldings,
        paperTradingAccounts: state.paperTradingAccounts,
      }),
    }
  )
) 