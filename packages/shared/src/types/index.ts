// Market Data Types
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
  category: 'market' | 'economic' | 'company' | 'regulatory'
  publishedAt: string
  readTime: string
}

// Sentiment Types
export interface SentimentData {
  ticker: string
  bullish_count: number
  neutral_count: number
  bearish_count: number
  total_votes: number
  bullish_percentage: number
  neutral_percentage: number
  bearish_percentage: number
  average_confidence: number
  last_updated: string
}

export interface SentimentVote {
  ticker: string
  sentiment: 'bullish' | 'neutral' | 'bearish'
  confidence: number
}

// Portfolio Types
export interface PortfolioHolding {
  id?: string
  ticker: string
  name: string
  quantity: number
  purchase_price: number
  purchase_date?: string
  notes?: string
  current_price?: number
  current_value?: number
  total_gain_loss?: number
  total_gain_loss_percent?: number
}

export interface PortfolioSummary {
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_percent: number
  holdings_count: number
  last_updated: string
}

export interface CreatePortfolioRequest {
  name: string
  description?: string
}

export interface UpdateHoldingRequest {
  quantity?: number
  purchase_price?: number
  purchase_date?: string
  notes?: string
}

export interface AddHoldingRequest {
  ticker: string
  quantity: number
  purchase_price: number
  purchase_date?: string
  notes?: string
}

// Currency Types
export interface CurrencyPair {
  base: string
  quote: string
  rate: number
  change: number
  changePercent: number
  lastUpdated: string
}

export interface CurrencyAlert {
  id: string
  pair: string
  targetRate: number
  condition: 'above' | 'below'
  isActive: boolean
  createdAt: string
}

// Paper Trading Types
export interface TradingAccount {
  id: string
  name: string
  balance: number
  cash: number
  totalValue: number
  totalGainLoss: number
  totalGainLossPercent: number
  createdAt: string
}

export interface TradingPosition {
  id: string
  ticker: string
  quantity: number
  averagePrice: number
  currentPrice: number
  totalValue: number
  totalGainLoss: number
  totalGainLossPercent: number
}

export interface TradingOrder {
  id: string
  ticker: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
  createdAt: string
  filledAt?: string
}

// User Types
export interface User {
  id: string
  email: string
  name?: string
  avatar?: string
  isPremium: boolean
  createdAt: string
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// Feature Flags
export interface FeatureFlags {
  paperTrading: boolean
  premiumFeatures: boolean
  advancedAnalytics: boolean
  sentimentVoting: boolean
  currencyConverter: boolean
  newsletterSignup: boolean
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system'

export interface ThemeConfig {
  current: Theme
  system: Theme
} 