import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import AsyncStorage from '@react-native-async-storage/async-storage'

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

export interface User {
  id: string
  email: string
  name?: string
}

interface AppState {
  // User state
  user: User | null
  isAuthenticated: boolean
  
  // Market data
  marketData: MarketData[]
  macroData: MacroData[]
  newsItems: NewsItem[]
  
  // User preferences
  watchlist: string[]
  notifications: boolean
  language: 'en' | 'ar' | 'fr'
  
  // Loading states
  isLoading: boolean
  
  // Actions
  setUser: (user: User | null) => void
  setAuthenticated: (isAuthenticated: boolean) => void
  setMarketData: (data: MarketData[]) => void
  setMacroData: (data: MacroData[]) => void
  setNewsItems: (items: NewsItem[]) => void
  addToWatchlist: (symbol: string) => void
  removeFromWatchlist: (symbol: string) => void
  setNotifications: (enabled: boolean) => void
  setLanguage: (language: 'en' | 'ar' | 'fr') => void
  setLoading: (loading: boolean) => void
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      marketData: [],
      macroData: [],
      newsItems: [],
      watchlist: [],
      notifications: true,
      language: 'en',
      isLoading: false,
      
      // Actions
      setUser: (user) => set({ user }),
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      setMarketData: (marketData) => set({ marketData }),
      setMacroData: (macroData) => set({ macroData }),
      setNewsItems: (newsItems) => set({ newsItems }),
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
      setNotifications: (notifications) => set({ notifications }),
      setLanguage: (language) => set({ language }),
      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'casablanca-insight-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        watchlist: state.watchlist,
        notifications: state.notifications,
        language: state.language,
      }),
    }
  )
) 